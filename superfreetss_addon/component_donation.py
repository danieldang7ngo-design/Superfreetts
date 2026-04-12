import aqt.qt
import os
from . import component_common
from . import constants
from . import i18n
from . import logging_utils
from . import gui_utils

logger = logging_utils.get_child_logger(__name__)

class ResponsiveImageLabel(aqt.qt.QLabel):
    """A QLabel that maintains aspect ratio of its pixmap when resized."""
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.original_pixmap = pixmap
        self.setMinimumSize(250, 250) # Even larger min size
        self.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Expanding)
        self.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        if not self.original_pixmap.isNull():
            scaled = self.original_pixmap.scaled(
                self.size(), 
                aqt.qt.Qt.AspectRatioMode.KeepAspectRatio, 
                aqt.qt.Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled)
        super().resizeEvent(event)

class DonationComponent(component_common.ConfigComponentBase):
    def __init__(self, hypertts):
        self.hypertts = hypertts

    def get_model(self):
        return None

    def load_model(self, model):
        pass

    def draw(self, layout):
        lang = self.hypertts.get_ui_language()
        
        # Main container
        container = aqt.qt.QWidget()
        vlayout = aqt.qt.QVBoxLayout(container)
        vlayout.setContentsMargins(5, 5, 5, 5) # Minimal margins
        vlayout.setSpacing(0)

        # The new image donation_qr_v6.png is the latest Agribank VietQR.
        try:
            qr_path = gui_utils.get_graphics_path("donation_qr_v6.png")
            pixmap = aqt.qt.QPixmap(qr_path)
            self.resp_qr = ResponsiveImageLabel(pixmap)
            vlayout.addWidget(self.resp_qr, 1)
        except Exception as e:
            logger.error(f"Failed to load QR image: {e}")
            err_label = aqt.qt.QLabel("QR Image not found")
            err_label.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
            vlayout.addWidget(err_label)

        # Info labels
        info_layout = aqt.qt.QVBoxLayout()
        info_layout.setContentsMargins(10, 5, 10, 10)
        info_layout.setSpacing(5)

        def add_info_row(label_key, value):
            row = aqt.qt.QHBoxLayout()
            row.addStretch()
            lbl = aqt.qt.QLabel(f"<b>{i18n.get_text(label_key, lang)}:</b>")
            val = aqt.qt.QLabel(value)
            val.setTextInteractionFlags(aqt.qt.Qt.TextInteractionFlag.TextSelectableByMouse)
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            info_layout.addLayout(row)

        add_info_row("donation_bank", "Agribank")
        add_info_row("donation_account_number", "6460 2059 95890")
        add_info_row("donation_account_name", "NGO MINH DANG")

        vlayout.addLayout(info_layout)
        
        layout.addWidget(container)
