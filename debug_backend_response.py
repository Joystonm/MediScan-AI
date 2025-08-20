#!/usr/bin/env python3
"""
Debug Backend Response
Check what the backend is actually returning for skin analysis
"""

import requests
import json
from pathlib import Path

def test_backend_response():
    """Test what the backend actually returns"""
    
    print("🔍 Testing Backend Response")
    print("=" * 50)
    
    # Test with a simple image upload
    backend_url = "http://localhost:8000"
    
    try:
        # Test health endpoint first
        print("1. Testing health endpoint...")
        health_response = requests.get(f"{backend_url}/api/v1/health")
        print(f"   Health Status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend not responding")
            return
        
        # Create a test image file
        print("\n2. Creating test image...")
        import io
        from PIL import Image
        import numpy as np
        
        # Create a simple test image
        test_image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
        
        # Save to bytes
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        print("   ✅ Test image created")
        
        # Test skin analysis endpoint
        print("\n3. Testing skin analysis endpoint...")
        
        files = {
            'image': ('test.jpg', img_bytes, 'image/jpeg')
        }
        
        response = requests.post(
            f"{backend_url}/api/v1/skin-analysis/analyze",
            files=files,
            timeout=30
        )
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n📊 Backend Response Analysis:")
            print(f"   Top Prediction: {result.get('top_prediction', 'Missing')}")
            print(f"   Confidence: {result.get('confidence', 'Missing')}")
            print(f"   Risk Level: {result.get('risk_level', 'Missing')}")
            
            # Check AI Summary
            ai_summary = result.get('ai_summary', {})
            print(f"\n🧠 AI Summary:")
            print(f"   Has Summary: {'✅' if ai_summary.get('summary') else '❌'}")
            print(f"   Summary Length: {len(ai_summary.get('summary', ''))}")
            print(f"   Has Explanation: {'✅' if ai_summary.get('explanation') else '❌'}")
            print(f"   Explanation Length: {len(ai_summary.get('explanation', ''))}")
            
            if ai_summary.get('summary'):
                print(f"   Summary Preview: {ai_summary.get('summary', '')[:100]}...")
            
            # Check Medical Resources
            resources = result.get('medical_resources', {})
            articles = resources.get('medical_articles', [])
            print(f"\n📚 Medical Resources:")
            print(f"   Articles Count: {len(articles)}")
            
            if articles:
                print(f"   First Article: {articles[0].get('title', 'No title')[:50]}...")
            
            # Check Keywords
            keywords = result.get('keywords', {})
            total_keywords = sum(len(v) for k, v in keywords.items() if isinstance(v, list))
            print(f"\n🏷️ Keywords:")
            print(f"   Total Keywords: {total_keywords}")
            
            for category in ['conditions', 'symptoms', 'treatments', 'procedures', 'general']:
                count = len(keywords.get(category, []))
                if count > 0:
                    print(f"   {category.title()}: {count}")
            
            # Check if data is actually there
            has_content = (
                ai_summary.get('summary') or 
                len(articles) > 0 or 
                total_keywords > 0
            )
            
            print(f"\n🎯 Content Analysis:")
            print(f"   Has Actual Content: {'✅' if has_content else '❌'}")
            
            if has_content:
                print("   ✅ Backend is returning real data!")
                print("   🔍 Issue is likely in frontend display logic")
            else:
                print("   ❌ Backend is not returning content")
                print("   🔍 Issue is in backend data generation")
            
            # Save full response for debugging
            with open('backend_response_debug.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Full response saved to: backend_response_debug.json")
            
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_backend_response()
