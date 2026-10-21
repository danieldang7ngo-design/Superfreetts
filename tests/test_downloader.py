"""Downloader timeout, range-fallback, size and checksum behavior."""

import hashlib
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from superfreetts_addon.downloader import TurboDownloader


PAYLOAD = (b"SuperFreeTTS-download-test-" * 500)


class _Handler(BaseHTTPRequestHandler):
    supports_ranges = True

    def log_message(self, *_args):
        pass

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Length", str(len(PAYLOAD)))
        if self.supports_ranges:
            self.send_header("Accept-Ranges", "bytes")
        self.end_headers()

    def do_GET(self):
        range_header = self.headers.get("Range")
        if self.supports_ranges and range_header:
            start_text, end_text = range_header.replace("bytes=", "").split("-", 1)
            start = int(start_text)
            end = int(end_text)
            chunk = PAYLOAD[start:end + 1]
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{len(PAYLOAD)}")
            self.send_header("Content-Length", str(len(chunk)))
            self.end_headers()
            self.wfile.write(chunk)
            return

        self.send_response(200)
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.end_headers()
        self.wfile.write(PAYLOAD)


@pytest.fixture
def http_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/file.bin"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.unit
def test_downloader_merges_ranged_download(http_server, tmp_path):
    destination = tmp_path / "downloaded.bin"
    downloader = TurboDownloader(
        http_server,
        str(destination),
        concurrency=3,
        expected_sha256=hashlib.sha256(PAYLOAD).hexdigest(),
    )
    downloader.start()

    assert destination.read_bytes() == PAYLOAD


@pytest.mark.unit
def test_downloader_falls_back_when_server_ignores_ranges(monkeypatch, tmp_path):
    monkeypatch.setattr(_Handler, "supports_ranges", False)
    # Bind a server after changing the class flag.
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        destination = tmp_path / "fallback.bin"
        downloader = TurboDownloader(
            f"http://127.0.0.1:{server.server_port}/file.bin",
            str(destination),
            concurrency=3,
        )
        downloader.start()
        assert destination.read_bytes() == PAYLOAD
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.unit
def test_downloader_verifies_expected_md5(http_server, tmp_path):
    destination = tmp_path / "piper-model.onnx"
    downloader = TurboDownloader(
        http_server,
        str(destination),
        concurrency=3,
        expected_md5=hashlib.md5(PAYLOAD).hexdigest(),
    )
    downloader.start()
    assert destination.read_bytes() == PAYLOAD


@pytest.mark.unit
def test_downloader_rejects_bad_md5(http_server, tmp_path):
    destination = tmp_path / "bad-piper-model.onnx"
    downloader = TurboDownloader(
        http_server,
        str(destination),
        concurrency=1,
        expected_md5="0" * 32,
    )
    with pytest.raises(IOError, match="MD5 mismatch"):
        downloader.start()
    assert not destination.exists()


@pytest.mark.unit
def test_downloader_deletes_file_on_checksum_mismatch(http_server, tmp_path):
    destination = tmp_path / "bad.bin"
    downloader = TurboDownloader(
        http_server,
        str(destination),
        concurrency=1,
        expected_sha256="0" * 64,
    )

    with pytest.raises(IOError, match="SHA-256 mismatch"):
        downloader.start()
    assert not destination.exists()
