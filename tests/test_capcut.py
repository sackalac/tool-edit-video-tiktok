import json
from pathlib import Path
from src.capcut.injector import CapCutInjector
from src.whisper.aligner import WordTimestamp

def test_inject_audio_and_duration():
    mock_draft = {
        "duration": 5000000,
        "materials": {
            "audios": [{"id": "audio_1", "path": "old_audio.mp3", "duration": 5000000}],
            "texts": [],
            "videos": [{"id": "vid_1", "path": "old_bg.mp4", "duration": 5000000}]
        },
        "tracks": [
            {"id": "track_audio", "type": "audio", "segments": [{"material_id": "audio_1", "target_timerange": {"duration": 5000000}}]},
            {"id": "track_video", "type": "video", "segments": [{"material_id": "vid_1", "target_timerange": {"duration": 5000000}}]},
            {"id": "track_text", "type": "text", "segments": []}
        ]
    }
    
    injector = CapCutInjector()
    timestamps = [
        WordTimestamp(word="Xin", start=0.0, end=0.3),
        WordTimestamp(word="chào", start=0.3, end=0.6)
    ]
    
    updated = injector.inject_data(
        draft_json=mock_draft,
        audio_path="assets/audio/voice.mp3",
        duration_seconds=10.0,
        timestamps=timestamps,
        video_path="assets/video/bg.mp4"
    )
    
    # 10s = 10,000,000 microseconds
    assert updated["duration"] == 10_000_000
    assert updated["materials"]["audios"][0]["path"] == "assets/audio/voice.mp3"
    assert updated["materials"]["videos"][0]["path"] == "assets/video/bg.mp4"
    assert len(updated["materials"]["texts"]) == 2
    assert updated["materials"]["texts"][0]["content"] == "Xin"
    assert updated["materials"]["texts"][1]["content"] == "chào"
