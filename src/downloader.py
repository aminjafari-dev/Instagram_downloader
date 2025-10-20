import os
import sys
import shutil
from typing import Any, Dict, Callable, Optional, List


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


def read_excel_urls(excel_file_path: str, url_column: str = "url") -> List[str]:
    """
    Read Instagram URLs from an Excel file.
    
    Args:
        excel_file_path: Path to the Excel file
        url_column: Name of the column containing URLs (default: "url")
    
    Returns:
        List of URLs found in the Excel file
    
    Raises:
        Exception: If pandas is not installed or file cannot be read
    """
    try:
        import pandas as pd  # type: ignore
    except ImportError:
        raise Exception("pandas is not installed. Run: pip install pandas openpyxl")
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file_path)
        
        # Check if URL column exists
        if url_column not in df.columns:
            available_columns = ", ".join(df.columns.tolist())
            raise Exception(f"Column '{url_column}' not found. Available columns: {available_columns}")
        
        # Extract URLs and filter out empty/NaN values
        urls = df[url_column].dropna().astype(str).str.strip()
        urls = urls[urls != ""].tolist()
        
        return urls
        
    except Exception as e:
        raise Exception(f"Error reading Excel file: {str(e)}")


def download_videos_from_excel(
    excel_file_path: str,
    output_dir: str,
    cookies_file: str | None,
    url_column: str = "url",
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> Dict[str, int]:
    """
    Download Instagram videos from URLs listed in an Excel file.
    
    Args:
        excel_file_path: Path to the Excel file containing URLs
        output_dir: Directory to save downloaded videos
        cookies_file: Optional cookies file path
        url_column: Name of the column containing URLs (default: "url")
        progress_callback: Optional callback function(current, total, current_url)
    
    Returns:
        Dictionary with 'success' and 'failed' counts
    """
    try:
        # Read URLs from Excel
        urls = read_excel_urls(excel_file_path, url_column)
        
        if not urls:
            return {"success": 0, "failed": 0}
        
        success_count = 0
        failed_count = 0
        total_urls = len(urls)
        
        for i, url in enumerate(urls, 1):
            try:
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(i, total_urls, url)
                
                # Download the video
                result = download_instagram_video(url, output_dir, cookies_file)
                
                if result == 0:
                    success_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                print(f"Error downloading {url}: {e}", file=sys.stderr)
                failed_count += 1
        
        return {"success": success_count, "failed": failed_count}
        
    except Exception as e:
        print(f"Error processing Excel file: {e}", file=sys.stderr)
        return {"success": 0, "failed": 0}


