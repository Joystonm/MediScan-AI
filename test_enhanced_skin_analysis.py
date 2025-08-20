#!/usr/bin/env python3
"""
Test Enhanced Skin Analysis
Verifies that the skin analysis endpoint returns enhanced data
"""

import asyncio
import os
import sys
from pathlib import Path
import json

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

async def test_enhanced_skin_analysis():
    """Test the enhanced skin analysis functionality"""
    
    print("🔬 Testing Enhanced Skin Analysis")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # Import the services
        from app.services.api_integrations import APIIntegrationService
        from app.services.skin_analysis_service import SkinAnalysisService
        
        # Initialize services
        api_service = APIIntegrationService()
        skin_service = SkinAnalysisService()
        
        print("✅ Services initialized successfully")
        
        # Test skin analysis service
        print("\n🧪 Testing Skin Analysis Service...")
        
        # Create a mock image (PIL Image)
        from PIL import Image
        import numpy as np
        
        # Create a simple test image
        test_image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
        
        # Run skin analysis
        predictions = await skin_service.analyze_lesion(test_image)
        print(f"✅ Skin analysis completed: {predictions['top_class']} ({predictions['confidence']:.2%})")
        
        # Test API enhancements
        print("\n🚀 Testing API Enhancements...")
        
        enhancements = await api_service.enhance_analysis_results(
            prediction=predictions["top_class"],
            confidence=predictions["confidence"],
            risk_level="MEDIUM",
            recommendations=[
                "Schedule dermatologist appointment",
                "Monitor lesion for changes",
                "Consider dermoscopy examination"
            ],
            analysis_type="skin"
        )
        
        print("✅ API enhancements completed")
        
        # Check enhancement results
        print("\n📊 Enhancement Results:")
        
        ai_summary = enhancements.get("ai_summary", {})
        medical_resources = enhancements.get("medical_resources", {})
        keywords = enhancements.get("keywords", {})
        
        # AI Summary
        if ai_summary.get("summary"):
            print(f"  ✅ AI Summary: Available ({len(ai_summary['summary'])} chars)")
            print(f"     Preview: {ai_summary['summary'][:100]}...")
        else:
            print(f"  ❌ AI Summary: Not available")
        
        if ai_summary.get("explanation"):
            print(f"  ✅ AI Explanation: Available ({len(ai_summary['explanation'])} chars)")
        else:
            print(f"  ❌ AI Explanation: Not available")
        
        # Medical Resources
        articles = medical_resources.get("medical_articles", [])
        images = medical_resources.get("reference_images", [])
        
        print(f"  📚 Medical Articles: {len(articles)} found")
        print(f"  🖼️ Reference Images: {len(images)} found")
        
        if articles:
            print(f"     Sample Article: {articles[0].get('title', 'No title')}")
        
        # Keywords
        total_keywords = 0
        for category in ["conditions", "symptoms", "treatments", "procedures", "general"]:
            count = len(keywords.get(category, []))
            total_keywords += count
            if count > 0:
                print(f"  🏷️ {category.title()}: {count} keywords")
        
        print(f"  📝 Total Keywords: {total_keywords}")
        
        # Test complete enhanced response structure
        print("\n🔍 Testing Complete Response Structure...")
        
        # Simulate the complete skin analysis response
        from app.models.schemas import SkinAnalysisResult, SkinLesionCharacteristics, VisualOverlay, SeverityLevel
        from datetime import datetime
        
        # Create mock characteristics
        characteristics = SkinLesionCharacteristics(
            asymmetry_score=0.6,
            border_irregularity=0.7,
            color_variation=0.5,
            diameter_mm=None,
            evolution_risk=0.4
        )
        
        # Create mock visual overlay
        visual_overlay = VisualOverlay(
            bounding_boxes=[],
            heatmap=[],
            overlay_image_url=None
        )
        
        # Create complete result
        complete_result = SkinAnalysisResult(
            analysis_id="test-123",
            predictions=predictions["probabilities"],
            top_prediction=predictions["top_class"],
            confidence=predictions["confidence"],
            risk_level=SeverityLevel.MEDIUM,
            characteristics=characteristics,
            visual_overlay=visual_overlay,
            recommendations=[
                "Schedule dermatologist appointment",
                "Monitor lesion for changes"
            ],
            next_steps=[
                "Call dermatologist within 2 weeks",
                "Take photos to track changes"
            ],
            ai_summary=ai_summary,
            medical_resources=medical_resources,
            keywords=keywords,
            enhancement_timestamp=datetime.utcnow().isoformat()
        )
        
        print("✅ Complete response structure created successfully")
        
        # Convert to dict to simulate JSON response
        result_dict = complete_result.dict()
        
        # Check that all enhanced fields are present
        required_fields = ["ai_summary", "medical_resources", "keywords", "enhancement_timestamp"]
        missing_fields = []
        
        for field in required_fields:
            if field not in result_dict or not result_dict[field]:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing enhanced fields: {', '.join(missing_fields)}")
        else:
            print("✅ All enhanced fields present in response")
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 Test Summary:")
        print(f"  Skin Analysis: ✅ Working")
        print(f"  API Enhancements: ✅ Working")
        print(f"  AI Summary: {'✅' if ai_summary.get('summary') else '❌'}")
        print(f"  Medical Resources: {'✅' if articles or images else '❌'}")
        print(f"  Keywords: {'✅' if total_keywords > 0 else '❌'}")
        print(f"  Complete Structure: {'✅' if not missing_fields else '❌'}")
        
        return len(missing_fields) == 0
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_skin_analysis())
    
    if success:
        print("\n🎉 Enhanced skin analysis is working correctly!")
        print("The backend should now return enhanced data to the frontend.")
    else:
        print("\n⚠️ Issues found with enhanced skin analysis.")
        print("Check the error messages above for details.")
    
    sys.exit(0 if success else 1)
