import subprocess
from pathlib import Path
from typing import List, Union

class MediaPreprocessor:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu

    def build_trim_and_scale_command(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        duration: float,
        target_width: int = 1080,
        target_height: int = 1920
    ) -> List[str]:
        """Tạo câu lệnh FFmpeg để cắt ghép và chuẩn hóa video về tỉ lệ 9:16."""
        encoder = "h264_nvenc" if self.use_gpu else "libx264"
        
        # Filter: Scale và crop chuẩn 9:16
        vf_filter = (
            f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase,"
            f"crop={target_width}:{target_height}"
        )
        
        cmd = [
            "ffmpeg",
            "-y",  # Ghi đè file nếu đã tồn tại
            "-stream_loop", "-1",  # Lặp lại nếu video ngắn hơn audio
            "-i", str(input_path),
            "-vf", vf_filter,
            "-t", str(duration),
            "-c:v", encoder,
            "-preset", "p4" if self.use_gpu else "medium",
            "-an",  # Tắt tiếng video gốc để tránh lẫn với voiceover/nhạc nền
            str(output_path)
        ]
        return cmd

    def process_background_video(
        self,
        input_path: Path,
        output_path: Path,
        duration: float
    ) -> Path:
        """Chạy FFmpeg để xử lý video nền, tự động fallback CPU nếu GPU lỗi."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = self.build_trim_and_scale_command(input_path, output_path, duration)
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            if self.use_gpu:
                # Fallback to CPU libx264
                self.use_gpu = False
                cpu_cmd = self.build_trim_and_scale_command(input_path, output_path, duration)
                subprocess.run(cpu_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                raise
        return output_path
