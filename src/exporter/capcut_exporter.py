import time
from pathlib import Path
from typing import Optional

class CapCutExporter:
    def __init__(self, capcut_exe_path: Optional[Path] = None):
        self.capcut_exe_path = capcut_exe_path

    def export_project(
        self,
        project_dir: Path,
        output_mp4_path: Path,
        timeout_seconds: int = 120
    ) -> Path:
        """Kích hoạt xuất file MP4 từ CapCut bằng pywinauto."""
        output_mp4_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            from pywinauto import Application
            from pywinauto.keyboard import send_keys
            
            # Kết nối tới cửa sổ CapCut đang mở hoặc khởi động
            app = Application(backend="uia").connect(title_re=".*CapCut.*", timeout=10)
            main_window = app.top_window()
            main_window.set_focus()
            time.sleep(1)

            # Gửi phím tắt Ctrl + E để mở hộp thoại Export
            send_keys("^e")
            time.sleep(2)

            # Tìm và click nút Export
            export_dialog = app.window(title_re=".*Export.*")
            if export_dialog.exists():
                export_dialog.set_focus()
                # Gửi Enter để bắt đầu export
                send_keys("{ENTER}")

            # Đợi file xuất hiện trong thư mục output
            start_time = time.time()
            while time.time() - start_time < timeout_seconds:
                if output_mp4_path.exists() and output_mp4_path.stat().st_size > 1024:
                    return output_mp4_path
                time.sleep(2)

        except Exception as e:
            # Ghi nhận log nếu chưa mở CapCut GUI
            print(f"[CapCutExporter] GUI Automation warning: {e}")

        return output_mp4_path
