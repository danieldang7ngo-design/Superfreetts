import os
import shutil

from aqt import mw
from aqt.qt import *

from . import constants
from . import gui_utils
from . import i18n
from .services import service_supertonic


class SupertonicVoiceManagerDialog(QDialog):
    def __init__(self, parent=None, voices_dir=None):
        super().__init__(parent)
        self.lang = mw.pm.meta.get("superfreetts_lang", "en")
        self.voices_dir = voices_dir or constants.SUPERTONIC_CUSTOM_VOICES_DIR
        self.setWindowTitle(i18n.get_text("supertonic_voice_manager_title", self.lang))
        self.setMinimumWidth(520)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.info_label = QLabel(i18n.get_text("supertonic_voice_manager_info", self.lang))
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        buttons = QHBoxLayout()
        self.import_btn = QPushButton(i18n.get_text("supertonic_voice_manager_import", self.lang))
        self.import_btn.clicked.connect(self.import_voice)
        gui_utils.configure_primary_button(self.import_btn)

        self.delete_btn = QPushButton(i18n.get_text("supertonic_voice_manager_delete", self.lang))
        self.delete_btn.clicked.connect(self.delete_selected)
        gui_utils.configure_secondary_button(self.delete_btn)

        self.close_btn = QPushButton(i18n.get_text("button_close", self.lang))
        self.close_btn.clicked.connect(self.accept)
        buttons.addStretch()
        buttons.addWidget(self.import_btn)
        buttons.addWidget(self.delete_btn)
        buttons.addWidget(self.close_btn)
        layout.addLayout(buttons)

        self.refresh()

    def refresh(self):
        os.makedirs(self.voices_dir, exist_ok=True)
        self.list_widget.clear()
        for path in service_supertonic.list_custom_voice_files(self.voices_dir):
            item = QListWidgetItem(service_supertonic.normalize_custom_voice_name(path))
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.list_widget.addItem(item)
        self.status_label.setText(
            i18n.get_text("supertonic_voice_manager_count", self.lang).format(self.list_widget.count())
        )

    def import_voice(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            i18n.get_text("supertonic_voice_manager_select_json", self.lang),
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return

        name = service_supertonic.normalize_custom_voice_name(path)
        if service_supertonic.is_reserved_voice_name(name):
            QMessageBox.warning(
                self,
                i18n.get_text("generic_error", self.lang),
                i18n.get_text("supertonic_voice_manager_reserved", self.lang).format(name),
            )
            return

        os.makedirs(self.voices_dir, exist_ok=True)
        dest = os.path.join(self.voices_dir, name + ".json")
        if os.path.exists(dest):
            reply = QMessageBox.question(
                self,
                i18n.get_text("generic_warning", self.lang),
                i18n.get_text("supertonic_voice_manager_overwrite", self.lang).format(name),
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            shutil.copy2(path, dest)
            self.refresh()
            QMessageBox.information(
                self,
                i18n.get_text("generic_success", self.lang),
                i18n.get_text("supertonic_voice_manager_imported", self.lang).format(name),
            )
        except Exception as exc:
            QMessageBox.critical(self, i18n.get_text("generic_error", self.lang), str(exc))

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.warning(
                self,
                i18n.get_text("generic_error", self.lang),
                i18n.get_text("supertonic_voice_manager_select_one", self.lang),
            )
            return

        name = item.text()
        path = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            i18n.get_text("generic_warning", self.lang),
            i18n.get_text("supertonic_voice_manager_confirm_delete", self.lang).format(name),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if path and os.path.exists(path):
                os.remove(path)
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, i18n.get_text("generic_error", self.lang), str(exc))
