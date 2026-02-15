from pydoc import describe
import sys
import os
import aqt.qt
import webbrowser

from . import component_common
from . import config_models
from . import constants
from . import constants_events
from .constants_events import Event
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


sc = stats.StatsContext(constants_events.EventContext.services)

class Configuration(component_common.ConfigComponentBase):

    @sc.event(Event.open)
    def __init__(self, hypertts, dialog):
        self.hypertts = hypertts
        self.dialog = dialog
        self.model = config_models.Configuration()
        self.service_stack_map = {}
        self.clt_stack_map = {}
        # map service.name -> service enabled checkbox (dùng cho Enable All)
        self.service_checkbox_map = {}
        # map service.name -> service card widget (dùng cho TOC bên trái)
        self.service_card_map = {}
        # tham chiếu scroll area + container, được set trong draw()
        self._services_scroll_area = None
        self._services_container_widget = None
        self.enable_model_change = False
        self.api_key_valid = False
        self.about_component = component_about.AboutComponent(hypertts)

    def get_model(self):
        return self.model

    def load_model(self, model):
        self.model = model

    def hyperttspro_account_config_change(self, account_config: config_models.HyperTTSProAccountConfig):
        # Super Free TTS: Pro mode disabled, keep method for API compat
        pass

    def model_change(self):
        if self.enable_model_change:
            self.save_button.setEnabled(True)
            self.save_button.setStyleSheet(self.hypertts.anki_utils.get_green_stylesheet())

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

    def cloud_language_tools_enabled(self):
        # Super Free TTS: CLT/Pro always disabled
        return False

    def set_cloud_language_tools_enabled(self):
        # Super Free TTS: Always show Lite header, no CLT logic needed
        pass

    def manage_service_stack(self, service, service_stack, clt_stack):
        # Super Free TTS: Always show the free service stack
        service_stack.setVisible(True)
        clt_stack.setVisible(False)

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
            options_gridlayout.addWidget(aqt.qt.QLabel(key + ':'), row, 0, 1, 1)
            if type == str:
                lineedit = aqt.qt.QLineEdit()
                lineedit.setText(self.model.get_service_configuration_key(service.name, key))
                lineedit.setObjectName(widget_name)
                lineedit.textChanged.connect(self.get_service_config_str_change_fn(service, key))
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
                lineedit = aqt.qt.QLineEdit()
                lineedit.setText(self.model.get_service_configuration_key(service.name, key))
                lineedit.setObjectName(widget_name)
                lineedit.textChanged.connect(self.get_service_config_str_change_fn(service, key))
                
                btn = aqt.qt.QPushButton("Browse...")
                def browse_file(le=lineedit, f=filter_str):
                    path, _ = aqt.qt.QFileDialog.getOpenFileName(self.dialog, "Select File", "", f)
                    if path:
                        le.setText(path)
                btn.clicked.connect(lambda checked=False, le=lineedit, f=filter_str: browse_file(le, f))
                gui_utils.configure_secondary_button(btn)
                
                h_layout.addWidget(lineedit)
                h_layout.addWidget(btn)
                
                # Special logic for KokoroTTS Engine Path: Add "Install/Update" button
                if service.name == "KokoroTTS" and key == "engine_path":
                     install_btn = aqt.qt.QPushButton("Install Kokoro...")
                     def open_kokoro_manager(le=lineedit):
                         dlg = component_kokoro_manager.KokoroInstallManager(self.dialog)
                         if dlg.exec():
                             # If installed successfully, update the path
                             default_path = os.path.join(component_kokoro_manager.PYTHON_EXE)
                             if os.path.exists(default_path):
                                 le.setText(default_path)
                     install_btn.clicked.connect(lambda checked=False, le=lineedit: open_kokoro_manager(le))
                     gui_utils.configure_primary_button(install_btn)
                     h_layout.addWidget(install_btn)

                # Special logic for MmsTTS: Add "Install MMS..." button
                if service.name == "MmsTTS" and key == "python_path":
                     install_btn = aqt.qt.QPushButton("Install MMS...")
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
                     h_layout.addWidget(install_btn)

                options_gridlayout.addLayout(h_layout, row, 1, 1, 1)

            elif isinstance(type, tuple) and type[0] == 'directory': # ('directory', 'Title')
                title_str = type[1]
                h_layout = aqt.qt.QHBoxLayout()
                lineedit = aqt.qt.QLineEdit()
                lineedit.setText(self.model.get_service_configuration_key(service.name, key))
                lineedit.setObjectName(widget_name)
                lineedit.textChanged.connect(self.get_service_config_str_change_fn(service, key))
                
                btn = aqt.qt.QPushButton("Browse...")
                def browse_dir(le=lineedit):
                    path = aqt.qt.QFileDialog.getExistingDirectory(self.dialog, "Select Directory")
                    if path:
                        le.setText(path)
                btn.clicked.connect(lambda checked=False, le=lineedit: browse_dir(le))
                gui_utils.configure_secondary_button(btn)
                
                h_layout.addWidget(lineedit)
                h_layout.addWidget(btn)
                
                # Special logic for PiperTTS Models Path: Add "Download Models" button
                if service.name == "PiperTTS" and key == "models_path":
                     dl_btn = aqt.qt.QPushButton("Download Models...")
                     def open_downloader(le=lineedit):
                         dest_dir = le.text()
                         if not dest_dir:
                             aqt.utils.showInfo("Please select a models directory first.")
                             return
                         dlg = component_piper_manager.PiperManagerDialog(self.dialog, dest_dir)
                         dlg.exec()
                     dl_btn.clicked.connect(lambda checked=False, le=lineedit: open_downloader(le))
                     gui_utils.configure_primary_button(dl_btn)
                     h_layout.addWidget(dl_btn)

                # MeloTTS removed

                options_gridlayout.addLayout(h_layout, row, 1, 1, 1)

            elif isinstance(type, list):
                combobox = aqt.qt.QComboBox()
                combobox.setObjectName(widget_name)
                combobox.addItems(type)
                combobox.setCurrentText(self.model.get_service_configuration_key(service.name, key))
                combobox.currentTextChanged.connect(self.get_service_config_list_change_fn(service, key))
                options_gridlayout.addWidget(combobox, row, 1, 1, 1)
            row += 1
        
        layout.addLayout(options_gridlayout)

        # trả về checkbox để caller có thể dùng cho việc highlight card
        return service_enabled_checkbox

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
                    border: 1px solid {constants.COLOR_ACCENT}; 
                    border-radius: 12px;
                }}"""
            )
        else:
            service_card.setStyleSheet(
                """QFrame { 
                    background-color: transparent; 
                    border: 1px solid #E2E8F0; 
                    border-radius: 12px;
                }"""
            )

    def draw_service(self, service, layout):
        logger.info(f'draw_service {service.name}')
        
        def get_service_header_label(service):
            header_label = gui_utils.get_service_header_label(service.name)
            return header_label        

        def get_service_description_label(service):
            # Dùng i18n để mô tả rõ ràng hơn theo ngôn ngữ giao diện
            lang = self.hypertts.get_ui_language()
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
            header_row.addWidget(gui_utils.get_status_badge("Free"))
            
        header_row.addStretch()
        combined_service_vlayout.addLayout(header_row)
        combined_service_vlayout.addWidget(get_service_description_label(service))

        # add service config options, when cloudlanguagetools not enabled
        # ===============================================================

        invisible_widget = aqt.qt.QWidget()
        invisible_widget.setVisible(False)


        service_stack = aqt.qt.QWidget(invisible_widget)
        service_vlayout = aqt.qt.QVBoxLayout()
        service_vlayout.setContentsMargins(0, 0, 0, 0)
        if service.cloudlanguagetools_enabled():
            buttons_layout = aqt.qt.QHBoxLayout()
            logo = gui_utils.get_graphic(constants.GRAPHICS_SERVICE_COMPATIBLE)
            buttons_layout.addStretch()
            buttons_layout.addWidget(logo)
            service_vlayout.addLayout(buttons_layout)
        service_enabled_checkbox = self.draw_service_options(service, service_vlayout)
        service_stack.setLayout(service_vlayout)

        # when cloudlanguagetools is enabled
        # ==================================
        clt_stack = aqt.qt.QWidget(invisible_widget)
        clt_vlayout = aqt.qt.QVBoxLayout()
        clt_vlayout.setContentsMargins(0, 0, 0, 0)
        logo = gui_utils.get_graphic(constants.GRAPHICS_SERVICE_ENABLED)
        clt_vlayout.addWidget(logo)
        clt_stack.setLayout(clt_vlayout)


        self.manage_service_stack(service, service_stack, clt_stack)

        self.service_stack_map[service.name] = service_stack
        self.clt_stack_map[service.name] = clt_stack

        combined_service_vlayout.addWidget(service_stack)
        combined_service_vlayout.addWidget(clt_stack)

        # bọc tất cả vào một "card" tối giản để phân tách từng service rõ ràng
        service_card = aqt.qt.QFrame()
        service_card.setLayout(combined_service_vlayout)
        service_card.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)

        # áp dụng style ban đầu dựa trên trạng thái enabled hiện tại
        self._apply_service_card_style(service_card, service_enabled_checkbox.isChecked())

        # khi user bật/tắt checkbox, update luôn style của card
        def on_enabled_changed(state):
            self._apply_service_card_style(service_card, state == 2)

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
        def service_sort_key(service):
            return service.name
        # HyperTTS Lite: Only show Free services
        service_list = [s for s in self.hypertts.service_manager.get_all_services() if s.service_fee == constants.ServiceFee.free]
        service_list.sort(key=service_sort_key)
        return service_list


    def draw(self, layout):
        lang = self.hypertts.get_ui_language()
        # layout gốc cho phần nội dung bên phải (Content Panel)
        self.global_vlayout = aqt.qt.QVBoxLayout()

        def make_scroll_fn(target_widget):
            def _scroll():
                if self._services_scroll_area is not None and target_widget is not None:
                    self._services_scroll_area.ensureWidgetVisible(target_widget)
            return _scroll

        # logo header (always Lite/Free)

        # logo header (always Lite/Free)
        # ===============================
        header_widget = aqt.qt.QWidget()
        header_widget.setLayout(gui_utils.get_superfreetss_label_header(False))
        self.global_vlayout.addWidget(header_widget)

        # superfreetss pro is removed in Lite version

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
        header_label.setFont(header_font)
        self.global_vlayout.addWidget(header_label)
        # mô tả ngắn cho người dùng mới
        services_description_label = aqt.qt.QLabel(i18n.get_text("services_header_description", lang))
        services_description_label.setWordWrap(True)
        self.global_vlayout.addWidget(services_description_label)

        # thanh tìm kiếm dịch vụ (bên khu vực Dịch vụ TTS, không nằm ở TOC)
        search_hlayout = aqt.qt.QHBoxLayout()
        self.search_input = aqt.qt.QLineEdit()
        self.search_input.setPlaceholderText(i18n.get_text("config_search_placeholder", lang))
        search_hlayout.addWidget(self.search_input)
        self.global_vlayout.addLayout(search_hlayout)

        # scroll area cho danh sách services
        services_scroll_area = ScrollAreaCustom()
        services_scroll_area.setWidgetResizable(True)
        # services_scroll_area.setHorizontalScrollBarPolicy(aqt.qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Allow horizontal scroll if needed
        services_scroll_area.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignTop) # Align top
        services_widget = aqt.qt.QWidget()
        self.services_vlayout = aqt.qt.QVBoxLayout(services_widget)
        self.services_vlayout.setSpacing(20) # Spacing between categories

        # Split services
        tts_services = [s for s in service_list if s.service_type == constants.ServiceType.tts]
        dict_services = [s for s in service_list if s.service_type == constants.ServiceType.dictionary]

        # Helper to draw category
        def draw_category(title, services, parent_layout, default_expanded=True):
            if not services:
                return

            group_box = aqt.qt.QGroupBox(title)
            group_box.setCheckable(False)

            group_layout = aqt.qt.QVBoxLayout()
            group_layout.setSpacing(8)
            
            # Toggle All Checkbox
            toggle_all_cb = aqt.qt.QCheckBox(i18n.get_text("generic_enable_all", lang))
            toggle_all_cb.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
            toggle_all_cb.setTristate(False)
            toggle_all_font = toggle_all_cb.font()
            toggle_all_font.setPointSize(10)
            toggle_all_cb.setFont(toggle_all_font)

            # Guard flag to prevent infinite signal loops between toggle_all ↔ individual
            updating = {"value": False}

            # Initialize state: default all enabled
            all_enabled = all(s.enabled for s in services)
            toggle_all_cb.setChecked(all_enabled)

            # Master → individual: check/uncheck all services in this category
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
                # Highlight EdgeTTS with a "Recommended" badge
                if service.name == "EdgeTTS":
                    card = self.service_card_map.get(service.name)
                    if card:
                        card_layout = card.layout()
                        if card_layout:
                            badge_row = aqt.qt.QHBoxLayout()
                            badge = gui_utils.get_status_badge(
                                i18n.get_text("service_badge_recommended", lang))
                            badge_row.addWidget(badge)
                            badge_row.addStretch()
                            card_layout.insertLayout(0, badge_row)

                # Individual → master: sync toggle_all when any single checkbox changes
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

        # Draw Categories — clean text, no emoji
        
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

        # self.enable_all_free_services_button.pressed.connect(self.enable_all_free_services)
        # self.disable_all_services_button.pressed.connect(self.disable_all_services)

        self.save_button.pressed.connect(self.save_button_pressed)
        self.cancel_button.pressed.connect(self.cancel_button_pressed)

        # run event once
        # self.pro_api_key_entered()
        self.enable_model_change = True

        # hành vi search: lọc theo tên service (ẩn các service không khớp) và cuộn tới kết quả đầu tiên
        def run_search():
            query = self.search_input.text().strip().lower()
            first_match_widget = None

            # nếu ô tìm kiếm rỗng -> hiển thị lại tất cả services
            if not query:
                for service in service_list:
                    card_widget = self.service_card_map.get(service.name)
                    if card_widget is not None:
                        card_widget.setVisible(True)
                return

            # lọc: chỉ hiển thị các service có tên chứa query
            for service in service_list:
                card_widget = self.service_card_map.get(service.name)
                if card_widget is None:
                    continue
                if query in service.name.lower():
                    card_widget.setVisible(True)
                    if first_match_widget is None:
                        first_match_widget = card_widget
                else:
                    card_widget.setVisible(False)

            # cuộn đến kết quả đầu tiên nếu có
            if first_match_widget is not None and self._services_scroll_area is not None:
                self._services_scroll_area.ensureWidgetVisible(first_match_widget)

        # filter ngay khi người dùng gõ (debounce nhẹ do Qt tự xử lý sự kiện tuần tự)
        self.search_input.textChanged.connect(lambda _text: run_search())

        # === Swiss Style main layout: TOC bên trái, content bên phải ===
        main_hlayout = aqt.qt.QHBoxLayout()

        # TOC panel (sidebar trái) - đóng vai trò mục lục / filter
        toc_widget = aqt.qt.QWidget()
        toc_layout = aqt.qt.QVBoxLayout(toc_widget)
        toc_layout.setContentsMargins(8, 8, 8, 8)
        toc_layout.setSpacing(12)

        toc_title_label = aqt.qt.QLabel(i18n.get_text("config_toc_title", lang))
        toc_title_font = toc_title_label.font()
        toc_title_font.setBold(True)
        toc_title_label.setFont(toc_title_font)
        toc_layout.addWidget(toc_title_label)

        # TOC theo nhóm + từng service (Dictionary / TTS)

        # nút: Tất cả dịch vụ (scroll về đầu danh sách)
        btn_all = aqt.qt.QPushButton(i18n.get_text("config_toc_services", lang))
        btn_all.setFlat(True)
        btn_all.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
        btn_all.setStyleSheet("""
            QPushButton { text-align: left; padding: 6px 10px; border: none; font-weight: bold; }
            QPushButton:hover { background-color: palette(alternate-base); border-radius: 4px; }
        """)
        btn_all.pressed.connect(make_scroll_fn(self._services_container_widget))
        toc_layout.addWidget(btn_all)

        # nhóm \"Từ điển\" với từng service con
        dictionary_services = [s for s in service_list if s.service_type == constants.ServiceType.dictionary]
        tts_services = [s for s in service_list if s.service_type == constants.ServiceType.tts]

        if dictionary_services:
            dict_header = aqt.qt.QLabel(i18n.get_text("config_category_dictionary", lang))
            dict_font = dict_header.font()
            dict_font.setBold(True)
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

        def show_services():
            self._services_scroll_area.setVisible(True)
            self.about_container.setVisible(False)
            # Show search bar
            self.search_input.setVisible(True)
            header_label.setVisible(True)
            services_description_label.setVisible(True)

        btn_about.pressed.connect(show_about)
        btn_all.pressed.connect(show_services)
        
        toc_layout.addWidget(btn_about)
        toc_layout.addStretch()

        toc_widget.setFixedWidth(220)
        toc_widget.setStyleSheet("""
            QWidget {
                border-right: 1px solid palette(mid);
                background-color: palette(window);
            }
        """)

        # gắn TOC và content vào layout chính
        main_hlayout.addWidget(toc_widget)

        content_widget = aqt.qt.QWidget()
        content_widget.setLayout(self.global_vlayout)
        main_hlayout.addWidget(content_widget, 1)

        # lưu reference để TOC có thể scroll tới phần services
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