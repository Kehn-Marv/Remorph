#!/usr/bin/env python3
"""
API testing script for Remorph.
Tests all endpoints with sample data.
"""

import requests
import os
from PIL import Image
import io

def create_test_image(size=(256, 256), color='red'):
    """Create a test image for API testing"""
    img = Image.new('RGB', size, color=color)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

def test_health_endpoint(base_url):
    """Test health endpoints"""
    print("Testing health endpoints...")
    
    try:
        # Basic health
        response = requests.get(f"{base_url}/health")
        print(f"Health: {response.status_code}")
        if response.status_code == 200:
            print(f"  Status: {response.json().get('status', 'unknown')}")
        
        # Detailed health
        response = requests.get(f"{base_url}/health/detailed")
        print(f"Detailed health: {response.status_code}")
        
    except Exception as e:
        print(f"Health test failed: {e}")

def test_stats_endpoints(base_url):
    """Test statistics endpoints"""
    print("Testing stats endpoints...")
    
    try:
        # Stats
        response = requests.get(f"{base_url}/stats")
        print(f"Stats: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Families: {data.get('attribution', {}).get('total_families', 0)}")
        
        # Families
        response = requests.get(f"{base_url}/families")
        print(f"Families: {response.status_code}")
        
    except Exception as e:
        print(f"Stats test failed: {e}")

def test_analyze_endpoint(base_url):
    """Test image analysis endpoint"""
    print("Testing analyze endpoint...")
    
    try:
        # Create test image
        test_img = create_test_image()
        
        files = {'file': ('test.jpg', test_img, 'image/jpeg')}
        response = requests.post(f"{base_url}/analyze", files=files)
        
        print(f"Analyze: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Analysis ID: {data.get('id', 'unknown')}")
            print(f"  Face found: {data.get('face', {}).get('found', False)}")
            print(f"  Heuristic score: {data.get('scores', {}).get('heuristic_deepfake_score', 0):.3f}")
            
            # Test file URLs
            heatmap_url = data.get('files', {}).get('heatmap_url', '')
            if heatmap_url:
                file_response = requests.get(f"{base_url}{heatmap_url}")
                print(f"  Heatmap file: {file_response.status_code}")
        
    except Exception as e:
        print(f"Analyze test failed: {e}")

def main():
    base_url = "http://localhost:8080"

    print(f"Testing Remorph API at {base_url}")
    print("=" * 50)
    
    # Test all endpoints
    test_health_endpoint(base_url)
    print()
    test_stats_endpoints(base_url)
    print()
    test_analyze_endpoint(base_url)
    
    print("\nAPI testing complete!")

if __name__ == "__main__":
    main()