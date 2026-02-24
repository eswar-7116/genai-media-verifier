
import os
from typing import Dict


def get_bool_env(key: str, default: bool) -> bool:
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_float_env(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


ENSEMBLE_WEIGHTS = {
    'neural': 0.50,
    'frequency': 0.25,
    'face': 0.15,
    'metadata': 0.10
}


RISK_THRESHOLDS = {
    'high': get_float_env('RISK_THRESHOLD_HIGH', 0.65),
    'medium': get_float_env('RISK_THRESHOLD_MEDIUM', 0.40)
}


MODEL_CONFIG = {
    'huggingface': os.getenv('HUGGINGFACE_MODEL', 'prithivMLmods/Deep-Fake-Detector-Model'),
    'device': os.getenv('MODEL_DEVICE', 'cuda'),
}


MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}


UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')


FREQUENCY_ANALYSIS_ENABLED = get_bool_env('FREQUENCY_ANALYSIS_ENABLED', True)
FACE_ANALYSIS_ENABLED = get_bool_env('FACE_ANALYSIS_ENABLED', True)
METADATA_ANALYSIS_ENABLED = get_bool_env('METADATA_ANALYSIS_ENABLED', True)
NEURAL_ENSEMBLE_ENABLED = get_bool_env('NEURAL_ENSEMBLE_ENABLED', True)


ENABLE_DYNAMIC_WEIGHTING = get_bool_env('ENABLE_DYNAMIC_WEIGHTING', True)
NEURAL_CONFIDENCE_BOOST = 2.5
NEURAL_HIGH_CONFIDENCE_BOOST = 2.0
NEURAL_MEDIUM_BOOST = 1.7
AGREEMENT_BOOST = 1.4
FACE_NOT_DETECTED_REDISTRIBUTE = True


FACE_DETECTION_CONFIDENCE = 0.5
MIN_FACE_SIZE = 50


ENABLE_DETAILED_BREAKDOWN = get_bool_env('ENABLE_DETAILED_BREAKDOWN', True)
ENABLE_CONFIDENCE_SCORES = get_bool_env('ENABLE_CONFIDENCE_SCORES', True)


def get_cors_origins():
    cors_env = os.getenv('CORS_ORIGINS', '')
    
    if cors_env:
        custom_origins = [origin.strip() for origin in cors_env.split(',') if origin.strip()]
        return custom_origins
    
    return ["*"]

CORS_ORIGINS = get_cors_origins()
