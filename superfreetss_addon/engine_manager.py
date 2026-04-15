import os
import sys
import shutil
import zipfile
import subprocess
import threading
from typing import Optional, Callable

from . import logging_utils
from .downloader import TurboDownloader
from . import constants

logger = logging_utils.get_child_logger(__name__)

logger = logging_utils.get_child_logger(__name__)

# Constants for Python Installation
PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

ADDON_DIR = os.path.dirname(__file__)

class EngineManager:
    _lock = threading.Lock()
    _installing = False

    @staticmethod
    def get_python_exe() -> str:
        """Return the path to the shared python executable."""
        return os.path.join(constants.SHARED_ENGINE_DIR, 'python.exe')

    @classmethod
    def is_installed(cls) -> bool:
        """Check if the shared python engine is installed."""
        return os.path.exists(cls.get_python_exe())

    @classmethod
    def ensure_installed(cls, progress_callback: Optional[Callable] = None):
        """Thread-safe installation of the shared python environment."""
        if cls.is_installed():
            return True

        with cls._lock:
            if cls._installing:
                return False
            cls._installing = True

        try:
            os.makedirs(constants.SHARED_ENGINE_DIR, exist_ok=True)
            
            # 1. Download & Extract Python
            zip_path = os.path.join(constants.SHARED_ENGINE_DIR, 'python.zip')
            if not os.path.exists(cls.get_python_exe()):
                logger.info(f"Downloading Python from {PYTHON_EMBED_URL}")
                downloader = TurboDownloader(PYTHON_EMBED_URL, zip_path, progress_callback=progress_callback)
                downloader.start()
                
                logger.info("Extracting Python...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(constants.SHARED_ENGINE_DIR)
                
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                
                cls._configure_python_pth()

            # 2. Install Pip
            scripts_dir = os.path.join(constants.SHARED_ENGINE_DIR, 'Scripts')
            pip_exe = os.path.join(scripts_dir, 'pip.exe')
            if not os.path.exists(pip_exe):
                get_pip_path = os.path.join(constants.SHARED_ENGINE_DIR, 'get-pip.py')
                logger.info(f"Downloading Pip from {GET_PIP_URL}")
                downloader = TurboDownloader(GET_PIP_URL, get_pip_path)
                downloader.start()
                
                logger.info("Installing Pip...")
                cls._run_command([cls.get_python_exe(), get_pip_path])
                
                if os.path.exists(get_pip_path):
                    os.remove(get_pip_path)

            # 3. Install Core Foundations
            logger.info("Installing foundations (numpy, setuptools, wheel)...")
            cls._run_command([cls.get_python_exe(), '-m', 'pip', 'install', 'numpy<2.0.0', 'setuptools', 'wheel'])
            
            # Note: soundfile and others as needed. 
            # We skip heavy specific TTS libs here, they should be installed by respective managers if needed.
            # But numpy and soundfile are shared.
            cls._run_command([cls.get_python_exe(), '-m', 'pip', 'install', 'soundfile', 'regex', 'rdflib', 'importlib-metadata'])

            logger.info("EngineManager: Shared Python environment ready.")
            return True
        except Exception as e:
            logger.error(f"EngineManager: Installation failed: {e}")
            return False
        finally:
            try:
                with cls._lock:
                    cls._installing = False
            except Exception as cleanup_err:
                logger.error(f"EngineManager: Failed to clean up lock: {cleanup_err}")

    @staticmethod
    def _configure_python_pth():
        """Uncomment 'import site' in ._pth file to enable site-packages."""
        pth_files = [f for f in os.listdir(constants.SHARED_ENGINE_DIR) if f.endswith('._pth')]
        if pth_files:
            pth_path = os.path.join(constants.SHARED_ENGINE_DIR, pth_files[0])
            with open(pth_path, 'r') as f:
                content = f.read()
            
            if '#import site' in content:
                content = content.replace('#import site', 'import site')
                with open(pth_path, 'w') as f:
                    f.write(content)
                logger.info("EngineManager: Configured python._pth")

    @staticmethod
    def _run_command(cmd):
        """Run a command in the shared engine directory."""
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=constants.SHARED_ENGINE_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if process.returncode != 0:
            logger.error(f"Command failed: {' '.join(cmd)}\nError: {process.stderr}")
            raise Exception(f"Command failed with code {process.returncode}")
