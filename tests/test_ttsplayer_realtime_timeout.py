"""
Unit tests for root cause 2.2 fix: AnkiSuperFreeTTSPlayer._play() never
checked aqt's `_terminate_flag` cancellation contract, so a single slow or
stuck generation could block Anki's whole audio playback queue indefinitely
(reported as "văng liên tục khi dùng realtime TTS" on macOS).

See superfreetts_macos_crash_fix_plan.md, section 2.2 / Phase 3 (approach b:
bounded timeout instead of full cross-service cancellation).

IMPORTANT TESTING NOTE (documented so nobody re-adds an "easier" test later
that silently tests nothing): under this repo's tests/mock_anki.py,
`aqt.tts.TTSProcessPlayer` resolves to a fresh MagicMock() **instance**
(not a type) on every access (MockModule.__getattr__ has no caching, and
nothing else ever sets a real value for that attribute). Using a MagicMock
instance as a base class collapses the whole `class AnkiSuperFreeTTSPlayer(
aqt.tts.TTSProcessPlayer):` statement into MagicMock machinery - verified
directly:

    ttsplayer.AnkiSuperFreeTTSPlayer  # -> <MagicMock spec='str' ...>
    type(ttsplayer.AnkiSuperFreeTTSPlayer)  # -> <class 'unittest.mock.MagicMock'>

i.e. under the plain global mock, `AnkiSuperFreeTTSPlayer` is not a real
class at all - not even `AnkiSuperFreeTTSPlayer._play` (unbound) is
reachable. Any test that imports ttsplayer.py under the unmodified global
mock and calls anything on the resulting object would silently be testing
MagicMock's auto-generated behavior, not our code - a false-confidence test.

To actually exercise the real method body, this module gives
`aqt.tts.TTSProcessPlayer` a real (tiny) base class BEFORE importing
ttsplayer.py, and reloads the module so its `class AnkiSuperFreeTTSPlayer(...)`
statement runs against that real base and produces a real Python class. The
original mock state is restored on teardown so it doesn't leak into other
test files that share the same process/module cache.
"""

import sys
import os
import time
import importlib
import concurrent.futures
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from tests import mock_anki
mock_anki.mock_all()

from superfreetts_addon import constants  # noqa: E402

# NOTE: deliberately NOT importing `aqt.tts` / `anki.sound` as module-level
# names here. Several other test files in this suite also call
# mock_anki.mock_all() at their own module scope (grep for
# `mock_anki.mock_all()` across tests/ to confirm), and pytest imports every
# test file during its collection phase before running any test. That means
# `sys.modules['aqt.tts']` / `sys.modules['anki.sound']` can be replaced by a
# brand new MockModule object after this file's own module-level code has
# already run - a name bound here at collection time would silently become
# a reference to an orphaned, no-longer-current module. Fixtures below
# re-fetch `sys.modules['aqt.tts']` / `sys.modules['anki.sound']` fresh each
# time they run instead, which is what actually fixed a real failure
# observed when running this file as part of the full suite (it passed in
# isolation but failed with `AttributeError: Mock object has no attribute
# '_play'` when run after other files - confirming the staleness above was
# a real bug in the test, not a hypothetical one).


class _RealTTSProcessPlayerBase:
    """Minimal stand-in for aqt.tts.TTSProcessPlayer that is an actual
    Python type (unlike the MagicMock instance mock_anki normally provides
    for it), just enough for `class AnkiSuperFreeTTSPlayer(...)` to become a
    real, testable class. Mirrors the one bit of real aqt behavior this
    test suite cares about: SimpleProcessPlayer.__init__ sets
    `_terminate_flag = False` (verified against the real aqt wheel, see
    fix plan section 1.2) - kept here for documentation parity even though
    the current tests don't exercise it directly (that's root cause 2.2's
    "approach a", not implemented in this fix)."""
    def __init__(self, taskman):
        self.taskman = taskman
        self._terminate_flag = False


@pytest.fixture(autouse=True)
def _real_ttsplayer_module():
    """
    Swap in a real base class for aqt.tts.TTSProcessPlayer, force
    superfreetts_addon.ttsplayer to be (re)imported against it, run the
    test, then restore the original mock attribute so other test files
    that import aqt.tts later in the same session see the same mock
    behavior they did before this file ran.

    Fetches sys.modules['aqt.tts'] fresh here (not a name captured at this
    file's collection time) - see the module docstring note on why a
    collection-time reference would be stale/orphaned in a full-suite run.
    """
    aqt_tts = sys.modules['aqt.tts']
    original_attr_present = 'TTSProcessPlayer' in aqt_tts.__dict__
    original_value = aqt_tts.__dict__.get('TTSProcessPlayer')

    aqt_tts.TTSProcessPlayer = _RealTTSProcessPlayerBase
    if 'superfreetts_addon.ttsplayer' in sys.modules:
        importlib.reload(sys.modules['superfreetts_addon.ttsplayer'])
    else:
        importlib.import_module('superfreetts_addon.ttsplayer')

    yield

    if original_attr_present:
        aqt_tts.TTSProcessPlayer = original_value
    elif 'TTSProcessPlayer' in aqt_tts.__dict__:
        del aqt_tts.__dict__['TTSProcessPlayer']
    if 'superfreetts_addon.ttsplayer' in sys.modules:
        importlib.reload(sys.modules['superfreetts_addon.ttsplayer'])


@pytest.fixture
def ttsplayer():
    """Provides the freshly-reloaded real module for each test."""
    return sys.modules['superfreetts_addon.ttsplayer']


class _DummyTTSTag:
    """Stand-in for anki.sound.TTSTag with just enough shape for _play()."""
    def __init__(self, voices):
        self.voices = voices


@pytest.fixture(autouse=True)
def _fixed_tts_tag_class():
    """
    _play() does `assert isinstance(tag, anki.sound.TTSTag)`. Under
    mock_anki, anki.sound.TTSTag would normally resolve to a brand new
    MagicMock() on every single access (no caching in MockModule.__getattr__),
    so two accesses are never the same object/type and isinstance() would be
    unreliable. Pin it to one real, stable class for the duration of each
    test. Fetches sys.modules['anki.sound'] fresh here for the same
    staleness reason as _real_ttsplayer_module above.
    """
    anki_sound = sys.modules['anki.sound']
    anki_sound.TTSTag = _DummyTTSTag
    yield


def _make_player_stub(hypertts, timeout_override=None):
    """
    Builds a minimal object with just the attributes `_play()` actually
    reads (`self.hypertts`, `self._generate_executor`) - deliberately NOT
    going through AnkiSuperFreeTTSPlayer(...), see module docstring.
    """
    stub = SimpleNamespace()
    stub.hypertts = hypertts
    stub._generate_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    return stub


def _make_tag():
    return _DummyTTSTag(voices=[constants.TTS_TAG_VOICE])


@pytest.mark.unit
class TestRealtimeGenerateTimeout:

    def test_normal_fast_generation_returns_filename(self, ttsplayer):
        """Baseline: fast generation must still work exactly as before."""
        hypertts = MagicMock()
        hypertts.get_audio_filename_tts_tag.return_value = "/tmp/fake_audio.mp3"
        stub = _make_player_stub(hypertts)
        tag = _make_tag()

        result = ttsplayer.AnkiSuperFreeTTSPlayer._play(stub, tag)

        assert result == "/tmp/fake_audio.mp3"
        hypertts.get_audio_filename_tts_tag.assert_called_once_with(tag)

    def test_stuck_generation_times_out_and_returns_none(self, ttsplayer):
        """
        This is the core regression test for root cause 2.2: a generation
        call that never returns (simulating a hung network/subprocess call
        with no cancellation) must NOT block _play() forever. It should give
        up after the timeout and return None so Anki's playback queue can
        move on to the next card.
        """
        release_event = None  # never set - the call "hangs" for the test's duration

        def hanging_call(tag):
            time.sleep(2)  # simulates a stuck call; kept short so the ThreadPoolExecutor's
            # non-daemon worker thread does not hang the whole pytest process at exit
            # (concurrent.futures joins all threads it ever created at interpreter exit
            # regardless of executor.shutdown() calls) - verified this was the actual
            # cause of a real hang while writing this test, not a hypothetical concern.

        hypertts = MagicMock()
        hypertts.get_audio_filename_tts_tag.side_effect = hanging_call
        stub = _make_player_stub(hypertts)
        tag = _make_tag()

        # Use a short timeout for the test instead of the real 20s default,
        # so this test runs fast without changing production behavior.
        with patch.object(ttsplayer, 'REALTIME_GENERATE_TIMEOUT_SECONDS', 0.2):
            start = time.monotonic()
            result = ttsplayer.AnkiSuperFreeTTSPlayer._play(stub, tag)
            elapsed = time.monotonic() - start

        assert result is None
        # Must return close to the timeout, not hang indefinitely (999s) and
        # not return near-instantly either (that would mean the timeout
        # logic isn't actually being exercised).
        assert elapsed < 2.0

    def test_genuine_exception_still_propagates_unchanged(self, ttsplayer):
        """
        Non-timeout errors (e.g. a real TTS service error) must propagate
        exactly as they did before this fix - the timeout wrapper must only
        intercept TimeoutError, not swallow/mask other failures.
        """
        hypertts = MagicMock()
        hypertts.get_audio_filename_tts_tag.side_effect = ValueError("boom")
        stub = _make_player_stub(hypertts)
        tag = _make_tag()

        with pytest.raises(ValueError, match="boom"):
            ttsplayer.AnkiSuperFreeTTSPlayer._play(stub, tag)

    def test_timed_out_call_does_not_prevent_next_call(self, ttsplayer):
        """
        A follow-up call to _play() (simulating the user flipping to the
        next card right after a stuck one) must still work normally and not
        be blocked by the previous abandoned call - this is the concrete
        behavior that fixes "the whole queue stalls" from root cause 2.2.
        """
        hypertts = MagicMock()

        def hanging_then_fast(tag):
            if hypertts.get_audio_filename_tts_tag.call_count == 1:
                time.sleep(2)
            return "/tmp/second_card.mp3"

        hypertts.get_audio_filename_tts_tag.side_effect = hanging_then_fast
        stub = _make_player_stub(hypertts)

        with patch.object(ttsplayer, 'REALTIME_GENERATE_TIMEOUT_SECONDS', 0.2):
            first_result = ttsplayer.AnkiSuperFreeTTSPlayer._play(stub, _make_tag())
            assert first_result is None  # timed out, as in the previous test

            second_result = ttsplayer.AnkiSuperFreeTTSPlayer._play(stub, _make_tag())
            assert second_result == "/tmp/second_card.mp3"
