# Configuration for Deepfake Detection System
import os
from typing import Dict

# Helper function to parse boolean from env
def get_bool_env(key: str, default: bool) -> bool:
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

# Helper function to parse float from env
def get_float_env(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default

# AGGRESSIVE ensemble weights - heavily favors neural networks when confident
ENSEMBLE_WEIGHTS = {
    'neural': 0.50,      # Base weight for neural networks
    'frequency': 0.25,   # Frequency domain analysis
    'face': 0.15,        # Facial analysis (only when face detected)
    'metadata': 0.10     # Metadata forensics
}

# Risk level thresholds - now configurable via environment variables
RISK_THRESHOLDS = {
    'high': get_float_env('RISK_THRESHOLD_HIGH', 0.65),
    'medium': get_float_env('RISK_THRESHOLD_MEDIUM', 0.40)
}

# Model configuration
MODEL_CONFIG = {
    'huggingface': os.getenv('HUGGINGFACE_MODEL', 'prithivMLmods/Deep-Fake-Detector-Model'),
    'device': os.getenv('MODEL_DEVICE', 'cuda'),  # Will auto-fallback to CPU if CUDA unavailable
}

# File upload limits
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}

# Upload directory - configurable for deployment
UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')

# Analysis settings - configurable via environment variables
FREQUENCY_ANALYSIS_ENABLED = get_bool_env('FREQUENCY_ANALYSIS_ENABLED', True)
FACE_ANALYSIS_ENABLED = get_bool_env('FACE_ANALYSIS_ENABLED', True)
METADATA_ANALYSIS_ENABLED = get_bool_env('METADATA_ANALYSIS_ENABLED', True)
NEURAL_ENSEMBLE_ENABLED = get_bool_env('NEURAL_ENSEMBLE_ENABLED', True)

# AGGRESSIVE dynamic weighting settings
ENABLE_DYNAMIC_WEIGHTING = get_bool_env('ENABLE_DYNAMIC_WEIGHTING', True)
NEURAL_CONFIDENCE_BOOST = 2.5      # 2.5x boost when >95% confidence + unanimous
NEURAL_HIGH_CONFIDENCE_BOOST = 2.0  # 2.0x boost when >93% confidence + strong agreement
NEURAL_MEDIUM_BOOST = 1.7          # 1.7x boost when >90% confidence
AGREEMENT_BOOST = 1.4              # 1.4x boost when multiple methods agree
FACE_NOT_DETECTED_REDISTRIBUTE = True  # Redistribute face weight to neural when no face detected

# MediaPipe face detection confidence
FACE_DETECTION_CONFIDENCE = 0.5
MIN_FACE_SIZE = 50

# Feature toggles
ENABLE_DETAILED_BREAKDOWN = get_bool_env('ENABLE_DETAILED_BREAKDOWN', True)
ENABLE_CONFIDENCE_SCORES = get_bool_env('ENABLE_CONFIDENCE_SCORES', True)

# CORS Origins - parse from environment variable
def get_cors_origins():
    """Parse CORS origins from environment variable"""
    cors_env = os.getenv('CORS_ORIGINS', '')
    
    # Check if we're in production with specific domain
    if cors_env:
        # Split by comma and strip whitespace
        custom_origins = [origin.strip() for origin in cors_env.split(',') if origin.strip()]
        return custom_origins
    
    # Development/testing - allow all origins
    # Note: Wildcard patterns like *.vercel.app don't work with standard CORS
    # You need to either:
    # 1. Allow all with ["*"]
    # 2. Add your specific Vercel URL as environment variable
    return ["*"]  # Allow all origins for development

CORS_ORIGINS = get_cors_origins()
