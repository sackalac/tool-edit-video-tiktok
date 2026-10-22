from pathlib import Path
from typing import Optional, List, Dict, Any
import edge_tts
from .base import BaseTTSProvider, TTSResult

class EdgeTTSProvider(BaseTTSProvider):
    DEFAULT_VOICE = "vi-VN-HoaiMyNeural"  # Giọng nữ tiếng Việt chuẩn

    async def generate_async(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None
    ) -> TTSResult:
        selected_voice = voice or self.DEFAULT_VOICE
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        communicate = edge_tts.Communicate(text, selected_voice)
        sub_maker = edge_tts.SubMaker()
        
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    sub_maker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

        # Chuyển đổi timestamp từ SubMaker sang format chuẩn
        timestamps: List[Dict[str, Any]] = []
        for (offset, duration), word in zip(sub_maker.offset, [s[2] for s in sub_maker.subs] if hasattr(sub_maker, 'subs') else []):
            start_sec = offset / 10_000_000
            dur_sec = duration / 10_000_000
            timestamps.append({
                "word": word,
                "start": start_sec,
                "end": start_sec + dur_sec
            })

        # Tính toán duration ước tính
        duration = 0.0
        if timestamps:
            duration = timestamps[-1]["end"]
        else:
            # Fallback nếu không có subs
            duration = max(1.0, len(text.split()) * 0.3)

        return TTSResult(
            audio_path=output_path,
            duration=duration,
            timestamps=timestamps
        )
