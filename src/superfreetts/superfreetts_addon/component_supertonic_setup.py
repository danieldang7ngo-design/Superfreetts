import os
import shutil
import subprocess
import threading

from aqt import mw
from aqt.qt import *

from . import constants
from . import gui_utils
from . import i18n
from . import logging_utils
from . import service_logger
from .component_supertonic_voice_manager import SupertonicVoiceManagerDialog
from .engine_manager import EngineManager

logger = logging_utils.get_child_logger(__name__)


class SupertonicSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = mw.pm.meta.get("superfreetts_lang", "en")
        self.setWindowTitle(i18n.get_text("supertonic_setup_title", self.lang))
        self.setMinimumWidth(540)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.status_label = QLabel(i18n.get_text("supertonic_setup_ready", self.lang))
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(170)
        layout.addWidget(self.log_area)

        buttons = QHBoxLayout()
        self.uninstall_btn = QPushButton(i18n.get_text("supertonic_setup_button_uninstall", self.lang))
        self.uninstall_btn.clicked.connect(self.start_uninstall)
        gui_utils.configure_secondary_button(self.uninstall_btn)

        self.manage_btn = QPushButton(i18n.get_text("supertonic_setup_button_manage", self.lang))
        self.manage_btn.clicked.connect(self.open_voice_manager)
        self.manage_btn.setEnabled(os.path.exists(constants.SUPERTONIC_CUSTOM_VOICES_DIR))

        self.install_btn = QPushButton(i18n.get_text("supertonic_setup_button_install", self.lang))
        self.install_btn.clicked.connect(self.start_setup)
        gui_utils.configure_primary_button(self.install_btn)

        self.close_btn = QPushButton(i18n.get_text("button_close", self.lang))
        self.close_btn.clicked.connect(self.accept)

        buttons.addStretch()
        buttons.addWidget(self.uninstall_btn)
        buttons.addWidget(self.manage_btn)
        buttons.addWidget(self.install_btn)
        buttons.addWidget(self.close_btn)
        layout.addLayout(buttons)

    def log(self, text):
        self.log_area.append(text)

    def start_setup(self):
        self.install_btn.setEnabled(False)
        self.uninstall_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        threading.Thread(target=self._run_setup, daemon=True).start()

    def _run_setup(self):
        try:
            service_logger.write_log("supertonic", "install", "INFO", "Starting Supertonic setup")
            os.makedirs(constants.SUPERTONIC_ENGINE_DIR, exist_ok=True)
            os.makedirs(constants.SUPERTONIC_CACHE_DIR, exist_ok=True)
            os.makedirs(constants.SUPERTONIC_CUSTOM_VOICES_DIR, exist_ok=True)

            mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("supertonic_setup_installing_python", self.lang)))

            def on_engine_progress(data):
                percent = int(data.get("percent", 0))
                mw.taskman.run_on_main(lambda p=percent: self.progress_bar.setValue(min(p, 40)))

            if not EngineManager.ensure_installed(progress_callback=on_engine_progress):
                raise RuntimeError("Failed to install shared Python runtime")

            python_exe = EngineManager.get_python_exe()
            mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("supertonic_setup_installing_sdk", self.lang)))
            mw.taskman.run_on_main(lambda: self.log(i18n.get_text("supertonic_setup_log_pip", self.lang)))
            self._run_command([python_exe, "-m", "pip", "install", "--upgrade", "supertonic"])
            mw.taskman.run_on_main(lambda: self.progress_bar.setValue(65))

            mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("supertonic_setup_downloading_model", self.lang)))
            mw.taskman.run_on_main(lambda: self.log(i18n.get_text("supertonic_setup_log_model", self.lang)))
            self._download_model(python_exe)
            self._write_marker()

            service_logger.write_log("supertonic", "install", "OK", "Supertonic setup complete")
            mw.taskman.run_on_main(self.setup_complete)
        except Exception as exc:
            service_logger.write_log("supertonic", "install", "ERROR", f"Supertonic setup failed: {exc}")
            mw.taskman.run_on_main(lambda err=exc: self.setup_failed(str(err)))

    def _run_command(self, cmd):
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors='replace',
            cwd=constants.SHARED_ENGINE_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if process.stdout:
            mw.taskman.run_on_main(lambda out=process.stdout[-1000:]: self.log(out.strip()))
        if process.returncode != 0:
            raise RuntimeError(process.stderr.strip() or f"Command failed: {' '.join(cmd)}")

    def _download_model(self, python_exe):
        code = (
            "import os\n"
            f"os.environ['HF_HOME'] = r'{constants.SUPERTONIC_CACHE_DIR}'\n"
            f"os.environ['HUGGINGFACE_HUB_CACHE'] = r'{os.path.join(constants.SUPERTONIC_CACHE_DIR, 'hub')}'\n"
            "from supertonic import TTS\n"
            "try:\n"
            f"    TTS(auto_download=True, cache_dir=r'{constants.SUPERTONIC_CACHE_DIR}')\n"
            "except TypeError:\n"
            "    TTS(auto_download=True)\n"
        )
        self._run_command([python_exe, "-c", code])

    def _write_marker(self):
        marker = os.path.join(constants.SUPERTONIC_CACHE_DIR, "supertonic_model.ready")
        with open(marker, "w", encoding="utf-8") as handle:
            handle.write("ready\n")

    def start_uninstall(self):
        reply = QMessageBox.question(
            self,
            i18n.get_text("supertonic_setup_button_uninstall", self.lang),
            i18n.get_text("supertonic_setup_uninstall_confirm", self.lang),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.install_btn.setEnabled(False)
        self.uninstall_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        threading.Thread(target=self._run_uninstall, daemon=True).start()

    def _run_uninstall(self):
        try:
            mw.taskman.run_on_main(lambda: self.status_label.setText(i18n.get_text("supertonic_setup_uninstalling", self.lang)))
            for path in (constants.SUPERTONIC_CACHE_DIR, constants.SUPERTONIC_CUSTOM_VOICES_DIR):
                if os.path.exists(path):
                    shutil.rmtree(path, ignore_errors=True)
            mw.taskman.run_on_main(self.uninstall_complete)
        except Exception as exc:
            mw.taskman.run_on_main(lambda err=exc: self.setup_failed(str(err)))

    def setup_complete(self):
        self.progress_bar.setValue(100)
        self.status_label.setText(i18n.get_text("supertonic_setup_success", self.lang))
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        self.manage_btn.setEnabled(True)
        QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("supertonic_setup_success_msg", self.lang))
        self.accept()

    def uninstall_complete(self):
        self.progress_bar.setValue(100)
        self.status_label.setText(i18n.get_text("supertonic_setup_uninstall_success", self.lang))
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        self.manage_btn.setEnabled(False)
        QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("supertonic_setup_uninstall_success", self.lang))

    def setup_failed(self, err):
        self.status_label.setText(i18n.get_text("supertonic_setup_failed", self.lang))
        self.log(f"Error: {err}")
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        QMessageBox.critical(self, i18n.get_text("generic_error", self.lang), i18n.get_text("supertonic_setup_failed_msg", self.lang).format(err))

    def open_voice_manager(self):
        dlg = SupertonicVoiceManagerDialog(self, constants.SUPERTONIC_CUSTOM_VOICES_DIR)
        dlg.exec()
