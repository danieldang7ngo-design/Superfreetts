"""
audio_generator.py — Single-note audio generation for Super Free TTS.

Responsibility:
  - Choosing the appropriate voice for a given VoiceSelection config.
  - Generating audio for a single piece of text (process_note_audio, get_note_audio).
  - Writing the audio file to disk and returning the filename.
  - Retrying with priority-list fallback when a voice fails.
  - Delegating service calls to service_manager and file writes to audio_store.

NOT responsible for:
  - Batch orchestration (→ batch_orchestrator.py)
  - Realtime TTS tag rendering (→ realtime_manager.py)
  - Config persistence (→ config_store.py)
  - Anki Editor interactions (→ editor_manager.py)
"""

import copy
import random
from typing import Any, List, Optional, Tuple

from . import constants
from . import config_models
from . import errors
from . import voice as voice_module
from . import text_utils
from . import context
from . import audio_file_store
from . import logging_utils
from . import performance_tracker
from . import note_audio_updater
from . import i18n
from . import source_text_resolver

logger = logging_utils.get_child_logger(__name__)


class AudioGenerator:
    """
    Generates TTS audio for a single note / text string.

    Delegates audio file writes to ``hypertts.audio_store``,
    service calls to ``hypertts.service_manager``, and executor
    cache writes to ``hypertts.executor``.
    """

    def __init__(self, hypertts: Any) -> None:
        self.hypertts = hypertts
        self.anki_utils = hypertts.anki_utils
        self.service_manager = hypertts.service_manager

    # ------------------------------------------------------------------
    # Properties that follow the parent's mutable references
    # ------------------------------------------------------------------

    @property
    def audio_store(self) -> Any:
        return self.hypertts.audio_store

    @property
    def executor(self) -> Any:
        return self.hypertts.executor

    # ------------------------------------------------------------------
    # Voice selection
    # ------------------------------------------------------------------

    def choose_voice(
        self,
        voice_selection: config_models.VoiceSelectionBase,
        voice_list: Optional[List],
        sequence_index: Optional[int] = None,
    ) -> config_models.VoiceWithOptions:
        """Pick a concrete voice from *voice_selection* config."""
        if voice_selection.selection_mode == constants.VoiceSelectionMode.single:
            return voice_selection.voice
        elif voice_selection.selection_mode == constants.VoiceSelectionMode.random:
            logger.info(f'choosing from {len(voice_selection.voice_list)} voices')
            choice = random.choices(
                voice_selection.voice_list,
                weights=[x.random_weight for x in voice_selection.voice_list],
            )
            return choice[0]
        elif voice_selection.selection_mode == constants.VoiceSelectionMode.priority:
            return voice_list.pop(0)
        elif voice_selection.selection_mode == constants.VoiceSelectionMode.sequence:
            voice_count = len(voice_selection.voice_list)
            if voice_count == 0:
                raise errors.NoVoicesAdded()
            if sequence_index is None:
                sequence_index = getattr(voice_selection, '_sequence_runtime_index', 0)
                voice_selection._sequence_runtime_index = sequence_index + 1
            return voice_selection.voice_list[sequence_index % voice_count]

    # ------------------------------------------------------------------
    # Core audio write
    # ------------------------------------------------------------------

    def generate_audio_write_file(
        self,
        source_text: str,
        voice_id: voice_module.TtsVoiceId_v3,
        voice_options: dict,
        audio_request_context: Any,
    ) -> Tuple[str, str]:
        """Generate TTS audio and write it to the user_files directory.

        Returns ``(full_filename, audio_filename)``.
        Uses the audio_store cache; hits the TTS service only on a miss.
        """
        assert isinstance(voice_id, voice_module.TtsVoiceId_v3), (
            f"Expected voice_id to be TtsVoiceId_v3, got {type(voice_id).__name__}"
        )
        request_key = self.audio_store.build_request_key(source_text, voice_id, voice_options)
        cached_file = self.audio_store.get_cached_file(request_key)
        file_result = cached_file or self.audio_store.get_file_result(request_key, cache_hit=False)
        logger.info(
            f'requesting audio for hash {request_key.hash()}, '
            f'full filename {file_result.full_filename}'
        )

        tracker = performance_tracker.get_performance_tracker()
        try:
            service_name = getattr(voice_id, 'service', 'unknown')
            if hasattr(voice_id, 'voice_key'):
                voice_key_name = (
                    voice_id.voice_key.get('name', 'unknown')
                    if isinstance(voice_id.voice_key, dict)
                    else str(voice_id.voice_key)
                )
            else:
                voice_key_name = 'unknown'
            voice_name = f"{service_name}:{voice_key_name}"
        except Exception as e:
            voice_name = str(voice_id)
            logger.debug(f'Error extracting voice name for tracking: {e}')
        tracker.start_generation(source_text, voice_name)

        try:
            if cached_file is None:
                voice = self.service_manager.locate_voice(voice_id)
                logger.info(f'located voice: {voice}')
                audio_data = self.service_manager.get_tts_audio(
                    source_text, voice, voice_options, audio_request_context
                )
                logger.info('not found in cache, requesting')
                logger.debug(f'writing {file_result.full_filename}')
                file_result = self.audio_store.write_audio_file_atomic(request_key, audio_data)
                logger.debug('wrote audio data')
            else:
                logger.info('file exists in cache')
        finally:
            tracker.end_generation()

        return file_result.full_filename, file_result.audio_filename

    # ------------------------------------------------------------------
    # Public API: get audio file (handles priority fallback)
    # ------------------------------------------------------------------

    def get_audio_file(
        self,
        processed_text: str,
        voice_selection: Any,
        audio_request_context: Any,
    ) -> Tuple[str, str]:
        """Return ``(full_filename, audio_filename)`` for *processed_text*.

        Handles single / random / priority / sequence selection modes.
        Priority mode iterates the voice list until one succeeds.
        """
        if voice_selection.selection_mode in [
            constants.VoiceSelectionMode.priority,
            constants.VoiceSelectionMode.random,
            constants.VoiceSelectionMode.sequence,
        ]:
            if len(voice_selection.voice_list) == 0:
                raise errors.NoVoicesAdded()

        voice_list = None
        priority_mode = voice_selection.selection_mode == constants.VoiceSelectionMode.priority
        if priority_mode:
            voice_list = copy.copy(voice_selection.voice_list)
        sound_found = False
        loop_condition = True
        while loop_condition:
            try:
                voice_with_options = self.choose_voice(voice_selection, voice_list)
                logger.debug(f'about to generate audio file for {processed_text}')
                voice_id = voice_with_options.voice_id
                assert isinstance(voice_id, voice_module.TtsVoiceId_v3), (
                    f"Expected TtsVoiceId_v3, got {type(voice_id).__name__}, "
                    f"voice_with_options: {type(voice_with_options).__name__}"
                )
                full_filename, audio_filename = self.generate_audio_write_file(
                    processed_text,
                    voice_with_options.voice_id,
                    voice_with_options.options,
                    audio_request_context,
                )
                logger.debug(f'finished generating audio for {processed_text}')
                self.anki_utils.run_on_main(self.hypertts.config_register_added_audio)
                return full_filename, audio_filename
            except errors.AudioNotFoundError as exc:
                if not priority_mode:
                    raise exc
            loop_condition = priority_mode and sound_found is False and len(voice_list) > 0
        raise errors.AudioNotFoundAnyVoiceError(processed_text)

    # ------------------------------------------------------------------
    # Public API: process and write audio for a single note
    # ------------------------------------------------------------------

    def process_note_audio(
        self,
        batch: config_models.BatchConfig,
        note: Any,
        add_mode: bool,
        audio_request_context: Any,
        text_override: Optional[str],
        anki_collection: Any,
    ) -> Tuple[str, str, str, str]:
        """Generate audio for *note* and write it into the note's target field.

        Returns ``(source_text, processed_text, sound_file, full_filename)``.
        """
        target_field = batch.target.target_field
        if target_field not in note:
            raise errors.TargetFieldNotFoundError(target_field)

        source_text = self.hypertts.get_source_text(note, batch.source, text_override)
        processed_text = self.hypertts.process_text(source_text, batch.text_processing)

        full_filename, audio_filename = self.get_audio_file(
            processed_text, batch.voice_selection, audio_request_context
        )
        sound_file = audio_filename
        logger.debug(f'setting note[{target_field}] to audio file {sound_file}')
        note_audio_updater.update_note_with_audio(
            self.anki_utils,
            note,
            batch,
            source_text,
            sound_file,
            full_filename,
            anki_collection,
            update_collection=not add_mode,
        )
        return source_text, processed_text, sound_file, full_filename

    def get_note_audio(
        self,
        batch: config_models.BatchConfig,
        note: Any,
        audio_request_context: Any,
        text_override: Optional[str],
    ) -> Tuple[str, str]:
        """Return ``(full_filename, audio_filename)`` without writing to the note.

        Used for preview playback.
        """
        source_text = self.hypertts.get_source_text(note, batch.source, text_override)
        processed_text = text_utils.process_text(source_text, batch.text_processing)
        if len(processed_text) == 0:
            raise errors.SourceTextEmpty()
        return self.get_audio_file(processed_text, batch.voice_selection, audio_request_context)

    def play_sound(
        self,
        source_text: str,
        voice_id: voice_module.TtsVoiceId_v3,
        options: dict,
    ) -> None:
        """Generate and immediately play audio for *source_text*."""
        logger.info(f'playing audio for {source_text}')
        if not source_text:
            raise errors.SourceTextEmpty()
        full_filename, _ = self.generate_audio_write_file(
            source_text, voice_id, options,
            context.AudioRequestContext(constants.AudioRequestReason.preview)
        )
        self.anki_utils.play_sound(full_filename)
