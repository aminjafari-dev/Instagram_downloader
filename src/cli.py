import argparse
import os
import sys

from .downloader import download_instagram_video
from .page_downloader import download_profile_videos, print_download_summary, extract_username_from_url

try:
    from .gui import DownloaderGUI  # type: ignore
    GUI_AVAILABLE = True
except Exception:
    DownloaderGUI = None  # type: ignore
    GUI_AVAILABLE = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Instagram videos using yt-dlp")
    parser.add_argument("url", nargs="?", help="Instagram video/Reel URL or profile URL")
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
    parser.add_argument(
        "--page",
        action="store_true",
        help="Download all videos from Instagram profile (use with profile URL)",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=50,
        help="Maximum number of videos to download from profile (default: 50)",
    )
    parser.add_argument("--gui", action="store_true", help="Launch the graphical interface")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.gui or not args.url:
        if not GUI_AVAILABLE:
            print("GUI is unavailable in this environment.", file=sys.stderr)
            sys.exit(3)
        DownloaderGUI().run()
        return

    # Check if it's a profile URL and page mode is requested
    if args.page:
        username = extract_username_from_url(args.url)
        if not username:
            print("Error: Invalid Instagram profile URL. Use --page with a profile URL like https://instagram.com/username", file=sys.stderr)
            sys.exit(1)
        
        print(f"Starting bulk download from @{username}...")
        results = download_profile_videos(
            args.url,
            args.output_dir,
            args.cookies_file,
            args.max_videos
        )
        
        print_download_summary(results, username)
        
        # Exit with error code if any downloads failed
        if results['failed'] > 0:
            sys.exit(1)
    else:
        # Single video download
        exit_code = download_instagram_video(args.url, args.output_dir, args.cookies_file)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()


