"""
Download missing OpenCV cascade files
"""
import urllib.request
import os

# GitHub raw URLs for OpenCV cascade files
CASCADE_URLS = {
    'haarcascade_mcs_mouth.xml': 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades_cuda/haarcascade_mcs_mouth.xml',
}

def download_cascades():
    """Download missing cascade files to models_cache"""
    models_cache = os.path.join(os.path.dirname(__file__), 'models_cache')
    os.makedirs(models_cache, exist_ok=True)
    
    for filename, url in CASCADE_URLS.items():
        filepath = os.path.join(models_cache, filename)
        
        if os.path.exists(filepath):
            print(f"✓ {filename} already exists")
            continue
        
        try:
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filepath)
            print(f"✓ Downloaded {filename}")
        except Exception as e:
            print(f"✗ Failed to download {filename}: {e}")
            # Try alternative URL
            alt_url = 'https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/haarcascade_mcs_mouth.xml'
            try:
                urllib.request.urlretrieve(alt_url, filepath)
                print(f"✓ Downloaded {filename} (alternative source)")
            except Exception as e2:
                print(f"✗ Failed with alternative URL: {e2}")

if __name__ == "__main__":
    download_cascades()
    print("\nDone! Cascade files are ready.")
