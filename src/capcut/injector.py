import json
import shutil
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.whisper.aligner import WordTimestamp
from .schema import create_text_material, create_text_segment

class CapCutInjector:
    def inject_data(
        self,
        draft_json: Dict[str, Any],
        audio_path: str,
        duration_seconds: float,
        timestamps: List[WordTimestamp],
        video_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cập nhật nội dung audio, video, text subtitle vào cấu trúc JSON của CapCut draft."""
        duration_us = int(duration_seconds * 1_000_000)
        draft_json["duration"] = duration_us

        # 1. Thay thế Audio voiceover
        audios = draft_json.setdefault("materials", {}).setdefault("audios", [])
        if audios:
            audios[0]["path"] = str(audio_path)
            audios[0]["duration"] = duration_us
        else:
            audio_id = str(uuid.uuid4())
            audios.append({
                "id": audio_id,
                "path": str(audio_path),
                "duration": duration_us,
                "type": "extract_music"
            })

        # 2. Thay thế Video background nếu có
        if video_path:
            videos = draft_json.setdefault("materials", {}).setdefault("videos", [])
            if videos:
                videos[0]["path"] = str(video_path)
                videos[0]["duration"] = duration_us
            else:
                vid_id = str(uuid.uuid4())
                videos.append({
                    "id": vid_id,
                    "path": str(video_path),
                    "duration": duration_us,
                    "type": "video"
                })

        # 3. Cập nhật duration trong các track segments
        tracks = draft_json.setdefault("tracks", [])
        text_track = None
        for track in tracks:
            track_type = track.get("type")
            if track_type in ("audio", "video") and track.get("segments"):
                for seg in track["segments"]:
                    if "target_timerange" in seg:
                        seg["target_timerange"]["duration"] = duration_us
            elif track_type == "text":
                text_track = track

        # Nếu chưa có text track thì tạo mới
        if text_track is None:
            text_track = {
                "id": str(uuid.uuid4()),
                "type": "text",
                "segments": []
            }
            tracks.append(text_track)

        # 4. Inject Subtitle texts theo timestamp
        texts = draft_json.setdefault("materials", {}).setdefault("texts", [])
        texts.clear()
        text_track["segments"] = []

        for wt in timestamps:
            t_id = str(uuid.uuid4())
            s_id = str(uuid.uuid4())
            
            # Thêm text material
            texts.append(create_text_material(t_id, wt.word))
            
            # Thêm segment vào track
            text_track["segments"].append(
                create_text_segment(s_id, t_id, wt.start_us, wt.duration_us)
            )

        return draft_json

    def create_project_from_template(
        self,
        template_dir: Path,
        target_dir: Path,
        audio_path: Path,
        duration_seconds: float,
        timestamps: List[WordTimestamp],
        video_path: Optional[Path] = None
    ) -> Path:
        """Clone template CapCut và inject dữ liệu mới vào draft_content.json."""
        if not template_dir.exists():
            raise FileNotFoundError(f"Template directory '{template_dir}' does not exist.")

        # Copy template sang thư mục target
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(template_dir, target_dir)

        # Tìm file draft
        draft_file = target_dir / "draft_content.json"
        if not draft_file.exists():
            draft_file = target_dir / "draft_info.json"
        
        if not draft_file.exists():
            raise FileNotFoundError(f"Neither draft_content.json nor draft_info.json found in {target_dir}")

        with open(draft_file, "r", encoding="utf-8") as f:
            draft_data = json.load(f)

        updated_data = self.inject_data(
            draft_json=draft_data,
            audio_path=str(audio_path),
            duration_seconds=duration_seconds,
            timestamps=timestamps,
            video_path=str(video_path) if video_path else None
        )

        with open(draft_file, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)

        return target_dir
