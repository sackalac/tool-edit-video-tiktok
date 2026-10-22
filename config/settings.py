from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    
    # API Keys
    GEMINI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    PEXELS_API_KEY: str = ""
    
    # CapCut Settings
    CAPCUT_DRAFT_PATH: Path = Path(r"C:\Users\quanvm\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    @property
    def ASSETS_DIR(self) -> Path:
        return self.BASE_DIR / "assets"

    @property
    def AUDIO_DIR(self) -> Path:
        return self.ASSETS_DIR / "audio"

    @property
    def VIDEO_DIR(self) -> Path:
        return self.ASSETS_DIR / "video"

    @property
    def OUTPUT_DIR(self) -> Path:
        return self.BASE_DIR / "output"

    def ensure_directories(self) -> None:
        self.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        self.VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
