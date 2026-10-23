import os
import sys

import pytest

from tests import mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from unittest.mock import MagicMock

from superfreetts_addon.realtime_manager import RealtimeManager


def make_rm():
    hypertts = MagicMock()
    return RealtimeManager(hypertts)


@pytest.mark.unit
def test_remove_tts_tag_non_greedy_keeps_between_tags():
    rm = make_rm()
    template = "A {{tts X}} B {{tts Y}} C"
    assert rm.remove_tts_tag(template) == "A  B  C"


@pytest.mark.unit
def test_remove_tts_tag_single():
    rm = make_rm()
    assert rm.remove_tts_tag("hello {{tts foo}} world") == "hello  world"
