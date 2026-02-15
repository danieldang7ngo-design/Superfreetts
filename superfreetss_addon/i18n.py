from typing import Dict

# Danh sách ngôn ngữ giao diện được hỗ trợ
SUPPORTED_LANGUAGES = ["en", "vi"]

# Bảng chuỗi cho từng ngôn ngữ.
# Lưu ý: nếu thêm key mới, cần thêm cho cả "en" và "vi".
STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        # Menus / dialog titles
        "menu_services_configuration": "Super Free TTS: Services Configuration",
        "menu_preferences": "Super Free TTS: Preferences",
        "dialog_services_title": "Super Free TTS: Services Configuration",
        "dialog_preferences_title": "Super Free TTS: Preferences",
        "dialog_easy_title": "Super Free TTS: Add Audio (Easy)",
        "dialog_collection_title": "Super Free TTS: Add Audio (Collection)",
        "dialog_realtime_title": "Super Free TTS: Add Audio (Realtime)",
        "dialog_preset_rules_title": "Super Free TTS: Preset Rules",

        # Generic buttons
        "button_save": "Save",
        "button_cancel": "Cancel",
        "button_close": "Close",
        "generic_enable": "Enable",
        "generic_enable_all": "Enable All",
        "button_open": "Open",
        "button_duplicate": "Duplicate",
        "button_rename": "Rename",
        "button_delete": "Delete",
        "button_save_and_close": "Save and Close",
        "button_advanced": "Advanced",
        "dialog_save_changes": "Save changes to current preset?",
        "dialog_enter_new_name": "Enter new preset name",
        "dialog_rename_title": "Rename Preset",
        "dialog_delete_confirm": "Delete Preset {0}?",
        "dialog_choose_preset_open": "Choose a preset to open",
        "dialog_choose_preset_duplicate": "Choose a preset to duplicate",

        # Easy mode buttons
        "easy_button_preview_audio": "Preview Audio",
        "easy_button_previewing": "Playing Preview...",
        "easy_button_add_audio": "Add Audio",
        "easy_button_adding_audio": "Adding Audio...",
        "easy_button_more_settings": "More Settings...",
        "easy_button_hide_settings": "Hide Settings...",

        # Collection / batch buttons
        "batch_button_preset": "Preset:",
        "batch_button_preview_sound": "Preview Sound",
        "batch_button_apply_to_notes": "Apply To Notes",
        "batch_button_apply_to_note": "Apply To Note",
        "batch_button_loading": "Loading...",
        "batch_button_save_and_close": "Save and Close",
        "batch_button_open": "Open",
        "batch_button_duplicate": "Duplicate",
        "batch_button_rename": "Rename",
        "batch_button_delete": "Delete",
        "batch_button_done": "Done",
        "batch_button_select_note_to_preview": "Select Note to Preview Sound",

        # Realtime buttons / tabs
        "realtime_button_apply_to_note": "Apply To Note",
        "realtime_tab_front": "Front Side",
        "realtime_tab_back": "Back Side",

        # Preset mapping rules
        "preset_rules_group_note_info": "Note Info",
        "preset_rules_group_need_help": "Need Help?",
        "preset_rules_group_settings": "Settings",
        "preset_rules_group_preset_rules": "Preset Rules",
        "preset_rules_button_preview_all": "Preview All",
        "preset_rules_button_run_all": "Run All",
        "preset_rules_button_add_rule": "Add Rule",
        "preset_rules_button_save_and_close": "Save and Close",

        # Voice selection
        "voice_filters_group_title": "Voice Filters",
        "voice_label_language": "Language",
        "voice_label_locale": "Locale",
        "voice_label_service": "Service",
        "voice_label_gender": "Gender",
        "voice_button_reset_filters": "Reset Filters",
        "voice_group_voice": "Voice",
        "voice_button_play_sample": "Play Sample",
        "voice_button_play_sample_wait": "Select note to play sample",
        "voice_group_selection_mode": "Selection Mode",
        "voice_radio_single": "Single: a single voice will be used for all notes.",
        "voice_radio_random": "Random: select randomly from a list of voices.",
        "voice_radio_priority": "Priority: try first voice, then move to second if not found.",
        "voice_group_voice_list": "Voice List",
        "voice_button_add_voice": "Add Voice",
        "voice_button_remove_voice": "Remove",
        "voice_button_move_up": "Up",
        "voice_button_move_down": "Down",

        # Services configuration
        "services_header_title": "Services",
        "services_header_description": "Choose which free text-to-speech services you want to use. You can enable multiple services at once.",
        "services_button_enable_all_free": "Enable All Free Services",
        "services_button_disable_all": "Disable All Services",
        "config_toc_title": "Configuration",
        "config_toc_services": "Services",
        "config_toc_about": "About",
        "config_search_placeholder": "Search service…",

        # Service fee / type descriptions
        "service_fee_free": "Free",
        "service_fee_paid": "Paid",
        "service_type_dictionary_description": "Dictionary, contains recordings of words.",
        "service_type_tts_description": "Text To Speech, can generate audio for full sentences.",

        # Specific service descriptions
        "service_description_GoogleTranslate": "Uses Google's free translation API. Multilingual support. (Online)",
        "service_description_EdgeTTS": "High quality, natural sounding AI voices from Microsoft Edge. (Online)",
        "service_description_Windows": "Standard Windows voices (SAPI 5). Fast and works offline.",
        "service_description_MacOS": "Standard MacOS voices. High quality and works offline.",
        "service_description_ESpeakNg": "Open source synthesizer. Robotic voice but very fast and supports many languages. (Offline)",

        # Tabs (batch dialog)
        "tab_source": "Source",
        "tab_target": "Target",
        "tab_voice_selection": "Voice Selection",
        "tab_text_processing": "Text Processing",

        # Batch dialog extra buttons
        "batch_button_show_settings": "Show Settings",
        "batch_button_hide_settings": "Hide Settings",

        # Preferences - language
        "preferences_group_language_title": "Language / Ngôn ngữ",
        "preferences_label_interface_language": "Interface Language / Ngôn ngữ giao diện",
        "preferences_option_language_en": "English",
        "preferences_option_language_vi": "Tiếng Việt",
        "preferences_language_tooltip": "Choose the language for Super Free TTS buttons and dialogs.",

        # Choose Easy/Advanced dialog
        "choose_mode_title": "How would you like to add audio?",
        "choose_mode_subtitle": "Pick the mode that fits your workflow. You can change this later.",
        "choose_mode_easy_title": "Easy Mode",
        "choose_mode_easy_desc": "Simple interface for adding audio manually. Just choose the field and the voice. Similar to AwesomeTTS.",
        "choose_mode_advanced_title": "Advanced Mode",
        "choose_mode_advanced_desc": "Full interface with presets, batch processing, and mapping rules. Offers complete control.",
        "choose_mode_footer": "You can change this later in the editor button bar (Configure preset rules).",

        # Service badges
        "service_badge_recommended": "Recommended",
        "service_badge_free": "Free",
        "service_badge_enabled": "Enabled",

        # Category labels (no emoji)
        "config_category_tts": "TTS Services",
        "config_category_dictionary": "Dictionary Services",
        "about_header_title": "About SuperFreeTTS",
        "about_contributor": "Honorable Contributor",
        "about_author": "Author",
        "about_version": "Version",
        "about_website": "Website",
        "about_facebook": "Facebook",
        "about_description": "SuperFreeTTS is a 100% free text-to-speech addon for Anki, designed to make language learning more accessible and effective.",
    },
    "vi": {
        # Menus / dialog titles
        "menu_services_configuration": "Super Free TTS: Cấu hình dịch vụ",
        "menu_preferences": "Super Free TTS: Tùy chọn",
        "dialog_services_title": "Super Free TTS: Cấu hình dịch vụ",
        "dialog_preferences_title": "Super Free TTS: Tùy chọn",
        "dialog_easy_title": "Super Free TTS: Thêm âm thanh (Dễ)",
        "dialog_collection_title": "Super Free TTS: Thêm âm thanh (Nhiều thẻ)",
        "dialog_realtime_title": "Super Free TTS: Âm thanh tự phát (Realtime)",
        "dialog_preset_rules_title": "Super Free TTS: Quy tắc preset",

        # Generic buttons
        "button_save": "Lưu",
        "button_cancel": "Hủy",
        "button_close": "Đóng",
        "generic_enable": "Bật",
        "generic_enable_all": "Bật tất cả",
        "button_open": "Mở",
        "button_duplicate": "Sao chép",
        "button_rename": "Đổi tên",
        "button_delete": "Xóa",
        "button_save_and_close": "Lưu và Đóng",
        "button_advanced": "Nâng cao",

        # Easy mode buttons
        "easy_button_preview_audio": "Nghe thử",
        "easy_button_previewing": "Đang phát thử...",
        "easy_button_add_audio": "Thêm âm thanh",
        "easy_button_adding_audio": "Đang thêm âm thanh...",
        "easy_button_more_settings": "Tùy chọn nâng cao...",
        "easy_button_hide_settings": "Ẩn bớt tùy chọn...",

        # Collection / batch buttons
        "batch_button_preset": "Preset:",
        "batch_button_preview_sound": "Nghe thử",
        "batch_button_apply_to_notes": "Áp dụng cho nhiều thẻ",
        "batch_button_apply_to_note": "Áp dụng cho thẻ",
        "batch_button_loading": "Đang xử lý...",
        "batch_button_save_and_close": "Lưu và đóng",
        "batch_button_open": "Mở",
        "batch_button_duplicate": "Nhân bản",
        "batch_button_rename": "Đổi tên",
        "batch_button_delete": "Xóa",
        "batch_button_done": "Hoàn tất",
        "batch_button_select_note_to_preview": "Chọn thẻ để nghe thử",

        # Realtime buttons / tabs
        "realtime_button_apply_to_note": "Áp dụng cho thẻ",
        "realtime_tab_front": "Mặt trước",
        "realtime_tab_back": "Mặt sau",

        # Preset mapping rules
        "preset_rules_group_note_info": "Thông tin thẻ",
        "preset_rules_group_need_help": "Cần trợ giúp?",
        "preset_rules_group_settings": "Cài đặt",
        "preset_rules_group_preset_rules": "Quy tắc preset",
        "preset_rules_button_preview_all": "Nghe thử tất cả",
        "preset_rules_button_run_all": "Chạy tất cả",
        "preset_rules_button_add_rule": "Thêm quy tắc",
        "preset_rules_button_save_and_close": "Lưu và đóng",

        # Voice selection
        "voice_filters_group_title": "Bộ lọc giọng đọc",
        "voice_label_language": "Ngôn ngữ",
        "voice_label_locale": "Giọng (vùng)",
        "voice_label_service": "Dịch vụ",
        "voice_label_gender": "Giới tính",
        "voice_button_reset_filters": "Đặt lại bộ lọc",
        "voice_group_voice": "Giọng đọc",
        "voice_button_play_sample": "Nghe mẫu",
        "voice_button_play_sample_wait": "Chọn thẻ để nghe mẫu",
        "voice_group_selection_mode": "Chế độ chọn giọng",
        "voice_radio_single": "Một giọng: dùng cùng một giọng cho mọi thẻ.",
        "voice_radio_random": "Ngẫu nhiên: chọn ngẫu nhiên từ danh sách giọng.",
        "voice_radio_priority": "Ưu tiên: thử giọng 1, lỗi thì chuyển giọng 2, v.v.",
        "voice_group_voice_list": "Danh sách giọng đã chọn",
        "voice_button_add_voice": "Thêm giọng",
        "voice_button_remove_voice": "Xóa",
        "voice_button_move_up": "Lên",
        "voice_button_move_down": "Xuống",

        # Services configuration
        "services_header_title": "Dịch vụ TTS",
        "services_header_description": "Chọn các dịch vụ đọc văn bản thành giọng nói miễn phí bạn muốn dùng. Có thể bật nhiều dịch vụ cùng lúc.",
        "services_button_enable_all_free": "Bật tất cả dịch vụ miễn phí",
        "services_button_disable_all": "Tắt tất cả dịch vụ",
        "config_toc_title": "Cấu hình",
        "config_toc_services": "Dịch vụ",
        "config_toc_about": "Thông tin",
        "config_search_placeholder": "Tìm dịch vụ…",

        # Service fee / type descriptions
        "service_fee_free": "Miễn phí",
        "service_fee_paid": "Trả phí",
        "service_type_dictionary_description": "Từ điển, chứa các bản ghi âm từ vựng.",
        "service_type_tts_description": "Text To Speech, có thể đọc trọn câu/văn bản.",
        
        # Specific service descriptions
        "service_description_GoogleTranslate": "Sử dụng API miễn phí của Google Translate. Hỗ trợ đa ngôn ngữ. (Online)",
        "service_description_EdgeTTS": "Giọng đọc AI tự nhiên, chất lượng cao từ Microsoft Edge. (Online)",
        "service_description_Windows": "Giọng đọc có sẵn trên Windows (SAPI 5). Nhanh và hoạt động offline.",
        "service_description_MacOS": "Giọng đọc có sẵn trên MacOS. Chất lượng cao và hoạt động offline.",
        "service_description_ESpeakNg": "Trình tổng hợp mã nguồn mở. Giọng hơi máy nhưng rất nhanh và hỗ trợ nhiều ngôn ngữ. (Offline)",

        # Tabs (batch dialog)
        "tab_source": "Nguồn",
        "tab_target": "Trường nhận âm thanh",
        "tab_voice_selection": "Chọn giọng",
        "tab_text_processing": "Xử lý text",

        # Batch dialog extra buttons
        "batch_button_show_settings": "Hiện cài đặt",
        "batch_button_hide_settings": "Ẩn cài đặt",

        # Preferences - language
        "preferences_group_language_title": "Language / Ngôn ngữ",
        "preferences_label_interface_language": "Interface Language / Ngôn ngữ giao diện",
        "preferences_option_language_en": "English",
        "preferences_option_language_vi": "Tiếng Việt",
        "preferences_language_tooltip": "Chọn ngôn ngữ cho nút bấm và hộp thoại của Super Free TTS.",

        # Choose Easy/Advanced dialog
        "choose_mode_title": "Bạn muốn thêm âm thanh theo cách nào?",
        "choose_mode_subtitle": "Chọn chế độ phù hợp. Bạn có thể đổi lại sau.",
        "choose_mode_easy_title": "Chế độ Dễ",
        "choose_mode_easy_desc": "Giao diện đơn giản để thêm âm thanh. Chỉ cần chọn trường và giọng đọc. Tương tự AwesomeTTS.",
        "choose_mode_advanced_title": "Chế độ Nâng cao",
        "choose_mode_advanced_desc": "Giao diện đầy đủ với preset, xử lý hàng loạt và quy tắc ánh xạ. Kiểm soát hoàn toàn.",
        "choose_mode_footer": "Bạn có thể đổi lại sau ở thanh nút trên trình soạn thẻ (Cấu hình quy tắc preset).",

        # Service badges
        "service_badge_recommended": "Gợi ý",
        "service_badge_free": "Miễn phí",
        "service_badge_enabled": "Đã bật",

        # Category labels (no emoji)
        "config_category_tts": "Dịch vụ TTS",
        "config_category_dictionary": "Dịch vụ Từ điển",
        "about_header_title": "Thông tin SuperFreeTTS",
        "about_contributor": "Người đóng góp danh dự",
        "about_author": "Tác giả",
        "about_version": "Phiên bản",
        "about_website": "Trang web",
        "about_facebook": "Facebook",
        "about_description": "SuperFreeTTS là một addon chuyển văn bản thành giọng nói hoàn toàn miễn phí cho Anki, được thiết kế để giúp việc học ngôn ngữ trở nên dễ dàng và hiệu quả hơn.",
    },
}


def _normalize_language(lang: str) -> str:
    """
    Chuẩn hóa mã ngôn ngữ. Nếu không hỗ trợ thì fallback về 'en'.
    """
    if lang not in SUPPORTED_LANGUAGES:
        return "en"
    return lang


def get_text(key: str, lang: str) -> str:
    """
    Lấy chuỗi giao diện theo key và ngôn ngữ.
    - Nếu lang không hợp lệ: dùng 'en'.
    - Nếu thiếu key trong lang hiện tại: fallback về 'en'.
    - Nếu vẫn thiếu: trả lại chính key (giúp debug).
    """
    lang = _normalize_language(lang)
    lang_dict = STRINGS.get(lang, STRINGS["en"])
    if key in lang_dict:
        return lang_dict[key]
    # fallback sang en nếu key không có trong lang hiện tại
    if key in STRINGS["en"]:
        return STRINGS["en"][key]
    # cuối cùng trả lại chính key
    return key

