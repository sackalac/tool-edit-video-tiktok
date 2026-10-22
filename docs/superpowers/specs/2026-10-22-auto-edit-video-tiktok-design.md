# Design Doc: Hệ thống Auto-Edit Video TikTok (Local Pipeline)

- **Date:** 2026-10-22
- **Author:** quanvm & Antigravity Agent
- **Target OS:** Windows 10/11 (NVIDIA RTX 3060 CUDA)
- **Status:** Proposed

---

## 1. Mục tiêu (Goals & Non-Goals)

### Goals
- Xây dựng pipeline tự động hóa tạo video TikTok dạng dọc 9:16 từ văn bản/kịch bản thô.
- Hỗ trợ đa dạng nguồn giọng đọc (Multi-provider TTS): `edge-tts` (miễn phí), `gemini` (cảm xúc), `elevenlabs` (điện ảnh, voice clone).
- Tự động đồng bộ phụ đề nhảy chữ karaoke cấp độ từ (word-level timestamps) qua `faster-whisper` chạy trên RTX 3060 GPU.
- Tận dụng template CapCut PC có sẵn để giữ lại hiệu ứng đẹp, animation và transition thông qua kỹ thuật "JSON Hacking" vào `draft_content.json`.
- Tự động hóa khâu Export dự án CapCut thành file MP4 hoàn chỉnh bằng `pywinauto`.
- Sinh kèm file metadata (tiêu đề, caption, hashtag gợi ý).

### Non-Goals
- Tự động upload lên TikTok (người dùng sẽ chủ động đăng tay để an toàn cho tài khoản).

---

## 2. Kiến trúc & Công nghệ (Tech Stack)

- **Ngôn ngữ:** Python 3.10+
- **Môi trường & Phần cứng:** Windows 10/11, CUDA 12.x, NVIDIA GeForce RTX 3060 (12GB VRAM).
- **TTS:**
  - `edge-tts` (Free, giọng `vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural`, word boundaries native).
  - `google-genai` (Gemini 2.0 Flash Audio).
  - `elevenlabs` (ElevenLabs API v1 / Multilingual v2).
- **AI Subtitle / Timestamp:** `faster-whisper` (CTranslate2 + cuBLAS/cuDNN).
- **Media Preprocessing:** `ffmpeg-python` (NVENC: `h264_nvenc`).
- **Stock Media API:** `requests` gọi Pexels API (chọn video dọc 9:16 theo từ khóa kịch bản) hoặc lấy từ kho local `assets/video/`.
- **CapCut Injection:** Python `json` + `uuid` can thiệp `draft_content.json`.
- **GUI Automation:** `pywinauto` (UIA backend) kích hoạt phím tắt `Ctrl + E` và điều khiển hộp thoại Export của CapCut.
- **Database & Queue:** SQLite + Python queue/dispatcher.

---

## 3. Quy trình thực thi (Data Pipeline)

```
[Kịch bản Text / Topic]
        │
        ▼
[1. Voice Generator] ───(edge-tts / gemini / elevenlabs)───► Audio File (.mp3/.wav)
        │
        ▼
[2. Subtitle Align] ───(faster-whisper / native edge-tts)──► Word-level Timestamps JSON
        │
        ▼
[3. Media Fetcher] ───(Pexels API / Local Assets) + FFmpeg NVENC ──► Trimmed Background Video
        │
        ▼
[4. CapCut Injector] ───(Clone Template + Update draft_content.json) ──► CapCut Ready Project
        │
        ▼
[5. CapCut Exporter] ───(pywinauto Trigger Ctrl+E) ──► output/VID_xxx.mp4 + VID_xxx_info.txt
```

---

## 4. Kế hoạch triển khai từng bước (Milestones)

1. **Phase 1: Project Setup & TTS Multi-provider Engine**
   - Thiết lập cấu trúc thư mục, môi trường virtualenv, `requirements.txt`.
   - Viết module `tts_manager` hỗ trợ `edge-tts`, `gemini`, `elevenlabs`.
   - Tích hợp `faster-whisper` chạy trên GPU RTX 3060 để xuất mảng timestamp chuẩn `[{"word": "...", "start": 0.0, "end": 0.2}]`.

2. **Phase 2: Media Fetcher & Preprocessing (FFmpeg NVENC)**
   - Viết module kết nối Pexels API tải video nền 9:16 theo kịch bản.
   - Viết script FFmpeg cắt ghép (trim/scale) video khớp chính xác với thời lượng voiceover.

3. **Phase 3: CapCut Draft JSON Injector**
   - Phân tích template mẫu của người dùng (`draft_content.json`).
   - Xây dựng module nhân bản project và thay thế: `duration`, audio path, video path, inject karaoke text tokens với animation tracks.

4. **Phase 4: Auto Exporter (`pywinauto`) & Pipeline Runner**
   - Tự động mở CapCut, tương tác nút Export và theo dõi file hoàn tất trong thư mục `output/`.
   - Sinh file caption, hashtag gợi ý.
