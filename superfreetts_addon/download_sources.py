"""Pinned download locations and integrity fingerprints.

Keep every engine download URL and its expected digest here.  A release that
intentionally changes an upstream asset must update the digest in this file;
a changed asset with an unchanged digest is rejected by ``TurboDownloader``
instead of being silently installed.

Notes
-----
* Python embeddable archives and Piper release archives use immutable
  versioned URLs plus SHA-256.
* Kokoro's GitHub release assets are immutable, but are still checked against
  a SHA-256 because GitHub release files can be replaced by the owner.
* Piper voice files use the MD5 published by the upstream ``voices.json``.
  That MD5 is an upstream integrity check, not a modern security boundary; it
  is used with ``usedforsecurity=False`` and always in addition to the HTTPS
  transport and size check.
* The MMS ONNX model repository does not publish per-file checksums.  Its
  revision is pinned to a commit so the file set cannot move under us, and
  the downloader rejects empty/truncated files via the size check.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Python runtime used by the Windows-only engine bootstraps
# ---------------------------------------------------------------------------
PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
PYTHON_EMBED_SHA256 = "608619f8619075629c9c69f361352a0da6ed7e62f83a0e19c63e0ea32eb7629d"
PYTHON_EMBED_SIZE = 8629277

# The PyPA 3.10-specific get-pip path currently returns 404.  The 3.9 path is
# still published, is versioned, and its script supports the embedded Python
# 3.10 runtime.  Pin its SHA-256 as the primary integrity boundary.
GET_PIP_URL = "https://bootstrap.pypa.io/pip/3.9/get-pip.py"
GET_PIP_SHA256 = "95c0ae79ccf9ac1e47e4187f49081d6ae1f45997afd4549e14f37337cbcfd766"
GET_PIP_SIZE = 2193444

# ---------------------------------------------------------------------------
# Piper engine binaries (release 2023.11.14-2)
# ---------------------------------------------------------------------------
PIPER_ENGINE_URL_WINDOWS = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
PIPER_ENGINE_URL_LINUX_X86_64 = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz"
PIPER_ENGINE_SHA256_WINDOWS = "f3c58906402b24f3a96d92145f58acba6d86c9b5db896d207f78dc80811efcea"
PIPER_ENGINE_SHA256_LINUX = "a50cb45f355b7af1f6d758c1b360717877ba0a398cc8cbe6d2a7a3a26e225992"
PIPER_ENGINE_SIZE_WINDOWS = 22477236
PIPER_ENGINE_SIZE_LINUX = 26460462

# Immutable voice catalogue.  Model files referenced by this JSON are fetched
# from the same tagged revision.
PIPER_VOICES_JSON_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/voices.json"
PIPER_VOICES_JSON_SHA256 = "7a5513ddc3345a5828f0df04e6784c6cc4823c1f33538498d9718ac1ef93db2b"
PIPER_HF_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

# ---------------------------------------------------------------------------
# Kokoro ONNX model assets (GitHub release model-files-v1.0)
# ---------------------------------------------------------------------------
KOKORO_V10_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
KOKORO_V10_MODEL_SHA256 = "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5"
KOKORO_V10_MODEL_SIZE = 325532387

KOKORO_V10_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
KOKORO_V10_VOICES_SHA256 = "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"
KOKORO_V10_VOICES_SIZE = 28214398

# ---------------------------------------------------------------------------
# MMS multilingual ONNX repository
# ---------------------------------------------------------------------------
# Pinned to the repository commit observed when this release was prepared.
# HF resolves files under this commit, so a later force-push to main cannot
# change what users download.
MMS_REVISION = "4f49fc254f11ddb0e35fbf25b6e48b04463a6779"
MMS_BASE_URL = (
    "https://huggingface.co/willwade/mms-tts-multilingual-models-onnx/"
    f"resolve/{MMS_REVISION}"
)
