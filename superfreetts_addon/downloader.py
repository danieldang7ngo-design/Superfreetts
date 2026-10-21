
import os
import hashlib
import threading
import time
import urllib.request
import shutil
from typing import Callable, Optional
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


class RangeNotSupported(Exception):
    """The server ignored a Range request; fall back to one connection."""


class TurboDownloader:
    """
    High-performance multi-threaded downloader designed for large TTS models.
    Inspired by IDM / XDM strategies.
    Robust handling for Windows file locks (WinError 32).
    """
    def __init__(
        self,
        url: str,
        dest: str,
        progress_callback: Optional[Callable] = None,
        concurrency: int = 8,
        debug_mode: bool = False,
        expected_sha256: Optional[str] = None,
        expected_size: Optional[int] = None,
    ):
        self.url = url
        self.dest = dest
        self.progress_callback = progress_callback
        self.concurrency = max(1, int(concurrency))
        self.debug_mode = debug_mode
        self.expected_sha256 = expected_sha256.lower() if expected_sha256 else None
        self.expected_size = expected_size
        self.file_size = 0
        self.downloaded_bytes = 0
        self.lock = threading.Lock()
        self.start_time = 0
        self._stop_event = threading.Event()
        self._range_unsupported = False
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
            with urllib.request.urlopen(req, timeout=30) as resp:
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
                
                with urllib.request.urlopen(req, timeout=60) as resp:
                    status = getattr(resp, "status", None) or resp.getcode()
                    if self.concurrency > 1 and status != 206:
                        self._range_unsupported = True
                        raise RangeNotSupported(
                            f"Server returned {status} instead of 206 for a ranged request"
                        )
                    
                    f = None
                    file_retries = 5
                    while file_retries > 0:
                        try:
                            f = open(part_file, 'wb')
                            break
                        except PermissionError as e:
                            if e.errno == 13 or (hasattr(e, 'winerror') and e.winerror == 32):
                                self.log_debug(f"File lock detected on {part_file}, retrying in 1s...")
                                time.sleep(1)
                                file_retries -= 1
                            else:
                                raise

                    if not f:
                        raise Exception(f"Could not open part file {part_file} after retries")

                    try:
                        bytes_written = 0
                        while not self._stop_event.is_set():
                            chunk = resp.read(1024 * 64)
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_written += len(chunk)
                            with self.lock:
                                self.downloaded_bytes += len(chunk)
                                self.last_bytes.append((time.time(), len(chunk)))
                                now = time.time()
                                while self.last_bytes and now - self.last_bytes[0][0] > 2.0:
                                    self.last_bytes.pop(0)

                        if not self._stop_event.is_set():
                            expected_bytes = end - start + 1
                            if bytes_written != expected_bytes:
                                raise IOError(
                                    f"Chunk {start}-{end} was truncated: "
                                    f"got {bytes_written} of {expected_bytes} bytes"
                                )
                            self._report_progress()
                            return
                    finally:
                        f.close()
                        
            except RangeNotSupported as e:
                self.log_debug(str(e))
                return
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
            self._download_standard()
            self._verify_download()
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

        if self._range_unsupported:
            self.log_debug("Server ignored range requests; retrying with one connection")
            self._cleanup_parts()
            self._download_standard()
            self._verify_download()
            return

        if self._stop_event.is_set():
            self._cleanup_parts()
            raise Exception("Download aborted or failed.")

        self._merge_parts()
        self._verify_download()
        self.log_debug("Download completed successfully.")

    def _download_standard(self):
        """Single-connection fallback with a timeout and resumable-free cleanup."""
        temp_path = self.dest + ".download"
        req = urllib.request.Request(self.url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                total = int(headers.get('content-length', self.file_size or 0))
                self.file_size = total
                with open(temp_path, "wb") as output:
                    while not self._stop_event.is_set():
                        chunk = resp.read(1024 * 64)
                        if not chunk:
                            break
                        output.write(chunk)
                        with self.lock:
                            self.downloaded_bytes += len(chunk)
                            self.last_bytes.append((time.time(), len(chunk)))
                            now = time.time()
                            while self.last_bytes and now - self.last_bytes[0][0] > 2.0:
                                self.last_bytes.pop(0)
                        self._report_progress()
            if self._stop_event.is_set():
                raise Exception("Download aborted")
            os.replace(temp_path, self.dest)
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

    def _verify_download(self):
        if not os.path.exists(self.dest):
            raise IOError(f"Download did not produce {self.dest}")

        actual_size = os.path.getsize(self.dest)
        expected_size = self.expected_size or self.file_size
        if expected_size and actual_size != expected_size:
            self._remove_bad_download()
            raise IOError(
                f"Download size mismatch for {self.dest}: "
                f"got {actual_size}, expected {expected_size}"
            )

        if self.expected_sha256:
            digest = hashlib.sha256()
            with open(self.dest, "rb") as handle:
                while True:
                    chunk = handle.read(1024 * 1024)
                    if not chunk:
                        break
                    digest.update(chunk)
            actual_hash = digest.hexdigest()
            if actual_hash != self.expected_sha256:
                self._remove_bad_download()
                raise IOError(
                    f"SHA-256 mismatch for {self.dest}: "
                    f"got {actual_hash}, expected {self.expected_sha256}"
                )

    def _remove_bad_download(self):
        try:
            if os.path.exists(self.dest):
                os.remove(self.dest)
        except OSError as e:
            logger.warning(f"Failed to remove invalid download {self.dest}: {e}")

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
                except Exception: pass
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
