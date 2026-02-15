import os
import json
import logging
import shutil
from typing import List, Dict, Optional

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, showWarning, askUser

from . import gui_utils
from . import logging_utils
from . import utils_hf
from . import constants
from .component_mms_manager import DATA_DIR

logger = logging_utils.get_child_logger(__name__)

# Standard directory for all ONNX models
ONNX_MODELS_DIR = os.path.join(DATA_DIR, 'onnx_models')

class OnnxManagerComponent:
    """A component to be drawn inside the main configuration UI using HTML for display."""
    def __init__(self, parent_dialog):
        self.parent_dialog = parent_dialog
        self.repo_files = []
        self.selected_files = set()
        self.installed_models = []

    def draw(self, layout: QVBoxLayout):
        # Header Style for the whole section
        style = """
            QTextBrowser {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            a {
                color: #3498db;
                text-decoration: none;
                font-weight: bold;
            }
        """

        # --- PHẦN 1: QUẢN LÝ MODEL ĐÃ CÀI ---
        self.group_installed = QGroupBox("1. Các Model đã cài đặt")
        inst_layout = QVBoxLayout()
        self.group_installed.setLayout(inst_layout)
        
        self.installed_browser = QTextBrowser()
        self.installed_browser.setOpenExternalLinks(False)
        self.installed_browser.anchorClicked.connect(self.handle_installed_click)
        self.installed_browser.setStyleSheet(style)
        self.installed_browser.setMinimumHeight(150)
        inst_layout.addWidget(self.installed_browser)
        
        refresh_btn = QPushButton("Làm mới danh sách")
        refresh_btn.clicked.connect(self.refresh_installed_models)
        inst_layout.addWidget(refresh_btn)
        
        layout.addWidget(self.group_installed)

        # --- PHẦN 2: THÊM TỪ HUGGINGFACE ---
        self.group_hf = QGroupBox("2. Thêm Model mới từ HuggingFace")
        hf_layout = QVBoxLayout()
        self.group_hf.setLayout(hf_layout)
        
        hf_layout.addWidget(QLabel("Dán Repo ID vào đây (ví dụ: hexgrad/Kokoro-82M):"))
        
        input_h = QHBoxLayout()
        self.hf_input = QLineEdit()
        self.hf_input.setPlaceholderText("username/repo-name")
        input_h.addWidget(self.hf_input)
        
        self.check_btn = QPushButton("Kiểm tra Model")
        self.check_btn.clicked.connect(self.fetch_hf_repo)
        input_h.addWidget(self.check_btn)
        hf_layout.addLayout(input_h)
        
        # HTML Browser for file list
        self.hf_browser = QTextBrowser()
        self.hf_browser.setOpenExternalLinks(False)
        self.hf_browser.anchorClicked.connect(self.handle_hf_click)
        self.hf_browser.setStyleSheet(style)
        self.hf_browser.setMinimumHeight(250)
        self.hf_browser.setVisible(False)
        hf_layout.addWidget(self.hf_browser)
        
        self.import_btn = QPushButton("Bắt đầu tải về máy")
        self.import_btn.clicked.connect(self.start_hf_import)
        self.import_btn.setVisible(False)
        gui_utils.configure_primary_button(self.import_btn)
        hf_layout.addWidget(self.import_btn)
        
        layout.addWidget(self.group_hf)

        # Progress & Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Sẵn sàng.")
        self.status_label.setStyleSheet("color: #3498db; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Initial scan
        self.refresh_installed_models()

    def update_installed_html(self):
        html = "<html><body style='color:#ffffff;'>"
        if not self.installed_models:
            html += "<p style='color:#888;'>Chưa cài đặt model nào.</p>"
        else:
            html += "<table width='100%' cellpadding='5'>"
            for category, name, path in self.installed_models:
                html += f"""
                <tr>
                    <td><b>[{category.upper()}]</b> {name}</td>
                    <td align='right'><a href='delete:{path}' style='color:#e74c3c;'>[XÓA]</a></td>
                </tr>
                """
            html += "</table>"
        html += "</body></html>"
        self.installed_browser.setHtml(html)

    def refresh_installed_models(self):
        self.installed_models = []
        if not os.path.exists(ONNX_MODELS_DIR):
            os.makedirs(ONNX_MODELS_DIR, exist_ok=True)
            
        for category in os.listdir(ONNX_MODELS_DIR):
            cat_path = os.path.join(ONNX_MODELS_DIR, category)
            if not os.path.isdir(cat_path): continue
            for model_name in os.listdir(cat_path):
                model_path = os.path.join(cat_path, model_name)
                if os.path.isdir(model_path):
                    self.installed_models.append((category, model_name, model_path))
        
        self.update_installed_html()

    def handle_installed_click(self, url):
        link = url.toString()
        if link.startswith("delete:"):
            path = link.replace("delete:", "")
            if askUser(f"Ba muốn xóa model này phải không ạ?\n{path}"):
                try:
                    shutil.rmtree(path)
                    self.refresh_installed_models()
                except Exception as e:
                    showWarning(str(e))

    def fetch_hf_repo(self):
        repo_id = self.hf_input.text().strip()
        if not repo_id: return
        
        self.status_label.setText("Đang quét Repo... đợi con tí...")
        self.hf_browser.setVisible(True)
        self.hf_browser.setHtml("<p style='color:white;'>Đang tải danh sách file...</p>")
        
        def task():
            return utils_hf.get_hf_model_files(repo_id)
            
        def on_done(future):
            try:
                self.repo_files = future.result()
                if not self.repo_files:
                    self.hf_browser.setHtml("<p style='color:red;'>Không thấy Repo hoặc lỗi mạng ba ơi.</p>")
                    return
                
                # Auto-select important files
                self.selected_files = set()
                for f in self.repo_files:
                    if f.lower().endswith(('.onnx', '.txt', '.json', '.lexicon', '.yaml', '.yml')):
                        self.selected_files.add(f)
                
                self.update_hf_html()
                self.import_btn.setVisible(True)
                self.status_label.setText(f"Tìm thấy {len(self.repo_files)} file ạ!")
            except Exception as e:
                self.status_label.setText(f"Lỗi: {e}")
            
        mw.taskman.run_in_background(task, on_done)

    def update_hf_html(self):
        html = "<html><body style='color:#ffffff;'>"
        html += "<p>Hòa chọn các file quan trọng giúp ba rồi, ba thích thêm file nào thì bấm vào nha:</p>"
        html += "<table width='100%' cellpadding='3'>"
        for f in self.repo_files:
            is_selected = f in self.selected_files
            color = "#2ecc71" if is_selected else "#888"
            status = "<b>[TÍCH]</b>" if is_selected else "[  ]"
            html += f"""
            <tr>
                <td><a href='toggle:{f}' style='color:{color}; text-decoration:none;'>{status} {f}</a></td>
            </tr>
            """
        html += "</table>"
        html += "</body></html>"
        self.hf_browser.setHtml(html)

    def handle_hf_click(self, url):
        link = url.toString()
        if link.startswith("toggle:"):
            filename = link.replace("toggle:", "")
            if filename in self.selected_files:
                self.selected_files.remove(filename)
            else:
                self.selected_files.add(filename)
            self.update_hf_html()

    def start_hf_import(self):
        repo_id = self.hf_input.text().strip()
        files_to_download = list(self.selected_files)
        if not files_to_download:
            showWarning("Ba chưa chọn file nào để tải kìa.")
            return
            
        items = ["vits", "piper", "custom"]
        cat, ok = QInputDialog.getItem(self.parent_dialog, "Loại model", "Đây là model gì ạ?", items, 0, False)
        if not ok: return
        
        default_name = repo_id.split('/')[-1]
        name, ok = QInputDialog.getText(self.parent_dialog, "Tên Model", "Đặt tên cho model:", QLineEdit.EchoMode.Normal, default_name)
        if not ok: return
        
        dest_dir = os.path.join(ONNX_MODELS_DIR, cat, name)
        os.makedirs(dest_dir, exist_ok=True)
        
        self.progress_bar.setVisible(True)
        self.import_btn.setEnabled(False)
        
        def download_task():
            total = len(files_to_download)
            for idx, filename in enumerate(files_to_download):
                url = utils_hf.get_download_url(repo_id, filename)
                target = os.path.join(dest_dir, os.path.basename(filename))
                mw.taskman.run_on_main(lambda f=filename: self.status_label.setText(f"Đang tải: {f}"))
                def prog(d, t):
                    p = int((idx/total*100) + (d/t*100/total))
                    mw.taskman.run_on_main(lambda v=p: self.progress_bar.setValue(v))
                if not utils_hf.download_file(url, target, prog):
                    return False, f"Lỗi tải {filename}"
            
            # Create a simple metadata.json
            meta_path = os.path.join(dest_dir, 'metadata.json')
            try:
                with open(meta_path, 'w', encoding='utf-8') as f:
                    json.dump({"name": name, "category": cat, "repo": repo_id}, f, indent=4)
            except: pass
                
            return True, "Xong"

        def on_done(future):
            success, msg = future.result()
            self.import_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            if success:
                showInfo(f"Tuyệt vời! Đã tải xong model {name} rồi ạ.")
                self.refresh_installed_models()
                self.hf_browser.setVisible(False)
                self.import_btn.setVisible(False)
            else:
                showWarning(msg)
                
        mw.taskman.run_in_background(download_task, on_done)
