from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class WordTimestamp:
    word: str
    start: float  # seconds
    end: float    # seconds

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    @property
    def start_us(self) -> int:
        """Thời gian bắt đầu tính bằng microsecond (1s = 1,000,000us cho CapCut)."""
        return int(self.start * 1_000_000)

    @property
    def end_us(self) -> int:
        """Thời gian kết thúc tính bằng microsecond."""
        return int(self.end * 1_000_000)

    @property
    def duration_us(self) -> int:
        """Độ dài tính bằng microsecond."""
        return int(self.duration * 1_000_000)

class SubtitleAligner:
    def __init__(self, model_size: str = "base", device: str = "cuda", compute_type: str = "float16"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
            except Exception:
                # Fallback to CPU if CUDA is unavailable
                from faster_whisper import WhisperModel
                self._model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8"
                )
        return self._model

    def align(self, audio_path: Path) -> List[WordTimestamp]:
        """Bóc tách audio thành danh sách WordTimestamp (cấp độ từ)."""
        model = self._get_model()
        segments, _ = model.transcribe(
            str(audio_path),
            word_timestamps=True,
            language="vi"
        )
        
        result: List[WordTimestamp] = []
        for segment in segments:
            if hasattr(segment, 'words') and segment.words:
                for word_info in segment.words:
                    clean_word = word_info.word.strip()
                    if clean_word:
                        result.append(WordTimestamp(
                            word=clean_word,
                            start=word_info.start,
                            end=word_info.end
                        ))
        return result
