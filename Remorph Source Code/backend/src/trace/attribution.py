import json
import math
import os
from typing import Dict, List, Tuple, Any
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class AttributionIndex:
    """Enhanced attribution index with better error handling and persistence"""
    
    def __init__(self, path: str):
        self.path = path
        self.db = {"version": 1, "families": []}
        self._load()

    def _load(self):
        """Load fingerprints database with error handling"""
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    self.db = json.load(f)
                logger.info(f"Loaded {len(self.db.get('families', []))} attribution families")
            else:
                logger.warning(f"Fingerprints file not found: {self.path}")
                self._create_default_db()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in fingerprints file: {e}")
            self._create_default_db()
        except Exception as e:
            logger.error(f"Failed to load fingerprints: {e}")
            self._create_default_db()

    def _create_default_db(self):
        """Create default fingerprints database"""
        self.db = {
            "version": 1,
            "families": [
                {
                    "name": "faceswap_blend",
                    "features_mean": {
                        "fft_high_ratio": 0.62,
                        "ela_mean": 18.0,
                        "lap_var": 120.0,
                        "jpeg_score": 0.55
                    },
                    "sample_count": 0,
                    "last_updated": None
                },
                {
                    "name": "diffusion_inpaint",
                    "features_mean": {
                        "fft_high_ratio": 0.68,
                        "ela_mean": 12.0,
                        "lap_var": 160.0,
                        "jpeg_score": 0.35
                    },
                    "sample_count": 0,
                    "last_updated": None
                },
                {
                    "name": "stylegan_family",
                    "features_mean": {
                        "fft_high_ratio": 0.75,
                        "ela_mean": 9.5,
                        "lap_var": 180.0,
                        "jpeg_score": 0.4
                    },
                    "sample_count": 0,
                    "last_updated": None
                }
            ]
        }
        self._save()
        logger.info("Created default fingerprints database")

    def _save(self):
        """Save fingerprints database"""
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.db, f, indent=2)
            logger.debug("Fingerprints database saved")
        except Exception as e:
            logger.error(f"Failed to save fingerprints: {e}")

    def all_families(self) -> List[str]:
        """Get all family names"""
        return [f["name"] for f in self.db.get("families", [])]

    def match(self, feats: Dict[str, float], topk: int = 3) -> List[Tuple[str, float]]:
        """
        Match features against known families using cosine similarity.
        Returns list of (family_name, similarity_score) tuples.
        """
        if not feats:
            logger.warning("No features provided for attribution matching")
            return []
        
        results = []
        
        for family in self.db.get("families", []):
            try:
                family_features = family.get("features_mean", {})
                
                # Find overlapping feature keys
                common_keys = [k for k in family_features.keys() if k in feats]
                
                if not common_keys:
                    logger.debug(f"No common features with family {family['name']}")
                    continue
                
                # Calculate cosine similarity
                query_vector = [feats[k] for k in common_keys]
                family_vector = [family_features[k] for k in common_keys]
                
                dot_product = sum(x * y for x, y in zip(query_vector, family_vector))
                norm_query = math.sqrt(sum(x * x for x in query_vector)) + 1e-8
                norm_family = math.sqrt(sum(y * y for y in family_vector)) + 1e-8
                
                similarity = dot_product / (norm_query * norm_family)
                results.append((family["name"], float(similarity)))
                
            except Exception as e:
                logger.error(f"Error matching family {family.get('name', 'unknown')}: {e}")
                continue
        
        # Sort by similarity (highest first) and return top-k
        results.sort(key=lambda x: x[1], reverse=True)
        top_results = results[:topk]
        
        logger.debug(f"Attribution matching: {len(results)} families, top match: {top_results[0] if top_results else 'none'}")
        
        return top_results

    def add_sample(self, family_name: str, features: Dict[str, float]) -> bool:
        """
        Add a new sample to update family fingerprints.
        Uses incremental averaging for online learning.
        """
        try:
            family = None
            for f in self.db["families"]:
                if f["name"] == family_name:
                    family = f
                    break
            
            if family is None:
                # Create new family
                family = {
                    "name": family_name,
                    "features_mean": features.copy(),
                    "sample_count": 1,
                    "last_updated": datetime.now().isoformat()
                }
                self.db["families"].append(family)
                logger.info(f"Created new attribution family: {family_name}")
            else:
                # Update existing family with incremental averaging
                n = family.get("sample_count", 0)
                current_features = family.get("features_mean", {})
                
                for key, value in features.items():
                    if key in current_features:
                        # Incremental average: new_avg = old_avg + (new_value - old_avg) / (n + 1)
                        current_features[key] += (value - current_features[key]) / (n + 1)
                    else:
                        current_features[key] = value
                
                family["features_mean"] = current_features
                family["sample_count"] = n + 1
                family["last_updated"] = datetime.now().isoformat()
                
                logger.info(f"Updated attribution family {family_name}: {n + 1} samples")
            
            self._save()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add sample to family {family_name}: {e}")
            return False

    def get_family_stats(self) -> Dict[str, Any]:
        """Get statistics about the attribution database"""
        families = self.db.get("families", [])
        total_samples = sum(f.get("sample_count", 0) for f in families)
        
        return {
            "total_families": len(families),
            "total_samples": total_samples,
            "families": [
                {
                    "name": f["name"],
                    "sample_count": f.get("sample_count", 0),
                    "last_updated": f.get("last_updated")
                }
                for f in families
            ]
        }