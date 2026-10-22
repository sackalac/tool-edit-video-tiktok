import pytest
from pathlib import Path
from src.tts.base import BaseTTSProvider, TTSResult
from src.tts.manager import TTSManager

def test_tts_manager_registered_providers():
    manager = TTSManager()
    assert "edge-tts" in manager.providers
    assert "gemini" in manager.providers
    assert "elevenlabs" in manager.providers

def test_tts_result_dataclass():
    res = TTSResult(
        audio_path=Path("assets/audio/test.mp3"),
        timestamps=[{"word": "Xin", "start": 0.0, "end": 0.2}],
        duration=0.5
    )
    assert res.duration == 0.5
    assert len(res.timestamps) == 1
    assert res.audio_path.name == "test.mp3"

def test_unknown_provider_raises_error():
    manager = TTSManager()
    with pytest.raises(ValueError, match="Unsupported TTS provider"):
        manager.get_provider("non_existent_provider")
