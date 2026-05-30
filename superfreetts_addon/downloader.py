
import os
import threading
import time
import urllib.request
import shutil
from typing import Callable, Optional
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

class TurboDownloader:
    """
    High-performance multi-threaded downloader designed for large TTS models.
    Inspired by IDM / XDM strategies.
    Robust handling for Windows file locks (WinError 32).
    """
    def __init__(self, url: str, dest: str, progress_callback: Optional[Callable] = None, concurrency: int = 8, debug_mode: bool = False):
        self.url = url
        self.dest = dest
        self.progress_callback = progress_callback
        self.concurrency = concurrency
        self.debug_mode = debug_mode
        self.file_size = 0
        self.downloaded_bytes = 0
        self.lock = threading.Lock()
        self.start_time = 0
        self._stop_event = threading.Event()
        self.parts = []
        self.last_bytes = [] # To calculate windowed speed

    def log_debug(self, message: str):
        if self.debug_mode:
            logger.info(f"[TurboDownloader] {message}")
            print(f"[TurboDownloader] {message}")

    def _get_file_info(self):
        try:
            req = urllib.request.Request(self.url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            with urllib.request.urlopen(req) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                self.file_size = int(headers.get('content-length', 0))
                self.accept_ranges = headers.get('accept-ranges') == 'bytes' or 'content-range' in headers
            self.log_debug(f"File size: {self.file_size} bytes, Accept-Ranges: {self.accept_ranges}")
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            self.file_size = 0
            self.accept_ranges = False

    def _download_chunk(self, start: int, end: int, part_file: str):
        retry = 5 # Increased retries
        while retry > 0 and not self._stop_event.is_set():
            try:
                req = urllib.request.Request(self.url)
                req.add_header('Range', f'bytes={start}-{end}')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.status != 206 and self.concurrency > 1:
                        self.log_debug(f"Warning: Server returned {resp.status} instead of 206 for chunk.")
                    
                    # Handle WinError 32: Process cannot access file
                    f = None
                    file_retries = 5
                    while file_retries > 0:
                        try:
                            f = open(part_file, 'wb')
                            break
                        except PermissionError as e: # Catch WinError 32
                            if e.errno == 13 or (hasattr(e, 'winerror') and e.winerror == 32):
                                self.log_debug(f"File lock detected on {part_file}, retrying in 1s...")
                                time.sleep(1)
                                file_retries -= 1
                            else:
                                raise
                    
                    if not f:
                        raise Exception(f"Could not open part file {part_file} after retries")

                    try:
                        while not self._stop_event.is_set():
                            chunk = resp.read(1024 * 64) # Balanced buffer
                            if not chunk:
                                break
                            f.write(chunk)
                            with self.lock:
                                self.downloaded_bytes += len(chunk)
                                self.last_bytes.append((time.time(), len(chunk)))
                                now = time.time()
                                while self.last_bytes and now - self.last_bytes[0][0] > 2.0:
                                    self.last_bytes.pop(0)
                        
                        if not self._stop_event.is_set():
                            self._report_progress()
                            return # Success
                    finally:
                        f.close()
                        
            except Exception as e:
                retry -= 1
                self.log_debug(f"Chunk {start}-{end} failed, retrying ({retry} left): {e}")
                time.sleep(1.5)
        
        if retry == 0:
            self._stop_event.set()
            raise Exception(f"Failed to download chunk {start}-{end} after retries")

    def _report_progress(self):
        if not self.progress_callback:
            return
        
        now = time.time()
        with self.lock:
            recent_bytes = sum(b for t, b in self.last_bytes if now - t <= 2.0)
            duration = min(2.0, now - self.start_time)
            speed = recent_bytes / (duration if duration > 0.1 else 0.1)
            percent = (self.downloaded_bytes / self.file_size * 100) if self.file_size > 0 else 0
        
        self.progress_callback({
            "percent": int(percent),
            "downloaded": self.downloaded_bytes,
            "total": self.file_size,
            "speed": speed,
            "speed_mb": speed / (1024 * 1024)
        })

    def start(self):
        self.start_time = time.time()
        self._get_file_info()

        # Pre-cleanup: Delete any existing .part files to avoid stale locks
        self.parts = [f"{self.dest}.part{i}" for i in range(self.concurrency)]
        self._cleanup_parts()

        if self.file_size <= 0 or not self.accept_ranges:
            self.log_debug("Falling back to standard download")
            urllib.request.urlretrieve(self.url, self.dest, 
                reporthook=lambda count, block_size, total_size: self._legacy_report(count, block_size, total_size))
            return

        chunk_size = self.file_size // self.concurrency
        threads = []

        for i in range(self.concurrency):
            start = i * chunk_size
            end = (i + 1) * chunk_size - 1 if i < self.concurrency - 1 else self.file_size - 1
            part_file = self.parts[i]
            
            t = threading.Thread(target=self._download_chunk, args=(start, end, part_file))
            t.daemon = True # Ensure threads don't block Anki exit
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if self._stop_event.is_set():
            self._cleanup_parts()
            raise Exception("Download aborted or failed.")

        self._merge_parts()
        self.log_debug("Download completed successfully.")

    def _merge_parts(self):
        self.log_debug(f"Merging {len(self.parts)} parts into {self.dest}...")
        # Use a temporary file for merging to avoid locking the actual destination prematurely
        temp_merged = self.dest + ".merging"
        try:
            with open(temp_merged, 'wb') as outfile:
                for part in self.parts:
                    if not os.path.exists(part):
                        raise Exception(f"Part file missing: {part}")
                    with open(part, 'rb') as infile:
                        shutil.copyfileobj(infile, outfile)
            
            # Atomic rename (as much as possible on Windows)
            if os.path.exists(self.dest):
                os.remove(self.dest)
            os.rename(temp_merged, self.dest)
        finally:
            if os.path.exists(temp_merged):
                try: os.remove(temp_merged)
                except: pass
        self._cleanup_parts()

    def _cleanup_parts(self):
        for part in self.parts:
            # Retry deletion because handles might take a moment to release
            for _ in range(3):
                try:
                    if os.path.exists(part):
                        os.remove(part)
                    break
                except PermissionError:
                    time.sleep(0.5)

    def _legacy_report(self, count, block_size, total_size):
        self.file_size = total_size
        new_downloaded = count * block_size
        diff = new_downloaded - self.downloaded_bytes
        if diff > 0:
            with self.lock:
                self.downloaded_bytes = new_downloaded
                self.last_bytes.append((time.time(), diff))
                now = time.time()
                while self.last_bytes and now - self.last_bytes[0][0] > 2.0:
                    self.last_bytes.pop(0)
        self._report_progress()
