#!/usr/bin/env python3
"""
Test script to verify GROQ, Tavily, and Keyword AI integrations
Tests enhanced analysis pipeline for both skin and radiology modules
"""

import requests
import time
from PIL import Image
import io
import json

def create_test_images():
    """Create test images for API integration testing"""
    images = {}
    
    # Skin lesion test image (reddish)
    skin_lesion = Image.new('RGB', (400, 300), color=(180, 100, 80))
    skin_bytes = io.BytesIO()
    skin_lesion.save(skin_bytes, format='JPEG')
    skin_bytes.seek(0)
    images['skin_lesion'] = ('skin_lesion.jpg', skin_bytes, 'image/jpeg')
    
    # Chest X-ray test image (grayscale-like)
    chest_xray = Image.new('RGB', (512, 512), color=(120, 120, 120))
    chest_bytes = io.BytesIO()
    chest_xray.save(chest_bytes, format='JPEG')
    chest_bytes.seek(0)
    images['chest_xray'] = ('chest_xray.jpg', chest_bytes, 'image/jpeg')
    
    return images

def test_skin_analysis_with_apis(image_data):
    """Test skin analysis with API enhancements"""
    try:
        files = {'file': image_data}
        response = requests.post(
            'http://localhost:8000/api/v1/skin-analysis/analyze',
            files=files,
            timeout=60  # Longer timeout for API calls
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'basic_analysis': {
                    'top_prediction': result.get('top_prediction'),
                    'confidence': result.get('confidence'),
                    'risk_level': result.get('risk_level')
                },
                'api_enhancements': {
                    'ai_explanation': result.get('ai_explanation'),
                    'medical_references': result.get('medical_references'),
                    'medical_keywords': result.get('medical_keywords')
                },
                'processing_time': result.get('processing_time_seconds'),
                'analysis_id': result.get('analysis_id')
            }
        else:
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def test_radiology_analysis_with_apis(image_data):
    """Test radiology analysis with API enhancements"""
    try:
        files = {'file': image_data}
        response = requests.post(
            'http://localhost:8000/api/v1/radiology/analyze?scan_type=chest_xray',
            files=files,
            timeout=60  # Longer timeout for API calls
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'basic_analysis': {
                    'findings': result.get('findings'),
                    'urgency_level': result.get('urgency_level')
                },
                'api_enhancements': {
                    'ai_explanation': result.get('ai_explanation'),
                    'medical_references': result.get('medical_references'),
                    'medical_keywords': result.get('medical_keywords')
                },
                'processing_time': result.get('processing_time_seconds'),
                'analysis_id': result.get('analysis_id')
            }
        else:
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def test_api_services_status():
    """Test API services status"""
    try:
        response = requests.get('http://localhost:8000/api/v1/system/status', timeout=10)
        if response.status_code == 200:
            status = response.json()
            return {
                'success': True,
                'status': status.get('status'),
                'version': status.get('version'),
                'models': status.get('models', {}),
                'endpoints': status.get('endpoints', {})
            }
        else:
            return {
                'success': False,
                'error': f"Status check failed: {response.status_code}"
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def run_api_integration_tests():
    """Run comprehensive API integration tests"""
    print("🚀 MediScan-AI API Integration Test Suite")
    print("=" * 60)
    
    # Test system status first
    print("\n🔍 Testing System Status...")
    status_result = test_api_services_status()
    if status_result['success']:
        print(f"✅ System Status: {status_result['status']}")
        print(f"   Version: {status_result['version']}")
        if status_result.get('models'):
            models_info = status_result['models']
            print(f"   Models loaded: {models_info.get('models_loaded', [])}")
            print(f"   GPU available: {models_info.get('gpu_available', False)}")
    else:
        print(f"❌ System Status Failed: {status_result['error']}")
        return
    
    # Create test images
    print("\n📸 Creating test images...")
    test_images = create_test_images()
    
    # Test Skin Analysis with API Enhancements
    print("\n🔬 Testing Skin Analysis with API Enhancements")
    print("-" * 50)
    
    skin_image = test_images['skin_lesion']
    skin_image[1].seek(0)
    skin_result = test_skin_analysis_with_apis(skin_image)
    
    if skin_result['success']:
        print("✅ Skin Analysis: SUCCESS")
        
        # Basic analysis
        basic = skin_result['basic_analysis']
        print(f"   📊 Prediction: {basic['top_prediction']} ({basic['confidence']:.1%})")
        print(f"   ⚠️  Risk Level: {basic['risk_level']}")
        print(f"   ⏱️  Processing Time: {skin_result['processing_time']:.2f}s")
        
        # API enhancements
        enhancements = skin_result['api_enhancements']
        
        # GROQ AI Explanation
        if enhancements.get('ai_explanation'):
            ai_exp = enhancements['ai_explanation']
            print(f"   🤖 GROQ Explanation: {'✅ Available' if ai_exp.get('summary') else '❌ Missing'}")
            if ai_exp.get('summary'):
                print(f"      Summary: {ai_exp['summary'][:100]}...")
        else:
            print("   🤖 GROQ Explanation: ❌ Not available")
        
        # Tavily Medical References
        if enhancements.get('medical_references'):
            refs = enhancements['medical_references']
            print(f"   📚 Tavily References: ✅ {len(refs)} references found")
            for i, ref in enumerate(refs[:2]):  # Show first 2
                print(f"      {i+1}. {ref.get('title', 'No title')[:50]}...")
                print(f"         Source: {ref.get('source', 'Unknown')}")
        else:
            print("   📚 Tavily References: ❌ Not available")
        
        # Keyword AI Terms
        if enhancements.get('medical_keywords'):
            keywords = enhancements['medical_keywords']
            print(f"   🏷️  Keyword AI: ✅ {len(keywords)} keywords extracted")
            print(f"      Keywords: {', '.join(keywords[:5])}")
        else:
            print("   🏷️  Keyword AI: ❌ Not available")
            
    else:
        print(f"❌ Skin Analysis Failed: {skin_result['error']}")
    
    # Test Radiology Analysis with API Enhancements
    print("\n🩻 Testing Radiology Analysis with API Enhancements")
    print("-" * 50)
    
    radiology_image = test_images['chest_xray']
    radiology_image[1].seek(0)
    radiology_result = test_radiology_analysis_with_apis(radiology_image)
    
    if radiology_result['success']:
        print("✅ Radiology Analysis: SUCCESS")
        
        # Basic analysis
        basic = radiology_result['basic_analysis']
        findings = basic.get('findings', [])
        print(f"   📊 Findings: {len(findings)} detected")
        if findings:
            for finding in findings[:2]:  # Show first 2
                print(f"      - {finding.get('condition')} ({finding.get('confidence', 0):.1%})")
        print(f"   ⚠️  Urgency: {basic.get('urgency_level', 'unknown')}")
        print(f"   ⏱️  Processing Time: {radiology_result['processing_time']:.2f}s")
        
        # API enhancements
        enhancements = radiology_result['api_enhancements']
        
        # GROQ AI Explanation
        if enhancements.get('ai_explanation'):
            ai_exp = enhancements['ai_explanation']
            print(f"   🤖 GROQ Explanation: {'✅ Available' if ai_exp.get('summary') else '❌ Missing'}")
            if ai_exp.get('summary'):
                print(f"      Summary: {ai_exp['summary'][:100]}...")
        else:
            print("   🤖 GROQ Explanation: ❌ Not available")
        
        # Tavily Medical References
        if enhancements.get('medical_references'):
            refs = enhancements['medical_references']
            print(f"   📚 Tavily References: ✅ {len(refs)} references found")
            for i, ref in enumerate(refs[:2]):  # Show first 2
                print(f"      {i+1}. {ref.get('title', 'No title')[:50]}...")
                print(f"         Source: {ref.get('source', 'Unknown')}")
        else:
            print("   📚 Tavily References: ❌ Not available")
        
        # Keyword AI Terms
        if enhancements.get('medical_keywords'):
            keywords = enhancements['medical_keywords']
            print(f"   🏷️  Keyword AI: ✅ {len(keywords)} keywords extracted")
            print(f"      Keywords: {', '.join(keywords[:5])}")
        else:
            print("   🏷️  Keyword AI: ❌ Not available")
            
    else:
        print(f"❌ Radiology Analysis Failed: {radiology_result['error']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 API INTEGRATION SUMMARY")
    print("=" * 60)
    
    skin_success = skin_result.get('success', False)
    radiology_success = radiology_result.get('success', False)
    
    print(f"\n🎯 Overall Results:")
    print(f"   Skin Analysis: {'✅ PASS' if skin_success else '❌ FAIL'}")
    print(f"   Radiology Analysis: {'✅ PASS' if radiology_success else '❌ FAIL'}")
    
    if skin_success and radiology_success:
        print(f"\n🎉 All API integrations working successfully!")
        
        # Check API enhancement coverage
        skin_enhancements = skin_result.get('api_enhancements', {})
        radiology_enhancements = radiology_result.get('api_enhancements', {})
        
        groq_working = (skin_enhancements.get('ai_explanation') and 
                       radiology_enhancements.get('ai_explanation'))
        tavily_working = (skin_enhancements.get('medical_references') and 
                         radiology_enhancements.get('medical_references'))
        keyword_working = (skin_enhancements.get('medical_keywords') and 
                          radiology_enhancements.get('medical_keywords'))
        
        print(f"\n🔧 API Service Status:")
        print(f"   GROQ API: {'✅ Working' if groq_working else '⚠️  Limited/Not working'}")
        print(f"   Tavily API: {'✅ Working' if tavily_working else '⚠️  Limited/Not working'}")
        print(f"   Keyword AI: {'✅ Working' if keyword_working else '⚠️  Limited/Not working'}")
        
        if groq_working and tavily_working and keyword_working:
            print(f"\n🚀 Full API integration pipeline operational!")
        else:
            print(f"\n⚠️  Some API services may need configuration or have rate limits")
    else:
        print(f"\n❌ Some tests failed - check backend logs and API configurations")
    
    print("\n✅ API integration testing completed!")

if __name__ == "__main__":
    try:
        run_api_integration_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
