import os
from typing import Tuple
from PIL import Image
from fastapi import HTTPException

from src.config import MAX_FILE_SIZE_MB, MAX_IMAGE_DIMENSION, MIN_IMAGE_DIMENSION, SUPPORTED_FORMATS

def validate_file_upload(filename: str, file_size: int) -> None:
    """Validate uploaded file before processing"""
    
    # Check file size
    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
        )
    
    # Check file extension
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    ext = os.path.splitext(filename.lower())[1]
    if ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )

def validate_image_dimensions(image: Image.Image) -> None:
    """Validate image dimensions"""
    width, height = image.size
    
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        raise HTTPException(
            status_code=400,
            detail=f"Image too large. Maximum dimension: {MAX_IMAGE_DIMENSION}px"
        )
    
    if min(width, height) < MIN_IMAGE_DIMENSION:
        raise HTTPException(
            status_code=400,
            detail=f"Image too small. Minimum dimension: {MIN_IMAGE_DIMENSION}px"
        )

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks"""
    # Remove path components and dangerous characters
    safe_name = os.path.basename(filename)
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._-")
    
    # Ensure it's not empty and has reasonable length
    if not safe_name or len(safe_name) > 255:
        safe_name = "uploaded_image.jpg"
    
    return safe_name