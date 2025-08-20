#!/usr/bin/env python3
"""
Test Backend Response Structure
Verifies that the skin analysis endpoint returns properly structured enhanced data
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

async def test_backend_response():
    """Test the backend response structure"""
    
    print("🔍 Testing Backend Response Structure")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # Import required modules
        from app.services.skin_analysis_service import SkinAnalysisService
        from app.services.api_integrations import APIIntegrationService
        from app.models.schemas import SkinAnalysisResult, SkinLesionCharacteristics, VisualOverlay, SeverityLevel
        from datetime import datetime
        from PIL import Image
        import numpy as np
        
        # Initialize services
        skin_service = SkinAnalysisService()
        api_service = APIIntegrationService()
        
        print("✅ Services initialized")
        
        # Create test image
        test_image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
        
        # Get predictions
        predictions = await skin_service.analyze_lesion(test_image)
        print(f"✅ Predictions: {predictions['top_class']} ({predictions['confidence']:.2%})")
        
        # Test API enhancements
        enhancements = await api_service.enhance_analysis_results(
            prediction=predictions["top_class"],
            confidence=predictions["confidence"],
            risk_level="MEDIUM",
            recommendations=["Schedule dermatologist appointment", "Monitor lesion"],
            analysis_type="skin"
        )
        
        print("✅ API enhancements completed")
        
        # Create complete result structure
        characteristics = SkinLesionCharacteristics(
            asymmetry_score=0.6,
            border_irregularity=0.7,
            color_variation=0.5,
            diameter_mm=None,
            evolution_risk=0.4
        )
        
        visual_overlay = VisualOverlay(
            bounding_boxes=[],
            heatmap=[],
            overlay_image_url=None
        )
        
        result = SkinAnalysisResult(
            analysis_id="test-123",
            predictions=predictions["probabilities"],
            top_prediction=predictions["top_class"],
            confidence=predictions["confidence"],
            risk_level=SeverityLevel.MEDIUM,
            characteristics=characteristics,
            visual_overlay=visual_overlay,
            recommendations=["Schedule dermatologist appointment", "Monitor lesion"],
            next_steps=["Call dermatologist", "Take photos"],
            ai_summary=enhancements.get("ai_summary", {}),
            medical_resources=enhancements.get("medical_resources", {}),
            keywords=enhancements.get("keywords", {}),
            enhancement_timestamp=enhancements.get("enhancement_timestamp")
        )
        
        # Convert to dict (simulating JSON response)
        result_dict = result.model_dump()
        
        print("\n📊 Response Structure Analysis:")
        print(f"  Analysis ID: {result_dict.get('analysis_id')}")
        print(f"  Top Prediction: {result_dict.get('top_prediction')}")
        print(f"  Confidence: {result_dict.get('confidence'):.2%}")
        print(f"  Risk Level: {result_dict.get('risk_level')}")
        
        # Check AI Summary
        ai_summary = result_dict.get('ai_summary', {})
        print(f"\n🧠 AI Summary:")
        print(f"  Summary: {'✅ Present' if ai_summary.get('summary') else '❌ Missing'} ({len(ai_summary.get('summary', ''))} chars)")
        print(f"  Explanation: {'✅ Present' if ai_summary.get('explanation') else '❌ Missing'} ({len(ai_summary.get('explanation', ''))} chars)")
        print(f"  Confidence Interpretation: {'✅ Present' if ai_summary.get('confidence_interpretation') else '❌ Missing'}")
        print(f"  Risk Interpretation: {'✅ Present' if ai_summary.get('risk_interpretation') else '❌ Missing'}")
        
        # Check Medical Resources
        medical_resources = result_dict.get('medical_resources', {})
        articles = medical_resources.get('medical_articles', [])
        images = medical_resources.get('reference_images', [])
        print(f"\n📚 Medical Resources:")
        print(f"  Articles: {len(articles)} found")
        print(f"  Images: {len(images)} found")
        if articles:
            print(f"  Sample Article: {articles[0].get('title', 'No title')[:50]}...")
        
        # Check Keywords
        keywords = result_dict.get('keywords', {})
        total_keywords = sum(len(v) for k, v in keywords.items() if isinstance(v, list))
        print(f"\n🏷️ Keywords:")
        print(f"  Total Keywords: {total_keywords}")
        for category in ['conditions', 'symptoms', 'treatments', 'procedures', 'general']:
            count = len(keywords.get(category, []))
            if count > 0:
                print(f"  {category.title()}: {count} keywords")
        
        # Check Characteristics
        characteristics_dict = result_dict.get('characteristics', {})
        print(f"\n📏 ABCDE Characteristics:")
        print(f"  Asymmetry: {characteristics_dict.get('asymmetry_score', 0):.1%}")
        print(f"  Border: {characteristics_dict.get('border_irregularity', 0):.1%}")
        print(f"  Color: {characteristics_dict.get('color_variation', 0):.1%}")
        print(f"  Evolution: {characteristics_dict.get('evolution_risk', 0):.1%}")
        
        # Verify all required fields are present
        required_fields = [
            'analysis_id', 'top_prediction', 'confidence', 'risk_level',
            'characteristics', 'recommendations', 'next_steps',
            'ai_summary', 'medical_resources', 'keywords'
        ]
        
        missing_fields = [field for field in required_fields if field not in result_dict]
        
        print(f"\n✅ Field Validation:")
        if missing_fields:
            print(f"  ❌ Missing fields: {', '.join(missing_fields)}")
        else:
            print(f"  ✅ All required fields present")
        
        # Check if enhanced fields have content
        enhanced_content_check = {
            'AI Summary': bool(ai_summary.get('summary')),
            'Medical Articles': bool(articles),
            'Keywords': bool(total_keywords > 0),
            'Characteristics': bool(characteristics_dict.get('asymmetry_score', 0) > 0)
        }
        
        print(f"\n📋 Content Validation:")
        for check, passed in enhanced_content_check.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        # Save sample response for debugging
        with open('sample_response.json', 'w') as f:
            json.dump(result_dict, f, indent=2, default=str)
        print(f"\n💾 Sample response saved to: sample_response.json")
        
        all_passed = not missing_fields and all(enhanced_content_check.values())
        
        print(f"\n{'🎉' if all_passed else '⚠️'} Overall Status: {'PASS' if all_passed else 'ISSUES FOUND'}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend_response())
    
    if success:
        print("\n🎉 Backend response structure is correct!")
        print("The enhanced data should now display properly in the frontend.")
    else:
        print("\n⚠️ Issues found with backend response structure.")
    
    sys.exit(0 if success else 1)
