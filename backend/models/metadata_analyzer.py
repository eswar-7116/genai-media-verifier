import os
from PIL import Image
import piexif
import numpy as np
from utils.forensics_utils import apply_ela


def analyze_metadata(image_path):
    """
    Enhanced metadata and file forensics analysis.
    
    Returns:
        dict with comprehensive metadata scoring
    """
    try:
        exif_score, exif_data = analyze_exif_data(image_path)
        ela_score = perform_ela_analysis(image_path)
        software = detect_editing_software(exif_data)
        compression_score = check_compression_consistency(image_path)
        
        # Enhanced combination
        final_score = (
            exif_score * 0.35 +
            ela_score * 0.40 +
            compression_score * 0.25
        )
        
        return {
            'score': float(final_score),
            'exif_present': bool(len(exif_data) > 0),
            'exif_score': float(exif_score),
            'ela_score': float(ela_score),
            'compression_score': float(compression_score),
            'editing_software_detected': str(software),
            'exif_suspicious': bool(exif_score > 0.6),
            'ela_anomalies': bool(ela_score > 0.6),
            'metadata_details': exif_data
        }
    
    except Exception as e:
        print(f"Metadata analysis error: {e}")
        return {
            'score': 0.5,
            'exif_present': False,
            'error': str(e)
        }


def analyze_exif_data(image_path):
    """
    Enhanced EXIF analysis with pattern detection.
    """
    try:
        exif_dict = piexif.load(image_path)
        
        exif_data = {}
        suspicious_score = 0.0
        
        if '0th' in exif_dict:
            ifd = exif_dict['0th']
            
            if piexif.ImageIFD.Make in ifd:
                exif_data['camera_make'] = ifd[piexif.ImageIFD.Make].decode('utf-8', errors='ignore')
            
            if piexif.ImageIFD.Model in ifd:
                exif_data['camera_model'] = ifd[piexif.ImageIFD.Model].decode('utf-8', errors='ignore')
            
            if piexif.ImageIFD.Software in ifd:
                exif_data['software'] = ifd[piexif.ImageIFD.Software].decode('utf-8', errors='ignore')
            
            if piexif.ImageIFD.DateTime in ifd:
                exif_data['datetime'] = ifd[piexif.ImageIFD.DateTime].decode('utf-8', errors='ignore')
        
        if 'GPS' in exif_dict and len(exif_dict['GPS']) > 0:
            exif_data['has_gps'] = True
        
        if 'Exif' in exif_dict:
            exif_ifd = exif_dict['Exif']
            
            if piexif.ExifIFD.DateTimeOriginal in exif_ifd:
                exif_data['datetime_original'] = exif_ifd[piexif.ExifIFD.DateTimeOriginal].decode('utf-8', errors='ignore')
        
        # ENHANCED SCORING LOGIC
        
        # Complete absence of EXIF = moderately suspicious
        # (Many legitimate images have no EXIF: screenshots, social media, web images)
        if len(exif_data) == 0:
            suspicious_score = 0.60
        
        # No camera info = likely AI or heavily edited
        elif 'camera_make' not in exif_data and 'camera_model' not in exif_data:
            if 'software' in exif_data:
                software_lower = exif_data['software'].lower()
                # Check for AI generation keywords (expanded list)
                ai_keywords = [
                    'stable diffusion', 'midjourney', 'dall-e', 'dalle', 'generative',
                    'ai', 'gan', 'diffusion', 'automatic1111', 'novelai',
                    'invoke', 'comfyui', 'playground', 'leonardo', 'ideogram',
                    'flux', 'pixai', 'tensor.art', 'civitai', 'neural',
                    'synthesized', 'generated', 'pytorch', 'tensorflow'
                ]
                
                if any(keyword in software_lower for keyword in ai_keywords):
                    suspicious_score = 0.95  # Very high - clear AI signature
                elif any(editor in software_lower for editor in ['photoshop', 'gimp', 'paint', 'pixlr']):
                    suspicious_score = 0.70  # High - edited
                else:
                    suspicious_score = 0.65  # Medium-high - unknown software
            else:
                suspicious_score = 0.65  # Medium-high - no camera, no software info (reduced from 0.75)
        
        # Has camera info - check plausibility
        elif 'camera_make' in exif_data or 'camera_model' in exif_data:
            # Check if camera info is plausible
            make = exif_data.get('camera_make', '').lower()
            model = exif_data.get('camera_model', '').lower()
            
            # Common camera manufacturers
            known_makes = ['canon', 'nikon', 'sony', 'apple', 'samsung', 'google', 
                          'huawei', 'xiaomi', 'oneplus', 'fujifilm', 'olympus', 'panasonic']
            
            if any(brand in make for brand in known_makes):
                suspicious_score = 0.15  # Low - legitimate camera
            else:
                suspicious_score = 0.40  # Medium - unknown camera brand
        
        else:
            suspicious_score = 0.50  # Medium - partial data
        
        return float(suspicious_score), exif_data
    
    except Exception as e:
        # No EXIF or corrupted - reduced from 0.75 to 0.60 (more realistic for web images)
        return 0.60, {}


def perform_ela_analysis(image_path):
    """
    Enhanced Error Level Analysis.
    """
    try:
        ela_image = apply_ela(image_path, quality=95)
        
        # Enhanced analysis
        ela_variance = np.var(ela_image)
        ela_mean = np.mean(ela_image)
        ela_std = np.std(ela_image)
        
        # Calculate high-error regions more precisely
        threshold = ela_mean + (2 * ela_std)
        high_error_pixels = np.sum(ela_image > threshold)
        total_pixels = ela_image.size
        
        high_error_ratio = high_error_pixels / total_pixels
        
        # Check for regional inconsistencies
        h, w = ela_image.shape[:2] if len(ela_image.shape) == 2 else ela_image.shape[:2]
        
        # Divide into 16 regions (4x4 grid)
        region_variances = []
        for i in range(4):
            for j in range(4):
                y_start = i * h // 4
                y_end = (i + 1) * h // 4
                x_start = j * w // 4
                x_end = (j + 1) * w // 4
                
                region = ela_image[y_start:y_end, x_start:x_end]
                region_variances.append(np.var(region))
        
        # High variance between regions = likely edited
        regional_inconsistency = np.std(region_variances) / (np.mean(region_variances) + 1e-10)
        
        # Combine metrics
        score = min(
            (ela_variance * 8.0) + 
            (high_error_ratio * 4.0) + 
            (regional_inconsistency * 2.0),
            1.0
        )
        
        return float(score)
    
    except Exception as e:
        return 0.5


def detect_editing_software(exif_data):
    """
    Detect editing software with AI detection.
    """
    if 'software' in exif_data:
        software = exif_data['software'].lower()
        
        # AI generators
        if any(ai in software for ai in ['stable diffusion', 'midjourney', 'dall-e', 'dalle']):
            return 'AI Generator'
        
        # Common editors
        if 'photoshop' in software:
            return 'Adobe Photoshop'
        elif 'gimp' in software:
            return 'GIMP'
        elif 'paint' in software:
            return 'Paint'
        elif 'affinity' in software:
            return 'Affinity Photo'
        else:
            return software
    
    return 'Unknown'


def check_compression_consistency(image_path):
    """
    Enhanced JPEG compression consistency check.
    """
    try:
        image = Image.open(image_path).convert('RGB')
        img_array = np.array(image)
        
        h, w = img_array.shape[:2]
        block_size = 64
        
        block_scores = []
        
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = img_array[i:i+block_size, j:j+block_size]
                
                # Multiple metrics per block
                block_var = np.var(block)
                block_mean = np.mean(block)
                block_scores.append((block_var, block_mean))
        
        if len(block_scores) == 0:
            return 0.5
        
        # Separate variance and mean
        variances = [s[0] for s in block_scores]
        means = [s[1] for s in block_scores]
        
        # Check consistency
        var_std = np.std(variances)
        var_mean = np.mean(variances)
        mean_std = np.std(means)
        
        # High inconsistency = likely manipulated
        var_inconsistency = var_std / (var_mean + 1e-10)
        mean_inconsistency = mean_std / 50.0  # Normalize
        
        score = min((var_inconsistency * 0.7 + mean_inconsistency * 0.3) / 2.0, 1.0)
        
        return float(score)
    
    except Exception as e:
        return 0.5


def validate_camera_metadata(exif_data):
    """
    Validate camera metadata patterns.
    """
    if not exif_data:
        return 0.8
    
    has_make = 'camera_make' in exif_data
    has_model = 'camera_model' in exif_data
    has_datetime = 'datetime' in exif_data or 'datetime_original' in exif_data
    
    if has_make and has_model and has_datetime:
        return 0.1
    elif has_make or has_model:
        return 0.4
    else:
        return 0.7
