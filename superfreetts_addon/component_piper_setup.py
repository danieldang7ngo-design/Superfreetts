
import os
import shutil
import threading
import platform
from aqt import mw
from aqt.qt import *
from . import archive_utils
from . import i18n
from . import gui_utils
from . import logging_utils
from . import component_piper_manager
from . import constants
from . import service_logger
from .download_sources import (
    PIPER_ENGINE_SHA256_LINUX,
    PIPER_ENGINE_SHA256_WINDOWS,
    PIPER_ENGINE_SIZE_LINUX,
    PIPER_ENGINE_SIZE_WINDOWS,
    PIPER_ENGINE_URL_LINUX_X86_64,
    PIPER_ENGINE_URL_WINDOWS,
)

logger = logging_utils.get_child_logger(__name__)

def _get_piper_url():
    """Return the platform-appropriate Piper download URL."""
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Windows":
        return PIPER_ENGINE_URL_WINDOWS
    if system == "Linux" and machine in ("x86_64", "amd64"):
        return PIPER_ENGINE_URL_LINUX_X86_64
    raise RuntimeError(f"Unsupported platform: {system} {machine}. Piper only has prebuilt binaries for Windows x64 and Linux x86_64.")




class PiperSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = mw.pm.meta.get("superfreetts_lang", "en")
        self.setWindowTitle(i18n.get_text("piper_setup_title", self.lang))
        self.setMinimumWidth(500)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.status_label = QLabel(i18n.get_text("piper_setup_ready", self.lang))
        self.layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        self.layout.addWidget(self.log_area)

        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton(i18n.get_text("piper_setup_button_install", self.lang))
        self.install_btn.clicked.connect(self.start_setup)
        gui_utils.configure_primary_button(self.install_btn)
        
        self.manage_models_btn = QPushButton(i18n.get_text("piper_setup_button_manage", self.lang))
        self.manage_models_btn.clicked.connect(self.open_model_manager)
        piper_binary = 'piper.exe' if os.name == 'nt' else 'piper'
        self.manage_models_btn.setEnabled(os.path.exists(os.path.join(constants.PIPER_ENGINE_DIR, 'piper', piper_binary)))

        self.uninstall_btn = QPushButton(i18n.get_text("piper_setup_button_uninstall", self.lang))
        self.uninstall_btn.clicked.connect(self.start_uninstall)
        gui_utils.configure_secondary_button(self.uninstall_btn)
        
        self.close_btn = QPushButton(i18n.get_text("button_close", self.lang))
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.uninstall_btn)
        btn_layout.addWidget(self.manage_models_btn)
        btn_layout.addWidget(self.install_btn)
        btn_layout.addWidget(self.close_btn)
        self.layout.addLayout(btn_layout)

    def log(self, text):
        self.log_area.append(text)

    def start_setup(self):
        self.install_btn.setEnabled(False)
        self.uninstall_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        threading.Thread(target=self._run_setup).start()

    def _run_setup(self):
        try:
            if not os.path.exists(constants.PIPER_ENGINE_DIR):
                os.makedirs(constants.PIPER_ENGINE_DIR, exist_ok=True)
            
            if not os.path.exists(constants.PIPER_MODELS_DIR):
                os.makedirs(constants.PIPER_MODELS_DIR, exist_ok=True)

            service_logger.write_log('piper', 'install', 'INFO', 'Starting Piper setup')

            piper_binary = 'piper.exe' if os.name == 'nt' else 'piper'
            piper_exe_path = os.path.join(constants.PIPER_ENGINE_DIR, 'piper', piper_binary)
            
            if not os.path.exists(piper_exe_path):
                piper_url = _get_piper_url()
                mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("piper_setup_downloading_engine", self.lang)))
                mw.taskman.run_on_main(lambda: self.log(f"Downloading Piper from {piper_url}"))
                
                is_zip = piper_url.endswith('.zip')
                archive_path = os.path.join(constants.PIPER_ENGINE_DIR, "piper.zip" if is_zip else "piper.tar.gz")
                expected_sha256 = PIPER_ENGINE_SHA256_WINDOWS if is_zip else PIPER_ENGINE_SHA256_LINUX
                expected_size = PIPER_ENGINE_SIZE_WINDOWS if is_zip else PIPER_ENGINE_SIZE_LINUX
                from .downloader import TurboDownloader

                def on_download_progress(data):
                    percent = int(data.get("percent", 0))
                    speed = data.get("speed_mb", 0)
                    mw.taskman.run_on_main(lambda p=percent: self.progress_bar.setValue(min(p, 70)))
                    mw.taskman.run_on_main(lambda p=percent, s=speed: self.status_label.setText(
                        i18n.get_text("piper_setup_downloading_engine", self.lang) + f" ({p}%, {s:.1f} MB/s)"
                    ))

                downloader = TurboDownloader(
                    piper_url,
                    archive_path,
                    progress_callback=on_download_progress,
                    expected_sha256=expected_sha256,
                    expected_size=expected_size,
                )
                downloader.start()
                
                mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("piper_setup_extracting_engine", self.lang)))
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("piper_setup_extracting_zip", self.lang)))
                
                if is_zip:
                    archive_utils.safe_extract(archive_path, constants.PIPER_ENGINE_DIR, archive_type="zip")
                else:
                    archive_utils.safe_extract(archive_path, constants.PIPER_ENGINE_DIR, archive_type="tar")
                    # Make piper binary executable on Linux
                    piper_binary_path = os.path.join(constants.PIPER_ENGINE_DIR, 'piper', 'piper')
                    if os.path.exists(piper_binary_path):
                        # Executable bit on a downloaded binary; no write
                        # permission is granted to group/other users.
                        os.chmod(piper_binary_path, 0o755)  # nosec B103
                
                os.remove(archive_path)
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("piper_setup_extraction_complete", self.lang)))
            else:
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("piper_setup_already_exists", self.lang)))
                service_logger.write_log('piper', 'install', 'INFO', 'Piper engine already exists, skipping download')


            # Unified Engine Setup (Portable Python on Windows, system Python on Linux)
            from .engine_manager import EngineManager
            
            if not EngineManager.is_installed():
                mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("piper_setup_installing_runtime", self.lang)))
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("piper_setup_runtime_not_found", self.lang)))
                
                def on_engine_progress(data):
                    percent = data['percent']
                    mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("piper_setup_installing_progress", self.lang).format(percent)))
                    mw.taskman.run_on_main(lambda: self.progress_bar.setValue(percent))
                
                EngineManager.ensure_installed(progress_callback=on_engine_progress)
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("piper_setup_runtime_integrated", self.lang)))

            # Note: Sherpa-ONNX library is no longer required for Piper (Stock)
            # It will still be installed by Kokoro/MMS if needed.

            mw.taskman.run_on_main(self.setup_complete)
            service_logger.write_log('piper', 'install', 'OK', 'Piper setup complete')
        except Exception as e:
            service_logger.write_log('piper', 'install', 'ERROR', f'Piper setup failed: {e}')
            mw.taskman.run_on_main(lambda err=e: self.setup_failed(str(err)))

    def start_uninstall(self):
        if QMessageBox.question(self, i18n.get_text("piper_setup_button_uninstall", self.lang), 
                               i18n.get_text("piper_setup_uninstall_confirm", self.lang)) != QMessageBox.StandardButton.Yes:
            return
            
        self.install_btn.setEnabled(False)
        self.uninstall_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        threading.Thread(target=self._run_uninstall).start()

    def _run_uninstall(self):
        try:
            mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("piper_setup_status_uninstalling", self.lang)))
            
            # Delete Engine
            if os.path.exists(constants.PIPER_ENGINE_DIR):
                shutil.rmtree(constants.PIPER_ENGINE_DIR, ignore_errors=True)
                
            # Delete Models
            if os.path.exists(constants.PIPER_MODELS_DIR):
                shutil.rmtree(constants.PIPER_MODELS_DIR, ignore_errors=True)
                
            mw.taskman.run_on_main(self.uninstall_complete)
        except Exception as e:
            mw.taskman.run_on_main(lambda err=e: self.setup_failed(str(err)))

    def setup_complete(self):
        self.status_label.setText(i18n.get_text("piper_setup_success", self.lang))
        self.progress_bar.setValue(100)
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        self.manage_models_btn.setEnabled(True)
        QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("piper_setup_success_msg", self.lang))
        self.open_model_manager()
        self.accept()  # Close dialog and return True so engine_path gets set

    def uninstall_complete(self):
        self.status_label.setText(i18n.get_text("piper_setup_uninstall_success", self.lang))
        self.progress_bar.setValue(100)
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        self.manage_models_btn.setEnabled(False)
        QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("piper_setup_uninstall_success", self.lang))

    def setup_failed(self, err):
        self.status_label.setText(i18n.get_text("piper_setup_failed", self.lang))
        self.log(f"Error: {err}")
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        QMessageBox.critical(self, i18n.get_text("generic_error", self.lang), i18n.get_text("piper_setup_failed_msg", self.lang).format(err))

    def open_model_manager(self):
        # Open the existing Piper Manager to download voices
        dlg = component_piper_manager.PiperManagerDialog(self, constants.PIPER_MODELS_DIR)
        dlg.exec()

