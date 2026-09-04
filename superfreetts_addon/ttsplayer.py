"""
Register Super Free TTS voices with the Anki {{tts}} tag.
code modeled after 
https://ankiweb.net/shared/info/391644525 
https://github.com/ankitects/anki-addons/blob/master/code/gtts_player/__init__.py
"""

import sys
import concurrent.futures
from concurrent.futures import Future
from dataclasses import dataclass
from typing import List, cast

# import aqt
import aqt.tts
import anki
import anki.utils

from . import constants
from . import languages
from . import logging_utils
logger = logging_utils.get_child_logger(__name__)

# Root cause 2.2 (see superfreetts_macos_crash_fix_plan.md, section 2.2 /
# Phase 3): aqt's SimpleProcessPlayer.stop() sets `_terminate_flag`, and its
# built-in `_wait_for_termination()` polls that flag to actually interrupt a
# playing/generating tag when the user advances to a new card. This add-on
# fully overrides `_play()` and never calls `_wait_for_termination()` or
# checks `_terminate_flag`, so Anki's "stop current audio" request is
# silently ignored while a slow/stuck generation is in flight - the whole
# playback queue then stalls until that call finishes or errors on its own.
#
# True cancellation (aborting the in-flight network/subprocess call itself)
# would require threading a cancellation signal through every service's
# get_tts_audio/get_tts_audio_batch implementation (EdgeTTS, MMS, Kokoro,
# Piper, Supertonic, macOS `say`) - a much larger, higher-risk change touching
# many files. As a lower-risk first fix (documented as "approach b" in the
# plan) we instead bound how long a single generation is allowed to block
# playback: if it doesn't finish within this timeout, `_play()` gives up and
# lets Anki move on to the next card's audio. The abandoned call keeps
# running in its own thread until it completes or errors, and its result is
# simply discarded - this does not eliminate the orphaned resource usage,
# it only prevents one stuck request from freezing the whole session.
#
# This value is a conservative, not-yet-measured default (no real-network
# timing data was collected for this fix) - it intentionally sits above
# typical TTS generation latency to avoid cutting off legitimately slow but
# healthy requests (e.g. long-text EdgeTTS synthesis, cold-start local model
# load). Tune based on real-world reports if it proves too short/long.
REALTIME_GENERATE_TIMEOUT_SECONDS = 20


class AnkiSuperFreeTTSPlayer(aqt.tts.TTSProcessPlayer):
    def __init__(self, taskman: aqt.taskman.TaskManager, hypertts) -> None:
        super(aqt.tts.TTSProcessPlayer, self).__init__(taskman)
        self.hypertts = hypertts
        # Used only to bound generation time (see REALTIME_GENERATE_TIMEOUT_SECONDS
        # above) - small pool since Anki already serializes calls to _play()
        # one at a time via AVPlayer.current_player, this just lets a timed-out
        # call keep running in the background without blocking _play() itself.
        self._generate_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=4, thread_name_prefix='sftts-realtime-gen'
        )
        logger.info('created AnkiSuperFreeTTSPlayer')

    # this is called the first time Anki tries to play a TTS file
    def get_available_voices(self) -> List[aqt.tts.TTSVoice]:

        # register a voice for every possible language Super Free TTS supports. This avoids forcing the user to do a restart when
        # they configure a new TTS tag
        
        voices = []
        for audio_language in languages.AudioLanguage:
            language_name = audio_language.name
            if anki.utils.point_version() == 58:
                voices.append(aqt.tts.TTSVoice(name=constants.TTS_TAG_VOICE, lang=language_name, available=True))
            else:
                voices.append(aqt.tts.TTSVoice(name=constants.TTS_TAG_VOICE, lang=language_name))

        return voices  # type: ignore

    # this is called on a background thread, and will not block the UI
    def _play(self, tag: anki.sound.AVTag):
        self.audio_file_path = None
        self.playback_error = False
        self.playback_error_message = None

        assert isinstance(tag, anki.sound.TTSTag)

        if constants.TTS_TAG_VOICE not in tag.voices:
            logger.warning(f'Super Free TTS voice not found in tag {tag}, skipping')
            return None

        logger.info(f'playing TTS sound for {tag}, voices: {tag.voices}')

        future = self._generate_executor.submit(self.hypertts.get_audio_filename_tts_tag, tag)
        try:
            audio_filename = future.result(timeout=REALTIME_GENERATE_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            logger.warning(
                f'TTS generation exceeded {REALTIME_GENERATE_TIMEOUT_SECONDS}s for tag {tag}; '
                f'giving up on this card so playback can continue. The generation call is still '
                f'running in the background and its result will be discarded when it finishes.'
            )
            return None
        # Any other exception from get_audio_filename_tts_tag propagates unchanged
        # here (future.result() re-raises it), matching pre-fix behavior where the
        # exception propagated directly out of _play().
        return audio_filename

    # this is called on the main thread, after _play finishes
    def _on_done(self, ret: Future, cb: aqt.sound.OnDoneCallback) -> None:
        with self.hypertts.get_tts_player_action_context():
            audio_filename = ret.result()
            if audio_filename != None:
                logger.info(f'got audio_filename: {audio_filename}')
                try:
                    self.hypertts.usage_tracker.record_realtime_play()
                except Exception as e:
                    logger.debug(f'[USAGE] record_realtime_play failed: {e}')
                aqt.sound.av_player.insert_file(audio_filename)
            else:
                logger.warning(f'no audio filename, not playing any audio')
        cb()

