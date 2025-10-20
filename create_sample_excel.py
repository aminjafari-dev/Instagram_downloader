"""
Simple script to create a sample Excel file with Instagram URLs for batch downloading.
"""

def create_sample_excel():
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is not installed.")
        print("Please run: pip install pandas openpyxl")
        return
    
    # Sample Instagram URLs (replace with your actual URLs)
    sample_urls = [
        'https://www.instagram.com/p/EXAMPLE1/',
        'https://www.instagram.com/p/EXAMPLE2/',
        'https://www.instagram.com/p/EXAMPLE3/',
    ]
    
    # Create DataFrame
    df = pd.DataFrame({'url': sample_urls})
    
    # Save to Excel
    output_file = 'instagram_urls.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"✓ Sample Excel file created: {output_file}")
    print(f"✓ Contains {len(sample_urls)} sample URLs")
    print("\nNext steps:")
    print("1. Open the Excel file and replace the sample URLs with your actual Instagram video URLs")
    print("2. Save the file")
    print("3. Use the Instagram Video Downloader GUI to batch download the videos")

if __name__ == "__main__":
    create_sample_excel()


