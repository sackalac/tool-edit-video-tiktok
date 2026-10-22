import os
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any

class PexelsClient:
    BASE_URL = "https://api.pexels.com/videos"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY", "")

    def search_videos(
        self,
        query: str,
        orientation: str = "portrait",
        per_page: int = 5
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm video stock từ Pexels API chuẩn dọc 9:16."""
        if not self.api_key:
            raise ValueError("PEXELS_API_KEY is required to search and download stock videos.")

        headers = {"Authorization": self.api_key}
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": per_page
        }
        response = requests.get(f"{self.BASE_URL}/search", headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("videos", [])

    def download_video(self, video_data: Dict[str, Any], output_path: Path) -> Path:
        """Tải video chất lượng HD/FHD về thư mục output."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        video_files = video_data.get("video_files", [])
        if not video_files:
            raise ValueError("No downloadable video files found in video data.")

        # Chọn video có độ phân giải phù hợp nhất (HD/1080p)
        sorted_files = sorted(
            video_files,
            key=lambda x: x.get("width", 0) * x.get("height", 0),
            reverse=True
        )
        download_url = sorted_files[0]["link"]

        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path
