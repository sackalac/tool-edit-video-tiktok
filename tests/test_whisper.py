import pytest
from pathlib import Path
from src.whisper.aligner import SubtitleAligner, WordTimestamp

def test_word_timestamp_schema_and_microseconds():
    wt = WordTimestamp(word="Xin chào", start=1.5, end=2.0)
    assert wt.word == "Xin chào"
    assert wt.start == 1.5
    assert wt.end == 2.0
    assert wt.duration == 0.5
    assert wt.start_us == 1_500_000
    assert wt.end_us == 2_000_000
    assert wt.duration_us == 500_000

def test_subtitle_aligner_instantiation():
    aligner = SubtitleAligner(model_size="tiny", device="cpu")
    assert aligner.model_size == "tiny"
    assert aligner.device == "cpu"
