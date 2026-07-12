import os
import json
import logging
import shutil
from typing import List, Dict, Optional

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, showWarning, askUser

from . import i18n
from . import gui_utils
from . import logging_utils
from . import utils_hf
from . import constants

logger = logging_utils.get_child_logger(__name__)

def _get_onnx_models_dir():
    return os.path.join(constants.DATA_DIR, 'onnx_models')

class OnnxManagerComponent:
    """A component to be drawn inside the main configuration UI using HTML for display."""
    def __init__(self, parent_dialog):
        self.parent_dialog = parent_dialog
        self.lang = mw.pm.meta.get("superfreetts_lang", "en")
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
        self.group_installed = QGroupBox(i18n.get_text("onnx_manager_group_installed", self.lang))
        inst_layout = QVBoxLayout()
        self.group_installed.setLayout(inst_layout)
        
        self.installed_browser = QTextBrowser()
        self.installed_browser.setOpenExternalLinks(False)
        self.installed_browser.anchorClicked.connect(self.handle_installed_click)
        self.installed_browser.setStyleSheet(style)
        self.installed_browser.setMinimumHeight(150)
        inst_layout.addWidget(self.installed_browser)
        
        refresh_btn = QPushButton(i18n.get_text("onnx_manager_button_refresh", self.lang))
        refresh_btn.clicked.connect(self.refresh_installed_models)
        inst_layout.addWidget(refresh_btn)
        
        layout.addWidget(self.group_installed)

        # --- PHẦN 2: THÊM TỪ HUGGINGFACE ---
        self.group_hf = QGroupBox(i18n.get_text("onnx_manager_group_hf", self.lang))
        hf_layout = QVBoxLayout()
        self.group_hf.setLayout(hf_layout)
        
        hf_layout.addWidget(QLabel(i18n.get_text("onnx_manager_label_repo_id", self.lang)))
        
        input_h = QHBoxLayout()
        self.hf_input = QLineEdit()
        self.hf_input.setPlaceholderText(i18n.get_text("onnx_manager_placeholder_repo", self.lang))
        input_h.addWidget(self.hf_input)
        
        self.check_btn = QPushButton(i18n.get_text("onnx_manager_button_check", self.lang))
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
        
        self.import_btn = QPushButton(i18n.get_text("onnx_manager_button_import", self.lang))
        self.import_btn.clicked.connect(self.start_hf_import)
        self.import_btn.setVisible(False)
        gui_utils.configure_primary_button(self.import_btn)
        hf_layout.addWidget(self.import_btn)
        
        layout.addWidget(self.group_hf)

        # Progress & Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel(i18n.get_text("onnx_manager_status_ready", self.lang))
        self.status_label.setStyleSheet("color: #3498db; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Initial scan
        self.refresh_installed_models()

    def update_installed_html(self):
        html = "<html><body style='color:#ffffff;'>"
        if not self.installed_models:
            html += f"<p style='color:#888;'>{i18n.get_text('onnx_manager_no_installed', self.lang)}</p>"
        else:
            html += "<table width='100%' cellpadding='5'>"
            for category, name, path in self.installed_models:
                html += f"""
                <tr>
                    <td><b>[{category.upper()}]</b> {name}</td>
                    <td align='right'><a href='delete:{path}' style='color:#e74c3c;'>{i18n.get_text('onnx_manager_link_delete', self.lang)}</a></td>
                </tr>
                """
            html += "</table>"
        html += "</body></html>"
        self.installed_browser.setHtml(html)

    def refresh_installed_models(self):
        self.installed_models = []
        onnx_dir = _get_onnx_models_dir()
        if not os.path.exists(onnx_dir):
            os.makedirs(onnx_dir, exist_ok=True)
            
        for category in os.listdir(onnx_dir):
            cat_path = os.path.join(onnx_dir, category)
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
            if askUser(i18n.get_text("onnx_manager_confirm_delete", self.lang).format(path)):
                try:
                    shutil.rmtree(path)
                    self.refresh_installed_models()
                except Exception as e:
                    showWarning(str(e))

    def fetch_hf_repo(self):
        repo_id = self.hf_input.text().strip()
        if not repo_id: return
        
        self.status_label.setText(i18n.get_text("onnx_manager_status_scanning", self.lang))
        self.hf_browser.setVisible(True)
        self.hf_browser.setHtml(f"<p style='color:white;'>{i18n.get_text('onnx_manager_status_loading_files', self.lang)}</p>")
        
        def task():
            return utils_hf.get_hf_model_files(repo_id)
            
        def on_done(future):
            try:
                self.repo_files = future.result()
                if not self.repo_files:
                    self.hf_browser.setHtml(f"<p style='color:red;'>{i18n.get_text('onnx_manager_error_repo', self.lang)}</p>")
                    return
                
                # Auto-select important files
                self.selected_files = set()
                for f in self.repo_files:
                    if f.lower().endswith(('.onnx', '.txt', '.json', '.lexicon', '.yaml', '.yml')):
                        self.selected_files.add(f)
                
                self.update_hf_html()
                self.import_btn.setVisible(True)
                self.status_label.setText(i18n.get_text("onnx_manager_label_select_files", self.lang))
            except Exception as e:
                self.status_label.setText(f"{i18n.get_text('generic_error', self.lang)}: {e}")
            
        mw.taskman.run_in_background(task, on_done)

    def update_hf_html(self):
        html = "<html><body style='color:#ffffff;'>"
        html += f"<p>{i18n.get_text('onnx_manager_label_select_files', self.lang)}</p>"
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
            showWarning(i18n.get_text("onnx_manager_error_no_files", self.lang))
            return
            
        items = ["vits", "piper", "custom"]
        cat, ok = QInputDialog.getItem(self.parent_dialog, i18n.get_text("onnx_manager_input_type_title", self.lang), i18n.get_text("onnx_manager_input_type_label", self.lang), items, 0, False)
        if not ok: return
        
        default_name = repo_id.split('/')[-1]
        name, ok = QInputDialog.getText(self.parent_dialog, i18n.get_text("onnx_manager_input_name_title", self.lang), i18n.get_text("onnx_manager_input_name_label", self.lang), QLineEdit.EchoMode.Normal, default_name)
        if not ok: return
        
        dest_dir = os.path.join(_get_onnx_models_dir(), cat, name)
        os.makedirs(dest_dir, exist_ok=True)
        
        self.progress_bar.setVisible(True)
        self.import_btn.setEnabled(False)
        
        def download_task():
            total = len(files_to_download)
            for idx, filename in enumerate(files_to_download):
                url = utils_hf.get_download_url(repo_id, filename)
                target = os.path.join(dest_dir, os.path.basename(filename))
                mw.taskman.run_on_main(lambda f=filename: self.status_label.setText(i18n.get_text("onnx_manager_status_downloading", self.lang).format(f)))
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
            except Exception as e:
                logger.warning(f"Failed to write model meta: {e}")
                
            return True, "Xong"

        def on_done(future):
            success, msg = future.result()
            self.import_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            if success:
                showInfo(i18n.get_text("onnx_manager_success_msg", self.lang).format(name))
                self.refresh_installed_models()
                self.hf_browser.setVisible(False)
                self.import_btn.setVisible(False)
            else:
                showWarning(msg)
                
        mw.taskman.run_in_background(download_task, on_done)
