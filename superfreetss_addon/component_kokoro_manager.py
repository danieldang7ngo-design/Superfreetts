
import os
import sys
import shutil
import zipfile
import urllib.request
import subprocess
import threading
import json
import time

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip
from . import i18n
from . import logging_utils
from . import constants

logger = logging_utils.get_child_logger(__name__)

# Constants for Kokoro Installation
PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
# Update to v1.0 INT8 models for high performance
KOKORO_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
VOICES_BIN_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

# Local paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
KOKORO_ENGINE_DIR = os.path.join(DATA_DIR, 'kokoro_engine')
PYTHON_EXE = os.path.join(KOKORO_ENGINE_DIR, 'python.exe')
KOKORO_MODEL_PATH = os.path.join(KOKORO_ENGINE_DIR, 'kokoro-v1.0.int8.onnx')
VOICES_BIN_PATH = os.path.join(KOKORO_ENGINE_DIR, 'voices-v1.0.bin')

class KokoroInstallManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kokoro TTS Setup")
        self.setMinimumWidth(500)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Status Label
        self.status_label = QLabel("Ready to install Kokoro TTS Engine.")
        self.layout.addWidget(self.status_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)
        
        # Log Area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.layout.addWidget(self.log_area)

        # Buttons
        self.button_box = QDialogButtonBox()
        self.install_btn = QPushButton("Install Kokoro Engine")
        self.install_btn.clicked.connect(self.start_installation)
        self.button_box.addButton(self.install_btn, QDialogButtonBox.ButtonRole.ActionRole)
        self.close_btn = self.button_box.addButton(QDialogButtonBox.StandardButton.Close)
        self.close_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.button_box)

        self.worker_thread = None

    def log(self, message):
        self.log_area.append(message)
        # Scroll to bottom
        sb = self.log_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def update_status(self, message):
        self.status_label.setText(message)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def start_installation(self):
        self.install_btn.setEnabled(False)
        self.log("Starting installation process...")
        
        # Run in background to not freeze UI
        self.worker_thread = threading.Thread(target=self._install_worker)
        self.worker_thread.start()

    def _install_worker(self):
        try:
            self._ensure_dir(KOKORO_ENGINE_DIR)
            
            # Step 1: Download Python Embeddable
            if not os.path.exists(PYTHON_EXE):
                self._download_file(PYTHON_EMBED_URL, os.path.join(KOKORO_ENGINE_DIR, 'python.zip'), "Downloading Python Engine...", 10)
                self._extract_zip(os.path.join(KOKORO_ENGINE_DIR, 'python.zip'), KOKORO_ENGINE_DIR, "Extracting Python...", 20)
                # Step 2: Configure Python (Uncomment import site) - Only need if just extracted
                self._configure_python_pth()
            else:
                self.log("Python Engine already exists, skipping download.")
            
            # Step 3: Install Pip
            scripts_dir = os.path.join(KOKORO_ENGINE_DIR, 'Scripts')
            pip_exe = os.path.join(scripts_dir, 'pip.exe')
            if not os.path.exists(pip_exe):
                self._download_file(GET_PIP_URL, os.path.join(KOKORO_ENGINE_DIR, 'get-pip.py'), "Downloading Pip...", 30)
                self._run_command([PYTHON_EXE, 'get-pip.py'], "Installing Pip...", 40)
            else:
                self.log("Pip already installed, skipping.")
            
            # Step 4: Install Dependencies
            self._run_command([PYTHON_EXE, '-m', 'pip', 'install', 'kokoro-onnx', 'soundfile'], "Checking/Installing Libraries (kokoro-onnx)...", 60)
            
            # Step 5: Download Model
            if not os.path.exists(KOKORO_MODEL_PATH):
                self._download_file(KOKORO_MODEL_URL, KOKORO_MODEL_PATH, "Downloading Kokoro Model INT8 (88MB)...", 80)
                # Clean up old 330MB model if it exists to save space
                old_model = os.path.join(KOKORO_ENGINE_DIR, 'kokoro-v1.0.onnx')
                if os.path.exists(old_model):
                    self.log("Cleaning up old 330MB model file...")
                    try: os.remove(old_model)
                    except: pass
            else:
                self.log("Kokoro Model v1.0 INT8 already exists, skipping.")

            if not os.path.exists(VOICES_BIN_PATH):
                self._download_file(VOICES_BIN_URL, VOICES_BIN_PATH, "Downloading Voices Data...", 90)
            else:
                self.log("Voices Data v1.0 already exists, skipping.")

            mw.taskman.run_on_main(lambda: self.update_status("Installation Complete!"))
            mw.taskman.run_on_main(lambda: self.update_progress(100))
            mw.taskman.run_on_main(lambda: self.log("Success: Kokoro Engine is ready."))
            mw.taskman.run_on_main(lambda: showInfo("Kokoro TTS Engine installed successfully!"))

        except Exception as e:
            error_msg = str(e)
            mw.taskman.run_on_main(lambda: self.log(f"Error: {error_msg}"))
            mw.taskman.run_on_main(lambda: self.update_status("Installation Failed."))
        finally:
            mw.taskman.run_on_main(lambda: self.install_btn.setEnabled(True))

    def _ensure_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _download_file(self, url, dest, status_msg, progress_val):
        mw.taskman.run_on_main(lambda: self.update_status(status_msg))
        mw.taskman.run_on_main(lambda: self.update_progress(progress_val))
        mw.taskman.run_on_main(lambda: self.log(f"Downloading {url}..."))
        
        # Simple download with progress hook if needed, for now blocking is okay in thread
        urllib.request.urlretrieve(url, dest)
        mw.taskman.run_on_main(lambda: self.log(f"Downloaded to {dest}"))

    def _extract_zip(self, zip_path, extract_to, status_msg, progress_val):
        mw.taskman.run_on_main(lambda: self.update_status(status_msg))
        mw.taskman.run_on_main(lambda: self.update_progress(progress_val))
        mw.taskman.run_on_main(lambda: self.log(f"Extracting {zip_path}..."))
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Cleanup zip
        os.remove(zip_path)

    def _configure_python_pth(self):
        # We need to uncomment 'import site' in python3xx._pth to make pip work
        pth_files = [f for f in os.listdir(KOKORO_ENGINE_DIR) if f.endswith('._pth')]
        if pth_files:
            pth_path = os.path.join(KOKORO_ENGINE_DIR, pth_files[0])
            with open(pth_path, 'r') as f:
                content = f.read()
            
            content = content.replace('#import site', 'import site')
            
            with open(pth_path, 'w') as f:
                f.write(content)
            mw.taskman.run_on_main(lambda: self.log("Configured python._pth"))

    def _run_command(self, cmd, status_msg, progress_val):
        mw.taskman.run_on_main(lambda: self.update_status(status_msg))
        mw.taskman.run_on_main(lambda: self.update_progress(progress_val))
        mw.taskman.run_on_main(lambda: self.log(f"Running: {' '.join(cmd)}"))
        
        # Run command and capture output
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            cwd=KOKORO_ENGINE_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        for line in process.stdout:
            mw.taskman.run_on_main(lambda l=line: self.log(f"CMD: {l.strip()}"))
        
        process.wait()
        if process.returncode != 0:
            raise Exception(f"Command failed with code {process.returncode}")

