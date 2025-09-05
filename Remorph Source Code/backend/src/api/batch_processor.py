import asyncio
import uuid
from typing import List, Dict, Any
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from src.utils.logging import setup_logger
from src.models.face_detector import face_detector
from src.models.detector import HeuristicDetector, TorchDetector
from src.config import WEIGHTS_PATH

logger = setup_logger(__name__)

class BatchProcessor:
    """Process multiple images concurrently"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.heuristic_detector = HeuristicDetector()
        self.torch_detector = TorchDetector(WEIGHTS_PATH, device="cpu")
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def _process_single_image(self, image_data: tuple) -> Dict[str, Any]:
        """Process a single image (runs in thread)"""
        image_id, image = image_data
        
        try:
            # Face detection
            face_im, face_found, face_conf = face_detector.detect_largest_face(image)
            
            # Heuristic analysis
            heuristic_result = self.heuristic_detector.analyze(face_im)
            
            # Torch analysis if available
            torch_result = self.torch_detector.predict(face_im)
            
            return {
                "id": image_id,
                "success": True,
                "face_found": face_found,
                "face_confidence": face_conf,
                "heuristic_score": heuristic_result["score"],
                "features": heuristic_result["features"],
                "torch_available": torch_result.get("available", False),
                "torch_probs": torch_result.get("probs", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to process image {image_id}: {e}")
            return {
                "id": image_id,
                "success": False,
                "error": str(e)
            }
    
    async def process_batch(self, images: List[Image.Image]) -> List[Dict[str, Any]]:
        """Process multiple images concurrently"""
        if not images:
            return []
        
        logger.info(f"Starting batch processing of {len(images)} images")
        
        # Assign IDs to images
        image_data = [(str(uuid.uuid4())[:8], img) for img in images]
        
        # Process in thread pool
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(self.executor, self._process_single_image, data)
            for data in image_data
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch processing exception for image {i}: {result}")
                processed_results.append({
                    "id": image_data[i][0],
                    "success": False,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        successful = sum(1 for r in processed_results if r.get("success", False))
        logger.info(f"Batch processing complete: {successful}/{len(images)} successful")
        
        return processed_results
    
    def __del__(self):
        """Cleanup thread pool"""
        try:
            self.executor.shutdown(wait=False)
        except Exception:
            pass

# Global batch processor instance
batch_processor = BatchProcessor()