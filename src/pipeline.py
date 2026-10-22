import uuid
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from config.settings import Settings
from src.tts.manager import TTSManager
from src.whisper.aligner import SubtitleAligner, WordTimestamp
from src.media.preprocessor import MediaPreprocessor
from src.media.pexels import PexelsClient
from src.capcut.injector import CapCutInjector
from src.exporter.capcut_exporter import CapCutExporter

class VideoPipeline:
    def __init__(self, base_dir: Optional[Path] = None, dry_run: bool = False):
        self.settings = Settings(BASE_DIR=base_dir) if base_dir else Settings()
        self.settings.ensure_directories()
        self.dry_run = dry_run
        
        self.tts_manager = TTSManager()
        self.aligner = SubtitleAligner()
        self.preprocessor = MediaPreprocessor(use_gpu=True)
        self.pexels_client = PexelsClient(api_key=self.settings.PEXELS_API_KEY)
        self.injector = CapCutInjector()
        self.exporter = CapCutExporter()

    def run(
        self,
        script_text: str,
        tts_provider: str = "edge-tts",
        voice: Optional[str] = None,
        title: Optional[str] = None,
        video_keyword: Optional[str] = None,
        local_video_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Điều phối toàn bộ quy trình sản xuất video TikTok."""
        video_id = f"VID_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        video_title = title or f"TikTok Video {video_id}"

        # 1. Sinh Voiceover
        audio_output = self.settings.AUDIO_DIR / f"{video_id}.mp3"
        tts_res = self.tts_manager.generate(
            text=script_text,
            output_path=audio_output,
            provider=tts_provider,
            voice=voice
        )
        duration = tts_res.duration

        # 2. Xử lý Subtitle Timestamps
        word_timestamps: List[WordTimestamp] = []
        if tts_res.timestamps:
            # Dùng trực tiếp timestamp từ TTS (Edge-TTS)
            for ts in tts_res.timestamps:
                word_timestamps.append(WordTimestamp(
                    word=ts["word"],
                    start=ts["start"],
                    end=ts["end"]
                ))
        elif not self.dry_run:
            # Fallback dùng Whisper nếu TTS không có sẵn timestamp (Gemini / ElevenLabs)
            word_timestamps = self.aligner.align(audio_output)
        else:
            word_timestamps = [
                WordTimestamp(word=w, start=i*0.3, end=(i+1)*0.3)
                for i, w in enumerate(script_text.split()[:5])
            ]

        # 3. Chuẩn bị Video nền
        bg_video_path = None
        if local_video_path and Path(local_video_path).exists():
            bg_video_path = Path(local_video_path)
        elif video_keyword and self.settings.PEXELS_API_KEY and not self.dry_run:
            try:
                videos = self.pexels_client.search_videos(video_keyword)
                if videos:
                    downloaded = self.settings.VIDEO_DIR / f"raw_{video_id}.mp4"
                    self.pexels_client.download_video(videos[0], downloaded)
                    bg_video_path = self.settings.VIDEO_DIR / f"proc_{video_id}.mp4"
                    self.preprocessor.process_background_video(downloaded, bg_video_path, duration)
            except Exception as e:
                print(f"[VideoPipeline] Pexels download warning: {e}")

        # 4. Tạo file metadata (Title, Caption, Hashtags)
        info_file = self.settings.OUTPUT_DIR / f"{video_id}_info.txt"
        with open(info_file, "w", encoding="utf-8") as f:
            f.write(f"TIÊU ĐỀ: {video_title}\n\n")
            f.write(f"NỘI DUNG / CAPTION:\n{script_text}\n\n")
            f.write("HASHTAGS:\n#fyp #trending #viral #xuhuong #xuhuongtiktok\n")

        # 5. CapCut Injection & Export
        output_mp4 = self.settings.OUTPUT_DIR / f"{video_id}.mp4"
        project_dir = self.settings.CAPCUT_DRAFT_PATH / video_id

        if not self.dry_run:
            template_dir = self.settings.BASE_DIR / "assets" / "templates" / "default"
            if template_dir.exists():
                self.injector.create_project_from_template(
                    template_dir=template_dir,
                    target_dir=project_dir,
                    audio_path=audio_output,
                    duration_seconds=duration,
                    timestamps=word_timestamps,
                    video_path=bg_video_path
                )
                self.exporter.export_project(project_dir, output_mp4)

        return {
            "video_id": video_id,
            "title": video_title,
            "duration": duration,
            "audio_path": str(audio_output),
            "timestamps": [{"word": wt.word, "start": wt.start, "end": wt.end} for wt in word_timestamps],
            "metadata_file": str(info_file),
            "output_video": str(output_mp4),
            "status": "READY_FOR_EXPORT" if self.dry_run else "COMPLETED"
        }
