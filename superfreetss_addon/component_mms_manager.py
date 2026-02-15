import os
import json
import urllib.request
import threading
from aqt import mw
from aqt.qt import *
from . import component_kokoro_manager
from .component_kokoro_manager import PYTHON_EXE, KOKORO_ENGINE_DIR, DATA_DIR
from . import gui_utils

# MMS Models from Hugging Face (Sherpa-ONNX format by willwade)
MMS_BASE_URL = "https://huggingface.co/willwade/mms-tts-multilingual-models-onnx/resolve/main"

class MmsInstallManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MMS TTS Model Manager")
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.info_label = QLabel("MMS supports 1100+ languages. Select multiple for batch installation.")
        self.layout.addWidget(self.info_label)
        
        # Search and Filter (Horizontal Bar)
        filter_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by name, country or code...")
        self.search_bar.textChanged.connect(self.filter_languages)
        filter_layout.addWidget(self.search_bar, 1)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("All Languages", "all")
        self.lang_combo.currentIndexChanged.connect(self.filter_languages)
        filter_layout.addWidget(self.lang_combo, 1)
        self.layout.addLayout(filter_layout)
        
        self.lang_list = QListWidget()
        self.lang_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.lang_list)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Loading languages...")
        self.layout.addWidget(self.status_label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(100)
        self.layout.addWidget(self.log_area)

        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton("Install Selected")
        self.install_btn.clicked.connect(self.start_installation)
        gui_utils.configure_primary_button(self.install_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.install_btn)
        btn_layout.addWidget(self.close_btn)
        self.layout.addLayout(btn_layout)

        self.all_languages = []
        self.load_languages()

    def load_languages(self):
        json_path = os.path.join(os.path.dirname(__file__), 'mms_languages.json')
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.all_languages = json.load(f)
                
                # Populate language combo with unique base names
                # Some entries have names like "Witoto, Minika", we'll just take the full name for simplicity
                # or unique names if we want to be smarter. 
                # Let's take the first word or main name.
                unique_langs = sorted(list(set(l.get("Language Name", "Unknown") for l in self.all_languages)))
                
                self.lang_combo.blockSignals(True)
                for l_name in unique_langs:
                    self.lang_combo.addItem(l_name, l_name)
                self.lang_combo.blockSignals(False)
                
                self.status_label.setText(f"Available: {len(self.all_languages)} entries.")
                self.filter_languages()
            except Exception as e:
                self.log(f"Error loading language list: {e}")
        else:
            self.log("Error: mms_languages.json not found.")

    def filter_languages(self):
        query = self.search_bar.text().lower()
        selected_lang = self.lang_combo.currentData()
        self.lang_list.clear()
        
        for lang in self.all_languages:
            name = lang.get("Language Name", "")
            iso = lang.get("Iso Code", "")
            country = lang.get("Country", "")
            
            match_query = (query in name.lower() or query in iso.lower() or query in country.lower())
            match_combo = (selected_lang == "all" or name == selected_lang)
            
            if match_query and match_combo:
                display_text = f"{name} ({country}) [{iso}]"
                item = QListWidgetItem(display_text)
                
                # Check if installed
                mms_model_path = os.path.join(DATA_DIR, 'mms_models', iso, "model.onnx")
                if os.path.exists(mms_model_path):
                    item.setText(item.text() + " [Installed]")
                    item.setForeground(Qt.GlobalColor.gray)
                
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
            QMessageBox.warning(self, "No Selection", "Please select at least one language.")
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
            mw.taskman.run_on_main(lambda: self.update_status("Checking environment..."))
            self._configure_python_pth()
            
            import subprocess
            check_cmd = [PYTHON_EXE, "-m", "pip", "show", "sherpa-onnx", "soundfile"]
            res = subprocess.run(check_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if "Name: sherpa-onnx" not in res.stdout:
                mw.taskman.run_on_main(lambda: self.log("Installing sherpa-onnx..."))
                install_cmd = [PYTHON_EXE, "-m", "pip", "install", "--upgrade", "--only-binary", ":all:", "sherpa-onnx", "soundfile"]
                subprocess.run(install_cmd, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

            total_langs = len(langs)
            for idx, (lang_code, lang_name) in enumerate(langs):
                mw.taskman.run_on_main(lambda n=lang_name, i=idx, t=total_langs: self.update_status(f"Installing {n} ({i+1}/{t})..."))
                
                mms_dir = os.path.join(DATA_DIR, 'mms_models', lang_code)
                os.makedirs(mms_dir, exist_ok=True)
                
                files = ["model.onnx", "tokens.txt"]
                for f_idx, filename in enumerate(files):
                    dest = os.path.join(mms_dir, filename)
                    url = f"{MMS_BASE_URL}/{lang_code}/{filename}"
                    
                    if not os.path.exists(dest):
                        mw.taskman.run_on_main(lambda f=filename: self.log(f"Downloading {lang_code}/{f}..."))
                        urllib.request.urlretrieve(url, dest)
                    
                    lang_progress = (idx / total_langs) * 100
                    file_progress = ((f_idx + 1) / len(files)) * (100 / total_langs)
                    total_progress = int(lang_progress + file_progress)
                    mw.taskman.run_on_main(lambda p=total_progress: self.update_progress(p))

            mw.taskman.run_on_main(lambda: self.update_status("Batch Installation Complete!"))
            mw.taskman.run_on_main(lambda: self.update_progress(100))
            return True
        except Exception as e:
            mw.taskman.run_on_main(lambda: self.log(f"Error: {e}"))
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

    def on_finished(self, success):
        self.install_btn.setEnabled(True)
        self.search_bar.setEnabled(True)
        self.lang_combo.setEnabled(True)
        self.lang_list.setEnabled(True)
        if success:
            QMessageBox.information(self, "Success", "Selected MMS models installed!")
        else:
            QMessageBox.critical(self, "Error", "Installation failed. Check log.")
        self.filter_languages()

def show_mms_install_dialog(parent=None):
    dialog = MmsInstallManager(parent)
    dialog.exec()
