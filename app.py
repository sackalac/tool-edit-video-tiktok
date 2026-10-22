import argparse
import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.pipeline import VideoPipeline

def main():
    parser = argparse.ArgumentParser(description="Tool Tu Dong Tao Video TikTok tu Kich Ban")
    parser.add_argument("--script", "-s", type=str, help="Van ban kich ban truc tiep")
    parser.add_argument("--file", "-f", type=str, help="Duong dan file .txt chua kich ban")
    parser.add_argument("--provider", "-p", type=str, default="edge-tts", choices=["edge-tts", "gemini", "elevenlabs"], help="Nguon giong doc AI")
    parser.add_argument("--voice", "-v", type=str, default=None, help="Ten giong doc cu the")
    parser.add_argument("--keyword", "-k", type=str, default=None, help="Tu khoa tim video nen Pexels")
    parser.add_argument("--video", type=str, default=None, help="Duong dan file video nen co san")
    parser.add_argument("--title", "-t", type=str, default=None, help="Tieu de video")
    parser.add_argument("--dry-run", action="store_true", help="Chay thu khong mo CapCut GUI")

    args = parser.parse_args()

    script_text = ""
    if args.script:
        script_text = args.script
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[Loi] Khong tim thay file kich ban: {file_path}")
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            script_text = f.read().strip()
    else:
        print("\n=== TOOL AUTO-EDIT VIDEO TIKTOK ===")
        print("Nhap noi dung kich ban video (nhan Enter 2 lan de ket thuc):")
        lines = []
        while True:
            try:
                line = input()
                if not line:
                    break
                lines.append(line)
            except EOFError:
                break
        script_text = "\n".join(lines).strip()

    if not script_text:
        print("[Loi] Kich ban khong duoc de trong!")
        sys.exit(1)

    print(f"\n[1/4] Dang khoi dong Pipeline (TTS Provider: {args.provider})...")
    pipeline = VideoPipeline(dry_run=args.dry_run)

    print("[2/4] Dang sinh giong doc va boc tach chu nhay karaoke...")
    result = pipeline.run(
        script_text=script_text,
        tts_provider=args.provider,
        voice=args.voice,
        title=args.title,
        video_keyword=args.keyword,
        local_video_path=Path(args.video) if args.video else None
    )

    print("\n[3/4] Xu ly hoan tat!")
    print(f"- Video ID: {result['video_id']}")
    print(f"- Thoi luong: {result['duration']:.2f} giay")
    print(f"- Audio Voiceover: {result['audio_path']}")
    print(f"- File Caption/Hashtags: {result['metadata_file']}")
    print(f"- Video thanh pham: {result['output_video']}")
    print(f"- Trang thai: {result['status']}")
    print("\nBan co the mo file info.txt de copy caption va keo tha video len TikTok!")

if __name__ == "__main__":
    main()
