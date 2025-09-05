from dataclasses import dataclass
from typing import List
from src.config import FACE_CONFIDENCE_THRESHOLD, QUALITY_MIN_SIDE
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

@dataclass
class QualityFlags:
    face_found: bool
    face_conf: float
    width: int
    height: int
    min_side_ok: bool
    notes: List[str]

def accept_image(
    face_found: bool, 
    face_conf: float, 
    width: int, 
    height: int, 
    min_side: int = None
) -> tuple[bool, QualityFlags]:
    """
    Determine if image meets quality standards for learning.
    Uses configurable thresholds.
    """
    if min_side is None:
        min_side = QUALITY_MIN_SIDE
    
    notes = []
    min_side_ok = min(width, height) >= min_side
    
    if not min_side_ok:
        notes.append(f"min_side<{min_side}")
    
    if not face_found:
        notes.append("no_face_found")
    
    if face_found and face_conf < FACE_CONFIDENCE_THRESHOLD:
        notes.append(f"low_face_conf<{FACE_CONFIDENCE_THRESHOLD}")
    
    # Accept if face found with good confidence and meets size requirements
    accept = (face_found and face_conf >= FACE_CONFIDENCE_THRESHOLD and min_side_ok)
    
    flags = QualityFlags(face_found, face_conf, width, height, min_side_ok, notes)
    
    logger.debug(f"Quality assessment: accept={accept}, flags={flags}")
    
    return accept, flags