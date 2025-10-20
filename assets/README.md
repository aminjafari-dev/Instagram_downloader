# Instagram Video Downloader

A Python application for downloading Instagram videos and reels using yt-dlp. Supports both single video downloads and bulk profile downloads with automatic organization.

## Features

- ✅ Download single Instagram videos/reels
- ✅ Download all videos from Instagram profiles
- ✅ Automatic folder organization by username and date
- ✅ GUI and CLI interfaces
- ✅ Progress tracking
- ✅ Cookie authentication support
- ✅ FFmpeg integration for best quality

## Quick Start

### GUI Mode (Recommended)
1. Double-click `scripts\run_gui.bat`
2. Enter Instagram URL
3. Check "Download all videos from profile" for bulk downloads
4. Click Download

### CLI Mode
```bash
# Single video
python -m src.cli "https://instagram.com/reel/VIDEO_ID/"

# All videos from profile
python -m src.cli "https://instagram.com/username" --page --max-videos 50
```

## Installation

1. Install Python 3.8+
2. Install dependencies:
```bash
pip install -r scripts\requirements.txt
```

## Troubleshooting

### "Unable to extract data" Error

This error occurs when Instagram requires authentication or has changed their API. Solutions:

#### 1. Use Cookies File (Recommended)
```bash
# Run cookie helper
python scripts\cookie_helper.py

# Or double-click
scripts\setup_cookies.bat
```

Then use cookies:
```bash
python -m src.cli "https://instagram.com/username" --page -c cookies.txt
```

#### 2. Update yt-dlp
```bash
pip install --upgrade yt-dlp
```

#### 3. Try Individual Videos
If profile extraction fails, download individual video URLs:
```bash
python -m src.cli "https://instagram.com/reel/VIDEO_ID/"
```

### FFmpeg Not Found
For best quality video+audio merging:
```bash
# Windows (winget)
winget install --id=Gyan.FFmpeg -e

# Or download from https://www.gyan.dev/ffmpeg/builds/
```

### Private Profiles
- Use cookies file with your logged-in session
- Ensure you follow the account
- Some private content may not be accessible

## Folder Structure

Downloads are automatically organized:
```
downloads/
├── username1/
│   ├── 2024-01/
│   │   ├── username1_video1.mp4
│   │   └── username1_video2.mp4
│   └── 2024-02/
│       └── username1_video3.mp4
└── username2/
    └── 2024-01/
        └── username2_video1.mp4
```

## Usage Examples

### GUI Mode
- Launch: `scripts\run_gui.bat`
- Enter profile URL: `https://instagram.com/username`
- Check "Download all videos from profile"
- Set max videos (default: 50)
- Click Download

### CLI Mode
```bash
# Single video download
python -m src.cli "https://instagram.com/reel/ABC123/"

# Profile download with cookies
python -m src.cli "https://instagram.com/username" --page -c cookies.txt

# Custom output directory
python -m src.cli "https://instagram.com/username" --page -o "./my_videos"

# Limit videos
python -m src.cli "https://instagram.com/username" --page --max-videos 25
```

## File Structure

```
instagram_downloader/
├── src/                    # Source code
│   ├── cli.py             # Command-line interface
│   ├── downloader.py      # Core download logic
│   ├── gui.py             # GUI interface
│   ├── page_downloader.py # Profile bulk download
│   └── main.py            # Entry point
├── scripts/               # Scripts and dependencies
│   ├── requirements.txt   # Python dependencies
│   ├── run_gui.bat        # GUI launcher
│   ├── setup_cookies.bat  # Cookie helper
│   └── cookie_helper.py   # Cookie instructions
├── assets/                # Documentation
│   └── README.md          # This file
└── downloads/             # Downloaded videos
```

## Common Issues

1. **"Unable to extract data"**: Use cookies file or update yt-dlp
2. **"ffmpeg not found"**: Install FFmpeg for best quality
3. **Private profiles**: Use cookies with your logged-in session
4. **Rate limiting**: Add delays or use cookies
5. **No videos found**: Profile may be private or have no videos

## Support

- Update yt-dlp regularly: `pip install --upgrade yt-dlp`
- Use cookies for authentication
- Check Instagram's terms of service
- Report issues to yt-dlp GitHub if related to extraction

## Legal Notice

- Only download content you have permission to download
- Respect Instagram's terms of service
- Don't redistribute downloaded content without permission
- Use responsibly and ethically