"""
editor_manager.py — Anki Editor & Mapping Rules bridge for Super Free TTS.

Responsibility:
  - Extracting EditorContext (note, add_mode, selected text, clipboard) from
    an active Anki editor window.
  - Generating and immediately writing audio into a note from the editor.
  - Running preset Mapping Rules (preview or apply) against the current note
    in the background so the editor stays responsive.
  - Providing preview audio playback triggered directly from the editor.

NOT responsible for:
  - Batch/collection-wide operations (→ batch_orchestrator.py)
  - Single-note audio file generation (→ audio_generator.py)
  - Config/preset persistence (→ config_store.py)
  - Realtime TTS tag rendering (→ realtime_manager.py)
"""

import pprint
from typing import Any, Optional

import aqt
import aqt.addcards

from . import constants
from . import config_models
from . import errors
from . import context
from . import preset_rules_status
from . import i18n
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


class EditorManager:
    """
    Bridge between the Anki Editor and the audio generation pipeline.

    All UI interactions (editor.set_note, play_sound) are marshalled onto the
    Anki main thread via ``anki_utils.run_on_main`` to comply with Qt rules.
    """

    def __init__(self, hypertts: Any) -> None:
        self.hypertts = hypertts
        self.anki_utils = hypertts.anki_utils

    # ------------------------------------------------------------------
    # Editor context
    # ------------------------------------------------------------------

    def get_editor_context(self, editor: Any) -> config_models.EditorContext:
        """Build an EditorContext snapshot from the given editor window."""
        logger.debug(
            f'anki editor configuration: currentField: {editor.currentField} '
            f'last_field_index: {editor.last_field_index} '
            f'addMode: {editor.addMode} '
            f'selectedText: [{editor.web.selectedText()}] '
            + (
                f'card.note.items: {pprint.pformat(editor.card.note().items())} '
                f'card.note_type name: {pprint.pformat(editor.card.note_type()["name"])} '
                if editor.card is not None else 'card: None'
            )
        )

        selected_text: Optional[str] = None
        current_field_num = editor.currentField
        current_field_name: Optional[str] = None

        if current_field_num is not None:
            deck_note_type = self.get_editor_deck_note_type(editor)
            model = aqt.mw.col.models.get(deck_note_type.model_id)
            current_field_name = model['flds'][current_field_num]['name']

        if len(editor.web.selectedText()) > 0 and current_field_num is not None:
            selected_text = editor.web.selectedText()

        editor_context = config_models.EditorContext(
            note=editor.note,
            editor=editor,
            add_mode=editor.addMode,
            selected_text=selected_text,
            current_field=current_field_name,
            clipboard=self.anki_utils.get_clipboard_content(),
        )
        logger.debug(f'editor_context: {editor_context}')
        return editor_context

    def get_editor_deck_note_type(self, editor: Any) -> config_models.DeckNoteType:
        """Return the DeckNoteType for the note currently open in *editor*."""
        note = editor.note
        if note is None:
            raise RuntimeError('editor.note not found')

        if editor.addMode:
            add_cards: aqt.addcards.AddCards = editor.parentWindow
            return config_models.DeckNoteType(
                model_id=note.mid,
                deck_id=add_cards.deckChooser.selectedId(),
            )
        else:
            if editor.card is None:
                raise RuntimeError('editor.card not found')
            return config_models.DeckNoteType(model_id=note.mid, deck_id=editor.card.did)

    # ------------------------------------------------------------------
    # Add / process audio from editor
    # ------------------------------------------------------------------

    def editor_note_add_audio(
        self,
        batch: config_models.BatchConfig,
        editor_context: config_models.EditorContext,
        text_input: Optional[str] = None,
    ) -> None:
        """Generate audio for the note currently open in the editor and refresh it.

        Raises ``SuperFreeTTSError`` if *batch* targets ``CURSOR_LOCATION``
        (not supported from editor context).
        """
        if batch.target.insert_location == config_models.InsertLocation.CURSOR_LOCATION:
            lang = self.hypertts.get_ui_language()
            raise errors.SuperFreeTTSError(
                i18n.get_text("error_insert_cursor_unsupported", lang)
            )

        logger.debug(f'editor_note_add_audio, editor_context: {editor_context}')
        logger.debug(f'editor_note_add_audio, batch: {repr(batch)}')

        audio_request_context = context.AudioRequestContext(constants.AudioRequestReason.editor_browser)
        if editor_context.add_mode:
            audio_request_context = context.AudioRequestContext(constants.AudioRequestReason.editor_add)

        text_override: Optional[str] = None
        if text_input is not None:
            text_override = text_input
        elif batch.source.use_selection and editor_context.selected_text is not None:
            text_override = editor_context.selected_text

        logger.debug(f'text_override: {text_override}')
        source_text, processed_text, sound_file, full_filename = (
            self.hypertts.process_note_audio(
                batch,
                editor_context.note,
                editor_context.add_mode,
                audio_request_context,
                text_override,
                self.anki_utils.get_anki_collection(),
            )
        )

        logger.debug('after process_note_audio')
        logger.debug(f'about to call editor.set_note: {editor_context.note}')

        def get_set_note_lambda(editor: Any, note: Any):
            def editor_set_note():
                editor.set_note(note)
            return editor_set_note

        self.anki_utils.run_on_main(
            get_set_note_lambda(editor_context.editor, editor_context.note)
        )
        logger.debug('after set_note')
        self.anki_utils.play_sound(full_filename)

    def editor_note_process_rule(
        self,
        rule: config_models.MappingRule,
        editor_context: config_models.EditorContext,
    ) -> None:
        """Apply a single Mapping Rule unconditionally to the editor note."""
        preset = self.hypertts.load_preset(rule.preset_id)
        self.editor_note_add_audio(preset, editor_context)

    # ------------------------------------------------------------------
    # Preview audio from editor
    # ------------------------------------------------------------------

    def preview_note_audio_editor(
        self,
        batch: config_models.BatchConfig,
        editor_context: config_models.EditorContext,
    ) -> None:
        """Preview note audio, respecting *use_selection* if set."""
        text_override = None
        if batch.source.use_selection and editor_context.selected_text is not None:
            text_override = editor_context.selected_text
        self.preview_note_audio(batch, editor_context.note, text_override)

    def preview_note_audio(
        self,
        batch: config_models.BatchConfig,
        note: Any,
        text_override: Optional[str],
    ) -> None:
        """Generate and play audio for *note* without writing to any field."""
        batch.validate()
        full_filename, _ = self.hypertts.get_note_audio(
            batch,
            note,
            context.AudioRequestContext(constants.AudioRequestReason.preview),
            text_override,
        )
        self.anki_utils.play_sound(full_filename)

    # ------------------------------------------------------------------
    # Preview all mapping rules
    # ------------------------------------------------------------------

    def get_preview_all_rules_task(
        self,
        deck_note_type: config_models.DeckNoteType,
        editor_context: config_models.EditorContext,
        preset_mapping_rules: config_models.PresetMappingRules,
    ):
        def preview_fn():
            status = preset_rules_status.PresetRulesStatus('Previewing', self.anki_utils)
            for _, _, rule in preset_mapping_rules.iterate_applicable_rules(deck_note_type, False):
                with status.get_rule_action_context(rule) as rule_action_context:
                    logger.debug(f'previewing audio for rule {rule}')
                    preset = self.hypertts.load_preset(rule.preset_id)
                    rule_action_context.set_preset(preset)
                    self.preview_note_audio_editor(preset, editor_context)
        return preview_fn

    def get_preview_all_rules_done(self):
        lang = self.hypertts.get_ui_language()
        def done_fn(result):
            with self.hypertts.error_manager.get_single_action_context(
                i18n.get_text("title_previewing_rule", lang)
            ):
                result = result.result()
        return done_fn

    def preview_all_mapping_rules(
        self,
        editor_context: config_models.EditorContext,
        preset_mapping_rules: Optional[config_models.PresetMappingRules] = None,
    ) -> None:
        """Preview all Mapping Rules applicable to the current note type (background)."""
        if preset_mapping_rules is None:
            preset_mapping_rules = self.hypertts.load_mapping_rules()
        if len(preset_mapping_rules.rules) == 0:
            raise errors.NoPresetMappingRulesDefined()
        deck_note_type = self.get_editor_deck_note_type(editor_context.editor)
        self.anki_utils.run_in_background(
            self.get_preview_all_rules_task(deck_note_type, editor_context, preset_mapping_rules),
            self.get_preview_all_rules_done(),
        )

    # ------------------------------------------------------------------
    # Apply all mapping rules
    # ------------------------------------------------------------------

    def get_apply_all_rules_task(
        self,
        deck_note_type: config_models.DeckNoteType,
        editor_context: config_models.EditorContext,
        preset_mapping_rules: config_models.PresetMappingRules,
    ):
        def apply_fn():
            status = preset_rules_status.PresetRulesStatus('Applying', self.anki_utils)
            for _, _, rule in preset_mapping_rules.iterate_applicable_rules(deck_note_type, False):
                with status.get_rule_action_context(rule) as rule_action_context:
                    logger.debug(f'applying audio for rule {rule}')
                    preset = self.hypertts.load_preset(rule.preset_id)
                    rule_action_context.set_preset(preset)
                    self.editor_note_add_audio(preset, editor_context)
        return apply_fn

    def get_apply_all_rules_done(self):
        lang = self.hypertts.get_ui_language()
        def done_fn(result):
            with self.hypertts.error_manager.get_single_action_context(
                i18n.get_text("title_running_rules", lang)
            ):
                result = result.result()
        return done_fn

    def apply_all_mapping_rules(
        self,
        editor_context: config_models.EditorContext,
        preset_mapping_rules: Optional[config_models.PresetMappingRules] = None,
    ) -> None:
        """Apply all Mapping Rules applicable to the current note type (background)."""
        if preset_mapping_rules is None:
            preset_mapping_rules = self.hypertts.load_mapping_rules()
        if len(preset_mapping_rules.rules) == 0:
            raise errors.NoPresetMappingRulesDefined()
        deck_note_type = self.get_editor_deck_note_type(editor_context.editor)
        self.anki_utils.run_in_background(
            self.get_apply_all_rules_task(deck_note_type, editor_context, preset_mapping_rules),
            self.get_apply_all_rules_done(),
        )
