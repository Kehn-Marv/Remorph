import os
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as T

from src.utils.ela import error_level_analysis
from src.utils.frequency import fft_highfreq_ratio, laplacian_variance, jpeg_quant_score
from src.config import HEURISTIC_WEIGHTS
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class HeuristicDetector:
    """
    Lightweight, CPU-first heuristics. Returns a score in [0,1].
    """
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or HEURISTIC_WEIGHTS
        logger.info("Heuristic detector initialized with configurable weights")

    def features(self, im: Image.Image) -> Dict[str, float]:
        """Extract forensic features from image"""
        try:
            ela_img, ela_mean = error_level_analysis(im, quality=90)
            fft_ratio = fft_highfreq_ratio(im)
            lap_var = laplacian_variance(im)
            jq = jpeg_quant_score(im)
            
            features = {
                "ela_mean": ela_mean,
                "fft_high_ratio": fft_ratio,
                "lap_var": lap_var,
                "jpeg_score": jq
            }
            
            logger.debug(f"Extracted features: {features}")
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            # Return default features to prevent pipeline failure
            return {
                "ela_mean": 0.0,
                "fft_high_ratio": 0.5,
                "lap_var": 100.0,
                "jpeg_score": 0.5
            }

    def score(self, feats: Dict[str, float]) -> float:
        """Calculate deepfake probability score using weighted features"""
        try:
            x = (
                self.weights["fft_weight"] * feats["fft_high_ratio"] +
                self.weights["ela_weight"] * (feats["ela_mean"] / 50.0) +
                self.weights["lap_weight"] * (feats["lap_var"] / 200.0) -
                self.weights["jpeg_weight"] * feats["jpeg_score"]
            )
            
            # Sigmoid activation
            s = 1.0 / (1.0 + np.exp(-self.weights["steepness"] * (x - self.weights["threshold"])))
            score = float(np.clip(s, 0.0, 1.0))
            
            logger.debug(f"Calculated heuristic score: {score:.3f}")
            return score
            
        except Exception as e:
            logger.error(f"Score calculation failed: {e}")
            return 0.5  # Default neutral score

    def analyze(self, im: Image.Image) -> Dict[str, Any]:
        """Full heuristic analysis"""
        feats = self.features(im)
        s = self.score(feats)
        return {"score": s, "features": feats}


class TorchDetector:
    """
    Optional Torch model with improved error handling and caching.
    """
    def __init__(self, weights_path: str, device: Optional[str] = None, target_layer: Optional[str] = None):
        self.weights_path = weights_path
        self.available = os.path.exists(weights_path)
        self.model = None
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.target_layer = target_layer
        
        self.transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        if self.available:
            self._load_model()

    def _load_model(self):
        """Load the torch model with proper error handling"""
        try:
            if self.weights_path.endswith(".pt"):
                self.model = torch.jit.load(self.weights_path, map_location=self.device)
            else:
                self.model = torch.load(self.weights_path, map_location=self.device)
            
            self.model.eval()
            logger.info(f"Torch model loaded successfully from {self.weights_path}")
            
        except Exception as e:
            logger.error(f"Failed to load torch model: {e}")
            self.available = False
            self.model = None

    def predict(self, im: Image.Image) -> Dict[str, Any]:
        """Predict with the torch model"""
        if not self.available or self.model is None:
            return {"available": False, "error": "Model not available"}
        
        try:
            x = self.transform(im).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                logits = self.model(x)
            
            if logits.ndim == 1:
                logits = logits.unsqueeze(0)
            
            probs = torch.softmax(logits, dim=1).detach().cpu().numpy()[0].tolist()
            
            logger.debug(f"Torch model prediction: {probs}")
            return {"available": True, "probs": probs}
            
        except Exception as e:
            logger.error(f"Torch model prediction failed: {e}")
            return {"available": False, "error": str(e)}

    def gradcam(self, im: Image.Image, class_idx: Optional[int] = None) -> Optional[np.ndarray]:
        """Generate Grad-CAM heatmap"""
        if not self.available or self.model is None or self.target_layer is None:
            return None
        
        try:
            from src.models.gradcam import GradCAM
            x = self.transform(im).unsqueeze(0).to(self.device).requires_grad_(True)
            cam = GradCAM(self.model, self.target_layer).generate(x, class_idx=class_idx)
            return cam.numpy()
            
        except Exception as e:
            logger.error(f"Grad-CAM generation failed: {e}")
            return None