"""
component_usage.py — Usage dashboard page (read-only) for Super Free TTS.

Shows local-only statistics about what the user has created with the addon:
  - summary hero card (files, notes, chars, realtime plays, money saved, time)
  - engine breakdown
  - monthly activity (only months with usage)
  - recent session history

No reset button, no telemetry — everything stays on the local machine.
"""

import aqt.qt

from . import component_common
from . import constants
from . import gui_utils
from . import i18n
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


def _format_duration(seconds: float) -> str:
    seconds = max(0, seconds)
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    rem_seconds = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m{rem_seconds:02d}s"
    hours = minutes // 60
    rem_minutes = minutes % 60
    return f"{hours}h{rem_minutes:02d}m"


def _format_number(value: int) -> str:
    return f"{value:,}"


class UsagePage(component_common.ConfigComponentBase):
    def __init__(self, hypertts):
        self.hypertts = hypertts

    def get_model(self):
        return None

    def load_model(self, model):
        pass

    def draw(self, layout):
        lang = self.hypertts.get_ui_language()
        dark = gui_utils.is_night_mode()
        palette = self._get_palette(dark)

        container = aqt.qt.QWidget()
        container.setStyleSheet(f"QWidget {{ background: transparent; color: {palette['text_primary']}; }}")

        page_layout = aqt.qt.QVBoxLayout(container)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(18)

        scroll = aqt.qt.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(aqt.qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = aqt.qt.QWidget()
        content_layout = aqt.qt.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(18)

        try:
            summary = self.hypertts.get_usage_summary()
            recent_sessions = self.hypertts.get_usage_recent_sessions(limit=20)
            monthly = self.hypertts.get_usage_monthly_series()
        except Exception as e:
            logger.warning(f"[USAGE] failed to load usage stats: {e}")
            summary = {}
            recent_sessions = []
            monthly = []

        content_layout.addWidget(self._build_hero_card(lang, palette, summary))
        content_layout.addWidget(self._build_engine_section(lang, palette, summary.get("by_engine", {})))
        content_layout.addWidget(self._build_monthly_section(lang, palette, monthly))
        content_layout.addWidget(self._build_session_section(lang, palette, recent_sessions))
        content_layout.addWidget(self._build_footer(lang, palette))

        scroll.setWidget(content)
        page_layout.addWidget(scroll)
        layout.addWidget(container)

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _build_hero_card(self, lang, palette, summary):
        card = self._create_card()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {palette['hero_bg']};
                border: 1px solid {palette['hero_border']};
                border-radius: 22px;
            }}
            QLabel {{ background: transparent; border: none; }}
            """
        )

        card_layout = aqt.qt.QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        title = aqt.qt.QLabel(i18n.get_text("usage_header_title", lang))
        title_font = title.font()
        title_font.setPointSize(17)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setWordWrap(True)
        title.setStyleSheet(f"color: {palette['text_primary']};")
        card_layout.addWidget(title)

        desc = aqt.qt.QLabel(i18n.get_text("usage_header_description", lang))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {palette['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(desc)

        stats = [
            (i18n.get_text("usage_stat_files", lang), _format_number(summary.get("files_generated", 0))),
            (i18n.get_text("usage_stat_notes", lang), _format_number(summary.get("notes_updated", 0))),
            (i18n.get_text("usage_stat_chars", lang), _format_number(summary.get("chars_generated", 0))),
            (i18n.get_text("usage_stat_realtime", lang), _format_number(summary.get("realtime_plays", 0))),
        ]

        grid = aqt.qt.QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        for index, (label, value) in enumerate(stats):
            grid.addWidget(self._build_stat_card(palette, label, value), index // 2, index % 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        card_layout.addLayout(grid)

        highlight_layout = aqt.qt.QHBoxLayout()
        highlight_layout.setSpacing(12)

        money_saved = summary.get("money_saved_usd", 0.0)
        money_text = i18n.get_text("usage_money_saved", lang).format(f"${money_saved:,.2f}")
        highlight_layout.addWidget(self._build_highlight_card(palette, money_text, is_money=True), 1)

        gen_time = summary.get("generation_time_s", 0.0)
        time_text = i18n.get_text("usage_stat_time", lang).format(_format_duration(gen_time))
        highlight_layout.addWidget(self._build_highlight_card(palette, time_text, is_money=False), 1)

        card_layout.addLayout(highlight_layout)
        return card

    def _build_stat_card(self, palette, label, value):
        card = aqt.qt.QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {palette['card_bg']};
                border: 1px solid {palette['card_border']};
                border-radius: 14px;
            }}
            QLabel {{ background: transparent; border: none; }}
            """
        )
        layout = aqt.qt.QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        value_label = aqt.qt.QLabel(value)
        value_font = value_label.font()
        value_font.setPointSize(18)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {palette['text_primary']};")
        layout.addWidget(value_label)

        name_label = aqt.qt.QLabel(label)
        name_label.setWordWrap(True)
        name_label.setStyleSheet(f"color: {palette['text_muted']}; font-size: 11px;")
        layout.addWidget(name_label)
        return card

    def _build_highlight_card(self, palette, text, is_money):
        card = aqt.qt.QFrame()
        accent = constants.COLOR_ACCENT if not is_money else palette.get('badge_bg', '#059669')
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {accent};
                border: 1px solid {palette['card_border']};
                border-radius: 14px;
            }}
            QLabel {{ background: transparent; border: none; }}
            """
        )
        layout = aqt.qt.QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        value_label = aqt.qt.QLabel(text)
        value_font = value_label.font()
        value_font.setPointSize(14)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setWordWrap(True)
        value_label.setStyleSheet(f"color: {palette['text_primary']};")
        layout.addWidget(value_label)
        return card

    def _build_engine_section(self, lang, palette, by_engine):
        section = self._create_card()
        section.setStyleSheet(
            f"""
            QFrame {{
                background-color: {palette['card_bg']};
                border: 1px solid {palette['card_border']};
                border-radius: 18px;
            }}
            QLabel {{ background: transparent; border: none; }}
            """
        )
        layout = aqt.qt.QVBoxLayout(section)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = aqt.qt.QLabel(i18n.get_text("usage_engine_title", lang))
        title_font = title.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {palette['text_primary']};")
        layout.addWidget(title)

        if not by_engine:
            empty = aqt.qt.QLabel(i18n.get_text("usage_no_data", lang))
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {palette['text_muted']}; font-size: 12px;")
            layout.addWidget(empty)
            return section

        total = sum(by_engine.values()) or 1
        for engine, count in sorted(by_engine.items(), key=lambda kv: -kv[1]):
            row = aqt.qt.QHBoxLayout()
            row.setSpacing(10)

            name = aqt.qt.QLabel(engine)
            name.setStyleSheet(f"color: {palette['text_primary']}; font-size: 12px;")
            name.setMinimumWidth(120)
            row.addWidget(name)

            bar = aqt.qt.QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(count * 100 / total))
            bar.setTextVisible(False)
            bar.setFixedHeight(10)
            bar.setStyleSheet(
                f"""
                QProgressBar {{
                    background: {palette['bar_bg']};
                    border: none;
                    border-radius: 5px;
                }}
                QProgressBar::chunk {{
                    background: {constants.COLOR_ACCENT};
                    border-radius: 5px;
                }}
                """
            )
            row.addWidget(bar, 1)

            count_label = aqt.qt.QLabel(f"{count} ({count * 100 / total:.0f}%)")
            count_label.setStyleSheet(f"color: {palette['text_muted']}; font-size: 11px;")
            row.addWidget(count_label)

            layout.addLayout(row)

        return section

    def _build_monthly_section(self, lang, palette, monthly):
        section = self._create_card()
        section.setStyleSheet(
            f"""
            QFrame {{
                background-color: {palette['card_bg']};
                border: 1px solid {palette['card_border']};
                border-radius: 18px;
            }}
            QLabel {{ background: transparent; border: none; }}
            """
        )
        layout = aqt.qt.QVBoxLayout(section)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = aqt.qt.QLabel(i18n.get_text("usage_monthly_title", lang))
        title_font = title.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {palette['text_primary']};")
        layout.addWidget(title)

        if not monthly:
            empty = aqt.qt.QLabel(i18n.get_text("usage_no_data", lang))
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {palette['text_muted']}; font-size: 12px;")
            layout.addWidget(empty)
            return section

        max_files = max(m.get("files_generated", 0) for m in monthly) or 1
        for m in monthly:
            row = aqt.qt.QHBoxLayout()
            row.setSpacing(10)

            month_label = aqt.qt.QLabel(m["month"])
            month_label.setStyleSheet(f"color: {palette['text_primary']}; font-size: 12px;")
            month_label.setMinimumWidth(80)
            row.addWidget(month_label)

            bar = aqt.qt.QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(m.get("files_generated", 0) * 100 / max_files))
            bar.setTextVisible(False)
            bar.setFixedHeight(10)
            bar.setStyleSheet(
                f"""
                QProgressBar {{
                    background: {palette['bar_bg']};
                    border: none;
                    border-radius: 5px;
                }}
                QProgressBar::chunk {{
                    background: {constants.COLOR_ACCENT};
                    border-radius: 5px;
                }}
                """
            )
            row.addWidget(bar, 1)

            detail = aqt.qt.QLabel(
                i18n.get_text("usage_monthly_detail", lang).format(
                    m.get("files_generated", 0),
                    m.get("notes_updated", 0),
                    _format_number(m.get("chars_generated", 0)),
                )
            )
            detail.setStyleSheet(f"color: {palette['text_muted']}; font-size: 11px;")
            row.addWidget(detail)

            layout.addLayout(row)

        return section

    def _build_session_section(self, lang, palette, sessions):
        section = self._create_card()
        section.setStyleSheet(
            f"""
            QFrame {{
                background-color: {palette['card_bg']};
                border: 1px solid {palette['card_border']};
                border-radius: 18px;
            }}
            QLabel {{ background: transparent; border: none; }}
            """
        )
        layout = aqt.qt.QVBoxLayout(section)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title = aqt.qt.QLabel(i18n.get_text("usage_history_title", lang))
        title_font = title.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {palette['text_primary']};")
        layout.addWidget(title)

        if not sessions:
            empty = aqt.qt.QLabel(i18n.get_text("usage_no_data", lang))
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {palette['text_muted']}; font-size: 12px;")
            layout.addWidget(empty)
            return section

        kind_names = {
            "batch": i18n.get_text("usage_kind_batch", lang),
            "single": i18n.get_text("usage_kind_single", lang),
            "realtime": i18n.get_text("usage_kind_realtime", lang),
        }

        for s in sessions:
            kind = kind_names.get(s.get("kind", ""), s.get("kind", ""))
            date_str = s.get("date", "")
            label = s.get("label", "")
            files = s.get("files_generated", 0)
            notes = s.get("notes_updated", 0)
            realtime = s.get("realtime_plays", 0)
            chars = s.get("chars_generated", 0)
            duration = _format_duration(s.get("generation_time_s", 0.0))

            parts = [f"{date_str} · {kind}"]
            if label:
                parts.append(label)
            if files:
                parts.append(i18n.get_text("usage_session_files", lang).format(files))
            if notes:
                parts.append(i18n.get_text("usage_session_notes", lang).format(notes))
            if realtime:
                parts.append(i18n.get_text("usage_session_realtime", lang).format(realtime))
            if chars:
                parts.append(i18n.get_text("usage_session_chars", lang).format(_format_number(chars)))
            parts.append(i18n.get_text("usage_session_time", lang).format(duration))

            row = aqt.qt.QLabel(" — ".join(parts))
            row.setWordWrap(True)
            row.setStyleSheet(f"color: {palette['text_secondary']}; font-size: 12px;")
            layout.addWidget(row)

        return section

    def _build_footer(self, lang, palette):
        label = aqt.qt.QLabel(i18n.get_text("usage_footer", lang))
        label.setWordWrap(True)
        label.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {palette['text_muted']}; font-size: 11px;")
        return label

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _create_card(self):
        card = aqt.qt.QFrame()
        card.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)
        card.setAutoFillBackground(False)
        return card

    def _get_palette(self, dark):
        if dark:
            return {
                "hero_bg": "#0F172A",
                "hero_border": "#1E293B",
                "card_bg": "#111827",
                "card_border": "#334155",
                "text_primary": "#F8FAFC",
                "text_secondary": "#CBD5E1",
                "text_muted": "#94A3B8",
                "badge_bg": "#059669",
                "bar_bg": "#1E293B",
            }
        return {
            "hero_bg": "#F8FAFC",
            "hero_border": "#DCE7F2",
            "card_bg": "#FFFFFF",
            "card_border": "#E2E8F0",
            "text_primary": "#0F172A",
            "text_secondary": "#475569",
            "text_muted": "#64748B",
            "badge_bg": constants.COLOR_ACCENT_LIGHT,
            "bar_bg": "#E2E8F0",
        }


UsageComponent = UsagePage
