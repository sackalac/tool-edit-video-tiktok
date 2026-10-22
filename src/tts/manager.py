from pathlib import Path
from typing import Dict, Optional
from .base import BaseTTSProvider, TTSResult
from .edge_provider import EdgeTTSProvider
from .gemini_provider import GeminiTTSProvider
from .elevenlabs_provider import ElevenLabsProvider

class TTSManager:
    def __init__(self):
        self._providers: Dict[str, BaseTTSProvider] = {
            "edge-tts": EdgeTTSProvider(),
            "gemini": GeminiTTSProvider(),
            "elevenlabs": ElevenLabsProvider(),
        }

    @property
    def providers(self) -> Dict[str, BaseTTSProvider]:
        return self._providers

    def get_provider(self, provider_name: str) -> BaseTTSProvider:
        provider = self._providers.get(provider_name.lower())
        if not provider:
            raise ValueError(
                f"Unsupported TTS provider '{provider_name}'. "
                f"Available providers: {list(self._providers.keys())}"
            )
        return provider

    def generate(
        self,
        text: str,
        output_path: Path,
        provider: str = "edge-tts",
        voice: Optional[str] = None
    ) -> TTSResult:
        prov = self.get_provider(provider)
        return prov.generate(text, output_path, voice)
