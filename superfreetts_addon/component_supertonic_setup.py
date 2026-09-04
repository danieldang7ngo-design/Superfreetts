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

    def _get_venv_python(self):
        """Return the path to the Supertonic virtualenv python (Linux/macOS)."""
        if os.name == 'nt':
            return os.path.join(constants.SUPERTONIC_ENGINE_DIR, 'venv', 'Scripts', 'python.exe')
        return os.path.join(constants.SUPERTONIC_ENGINE_DIR, 'venv', 'bin', 'python')

    def _run_setup(self):
        try:
            service_logger.write_log("supertonic", "install", "INFO", "Starting Supertonic setup")
            os.makedirs(constants.SUPERTONIC_ENGINE_DIR, exist_ok=True)
            os.makedirs(constants.SUPERTONIC_CACHE_DIR, exist_ok=True)
            os.makedirs(constants.SUPERTONIC_CUSTOM_VOICES_DIR, exist_ok=True)

            import platform
            is_linux = platform.system() != "Windows"

            if is_linux:
                python_exe = self._setup_linux_venv()
            else:
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

    def _setup_linux_venv(self):
        """Create/refresh a dedicated virtual environment for Supertonic on Linux.

        Arch/CachyOS mark the system Python as externally managed (PEP 668),
        so pip cannot install into the system site-packages. We create an
        isolated venv inside the engine dir instead.
        """
        venv_python = self._get_venv_python()
        if os.path.exists(venv_python):
            return venv_python

        mw.taskman.run_on_main(lambda: self.log("Creating virtual environment for Supertonic..."))
        base_python = EngineManager.get_python_exe()
        if not base_python:
            base_python = "python3"
        self._run_command([base_python, "-m", "venv", os.path.join(constants.SUPERTONIC_ENGINE_DIR, 'venv')])
        return venv_python

    def _run_command(self, cmd, check=True):
        import platform
        cwd = constants.SHARED_ENGINE_DIR if platform.system() == "Windows" else None
        if cwd and not os.path.isdir(cwd):
            cwd = None
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors='replace',
            cwd=cwd,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if process.stdout:
            mw.taskman.run_on_main(lambda out=process.stdout[-1000:]: self.log(out.strip()))
        if check and process.returncode != 0:
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
            for path in (constants.SUPERTONIC_ENGINE_DIR, constants.SUPERTONIC_CACHE_DIR, constants.SUPERTONIC_CUSTOM_VOICES_DIR):
                if os.path.exists(path):
                    shutil.rmtree(path, ignore_errors=True)
            mw.taskman.run_on_main(self._clear_engine_path_config)
            mw.taskman.run_on_main(self.uninstall_complete)
        except Exception as exc:
            mw.taskman.run_on_main(lambda err=exc: self.setup_failed(str(err)))

    def setup_complete(self):
        self.progress_bar.setValue(100)
        self.status_label.setText(i18n.get_text("supertonic_setup_success", self.lang))
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        self.manage_btn.setEnabled(True)
        self._persist_engine_path()
        QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("supertonic_setup_success_msg", self.lang))
        self.accept()

    def _persist_engine_path(self):
        """Save the resolved python path into the addon config so
        _get_python_exe() finds it immediately after Anki restart."""
        import platform as _platform
        if _platform.system() == "Windows":
            return
        venv_python = self._get_venv_python()
        if not venv_python or not os.path.exists(venv_python):
            return
        try:
            addon_cfg = mw.addonManager.getConfig(constants.CONFIG_ADDON_NAME) or {}
            svc_cfg = addon_cfg.setdefault("configuration", {}).setdefault("service_config", {})
            st_cfg = svc_cfg.setdefault("SupertonicTTS", {})
            st_cfg["engine_path"] = venv_python
            mw.addonManager.writeConfig(constants.CONFIG_ADDON_NAME, addon_cfg)
        except Exception as exc:
            logging_utils.get_child_logger(__name__).warning(f"Failed to persist engine_path: {exc}")

    def _clear_engine_path_config(self):
        """Remove saved engine_path so _get_python_exe() falls back to runtime resolution."""
        try:
            addon_cfg = mw.addonManager.getConfig(constants.CONFIG_ADDON_NAME) or {}
            svc_cfg = addon_cfg.get("configuration", {}).get("service_config", {})
            st_cfg = svc_cfg.get("SupertonicTTS", {})
            st_cfg.pop("engine_path", None)
            mw.addonManager.writeConfig(constants.CONFIG_ADDON_NAME, addon_cfg)
        except Exception:
            pass

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
