from pathlib import Path
from unittest.mock import MagicMock, patch
from src.pipeline import VideoPipeline
from src.tts.base import TTSResult
from src.whisper.aligner import WordTimestamp

def test_pipeline_dry_run(tmp_path):
    pipeline = VideoPipeline(base_dir=tmp_path, dry_run=True)
    
    # Mock TTS
    mock_tts_result = TTSResult(
        audio_path=tmp_path / "assets" / "audio" / "test.mp3",
        duration=3.0,
        timestamps=[
            {"word": "Xin", "start": 0.0, "end": 0.5},
            {"word": "chào", "start": 0.5, "end": 1.0}
        ]
    )
    
    with patch.object(pipeline.tts_manager, "generate", return_value=mock_tts_result):
        result = pipeline.run(
            script_text="Xin chào các bạn đã đến với kênh",
            tts_provider="edge-tts",
            title="Video Chao Mung"
        )
        
        assert result["status"] == "READY_FOR_EXPORT"
        assert result["duration"] == 3.0
        assert "Xin" in [w["word"] for w in result["timestamps"]]
        assert (tmp_path / "output" / f"{result['video_id']}_info.txt").exists()
