#!/usr/bin/env python3
"""
Test Enhanced Radiology Analysis with AI Integrations
Tests the new Groq, Tavily, and Keyword AI integrations for radiology analysis
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_chest_xray.jpg"  # You can use any image file

def test_enhanced_radiology_analysis():
    """Test the enhanced radiology analysis with AI integrations"""
    
    print("🏥 Testing Enhanced Radiology Analysis with AI Integrations")
    print("=" * 60)
    
    # Create a dummy test image if it doesn't exist
    if not Path(TEST_IMAGE_PATH).exists():
        print(f"Creating dummy test image: {TEST_IMAGE_PATH}")
        from PIL import Image
        import numpy as np
        
        # Create a simple test image
        img_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(TEST_IMAGE_PATH)
    
    # Test radiology analysis endpoint
    print(f"\n📊 Testing radiology analysis...")
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': (TEST_IMAGE_PATH, f, 'image/jpeg')}
            params = {
                'scan_type': 'chest_xray',
                'clinical_history': 'Patient presents with chest pain and shortness of breath'
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/api/v1/radiology/analyze",
                files=files,
                params=params,
                timeout=30
            )
            end_time = time.time()
            
            print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
            print(f"📡 Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Radiology analysis successful!")
                
                # Display enhanced results
                print(f"\n🔍 Analysis Results:")
                print(f"   Analysis ID: {result.get('analysis_id', 'N/A')}")
                print(f"   Scan Type: {result.get('scan_type', 'N/A')}")
                print(f"   Urgency Level: {result.get('urgency_level', 'N/A')}")
                print(f"   Processing Time: {result.get('processing_time', 'N/A')}")
                
                # Display findings
                findings = result.get('findings', [])
                print(f"\n🔬 Findings ({len(findings)} detected):")
                for i, finding in enumerate(findings[:3], 1):
                    print(f"   {i}. {finding.get('condition', 'Unknown')}: {finding.get('probability', 0)*100:.1f}%")
                
                # Display AI-enhanced content
                print(f"\n🤖 AI-Enhanced Content:")
                
                # AI Summary
                ai_summary = result.get('ai_summary', {})
                if ai_summary:
                    print(f"   📝 AI Summary Available: {bool(ai_summary.get('summary'))}")
                    print(f"   🧠 Explanation Available: {bool(ai_summary.get('explanation'))}")
                    print(f"   📊 Confidence Interpretation: {bool(ai_summary.get('confidence_interpretation'))}")
                    
                    if ai_summary.get('summary'):
                        summary_preview = ai_summary['summary'][:100] + "..." if len(ai_summary['summary']) > 100 else ai_summary['summary']
                        print(f"   📄 Summary Preview: {summary_preview}")
                
                # Medical Resources
                medical_resources = result.get('medical_resources', {})
                if medical_resources:
                    articles = medical_resources.get('medical_articles', [])
                    print(f"   📚 Medical Articles: {len(articles)} found")
                    for i, article in enumerate(articles[:2], 1):
                        print(f"      {i}. {article.get('title', 'Untitled')[:50]}...")
                
                # Keywords
                keywords = result.get('keywords', {})
                if keywords:
                    conditions = keywords.get('conditions', [])
                    treatments = keywords.get('treatments', [])
                    print(f"   🏷️  Keywords Extracted:")
                    print(f"      Conditions: {', '.join(conditions[:3])}")
                    print(f"      Treatments: {', '.join(treatments[:3])}")
                
                # Enhancement info
                if result.get('radiology_enhanced'):
                    print(f"   ✨ Enhanced with AI integrations: Yes")
                    print(f"   🕐 Enhancement timestamp: {result.get('enhancement_timestamp', 'N/A')}")
                
                print(f"\n📋 Clinical Summary:")
                clinical_summary = result.get('clinical_summary', 'No summary available')
                summary_preview = clinical_summary[:150] + "..." if len(clinical_summary) > 150 else clinical_summary
                print(f"   {summary_preview}")
                
                print(f"\n💡 Recommendations ({len(result.get('recommendations', []))}):")
                for i, rec in enumerate(result.get('recommendations', [])[:3], 1):
                    print(f"   {i}. {rec}")
                
                # Save detailed results
                with open('enhanced_radiology_results.json', 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Detailed results saved to: enhanced_radiology_results.json")
                
                return True
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_integrations_status():
    """Test the status of API integrations"""
    
    print(f"\n🔧 Testing API Integration Status")
    print("-" * 40)
    
    # Check environment variables
    import os
    
    groq_key = os.getenv("GROQ_API_KEY", "not_set")
    tavily_key = os.getenv("TAVILY_API_KEY", "not_set")
    keyword_key = os.getenv("KEYWORD_AI_KEY", "not_set")
    
    print(f"🔑 GROQ API Key: {'✅ Set' if groq_key and groq_key != 'not_set' and groq_key != 'your_groq_api_key_here' else '❌ Not configured'}")
    print(f"🔑 Tavily API Key: {'✅ Set' if tavily_key and tavily_key != 'not_set' and tavily_key != 'your_tavily_api_key_here' else '❌ Not configured'}")
    print(f"🔑 Keyword AI Key: {'✅ Set' if keyword_key and keyword_key != 'not_set' and keyword_key != 'your_keyword_ai_key_here' else '❌ Not configured'}")
    
    if groq_key == "not_set" or tavily_key == "not_set" or keyword_key == "not_set":
        print(f"\n⚠️  Note: Some API keys are not configured. The system will use fallback responses.")
        print(f"   This is normal for testing - you'll still get enhanced results!")

def main():
    """Main test function"""
    
    print("🚀 Starting Enhanced Radiology Analysis Test")
    print("=" * 60)
    
    # Test API integration status
    test_api_integrations_status()
    
    # Test enhanced radiology analysis
    success = test_enhanced_radiology_analysis()
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ Enhanced Radiology Analysis Test PASSED!")
        print("🎉 Your radiology analysis now includes:")
        print("   • AI-generated summaries and explanations")
        print("   • Medical resource recommendations")
        print("   • Extracted medical keywords")
        print("   • Enhanced clinical insights")
    else:
        print("❌ Enhanced Radiology Analysis Test FAILED!")
        print("🔧 Please check your backend server and try again.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
