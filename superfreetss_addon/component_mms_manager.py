import os
import json
import urllib.request
import threading
from aqt import mw
from aqt.qt import *
from . import i18n
from . import component_kokoro_manager
from .component_kokoro_manager import PYTHON_EXE, KOKORO_ENGINE_DIR, DATA_DIR
from . import gui_utils
from .downloader import TurboDownloader

# MMS Models from Hugging Face (Sherpa-ONNX format by willwade)
MMS_BASE_URL = "https://huggingface.co/willwade/mms-tts-multilingual-models-onnx/resolve/main"

# Featured languages to show at the top
FEATURED_LANGS = ["vie", "eng", "kor", "jpn", "cmn", "swe", "yue", "fra", "deu", "spa"]

# Piper-VITS high quality models (converted for Sherpa-ONNX)
# Swedish: vits-piper-sv_SE-nst-medium
# Korean: vits-piper-ko_KR-kss-medium
PIPER_MODELS = {
    # Swedish and Korean disabled via Piper due to Sherpa-ONNX hang on some systems.
    # Falling back to stable MMS models.
}

class MmsInstallManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = mw.pm.meta.get("superfreetts_lang", "en")
        self.setWindowTitle(i18n.get_text("mms_manager_title", self.lang))
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.info_label = QLabel(i18n.get_text("mms_manager_info", self.lang))
        self.layout.addWidget(self.info_label)
        
        # Search and Filter (Horizontal Bar)
        filter_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(i18n.get_text("mms_manager_search_placeholder", self.lang))
        self.search_bar.textChanged.connect(self.filter_languages)
        filter_layout.addWidget(self.search_bar, 1)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(i18n.get_text("mms_manager_filter_all", self.lang), "all")
        self.lang_combo.addItem(i18n.get_text("mms_manager_filter_featured", self.lang), "featured")
        self.lang_combo.currentIndexChanged.connect(self.filter_languages)
        filter_layout.addWidget(self.lang_combo, 1)
        self.layout.addLayout(filter_layout)
        
        self.lang_list = QListWidget()
        self.lang_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.lang_list)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        self.status_label = QLabel(i18n.get_text("mms_manager_loading_languages", self.lang))
        self.layout.addWidget(self.status_label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(100)
        self.layout.addWidget(self.log_area)

        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton(i18n.get_text("mms_manager_button_install", self.lang))
        self.install_btn.clicked.connect(self.start_installation)
        gui_utils.configure_primary_button(self.install_btn)
        
        self.close_btn = QPushButton(i18n.get_text("button_close", self.lang))
        self.close_btn.clicked.connect(self.reject)
        
        self.open_log_btn = QPushButton(i18n.get_text("piper_manager_button_logs", self.lang)) # Reusing key
        self.open_log_btn.clicked.connect(self.open_log_folder)
        
        self.edit_lexicon_btn = QPushButton(i18n.get_text("mms_manager_button_edit_lexicon", self.lang))
        self.edit_lexicon_btn.clicked.connect(self.edit_lexicon)

        self.import_lexicon_btn = QPushButton(i18n.get_text("mms_manager_button_import_list", self.lang))
        self.import_lexicon_btn.clicked.connect(self.import_lexicon)

        self.auto_cmu_btn = QPushButton(i18n.get_text("mms_manager_button_autofix", self.lang))
        self.auto_cmu_btn.clicked.connect(self.auto_generate_cmu)
        
        self.uninstall_btn = QPushButton(i18n.get_text("mms_manager_button_uninstall", self.lang))
        self.uninstall_btn.clicked.connect(self.uninstall_selected)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.auto_cmu_btn)
        btn_layout.addWidget(self.import_lexicon_btn)
        btn_layout.addWidget(self.edit_lexicon_btn)
        btn_layout.addWidget(self.open_log_btn)
        btn_layout.addWidget(self.uninstall_btn)
        btn_layout.addWidget(self.install_btn)
        btn_layout.addWidget(self.close_btn)
        self.layout.addLayout(btn_layout)

        self.all_languages = []
        self.load_languages()

    def auto_generate_cmu(self):
        # Semi-automatic G2P using a web service or bundled logic
        selected_items = self.lang_list.selectedItems()
        if not selected_items or len(selected_items) > 1:
            QMessageBox.warning(self, i18n.get_text("generic_error", self.lang), i18n.get_text("mms_manager_error_select_one", self.lang))
            return

        iso = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if iso != 'eng':
             ret = QMessageBox.question(self, i18n.get_text("generic_warning", self.lang), i18n.get_text("mms_manager_confirm_autofix_non_eng", self.lang), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
             if ret == QMessageBox.StandardButton.No: return

        mms_dir = os.path.join(DATA_DIR, 'mms_models', iso)
        if not os.path.exists(os.path.join(mms_dir, "model.onnx")):
             QMessageBox.warning(self, i18n.get_text("generic_error", self.lang), i18n.get_text("mms_manager_error_not_installed", self.lang).format(iso))
             return

        # 1. Ask user for word list
        file_path, _ = QFileDialog.getOpenFileName(self, i18n.get_text("mms_manager_dialog_select_wordlist", self.lang), "", "Text Files (*.txt);;All Files (*)")
        if not file_path: return
        
        # 2. Process
        try:
            words = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    w = line.strip().split()[0] if line.strip() else "" # Take first word
                    if w: words.append(w.lower())
            
            if not words: return

            # 3. Simple G2P logic (Heuristic or Online?)
            # Since online is flaky and deps are hard, let's use a very simple built-in CMU subset 
            # OR ask the user if they want to download the full 5MB CMU dict.
            
            # Let's try downloading the standard CMU dict if not present
            cmu_path = os.path.join(DATA_DIR, 'cmudict-0.7b')
            if not os.path.exists(cmu_path):
                 ret = QMessageBox.question(self, i18n.get_text("mms_manager_dialog_download_cmu_title", self.lang), i18n.get_text("mms_manager_dialog_download_cmu_msg", self.lang), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                 if ret == QMessageBox.StandardButton.No: return
                 
                 self.log(i18n.get_text("mms_manager_log_downloading_cmu", self.lang))
                 url = "https://raw.githubusercontent.com/Alexir/CMUdict/master/cmudict-0.7b"
                 try:
                     debug_mode = False
                     if hasattr(mw, 'hyper_tts'):
                         debug_mode = mw.hyper_tts.get_preferences().error_handling.debug_mode
                     
                     downloader = TurboDownloader(url, cmu_path, debug_mode=debug_mode)
                     downloader.start()
                     self.log(i18n.get_text("mms_manager_log_cmu_downloaded", self.lang))
                 except Exception as e:
                     QMessageBox.critical(self, i18n.get_text("generic_error", self.lang), f"{i18n.get_text('mms_manager_error_download_cmu', self.lang)}: {e}")
                     return

            # 4. Load CMU
            self.update_status(i18n.get_text("mms_manager_status_loading_cmu", self.lang))
            cmu_dict = {}
            # CMU mapping to MMS (approximate)
            # Arpabet -> MMS Characters
            # This is key. "CHEMIST" -> K EH1 M AH0 S T -> k e m a s t?
            # MMS Eng seems to use: a, b/v, d, e, f, g, h, i, j/dZ, k, l, m, n, o, p, r, s, t, u, w, z
            # Vowels are tricky.
            # Heuristic map:
            # AA -> a, AE -> a, AH -> u, AO -> o, AW -> a u, AY -> a i, B -> b, CH -> t s, D -> d, DH -> d, etc.
            
            ARPABET_MAP = {
                'AA': 'a', 'AE': 'a', 'AH': 'u', 'AO': 'o', 'AW': 'a u', 'AY': 'a i',
                'B': 'b', 'CH': 't s', 'D': 'd', 'DH': 'd', 'EH': 'e', 'ER': 'r',
                'EY': 'e i', 'F': 'f', 'G': 'g', 'HH': 'h', 'IH': 'i', 'IY': 'i',
                'JH': 'd z', 'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'n g',
                'OW': 'o', 'OY': 'o i', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 's',
                'T': 't', 'TH': 't', 'UH': 'u', 'UW': 'u', 'V': 'v', 'W': 'w',
                'Y': 'j', 'Z': 'z', 'ZH': 'z'
            }

            with open(cmu_path, 'r', encoding='ISO-8859-1') as f:
                for line in f:
                    if line.startswith(';;;'): continue
                    parts = line.strip().split('  ')
                    if len(parts) == 2:
                        word_cmu = parts[0].lower()
                        phones_cmu = parts[1].split()
                        # Clean numbers from stress (EH1 -> EH)
                        phones_clean = [p[:2] for p in phones_cmu]
                        cmu_dict[word_cmu] = phones_clean

            # 5. Generate Lexicon
            generated_entries = []
            count = 0
            for w in words:
                # Remove punctuation
                w_clean = ''.join(c for c in w if c.isalnum() or c in "-'")
                if w_clean in cmu_dict:
                     phones = cmu_dict[w_clean]
                     mms_phones = []
                     for p in phones:
                         mms_char = ARPABET_MAP.get(p, '')
                         if mms_char: mms_phones.append(mms_char)
                     
                     if mms_phones:
                         generated_entries.append(f"{w} {' '.join(mms_phones)}")
                         count += 1
            
            if not generated_entries:
                 QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("mms_manager_no_words_found", self.lang))
                 return

            # 6. Append to Lexicon
            lexicon_path = os.path.join(mms_dir, "lexicon.txt")
            with open(lexicon_path, 'a', encoding='utf-8') as f:
                 f.write("\n# Auto-Generated from CMU Dict\n")
                 for entry in generated_entries:
                     f.write(entry + "\n")
            
            QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("mms_manager_autofix_success", self.lang).format(count))

        except Exception as e:
            QMessageBox.critical(self, i18n.get_text("generic_error", self.lang), str(e))
            self.log(str(e))

    def import_lexicon(self):
        selected_items = self.lang_list.selectedItems()
        if not selected_items or len(selected_items) > 1:
            QMessageBox.warning(self, i18n.get_text("generic_error", self.lang), i18n.get_text("mms_manager_error_select_one", self.lang))
            return

        iso = selected_items[0].data(Qt.ItemDataRole.UserRole)
        mms_dir = os.path.join(DATA_DIR, 'mms_models', iso)
        
        if not os.path.exists(os.path.join(mms_dir, "model.onnx")):
             QMessageBox.warning(self, i18n.get_text("generic_error", self.lang), i18n.get_text("mms_manager_error_not_installed", self.lang).format(iso))
             return
             
        file_path, _ = QFileDialog.getOpenFileName(self, i18n.get_text("mms_manager_dialog_select_lexicon_file", self.lang), "", "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)")
        if not file_path:
            return

        try:
            entries = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    # Support tab or space separation, but handle potential issues
                    # Format: word pronunciation...
                    # If CSV, maybe comma separated? Let's assume space/tab for now as per Sherpa standard.
                    if ',' in line and not '\t' in line:
                         parts = line.split(',', 1) # simple csv: word, pronunciation
                    else:
                         parts = line.split(None, 1)
                    
                    if len(parts) >= 2:
                        word = parts[0].strip()
                        phones = parts[1].strip()
                        # Clean phones to be space separated chars if they are concatenated? 
                        # No, assume user provides correct format or we might break it.
                        # But for MMS, phones usually are space-separated chars.
                        # Let's just trust the user input for now but normalize spaces.
                        phones = ' '.join(phones.split()) 
                        entries.append(f"{word} {phones}")
            
            if not entries:
                QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("mms_manager_info_no_valid_entries", self.lang))
                return
                
            lexicon_path = os.path.join(mms_dir, "lexicon.txt")
            mode = "a" if os.path.exists(lexicon_path) else "w"
            
            # Read existing to avoid full duplicates? 
            # Ideally we might want to update existing keys. 
            # But appending usually overrides in some parsers, or causes duplicates. 
            # Sherpa usually takes the first or last? Let's assume append is risky.
            # Safe approach: Read all, update dict, write back.
            
            existing_dict = {}
            if os.path.exists(lexicon_path):
                with open(lexicon_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(None, 1)
                        if len(parts) >= 2:
                            existing_dict[parts[0]] = parts[1]
            
            # Update dict
            for entry in entries:
                w, p = entry.split(None, 1)
                existing_dict[w] = p
                
            # Write back sorted
            with open(lexicon_path, 'w', encoding='utf-8') as f:
                f.write("# Format: word token1 token2 ...\n")
                for w in sorted(existing_dict.keys()):
                    f.write(f"{w} {existing_dict[w]}\n")
            
            QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("mms_manager_import_success", self.lang).format(len(entries)))

        except Exception as e:
            QMessageBox.critical(self, i18n.get_text("mms_manager_error_import_title", self.lang), str(e))

    def edit_lexicon(self):
        selected_items = self.lang_list.selectedItems()
        if not selected_items or len(selected_items) > 1:
            QMessageBox.warning(self, i18n.get_text("generic_error", self.lang), i18n.get_text("mms_manager_error_select_one_edit", self.lang))
            return

        iso = selected_items[0].data(Qt.ItemDataRole.UserRole)
        mms_dir = os.path.join(DATA_DIR, 'mms_models', iso)
        
        if not os.path.exists(os.path.join(mms_dir, "model.onnx")):
             QMessageBox.warning(self, "Not Installed", f"The model for {iso} is not installed yet.")
             return
             
        lexicon_path = os.path.join(mms_dir, "lexicon.txt")
        if not os.path.exists(lexicon_path):
            try:
                with open(lexicon_path, "w", encoding="utf-8") as f:
                    f.write("# Format: word token1 token2 ...\n")
                    f.write("# Example: chemist k e m i s t\n")
            except Exception as e:
                QMessageBox.critical(self, i18n.get_text("generic_error", self.lang), f"{i18n.get_text('mms_manager_error_create_lexicon', self.lang)}: {e}")
                return
        
        os.startfile(lexicon_path)

    def open_log_folder(self):
        log_dir = os.path.join(os.environ.get('APPDATA'), 'Anki2', 'addons21', 'Superfreetts', 'user_files')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        os.startfile(log_dir)

    def load_languages(self):
        json_path = os.path.join(os.path.dirname(__file__), 'mms_languages.json')
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.all_languages = json.load(f)
                
                # Sort all languages so that Featured ones come first, then alphabetical
                # This helps the search/filter logic present them nicely
                
                def get_sort_key(lang):
                    iso = lang.get("Iso Code", "")
                    name = lang.get("Language Name", "")
                    if iso in FEATURED_LANGS:
                        return (0, FEATURED_LANGS.index(iso))
                    return (1, name)
                
                self.all_languages.sort(key=get_sort_key)

                # Populate language combo with unique base names
                unique_langs = sorted(list(set(l.get("Language Name", "Unknown") for l in self.all_languages)))
                
                self.lang_combo.blockSignals(True)
                for l_name in unique_langs:
                    self.lang_combo.addItem(l_name, l_name)
                self.lang_combo.blockSignals(False)
                
                self.status_label.setText(i18n.get_text("mms_manager_available_entries", self.lang).format(len(self.all_languages)))
                self.filter_languages()
            except Exception as e:
                self.log(f"{i18n.get_text('mms_manager_error_load_lang_list', self.lang)}: {e}")
        else:
            self.log(i18n.get_text("mms_manager_error_json_not_found", self.lang))

    def filter_languages(self):
        query = self.search_bar.text().lower()
        selected_lang_filter = self.lang_combo.currentData()
        self.lang_list.clear()
        
        for lang in self.all_languages:
            name = lang.get("Language Name", "")
            iso = lang.get("Iso Code", "")
            country = lang.get("Country", "")
            
            match_query = (query in name.lower() or query in iso.lower() or query in country.lower())
            
            match_combo = True
            if selected_lang_filter == "all":
                match_combo = True
            elif selected_lang_filter == "featured":
                match_combo = (iso in FEATURED_LANGS)
            else:
                match_combo = (name == selected_lang_filter)
            
            is_available = lang.get("ONNX Exists", True)
            
            if match_query and match_combo:
                # SKIP if the model is explicitly marked as "Not available" 
                # AND it's not a special high-quality PIPER_MODELS override (which we'll restore later)
                if not is_available and iso not in PIPER_MODELS:
                    continue
                    
                display_text = f"{name} ({country}) [{iso}]"
                
                # Check if installed
                mms_model_path = os.path.join(DATA_DIR, 'mms_models', iso, "model.onnx")
                is_installed = os.path.exists(mms_model_path)

                if iso in FEATURED_LANGS:
                     display_text = f"⭐ {display_text}"

                if is_installed:
                    display_text = f"✅ {display_text} {i18n.get_text('piper_manager_installed_suffix', self.lang)}"

                item = QListWidgetItem(display_text)
                
                if is_installed:
                     item.setForeground(Qt.GlobalColor.gray)
                elif iso in FEATURED_LANGS:
                     item.setForeground(Qt.GlobalColor.blue) # Highlight featured

                item.setData(Qt.ItemDataRole.UserRole, iso)
                self.lang_list.addItem(item)

    def log(self, text):
        self.log_area.append(text)
        
    def update_status(self, text):
        self.status_label.setText(text)
        
    def update_progress(self, val):
        self.progress_bar.setValue(val)
        self.progress_bar.setVisible(True)

    def start_installation(self):
        selected_items = self.lang_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, i18n.get_text("generic_error", self.lang), i18n.get_text("mms_manager_error_no_selection", self.lang))
            return
            
        self.install_btn.setEnabled(False)
        self.search_bar.setEnabled(False)
        self.lang_combo.setEnabled(False)
        self.lang_list.setEnabled(False)
        
        langs_to_install = []
        for item in selected_items:
            iso = item.data(Qt.ItemDataRole.UserRole)
            name = item.text()
            langs_to_install.append((iso, name))
            
        mw.taskman.run_in_background(lambda: self.batch_install_task(langs_to_install), self.on_finished)

    def batch_install_task(self, langs):
        try:
            mw.taskman.run_on_main(lambda: self.update_status(i18n.get_text("mms_manager_status_checking_env", self.lang)))
            self._configure_python_pth()
            
            import subprocess
            check_cmd = [PYTHON_EXE, "-m", "pip", "show", "sherpa-onnx", "soundfile"]
            res = subprocess.run(check_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if "Name: sherpa-onnx" not in res.stdout:
                mw.taskman.run_on_main(lambda: self.log(i18n.get_text("mms_manager_log_installing_sherpa", self.lang)))
                install_cmd = [PYTHON_EXE, "-m", "pip", "install", "--upgrade", "--only-binary", ":all:", "sherpa-onnx", "soundfile"]
                subprocess.run(install_cmd, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

            total_langs = len(langs)
            for idx, (lang_code, lang_name) in enumerate(langs):
                mw.taskman.run_on_main(lambda n=lang_name, i=idx, t=total_langs: self.update_status(i18n.get_text("mms_manager_status_installing_n", self.lang).format(n, i+1, t)))
                
                mms_dir = os.path.join(DATA_DIR, 'mms_models', lang_code)
                os.makedirs(mms_dir, exist_ok=True)
                
                # Check for High Quality Piper Model
                piper_info = PIPER_MODELS.get(lang_code)
                if piper_info:
                    self.log(i18n.get_text("mms_manager_log_piper_detected", self.lang).format(lang_code))
                    files_to_download = piper_info["files"]
                    base_url = piper_info["base"]
                else:
                    files_to_download = ["model.onnx", "tokens.txt"]
                    base_url = f"{MMS_BASE_URL}/{lang_code}"
                
                for f_idx, filename in enumerate(files_to_download):
                    # We always save the main model as model.onnx for compatibility
                    local_filename = filename
                    if filename.endswith(".onnx"):
                        local_filename = "model.onnx"
                    
                    dest = os.path.join(mms_dir, local_filename)
                    url = f"{base_url}/{filename}"
                    
                    if not os.path.exists(dest):
                        mw.taskman.run_on_main(lambda f=filename: self.log(i18n.get_text("mms_manager_log_downloading_file", self.lang).format(lang_code, f)))
                        try:
                            debug_mode = False
                            if hasattr(mw, 'hyper_tts'):
                                debug_mode = mw.hyper_tts.get_preferences().error_handling.debug_mode
                            
                            def on_progress(data):
                                percent = data['percent']
                                speed_mb = data['speed_mb']
                                mw.taskman.run_on_main(lambda: self.update_status(f"Downloading {filename} ({percent}% - {speed_mb:.1f} MB/s)"))
                            
                            downloader = TurboDownloader(url, dest, progress_callback=on_progress, debug_mode=debug_mode)
                            downloader.start()
                        except Exception as dl_err:
                            mw.taskman.run_on_main(lambda err=dl_err, u=url: self.log(f"Failed to download {u}: {err}"))
                            # If it's a critical file and not a 404 on a non-existent folder
                            # We might want to continue batch or fail. 
                            # For batch robustness, let's just log and continue the next language.
                            continue 
                    
                    total_progress = int((idx / total_langs) * 100 + ((f_idx + 1) / len(files_to_download)) * (100 / total_langs))
                    mw.taskman.run_on_main(lambda p=total_progress: self.update_progress(p))

                # If Piper, we might need to note it
                if piper_info:
                    with open(os.path.join(mms_dir, "is_piper.txt"), "w") as f:
                        f.write("high_quality_piper_vits")
                    
                    # Special for Korean Piper (generate tokens.txt from json)
                    if lang_code == "kor":
                        json_path = os.path.join(mms_dir, "piper-kss-korean.onnx.json")
                        tokens_path = os.path.join(mms_dir, "tokens.txt")
                        if os.path.exists(json_path):
                            try:
                                with open(json_path, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                id_map = data.get("phoneme_id_map", {})
                                if id_map:
                                    with open(tokens_path, "w", encoding="utf-8") as f:
                                        for symbol, ids in id_map.items():
                                            if ids:
                                                f.write(f"{symbol} {ids[0]}\n")
                                    mw.taskman.run_on_main(lambda: self.log(i18n.get_text("mms_manager_log_generated_tokens", self.lang)))
                            except Exception as e:
                                mw.taskman.run_on_main(lambda err=e: self.log(f"{i18n.get_text('mms_manager_error_generate_tokens', self.lang)}: {err}"))

                # Special fix for English pronunciation (MMS is character-based)
                if lang_code == "eng":
                    lexicon_path = os.path.join(mms_dir, "lexicon.txt")
                    if not os.path.exists(lexicon_path):
                        try:
                            with open(lexicon_path, "w", encoding="utf-8") as f:
                                # Fix "chemist" -> "k e m i s t" (hardcoded respelling)
                                f.write("chemist k e m i s t\n")
                                f.write("schedule s k e d j u l\n")
                            mw.taskman.run_on_main(lambda: self.log(i18n.get_text("mms_manager_log_applied_chemist_fix", self.lang)))
                        except Exception as lex_err:
                            mw.taskman.run_on_main(lambda err=lex_err: self.log(f"{i18n.get_text('mms_manager_error_write_lexicon', self.lang)}: {err}"))

            mw.taskman.run_on_main(lambda: self.update_status(i18n.get_text("mms_manager_status_batch_complete", self.lang)))
            mw.taskman.run_on_main(lambda: self.update_progress(100))
            return True
        except Exception as e:
            mw.taskman.run_on_main(lambda err=e: self.log(f"Error: {err}"))
            return False

    def _configure_python_pth(self):
        pth_files = [f for f in os.listdir(KOKORO_ENGINE_DIR) if f.endswith('._pth')]
        if pth_files:
            pth_path = os.path.join(KOKORO_ENGINE_DIR, pth_files[0])
            try:
                with open(pth_path, 'r') as f:
                    content = f.read()
                if '#import site' in content:
                    content = content.replace('#import site', 'import site')
                    with open(pth_path, 'w') as f:
                        f.write(content)
            except: pass

    def uninstall_selected(self):
        selected_items = self.lang_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, i18n.get_text("generic_error", self.lang), i18n.get_text("mms_manager_error_uninstall_no_selection", self.lang))
            return

        ret = QMessageBox.question(self, i18n.get_text("mms_manager_confirm_uninstall_title", self.lang), 
                                 i18n.get_text("mms_manager_confirm_uninstall_msg", self.lang).format(len(selected_items)),
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.No:
            return

        import shutil
        success_count = 0
        for item in selected_items:
            iso = item.data(Qt.ItemDataRole.UserRole)
            mms_dir = os.path.join(DATA_DIR, 'mms_models', iso)
            if os.path.exists(mms_dir):
                try:
                    shutil.rmtree(mms_dir)
                    success_count += 1
                except Exception as e:
                    self.log(f"Failed to uninstall {iso}: {e}")

        if success_count > 0:
            QMessageBox.information(self, i18n.get_text("mms_manager_uninstall_complete_title", self.lang), i18n.get_text("mms_manager_uninstall_complete_msg", self.lang).format(success_count))
            # Refresh local UI list
            self.filter_languages()
            
            # Note: We used to try refreshing the whole addon UI here, 
            # but it was prone to errors. Anki will pick up changes on next use.
            self.log(f"Uninstalled {success_count} models. Refresh complete.")

    def on_finished(self, success):
        self.install_btn.setEnabled(True)
        self.search_bar.setEnabled(True)
        self.lang_combo.setEnabled(True)
        self.lang_list.setEnabled(True)
        
        if success:
            QMessageBox.information(self, i18n.get_text("generic_success", self.lang), i18n.get_text("mms_manager_install_success_msg", self.lang))
        else:
            QMessageBox.critical(self, i18n.get_text("generic_error", self.lang), i18n.get_text("mms_manager_install_failed_msg", self.lang))
        
        self.filter_languages()

def show_mms_install_dialog(parent=None):
    dialog = MmsInstallManager(parent)
    dialog.exec()
