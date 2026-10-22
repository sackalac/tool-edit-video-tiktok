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
                elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                    sub_maker.feed(chunk)

        # Chuyển đổi timestamp từ SubMaker cues sang format chuẩn
        timestamps: List[Dict[str, Any]] = []
        for cue in sub_maker.cues:
            timestamps.append({
                "word": cue.content,
                "start": cue.start.total_seconds(),
                "end": cue.end.total_seconds()
            })

        duration = 0.0
        if timestamps:
            duration = timestamps[-1]["end"]
        else:
            duration = max(1.0, len(text.split()) * 0.3)

        return TTSResult(
            audio_path=output_path,
            duration=duration,
            timestamps=timestamps
        )
