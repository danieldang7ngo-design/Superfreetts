import os
import requests
import threading
import json
import aqt
from aqt.qt import *
from dataclasses import dataclass
from typing import List, Optional, Dict

from . import logging_utils
from . import gui_utils

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
    def __init__(self, models: List[PiperModelInfo] = None, dest_dir: str = ""):
        super().__init__()
        self.models = models or []
        self.dest_dir = dest_dir
        self.signals = DownloadWorkerSignals()
        self.is_cancelled = False

    def fetch_voices(self):
        try:
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
                self.signals.error.emit(f"Failed to fetch voices.json: HTTP {response.status_code}")
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
                self.signals.progress.emit(int((idx / total_count) * 100), f"Installing {model.name} ({idx+1}/{total_count})...")
                
                self._download_file(model.url_onnx, model.key + ".onnx")
                if self.is_cancelled: return

                self._download_file(model.url_json, model.key + ".onnx.json")
                if self.is_cancelled: return
            
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))

    def _download_file(self, url, filename):
        filepath = os.path.join(self.dest_dir, filename)
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024
        wrote = 0
        
        with open(filepath, 'wb') as f:
            for data in response.iter_content(block_size):
                if self.is_cancelled: return
                wrote = wrote + len(data)
                f.write(data)
                # We optionally update status per file chunk if needed, but per-model is cleaner for batch

class PiperManagerDialog(QDialog):
    def __init__(self, parent, dest_dir):
        super().__init__(parent)
        self.dest_dir = dest_dir
        self.all_models: List[PiperModelInfo] = []
        
        self.setWindowTitle("Piper Model Manager")
        self.setMinimumWidth(600)
        self.setMinimumLength(600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Search and Filter
        filter_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search voices or languages...")
        self.search_bar.textChanged.connect(self.filter_models)
        filter_layout.addWidget(self.search_bar, 1)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("All Languages", "all")
        self.lang_combo.currentIndexChanged.connect(self.filter_models)
        filter_layout.addWidget(self.lang_combo, 1)
        self.layout.addLayout(filter_layout)
        
        self.model_list = QListWidget()
        self.model_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.model_list)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Loading voice list from Hugging Face...")
        self.layout.addWidget(self.status_label)
        
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("Install Selected")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.download_selected)
        gui_utils.configure_primary_button(self.download_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.close_btn)
        self.layout.addLayout(btn_layout)
        
        self.worker = None
        self.load_voices()

    def setMinimumLength(self, val): # Compatibility
        self.setMinimumHeight(val)

    def load_voices(self):
        self.worker = PiperDownloadWorker()
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
        
        self.status_label.setText(f"Available: {len(models)} voices.")
        self.download_btn.setEnabled(True)
        self.filter_models()

    def on_load_error(self, err):
        self.status_label.setText(f"Failed to load voices: {err}")
        aqt.utils.showWarning(f"Error loading Piper voices list: {err}")

    def filter_models(self):
        self.model_list.clear()
        selected_lang = self.lang_combo.currentData()
        query = self.search_bar.text().lower()
        
        for model in self.all_models:
            match_lang = (selected_lang == "all" or model.language_name == selected_lang)
            match_query = (query in model.name.lower() or query in model.language_name.lower())
            
            if match_lang and match_query:
                # Cleaner item display as requested
                display_text = f"{model.language_name} - {model.name} ({model.quality})"
                item = QListWidgetItem(display_text)
                
                if model_exists(self.dest_dir, model):
                    item.setText(item.text() + " [Installed]")
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
        
        self.worker = PiperDownloadWorker(models_to_download, self.dest_dir)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.download_finished)
        self.worker.signals.error.connect(self.download_error)
        
        threading.Thread(target=self.worker.run).start()

    def update_progress(self, percent, msg):
        self.progress_bar.setValue(percent)
        self.status_label.setText(msg)

    def download_finished(self):
        self.status_label.setText("Batch download complete!")
        self.progress_bar.setValue(100)
        self.download_btn.setEnabled(True)
        self.lang_combo.setEnabled(True)
        self.search_bar.setEnabled(True)
        self.model_list.setEnabled(True)
        aqt.utils.showInfo("Selected voices downloaded successfully!")
        self.filter_models()

    def download_error(self, err):
        self.status_label.setText(f"Error: {err}")
        self.download_btn.setEnabled(True)
        self.lang_combo.setEnabled(True)
        self.search_bar.setEnabled(True)
        self.model_list.setEnabled(True)
        aqt.utils.showWarning(f"Download failed: {err}")

def model_exists(dest_dir, model):
    onnx_path = os.path.join(dest_dir, model.key + ".onnx")
    return os.path.exists(onnx_path)

