# Auto-Edit Video TikTok Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng hệ thống tự động tạo video TikTok 9:16 từ kịch bản thô với multi-provider TTS (Edge-TTS, Gemini, ElevenLabs), bóc tách phụ đề chữ nhảy karaoke (Whisper/Edge), tải video nền Pexels, inject vào template CapCut PC và tự động export file MP4 thành phẩm.

**Architecture:** Kiến trúc module hóa 100% Python gồm: TTS Provider Adapter, Subtitle Aligner (`faster-whisper` CUDA), Media Preprocessor (`ffmpeg-python` NVENC), CapCut Draft JSON Injector (`draft_content.json`), và GUI Automation Exporter (`pywinauto`). Tất cả được điều phối qua một Pipeline Controller.

**Tech Stack:** Python 3.10+, `edge-tts`, `google-genai`, `elevenlabs`, `faster-whisper`, `ffmpeg-python`, `pywinauto`, `pydantic`, `pytest`.

**Spec:** `docs/superpowers/specs/2026-10-22-auto-edit-video-tiktok-design.md`

## Global Constraints

- Chạy trên Windows 10/11 với GPU NVIDIA RTX 3060 (CUDA 12.x).
- Đơn vị thời gian trong CapCut draft tính bằng microsecond ($1s = 1.000.000\mu s$).
- Các module phải độc lập, có thể test riêng lẻ (TDD).
- Không tự động đăng TikTok; chỉ xuất ra `output/` kèm file `.txt` metadata.

## Review Focus

1. **Edge-TTS / Gemini / ElevenLabs Network Timeout:** Xử lý mất mạng hoặc quota hết hạn mà không làm crash tiến trình.
2. **CapCut microsecond precision overflow:** Tránh lệch đồng bộ âm thanh và chữ karaoke khi video dài.
3. **CapCut Draft Corrupt Risk:** Thiếu UUID hoặc cấu trúc tracks không khớp khiến CapCut báo lỗi file draft.
4. **FFmpeg GPU NVENC Fallback:** Tự động fallback về CPU `libx264` nếu driver GPU hoặc NVENC bận.
5. **pywinauto Window Focus Loss:** Xử lý trường hợp cửa sổ CapCut bị che khuất hoặc chưa kịp render xong.

---

### Task 1: Project Scaffolding & Configuration Setup

**Files:**
- Create: `requirements.txt`
- Create: `config/settings.py`
- Create: `config/__init__.py`
- Create: `src/__init__.py`
- Test: `tests/test_settings.py`

**Interfaces:**
- Produces: `config.settings.Settings` class (chứa đường dẫn assets, output, template CapCut, API keys).

- [ ] **Step 1: Write the failing test for Settings**
```python
# tests/test_settings.py
from config.settings import Settings

def test_settings_default_paths(tmp_path):
    settings = Settings(base_dir=tmp_path)
    assert settings.ASSETS_DIR == tmp_path / "assets"
    assert settings.OUTPUT_DIR == tmp_path / "output"
    assert settings.AUDIO_DIR == tmp_path / "assets" / "audio"
    assert settings.VIDEO_DIR == tmp_path / "assets" / "video"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_settings.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'config.settings'`

- [ ] **Step 3: Implement `requirements.txt` & `config/settings.py`**
Tạo file cấu hình dùng `pydantic-settings` hoặc `dataclass` tự động tạo các thư mục `output`, `assets/audio`, `assets/video` nếu chưa tồn tại.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_settings.py`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add requirements.txt config/ tests/test_settings.py
git commit -m "chore: setup project scaffolding and settings"
```

---

### Task 2: Multi-Provider TTS Engine

**Files:**
- Create: `src/tts/base.py`
- Create: `src/tts/edge_provider.py`
- Create: `src/tts/gemini_provider.py`
- Create: `src/tts/elevenlabs_provider.py`
- Create: `src/tts/manager.py`
- Test: `tests/test_tts.py`

**Interfaces:**
- Produces: `TTSManager.generate(text: str, provider: str, voice: str | None = None) -> TTSResult`
- `TTSResult` chứa: `audio_path: Path`, `timestamps: list[dict]` (nếu có từ edge-tts), `duration: float`.

- [ ] **Step 1: Write test for TTSManager interface**
```python
# tests/test_tts.py
from src.tts.manager import TTSManager
from src.tts.base import BaseTTSProvider, TTSResult

def test_tts_manager_factory():
    manager = TTSManager()
    assert "edge-tts" in manager.providers
    assert "gemini" in manager.providers
    assert "elevenlabs" in manager.providers
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_tts.py`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement BaseTTSProvider & TTS Providers**
Triển khai `EdgeTTSProvider` (dùng `edge_tts.Communicate`), `GeminiTTSProvider`, `ElevenLabsProvider`, và `TTSManager`.

- [ ] **Step 4: Run test to verify unit tests pass**
Run: `pytest tests/test_tts.py`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add src/tts/ tests/test_tts.py
git commit -m "feat: implement multi-provider TTS engine"
```

---

### Task 3: Word-Level Subtitle Timestamping (`faster-whisper`)

**Files:**
- Create: `src/whisper/aligner.py`
- Test: `tests/test_whisper.py`

**Interfaces:**
- Consumes: `audio_path: Path`
- Produces: `SubtitleAligner.align(audio_path: Path) -> list[WordTimestamp]`
  (`WordTimestamp`: `word: str`, `start: float`, `end: float`).

- [ ] **Step 1: Write test for SubtitleAligner data structures & parsing**
```python
# tests/test_whisper.py
from src.whisper.aligner import SubtitleAligner, WordTimestamp

def test_word_timestamp_schema():
    wt = WordTimestamp(word="Xin chào", start=0.0, end=0.45)
    assert wt.word == "Xin chào"
    assert wt.duration == 0.45
    assert wt.start_us == 0
    assert wt.end_us == 450000
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_whisper.py`
Expected: FAIL

- [ ] **Step 3: Implement `SubtitleAligner` with `faster-whisper`**
Dùng model `faster-whisper` (`base` hoặc `small`), device `cuda` (fallback `cpu`), compute_type `float16`, word_timestamps=True.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_whisper.py`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add src/whisper/ tests/test_whisper.py
git commit -m "feat: implement word-level subtitle alignment"
```

---

### Task 4: Media Fetching & FFmpeg NVENC Preprocessing

**Files:**
- Create: `src/media/pexels.py`
- Create: `src/media/preprocessor.py`
- Test: `tests/test_media.py`

**Interfaces:**
- Produces: `PexelsClient.search_and_download(keyword: str, min_duration: float) -> Path`
- Produces: `MediaPreprocessor.prepare_background(input_video: Path, target_duration: float, output_path: Path) -> Path` (scale 1080x1920 9:16, trim or loop).

- [ ] **Step 1: Write test for media preprocessor command generation**
```python
# tests/test_media.py
from src.media.preprocessor import MediaPreprocessor

def test_generate_ffmpeg_command():
    processor = MediaPreprocessor(use_gpu=True)
    cmd = processor.build_trim_and_scale_command(
        input_path="assets/video/raw.mp4",
        output_path="assets/video/processed.mp4",
        duration=15.5
    )
    assert "h264_nvenc" in cmd
    assert "scale=1080:1920" in cmd or "crop=" in cmd
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_media.py`
Expected: FAIL

- [ ] **Step 3: Implement `PexelsClient` and `MediaPreprocessor`**
Thực thi FFmpeg subprocess với GPU acceleration `h264_nvenc`, hỗ trợ tự động fallback sang `libx264` nếu GPU bận.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_media.py`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add src/media/ tests/test_media.py
git commit -m "feat: implement media fetcher and ffmpeg preprocessor"
```

---

### Task 5: CapCut Template Clone & JSON Hacking (`draft_content.json`)

**Files:**
- Create: `src/capcut/schema.py`
- Create: `src/capcut/injector.py`
- Test: `tests/test_capcut.py`

**Interfaces:**
- Consumes: `template_dir: Path`, `audio_path: Path`, `video_path: Path`, `timestamps: list[WordTimestamp]`
- Produces: `CapCutInjector.create_project(project_id: str, audio_path: Path, video_path: Path, timestamps: list[WordTimestamp]) -> Path` (đường dẫn project CapCut mới được inject sẵn).

- [ ] **Step 1: Write test for CapCut JSON injection logic**
```python
# tests/test_capcut.py
import json
from src.capcut.injector import CapCutInjector
from src.whisper.aligner import WordTimestamp

def test_inject_audio_and_duration():
    mock_draft = {
        "duration": 5000000,
        "materials": {"audios": [], "texts": [], "videos": []},
        "tracks": []
    }
    injector = CapCutInjector()
    updated = injector.inject_data(
        draft_json=mock_draft,
        audio_path="assets/audio/voice.mp3",
        duration_seconds=12.5,
        timestamps=[WordTimestamp(word="Hello", start=0.0, end=1.0)]
    )
    assert updated["duration"] == 12500000  # 12.5 * 10^6 microseconds
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_capcut.py`
Expected: FAIL

- [ ] **Step 3: Implement `CapCutInjector`**
Clone template folder, parse `draft_content.json`, replace audio/video/text elements, calculate microseconds, sinh UUID cho materials/tracks.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_capcut.py`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add src/capcut/ tests/test_capcut.py
git commit -m "feat: implement capcut draft json injector"
```

---

### Task 6: Exporter Automation & Pipeline Controller

**Files:**
- Create: `src/exporter/capcut_exporter.py`
- Create: `src/pipeline.py`
- Create: `app.py`
- Test: `tests/test_pipeline.py`

**Interfaces:**
- Produces: `VideoPipeline.run(script_text: str, tts_provider: str = "edge-tts") -> Path`
- `app.py`: CLI / Web runner cho người dùng nhập kịch bản và nhận video thành phẩm.

- [ ] **Step 1: Write test for Pipeline execution flow with mocks**
```python
# tests/test_pipeline.py
from unittest.mock import MagicMock
from src.pipeline import VideoPipeline

def test_pipeline_dry_run():
    pipeline = VideoPipeline(dry_run=True)
    result = pipeline.run(script_text="Thử nghiệm video TikTok", tts_provider="edge-tts")
    assert result["status"] == "READY_FOR_EXPORT"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_pipeline.py`
Expected: FAIL

- [ ] **Step 3: Implement `CapCutExporter` (`pywinauto`), `VideoPipeline`, and `app.py`**
Tạo pipeline kết nối từ Kịch bản -> TTS -> Subtitle -> Background Video -> CapCut Inject -> Export MP4 -> Tạo `VID_xxx_info.txt`.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_pipeline.py`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add src/exporter/ src/pipeline.py app.py tests/test_pipeline.py
git commit -m "feat: implement exporter and end-to-end pipeline runner"
```
