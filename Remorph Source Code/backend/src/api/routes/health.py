import os
import psutil
from datetime import datetime
import psutil
from fastapi import APIRouter
from src.config import OUTPUT_DIR, FINGERPRINTS_PATH, WEIGHTS_PATH
from src.utils.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/health")
def health():
    """Enhanced health check with system information"""
    try:
        # Check system resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check file system
        output_exists = os.path.exists(OUTPUT_DIR)
        fingerprints_exist = os.path.exists(FINGERPRINTS_PATH)
        weights_exist = os.path.exists(WEIGHTS_PATH)
        
        # Check face detection availability
        face_detector_available = False
        try:
            from src.models.face_detector import face_detector
            face_detector_available = face_detector._available
        except Exception:
            pass
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "memory_usage_percent": memory.percent,
                "disk_usage_percent": disk.percent,
                "available_memory_gb": round(memory.available / (1024**3), 2)
            },
            "components": {
                "output_directory": output_exists,
                "fingerprints_db": fingerprints_exist,
                "torch_weights": weights_exist,
                "face_detector": face_detector_available
            },
            "paths": {
                "output_dir": OUTPUT_DIR,
                "fingerprints": FINGERPRINTS_PATH,
                "weights": WEIGHTS_PATH
            }
        }
        
        logger.debug("Health check completed successfully")
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/detailed")
def detailed_health():
    """Detailed health check with component testing"""
    try:
        from datetime import datetime
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Test heuristic detector
        try:
            from src.models.detector import HeuristicDetector
            detector = HeuristicDetector()
            results["components"]["heuristic_detector"] = "available"
        except Exception as e:
            results["components"]["heuristic_detector"] = f"error: {str(e)}"
        
        # Test torch detector
        try:
            from src.models.detector import TorchDetector
            torch_det = TorchDetector(WEIGHTS_PATH)
            results["components"]["torch_detector"] = "available" if torch_det.available else "weights_not_found"
        except Exception as e:
            results["components"]["torch_detector"] = f"error: {str(e)}"
        
        # Test attribution index
        try:
            from src.trace.attribution import AttributionIndex
            idx = AttributionIndex(FINGERPRINTS_PATH)
            families = idx.all_families()
            results["components"]["attribution_index"] = f"available ({len(families)} families)"
        except Exception as e:
            results["components"]["attribution_index"] = f"error: {str(e)}"
        
        return results
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}