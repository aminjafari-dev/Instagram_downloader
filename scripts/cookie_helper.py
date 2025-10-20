"""
Cookie Helper for Instagram Downloader

This script helps you create cookies.txt files for Instagram authentication.
Cookies are needed when Instagram requires login or has API restrictions.
"""

import os
import sys


def print_cookie_instructions():
    """Print detailed instructions for creating cookies.txt files."""
    print("="*70)
    print("HOW TO CREATE COOKIES.TXT FOR INSTAGRAM")
    print("="*70)
    print()
    print("Method 1: Browser Extension (Recommended)")
    print("-" * 40)
    print("1. Install 'Get cookies.txt' extension:")
    print("   Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid")
    print("   Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/")
    print("2. Go to instagram.com and log in")
    print("3. Click the extension icon")
    print("4. Click 'Export' to download cookies.txt")
    print("5. Place cookies.txt in your project folder")
    print()
    print("Method 2: Manual Export")
    print("-" * 40)
    print("1. Open Instagram in your browser")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to Application/Storage tab")
    print("4. Find Cookies > https://instagram.com")
    print("5. Copy sessionid, csrftoken, and other cookies")
    print("6. Create cookies.txt with Netscape format")
    print()
    print("Method 3: Using curl")
    print("-" * 40)
    print("1. Log into Instagram in browser")
    print("2. Export cookies using browser dev tools")
    print("3. Convert to Netscape format")
    print()
    print("IMPORTANT NOTES:")
    print("- Cookies expire after some time, regenerate as needed")
    print("- Never share your cookies.txt file")
    print("- Use cookies only for your own accounts")
    print("="*70)


def create_sample_cookies():
    """Create a sample cookies.txt file with proper format."""
    sample_content = """# Netscape HTTP Cookie File
# This is a sample cookies.txt file
# Replace the values below with your actual Instagram cookies

.instagram.com	TRUE	/	FALSE	0	sessionid	YOUR_SESSION_ID_HERE
.instagram.com	TRUE	/	FALSE	0	csrftoken	YOUR_CSRF_TOKEN_HERE
.instagram.com	TRUE	/	FALSE	0	ds_user_id	YOUR_USER_ID_HERE
"""
    
    sample_file = "cookies_sample.txt"
    try:
        with open(sample_file, 'w') as f:
            f.write(sample_content)
        print(f"Created sample cookies file: {sample_file}")
        print("Edit this file with your actual Instagram cookies")
    except Exception as e:
        print(f"Error creating sample file: {e}")


def main():
    """Main function to show cookie instructions."""
    print_cookie_instructions()
    
    response = input("\nWould you like to create a sample cookies.txt file? (y/n): ")
    if response.lower() in ['y', 'yes']:
        create_sample_cookies()


if __name__ == "__main__":
    main()
