from fastapi import APIRouter, HTTPException
from src.config import FINGERPRINTS_PATH
from src.trace.attribution import AttributionIndex
from src.utils.logging import setup_logger, log_error

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/stats")
def get_stats():
    """Get system and attribution statistics"""
    try:
        attribution_idx = AttributionIndex(FINGERPRINTS_PATH)
        stats = attribution_idx.get_family_stats()
        
        return {
            "attribution": stats,
            "system": {
                "fingerprints_path": FINGERPRINTS_PATH,
                "total_families": stats["total_families"]
            }
        }
        
    except Exception as e:
        log_error(logger, e, "stats retrieval")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")

@router.get("/families")
def get_families():
    """Get all attribution families"""
    try:
        attribution_idx = AttributionIndex(FINGERPRINTS_PATH)
        families = attribution_idx.all_families()
        
        return {
            "families": families,
            "count": len(families)
        }
        
    except Exception as e:
        log_error(logger, e, "families retrieval")
        raise HTTPException(status_code=500, detail="Failed to retrieve families")