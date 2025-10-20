# Excel Batch Download Feature

This feature allows you to download multiple Instagram videos from URLs listed in an Excel file.

## How to Use

### 1. Prepare Your Excel File

Create an Excel file (.xlsx or .xls) with Instagram video URLs. The file should have at least one column containing the URLs.

Example structure:

| url |
|-----|
| https://www.instagram.com/p/ABC123/ |
| https://www.instagram.com/p/DEF456/ |
| https://www.instagram.com/p/GHI789/ |

You can also use a different column name, such as "link", "video_url", etc.

### 2. Using the GUI

1. Launch the Instagram Video Downloader GUI
2. Check the "Download from Excel file" checkbox
3. Click "Browse" next to "Excel file:" and select your Excel file
4. If your URL column is not named "url", enter the column name in the "URL column name:" field
5. Select your output folder
6. (Optional) Select a cookies file if needed for authentication
7. Click "Download" to start the batch download

### 3. Progress Tracking

The GUI will show:
- Current video being downloaded
- Progress: [current/total] videos
- Success and failure counts at the end

### 4. Creating an Excel File Programmatically

You can create an Excel file using Python:

```python
import pandas as pd

# Your list of Instagram URLs
urls = [
    'https://www.instagram.com/p/ABC123/',
    'https://www.instagram.com/p/DEF456/',
    'https://www.instagram.com/p/GHI789/',
]

# Create DataFrame and save to Excel
df = pd.DataFrame({'url': urls})
df.to_excel('instagram_urls.xlsx', index=False)
```

## Requirements

Make sure you have installed the required dependencies:

```bash
pip install -r scripts/requirements.txt
```

This includes:
- yt-dlp (for downloading videos)
- pandas (for reading Excel files)
- openpyxl (for Excel file support)

## Tips

- Empty rows or cells will be skipped automatically
- The downloader will continue even if some videos fail to download
- Failed downloads will be reported in the final status
- Large batches may take a long time - the progress bar will keep you updated

## Troubleshooting

### "Column 'url' not found" error
- Check that your Excel file has the correct column name
- Update the "URL column name" field in the GUI to match your column name

### "pandas is not installed" error
- Run: `pip install pandas openpyxl`

### Videos failing to download
- Make sure the URLs are valid Instagram video/post URLs
- Some content may require authentication - use a cookies file
- Check your internet connection


