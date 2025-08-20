#!/usr/bin/env python3
"""
Test script to verify the radiology insights service fix
"""

import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_radiology_insights():
    """Test the radiology insights service directly"""
    
    print("🔧 Testing Radiology Dynamic Insights Service")
    print("=" * 50)
    
    try:
        from app.services.radiology_dynamic_insights import RadiologyDynamicInsightsService
        
        # Create service instance
        service = RadiologyDynamicInsightsService()
        print("✅ Service created successfully")
        
        # Test data
        test_findings = [
            {
                "condition": "Pleural effusion",
                "probability": 0.76
            },
            {
                "condition": "Bilateral pleural effusions", 
                "probability": 0.68
            }
        ]
        
        test_scan_type = "chest_xray"
        test_urgency = "urgent"
        test_summary = "Chest X-ray demonstrates bilateral pleural effusions with blunting of costophrenic angles."
        test_recommendations = [
            "Thoracentesis may be indicated",
            "Evaluate underlying cause of effusions",
            "Consider diuretic therapy if cardiac origin",
            "Monitor respiratory function"
        ]
        
        print("🧪 Running insights generation test...")
        
        # Test the insights generation
        result = await service.generate_radiology_insights(
            findings=test_findings,
            scan_type=test_scan_type,
            urgency_level=test_urgency,
            clinical_summary=test_summary,
            recommendations=test_recommendations
        )
        
        print("✅ Insights generated successfully!")
        print(f"📊 Result keys: {list(result.keys())}")
        
        # Check if all expected keys are present
        expected_keys = ["ai_summary", "medical_resources", "keywords", "generated_at", "radiology_enhanced"]
        missing_keys = [key for key in expected_keys if key not in result]
        
        if missing_keys:
            print(f"⚠️  Missing keys: {missing_keys}")
        else:
            print("✅ All expected keys present")
        
        # Check AI summary
        if "ai_summary" in result and result["ai_summary"]:
            ai_summary = result["ai_summary"]
            print(f"🤖 AI Summary available: {bool(ai_summary.get('summary'))}")
            if ai_summary.get('summary'):
                summary_preview = ai_summary['summary'][:100] + "..." if len(ai_summary['summary']) > 100 else ai_summary['summary']
                print(f"   Preview: {summary_preview}")
        
        # Check keywords
        if "keywords" in result and result["keywords"]:
            keywords = result["keywords"]
            conditions = keywords.get("conditions", [])
            treatments = keywords.get("treatments", [])
            print(f"🏷️  Keywords extracted:")
            print(f"   Conditions: {conditions[:3]}")
            print(f"   Treatments: {treatments[:3]}")
        
        # Check medical resources
        if "medical_resources" in result and result["medical_resources"]:
            resources = result["medical_resources"]
            articles = resources.get("medical_articles", [])
            print(f"📚 Medical resources: {len(articles)} articles found")
        
        print(f"✨ Enhanced: {result.get('radiology_enhanced', False)}")
        print(f"🕐 Generated at: {result.get('generated_at', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    
    print("🚀 Testing Radiology Insights Service Fix")
    print("=" * 50)
    
    success = await test_radiology_insights()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ RADIOLOGY INSIGHTS SERVICE TEST PASSED!")
        print("🎉 The scan_type error has been fixed!")
        print("💡 Your radiology analysis should now work properly.")
    else:
        print("❌ RADIOLOGY INSIGHTS SERVICE TEST FAILED!")
        print("🔧 There may still be issues to resolve.")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
