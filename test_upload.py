#!/usr/bin/env python3
"""
Test script to verify MediScan-AI backend functionality
"""

import requests
import os
from PIL import Image
import io

# Create a simple test image
def create_test_image():
    """Create a simple test image for testing"""
    img = Image.new('RGB', (224, 224), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:8000/api/v1/health')
        print(f"Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
            return True
    except Exception as e:
        print(f"Health endpoint error: {e}")
    return False

def test_skin_analysis():
    """Test skin cancer analysis endpoint"""
    try:
        test_image = create_test_image()
        files = {'file': ('test_image.jpg', test_image, 'image/jpeg')}
        
        response = requests.post(
            'http://localhost:8000/api/v1/skin-analysis/analyze',
            files=files
        )
        
        print(f"Skin analysis status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Skin analysis result: {result}")
            return True
        else:
            print(f"Skin analysis error: {response.text}")
    except Exception as e:
        print(f"Skin analysis error: {e}")
    return False

def test_radiology_analysis():
    """Test radiology analysis endpoint"""
    try:
        test_image = create_test_image()
        files = {'file': ('test_xray.jpg', test_image, 'image/jpeg')}
        
        response = requests.post(
            'http://localhost:8000/api/v1/radiology/analyze?scan_type=chest_xray',
            files=files
        )
        
        print(f"Radiology analysis status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Radiology analysis result: {result}")
            return True
        else:
            print(f"Radiology analysis error: {response.text}")
    except Exception as e:
        print(f"Radiology analysis error: {e}")
    return False

def test_triage_assessment():
    """Test triage assessment endpoint"""
    try:
        data = {
            "symptoms": "I have a headache and feel dizzy",
            "language": "en"
        }
        
        response = requests.post(
            'http://localhost:8000/api/v1/triage/assess',
            json=data
        )
        
        print(f"Triage assessment status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Triage assessment result: {result}")
            return True
        else:
            print(f"Triage assessment error: {response.text}")
    except Exception as e:
        print(f"Triage assessment error: {e}")
    return False

if __name__ == "__main__":
    print("Testing MediScan-AI Backend Endpoints")
    print("=" * 50)
    
    # Test all endpoints
    tests = [
        ("Health Check", test_health_endpoint),
        ("Skin Analysis", test_skin_analysis),
        ("Radiology Analysis", test_radiology_analysis),
        ("Triage Assessment", test_triage_assessment)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        success = test_func()
        results.append((test_name, success))
        print(f"✅ {test_name}: {'PASSED' if success else 'FAILED'}")
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
