import os
# import requests # lazy loaded
import threading
import json
import aqt
from aqt.qt import *
from dataclasses import dataclass
from typing import List, Optional, Dict

from . import i18n
from . import logging_utils
from . import gui_utils
from .downloader import TurboDownloader
from aqt import mw

logger = logging_utils.get_child_logger(__name__)

# Official voices.json URL
VOICES_JSON_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json"
HF_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

@dataclass
class PiperModelInfo:
    key: str
    name: str
    language_code: str
    language_name: str  # Full English name
    quality: str
    url_onnx: str
    url_json: str

class DownloadWorkerSignals(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    voices_loaded = pyqtSignal(list)

class PiperDownloadWorker(QObject):
    def __init__(self, models: List[PiperModelInfo] = None, dest_dir: str = "", lang: str = "en"):
        super().__init__()
        self.models = models or []
        self.dest_dir = dest_dir
        self.lang = lang
        self.signals = DownloadWorkerSignals()
        self.is_cancelled = False

    def fetch_voices(self):
        try:
            import requests
            response = requests.get(VOICES_JSON_URL)
            if response.status_code == 200:
                voices_data = response.json()
                models = []
                for voice_key, info in voices_data.items():
                    files = info.get('files', {})
                    onnx_rel_path = ""
                    for f_path in files.keys():
                        if f_path.endswith('.onnx'):
                            onnx_rel_path = f_path
                            break
                    
                    if not onnx_rel_path:
                        continue
                        
                    lang_info = info.get('language', {})
                    lang_name = lang_info.get('name_english', 'Unknown')
                    country = lang_info.get('country_english', '')
                    if country:
                        full_lang_name = f"{lang_name} ({country})"
                    else:
                        full_lang_name = lang_name

                    models.append(PiperModelInfo(
                        key=voice_key,
                        name=info.get('name', voice_key),
                        language_code=lang_info.get('code', 'unknown'),
                        language_name=full_lang_name,
                        quality=info.get('quality', 'medium'),
                        url_onnx=f"{HF_BASE_URL}/{onnx_rel_path}?download=true",
                        url_json=f"{HF_BASE_URL}/{onnx_rel_path}.json?download=true"
                    ))
                
                # Sort models: language name first, then voice name
                models.sort(key=lambda x: (x.language_name, x.name))
                self.signals.voices_loaded.emit(models)
            else:
                self.signals.error.emit(i18n.get_text("piper_manager_load_error", self.lang).format(response.status_code))
        except Exception as e:
            self.signals.error.emit(str(e))

    def run(self):
        if not self.models: return
        try:
            if not os.path.exists(self.dest_dir):
                os.makedirs(self.dest_dir)
            
            total_count = len(self.models)
            for idx, model in enumerate(self.models):
                if self.is_cancelled: break
                
                # Update progress for starting a new model
                self.signals.progress.emit(int((idx / total_count) * 100), i18n.get_text("piper_manager_installing_model", self.lang).format(model.name, idx+1, total_count))
                
                self._download_file(model.url_onnx, model.key + ".onnx")
                if self.is_cancelled: return

                self._download_file(model.url_json, model.key + ".onnx.json")
                if self.is_cancelled: return
            
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))

    def _download_file(self, url, filename):
        filepath = os.path.join(self.dest_dir, filename)
        
        debug_mode = False
        try:
            if hasattr(mw, 'hyper_tts'):
                debug_mode = mw.hyper_tts.get_preferences().error_handling.debug_mode
        except:
            pass

        def on_progress(data):
            percent = data['percent']
            speed_mb = data['speed_mb']
            # We emit an update signal to keep the UI responsive
            # Reusing the existing signal format if possible
            msg = i18n.get_text("piper_manager_installing_model", self.lang).format(filename, "?", "?")
            self.signals.progress.emit(percent, f"{msg} ({speed_mb:.1f} MB/s)")

        downloader = TurboDownloader(url, filepath, progress_callback=on_progress, debug_mode=debug_mode)
        downloader.start()

class PiperManagerDialog(QDialog):
    def __init__(self, parent, dest_dir):
        super().__init__(parent)
        self.dest_dir = dest_dir
        self.lang = mw.pm.meta.get("superfreetts_lang", "en")
        self.all_models: List[PiperModelInfo] = []
        
        self.setWindowTitle(i18n.get_text("piper_manager_title", self.lang))
        self.setMinimumWidth(600)
        self.setMinimumLength(600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Search and Filter
        filter_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(i18n.get_text("piper_manager_search_placeholder", self.lang))
        self.search_bar.textChanged.connect(self.filter_models)
        filter_layout.addWidget(self.search_bar, 1)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(i18n.get_text("piper_manager_filter_all", self.lang), "all")
        self.lang_combo.currentIndexChanged.connect(self.filter_models)
        filter_layout.addWidget(self.lang_combo, 1)
        self.layout.addLayout(filter_layout)
        
        self.model_list = QListWidget()
        self.model_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.model_list)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel(i18n.get_text("piper_manager_loading_voices", self.lang))
        self.layout.addWidget(self.status_label)
        
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton(i18n.get_text("piper_manager_button_install", self.lang))
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.download_selected)
        gui_utils.configure_primary_button(self.download_btn)
        
        self.close_btn = QPushButton(i18n.get_text("button_close", self.lang))
        self.close_btn.clicked.connect(self.reject)
        
        self.open_log_btn = QPushButton(i18n.get_text("piper_manager_button_logs", self.lang))
        self.open_log_btn.clicked.connect(self.open_log_folder)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.open_log_btn)
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.close_btn)
        self.layout.addLayout(btn_layout)
        
        self.worker = None
        self.load_voices()

    def setMinimumLength(self, val): # Compatibility
        self.setMinimumHeight(val)

    def open_log_folder(self):
        addon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        log_dir = os.path.join(addon_dir, 'user_files')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        os.startfile(log_dir)

    def load_voices(self):
        self.worker = PiperDownloadWorker(lang=self.lang)
        self.worker.signals.voices_loaded.connect(self.on_voices_loaded)
        self.worker.signals.error.connect(self.on_load_error)
        threading.Thread(target=self.worker.fetch_voices).start()

    def on_voices_loaded(self, models):
        self.all_models = models
        # Get unique language names for combo
        languages = sorted(list(set(m.language_name for m in models)))
        
        self.lang_combo.blockSignals(True)
        for lang in languages:
            self.lang_combo.addItem(lang, lang)
        
        # Try to find Vietnamese or English by name
        idx = self.lang_combo.findText("Vietnamese", Qt.MatchFlag.MatchContains)
        if idx == -1: idx = self.lang_combo.findText("English", Qt.MatchFlag.MatchContains)
        if idx != -1: self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.blockSignals(False)
        
        self.status_label.setText(i18n.get_text("piper_manager_available_voices", self.lang).format(len(models)))
        self.download_btn.setEnabled(True)
        self.filter_models()

    def on_load_error(self, err):
        self.status_label.setText(i18n.get_text("piper_manager_load_error", self.lang).format(err))
        aqt.utils.showWarning(f"{i18n.get_text('piper_manager_load_error', self.lang).format(err)}")

    def filter_models(self):
        self.model_list.clear()
        selected_lang = self.lang_combo.currentData()
        query = self.search_bar.text().lower()
        
        for model in self.all_models:
            match_lang = (selected_lang == "all" or model.language_name == selected_lang)
            match_query = (query in model.name.lower() or query in model.language_name.lower())
            
            if match_lang and match_query:
                # Cleaner item display as requested
                display_text = i18n.get_text("piper_manager_voice_item_format", self.lang).format(model.language_name, model.name, model.quality)
                item = QListWidgetItem(display_text)
                
                if model_exists(self.dest_dir, model):
                    item.setText(item.text() + i18n.get_text("piper_manager_installed_suffix", self.lang))
                    item.setForeground(Qt.GlobalColor.gray)
                
                item.setData(Qt.ItemDataRole.UserRole, model)
                self.model_list.addItem(item)

    def download_selected(self):
        selected_items = self.model_list.selectedItems()
        if not selected_items: return
            
        models_to_download = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        
        self.download_btn.setEnabled(False)
        self.lang_combo.setEnabled(False)
        self.search_bar.setEnabled(False)
        self.model_list.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = PiperDownloadWorker(models_to_download, self.dest_dir, lang=self.lang)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.download_finished)
        self.worker.signals.error.connect(self.download_error)
        
        threading.Thread(target=self.worker.run).start()

    def update_progress(self, percent, msg):
        self.progress_bar.setValue(percent)
        self.status_label.setText(msg)

    def download_finished(self):
        self.status_label.setText(i18n.get_text("piper_manager_download_complete", self.lang))
        self.progress_bar.setValue(100)
        self.download_btn.setEnabled(True)
        self.lang_combo.setEnabled(True)
        self.search_bar.setEnabled(True)
        self.model_list.setEnabled(True)
        aqt.utils.showInfo(i18n.get_text("piper_manager_download_success_msg", self.lang))
        self.filter_models()

    def download_error(self, err):
        self.status_label.setText(f"{i18n.get_text('generic_error', self.lang)}: {err}")
        self.download_btn.setEnabled(True)
        self.lang_combo.setEnabled(True)
        self.search_bar.setEnabled(True)
        self.model_list.setEnabled(True)
        aqt.utils.showWarning(i18n.get_text("piper_manager_download_failed_msg", self.lang).format(err))

def model_exists(dest_dir, model):
    onnx_path = os.path.join(dest_dir, model.key + ".onnx")
    return os.path.exists(onnx_path)

