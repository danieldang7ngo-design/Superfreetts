import os
import aqt.qt

from . import component_common
from . import config_models
from . import constants
from .stats import Event
from . import gui_utils
from . import logging_utils
from . import stats
from . import i18n
from . import component_piper_manager
from . import component_kokoro_manager, component_mms_manager, component_supertonic_setup

logger = logging_utils.get_child_logger(__name__)
sc = stats.StatsContext(stats.EventContext.services)


class ServicesPage(component_common.ConfigComponentBase):

    @sc.event(Event.open)
    def __init__(self, hypertts, dialog):
        self.hypertts = hypertts
        self.dialog = dialog
        self.model = config_models.Configuration()
        self.service_checkbox_map = {}
        self.service_status_badge_map = {}
        self.service_search_index = {}
        self.service_expand_toggle_map = {}
        self.services_summary_label = None
        self.service_card_map = {}
        self._services_scroll_area = None
        self._services_container_widget = None
        self.enable_model_change = False
        self.api_key_valid = False
        self.search_debounce_timer = None
        self.option_validation_label_map = {}

    def get_model(self):
        return self.model

    def load_model(self, model):
        self.model = model

    def model_change(self):
        if self.enable_model_change:
            self.save_button.setEnabled(True)
            self.save_button.setProperty("cssClass", "primaryButton")
            self.save_button.style().unpolish(self.save_button)
            self.save_button.style().polish(self.save_button)
            self._refresh_service_status_badges()

    def _get_service_option_label(self, service, key, option_type):
        lang = self.hypertts.get_ui_language()
        label_key = f"service_option_{service.name}_{key}"
        translated_label = i18n.get_text(label_key, lang)
        if translated_label != label_key:
            if service.name == "EdgeTTS" and key == "concurrency_workers":
                max_workers = option_type[4] if isinstance(option_type, tuple) and len(option_type) > 4 else ''
                return translated_label.format(max_workers=max_workers)
            return translated_label

        if isinstance(option_type, tuple) and len(option_type) > 1:
            if option_type[0] in ['file', 'directory', 'number', 'bool']:
                return option_type[1]
        return key

    def _build_service_search_text(self, service, service_description):
        chunks = [service.name, service_description]

        try:
            for key, option_type in service.configuration_options().items():
                chunks.append(str(key))
                chunks.append(str(self._get_service_option_label(service, key, option_type)))
        except Exception:
            pass

        try:
            if hasattr(service, 'advanced_configuration_options'):
                for key, option_type in service.advanced_configuration_options().items():
                    chunks.append(str(key))
                    chunks.append(str(self._get_service_option_label(service, key, option_type)))
        except Exception:
            pass

        return ' '.join(chunks).lower()

    def _get_service_status_info(self, service):
        lang = self.hypertts.get_ui_language()
        enabled = bool(self.model.get_service_enabled(service.name))
        dark = gui_utils.is_night_mode()
        if not enabled:
            return (
                i18n.get_text("service_status_disabled", lang),
                '#334155' if dark else constants.COLOR_BORDER,
                '#CBD5E1' if dark else constants.COLOR_SECONDARY,
            )

        missing = 0
        configuration_options = service.configuration_options()
        for key, option_type in configuration_options.items():
            value = self.model.get_service_configuration_key(service.name, key)
            key_lower = key.lower()

            if isinstance(option_type, tuple) and option_type[0] in ['file', 'directory']:
                if not value or (isinstance(value, str) and not os.path.exists(value)):
                    missing += 1
                continue

            if option_type == str and any(token in key_lower for token in ['api', 'token', 'secret', 'key']):
                if value is None or (isinstance(value, str) and len(value.strip()) == 0):
                    missing += 1

        if missing > 0:
            return (
                i18n.get_text("service_status_setup_needed", lang),
                '#78350F' if dark else '#FEF3C7',
                '#FDE68A' if dark else '#92400E',
            )

        return (
            i18n.get_text("service_status_ready", lang),
            '#022C22' if dark else '#FFFFFF',
            '#34D399' if dark else '#059669',
        )

    def _refresh_service_status_badges(self):
        for service in self.get_service_list():
            badge = self.service_status_badge_map.get(service.name)
            if badge is None:
                continue
            text, bg, fg = self._get_service_status_info(service)
            badge.setText(text)
            badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg};
                    color: {fg};
                    border-radius: 10px;
                    padding: 2px 10px;
                    font-size: 10px;
                    font-weight: 600;
                }}
            """)

        self._refresh_services_summary_label()

    def _get_services_status_counts(self):
        lang = self.hypertts.get_ui_language()
        counts = {
            i18n.get_text("service_status_ready", lang): 0,
            i18n.get_text("service_status_setup_needed", lang): 0,
            i18n.get_text("service_status_disabled", lang): 0,
        }
        for service in self.get_service_list():
            status_text, _, _ = self._get_service_status_info(service)
            counts[status_text] = counts.get(status_text, 0) + 1
        return counts

    def _refresh_services_summary_label(self):
        if self.services_summary_label is None:
            return
        lang = self.hypertts.get_ui_language()
        counts = self._get_services_status_counts()
        self.services_summary_label.setText(
            i18n.get_text("services_summary_status", lang).format(
                counts.get(i18n.get_text("service_status_ready", lang), 0),
                counts.get(i18n.get_text("service_status_setup_needed", lang), 0),
                counts.get(i18n.get_text("service_status_disabled", lang), 0),
            )
        )
        self.services_summary_label.setStyleSheet(
            f"color: {constants.COLOR_SECONDARY}; font-size: 11px;"
        )

    def _set_validation_label(self, label: aqt.qt.QLabel, ok: bool, message: str):
        color = constants.COLOR_ACCENT_DARK if ok else constants.COLOR_ERROR
        label.setText(message)
        label.setStyleSheet(f"color: {color}; font-size: 10px; margin-top: 2px;")

    def _wire_required_text_validation(self, key, lineedit: aqt.qt.QLineEdit, label: aqt.qt.QLabel):
        lang = self.hypertts.get_ui_language()

        def update_message(text):
            if text and text.strip():
                self._set_validation_label(label, True, i18n.get_text("config_validation_value_set", lang))
            else:
                self._set_validation_label(label, False, i18n.get_text("config_validation_required", lang))

        lineedit.textChanged.connect(update_message)
        update_message(lineedit.text())

    def _wire_path_validation(self, lineedit: aqt.qt.QLineEdit, label: aqt.qt.QLabel):
        lang = self.hypertts.get_ui_language()

        def update_message(path_text):
            path = (path_text or "").strip()
            if not path:
                self._set_validation_label(label, False, i18n.get_text("config_validation_required", lang))
                return
            if os.path.exists(path):
                self._set_validation_label(label, True, i18n.get_text("config_validation_path_found", lang))
            else:
                self._set_validation_label(label, False, i18n.get_text("config_validation_path_missing", lang))

        lineedit.textChanged.connect(update_message)
        update_message(lineedit.text())

    def _supports_setup_shortcut(self, service) -> bool:
        return service.name in {"KokoroTTS", "MmsTTS", "PiperTTS", "SupertonicTTS"}

    def _set_service_config_value_with_ui_sync(self, service_name: str, key: str, value: str):
        self.model.set_service_configuration_key(service_name, key, value)
        widget_name = f'{service_name}_{key}'
        lineedit = self.dialog.findChild(aqt.qt.QLineEdit, widget_name)
        if lineedit is not None and lineedit.text() != value:
            lineedit.setText(value)
        self.model_change()

    def _open_setup_dialog_for_service(self, service):
        if service.name == "KokoroTTS":
            dlg = component_kokoro_manager.KokoroInstallManager(self.dialog)
            if dlg.exec():
                engine_path = component_kokoro_manager._get_python_exe()
                if os.path.exists(engine_path):
                    self._set_service_config_value_with_ui_sync(service.name, "engine_path", engine_path)
            return

        if service.name == "MmsTTS":
            dlg = component_mms_manager.MmsInstallManager(self.dialog)
            dlg.exec()
            self.hypertts.service_manager.clear_voice_list_cache()
            self.model_change()

            from .mms_engine_manager import MmsEngineManager
            engine_path = MmsEngineManager.get_python_exe()
            if os.path.exists(engine_path):
                self._set_service_config_value_with_ui_sync(service.name, "engine_path", engine_path)
            return

        if service.name == "PiperTTS":
            from . import component_piper_setup
            dlg = component_piper_setup.PiperSetupDialog(self.dialog)
            dlg.exec()
            if os.path.exists(constants.PIPER_ENGINE_DIR):
                self._set_service_config_value_with_ui_sync(service.name, "executable_path", constants.PIPER_ENGINE_DIR)
            return

        if service.name == "SupertonicTTS":
            dlg = component_supertonic_setup.SupertonicSetupDialog(self.dialog)
            dlg.exec()
            self.hypertts.service_manager.clear_voice_list_cache()
            self.model_change()
            from .engine_manager import EngineManager
            engine_path = EngineManager.get_python_exe()
            if os.path.exists(engine_path):
                self._set_service_config_value_with_ui_sync(service.name, "engine_path", engine_path)
            if os.path.exists(constants.SUPERTONIC_CACHE_DIR):
                self._set_service_config_value_with_ui_sync(service.name, "cache_path", constants.SUPERTONIC_CACHE_DIR)
            if os.path.exists(constants.SUPERTONIC_CUSTOM_VOICES_DIR):
                self._set_service_config_value_with_ui_sync(service.name, "custom_voices_path", constants.SUPERTONIC_CUSTOM_VOICES_DIR)
            return

    def get_service_enable_change_fn(self, service):
        def enable_change(value):
            enabled = value == 2
            logger.info(f'{service.name} enabled: {enabled}')
            self.model.set_service_enabled(service.name, enabled)
            self.model_change()
        return enable_change

    def get_service_config_str_change_fn(self, service, key):
        def str_change(text):
            logger.info(f'{service.name} {key}: {text}')
            self.model.set_service_configuration_key(service.name, key, text)
            self.model_change()
        return str_change

    def get_service_config_int_change_fn(self, service, key):
        def int_change(value):
            logger.info(f'{service.name} {key}: {value}')
            self.model.set_service_configuration_key(service.name, key, value)
            self.model_change()
        return int_change

    def get_service_config_float_change_fn(self, service, key):
        def float_change(value):
            logger.info(f'{service.name} {key}: {value}')
            self.model.set_service_configuration_key(service.name, key, value)
            self.model_change()
        return float_change

    def get_service_config_list_change_fn(self, service, key):
        def list_change(text):
            logger.info(f'{service.name} {key}: {text}')
            self.model.set_service_configuration_key(service.name, key, text)
            self.model_change()
        return list_change

    def get_service_config_bool_change_fn(self, service, key):
        def bool_change(checkbox_value):
            value = checkbox_value == 2
            logger.info(f'{service.name} {key}: {value}')
            self.model.set_service_configuration_key(service.name, key, value)
            self.model_change()
        return bool_change

    def get_service_enabled_widget_name(self, service):
        return f'{service.name}_enabled'

    def draw_service_options(self, service, layout):
        lang = self.hypertts.get_ui_language()
        service_enabled_checkbox = aqt.qt.QCheckBox(i18n.get_text("generic_enable", lang))
        service_enabled_checkbox.setObjectName(self.get_service_enabled_widget_name(service))
        service_enabled_checkbox.setChecked(service.enabled)
        self.service_checkbox_map[service.name] = service_enabled_checkbox
        service_enabled_checkbox.stateChanged.connect(self.get_service_enable_change_fn(service))
        service_enabled_checkbox.setVisible(False)

        configuration_options = service.configuration_options()
        options_gridlayout = aqt.qt.QGridLayout()
        row = 0
        for key, type in configuration_options.items():
            widget_name = f'{service.name}_{key}'
            label_text = self._get_service_option_label(service, key, type) + ':'

            options_gridlayout.addWidget(aqt.qt.QLabel(label_text), row, 0, 1, 1)
            if type == str:
                lineedit = aqt.qt.QLineEdit()
                lineedit.setText(self.model.get_service_configuration_key(service.name, key))
                lineedit.setObjectName(widget_name)
                lineedit.textChanged.connect(self.get_service_config_str_change_fn(service, key))
                if any(token in key.lower() for token in ['api', 'token', 'secret', 'key']):
                    validation_label = aqt.qt.QLabel()
                    validation_label.setWordWrap(True)
                    self.option_validation_label_map[f"{service.name}_{key}"] = validation_label
                    v_layout = aqt.qt.QVBoxLayout()
                    v_layout.addWidget(lineedit)
                    v_layout.addWidget(validation_label)
                    self._wire_required_text_validation(key, lineedit, validation_label)
                    options_gridlayout.addLayout(v_layout, row, 1, 1, 1)
                else:
                    options_gridlayout.addWidget(lineedit, row, 1, 1, 1)
            elif type == int:
                spinbox = aqt.qt.QSpinBox()
                saved_value = self.model.get_service_configuration_key(service.name, key)
                if saved_value != None:
                    spinbox.setValue(saved_value)
                spinbox.setObjectName(widget_name)
                spinbox.valueChanged.connect(self.get_service_config_int_change_fn(service, key))
                options_gridlayout.addWidget(spinbox, row, 1, 1, 1)
            elif type == float:
                spinbox = aqt.qt.QDoubleSpinBox()
                saved_value = self.model.get_service_configuration_key(service.name, key)
                if saved_value != None:
                    spinbox.setValue(saved_value)
                spinbox.setObjectName(widget_name)
                spinbox.valueChanged.connect(self.get_service_config_float_change_fn(service, key))
                options_gridlayout.addWidget(spinbox, row, 1, 1, 1)
            elif type == bool:
                checkbox = aqt.qt.QCheckBox()
                saved_value = self.model.get_service_configuration_key(service.name, key)
                if saved_value != None:
                    checkbox.setChecked(saved_value)
                checkbox.setObjectName(widget_name)
                checkbox.stateChanged.connect(self.get_service_config_bool_change_fn(service, key))
                options_gridlayout.addWidget(checkbox, row, 1, 1, 1)
            elif isinstance(type, tuple) and type[0] == 'file':
                filter_str = type[2] if len(type) > 2 else type[1]
                h_layout = aqt.qt.QHBoxLayout()

                lineedit = aqt.qt.QLineEdit()
                lineedit.setText(self.model.get_service_configuration_key(service.name, key))
                lineedit.setObjectName(widget_name)
                lineedit.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Fixed)
                lineedit.textChanged.connect(self.get_service_config_str_change_fn(service, key))

                btn = aqt.qt.QPushButton("Browse...")
                def browse_file(le=lineedit, f=filter_str):
                    path, _ = aqt.qt.QFileDialog.getOpenFileName(self.dialog, i18n.get_text("dialog_select_file", lang), "", f)
                    if path:
                        le.setText(path)
                btn.clicked.connect(lambda checked=False, le=lineedit, f=filter_str: browse_file(le, f))
                gui_utils.configure_secondary_button(btn)

                h_layout.addWidget(lineedit)
                h_layout.addWidget(btn)

                if service.name == "KokoroTTS" and key == "engine_path":
                     install_btn = aqt.qt.QPushButton(i18n.get_text("button_install_kokoro", lang))
                     def open_kokoro_manager(le=lineedit):
                         dlg = component_kokoro_manager.KokoroInstallManager(self.dialog)
                         if dlg.exec():
                             default_path = component_kokoro_manager._get_python_exe()
                             if os.path.exists(default_path):
                                 le.setText(default_path)
                     install_btn.clicked.connect(lambda checked=False, le=lineedit: open_kokoro_manager(le))
                     gui_utils.configure_primary_button(install_btn)
                     h_layout.addWidget(install_btn)

                if service.name == "MmsTTS" and key == "engine_path":
                     install_mms_btn = aqt.qt.QPushButton(i18n.get_text("button_install_mms", lang))
                     def open_mms_manager_inline(le=lineedit):
                         from . import component_mms_manager
                         dlg = component_mms_manager.MmsInstallManager(self.dialog)
                         dlg.exec()
                         self.hypertts.service_manager.clear_voice_list_cache()
                         self.model_change()
                         from .mms_engine_manager import MmsEngineManager
                         engine_path = MmsEngineManager.get_python_exe()
                         if os.path.exists(engine_path):
                             self._set_service_config_value_with_ui_sync(service.name, "engine_path", engine_path)
                     install_mms_btn.clicked.connect(lambda checked=False, le=lineedit: open_mms_manager_inline(le))
                     gui_utils.configure_primary_button(install_mms_btn)
                     h_layout.addWidget(install_mms_btn)

                if service.name == "PiperTTS" and key == "executable_path":
                     setup_btn = aqt.qt.QPushButton(i18n.get_text("button_setup_piper", lang))
                     def open_piper_setup(le=lineedit):
                          from . import component_piper_setup
                          dlg = component_piper_setup.PiperSetupDialog(self.dialog)
                          dlg.exec()
                          if os.path.exists(constants.PIPER_ENGINE_DIR):
                              le.setText(constants.PIPER_ENGINE_DIR)
                     setup_btn.clicked.connect(lambda checked=False, le=lineedit: open_piper_setup(le))
                     gui_utils.configure_primary_button(setup_btn)
                     h_layout.addWidget(setup_btn)

                if service.name == "SupertonicTTS" and key == "engine_path":
                     setup_btn = aqt.qt.QPushButton(i18n.get_text("button_setup_supertonic", lang))
                     def open_supertonic_setup(le=lineedit):
                         dlg = component_supertonic_setup.SupertonicSetupDialog(self.dialog)
                         dlg.exec()
                         from .engine_manager import EngineManager
                         engine_path = EngineManager.get_python_exe()
                         if os.path.exists(engine_path):
                             le.setText(engine_path)
                         self.hypertts.service_manager.clear_voice_list_cache()
                         self.model_change()
                     setup_btn.clicked.connect(lambda checked=False, le=lineedit: open_supertonic_setup(le))
                     gui_utils.configure_primary_button(setup_btn)
                     h_layout.addWidget(setup_btn)

                validation_label = aqt.qt.QLabel()
                validation_label.setWordWrap(True)
                self.option_validation_label_map[f"{service.name}_{key}"] = validation_label
                v_layout = aqt.qt.QVBoxLayout()
                v_layout.addLayout(h_layout)
                v_layout.addWidget(validation_label)
                self._wire_path_validation(lineedit, validation_label)
                options_gridlayout.addLayout(v_layout, row, 1, 1, 1)

            elif isinstance(type, tuple) and type[0] == 'directory':
                title_str = type[1]
                h_layout = aqt.qt.QHBoxLayout()
                lineedit = aqt.qt.QLineEdit()
                lineedit.setText(self.model.get_service_configuration_key(service.name, key))
                lineedit.setObjectName(widget_name)
                lineedit.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Fixed)
                lineedit.textChanged.connect(self.get_service_config_str_change_fn(service, key))

                btn = aqt.qt.QPushButton(i18n.get_text("button_browse", lang))
                def browse_dir(le=lineedit):
                    path = aqt.qt.QFileDialog.getExistingDirectory(self.dialog, i18n.get_text("dialog_select_directory", lang))
                    if path:
                        le.setText(path)
                btn.clicked.connect(lambda checked=False, le=lineedit: browse_dir(le))
                gui_utils.configure_secondary_button(btn)

                h_layout.addWidget(lineedit)
                h_layout.addWidget(btn)

                if service.name == "PiperTTS" and key == "models_path":
                     dl_btn = aqt.qt.QPushButton(i18n.get_text("button_manage_voices", lang))
                     def open_downloader(le=lineedit):
                         dest_dir = le.text()
                         if not dest_dir:
                             dest_dir = constants.PIPER_MODELS_DIR
                             os.makedirs(dest_dir, exist_ok=True)
                             le.setText(dest_dir)

                         from . import component_piper_manager
                         dlg = component_piper_manager.PiperManagerDialog(self.dialog, dest_dir)
                         dlg.exec()
                         self.hypertts.service_manager.clear_voice_list_cache()

                         self.model.set_service_enabled("PiperTTS", True)
                         piper_cb = self.service_checkbox_map.get("PiperTTS")
                         if piper_cb:
                             piper_cb.setChecked(True)
                         self.model_change()

                     dl_btn.clicked.connect(lambda checked=False, le=lineedit: open_downloader(le))
                     gui_utils.configure_secondary_button(dl_btn)

                     setup_btn = aqt.qt.QPushButton(i18n.get_text("button_setup_piper", lang))
                     def open_setup(le=lineedit):
                         from . import component_piper_setup
                         dlg = component_piper_setup.PiperSetupDialog(self.dialog)
                         dlg.exec()
                         if not le.text():
                             le.setText(constants.PIPER_MODELS_DIR)
                         self.hypertts.service_manager.clear_voice_list_cache()

                         if os.path.exists(constants.PIPER_EXE_PATH):
                             self.model.set_service_enabled("PiperTTS", True)
                             piper_cb = self.service_checkbox_map.get("PiperTTS")
                             if piper_cb:
                                 piper_cb.setChecked(True)
                             self.model_change()

                     setup_btn.clicked.connect(lambda checked=False, le=lineedit: open_setup(le))
                     gui_utils.configure_primary_button(setup_btn)

                     h_layout.addWidget(dl_btn)
                     h_layout.addWidget(setup_btn)

                if service.name == "SupertonicTTS" and key == "custom_voices_path":
                     manage_btn = aqt.qt.QPushButton(i18n.get_text("button_manage_supertonic_voices", lang))
                     def open_supertonic_voice_manager(le=lineedit):
                         dest_dir = le.text() or constants.SUPERTONIC_CUSTOM_VOICES_DIR
                         os.makedirs(dest_dir, exist_ok=True)
                         le.setText(dest_dir)
                         from .component_supertonic_voice_manager import SupertonicVoiceManagerDialog
                         dlg = SupertonicVoiceManagerDialog(self.dialog, dest_dir)
                         dlg.exec()
                         self.hypertts.service_manager.clear_voice_list_cache()
                         self.model_change()
                     manage_btn.clicked.connect(lambda checked=False, le=lineedit: open_supertonic_voice_manager(le))
                     gui_utils.configure_secondary_button(manage_btn)
                     h_layout.addWidget(manage_btn)

                validation_label = aqt.qt.QLabel()
                validation_label.setWordWrap(True)
                self.option_validation_label_map[f"{service.name}_{key}"] = validation_label
                v_layout = aqt.qt.QVBoxLayout()
                v_layout.addLayout(h_layout)
                v_layout.addWidget(validation_label)
                self._wire_path_validation(lineedit, validation_label)
                options_gridlayout.addLayout(v_layout, row, 1, 1, 1)

            elif isinstance(type, tuple) and type[0] == 'number':
                 spinbox = aqt.qt.QSpinBox()

                 min_val = 0
                 max_val = 32

                 if len(type) > 3:
                     min_val = type[3]
                 if len(type) > 4:
                     max_val = type[4]

                 spinbox.setRange(min_val, max_val)

                 saved_value = self.model.get_service_configuration_key(service.name, key)
                 if saved_value is None and len(type) > 2:
                     saved_value = type[2]

                 if saved_value is not None:
                     try: spinbox.setValue(int(saved_value))
                     except Exception as e:
                         logger.warning(f"Failed to set spinbox value: {e}")

                     spinbox.setObjectName(widget_name)
                     spinbox.valueChanged.connect(self.get_service_config_int_change_fn(service, key))
                     options_gridlayout.addWidget(spinbox, row, 1, 1, 1)

            elif isinstance(type, tuple) and type[0] == 'bool':
                 checkbox = aqt.qt.QCheckBox()
                 saved_value = self.model.get_service_configuration_key(service.name, key)
                 if saved_value is None and len(type) > 2:
                     saved_value = type[2]

                 if saved_value is not None:
                     checkbox.setChecked(bool(saved_value))

                 checkbox.setObjectName(widget_name)
                 checkbox.stateChanged.connect(self.get_service_config_bool_change_fn(service, key))
                 options_gridlayout.addWidget(checkbox, row, 1, 1, 1)

            elif isinstance(type, list):
                combobox = aqt.qt.QComboBox()
                combobox.setObjectName(widget_name)
                combobox.addItems(type)
                combobox.setCurrentText(self.model.get_service_configuration_key(service.name, key))
                combobox.currentTextChanged.connect(self.get_service_config_list_change_fn(service, key))
                options_gridlayout.addWidget(combobox, row, 1, 1, 1)
            row += 1

        layout.addLayout(options_gridlayout)

        if hasattr(service, 'advanced_configuration_options'):
            advanced_options = service.advanced_configuration_options()
            if advanced_options:
                self.draw_service_advanced_options(service, layout, advanced_options)

        return service_enabled_checkbox

    def draw_service_advanced_options(self, service, layout, advanced_options: dict) -> None:
        lang = self.hypertts.get_ui_language()
        advanced_hlayout = aqt.qt.QHBoxLayout()

        advanced_text = i18n.get_text("button_advanced_settings", lang)
        advanced_btn = aqt.qt.QPushButton(advanced_text)
        advanced_btn.setIcon(aqt.qt.QIcon(gui_utils.get_graphics_path(constants.GRAPHICS_ICON_CHEVRON_RIGHT)))
        advanced_btn.setCheckable(True)
        advanced_btn.setChecked(False)

        advanced_widget = aqt.qt.QWidget()
        advanced_widget.setVisible(False)
        advanced_gridlayout = aqt.qt.QGridLayout()
        advanced_gridlayout.setSpacing(8)
        advanced_gridlayout.setContentsMargins(10, 10, 10, 10)

        row = 0
        for key, type in advanced_options.items():
            widget_name = f'{service.name}_{key}_adv'
            label_text = self._get_service_option_label(service, key, type) + ':'

            advanced_gridlayout.addWidget(aqt.qt.QLabel(label_text), row, 0, 1, 1)

            if isinstance(type, tuple) and type[0] == 'number':
                spinbox = aqt.qt.QSpinBox()
                min_val = type[3] if len(type) > 3 else 0
                max_val = type[4] if len(type) > 4 else 32
                spinbox.setRange(min_val, max_val)

                saved_value = self.model.get_service_configuration_key(service.name, key)
                if saved_value is None and len(type) > 2:
                    saved_value = type[2]
                if saved_value is not None:
                    try: spinbox.setValue(int(saved_value))
                    except Exception as e:
                        logger.warning(f"Failed to set spinbox value: {e}")

                    spinbox.setObjectName(widget_name)
                    spinbox.valueChanged.connect(self.get_service_config_int_change_fn(service, key))
                    advanced_gridlayout.addWidget(spinbox, row, 1, 1, 1)

            elif isinstance(type, tuple) and type[0] == 'bool':
                checkbox = aqt.qt.QCheckBox()
                saved_value = self.model.get_service_configuration_key(service.name, key)
                if saved_value is None and len(type) > 2:
                    saved_value = type[2]
                if saved_value is not None:
                    checkbox.setChecked(bool(saved_value))

                checkbox.setObjectName(widget_name)
                checkbox.stateChanged.connect(self.get_service_config_bool_change_fn(service, key))
                advanced_gridlayout.addWidget(checkbox, row, 1, 1, 1)

            row += 1

        advanced_widget.setLayout(advanced_gridlayout)

        separator = aqt.qt.QFrame()
        separator.setFrameShape(aqt.qt.QFrame.Shape.HLine)
        separator.setFrameShadow(aqt.qt.QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"color: {constants.COLOR_BORDER};")
        layout.addWidget(separator)

        def toggle_advanced(checked: bool) -> None:
            advanced_widget.setVisible(checked)
            if checked:
                advanced_btn.setIcon(aqt.qt.QIcon(gui_utils.get_graphics_path(constants.GRAPHICS_ICON_CHEVRON_DOWN)))
            else:
                advanced_btn.setIcon(aqt.qt.QIcon(gui_utils.get_graphics_path(constants.GRAPHICS_ICON_CHEVRON_RIGHT)))

        advanced_btn.clicked.connect(toggle_advanced)

        advanced_hlayout.addWidget(advanced_btn)
        advanced_hlayout.addStretch()
        layout.addLayout(advanced_hlayout)
        layout.addWidget(advanced_widget)

    def _apply_service_card_style(self, service_card: aqt.qt.QFrame, enabled: bool):
        service_card.setProperty("cssClass", "serviceCard")
        if enabled:
            service_card.setProperty("cardState", "enabled")
        else:
            service_card.setProperty("cardState", "disabled")

        service_card.style().unpolish(service_card)
        service_card.style().polish(service_card)

    def draw_service(self, service, layout):
        logger.debug(f'draw_service {service.name}')
        lang = self.hypertts.get_ui_language()

        def get_service_header_label(service):
            header_label = gui_utils.get_service_header_label(service.name)
            return header_label

        def get_service_description_text(service, lang=lang):
            fee_key = f"service_fee_{service.service_fee.name}"
            fee_text = i18n.get_text(fee_key, lang)

            desc_key = f"service_description_{service.name}"
            specific_desc = i18n.get_text(desc_key, lang)

            if specific_desc != desc_key:
                service_description = f'{fee_text}, {specific_desc}'
            else:
                type_key = f"service_type_{service.service_type.name}_description"
                type_text = i18n.get_text(type_key, lang)
                service_description = f'{fee_text}, {type_text}'

            return service_description

        def get_service_description_label(service, lang=lang):
            service_description = get_service_description_text(service, lang)

            service_description_label = aqt.qt.QLabel(service_description)
            service_description_label.setMargin(0)
            service_description_label.setWordWrap(True)
            return service_description_label

        combined_service_vlayout = aqt.qt.QVBoxLayout()
        combined_service_vlayout.setContentsMargins(16, 16, 16, 16)
        combined_service_vlayout.setSpacing(8)

        header_row = aqt.qt.QHBoxLayout()
        collapse_button = aqt.qt.QToolButton()
        collapse_button.setCheckable(True)
        collapse_button.setToolButtonStyle(aqt.qt.Qt.ToolButtonStyle.ToolButtonIconOnly)
        collapse_button.setStyleSheet("QToolButton { border: none; padding: 0 2px; }")
        header_row.addWidget(collapse_button)
        header_row.addWidget(get_service_header_label(service))

        if service.service_fee.name == 'free':
            dark = gui_utils.is_night_mode()
            header_row.addSpacing(8)
            header_row.addWidget(gui_utils.get_status_badge(
                i18n.get_text("service_badge_free", lang),
                bg_color="#FFFFFF" if not dark else "#022C22",
                text_color="#059669" if not dark else "#34D399"
            ))

        if service.name == "EdgeTTS":
            dark = gui_utils.is_night_mode()
            header_row.addSpacing(8)
            header_row.addWidget(gui_utils.get_status_badge(
                i18n.get_text("service_badge_recommended", lang),
                bg_color="#78350F" if dark else "#FEF3C7",
                text_color="#FDE68A" if dark else "#92400E"
            ))

        header_row.addSpacing(8)
        status_text, status_bg, status_fg = self._get_service_status_info(service)
        status_badge = gui_utils.get_status_badge(
            status_text,
            bg_color=status_bg,
            text_color=status_fg,
        )
        self.service_status_badge_map[service.name] = status_badge
        header_row.addWidget(status_badge)

        setup_action_button = aqt.qt.QPushButton(i18n.get_text("generic_setup", lang))
        setup_action_button.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
        setup_action_button.setMinimumHeight(22)
        setup_action_button.setMinimumWidth(80)
        setup_action_button.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)
        setup_action_button.setStyleSheet(
            "QPushButton { background-color: #FEF3C7; color: #92400E; border: none; border-radius: 12px; padding: 2px 10px; font-weight: 700; }"
            "QPushButton:hover { background-color: #FDE68A; }"
        )
        header_row.addSpacing(6)
        header_row.addWidget(setup_action_button)

        header_row.addStretch()
        combined_service_vlayout.addLayout(header_row)
        combined_service_vlayout.addWidget(get_service_description_label(service))

        self.service_search_index[service.name] = self._build_service_search_text(
            service,
            get_service_description_text(service, lang),
        )

        service_stack = aqt.qt.QWidget()
        service_vlayout = aqt.qt.QVBoxLayout()
        service_vlayout.setContentsMargins(0, 0, 0, 0)
        service_enabled_checkbox = self.draw_service_options(service, service_vlayout)
        service_stack.setLayout(service_vlayout)

        def refresh_setup_action_button():
            need_setup_text = i18n.get_text("service_status_setup_needed", lang)
            current_status_text, _, _ = self._get_service_status_info(service)
            should_show = self._supports_setup_shortcut(service) and current_status_text == need_setup_text
            setup_action_button.setVisible(should_show)

        setup_action_button.clicked.connect(lambda: self._open_setup_dialog_for_service(service))
        setup_action_button.clicked.connect(lambda: self._refresh_service_status_badges())
        setup_action_button.clicked.connect(lambda: refresh_setup_action_button())
        refresh_setup_action_button()

        default_expanded = service_enabled_checkbox.isChecked()
        collapse_button.setChecked(default_expanded)
        collapse_button.setArrowType(
            aqt.qt.Qt.ArrowType.DownArrow if default_expanded else aqt.qt.Qt.ArrowType.RightArrow
        )
        service_stack.setVisible(default_expanded)

        def on_collapse_toggled(checked):
            service_stack.setVisible(checked)
            collapse_button.setArrowType(
                aqt.qt.Qt.ArrowType.DownArrow if checked else aqt.qt.Qt.ArrowType.RightArrow
            )

        collapse_button.toggled.connect(on_collapse_toggled)
        self.service_expand_toggle_map[service.name] = collapse_button

        combined_service_vlayout.addWidget(service_stack)

        service_card = aqt.qt.QFrame()
        service_card.setObjectName("serviceCard")
        service_card.setLayout(combined_service_vlayout)
        service_card.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)

        self._apply_service_card_style(service_card, service_enabled_checkbox.isChecked())

        def on_enabled_changed(state):
            self._apply_service_card_style(service_card, state == 2)
            self._refresh_service_status_badges()
            refresh_setup_action_button()

        service_enabled_checkbox.stateChanged.connect(on_enabled_changed)

        def card_mouse_press(event, checkbox=service_enabled_checkbox):
            checkbox.setChecked(not checkbox.isChecked())

        service_card.mousePressEvent = card_mouse_press

        self.service_card_map[service.name] = service_card

        layout.addWidget(service_card)

    def get_service_list(self):
        all_services = self.hypertts.service_manager.get_all_services()
        service_list = [s for s in all_services if s.service_fee.name == 'free']
        return service_list

    def draw(self, layout, show_action_buttons=True):
        lang = self.hypertts.get_ui_language()
        self.global_vlayout = aqt.qt.QVBoxLayout()
        self.global_vlayout.setContentsMargins(16, 12, 16, 10)
        self.global_vlayout.setSpacing(10)

        service_list = self.get_service_list()

        header_hlayout = aqt.qt.QHBoxLayout()
        header_hlayout.setContentsMargins(4, 0, 4, 8)

        self.services_summary_label = aqt.qt.QLabel()
        self.services_summary_label.setWordWrap(True)
        summary_font = self.services_summary_label.font()
        summary_font.setBold(True)
        summary_font.setPointSize(max(summary_font.pointSize(), 11))
        self.services_summary_label.setFont(summary_font)
        self.services_summary_label.setStyleSheet("color: #123A63; padding-top: 4px;")
        header_hlayout.addWidget(self.services_summary_label)
        header_hlayout.addStretch()

        self.search_input = aqt.qt.QLineEdit()
        self.search_input.setPlaceholderText(i18n.get_text("config_search_placeholder", lang))
        self.search_input.setMinimumHeight(32)
        self.search_input.setMinimumWidth(120)
        self.search_input.setMaximumWidth(240)
        self.search_input.setStyleSheet(
            "QLineEdit { border: 1px solid #CBD5E1; border-radius: 6px; padding: 4px 10px; "
            "font-size: 12px; color: #334155; background-color: #FFFFFF; }"
        )
        self.search_debounce_timer = aqt.qt.QTimer(self.dialog)
        self.search_debounce_timer.setSingleShot(True)
        header_hlayout.addWidget(self.search_input)
        self.global_vlayout.addLayout(header_hlayout)

        services_scroll_area = aqt.qt.QScrollArea()
        services_scroll_area.setWidgetResizable(True)
        services_scroll_area.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)
        services_scroll_area.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignTop)
        services_widget = aqt.qt.QWidget()
        self.services_vlayout = aqt.qt.QVBoxLayout(services_widget)
        self.services_vlayout.setSpacing(14)

        tts_services = [s for s in service_list if s.service_type.name == "tts"]
        dict_services = [s for s in service_list if s.service_type.name == "dictionary"]
        category_sections = []

        def draw_category(title, services, parent_layout, default_expanded=True):
            if not services:
                return

            section_button = aqt.qt.QToolButton()
            section_button.setText(title)
            section_button.setCheckable(True)
            section_button.setChecked(default_expanded)
            section_button.setToolButtonStyle(aqt.qt.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            section_button.setArrowType(
                aqt.qt.Qt.ArrowType.DownArrow if default_expanded else aqt.qt.Qt.ArrowType.RightArrow
            )
            section_button.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Fixed)
            section_button.setStyleSheet(
                "QToolButton { text-align: left; font-weight: bold; font-size: 14px; border: none; "
                "border-radius: 10px; padding: 10px 14px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                "stop:0 #4776E6, stop:1 #8E54E9); color: white; }"
                "QToolButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5B86E5, stop:1 #A17FE0); }"
            )
            parent_layout.addWidget(section_button)

            group_box = aqt.qt.QGroupBox("")
            group_box.setCheckable(False)
            group_box.setStyleSheet("QGroupBox { margin-top: 2px; border: none; }")

            group_layout = aqt.qt.QVBoxLayout()
            group_layout.setContentsMargins(10, 10, 10, 8)
            group_layout.setSpacing(8)

            toggle_all_cb = aqt.qt.QCheckBox(i18n.get_text("generic_enable_all", lang))
            toggle_all_cb.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
            toggle_all_cb.setTristate(False)
            toggle_all_font = toggle_all_cb.font()
            toggle_all_font.setPointSize(10)
            toggle_all_cb.setFont(toggle_all_font)
            updating = {"value": False}
            toggle_all_cb.setChecked(all(s.enabled for s in services))

            def toggle_all_services(checked):
                if updating["value"]:
                    return
                updating["value"] = True
                for service in services:
                    cb = self.service_checkbox_map.get(service.name)
                    if cb and cb.isChecked() != checked:
                        cb.setChecked(checked)
                updating["value"] = False

            toggle_all_cb.clicked.connect(toggle_all_services)
            group_layout.addWidget(toggle_all_cb)

            for service in services:
                self.draw_service(service, group_layout)
                cb = self.service_checkbox_map.get(service.name)
                if cb:
                    def on_individual_changed(_state, _services=services, _toggle=toggle_all_cb, _guard=updating):
                        if _guard["value"]:
                            return
                        all_checked = all(
                            self.service_checkbox_map.get(s.name).isChecked()
                            for s in _services
                            if self.service_checkbox_map.get(s.name) is not None
                        )
                        _toggle.setChecked(all_checked)

                    cb.stateChanged.connect(on_individual_changed)

            group_box.setLayout(group_layout)
            parent_layout.addWidget(group_box)

            def on_section_toggled(checked, btn=section_button, content=group_box):
                content.setVisible(checked)
                btn.setArrowType(aqt.qt.Qt.ArrowType.DownArrow if checked else aqt.qt.Qt.ArrowType.RightArrow)

            section_button.toggled.connect(on_section_toggled)
            group_box.setVisible(default_expanded)
            category_sections.append((services, section_button))

        draw_category(i18n.get_text("config_category_tts", lang), tts_services, self.services_vlayout, default_expanded=True)
        draw_category(
            i18n.get_text("config_category_dictionary", lang), dict_services, self.services_vlayout, default_expanded=False
        )
        self.services_vlayout.addStretch()

        services_scroll_area.setWidget(services_widget)
        self.global_vlayout.addWidget(services_scroll_area, 1)

        self.save_button = aqt.qt.QPushButton(i18n.get_text("button_save", lang))
        self.save_button.setEnabled(False)
        gui_utils.configure_primary_button(self.save_button, min_height=40, min_width=100, font_size=11)
        self.cancel_button = aqt.qt.QPushButton(i18n.get_text("button_cancel", lang))
        gui_utils.configure_secondary_button(self.cancel_button, min_height=40, min_width=100, font_size=11)
        if show_action_buttons:
            buttons_layout = aqt.qt.QHBoxLayout()
            buttons_layout.addStretch()
            buttons_layout.addWidget(self.save_button)
            buttons_layout.addWidget(self.cancel_button)
            self.global_vlayout.addLayout(buttons_layout)
            self.save_button.pressed.connect(self.save_button_pressed)
            self.cancel_button.pressed.connect(self.cancel_button_pressed)

        self.enable_model_change = True

        def run_search():
            query = self.search_input.text().strip().lower()
            first_match_widget = None
            matched_services = set()

            if self._services_scroll_area is not None:
                self._services_scroll_area.setUpdatesEnabled(False)

            if not query:
                for service in service_list:
                    card_widget = self.service_card_map.get(service.name)
                    if card_widget is not None:
                        card_widget.setVisible(True)
            else:
                for service in service_list:
                    card_widget = self.service_card_map.get(service.name)
                    if card_widget is None:
                        continue
                    search_blob = self.service_search_index.get(service.name, service.name.lower())
                    if query in search_blob:
                        card_widget.setVisible(True)
                        matched_services.add(service.name)
                        expand_btn = self.service_expand_toggle_map.get(service.name)
                        if expand_btn is not None and not expand_btn.isChecked():
                            expand_btn.setChecked(True)
                        if first_match_widget is None:
                            first_match_widget = card_widget
                    else:
                        card_widget.setVisible(False)

                for category_services, category_button in category_sections:
                    if any(s.name in matched_services for s in category_services) and not category_button.isChecked():
                        category_button.setChecked(True)

            if first_match_widget is not None and self._services_scroll_area is not None:
                self._services_scroll_area.ensureWidgetVisible(first_match_widget)

            if self._services_scroll_area is not None:
                self._services_scroll_area.setUpdatesEnabled(True)

        self.search_debounce_timer.timeout.connect(run_search)
        self.search_input.textChanged.connect(lambda _text: self.search_debounce_timer.start(180))

        self._refresh_services_summary_label()
        self._services_scroll_area = services_scroll_area
        self._services_container_widget = services_widget
        layout.addLayout(self.global_vlayout)

    @sc.event(Event.click_save)
    def save_button_pressed(self):
        with self.hypertts.error_manager.get_single_action_context('Saving Service Configuration'):
            self.hypertts.save_configuration(self.model)
            self.hypertts.reconfigure_service_manager()
            self.dialog.close()

    @sc.event(Event.click_cancel)
    def cancel_button_pressed(self):
        self.dialog.close()