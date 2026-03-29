
import os
import shutil
import zipfile
import urllib.request
import threading
from aqt import mw
from aqt.qt import *
from . import i18n
from . import gui_utils
from . import logging_utils
from . import component_piper_manager
from . import constants

logger = logging_utils.get_child_logger(__name__)

# Piper Engine release (Standard CPU optimized)
PIPER_ENGINE_URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"




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
        self.manage_models_btn.setEnabled(os.path.exists(constants.PIPER_EXE_PATH))

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

            zip_path = os.path.join(constants.PIPER_ENGINE_DIR, "piper.zip")
            
            if not os.path.exists(constants.PIPER_EXE_PATH):
                mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("piper_setup_downloading_engine", self.lang)))
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("piper_setup_downloading_github", self.lang)))
                
                urllib.request.urlretrieve(PIPER_ENGINE_URL, zip_path)
                
                mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("piper_setup_extracting_engine", self.lang)))
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("piper_setup_extracting_zip", self.lang)))
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(constants.PIPER_ENGINE_DIR)
                
                os.remove(zip_path)
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("piper_setup_extraction_complete", self.lang)))
            else:
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("piper_setup_already_exists", self.lang)))

            # Unified Engine & Sherpa-ONNX Library Setup
            from .engine_manager import EngineManager
            from .sherpa_manager import SherpaManager
            
            if not EngineManager.is_installed():
                mw.taskman.run_on_main(lambda: self.status_label.setText("Installing Python Engine..."))
                mw.taskman.run_on_main(lambda: self.log("Python engine not found. Downloading shared environment..."))
                
                def on_engine_progress(data):
                    percent = data['percent']
                    mw.taskman.run_on_main(lambda: self.status_label.setText(f"Installing Engine ({percent}%)"))
                
                EngineManager.ensure_installed(progress_callback=on_engine_progress)
                mw.taskman.run_on_main(lambda: self.log("Python engine integrated."))

            if not SherpaManager.is_installed():
                mw.taskman.run_on_main(lambda: self.status_label.setText("Installing Sherpa-ONNX Library..."))
                mw.taskman.run_on_main(lambda: self.log("Sherpa-ONNX not found. Downloading unified library..."))
                
                # Use a simple progress wrapper
                def on_lib_progress(data):
                    percent = data['percent']
                    mw.taskman.run_on_main(lambda: self.status_label.setText(f"Installing Sherpa-ONNX ({percent}%)"))
                
                SherpaManager.ensure_installed(progress_callback=on_lib_progress)
                mw.taskman.run_on_main(lambda: self.log("Sherpa-ONNX library integrated."))

            mw.taskman.run_on_main(self.setup_complete)
        except Exception as e:
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

def show_piper_setup(parent=None):
    dlg = PiperSetupDialog(parent)
    dlg.exec()
