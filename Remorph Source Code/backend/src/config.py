import os
from typing import Dict, Any

# Core paths
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
FINGERPRINTS_PATH = os.getenv("FINGERPRINTS_PATH", "data/fingerprints.json")
WEIGHTS_PATH = os.getenv("WEIGHTS_PATH", "weights/detector.pt")

# API Configuration
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_IMAGE_DIMENSION = int(os.getenv("MAX_IMAGE_DIMENSION", "4096"))
MIN_IMAGE_DIMENSION = int(os.getenv("MIN_IMAGE_DIMENSION", "224"))

# Detection thresholds
FACE_CONFIDENCE_THRESHOLD = float(os.getenv("FACE_CONFIDENCE_THRESHOLD", "0.90"))
QUALITY_MIN_SIDE = int(os.getenv("QUALITY_MIN_SIDE", "224"))

# Heuristic weights
HEURISTIC_WEIGHTS = {
    "fft_weight": float(os.getenv("HEURISTIC_FFT_WEIGHT", "0.9")),
    "ela_weight": float(os.getenv("HEURISTIC_ELA_WEIGHT", "0.6")),
    "lap_weight": float(os.getenv("HEURISTIC_LAP_WEIGHT", "0.2")),
    "jpeg_weight": float(os.getenv("HEURISTIC_JPEG_WEIGHT", "0.15")),
    "threshold": float(os.getenv("HEURISTIC_THRESHOLD", "0.7")),
    "steepness": float(os.getenv("HEURISTIC_STEEPNESS", "4.0"))
}

# Supported image formats
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

def validate_config():
    """Validate configuration on startup"""
    errors = []
    
    if MAX_FILE_SIZE_MB <= 0:
        errors.append("MAX_FILE_SIZE_MB must be positive")
    
    if MAX_IMAGE_DIMENSION <= MIN_IMAGE_DIMENSION:
        errors.append("MAX_IMAGE_DIMENSION must be greater than MIN_IMAGE_DIMENSION")
    
    if not (0.0 <= FACE_CONFIDENCE_THRESHOLD <= 1.0):
        errors.append("FACE_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")
    
    return True