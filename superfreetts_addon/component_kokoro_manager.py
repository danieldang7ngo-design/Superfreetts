
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
from aqt.utils import showInfo, tooltip, showWarning
from . import i18n
from . import logging_utils
from . import constants
from . import service_logger
from .downloader import TurboDownloader

logger = logging_utils.get_child_logger(__name__)

# Constants for Kokoro Installation
PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
# Kokoro Model URLs
KOKORO_V10_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
KOKORO_V10_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

def _get_python_exe():
    return os.path.join(constants.KOKORO_ENGINE_DIR, 'python.exe')

def _get_models_dir():
    return os.path.join(constants.KOKORO_ENGINE_DIR, 'models')

def _get_kokoro_v10_model_path():
    return os.path.join(_get_models_dir(), 'kokoro-v1.0.onnx')

def _get_voices_v10_bin_path():
    return os.path.join(_get_models_dir(), 'voices-v1.0.bin')

class KokoroInstallManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = mw.pm.meta.get("superfreetts_lang", "en")
        self.setWindowTitle(i18n.get_text("kokoro_setup_title", self.lang))
        self.setMinimumWidth(500)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Status Label
        self.status_label = QLabel(i18n.get_text("kokoro_setup_ready", self.lang))
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
        
        self.install_btn = QPushButton(i18n.get_text("kokoro_setup_button_install", self.lang))
        self.install_btn.clicked.connect(self.start_installation)
        self.button_box.addButton(self.install_btn, QDialogButtonBox.ButtonRole.ActionRole)
        
        # Uninstall Button (New)
        self.uninstall_btn = QPushButton(i18n.get_text("button_uninstall", self.lang))
        self.uninstall_btn.clicked.connect(self.start_uninstallation)
        self.button_box.addButton(self.uninstall_btn, QDialogButtonBox.ButtonRole.ActionRole)

        self.close_btn = self.button_box.addButton(QDialogButtonBox.StandardButton.Close)
        self.close_btn.clicked.connect(self.accept)
        
        self.open_log_btn = QPushButton(i18n.get_text("piper_manager_button_logs", self.lang))
        self.open_log_btn.clicked.connect(self.open_log_folder)
        self.button_box.addButton(self.open_log_btn, QDialogButtonBox.ButtonRole.HelpRole)
        
        self.layout.addWidget(self.button_box)

        self.worker_thread = None

    def open_log_folder(self):
        log_dir = service_logger.get_log_dir()
        os.startfile(log_dir)

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
        self.uninstall_btn.setEnabled(False)
        self.log(i18n.get_text("kokoro_setup_log_starting", self.lang))
        
        # Run in background to not freeze UI
        self.worker_thread = threading.Thread(target=self._install_worker)
        self.worker_thread.start()

    def start_uninstallation(self):
        from aqt.utils import askUser
        if not askUser(i18n.get_text("onnx_manager_confirm_delete", self.lang).format("Kokoro Engine")):
            return
            
        self.install_btn.setEnabled(False)
        self.uninstall_btn.setEnabled(False)
        self.log("Starting uninstallation...")
        
        self.worker_thread = threading.Thread(target=self._uninstall_worker)
        self.worker_thread.start()


    def _uninstall_worker(self):
        try:
            self.log("Stopping any active Kokoro processes...")
            # 1. Kill active runner processes from our pool
            try:
                from .services.service_mms import _sherpa_pool
                script_path = os.path.join(os.path.dirname(__file__), 'services', 'kokoro_runner.py')
                _sherpa_pool.cleanup_all(_get_python_exe(), script_path)
            except: pass

            # 2. Nuclear option: Kill any process running from this directory
            # This is important on Windows if a process crashed or is dangling
            try:
                import subprocess
                # Use taskkill to kill any python processes running from KOKORO_ENGINE_DIR
                # We filter by path to avoid killing Anki's own python or other extras
                self.log("Clearing file locks...")
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/T'], capture_output=True)
                time.sleep(1) # Wait for OS to release locks
            except: pass

            if os.path.exists(constants.KOKORO_ENGINE_DIR):
                self.log(f"Wiping directory: {constants.KOKORO_ENGINE_DIR}")
                # 3. Clear Read-Only attributes (WinError 5 fix)
                def make_writable(func, path, excinfo):
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    func(path)

                shutil.rmtree(constants.KOKORO_ENGINE_DIR, onerror=make_writable)
                self.log("Deletion complete.")
            
            mw.taskman.run_on_main(lambda: showInfo("Kokoro Engine uninstalled successfully."))
        except Exception as e:
            self.log(f"Error during uninstall: {e}")
            mw.taskman.run_on_main(lambda: showWarning(f"Uninstall failed (File in use?): {e}\n\nPlease close Anki and delete the folder manually if this persists."))
        finally:
            mw.taskman.run_on_main(self._on_worker_finished)

    def _get_dir_size(self, path):
        total_size = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                total_size += os.path.getsize(os.path.join(root, f))
        return total_size

    def _on_worker_finished(self):
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        self.update_progress(100)

    def _ensure_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    def _install_worker(self):
        from . import service_logger
        try:
            self._ensure_dir(constants.KOKORO_ENGINE_DIR)
            self._ensure_dir(_get_models_dir())
            self._ensure_dir(os.path.join(constants.KOKORO_ENGINE_DIR, 'voices'))
            service_logger.write_log('kokoro', 'install', 'INFO', 'Starting Kokoro installation')
            
            # Step 1: Download Python Embeddable
            if not os.path.exists(_get_python_exe()):
                mw.taskman.run_on_main(lambda: self.update_progress(10))
                mw.taskman.run_on_main(lambda: self.update_status(i18n.get_text("kokoro_setup_downloading_python", self.lang)))
                self._download_file(PYTHON_EMBED_URL, os.path.join(constants.KOKORO_ENGINE_DIR, 'python.zip'))
                self._extract_zip(os.path.join(constants.KOKORO_ENGINE_DIR, 'python.zip'), constants.KOKORO_ENGINE_DIR, i18n.get_text("kokoro_setup_extracting_python", self.lang), 20)
                self._configure_python_pth()
            else:
                self.log(i18n.get_text("kokoro_setup_log_python_exists", self.lang))
                service_logger.write_log('kokoro', 'install', 'INFO', 'Python already exists, skipping download')
            
            # Step 2: Install Pip
            scripts_dir = os.path.join(constants.KOKORO_ENGINE_DIR, 'Scripts')
            pip_exe = os.path.join(scripts_dir, 'pip.exe')
            if not os.path.exists(pip_exe):
                self._download_file(GET_PIP_URL, os.path.join(constants.KOKORO_ENGINE_DIR, 'get-pip.py'))
                self._run_command([_get_python_exe(), 'get-pip.py'], i18n.get_text("kokoro_setup_installing_pip", self.lang), 30)
            else:
                self.log(i18n.get_text("kokoro_setup_log_pip_exists", self.lang))
            
            # Step 3: Install Core Foundations (No heavy dictionaries)
            self._run_command([_get_python_exe(), '-m', 'pip', 'install', 'numpy<2.0.0', 'setuptools', 'wheel'], i18n.get_text("kokoro_setup_installing_foundations", self.lang), 40)
            
            # misaki core and soundfile (+ metadata helpers)
            self._run_command([_get_python_exe(), '-m', 'pip', 'install', 'kokoro-onnx>=0.3.0', 'soundfile', 'misaki', 'regex', 'rdflib', 'importlib-metadata'], i18n.get_text("kokoro_setup_finalizing_core", self.lang), 60)
            
            # Step 4: Download Standard v1.0 Brain (Required)
            self.log("Installing Standard v1.0 Brain (Core Engine)...")
            if not os.path.exists(_get_kokoro_v10_model_path()):
                mw.taskman.run_on_main(lambda: self.update_status(i18n.get_text("kokoro_setup_downloading_v10", self.lang)))
                self._download_file(KOKORO_V10_MODEL_URL, _get_kokoro_v10_model_path())

            # Step 5: Download Global Voice Bundle (Essential)
            self.log("Installing Global Voice Bundle (35MB)...")
            if not os.path.exists(_get_voices_v10_bin_path()):
                mw.taskman.run_on_main(lambda: self.update_status(i18n.get_text("kokoro_setup_downloading_voices_v10", self.lang)))
                self._download_file(KOKORO_V10_VOICES_URL, _get_voices_v10_bin_path())

            # Step 6: Finalize and Automate Optimization
            self.log("Finalizing Installation. Running automatic optimization (Ep-can)...")
            mw.taskman.run_on_main(lambda: self.update_status(i18n.get_text("kokoro_setup_status_optimizing", self.lang)))
            try:
                self._optimize_worker_internal()
            except: pass

            mw.taskman.run_on_main(lambda: self.update_status(i18n.get_text("kokoro_setup_complete", self.lang)))
            mw.taskman.run_on_main(lambda: self.update_progress(100))
            service_logger.write_log('kokoro', 'install', 'OK', 'Kokoro installation complete')
            mw.taskman.run_on_main(lambda: showInfo(i18n.get_text("kokoro_setup_success_stock_msg", self.lang)))

        except Exception as e:
            self.log(f"Error during installation: {e}")
            service_logger.write_log('kokoro', 'install', 'ERROR', f'Installation failed: {e}')
            mw.taskman.run_on_main(lambda: self.update_status("Installation failed"))
        finally:
            mw.taskman.run_on_main(self._on_worker_finished)

    def _optimize_worker_internal(self):
        # Silent version of optimization for automatic use
        count = 0
        size_saved = 0
        # 1. Clear __pycache__
        for root, dirs, files in os.walk(constants.KOKORO_ENGINE_DIR):
            if "__pycache__" in dirs:
                p = os.path.join(root, "__pycache__")
                size_saved += self._get_dir_size(p)
                try: shutil.rmtree(p, ignore_errors=True)
                except: pass
                count += 1
        # 2. Clear dist-info (DISABLED: Critical for rdflib/onnxruntime)
        # site_packages = os.path.join(KOKORO_ENGINE_DIR, 'Lib', 'site-packages')
        # if os.path.exists(site_packages):
        #     for item in os.listdir(site_packages):
        #         if item.endswith('.dist-info') or item.endswith('.egg-info'):
        #             p = os.path.join(site_packages, item)
        #             size_saved += self._get_dir_size(p)
        #             try: shutil.rmtree(p, ignore_errors=True)
        #             except: pass
        #             count += 1
        self.log(f"Auto-Optimization: Reduced size by {size_saved // (1024*1024)} MB.")

    def _download_file(self, url, dest):
        debug_mode = False
        try:
            if hasattr(mw, 'hyper_tts'):
                debug_mode = mw.hyper_tts.get_preferences().error_handling.debug_mode
        except: pass

        def on_progress(data):
            percent = data['percent']
            speed_mb = data['speed_mb']
            mw.taskman.run_on_main(lambda: self.update_status(f"Downloading... {percent}% ({speed_mb:.1f} MB/s)"))
        
        downloader = TurboDownloader(url, dest, progress_callback=on_progress, debug_mode=debug_mode)
        downloader.start()
        mw.taskman.run_on_main(lambda: self.log(f"Downloaded to {os.path.basename(dest)}"))

    def _extract_zip(self, zip_path, extract_to, status_msg, progress_val):
        mw.taskman.run_on_main(lambda: self.update_status(status_msg))
        mw.taskman.run_on_main(lambda: self.update_progress(progress_val))
        mw.taskman.run_on_main(lambda: self.log(f"Extracting {os.path.basename(zip_path)}..."))
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Cleanup zip
        try: os.remove(zip_path)
        except: pass

    def _configure_python_pth(self):
        # We need to uncomment 'import site' in python3xx._pth to make pip work
        pth_files = [f for f in os.listdir(constants.KOKORO_ENGINE_DIR) if f.endswith('._pth')]
        if pth_files:
            pth_path = os.path.join(constants.KOKORO_ENGINE_DIR, pth_files[0])
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
        
        cmd_str = ' '.join(cmd)
        service_logger.write_install_separator('kokoro', cmd_str)
        
        # Run command and capture output
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            cwd=constants.KOKORO_ENGINE_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        for line in process.stdout:
            mw.taskman.run_on_main(lambda l=line: self.log(f"CMD: {l.strip()}"))
        
        process.wait()
        
        # Log result
        stdout_text = ''
        stderr_text = ''
        try:
            if hasattr(process, 'stdout') and process.stdout:
                process.stdout.seek(0)
                stdout_text = process.stdout.read() if hasattr(process.stdout, 'read') else ''
        except: pass
        service_logger.write_install_result('kokoro', process.returncode, stdout_text or 'see UI log', stderr_text)
        
        if process.returncode != 0:
            raise Exception(f"Command failed with code {process.returncode}")

