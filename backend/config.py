# Configuration for Deepfake Detection System

# Ensemble weights for combining different detection methods
ENSEMBLE_WEIGHTS = {
    'neural': 0.40,
    'frequency': 0.30,
    'face': 0.20,
    'metadata': 0.10
}

# Risk level thresholds
RISK_THRESHOLDS = {
    'high': 0.70,
    'medium': 0.40
}

# Model configuration
MODEL_CONFIG = {
    'huggingface': 'prithivMLmods/Deep-Fake-Detector-Model',
    'device': 'cuda',  # Will auto-fallback to CPU if CUDA unavailable
}

# File upload limits
MAX_FILE_SIZE_MB = 50
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}

# Analysis settings
FREQUENCY_ANALYSIS_ENABLED = True
FACE_ANALYSIS_ENABLED = True
METADATA_ANALYSIS_ENABLED = True
NEURAL_ENSEMBLE_ENABLED = True

# MediaPipe face detection confidence
FACE_DETECTION_CONFIDENCE = 0.5
MIN_FACE_SIZE = 50  # Minimum face size in pixels

# Feature toggles
ENABLE_DETAILED_BREAKDOWN = True
ENABLE_CONFIDENCE_SCORES = True
