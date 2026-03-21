from pydoc import describe
import sys
import os
import aqt.qt
import webbrowser

from . import component_common
from . import config_models
from . import constants
# from . import constants_events removed
from .stats import Event
from . import gui_utils
from . import logging_utils
from . import stats
from . import i18n
from . import component_about
from . import component_piper_manager
from . import component_kokoro_manager, component_mms_manager
from . import component_onnx_manager

logger = logging_utils.get_child_logger(__name__)

class ScrollAreaCustom(aqt.qt.QScrollArea):
    def __init__(self):
        aqt.qt.QScrollArea.__init__(self)
        # Cho phép nội dung bên trong tự giãn theo kích thước mới của dialog
        # Khi người dùng kéo to/nhỏ cửa sổ, widget con sẽ resize theo
        self.setWidgetResizable(True)

    def sizeHint(self):
        return aqt.qt.QSize(100, 100)


sc = stats.StatsContext(stats.EventContext.services)

class Configuration(component_common.ConfigComponentBase):

    @sc.event(Event.open)
    def __init__(self, hypertts, dialog):
        self.hypertts = hypertts
        self.dialog = dialog
        self.model = config_models.Configuration()
        # map service.name -> service enabled checkbox (dùng cho Enable All)
        self.service_checkbox_map = {}
        # map service.name -> dynamic status badge label
        self.service_status_badge_map = {}
        # map service.name -> searchable normalized text
        self.service_search_index = {}
        self.services_summary_label = None
        # map service.name -> service card widget (dùng cho TOC bên trái)
        self.service_card_map = {}
        # tham chiếu scroll area + container, được set trong draw()
        self._services_scroll_area = None
        self._services_container_widget = None
        self.enable_model_change = False
        self.api_key_valid = False
        self.search_debounce_timer = None
        self.option_validation_label_map = {}
        self.about_component = component_about.AboutComponent(hypertts)

    def get_model(self):
        return self.model

    def load_model(self, model):
        self.model = model


    def model_change(self):
        if self.enable_model_change:
            self.save_button.setEnabled(True)
            self.save_button.setStyleSheet(self.hypertts.anki_utils.get_green_stylesheet())
            self._refresh_service_status_badges()

    def _build_service_search_text(self, service, service_description):
        """Build normalized search text including service/options/advanced labels."""
        chunks = [service.name, service_description]

        try:
            for key, option_type in service.configuration_options().items():
                chunks.append(str(key))
                if isinstance(option_type, tuple) and len(option_type) > 1 and option_type[0] in ['file', 'directory', 'number', 'bool']:
                    chunks.append(str(option_type[1]))
        except Exception:
            pass

        try:
            if hasattr(service, 'advanced_configuration_options'):
                for key, option_type in service.advanced_configuration_options().items():
                    chunks.append(str(key))
                    if isinstance(option_type, tuple) and len(option_type) > 1 and option_type[0] in ['file', 'directory', 'number', 'bool']:
                        chunks.append(str(option_type[1]))
        except Exception:
            pass

        return ' '.join(chunks).lower()

    def _get_service_status_info(self, service):
        """Return (text, bg_color, text_color) for current service readiness."""
        lang = self.hypertts.get_ui_language()
        enabled = bool(self.model.get_service_enabled(service.name))
        if not enabled:
            return (
                i18n.get_text("service_status_disabled", lang),
                constants.COLOR_BORDER,
                constants.COLOR_SECONDARY,
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
                '#FEF3C7',
                '#92400E',
            )

        return (
            i18n.get_text("service_status_ready", lang),
            constants.COLOR_ACCENT_LIGHT,
            constants.COLOR_ACCENT_DARK,
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
                    border: 1px solid {bg};
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


    @sc.event(Event.click_disable_all_services)
    def disable_all_services(self):
        for service in self.get_service_list():
            checkbox = self.service_checkbox_map.get(service.name)
            if checkbox:
                checkbox.setChecked(False)

    @sc.event(Event.click_enable_free_services)
    def enable_all_free_services(self):
        for service in self.get_service_list():
            if service.service_fee == constants.ServiceFee.free:
                checkbox = self.service_checkbox_map.get(service.name)
                if checkbox:
                    checkbox.setChecked(True)

    def get_service_enabled_widget_name(self, service):
        return f'{service.name}_enabled'

    def draw_service_options(self, service, layout):
        lang = self.hypertts.get_ui_language()
        service_enabled_checkbox = aqt.qt.QCheckBox(i18n.get_text("generic_enable", lang))
        service_enabled_checkbox.setObjectName(self.get_service_enabled_widget_name(service))
        service_enabled_checkbox.setChecked(service.enabled)
        # store reference for Enable All toggle
        self.service_checkbox_map[service.name] = service_enabled_checkbox
        service_enabled_checkbox.stateChanged.connect(self.get_service_enable_change_fn(service))
        layout.addWidget(service_enabled_checkbox)

        configuration_options = service.configuration_options()
        options_gridlayout = aqt.qt.QGridLayout()
        row = 0
        for key, type in configuration_options.items():
            widget_name = f'{service.name}_{key}'
            
            # Determine label text
            label_text = key + ':'
            if isinstance(type, tuple) and len(type) > 1:
                # Support custom labels for file, directory, number, bool types
                if type[0] in ['file', 'directory', 'number', 'bool']:
                    label_text = type[1] + ':'
            
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
            elif isinstance(type, tuple) and type[0] == 'file': # ('file', 'Filter (*.exe)')
                filter_str = type[1]
                h_layout = aqt.qt.QHBoxLayout()
                actions_layout = aqt.qt.QHBoxLayout()
                lineedit = aqt.qt.QLineEdit()
                lineedit.setText(self.model.get_service_configuration_key(service.name, key))
                lineedit.setObjectName(widget_name)
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
                
                # Special logic for KokoroTTS Engine Path: Add "Install/Update" button
                if service.name == "KokoroTTS" and key == "engine_path":

                     install_btn = aqt.qt.QPushButton(i18n.get_text("button_install_kokoro", lang))
                     def open_kokoro_manager(le=lineedit):
                         dlg = component_kokoro_manager.KokoroInstallManager(self.dialog)
                         if dlg.exec():
                             # If installed successfully, update the path
                             default_path = os.path.join(component_kokoro_manager.PYTHON_EXE)
                             if os.path.exists(default_path):
                                 le.setText(default_path)
                     install_btn.clicked.connect(lambda checked=False, le=lineedit: open_kokoro_manager(le))
                     gui_utils.configure_primary_button(install_btn)
                     actions_layout.addWidget(install_btn)

                # Special logic for MmsTTS: Add "Install MMS..." button
                if service.name == "MmsTTS" and key == "python_path":
                     install_btn = aqt.qt.QPushButton(i18n.get_text("button_install_mms", lang))
                     def open_mms_manager(le=lineedit):
                         from . import component_mms_manager
                         dlg = component_mms_manager.MmsInstallManager(self.dialog)
                         dlg.exec()
                         # After closing, check if python path is now valid
                         from .component_kokoro_manager import PYTHON_EXE
                         if os.path.exists(PYTHON_EXE):
                             le.setText(PYTHON_EXE)
                     install_btn.clicked.connect(lambda checked=False, le=lineedit: open_mms_manager(le))
                     gui_utils.configure_primary_button(install_btn)
                     actions_layout.addWidget(install_btn)

                # Special logic for PiperTTS: Add "Setup Piper" button
                if service.name == "PiperTTS" and key == "engine_path":
                     setup_btn = aqt.qt.QPushButton(i18n.get_text("button_setup_piper", lang))
                     def open_piper_setup(le=lineedit):
                          from . import component_piper_setup
                          dlg = component_piper_setup.PiperSetupDialog(self.dialog)
                          dlg.exec()
                          # After setup, update path if exists
                          if os.path.exists(component_piper_setup.PIPER_EXE_PATH):
                              le.setText(component_piper_setup.PIPER_EXE_PATH)
                     setup_btn.clicked.connect(lambda checked=False, le=lineedit: open_piper_setup(le))
                     gui_utils.configure_primary_button(setup_btn)
                     actions_layout.addWidget(setup_btn)

                validation_label = aqt.qt.QLabel()
                validation_label.setWordWrap(True)
                self.option_validation_label_map[f"{service.name}_{key}"] = validation_label
                v_layout = aqt.qt.QVBoxLayout()
                v_layout.addLayout(h_layout)
                if actions_layout.count() > 0:
                    actions_layout.addStretch()
                    v_layout.addLayout(actions_layout)
                v_layout.addWidget(validation_label)
                self._wire_path_validation(lineedit, validation_label)
                options_gridlayout.addLayout(v_layout, row, 1, 1, 1)

            elif isinstance(type, tuple) and type[0] == 'directory': # ('directory', 'Title')
                title_str = type[1]
                h_layout = aqt.qt.QHBoxLayout()
                lineedit = aqt.qt.QLineEdit()
                lineedit.setText(self.model.get_service_configuration_key(service.name, key))
                lineedit.setObjectName(widget_name)
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
                
                # Special logic for PiperTTS Models Path: Add "Download Models" button
                if service.name == "PiperTTS" and key == "models_path":
                     h_piper_layout = aqt.qt.QHBoxLayout()
                     
                     dl_btn = aqt.qt.QPushButton(i18n.get_text("button_manage_voices", lang))
                     def open_downloader(le=lineedit):
                         dest_dir = le.text()
                         if not dest_dir:
                             from . import component_piper_setup
                             dest_dir = component_piper_setup.PIPER_MODELS_DIR
                             os.makedirs(dest_dir, exist_ok=True)
                             le.setText(dest_dir)
                         
                         from . import component_piper_manager
                         dlg = component_piper_manager.PiperManagerDialog(self.dialog, dest_dir)
                         dlg.exec()
                         # After downloading, clear cache so new voices show up in Generate menu
                         self.hypertts.service_manager.clear_voice_list_cache()
                         
                         # Auto-enable service if voices downloaded
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
                         # After setup, set default path if empty
                         if not le.text():
                             le.setText(component_piper_setup.PIPER_MODELS_DIR)
                         self.hypertts.service_manager.clear_voice_list_cache()
                         
                         # Auto-enable service
                         from . import component_piper_setup
                         if os.path.exists(component_piper_setup.PIPER_EXE_PATH):
                             self.model.set_service_enabled("PiperTTS", True)
                             piper_cb = self.service_checkbox_map.get("PiperTTS")
                             if piper_cb:
                                 piper_cb.setChecked(True)
                             self.model_change()
                             
                     setup_btn.clicked.connect(lambda checked=False, le=lineedit: open_setup(le))
                     gui_utils.configure_primary_button(setup_btn)
                     
                     h_piper_layout.addWidget(dl_btn)
                     h_piper_layout.addWidget(setup_btn)
                     h_layout.addLayout(h_piper_layout)

                # MeloTTS removed

                validation_label = aqt.qt.QLabel()
                validation_label.setWordWrap(True)
                self.option_validation_label_map[f"{service.name}_{key}"] = validation_label
                v_layout = aqt.qt.QVBoxLayout()
                v_layout.addLayout(h_layout)
                v_layout.addWidget(validation_label)
                self._wire_path_validation(lineedit, validation_label)
                options_gridlayout.addLayout(v_layout, row, 1, 1, 1)

            elif isinstance(type, tuple) and type[0] == 'number': # ('number', 'Label', default, min, max)
                 spinbox = aqt.qt.QSpinBox()
                 
                 # Set default range
                 min_val = 0
                 max_val = 32
                 
                 # Check for explicit constraints in the tuple
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
                     except: pass
                 
                 spinbox.setObjectName(widget_name)
                 spinbox.valueChanged.connect(self.get_service_config_int_change_fn(service, key))
                 options_gridlayout.addWidget(spinbox, row, 1, 1, 1)

            elif isinstance(type, tuple) and type[0] == 'bool': # ('bool', 'Label', default)
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

        # Add Advanced dropdown for services with advanced options
        if hasattr(service, 'advanced_configuration_options'):
            advanced_options = service.advanced_configuration_options()
            if advanced_options:
                self.draw_service_advanced_options(service, layout, advanced_options)

        # trả về checkbox để caller có thể dùng cho việc highlight card
        return service_enabled_checkbox
    
    def draw_service_advanced_options(self, service, layout, advanced_options: dict) -> None:
        """Draw collapsible Advanced settings dropdown for services."""
        lang = self.hypertts.get_ui_language()
        # Create horizontal layout for Advanced button
        advanced_hlayout = aqt.qt.QHBoxLayout()
        
        # Create dropdown button
        advanced_text = i18n.get_text("button_advanced_settings", lang)
        advanced_btn = aqt.qt.QPushButton(f"⚙️ {advanced_text}")
        advanced_btn.setCheckable(True)
        advanced_btn.setChecked(False)
        advanced_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: palette(alternate-base);
                border: 1px solid {constants.COLOR_BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                color: palette(text);
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: palette(base);
                border: 1px solid {constants.COLOR_ACCENT};
            }}
            QPushButton:pressed {{
                background-color: palette(button);
            }}
            QPushButton:checked {{
                background-color: {constants.COLOR_ACCENT_LIGHT};
                color: {constants.COLOR_ACCENT_DARK};
                border: 1px solid {constants.COLOR_ACCENT};
            }}
        """)
        
        # Create collapsible widget for advanced options
        advanced_widget = aqt.qt.QWidget()
        advanced_widget.setVisible(False)
        advanced_gridlayout = aqt.qt.QGridLayout()
        advanced_gridlayout.setSpacing(8)
        advanced_gridlayout.setContentsMargins(10, 10, 10, 10)
        
        row = 0
        for key, type in advanced_options.items():
            widget_name = f'{service.name}_{key}_adv'
            
            # Determine label text
            label_text = key + ':'
            if isinstance(type, tuple) and len(type) > 1:
                if type[0] in ['file', 'directory', 'number', 'bool']:
                    label_text = type[1] + ':'
            
            advanced_gridlayout.addWidget(aqt.qt.QLabel(label_text), row, 0, 1, 1)
            
            # Handle number type (with min/max constraints)
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
                    except: pass
                
                spinbox.setObjectName(widget_name)
                spinbox.valueChanged.connect(self.get_service_config_int_change_fn(service, key))
                advanced_gridlayout.addWidget(spinbox, row, 1, 1, 1)
            
            # Handle bool type
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
        
        # Add separator
        separator = aqt.qt.QFrame()
        separator.setFrameShape(aqt.qt.QFrame.Shape.HLine)
        separator.setFrameShadow(aqt.qt.QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"color: {constants.COLOR_BORDER};")
        layout.addWidget(separator)
        
        # Connect button toggle to show/hide advanced options
        def toggle_advanced(checked: bool) -> None:
            advanced_widget.setVisible(checked)
            advanced_btn.setText(f"⚙️ {advanced_text}" + (" ▼" if checked else " ▶"))
        
        advanced_btn.clicked.connect(toggle_advanced)
        
        advanced_hlayout.addWidget(advanced_btn)
        advanced_hlayout.addStretch()
        layout.addLayout(advanced_hlayout)
        layout.addWidget(advanced_widget)

    def _apply_service_card_style(self, service_card: aqt.qt.QFrame, enabled: bool):
        """
        Apply modern Slate/Emerald card styling.
        - enabled = True: Emerald border and soft slate background
        - enabled = False: Subtle border, semi-transparent background
        """
        if enabled:
            service_card.setStyleSheet(
                f"""QFrame {{ 
                    background-color: palette(window); 
                    border: 2px solid {constants.COLOR_ACCENT}; 
                    border-radius: 12px;
                }}"""
            )
        else:
            service_card.setStyleSheet(
                f"""QFrame {{ 
                    background-color: transparent; 
                    border: 1px solid {constants.COLOR_BORDER}; 
                    border-radius: 12px;
                }}"""
            )

    def draw_service(self, service, layout):
        logger.info(f'draw_service {service.name}')
        lang = self.hypertts.get_ui_language()
        
        def get_service_header_label(service):
            header_label = gui_utils.get_service_header_label(service.name)
            return header_label        

        def get_service_description_text(service, lang=lang):
            # Dùng i18n để mô tả rõ ràng hơn theo ngôn ngữ giao diện
            fee_key = f"service_fee_{service.service_fee.name}"
            # type_key = f"service_type_{service.service_type.name}_description"
            fee_text = i18n.get_text(fee_key, lang)
            
            # Try to get specific description for this service
            desc_key = f"service_description_{service.name}"
            specific_desc = i18n.get_text(desc_key, lang)
            
            if specific_desc != desc_key:
                # Found specific description
                service_description = f'{fee_text}, {specific_desc}'
            else:
                # Fallback to generic type description
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

        # layout dọc cho nội dung bên trong card service
        combined_service_vlayout = aqt.qt.QVBoxLayout()
        combined_service_vlayout.setContentsMargins(16, 16, 16, 16)
        combined_service_vlayout.setSpacing(8)

        # header row with badge
        header_row = aqt.qt.QHBoxLayout()
        header_row.addWidget(get_service_header_label(service))
        
        # Add "Free" badge for free services
        if service.service_fee == constants.ServiceFee.free:
            header_row.addSpacing(8)
            header_row.addWidget(gui_utils.get_status_badge(
                i18n.get_text("service_badge_free", lang)
            ))

        # Highlight EdgeTTS with a "Recommended" badge
        if service.name == "EdgeTTS":
            header_row.addSpacing(8)
            header_row.addWidget(gui_utils.get_status_badge(
                i18n.get_text("service_badge_recommended", lang),
                bg_color="#FEF3C7", # Amber 100
                text_color="#92400E" # Amber 800
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
            
        header_row.addStretch()
        combined_service_vlayout.addLayout(header_row)
        combined_service_vlayout.addWidget(get_service_description_label(service))

        # Build smarter search index (service name + description + option labels).
        self.service_search_index[service.name] = self._build_service_search_text(
            service,
            get_service_description_text(service, lang),
        )

        # add service config options
        # ==========================

        service_stack = aqt.qt.QWidget()
        service_vlayout = aqt.qt.QVBoxLayout()
        service_vlayout.setContentsMargins(0, 0, 0, 0)
        service_enabled_checkbox = self.draw_service_options(service, service_vlayout)
        service_stack.setLayout(service_vlayout)

        combined_service_vlayout.addWidget(service_stack)

        # bọc tất cả vào một "card" tối giản để phân tách từng service rõ ràng
        service_card = aqt.qt.QFrame()
        service_card.setLayout(combined_service_vlayout)
        service_card.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)

        # áp dụng style ban đầu dựa trên trạng thái enabled hiện tại
        self._apply_service_card_style(service_card, service_enabled_checkbox.isChecked())

        # khi user bật/tắt checkbox, update luôn style của card
        def on_enabled_changed(state):
            self._apply_service_card_style(service_card, state == 2)
            self._refresh_service_status_badges()

        service_enabled_checkbox.stateChanged.connect(on_enabled_changed)

        # cho phép click toàn bộ card để bật/tắt Enable (thay vì chỉ tick vào checkbox)
        def card_mouse_press(event, checkbox=service_enabled_checkbox):
            # đảo trạng thái checkbox; Qt sẽ tự kích hoạt stateChanged và cập nhật style
            checkbox.setChecked(not checkbox.isChecked())

        service_card.mousePressEvent = card_mouse_press

        # lưu reference để TOC có thể scroll thẳng đến từng service
        self.service_card_map[service.name] = service_card

        layout.addWidget(service_card)

    def get_service_list(self):
        # HyperTTS Lite: Only show Free services
        # Order is determined by ServiceManager (Edge -> Piper -> Kokoro -> MMS)
        service_list = [s for s in self.hypertts.service_manager.get_all_services() if s.service_fee == constants.ServiceFee.free]
        return service_list


    def draw(self, layout):
        lang = self.hypertts.get_ui_language()
        # layout gốc cho phần nội dung bên phải (Content Panel)
        self.global_vlayout = aqt.qt.QVBoxLayout()
        self.global_vlayout.setContentsMargins(16, 12, 16, 10)
        self.global_vlayout.setSpacing(10)

        def make_scroll_fn(target_widget):
            def _scroll():
                if self._services_scroll_area is not None and target_widget is not None:
                    self._services_scroll_area.ensureWidgetVisible(target_widget)
            return _scroll

        # services
        # ========

        def get_separator():
            separator = aqt.qt.QFrame()
            separator.setFrameShape(aqt.qt.QFrame.Shape.HLine)
            separator.setSizePolicy(aqt.qt.QSizePolicy.Policy.Minimum, aqt.qt.QSizePolicy.Policy.Expanding)
            separator.setStyleSheet('color: #cccccc;')
            separator.setLineWidth(2)
            return separator

        # lấy danh sách services một lần để dùng cho cả content và TOC
        service_list = self.get_service_list()

        # tiêu đề khu vực cấu hình dịch vụ
        header_label = aqt.qt.QLabel(i18n.get_text("services_header_title", lang))
        header_font = header_label.font()
        header_font.setBold(True)
        header_font.setPointSize(max(header_font.pointSize(), 12))
        header_label.setFont(header_font)
        self.global_vlayout.addWidget(header_label)
        # mô tả ngắn cho người dùng mới
        services_description_label = aqt.qt.QLabel(i18n.get_text("services_header_description", lang))
        services_description_label.setWordWrap(True)
        services_description_label.setStyleSheet("color: palette(mid);")
        self.global_vlayout.addWidget(services_description_label)

        self.services_summary_label = aqt.qt.QLabel()
        self.services_summary_label.setWordWrap(True)
        self.services_summary_label.setStyleSheet("color: palette(dark);")
        self.global_vlayout.addWidget(self.services_summary_label)

        # thanh tìm kiếm dịch vụ (bên khu vực Dịch vụ TTS, không nằm ở TOC)
        search_hlayout = aqt.qt.QHBoxLayout()
        self.search_input = aqt.qt.QLineEdit()
        self.search_input.setPlaceholderText(i18n.get_text("config_search_placeholder", lang))
        self.search_input.setMinimumHeight(34)
        self.search_debounce_timer = aqt.qt.QTimer(self.dialog)
        self.search_debounce_timer.setSingleShot(True)
        search_hlayout.addWidget(self.search_input)
        self.global_vlayout.addLayout(search_hlayout)

        # scroll area cho danh sách services
        services_scroll_area = ScrollAreaCustom()
        services_scroll_area.setWidgetResizable(True)
        # services_scroll_area.setHorizontalScrollBarPolicy(aqt.qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Allow horizontal scroll if needed
        services_scroll_area.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignTop) # Align top
        services_widget = aqt.qt.QWidget()
        self.services_vlayout = aqt.qt.QVBoxLayout(services_widget)
        self.services_vlayout.setSpacing(14)

        # Split services
        tts_services = [s for s in service_list if s.service_type == constants.ServiceType.tts]
        dict_services = [s for s in service_list if s.service_type == constants.ServiceType.dictionary]

        # Helper to draw category
        def draw_category(title, services, parent_layout, default_expanded=True):
            if not services:
                return

            group_box = aqt.qt.QGroupBox(title)
            group_box.setCheckable(False)
            group_box.setStyleSheet(
                "QGroupBox { margin-top: 8px; font-weight: 600; }"
                "QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }"
            )

            group_layout = aqt.qt.QVBoxLayout()
            group_layout.setContentsMargins(10, 10, 10, 8)
            group_layout.setSpacing(8)
            
            # Toggle All Checkbox
            toggle_all_cb = aqt.qt.QCheckBox(i18n.get_text("generic_enable_all", lang))
            toggle_all_cb.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
            toggle_all_cb.setTristate(False)
            toggle_all_font = toggle_all_cb.font()
            toggle_all_font.setPointSize(10)
            toggle_all_cb.setFont(toggle_all_font)

            # Guard flag to prevent infinite signal loops between toggle_all \u2194 individual
            updating = {"value": False}

            # Initialize state: default all enabled
            all_enabled = all(s.enabled for s in services)
            toggle_all_cb.setChecked(all_enabled)

            # Master \u2192 individual: check/uncheck all services in this category
            def toggle_all_services(checked):
                if updating["value"]:
                    return
                updating["value"] = True
                for service in services:
                    cb = self.service_checkbox_map.get(service.name)
                    if cb:
                        if cb.isChecked() != checked:
                            cb.setChecked(checked)
                updating["value"] = False
            
            toggle_all_cb.clicked.connect(toggle_all_services)
            group_layout.addWidget(toggle_all_cb)

            # Draw services
            for service in services:
                self.draw_service(service, group_layout)
                # Specialized logic per service type/name can go here (EdgeTTS badge integrated into header)

                # Individual \u2192 master: sync toggle_all when any single checkbox changes
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
            return toggle_all_cb

        # Draw Categories \u2014 clean text, no emoji
        
        self.tts_group_toggle = draw_category(
            i18n.get_text("config_category_tts", lang), tts_services, self.services_vlayout)

        self.dict_group_toggle = draw_category(
            i18n.get_text("config_category_dictionary", lang), dict_services, self.services_vlayout)

        self.services_vlayout.addStretch()

        services_scroll_area.setWidget(services_widget)
        self.global_vlayout.addWidget(services_scroll_area, 1)

        # 4. About Section (invisible by default, but reachable via TOC)
        self.about_container = aqt.qt.QWidget()
        self.about_layout = aqt.qt.QVBoxLayout(self.about_container)
        self.about_component.draw(self.about_layout)
        self.about_container.setVisible(False) # We'll swap visibility
        self.global_vlayout.addWidget(self.about_container, 1)

        # bottom buttons
        # ==============

        buttons_layout = aqt.qt.QHBoxLayout()
        self.save_button = aqt.qt.QPushButton(i18n.get_text("button_save", lang))
        self.save_button.setEnabled(False)
        gui_utils.configure_primary_button(self.save_button, min_height=40, min_width=100, font_size=11)
        self.cancel_button = aqt.qt.QPushButton(i18n.get_text("button_cancel", lang))
        gui_utils.configure_secondary_button(self.cancel_button, min_height=40, min_width=100, font_size=11)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        self.global_vlayout.addLayout(buttons_layout)

        # wire events
        # ===========


        self.save_button.pressed.connect(self.save_button_pressed)
        self.cancel_button.pressed.connect(self.cancel_button_pressed)

        # run event once
        self.enable_model_change = True

        # h\u00e0nh vi search: l\u1ecdc theo t\u00ean service (\u1ea9n c\u00e1c service kh\u00f4ng kh\u1edbp) v\u00e0 cu\u1ed9n t\u1edbi k\u1ebf t qu\u1ea3 \u0111\u1ea7u ti\u00ean
        def run_search():
            query = self.search_input.text().strip().lower()
            first_match_widget = None

            # n\u1ebfu \u00f4 t\u00ecm ki\u1ebfm r\u1edng -> hi\u1ec3n th\u1ecb l\u1ea1i t\u1ea5t c\u1ea3 services
            if not query:
                for service in service_list:
                    card_widget = self.service_card_map.get(service.name)
                    if card_widget is not None:
                        card_widget.setVisible(True)
                return

            # l\u1ecdc: ch\u1ec9 hi\u1ec3n th\u1ecb c\u00e1c service c\u00f3 t\u00ean ch\u1ee9a query
            for service in service_list:
                card_widget = self.service_card_map.get(service.name)
                if card_widget is None:
                    continue
                search_blob = self.service_search_index.get(service.name, service.name.lower())
                if query in search_blob:
                    card_widget.setVisible(True)
                    if first_match_widget is None:
                        first_match_widget = card_widget
                else:
                    card_widget.setVisible(False)

            # cu\u1ed9n \u0111\u1ebfn k\u1ebft qu\u1ea3 \u0111\u1ea7u ti\u00ean n\u1ebfu c\u00f3
            if first_match_widget is not None and self._services_scroll_area is not None:
                self._services_scroll_area.ensureWidgetVisible(first_match_widget)

        # filter với debounce để tránh relayout dồn khi gõ nhanh
        self.search_debounce_timer.timeout.connect(run_search)

        def schedule_search(_text):
            self.search_debounce_timer.start(180)

        self.search_input.textChanged.connect(schedule_search)

        self._refresh_services_summary_label()

        # === Swiss Style main layout: TOC b\u00ean tr\u00e1i, content b\u00ean ph\u1ea3i ===
        main_hlayout = aqt.qt.QHBoxLayout()
        main_hlayout.setContentsMargins(0, 0, 0, 0)
        main_hlayout.setSpacing(0)

        # TOC panel (sidebar tr\u00e1i) - \u0111\u00f3ng vai tr\u00f2 m\u1ee5c l\u1ee5c / filter
        toc_widget = aqt.qt.QWidget()
        toc_layout = aqt.qt.QVBoxLayout(toc_widget)
        toc_layout.setContentsMargins(8, 8, 8, 8)
        toc_layout.setSpacing(12)

        toc_title_label = aqt.qt.QLabel(i18n.get_text("config_toc_title", lang))
        toc_title_font = toc_title_label.font()
        toc_title_font.setBold(True)
        toc_title_font.setPointSize(max(toc_title_font.pointSize(), 11))
        toc_title_label.setFont(toc_title_font)
        toc_layout.addWidget(toc_title_label)

        # TOC theo nh\u00f3m + t\u1eebng service (Dictionary / TTS)

        # n\u00fat: T\u1ea5t c\u1ea3 d\u1ecbch v\u1ee5 (scroll v\u1ec1 \u0111\u1ea7u danh s\u00e1ch)
        btn_all = aqt.qt.QPushButton(i18n.get_text("config_toc_services", lang))
        btn_all.setFlat(True)
        btn_all.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
        btn_all.setStyleSheet("""
            QPushButton { text-align: left; padding: 6px 10px; border: none; font-weight: bold; }
            QPushButton:hover { background-color: palette(alternate-base); border-radius: 4px; }
        """)
        btn_all.pressed.connect(make_scroll_fn(self._services_container_widget))
        toc_layout.addWidget(btn_all)

        # nh\u00f3m \"T\u1eeb \u0111i\u1ec3n\" v\u1edbi t\u1eebng service con
        dictionary_services = [s for s in service_list if s.service_type == constants.ServiceType.dictionary]
        tts_services = [s for s in service_list if s.service_type == constants.ServiceType.tts]

        if dictionary_services:
            dict_header = aqt.qt.QLabel(i18n.get_text("config_category_dictionary", lang))
            dict_font = dict_header.font()
            dict_font.setBold(True)
            dict_font.setPointSize(max(dict_font.pointSize(), 10))
            dict_header.setFont(dict_font)
            toc_layout.addWidget(dict_header)
            for s in dictionary_services:
                card_widget = self.service_card_map.get(s.name)
                btn = aqt.qt.QPushButton(s.name)
                btn.setFlat(True)
                btn.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton { text-align: left; padding: 4px 16px; border: none; font-size: 11px; }
                    QPushButton:hover { background-color: palette(alternate-base); border-radius: 6px; }
                """)
                btn.pressed.connect(make_scroll_fn(card_widget))
                toc_layout.addWidget(btn)

        if tts_services:
            tts_header = aqt.qt.QLabel(i18n.get_text("config_category_tts", lang))
            tts_font = tts_header.font()
            tts_font.setBold(True)
            tts_font.setPointSize(max(tts_font.pointSize(), 10))
            tts_header.setFont(tts_font)
            toc_layout.addWidget(tts_header)
            for s in tts_services:
                card_widget = self.service_card_map.get(s.name)
                btn = aqt.qt.QPushButton(s.name)
                btn.setFlat(True)
                btn.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton { text-align: left; padding: 4px 16px; border: none; font-size: 11px; }
                    QPushButton:hover { background-color: palette(alternate-base); border-radius: 6px; }
                """)
                btn.pressed.connect(make_scroll_fn(card_widget))
                toc_layout.addWidget(btn)

        toc_layout.addSpacing(20)
        
        # Tab "About" in TOC
        btn_about = aqt.qt.QPushButton(i18n.get_text("config_toc_about", lang))
        btn_about.setFlat(True)
        btn_about.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
        btn_about.setStyleSheet("""
            QPushButton { text-align: left; padding: 6px 10px; border: none; font-weight: bold; }
            QPushButton:hover { background-color: palette(alternate-base); border-radius: 4px; }
        """)
        
        def show_about():
            self._services_scroll_area.setVisible(False)
            self.about_container.setVisible(True)
            # Hide search bar when in About tab
            self.search_input.setVisible(False)
            header_label.setVisible(False)
            services_description_label.setVisible(False)
            self.services_summary_label.setVisible(False)

        def show_services():
            self._services_scroll_area.setVisible(True)
            self.about_container.setVisible(False)
            # Show search bar
            self.search_input.setVisible(True)
            header_label.setVisible(True)
            services_description_label.setVisible(True)
            self.services_summary_label.setVisible(True)

        btn_about.pressed.connect(show_about)
        btn_all.pressed.connect(show_services)
        
        toc_layout.addWidget(btn_about)
        logo_in_sidebar = aqt.qt.QWidget()
        logo_in_sidebar.setLayout(gui_utils.get_superfreetss_label_header(False))
        toc_layout.addWidget(logo_in_sidebar)
        toc_layout.addStretch()

        toc_widget.setMinimumWidth(176)
        toc_widget.setMaximumWidth(240)
        toc_widget.setSizePolicy(aqt.qt.QSizePolicy.Policy.Preferred, aqt.qt.QSizePolicy.Policy.Expanding)
        toc_widget.setStyleSheet("""
            QWidget {
                border-right: 1px solid palette(mid);
                background-color: palette(window);
            }
        """)

        # g\u1eafn TOC v\u00e0 content v\u00e0o layout ch\u00ednh
        main_hlayout.addWidget(toc_widget)

        content_widget = aqt.qt.QWidget()
        content_widget.setLayout(self.global_vlayout)
        main_hlayout.addWidget(content_widget, 1)

        # l\u01b0u reference \u0111\u1ec3 TOC c\u00f3 th\u1ec3 scroll t\u1edbi ph\u1ea7n services
        self._services_scroll_area = services_scroll_area
        self._services_container_widget = services_widget

        layout.addLayout(main_hlayout)

    @sc.event(Event.click_save)
    def save_button_pressed(self):
        with self.hypertts.error_manager.get_single_action_context('Saving Service Configuration'):
            self.hypertts.save_configuration(self.model)
            self.hypertts.reconfigure_service_manager()
            self.dialog.close()

    @sc.event(Event.click_cancel)
    def cancel_button_pressed(self):
        self.dialog.close()