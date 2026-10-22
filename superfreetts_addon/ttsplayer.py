"""
Register Super Free TTS voices with the Anki {{tts}} tag.
code modeled after 
https://ankiweb.net/shared/info/391644525 
https://github.com/ankitects/anki-addons/blob/master/code/gtts_player/__init__.py
"""

import concurrent.futures
import threading
from concurrent.futures import Future
from typing import List

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

# Hard bound on abandoned realtime generations.  Anki calls _play()
# serially, but a timed-out call keeps running on the executor.  Without a
# cap, repeatedly flipping cards while a service is stuck would queue an
# unbounded number of dead generations.  When this many are still in
# flight, _play() returns None immediately instead of queueing another one.
MAX_REALTIME_IN_FLIGHT = 4


class AnkiSuperFreeTTSPlayer(aqt.tts.TTSProcessPlayer):
    def __init__(self, taskman: aqt.taskman.TaskManager, hypertts) -> None:
        super(aqt.tts.TTSProcessPlayer, self).__init__(taskman)
        self.hypertts = hypertts
        # Used only to bound generation time (see REALTIME_GENERATE_TIMEOUT_SECONDS
        # above) - small pool since Anki already serializes calls to _play()
        # one at a time via AVPlayer.current_player, this just lets a timed-out
        # call keep running in the background without blocking _play() itself.
        self._generate_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_REALTIME_IN_FLIGHT,
            thread_name_prefix='sftts-realtime-gen'
        )
        self._in_flight = 0
        self._in_flight_lock = threading.Lock()
        self._executor_shutdown = False
        # Bumped on every restart so callbacks from an older executor cannot
        # decrement the in-flight counter belonging to the new one.
        self._generation = 0
        logger.info('created AnkiSuperFreeTTSPlayer')

    def _release_in_flight_slot(self, generation: int = None) -> None:
        with self._in_flight_lock:
            if (
                generation is not None
                and generation != getattr(self, '_generation', 0)
            ):
                return
            self._in_flight = max(0, self._in_flight - 1)

    def restart(self) -> None:
        """Recreate the generation executor after a previous shutdown.

        Anki does not reload add-ons when the user switches profiles: only
        ``profile_will_close`` / ``profile_did_open`` fire.  Without this
        reset, the player shut down on the first profile close would keep
        rejecting realtime TTS until Anki restarts.
        """
        with self._in_flight_lock:
            if not getattr(self, '_executor_shutdown', False):
                return
            self._generation = getattr(self, '_generation', 0) + 1
            self._in_flight = 0
            self._generate_executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=MAX_REALTIME_IN_FLIGHT,
                thread_name_prefix='sftts-realtime-gen'
            )
            self._executor_shutdown = False
        logger.info('restarted realtime TTS executor after profile reopen')

    def shutdown(self, wait: bool = False) -> None:
        """Stop accepting realtime work and drop queued generations."""
        with self._in_flight_lock:
            if getattr(self, '_executor_shutdown', False):
                return
            self._executor_shutdown = True
            self._generation = getattr(self, '_generation', 0) + 1
            self._in_flight = 0
            executor = self._generate_executor
        try:
            executor.shutdown(wait=wait, cancel_futures=True)
        except TypeError:
            # Python < 3.9 compatibility (cancel_futures was added in 3.9).
            executor.shutdown(wait=wait)
        except Exception as e:
            logger.warning(f'Realtime executor shutdown error: {e}')

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

        with self._in_flight_lock:
            if getattr(self, '_executor_shutdown', False):
                logger.warning('Realtime TTS player is shutting down; skipping generation')
                return None
            if self._in_flight >= MAX_REALTIME_IN_FLIGHT:
                logger.warning(
                    f'Realtime TTS already has {MAX_REALTIME_IN_FLIGHT} generations in flight; '
                    f'skipping this card instead of queueing more work'
                )
                return None

            self._in_flight += 1
            # Read the generation under the same lock used by restart() so
            # a callback always belongs to the executor that ran the task.
            generation = getattr(self, '_generation', 0)
            executor = self._generate_executor
            try:
                future = executor.submit(
                    self.hypertts.get_audio_filename_tts_tag, tag
                )
            except RuntimeError:
                # The executor can be shut down between the flag check above
                # and submit() when a profile closes concurrently.
                self._in_flight = max(0, self._in_flight - 1)
                if getattr(self, '_executor_shutdown', False):
                    logger.warning('Realtime TTS player shut down while queuing generation')
                    return None
                raise
            except Exception:
                self._in_flight = max(0, self._in_flight - 1)
                raise

        future.add_done_callback(
            lambda _future: self._release_in_flight_slot(generation)
        )
        try:
            audio_filename = future.result(timeout=REALTIME_GENERATE_TIMEOUT_SECONDS)
        except concurrent.futures.CancelledError:
            logger.warning(
                f'TTS generation for tag {tag} was cancelled during shutdown; skipping playback'
            )
            return None
        except concurrent.futures.TimeoutError:
            # Best effort: this only succeeds if the task is still queued.
            # A running call cannot be interrupted safely here, but its slot
            # stays reserved until it actually finishes, so the number of
            # abandoned generations remains bounded.
            future.cancel()
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
                logger.warning('no audio filename, not playing any audio')
        cb()

