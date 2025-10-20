import argparse
import os
import sys
import shutil
from typing import Any, Dict


def ensure_output_directory(directory_path: str) -> None:
    if not directory_path:
        return
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def has_ffmpeg_installed() -> bool:
    # Check availability of ffmpeg on PATH
    return bool(shutil.which("ffmpeg") or shutil.which("ffmpeg.exe"))


def build_ydl_options(output_dir: str, cookies_file: str | None) -> Dict[str, Any]:
    out_template = os.path.join(output_dir, "%(uploader)s_%(id)s.%(ext)s")
    ffmpeg_available = has_ffmpeg_installed()
    # If ffmpeg is missing, prefer a single-file format to avoid merge step
    chosen_format = "bestvideo+bestaudio/best" if ffmpeg_available else "best"
    options: Dict[str, Any] = {
        "outtmpl": out_template,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "overwrites": False,
        "restrictfilenames": True,
        # Instagram often provides a single muxed format; fallback to single-file when ffmpeg is missing.
        "format": chosen_format,
        # Retry a few times for transient network issues.
        "retries": 3,
        # Progress output via hook
        "progress_hooks": [progress_hook],
    }
    if cookies_file:
        options["cookiefile"] = cookies_file
    return options


def progress_hook(status: Dict[str, Any]) -> None:
    # Minimal, readable progress messages
    if status.get("status") == "downloading":
        total = status.get("total_bytes") or status.get("total_bytes_estimate")
        downloaded = status.get("downloaded_bytes")
        if total and downloaded:
            pct = downloaded / total * 100
            sys.stdout.write(f"\rDownloading: {pct:5.1f}% ")
            sys.stdout.flush()
    elif status.get("status") == "finished":
        sys.stdout.write("\rDownloading: 100.0%\n")
        sys.stdout.flush()


def download_instagram_video(url: str, output_dir: str, cookies_file: str | None) -> int:
    try:
        from yt_dlp import YoutubeDL  # type: ignore
    except Exception as import_error:  # pragma: no cover
        print("Error: yt-dlp is not installed. Run: pip install -r requirements.txt", file=sys.stderr)
        print(str(import_error), file=sys.stderr)
        return 2

    ensure_output_directory(output_dir)
    ydl_opts = build_ydl_options(output_dir, cookies_file)

    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])
            return 0 if result == 0 else 1
    except Exception as e:  # pragma: no cover
        print(f"Download failed: {e}", file=sys.stderr)
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Instagram video/Reel using yt-dlp",
    )
    parser.add_argument("url", help="Instagram video/Reel URL")
    parser.add_argument(
        "-o",
        "--output",
        dest="output_dir",
        default=os.path.join(os.getcwd(), "downloads"),
        help="Output directory (default: ./downloads)",
    )
    parser.add_argument(
        "-c",
        "--cookies",
        dest="cookies_file",
        default=None,
        help="Path to cookies.txt file (optional, useful if login is required)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    exit_code = download_instagram_video(args.url, args.output_dir, args.cookies_file)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


