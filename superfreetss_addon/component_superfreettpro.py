import sys
import aqt.qt
import webbrowser

from . import component_common
from . import constants
from . import constants_events
from .constants_events import Event
from . import logging_utils
from . import gui_utils
from . import config_models
from . import stats
from . import version
logger = logging_utils.get_child_logger(__name__)

sc = stats.StatsContext(constants_events.EventContext.hyperttspro)

class HyperTTSPro(component_common.ConfigComponentBase):
    """Simplified About panel — replaces the old Pro/Trial/API Key UI."""

    def __init__(self, hypertts, model_change_callback):
        self.hypertts = hypertts
        self.model_change_callback = model_change_callback
        self.model = config_models.HyperTTSProAccountConfig()

    def get_model(self):
        return self.model

    def load_model(self, model: config_models.HyperTTSProAccountConfig):
        self.model = model

    def report_model_change(self):
        self.model_change_callback(self.get_model())

    def draw(self, global_vlayout):
        groupbox = aqt.qt.QGroupBox('About Super Free TTS')

        vlayout = aqt.qt.QVBoxLayout()

        # Version info
        ver = getattr(version, 'ANKI_SUPER_FREE_TTS_VERSION', 'unknown')
        version_label = aqt.qt.QLabel(f'<b>Super Free TTS</b> v{ver}')
        version_label.setStyleSheet(f'font-size: 14px; color: {constants.COLOR_ACCENT_TEAL};')
        vlayout.addWidget(version_label)

        # Description
        desc = aqt.qt.QLabel(
            'A free, open-source Text-to-Speech addon for Anki.\n'
            'Powered by EdgeTTS, gTTS, and other free TTS engines.\n\n'
            'All services are completely free — no API key required.'
        )
        desc.setWordWrap(True)
        desc.setStyleSheet('font-size: 12px; padding: 8px 0;')
        vlayout.addWidget(desc)

        # Links
        links_layout = aqt.qt.QHBoxLayout()

        github_btn = aqt.qt.QPushButton('⭐ GitHub')
        github_btn.setToolTip('Star us on GitHub!')
        gui_utils.configure_secondary_button(github_btn, min_height=30, min_width=100, font_size=10)
        github_btn.pressed.connect(lambda: webbrowser.open('https://github.com'))
        links_layout.addWidget(github_btn)

        rate_btn = aqt.qt.QPushButton('💬 Rate Addon')
        rate_btn.setToolTip('Rate this addon on AnkiWeb')
        gui_utils.configure_secondary_button(rate_btn, min_height=30, min_width=100, font_size=10)
        rate_btn.pressed.connect(lambda: webbrowser.open('https://ankiweb.net/shared/addons/'))
        links_layout.addWidget(rate_btn)

        links_layout.addStretch()
        vlayout.addLayout(links_layout)

        vlayout.addStretch()
        groupbox.setLayout(vlayout)
        global_vlayout.addWidget(groupbox)
