from pathlib import Path
from config.settings import Settings

def test_settings_default_paths(tmp_path):
    settings = Settings(BASE_DIR=tmp_path)
    assert settings.ASSETS_DIR == tmp_path / "assets"
    assert settings.OUTPUT_DIR == tmp_path / "output"
    assert settings.AUDIO_DIR == tmp_path / "assets" / "audio"
    assert settings.VIDEO_DIR == tmp_path / "assets" / "video"

def test_settings_ensure_dirs_created(tmp_path):
    settings = Settings(BASE_DIR=tmp_path)
    settings.ensure_directories()
    assert (tmp_path / "assets" / "audio").exists()
    assert (tmp_path / "assets" / "video").exists()
    assert (tmp_path / "output").exists()
