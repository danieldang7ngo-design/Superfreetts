import aqt.qt

from . import gui_utils
from . import i18n
from .component_services_legacy import Configuration as LegacyServicesComponent


class ServicesPage(LegacyServicesComponent):
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


Configuration = ServicesPage
