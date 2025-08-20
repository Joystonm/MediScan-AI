#!/usr/bin/env python3
"""
Simple API Integration Test
Tests if the API keys are working and services are accessible
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.api_integrations import APIIntegrationService

async def test_api_integrations():
    """Test API integrations with simple calls"""
    
    print("🧪 Testing MediScan-AI API Integrations")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check API keys
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    keyword_key = os.getenv("KEYWORD_AI_KEY")
    
    print(f"GROQ API Key: {'✓ Configured' if groq_key and groq_key != 'your_groq_api_key_here' else '✗ Missing/Invalid'}")
    print(f"Tavily API Key: {'✓ Configured' if tavily_key and tavily_key != 'your_tavily_api_key_here' else '✗ Missing/Invalid'}")
    print(f"Keyword AI Key: {'✓ Configured' if keyword_key and keyword_key != 'your_keyword_ai_key_here' else '✗ Missing/Invalid'}")
    print()
    
    # Test the integration service
    try:
        api_service = APIIntegrationService()
        
        print("🔬 Testing API Enhancement...")
        result = await api_service.enhance_analysis_results(
            prediction="Basal cell carcinoma",
            confidence=0.73,
            risk_level="MEDIUM",
            recommendations=[
                "Schedule dermatologist appointment within 2-4 weeks",
                "Monitor lesion for changes",
                "Consider dermoscopy for detailed examination"
            ],
            analysis_type="skin"
        )
        
        print("✅ API Enhancement Test Completed!")
        print()
        
        # Check results
        ai_summary = result.get("ai_summary", {})
        medical_resources = result.get("medical_resources", {})
        keywords = result.get("keywords", {})
        
        print("📊 Results Summary:")
        print(f"  AI Summary: {'✓ Available' if ai_summary.get('summary') and ai_summary['summary'] != 'Enhancement unavailable' else '✗ Unavailable'}")
        print(f"  Medical Resources: {'✓ Available' if medical_resources.get('medical_articles') or medical_resources.get('reference_images') else '✗ Unavailable'}")
        print(f"  Keywords: {'✓ Available' if any(keywords.get(k, []) for k in ['conditions', 'symptoms', 'treatments', 'procedures', 'general']) else '✗ Unavailable'}")
        
        if ai_summary.get('summary') and ai_summary['summary'] != 'Enhancement unavailable':
            print(f"\n📝 Sample AI Summary:")
            print(f"  {ai_summary['summary'][:100]}...")
        
        if medical_resources.get('medical_articles'):
            print(f"\n📚 Sample Medical Articles: {len(medical_resources['medical_articles'])} found")
            
        if keywords.get('conditions'):
            print(f"\n🏷️ Sample Keywords: {', '.join(keywords['conditions'][:3])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API integrations: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_integrations())
    if success:
        print("\n🎉 API integration test completed!")
    else:
        print("\n⚠️ API integration test failed!")
    
    sys.exit(0 if success else 1)
