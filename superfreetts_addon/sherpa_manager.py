import os
import sys
import shutil
import zipfile
import threading
from aqt import mw
from .downloader import TurboDownloader
from . import i18n
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

# Preferred Version
SHERPA_VERSION = "1.12.34"
# Official Wheel URL for Python 3.10 Windows x64 (matches our portable python)
SHERPA_WHEEL_URL = f"https://github.com/k2-fsa/sherpa-onnx/releases/download/v{SHERPA_VERSION}/sherpa_onnx-{SHERPA_VERSION}-cp310-cp310-win_amd64.whl"

ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(ADDON_DIR, 'libs')
SHERPA_PKG_DIR = os.path.join(LIBS_DIR, 'sherpa_onnx')

class SherpaManager:
    _lock = threading.Lock()
    _installing = False

    @staticmethod
    def get_libs_dir():
        """Return the absolute path to the shared libs directory."""
        return os.path.abspath(LIBS_DIR)

    @staticmethod
    def is_installed():
        """Check if sherpa_onnx is present in the local libs directory."""
        # Simple check for the package directory and its init file
        return os.path.exists(SHERPA_PKG_DIR) and os.path.exists(os.path.join(SHERPA_PKG_DIR, '__init__.py'))

    @classmethod
    def ensure_installed(cls, progress_callback=None):
        """
        Thread-safe method to ensure sherpa-onnx is available locally.
        If missing, it downloads the official wheel and extracts it to libs/.
        """
        if cls.is_installed():
            logger.info("SherpaManager: Library already installed.")
            return True

        with cls._lock:
            if cls._installing:
                logger.info("SherpaManager: Installation already in progress in another thread.")
                return False
            cls._installing = True

        try:
            logger.info(f"SherpaManager: Starting installation of v{SHERPA_VERSION}...")
            if not os.path.exists(LIBS_DIR):
                os.makedirs(LIBS_DIR, exist_ok=True)

            # We use the downloader utility already present in the addon
            temp_wheel = os.path.join(LIBS_DIR, f'sherpa_onnx_{SHERPA_VERSION}.whl')
            
            def internal_progress(data):
                if progress_callback:
                    progress_callback(data)
                # Log progress occasionally
                if data.get('percent', 0) % 25 == 0:
                    logger.debug(f"SherpaManager: Download {data.get('percent')}%")

            logger.info(f"SherpaManager: Downloading wheel from {SHERPA_WHEEL_URL}")
            downloader = TurboDownloader(SHERPA_WHEEL_URL, temp_wheel, progress_callback=internal_progress)
            downloader.start()

            # Wheels are ZIP files. Extracting them to libs/ is equivalent to installing them
            # as long as we add libs/ to sys.path later.
            logger.info(f"SherpaManager: Extracting wheel to {LIBS_DIR}")
            with zipfile.ZipFile(temp_wheel, 'r') as zip_ref:
                zip_ref.extractall(LIBS_DIR)

            # Cleanup the wheel file after extraction
            if os.path.exists(temp_wheel):
                try:
                    os.remove(temp_wheel)
                except: pass
            
            logger.info("SherpaManager: Unified installation complete.")
            return True
        except Exception as e:
            logger.error(f"SherpaManager: Installation failed: {str(e)}")
            # Cleanup on failure to avoid partial installs
            if os.path.exists(SHERPA_PKG_DIR):
                shutil.rmtree(SHERPA_PKG_DIR, ignore_errors=True)
            return False
        finally:
            with cls._lock:
                cls._installing = False

    @staticmethod
    def inject_to_sys_path():
        """Helper to add the shared libs to the current process sys.path."""
        ldir = SherpaManager.get_libs_dir()
        if os.path.exists(ldir) and ldir not in sys.path:
            sys.path.insert(0, ldir)
            logger.info(f"SherpaManager: Injected {ldir} to sys.path")
