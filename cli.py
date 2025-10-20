import argparse
import os
import sys

from downloader import download_instagram_video

try:
    from gui import DownloaderGUI  # type: ignore
    GUI_AVAILABLE = True
except Exception:
    DownloaderGUI = None  # type: ignore
    GUI_AVAILABLE = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Instagram video/Reel using yt-dlp")
    parser.add_argument("url", nargs="?", help="Instagram video/Reel URL")
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

    exit_code = download_instagram_video(args.url, args.output_dir, args.cookies_file)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


