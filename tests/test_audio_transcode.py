"""Unit tests for the shared audio-transcode helper (muc 4).

Policy: save what the engine produces; convert WAV->MP3 only when the user
picked MP3; never convert when the bytes already match; MP3->WAV is
unsupported and keeps the original bytes.
"""

from unittest.mock import MagicMock, patch

import pytest

from tests import mock_anki

mock_anki.mock_all()

from superfreetts_addon import audio_transcode, options


WAV_BYTES = b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 64
MP3_BYTES = b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"\x00" * 64


@pytest.mark.unit
def test_native_format_for_documents_engine_output():
    assert audio_transcode.native_format_for("EdgeTTS") == options.AudioFormat.mp3
    for service in ("PiperTTS", "KokoroTTS", "MmsTTS", "SupertonicTTS", "Piper", "MMS"):
        assert audio_transcode.native_format_for(service) == options.AudioFormat.wav


@pytest.mark.unit
def test_matching_format_does_not_call_converter():
    with patch.object(audio_transcode, "convert_wav_to_mp3") as convert:
        assert audio_transcode.maybe_convert(WAV_BYTES, options.AudioFormat.wav) == WAV_BYTES
        assert audio_transcode.maybe_convert(MP3_BYTES, options.AudioFormat.mp3) == MP3_BYTES
    convert.assert_not_called()


@pytest.mark.unit
def test_wav_to_mp3_converts_when_mp3_requested():
    with patch.object(audio_transcode, "convert_wav_to_mp3", return_value=MP3_BYTES) as convert:
        assert audio_transcode.maybe_convert(WAV_BYTES, options.AudioFormat.mp3) == MP3_BYTES
    convert.assert_called_once_with(WAV_BYTES)


@pytest.mark.unit
def test_wav_to_mp3_failure_keeps_wav():
    with patch.object(audio_transcode, "convert_wav_to_mp3", side_effect=RuntimeError("no ffmpeg")):
        assert audio_transcode.maybe_convert(WAV_BYTES, options.AudioFormat.mp3) == WAV_BYTES


@pytest.mark.unit
def test_mp3_to_wav_is_unsupported_and_keeps_mp3():
    with patch.object(audio_transcode, "convert_wav_to_mp3") as convert:
        assert audio_transcode.maybe_convert(MP3_BYTES, options.AudioFormat.wav) == MP3_BYTES
    convert.assert_not_called()


@pytest.mark.unit
def test_convert_if_requested_respects_preference():
    with patch.object(audio_transcode, "preferred_output_format", return_value="wav"):
        with patch.object(audio_transcode, "convert_wav_to_mp3") as convert:
            assert audio_transcode.convert_if_requested(WAV_BYTES, "KokoroTTS") == WAV_BYTES
        convert.assert_not_called()

    with patch.object(audio_transcode, "preferred_output_format", return_value="mp3"):
        with patch.object(audio_transcode, "convert_wav_to_mp3", return_value=MP3_BYTES):
            assert audio_transcode.convert_if_requested(WAV_BYTES, "KokoroTTS") == MP3_BYTES


@pytest.mark.unit
def test_preferred_output_format_defaults_to_wav_on_unexpected_config():
    with patch("aqt.mw", MagicMock()) as mw:
        mw.addonManager.getConfig.return_value = MagicMock()
        assert audio_transcode.preferred_output_format() == "wav"
