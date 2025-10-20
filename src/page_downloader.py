import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import urlparse

from .downloader import download_instagram_video, ensure_output_directory


def extract_username_from_url(url: str) -> Optional[str]:
    """Extract username from Instagram profile URL."""
    try:
        parsed = urlparse(url)
        if 'instagram.com' not in parsed.netloc:
            return None
        
        path_parts = parsed.path.strip('/').split('/')
        if path_parts and path_parts[0]:
            username = path_parts[0]
            # Remove @ if present
            if username.startswith('@'):
                username = username[1:]
            return username
        return None
    except Exception:
        return None


def get_profile_videos(url: str, max_videos: int = 50, cookies_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get list of video URLs from Instagram profile.
    Returns list of video metadata including URLs, titles, dates.
    """
    try:
        from yt_dlp import YoutubeDL  # type: ignore
    except Exception as import_error:
        print(f"Error: yt-dlp not available: {import_error}", file=sys.stderr)
        return []

    # Configure yt-dlp to extract playlist info only
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Don't download, just get metadata
        'playlistend': max_videos,
        'sleep_interval': 1,  # Add delay between requests
        'max_sleep_interval': 5,
    }
    
    # Add cookies if provided
    if cookies_file:
        ydl_opts['cookiefile'] = cookies_file

    videos = []
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Attempting to extract videos from profile...")
            info = ydl.extract_info(url, download=False)
            
            if info and 'entries' in info:
                for entry in info['entries']:
                    if entry and entry.get('url'):
                        video_info = {
                            'url': entry['url'],
                            'title': entry.get('title', ''),
                            'uploader': entry.get('uploader', ''),
                            'upload_date': entry.get('upload_date', ''),
                            'duration': entry.get('duration', 0),
                            'view_count': entry.get('view_count', 0),
                        }
                        videos.append(video_info)
                        
                print(f"Successfully extracted {len(videos)} videos")
            else:
                print("No video entries found in profile")
                
    except Exception as e:
        error_msg = str(e)
        print(f"Error extracting profile videos: {error_msg}")
        
        # Check if it's a common Instagram API issue
        if "Unable to extract data" in error_msg or "instagram:user" in error_msg:
            print("\n" + "="*60)
            print("INSTAGRAM API ISSUE DETECTED")
            print("="*60)
            print("Instagram has changed their API or requires authentication.")
            print("Try these solutions:")
            print("1. Use cookies file: Export cookies from your browser")
            print("2. Try individual video URLs instead of profile")
            print("3. Check if the profile is private")
            print("4. Update yt-dlp: pip install --upgrade yt-dlp")
            print("="*60)
    
    return videos


def create_organized_path(base_dir: str, username: str, video_info: Dict[str, Any]) -> str:
    """Create organized folder structure: base_dir/username/YYYY-MM/"""
    try:
        # Extract year-month from upload date
        upload_date = video_info.get('upload_date', '')
        if upload_date and len(upload_date) >= 6:
            year_month = f"{upload_date[:4]}-{upload_date[4:6]}"
        else:
            # Use current date if no upload date
            year_month = datetime.now().strftime("%Y-%m")
        
        organized_path = os.path.join(base_dir, username, year_month)
        ensure_output_directory(organized_path)
        return organized_path
    except Exception:
        # Fallback to base directory
        return base_dir


def download_profile_videos_fallback(
    profile_url: str,
    output_dir: str,
    cookies_file: Optional[str] = None,
    max_videos: int = 50,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Fallback method: Try to download individual videos if profile extraction fails.
    This method attempts to find video URLs manually.
    """
    username = extract_username_from_url(profile_url)
    if not username:
        return {'success': 0, 'failed': 0, 'errors': ['Invalid Instagram profile URL']}
    
    print(f"\nProfile extraction failed. Trying alternative method...")
    print(f"Please provide individual video URLs from @{username}")
    print("You can:")
    print("1. Copy video URLs manually from Instagram")
    print("2. Use browser extensions to extract video URLs")
    print("3. Try again with cookies file")
    
    return {
        'success': 0, 
        'failed': 0, 
        'errors': [
            'Profile extraction failed. Instagram may require authentication.',
            'Try using cookies file or download individual videos manually.'
        ]
    }


def download_profile_videos(
    profile_url: str,
    output_dir: str,
    cookies_file: Optional[str] = None,
    max_videos: int = 50,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Download all videos from an Instagram profile.
    
    Args:
        profile_url: Instagram profile URL
        output_dir: Base output directory
        cookies_file: Optional cookies file for authentication
        max_videos: Maximum number of videos to download
        progress_callback: Function to call with (current, total, current_video) progress
    
    Returns:
        Dict with download results: {'success': int, 'failed': int, 'errors': list}
    """
    username = extract_username_from_url(profile_url)
    if not username:
        return {'success': 0, 'failed': 0, 'errors': ['Invalid Instagram profile URL']}
    
    print(f"Extracting videos from @{username}...")
    videos = get_profile_videos(profile_url, max_videos, cookies_file)
    
    if not videos:
        print(f"\nNo videos found. This could be due to:")
        print("1. Instagram API changes requiring authentication")
        print("2. Private profile")
        print("3. Rate limiting")
        print("4. Profile has no videos")
        print("\nTrying fallback method...")
        return download_profile_videos_fallback(profile_url, output_dir, cookies_file, max_videos, progress_callback)
    
    print(f"Found {len(videos)} videos. Starting downloads...")
    
    results = {'success': 0, 'failed': 0, 'errors': []}
    
    for i, video_info in enumerate(videos, 1):
        try:
            # Create organized path for this video
            video_output_dir = create_organized_path(output_dir, username, video_info)
            
            # Update progress
            if progress_callback:
                progress_callback(i, len(videos), video_info.get('title', f'Video {i}'))
            
            print(f"\n[{i}/{len(videos)}] Downloading: {video_info.get('title', 'Untitled')}")
            
            # Download the video
            exit_code = download_instagram_video(
                video_info['url'],
                video_output_dir,
                cookies_file
            )
            
            if exit_code == 0:
                results['success'] += 1
                print(f"✅ Downloaded successfully")
            else:
                results['failed'] += 1
                error_msg = f"Failed to download: {video_info.get('title', 'Untitled')}"
                results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                
        except Exception as e:
            results['failed'] += 1
            error_msg = f"Error downloading video {i}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    return results


def print_download_summary(results: Dict[str, Any], username: str) -> None:
    """Print a summary of the download results."""
    print(f"\n{'='*50}")
    print(f"Download Summary for @{username}")
    print(f"{'='*50}")
    print(f"✅ Successfully downloaded: {results['success']}")
    print(f"❌ Failed downloads: {results['failed']}")
    
    if results['errors']:
        print(f"\nErrors encountered:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  • {error}")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more errors")
    
    print(f"{'='*50}")
