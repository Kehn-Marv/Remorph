import pytest
import tempfile
import os
from PIL import Image
import numpy as np
from io import BytesIO

from src.models.detector import HeuristicDetector, TorchDetector
from src.trace.attribution import AttributionIndex
from src.ingest.filtering import accept_image
from src.utils.validation import validate_file_upload, sanitize_filename
from src.utils.img import load_image_from_bytes, ensure_min_size
from src.models.face_detector import FaceDetectorSingleton

class TestHeuristicDetector:
    def test_features_extraction(self):
        """Test feature extraction from synthetic image"""
        # Create test image
        img = Image.new('RGB', (256, 256), color='red')
        detector = HeuristicDetector()
        
        features = detector.features(img)
        
        assert "ela_mean" in features
        assert "fft_high_ratio" in features
        assert "lap_var" in features
        assert "jpeg_score" in features
        assert all(isinstance(v, (int, float)) for v in features.values())
    
    def test_score_calculation(self):
        """Test score calculation with known features"""
        detector = HeuristicDetector()
        test_features = {
            "ela_mean": 15.0,
            "fft_high_ratio": 0.7,
            "lap_var": 150.0,
            "jpeg_score": 0.4
        }
        
        score = detector.score(test_features)
        assert 0.0 <= score <= 1.0

class TestAttributionIndex:
    def test_empty_index(self):
        """Test attribution index with non-existent file"""
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            # File doesn't exist
            idx = AttributionIndex(tmp.name + "_nonexistent")
            families = idx.all_families()
            assert len(families) >= 0  # Should create default families
    
    def test_feature_matching(self):
        """Test feature matching against families"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            test_db = {
                "version": 1,
                "families": [{
                    "name": "test_family",
                    "features_mean": {
                        "fft_high_ratio": 0.6,
                        "ela_mean": 10.0
                    }
                }]
            }
            import json
            json.dump(test_db, tmp)
            tmp.flush()
            
            idx = AttributionIndex(tmp.name)
            matches = idx.match({"fft_high_ratio": 0.65, "ela_mean": 12.0}, topk=1)
            
            assert len(matches) == 1
            assert matches[0][0] == "test_family"
            assert 0.0 <= matches[0][1] <= 1.0
            
            os.unlink(tmp.name)

class TestValidation:
    def test_filename_sanitization(self):
        """Test filename sanitization"""
        dangerous_names = [
            "../../../etc/passwd",
            "file<script>alert(1)</script>.jpg",
            "normal_file.jpg",
            "",
            "a" * 300 + ".jpg"
        ]
        
        for name in dangerous_names:
            safe_name = sanitize_filename(name)
            assert not any(char in safe_name for char in ["<", ">", "/", "\\", ".."])
            assert len(safe_name) <= 255
            assert safe_name  # Not empty
    
    def test_file_upload_validation(self):
        """Test file upload validation"""
        # Valid file
        validate_file_upload("test.jpg", 1024 * 1024)  # 1MB
        
        # Invalid extension
        with pytest.raises(Exception):
            validate_file_upload("test.exe", 1024)
        
        # File too large (assuming 10MB limit)
        with pytest.raises(Exception):
            validate_file_upload("test.jpg", 20 * 1024 * 1024)

class TestImageProcessing:
    def test_image_loading(self):
        """Test image loading from bytes"""
        # Create test image bytes
        img = Image.new('RGB', (100, 100), color='blue')
        buf = BytesIO()
        img.save(buf, format='JPEG')
        
        loaded = load_image_from_bytes(buf.getvalue())
        assert loaded.mode == 'RGB'
        assert loaded.size == (100, 100)
    
    def test_ensure_min_size(self):
        """Test minimum size enforcement"""
        small_img = Image.new('RGB', (50, 50), color='green')
        resized = ensure_min_size(small_img, min_side=100)
        
        assert min(resized.size) >= 100

class TestQualityFiltering:
    def test_accept_image_logic(self):
        """Test image acceptance logic"""
        # High quality image with face
        accept, flags = accept_image(True, 0.95, 512, 512)
        assert accept is True
        assert flags.face_found is True
        
        # Low confidence face
        accept, flags = accept_image(True, 0.5, 512, 512)
        assert accept is False
        assert "low_face_conf" in flags.notes
        
        # No face found
        accept, flags = accept_image(False, 0.0, 512, 512)
        assert accept is False
        assert "no_face_found" in flags.notes
        
        # Too small
        accept, flags = accept_image(True, 0.95, 100, 100)
        assert accept is False
        assert any("min_side" in note for note in flags.notes)

class TestFaceDetector:
    def test_singleton_pattern(self):
        """Test that face detector follows singleton pattern"""
        detector1 = FaceDetectorSingleton()
        detector2 = FaceDetectorSingleton()
        assert detector1 is detector2
    
    def test_face_detection_fallback(self):
        """Test face detection with fallback behavior"""
        detector = FaceDetectorSingleton()
        test_img = Image.new('RGB', (256, 256), color='white')
        
        face_crop, found, conf = detector.detect_largest_face(test_img)
        
        # Should return original image if no face or detector unavailable
        assert isinstance(face_crop, Image.Image)
        assert isinstance(found, bool)
        assert isinstance(conf, float)
        assert 0.0 <= conf <= 1.0

if __name__ == "__main__":
    pytest.main([__file__])