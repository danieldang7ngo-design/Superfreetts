"""
Unit tests for error handling module.
"""

import pytest
import sys
import os

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)

from superfreetts_addon import errors


@pytest.mark.unit
class TestErrorHierarchy:
    """Test error hierarchy and structure"""
    
    def test_base_error_inherits_from_exception(self):
        """Verify SuperFreeTTSError is a proper exception"""
        err = errors.SuperFreeTTSError("test message")
        assert isinstance(err, Exception)
    
    def test_hypertts_error_alias(self):
        """Test HyperTTSError is alias for SuperFreeTTSError"""
        assert errors.HyperTTSError is errors.SuperFreeTTSError
    
    def test_collection_not_open(self):
        """Test CollectionNotOpen error message"""
        err = errors.CollectionNotOpen()
        assert "Collection not open" in str(err)
        assert isinstance(err, errors.SuperFreeTTSError)
    
    def test_field_not_found_error(self):
        """Test field not found error includes field name"""
        field_name = "TestField"
        err = errors.FieldNotFoundError(field_name)
        assert field_name in str(err)
        assert "not found" in str(err).lower()
    
    def test_source_field_not_found(self):
        """Test source field not found error"""
        err = errors.SourceFieldNotFoundError("SourceTest")
        assert isinstance(err, errors.SuperFreeTTSError)
        assert "SourceTest" in str(err)
    
    def test_target_field_not_found(self):
        """Test target field not found error"""
        err = errors.TargetFieldNotFoundError("TargetTest")
        assert isinstance(err, errors.SuperFreeTTSError)
        assert "TargetTest" in str(err)
    
    def test_field_empty_error(self):
        """Test field empty error"""
        err = errors.FieldEmptyError("EmptyField")
        assert "empty" in str(err).lower()
        assert "EmptyField" in str(err)
    
    def test_source_text_empty(self):
        """Test source text empty error"""
        err = errors.SourceTextEmpty()
        assert "empty" in str(err).lower()
    
    def test_audio_not_found_error(self):
        """Test audio not found error contains details"""
        err = errors.AudioNotFoundError("hello", "voice123")
        assert "hello" in str(err)
        assert "voice123" in str(err)
        assert err.source_text == "hello"
        assert err.voice == "voice123"
    
    def test_voice_not_found(self):
        """Test voice not found error"""
        voice_data = "EdgeTTS-en-US"
        err = errors.VoiceNotFound(voice_data)
        assert voice_data in str(err)
    
    def test_preset_not_found(self):
        """Test preset not found error"""
        err = errors.PresetNotFound("MyPreset")
        assert "MyPreset" in str(err)
    
    def test_missing_directory(self):
        """Test missing directory error"""
        test_dir = "/nonexistent/path"
        err = errors.MissingDirectory(test_dir)
        assert test_dir in str(err)
    
    def test_text_replacement_error(self):
        """Test text replacement error includes context"""
        err = errors.TextReplacementError("hello", "\\d+", "NUM", "invalid pattern")
        assert "hello" in str(err)
        assert "NUM" in str(err)
        assert "invalid pattern" in str(err)


@pytest.mark.unit
class TestErrorMessages:
    """Test error message quality"""
    
    def test_error_messages_are_user_friendly(self):
        """Verify error messages are clear and helpful"""
        err = errors.CollectionNotOpen()
        msg = str(err)
        assert len(msg) > 20  # Message should be descriptive
        assert "Anki" in msg or "Collection" in msg
    
    def test_error_messages_include_field_names(self):
        """Verify field errors include the problematic field"""
        field = "TranslatedWord"
        err = errors.SourceFieldNotFoundError(field)
        assert field in str(err)


@pytest.mark.unit
class TestErrorCatching:
    """Test error catching patterns"""
    
    def test_all_custom_errors_catchable_as_base(self):
        """Verify all custom errors can be caught as SuperFreeTTSError"""
        errors_to_test = [
            errors.CollectionNotOpen(),
            errors.FieldNotFoundError("test"),
            errors.SourceTextEmpty(),
            errors.VoiceNotFound("test"),
            errors.PresetNotFound("test"),
        ]
        
        for err in errors_to_test:
            with pytest.raises(errors.SuperFreeTTSError):
                raise err
