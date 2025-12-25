import os
from PIL import Image
import piexif
import numpy as np
from utils.forensics_utils import apply_ela


def analyze_metadata(image_path):
    """
    Main entry point for metadata and file forensics analysis.
    
    Returns:
        dict: {
            'score': float (0-1, higher = more likely fake),
            'exif_present': bool,
            'exif_suspicious': bool,
            'ela_score': float,
            'editing_software_detected': str,
            'compression_score': float
        }
    """
    try:
        exif_score, exif_data = analyze_exif_data(image_path)
        ela_score = perform_ela_analysis(image_path)
        software = detect_editing_software(exif_data)
        compression_score = check_compression_consistency(image_path)
        
        # Combine scores
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
    Extract and analyze EXIF metadata.
    AI-generated images often lack proper EXIF or have suspicious patterns.
    """
    try:
        exif_dict = piexif.load(image_path)
        
        exif_data = {}
        suspicious_score = 0.0
        
        # Extract key EXIF fields
        if '0th' in exif_dict:
            ifd = exif_dict['0th']
            
            # Camera make and model
            if piexif.ImageIFD.Make in ifd:
                exif_data['camera_make'] = ifd[piexif.ImageIFD.Make].decode('utf-8', errors='ignore')
            
            if piexif.ImageIFD.Model in ifd:
                exif_data['camera_model'] = ifd[piexif.ImageIFD.Model].decode('utf-8', errors='ignore')
            
            # Software
            if piexif.ImageIFD.Software in ifd:
                exif_data['software'] = ifd[piexif.ImageIFD.Software].decode('utf-8', errors='ignore')
            
            # DateTime
            if piexif.ImageIFD.DateTime in ifd:
                exif_data['datetime'] = ifd[piexif.ImageIFD.DateTime].decode('utf-8', errors='ignore')
        
        # Check GPS data
        if 'GPS' in exif_dict and len(exif_dict['GPS']) > 0:
            exif_data['has_gps'] = True
        
        # Check Exif IFD
        if 'Exif' in exif_dict:
            exif_ifd = exif_dict['Exif']
            
            if piexif.ExifIFD.DateTimeOriginal in exif_ifd:
                exif_data['datetime_original'] = exif_ifd[piexif.ExifIFD.DateTimeOriginal].decode('utf-8', errors='ignore')
        
        # Analyze for suspicious patterns
        
        # 1. No EXIF data at all = suspicious
        if len(exif_data) == 0:
            suspicious_score = 0.8
        
        # 2. No camera info but has software = likely edited/generated
        elif 'camera_make' not in exif_data and 'camera_model' not in exif_data:
            if 'software' in exif_data:
                suspicious_score = 0.7
            else:
                suspicious_score = 0.6
        
        # 3. Check for AI generation software signatures
        elif 'software' in exif_data:
            software_lower = exif_data['software'].lower()
            ai_keywords = ['stable diffusion', 'midjourney', 'dall-e', 'generative', 'ai', 'gan']
            
            if any(keyword in software_lower for keyword in ai_keywords):
                suspicious_score = 0.9
            elif any(editor in software_lower for editor in ['photoshop', 'gimp', 'paint']):
                suspicious_score = 0.5
            else:
                suspicious_score = 0.2
        
        else:
            # Has camera info, looks legitimate
            suspicious_score = 0.1
        
        return float(suspicious_score), exif_data
    
    except Exception as e:
        # No EXIF data or corrupted
        return 0.7, {}


def perform_ela_analysis(image_path):
    """
    Error Level Analysis - detects regions with different compression levels.
    Manipulated areas show different error levels.
    """
    try:
        ela_image = apply_ela(image_path, quality=95)
        
        # Analyze ELA result
        # High variance in ELA = inconsistent compression = likely edited
        ela_variance = np.var(ela_image)
        ela_mean = np.mean(ela_image)
        
        # Calculate regions with high error
        threshold = ela_mean + (2 * np.std(ela_image))
        high_error_pixels = np.sum(ela_image > threshold)
        total_pixels = ela_image.size
        
        high_error_ratio = high_error_pixels / total_pixels
        
        # Combine metrics
        # Higher variance and high error ratio = more suspicious
        score = min((ela_variance * 10) + (high_error_ratio * 5), 1.0)
        
        return float(score)
    
    except Exception as e:
        return 0.5


def detect_editing_software(exif_data):
    """
    Detect editing software from EXIF data.
    """
    if 'software' in exif_data:
        software = exif_data['software'].lower()
        
        # Check for known software
        if 'photoshop' in software:
            return 'Adobe Photoshop'
        elif 'gimp' in software:
            return 'GIMP'
        elif 'paint' in software:
            return 'Paint'
        elif any(ai in software for ai in ['stable diffusion', 'midjourney', 'dall-e']):
            return 'AI Generator'
        else:
            return software
    
    return 'Unknown'


def check_compression_consistency(image_path):
    """
    Check for consistent JPEG compression across the image.
    Edited images show inconsistent compression.
    """
    try:
        image = Image.open(image_path).convert('RGB')
        img_array = np.array(image)
        
        # Divide image into blocks and check compression artifacts
        h, w = img_array.shape[:2]
        block_size = 64
        
        block_scores = []
        
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = img_array[i:i+block_size, j:j+block_size]
                
                # Calculate block variance (proxy for compression quality)
                block_var = np.var(block)
                block_scores.append(block_var)
        
        if len(block_scores) == 0:
            return 0.5
        
        # Check consistency across blocks
        score_std = np.std(block_scores)
        score_mean = np.mean(block_scores)
        
        # High standard deviation = inconsistent compression
        inconsistency = score_std / (score_mean + 1e-10)
        
        score = min(inconsistency / 2.0, 1.0)
        
        return float(score)
    
    except Exception as e:
        return 0.5


def validate_camera_metadata(exif_data):
    """
    Validate camera metadata patterns.
    Real cameras have consistent metadata patterns.
    """
    if not exif_data:
        return 0.8
    
    # Check for essential camera fields
    has_make = 'camera_make' in exif_data
    has_model = 'camera_model' in exif_data
    has_datetime = 'datetime' in exif_data or 'datetime_original' in exif_data
    
    if has_make and has_model and has_datetime:
        # Looks like real camera data
        return 0.1
    elif has_make or has_model:
        # Partial data
        return 0.4
    else:
        # Missing camera info
        return 0.7
