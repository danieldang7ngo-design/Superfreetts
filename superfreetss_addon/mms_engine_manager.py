import os
import sys
import shutil
import time
import zipfile
import subprocess
import threading
from typing import Optional, Callable, Tuple

from . import logging_utils
from . import service_logger
from .downloader import TurboDownloader
from .constants import DATA_DIR, MMS_ENGINE_DIR

logger = logging_utils.get_child_logger(__name__)

# Constants for Python Installation
PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

# Sherpa-ONNX version to install via pip
SHERPA_VERSION = "1.12.34"

PYTHON_EXE = os.path.join(MMS_ENGINE_DIR, 'python.exe')
SITE_PACKAGES = os.path.join(MMS_ENGINE_DIR, 'Lib', 'site-packages')

# Install logging is handled by service_logger module
# Log files: user_files/log/mms_install.log


class MmsEngineManager:
    """
    Self-contained engine manager for MMS TTS.
    Installs its own portable Python 3.10 + sherpa-onnx + dependencies.
    Fully independent from Kokoro or the shared engine.
    """
    _lock = threading.Lock()
    _installing = False

    @staticmethod
    def get_python_exe() -> str:
        """Return the path to the MMS-dedicated python executable."""
        return PYTHON_EXE

    @staticmethod
    def is_installed() -> bool:
        """Check if the MMS engine is fully installed (Python + sherpa_onnx)."""
        if not os.path.exists(PYTHON_EXE):
            return False
        # Check that sherpa_onnx is actually importable
        site_packages = os.path.join(MMS_ENGINE_DIR, 'Lib', 'site-packages')
        sherpa_pkg = os.path.join(site_packages, 'sherpa_onnx')
        return os.path.exists(sherpa_pkg) and os.path.exists(os.path.join(sherpa_pkg, '__init__.py'))

    @classmethod
    def ensure_installed(cls, progress_callback: Optional[Callable] = None) -> bool:
        """
        Thread-safe installation of MMS engine.
        Returns True on success, False on failure.
        """
        if cls.is_installed():
            logger.info("MmsEngineManager: Already installed.")
            service_logger.write_log('mms', 'install', 'INFO', 'Engine already installed, skipping')
            return True

        with cls._lock:
            if cls._installing:
                logger.info("MmsEngineManager: Installation already in progress.")
                return False
            cls._installing = True

        try:
            os.makedirs(MMS_ENGINE_DIR, exist_ok=True)

            def _report(msg, percent=0):
                logger.info(f"MmsEngineManager: {msg}")
                if progress_callback:
                    progress_callback({'message': msg, 'percent': percent})

            # ── Step 1: Download & Extract Python ──
            if not os.path.exists(PYTHON_EXE):
                _report("Downloading Python 3.10...", 5)
                service_logger.write_log('mms', 'install', 'INFO', 'Downloading Python 3.10 embeddable', {'URL': PYTHON_EMBED_URL})
                zip_path = os.path.join(MMS_ENGINE_DIR, 'python.zip')
                
                downloader = TurboDownloader(PYTHON_EMBED_URL, zip_path, progress_callback=progress_callback)
                downloader.start()

                _report("Extracting Python...", 20)
                service_logger.write_log('mms', 'install', 'INFO', 'Extracting Python to engine directory', {'Path': MMS_ENGINE_DIR})
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(MMS_ENGINE_DIR)

                if os.path.exists(zip_path):
                    os.remove(zip_path)

                # Configure ._pth to enable site-packages
                cls._configure_python_pth()
                _report("Python extracted.", 25)

            # ── Step 2: Install Pip ──
            scripts_dir = os.path.join(MMS_ENGINE_DIR, 'Scripts')
            pip_exe = os.path.join(scripts_dir, 'pip.exe')
            if not os.path.exists(pip_exe):
                _report("Downloading pip...", 30)
                get_pip_path = os.path.join(MMS_ENGINE_DIR, 'get-pip.py')
                downloader = TurboDownloader(GET_PIP_URL, get_pip_path)
                downloader.start()

                _report("Installing pip...", 35)
                cls._run_command([PYTHON_EXE, get_pip_path])

                if os.path.exists(get_pip_path):
                    os.remove(get_pip_path)
                _report("Pip installed.", 40)

            # ── Step 3: Install core dependencies ──
            core_deps = ['numpy', 'setuptools', 'wheel', 'soundfile']
            missing_deps = [d for d in core_deps if not cls._is_package_installed(d)]
            if missing_deps:
                _report(f"Installing {', '.join(missing_deps)}...", 45)
                cls._run_command([PYTHON_EXE, '-m', 'pip', 'install', 
                                'numpy<2.0.0', 'setuptools', 'wheel', 'soundfile'])
            else:
                _report("Core dependencies already installed, skipping.", 45)
                logger.info("MmsEngineManager: All core deps present, skipping pip install.")

            # ── Step 4: Install sherpa-onnx ──
            if not cls._is_package_installed('sherpa_onnx'):
                _report(f"Installing sherpa-onnx v{SHERPA_VERSION} (this may take a while)...", 55)
                cls._run_command([PYTHON_EXE, '-m', 'pip', 'install', 
                                f'sherpa-onnx=={SHERPA_VERSION}'])
                _report("sherpa-onnx installed.", 85)
            else:
                _report("sherpa-onnx already installed, skipping.", 85)
                logger.info("MmsEngineManager: sherpa_onnx already present, skipping pip install.")

            # ── Step 5: Verify ──
            _report("Verifying installation...", 90)
            ok, msg = cls.verify_sherpa()
            if not ok:
                logger.error(f"MmsEngineManager: Verification failed: {msg}")
                _report(f"Verification FAILED: {msg}", 100)
                return False

            _report("MMS Engine installation complete.", 100)
            logger.info("MmsEngineManager: Installation complete and verified.")
            service_logger.write_log('mms', 'install', 'OK', 'MMS Engine installation complete and verified')
            return True

        except Exception as e:
            logger.error(f"MmsEngineManager: Installation failed: {e}")
            service_logger.write_log('mms', 'install', 'ERROR', f'Installation failed: {e}')
            return False
        finally:
            with cls._lock:
                cls._installing = False

    @classmethod
    def verify_sherpa(cls) -> Tuple[bool, str]:
        """
        Actually run the MMS python interpreter and try to import sherpa_onnx.
        Returns (True, 'ok') on success, (False, error_message) on failure.
        """
        if not os.path.exists(PYTHON_EXE):
            return False, "Python executable not found"

        try:
            result = subprocess.run(
                [PYTHON_EXE, '-c', 'import sherpa_onnx; print("OK")'],
                capture_output=True, text=True, timeout=30,
                cwd=MMS_ENGINE_DIR,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0 and 'OK' in result.stdout:
                return True, 'ok'
            else:
                error_msg = result.stderr.strip() if result.stderr else f"Exit code {result.returncode}"
                return False, error_msg
        except subprocess.TimeoutExpired:
            return False, "Verification timed out"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _configure_python_pth():
        """Uncomment 'import site' in ._pth file to enable site-packages."""
        pth_files = [f for f in os.listdir(MMS_ENGINE_DIR) if f.endswith('._pth')]
        if pth_files:
            pth_path = os.path.join(MMS_ENGINE_DIR, pth_files[0])
            with open(pth_path, 'r') as f:
                content = f.read()

            if '#import site' in content:
                content = content.replace('#import site', 'import site')
                with open(pth_path, 'w') as f:
                    f.write(content)
                logger.info("MmsEngineManager: Enabled 'import site' in ._pth")

    @staticmethod
    def _is_package_installed(pkg_name):
        """Check if a Python package is installed in the MMS engine's site-packages."""
        if not os.path.exists(SITE_PACKAGES):
            return False
        # Check for package directory (e.g. numpy/, sherpa_onnx/)
        pkg_dir = os.path.join(SITE_PACKAGES, pkg_name)
        if os.path.isdir(pkg_dir):
            return True
        # Check for single-file module (e.g. soundfile.py)
        pkg_file = os.path.join(SITE_PACKAGES, f"{pkg_name}.py")
        if os.path.isfile(pkg_file):
            return True
        # Check for dist-info (handles cases like 'soundfile' installed as 'SoundFile')
        try:
            for item in os.listdir(SITE_PACKAGES):
                if item.lower().startswith(pkg_name.lower().replace('-', '_')) and item.endswith('.dist-info'):
                    return True
        except OSError:
            pass
        return False

    @staticmethod
    def _run_command(cmd):
        """Run a command in the MMS engine directory, logging output to file."""
        cmd_str = ' '.join(cmd)
        logger.info(f"MmsEngineManager: Running: {cmd_str}")
        
        # Log to centralized install log
        service_logger.write_install_separator('mms', cmd_str)
        
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=MMS_ENGINE_DIR,
            timeout=600,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Write result to install log
        service_logger.write_install_result('mms', process.returncode, process.stdout, process.stderr)
        
        if process.returncode != 0:
            error_detail = process.stderr[:500] if process.stderr else "No error output"
            logger.error(f"MmsEngineManager: Command failed: {cmd_str}\nError: {error_detail}")
            raise Exception(f"Command failed (code {process.returncode}): {error_detail}")
