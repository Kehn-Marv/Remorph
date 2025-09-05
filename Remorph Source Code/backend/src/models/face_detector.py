import numpy as np
from PIL import Image
from typing import Tuple, Optional
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class FaceDetectorSingleton:
    """Singleton MTCNN face detector to avoid recreating on each request"""
    _instance = None
    _mtcnn = None
    _available = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize MTCNN detector once"""
        try:
            from facenet_pytorch import MTCNN
            self._mtcnn = MTCNN(keep_all=True, device="cpu")
            self._available = True
            logger.info("MTCNN face detector initialized successfully")
        except Exception as e:
            logger.warning(f"MTCNN not available: {e}")
            self._available = False
    
    def detect_largest_face(self, pil_im: Image.Image) -> Tuple[Image.Image, bool, float]:
        """
        Detect and return the largest face in the image.
        Returns: (face_crop, face_found, confidence)
        """
        if not self._available or self._mtcnn is None:
            logger.debug("Face detection not available, using full image")
            return pil_im, False, 0.0
        
        try:
            boxes, probs = self._mtcnn.detect(pil_im)
            
            if boxes is None or len(boxes) == 0:
                logger.debug("No faces detected in image")
                return pil_im, False, 0.0
            
            # Find the face with highest confidence
            best_i = int(np.argmax(probs))
            x1, y1, x2, y2 = [int(v) for v in boxes[best_i]]
            conf = float(probs[best_i])
            
            # Ensure coordinates are within image bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(pil_im.width, x2)
            y2 = min(pil_im.height, y2)
            
            # Validate face region
            if x2 <= x1 or y2 <= y1:
                logger.warning("Invalid face coordinates detected")
                return pil_im, False, 0.0
            
            face = pil_im.crop((x1, y1, x2, y2))
            logger.debug(f"Face detected: confidence={conf:.3f}, size={face.size}")
            
            return face, True, conf
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return pil_im, False, 0.0

# Global instance
face_detector = FaceDetectorSingleton()