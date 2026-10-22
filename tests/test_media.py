import pytest
from pathlib import Path
from src.media.preprocessor import MediaPreprocessor
from src.media.pexels import PexelsClient

def test_generate_ffmpeg_command_gpu():
    processor = MediaPreprocessor(use_gpu=True)
    cmd = processor.build_trim_and_scale_command(
        input_path="assets/video/raw.mp4",
        output_path="assets/video/processed.mp4",
        duration=15.5
    )
    cmd_str = " ".join(cmd)
    assert "h264_nvenc" in cmd_str
    assert "1080:1920" in cmd_str
    assert "-t 15.5" in cmd_str

def test_generate_ffmpeg_command_cpu_fallback():
    processor = MediaPreprocessor(use_gpu=False)
    cmd = processor.build_trim_and_scale_command(
        input_path="assets/video/raw.mp4",
        output_path="assets/video/processed.mp4",
        duration=10.0
    )
    cmd_str = " ".join(cmd)
    assert "libx264" in cmd_str
    assert "1080:1920" in cmd_str

def test_pexels_client_missing_api_key():
    client = PexelsClient(api_key="")
    with pytest.raises(ValueError, match="PEXELS_API_KEY is required"):
        client.search_videos("nature")
