# Configuration for Deepfake Detection System

# Base ensemble weights (will be dynamically adjusted)
ENSEMBLE_WEIGHTS = {
    'neural': 0.50,      # Increased from 0.40 - Neural networks are most reliable
    'frequency': 0.25,   # Decreased from 0.30 - Can be unreliable for some fakes
    'face': 0.15,        # Decreased from 0.20 - Only useful when face detected
    'metadata': 0.10     # Kept same - Supporting evidence
}

# Risk level thresholds
RISK_THRESHOLDS = {
    'high': 0.65,    # Lowered from 0.70 - More sensitive detection
    'medium': 0.40   # Kept same
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

# Dynamic weighting settings
ENABLE_DYNAMIC_WEIGHTING = True
NEURAL_CONFIDENCE_BOOST = 1.5  # Boost neural weight when confidence > 90%
AGREEMENT_BOOST = 1.3          # Boost when multiple methods agree
FACE_NOT_DETECTED_REDISTRIBUTE = True  # Give face weight to neural when no face

# MediaPipe face detection confidence
FACE_DETECTION_CONFIDENCE = 0.5
MIN_FACE_SIZE = 50  # Minimum face size in pixels

# Feature toggles
ENABLE_DETAILED_BREAKDOWN = True
ENABLE_CONFIDENCE_SCORES = True
