from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional

@dataclass
class TTSResult:
    audio_path: Path
    duration: float
    timestamps: List[Dict[str, Any]] = field(default_factory=list)

class BaseTTSProvider(ABC):
    @abstractmethod
    async def generate_async(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None
    ) -> TTSResult:
        """Sinh file audio bất đồng bộ từ text."""
        pass

    def generate(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None
    ) -> TTSResult:
        """Sync wrapper cho sinh audio."""
        import asyncio
        return asyncio.run(self.generate_async(text, output_path, voice))
