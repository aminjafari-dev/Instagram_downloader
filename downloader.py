import os
import sys
import shutil
from typing import Any, Dict, Callable, Optional


def ensure_output_directory(directory_path: str) -> None:
    if not directory_path:
        return
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def has_ffmpeg_installed() -> bool:
    return bool(shutil.which("ffmpeg") or shutil.which("ffmpeg.exe"))


def progress_hook(status: Dict[str, Any]) -> None:
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


def build_ydl_options(
    output_dir: str,
    cookies_file: str | None,
    custom_progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    out_template = os.path.join(output_dir, "%(uploader)s_%(id)s.%(ext)s")
    ffmpeg_available = has_ffmpeg_installed()
    chosen_format = "bestvideo+bestaudio/best" if ffmpeg_available else "best"
    options: Dict[str, Any] = {
        "outtmpl": out_template,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "overwrites": False,
        "restrictfilenames": True,
        "format": chosen_format,
        "retries": 3,
        "progress_hooks": [custom_progress_hook or progress_hook],
    }
    if cookies_file:
        options["cookiefile"] = cookies_file
    return options


def download_instagram_video(
    url: str,
    output_dir: str,
    cookies_file: str | None,
    custom_progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> int:
    try:
        from yt_dlp import YoutubeDL  # type: ignore
    except Exception as import_error:  # pragma: no cover
        print("Error: yt-dlp is not installed. Run: pip install -r requirements.txt", file=sys.stderr)
        print(str(import_error), file=sys.stderr)
        return 2

    ensure_output_directory(output_dir)
    ydl_opts = build_ydl_options(output_dir, cookies_file, custom_progress_hook)

    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])
            return 0 if result == 0 else 1
    except Exception as e:  # pragma: no cover
        print(f"Download failed: {e}", file=sys.stderr)
        return 1


