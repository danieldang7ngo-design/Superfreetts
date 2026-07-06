"""
realtime_manager.py — Realtime TTS management for Super Free TTS.

Handles:
  - Rendering and extracting Anki `{{tts}}` tags in card templates.
  - Adding/removing TTS tags from note types.
  - Realtime TTS audio generation and playback.
"""

import copy
import re

from typing import List, Optional, Tuple, Any

from . import constants
from . import config_models
from . import errors
from . import voice as voice_module
from . import text_utils
from . import context
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


class RealtimeManager:
    """
    Manages realtime TTS playback, previews, and card template tags.
    Delegates back to the parent ``SuperFreeTTS`` instance for audio file generation.
    """

    def __init__(self, hypertts: Any) -> None:
        self.hypertts = hypertts
        self.anki_utils = hypertts.anki_utils
        self.service_manager = hypertts.service_manager

    def get_realtime_audio(self, realtime_model: config_models.RealtimeConfigSide, text: str) -> Tuple[str, str]:
        source_text = text
        processed_text = text_utils.process_text(source_text, realtime_model.text_processing)
        if len(processed_text) == 0:
            raise errors.SourceTextEmpty()
        return self.hypertts.get_audio_file(
            processed_text,
            realtime_model.voice_selection,
            context.AudioRequestContext(constants.AudioRequestReason.realtime)
        )

    def play_realtime_audio(self, realtime_model: config_models.RealtimeConfigSide, text: str) -> None:
        full_filename, audio_filename = self.get_realtime_audio(realtime_model, text)
        self.anki_utils.play_sound(full_filename)

    def get_audio_filename_tts_tag(self, tts_tag: Any) -> str:
        preset = self.extract_preset(tts_tag.other_args)
        realtime_side_model = self.get_realtime_side_config(preset)
        full_filename, audio_filename = self.get_realtime_audio(realtime_side_model, tts_tag.field_text)
        return full_filename

    def build_realtime_tts_tag(self, realtime_side_model: config_models.RealtimeConfigSide, setting_key: str) -> str:
        logger.debug('build_realtime_tts_tag')
        if realtime_side_model.source.mode == constants.RealtimeSourceType.AnkiTTSTag:
            logger.debug(f'build_realtime_tts_tag, realtime_side_model: {realtime_side_model}')
            
            # get the audio language of the first voice
            voice_selection = realtime_side_model.voice_selection
            logger.debug(f'voice_selection.selection_mode: {voice_selection.selection_mode}')
            if voice_selection.selection_mode == constants.VoiceSelectionMode.single:
                voice_id = voice_selection.voice.voice_id
            else:
                voice_id = voice_selection.get_voice_list()[0].voice_id

            voice = self.service_manager.locate_voice(voice_id)
            audio_language = voice_module.get_audio_language_for_voice(voice)

            field_format = realtime_side_model.source.field_name
            if realtime_side_model.source.field_type == constants.AnkiTTSFieldType.Cloze:
                field_format = f'cloze:{realtime_side_model.source.field_name}'
            elif realtime_side_model.source.field_type == constants.AnkiTTSFieldType.ClozeOnly:
                field_format = f'cloze-only:{realtime_side_model.source.field_name}'
            return '{{tts ' + f"""{audio_language.name} {constants.TTS_TAG_HYPERTTS_PRESET}={setting_key} voices={constants.TTS_TAG_VOICE}:{field_format}""" + '}}'
        else:
            raise Exception(f'unsupported RealtimeSourceType: {realtime_side_model.source.mode}')

    def extract_preset(self, extra_args_array: List[str]) -> str:
        subset = [
            x for x in extra_args_array
            if constants.TTS_TAG_HYPERTTS_PRESET in x or constants.TTS_TAG_HYPERTTS_PRESET_LEGACY in x
        ]
        if len(subset) != 1:
            logger.error(f'could not process TTS tag extra args: {extra_args_array}')
            raise errors.TTSTagProcessingError()
        array_entry = subset[0]
        components = array_entry.split('=')
        return components[1]

    def get_realtime_side_config(self, preset: str) -> config_models.RealtimeConfigSide:
        if constants.AnkiCardSide.Front.name in preset:
            preset_name = preset.replace(constants.AnkiCardSide.Front.name + '_', '')
            return self.hypertts.load_realtime_config(preset_name).front
        else:
            preset_name = preset.replace(constants.AnkiCardSide.Back.name + '_', '')
            return self.hypertts.load_realtime_config(preset_name).back

    def card_template_has_tts_tag(self, note: Any, side: constants.AnkiCardSide, card_ord: int) -> Optional[str]:
        note_model = note.note_type()
        card_template = note_model["tmpls"][card_ord]
        side_template_key = 'qfmt' if side == constants.AnkiCardSide.Front else 'afmt'
        side_template = card_template[side_template_key]
        side_template = side_template.replace('\n', ' ')
        m = re.match(r'.*{{tts.*superfreet(?:t|s)s_preset=([^\s]+).*}}.*', side_template)
        if m is not None:
            preset_name = m.groups()[0]
            preset_name = preset_name.replace(side.name + '_', '')
            logger.info(f'found preset name in TTS tag inside card template: {preset_name}')
            return preset_name
        else:
            logger.info(f'didnt find a TTS tag in card template: {side_template}')
        return None

    def remove_tts_tag(self, card_template: str) -> str:
        return re.sub('{{tts.*}}', '', card_template)

    def set_tts_tag_note_model(
        self,
        realtime_side_model: config_models.RealtimeConfigSide,
        setting_key: Optional[str],
        note_model: dict,
        side: constants.AnkiCardSide,
        card_ord: int,
        clear_only: bool
    ) -> dict:
        logger.debug('set_tts_tag_note_model')
        tts_tag = self.build_realtime_tts_tag(realtime_side_model, setting_key) if not clear_only else ''
        logger.info(f'tts tag: {tts_tag}')
        return self.alter_tts_tag_note_model(note_model, side, card_ord, clear_only, tts_tag)

    def alter_tts_tag_note_model(
        self,
        note_model: dict,
        side: constants.AnkiCardSide,
        card_ord: int,
        clear_only: bool,
        tts_tag: str
    ) -> dict:
        card_template = note_model["tmpls"][card_ord]
        side_template_key = 'qfmt' if side == constants.AnkiCardSide.Front else 'afmt'
        side_template = card_template[side_template_key]
        side_template = self.remove_tts_tag(side_template)
        if not clear_only:
            side_template += '\n' + tts_tag
        card_template[side_template_key] = side_template
        note_model["tmpls"][card_ord] = card_template
        return note_model

    def render_card_template_extract_tts_tag(
        self,
        realtime_model: config_models.RealtimeConfig,
        note: Any,
        side: constants.AnkiCardSide,
        card_ord: int
    ) -> Any:
        realtime_model.validate()
        note_model = note.note_type()
        note_model = copy.deepcopy(note_model)
        note_model = self.set_tts_tag_note_model(realtime_model, 'preview', note_model, side, card_ord, False)
        logger.debug(f'render_card_template_extract_tts_tag, note_model {note_model}')

        card = self.anki_utils.create_card_from_note(note, card_ord, note_model, note_model["tmpls"][card_ord])
        if side == constants.AnkiCardSide.Front:
            return self.anki_utils.extract_tts_tags(card.question_av_tags())
        elif side == constants.AnkiCardSide.Back:
            return self.anki_utils.extract_tts_tags(card.answer_av_tags())

    def build_side_settings_key(self, card_side: constants.AnkiCardSide, settings_key: str) -> str:
        return f'{card_side.name}_{settings_key}'

    def persist_realtime_config_update_note_type(
        self,
        realtime_model: config_models.RealtimeConfig,
        note: Any,
        card_ord: int,
        current_settings_key: Optional[str]
    ) -> None:
        logger.debug('persist_realtime_config_update_note_type')
        undo_id = self.anki_utils.undo_tts_tag_start()

        settings_key = self.hypertts.save_realtime_config(realtime_model, current_settings_key)
        note_model = note.note_type()
        
        # process front side
        side = constants.AnkiCardSide.Front
        if realtime_model.front.side_enabled:
            side_settings_key = self.build_side_settings_key(side, settings_key)
            note_model = self.set_tts_tag_note_model(realtime_model.front, side_settings_key, note_model, side, card_ord, False)
        else:
            note_model = self.set_tts_tag_note_model(realtime_model.front, None, note_model, side, card_ord, True)

        # process back side
        side = constants.AnkiCardSide.Back
        if realtime_model.back.side_enabled:
            side_settings_key = self.build_side_settings_key(side, settings_key)
            note_model = self.set_tts_tag_note_model(realtime_model.back, side_settings_key, note_model, side, card_ord, False)
        else:
            note_model = self.set_tts_tag_note_model(realtime_model.back, None, note_model, side, card_ord, True)

        # save note model
        self.anki_utils.save_note_type_update(note_model)
        self.anki_utils.undo_end(undo_id)

    def remove_tts_tags(self, note: Any, card_ord: int) -> None:
        logger.debug('remove_tts_tags')
        undo_id = self.anki_utils.undo_tts_tag_start()
        note_model = note.note_type()
        
        side = constants.AnkiCardSide.Front
        note_model = self.alter_tts_tag_note_model(note_model, side, card_ord, True, '')
        
        side = constants.AnkiCardSide.Back
        note_model = self.alter_tts_tag_note_model(note_model, side, card_ord, True, '')
        
        self.anki_utils.save_note_type_update(note_model)
        self.anki_utils.undo_end(undo_id)
