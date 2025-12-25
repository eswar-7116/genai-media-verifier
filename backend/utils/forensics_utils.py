import numpy as np
from PIL import Image
import cv2


def convert_to_frequency_domain(image):
    """Convert image to frequency domain using FFT"""
    if isinstance(image, Image.Image):
        image = np.array(image.convert('L'))
    elif len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    f_transform = np.fft.fft2(image)
    f_shift = np.fft.fftshift(f_transform)
    magnitude_spectrum = np.abs(f_shift)
    
    return magnitude_spectrum


def apply_dct(image):
    """Apply Discrete Cosine Transform"""
    if isinstance(image, Image.Image):
        image = np.array(image.convert('L'))
    elif len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    image_float = np.float32(image)
    dct = cv2.dct(image_float)
    
    return dct


def apply_ela(image_path, quality=95):
    """
    Error Level Analysis - detects regions with different compression levels
    Returns difference image highlighting manipulated areas
    """
    import io
    from PIL import Image
    
    original = Image.open(image_path).convert('RGB')
    
    # Resave at specified quality
    temp_buffer = io.BytesIO()
    original.save(temp_buffer, format='JPEG', quality=quality)
    temp_buffer.seek(0)
    
    compressed = Image.open(temp_buffer)
    
    # Calculate difference
    ela_image = np.array(original).astype(np.float32) - np.array(compressed).astype(np.float32)
    ela_image = np.abs(ela_image)
    
    # Normalize
    ela_image = (ela_image - ela_image.min()) / (ela_image.max() - ela_image.min() + 1e-10)
    
    return ela_image


def extract_image_patches(image, patch_size=64):
    """Extract patches from image for texture analysis"""
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    h, w = image.shape[:2]
    patches = []
    
    for i in range(0, h - patch_size, patch_size):
        for j in range(0, w - patch_size, patch_size):
            patch = image[i:i+patch_size, j:j+patch_size]
            patches.append(patch)
    
    return patches


def normalize_score(raw_score, min_val=0.0, max_val=1.0):
    """Normalize score to 0-1 range"""
    normalized = (raw_score - min_val) / (max_val - min_val + 1e-10)
    return np.clip(normalized, 0.0, 1.0)


def compute_image_statistics(image):
    """Compute statistical features of image"""
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    stats = {
        'mean': np.mean(gray),
        'std': np.std(gray),
        'entropy': -np.sum(gray * np.log2(gray + 1e-10)),
        'variance': np.var(gray)
    }
    
    return stats


def detect_blur(image):
    """Detect if image is blurry using Laplacian variance"""
    if isinstance(image, Image.Image):
        image = np.array(image.convert('L'))
    elif len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    
    return laplacian_var


def analyze_color_histogram(image):
    """Analyze color distribution"""
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    
    hist_features = []
    for i in range(3):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        hist = hist.flatten()
        hist_features.extend([np.mean(hist), np.std(hist)])
    
    return hist_features
