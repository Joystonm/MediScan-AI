"""
Test API endpoint for verifying API integrations
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from app.services.api_integrations import APIIntegrationService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize API integration service
api_service = APIIntegrationService()

@router.get("/test-api-integrations")
async def test_api_integrations() -> Dict[str, Any]:
    """Test endpoint to verify API integrations are working"""
    
    try:
        logger.info("Testing API integrations via endpoint")
        
        # Test with sample data
        result = await api_service.enhance_analysis_results(
            prediction="Basal cell carcinoma",
            confidence=0.73,
            risk_level="MEDIUM",
            recommendations=[
                "Schedule dermatologist appointment within 2-4 weeks",
                "Monitor lesion for ABCDE changes",
                "Consider dermoscopy for detailed examination"
            ],
            analysis_type="skin"
        )
        
        # Check if we got real data or fallbacks
        ai_summary = result.get("ai_summary", {})
        medical_resources = result.get("medical_resources", {})
        keywords = result.get("keywords", {})
        
        status = {
            "groq_working": bool(ai_summary.get("summary") and ai_summary["summary"] != "Enhancement unavailable"),
            "tavily_working": bool(medical_resources.get("medical_articles") or medical_resources.get("reference_images")),
            "keyword_ai_working": bool(any(keywords.get(k, []) for k in ["conditions", "symptoms", "treatments", "procedures", "general"]))
        }
        
        return {
            "status": "success",
            "api_status": status,
            "sample_results": {
                "ai_summary_preview": ai_summary.get("summary", "")[:100] + "..." if ai_summary.get("summary") else "Not available",
                "articles_count": len(medical_resources.get("medical_articles", [])),
                "images_count": len(medical_resources.get("reference_images", [])),
                "keywords_count": sum(len(keywords.get(k, [])) for k in ["conditions", "symptoms", "treatments", "procedures", "general"])
            },
            "full_results": result
        }
        
    except Exception as e:
        logger.error(f"Error testing API integrations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API integration test failed: {str(e)}")

@router.get("/test-groq")
async def test_groq_only() -> Dict[str, Any]:
    """Test only GROQ API"""
    
    try:
        result = await api_service.groq.generate_medical_summary(
            prediction="Melanoma",
            confidence=0.85,
            risk_level="HIGH",
            analysis_type="skin"
        )
        
        return {
            "status": "success",
            "groq_result": result
        }
        
    except Exception as e:
        logger.error(f"Error testing GROQ: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GROQ test failed: {str(e)}")

@router.get("/test-tavily")
async def test_tavily_only() -> Dict[str, Any]:
    """Test only Tavily API"""
    
    try:
        result = await api_service.tavily.fetch_medical_resources(
            condition="Basal cell carcinoma",
            analysis_type="skin"
        )
        
        return {
            "status": "success",
            "tavily_result": result
        }
        
    except Exception as e:
        logger.error(f"Error testing Tavily: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tavily test failed: {str(e)}")

@router.get("/test-keyword-ai")
async def test_keyword_ai_only() -> Dict[str, Any]:
    """Test only Keyword AI"""
    
    try:
        result = await api_service.keyword_ai.extract_medical_keywords(
            text_content=["Basal cell carcinoma", "dermatologist consultation", "biopsy recommended"],
            analysis_type="skin"
        )
        
        return {
            "status": "success",
            "keyword_ai_result": result
        }
        
    except Exception as e:
        logger.error(f"Error testing Keyword AI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Keyword AI test failed: {str(e)}")
