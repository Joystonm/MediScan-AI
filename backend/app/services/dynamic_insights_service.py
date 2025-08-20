"""
Dynamic Insights Service
Generates prediction-based insights using GROQ, Tavily, and Keyword AI
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime

from .api_integrations import APIIntegrationService

logger = logging.getLogger(__name__)

class DynamicInsightsService:
    """Service for generating dynamic insights based on AI predictions"""
    
    def __init__(self):
        self.api_service = APIIntegrationService()
        
    async def generate_prediction_insights(
        self,
        top_prediction: str,
        confidence: float,
        risk_level: str,
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights based on the top prediction
        Always returns immediate results, with API enhancements if available
        """
        
        logger.info(f"Generating dynamic insights for: {top_prediction} ({confidence:.1%})")
        
        try:
            # Generate immediate summary based on prediction (always available)
            immediate_summary = self._generate_immediate_summary(top_prediction, confidence, risk_level)
            immediate_resources = self._get_fallback_resources(top_prediction)
            immediate_keywords = self._get_fallback_keywords(top_prediction, recommendations)
            
            # Try to enhance with API calls, but don't wait long
            try:
                # Start parallel API calls with very short timeout
                tasks = [
                    asyncio.create_task(
                        self._generate_ai_insights(top_prediction, confidence, risk_level),
                        name="ai_insights"
                    ),
                    asyncio.create_task(
                        self._fetch_medical_resources(top_prediction),
                        name="medical_resources"
                    ),
                    asyncio.create_task(
                        self._extract_keywords(top_prediction, recommendations),
                        name="keywords"
                    )
                ]
                
                # Wait for API results with very short timeout for immediate response
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=3.0  # Very short timeout for immediate response
                )
                
                ai_insights, medical_resources, keywords = results
                
                # Use API results if successful, otherwise use immediate fallbacks
                final_ai_summary = ai_insights if not isinstance(ai_insights, Exception) else immediate_summary
                final_resources = medical_resources if not isinstance(medical_resources, Exception) else immediate_resources
                final_keywords = keywords if not isinstance(keywords, Exception) else immediate_keywords
                
                logger.info("API enhancements completed successfully")
                
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"API calls failed or timed out: {e}, using immediate fallbacks")
                # Use immediate fallbacks
                final_ai_summary = immediate_summary
                final_resources = immediate_resources
                final_keywords = immediate_keywords
            
            return {
                "ai_summary": final_ai_summary,
                "medical_resources": final_resources,
                "keywords": final_keywords,
                "generated_at": datetime.utcnow().isoformat(),
                "prediction_based": True
            }
            
        except Exception as e:
            logger.error(f"Error generating prediction insights: {str(e)}")
            # Always return something useful
            return {
                "ai_summary": self._generate_immediate_summary(top_prediction, confidence, risk_level),
                "medical_resources": self._get_fallback_resources(top_prediction),
                "keywords": self._get_fallback_keywords(top_prediction, recommendations),
                "generated_at": datetime.utcnow().isoformat(),
                "prediction_based": True,
                "error": str(e)
            }
    
    def _generate_immediate_summary(self, prediction: str, confidence: float, risk_level: str) -> Dict[str, Any]:
        """Generate immediate summary based on prediction - no API calls"""
        
        # Condition-specific summaries
        summaries = {
            "basal cell carcinoma": {
                "summary": f"Basal Cell Carcinoma detected with {confidence:.1%} confidence. This is the most common form of skin cancer that grows slowly and rarely spreads to other parts of the body. While it's considered {risk_level.lower()} risk, early treatment prevents complications and ensures the best cosmetic outcome.",
                "explanation": "Basal Cell Carcinoma (BCC) develops in the basal cells of the skin's outer layer. It typically appears as a pearly or waxy bump, a flat, flesh-colored or brown scar-like lesion, or a bleeding or scabbing sore that heals and returns. BCC is highly treatable when caught early, with cure rates exceeding 95% with appropriate treatment."
            },
            "squamous cell carcinoma": {
                "summary": f"Squamous Cell Carcinoma identified with {confidence:.1%} confidence. This is the second most common type of skin cancer that can be more aggressive than basal cell carcinoma. The {risk_level.lower()} risk assessment indicates the need for prompt medical evaluation and treatment.",
                "explanation": "Squamous Cell Carcinoma (SCC) arises from squamous cells in the skin's upper layers. It often appears as a firm, red nodule or a flat lesion with a scaly, crusted surface. While SCC can spread to other parts of the body if left untreated, early detection and treatment result in excellent outcomes."
            },
            "melanoma": {
                "summary": f"Melanoma detected with {confidence:.1%} confidence. This is the most serious type of skin cancer that can spread rapidly if not treated early. The {risk_level.lower()} risk classification emphasizes the critical importance of immediate professional medical evaluation.",
                "explanation": "Melanoma develops in melanocytes, the cells that produce melanin. It can appear anywhere on the body and may develop from an existing mole or appear as a new, unusual growth. Early detection is crucial as melanoma can spread to lymph nodes and other organs. When caught early, melanoma is highly treatable."
            },
            "actinic keratosis": {
                "summary": f"Actinic Keratosis identified with {confidence:.1%} confidence. This is a precancerous condition caused by sun damage that has the potential to develop into squamous cell carcinoma. The {risk_level.lower()} risk indicates the importance of monitoring and potential treatment.",
                "explanation": "Actinic Keratosis (AK) appears as rough, scaly patches on sun-exposed areas of the skin. While AK itself is not cancer, it's considered precancerous because it can progress to squamous cell carcinoma in some cases. Treatment can prevent this progression and is typically straightforward."
            },
            "seborrheic keratosis": {
                "summary": f"Seborrheic Keratosis detected with {confidence:.1%} confidence. This is a common, benign (non-cancerous) skin growth that typically appears as people age. The {risk_level.lower()} risk assessment reflects its generally harmless nature, though professional evaluation confirms the diagnosis.",
                "explanation": "Seborrheic Keratosis appears as waxy, scaly, or slightly raised growths that can range in color from light tan to black. These growths are very common and typically harmless, though they can sometimes be confused with other skin conditions, making professional evaluation important for accurate diagnosis."
            },
            "nevus": {
                "summary": f"Nevus (mole) identified with {confidence:.1%} confidence. This appears to be a common skin growth that is typically benign. The {risk_level.lower()} risk assessment suggests routine monitoring, as most moles remain harmless throughout life.",
                "explanation": "A nevus is a common type of skin growth, often called a mole. Most nevi are benign and pose no health risk. However, changes in size, shape, color, or texture should be evaluated by a healthcare professional, as these could indicate the need for closer monitoring or treatment."
            }
        }
        
        # Find matching summary
        prediction_lower = prediction.lower()
        for condition, content in summaries.items():
            if condition in prediction_lower:
                return {
                    **content,
                    "confidence_interpretation": self._interpret_confidence(confidence),
                    "risk_interpretation": self._interpret_risk(risk_level),
                    "generated_at": datetime.utcnow().isoformat()
                }
        
        # Default summary for unknown conditions
        return {
            "summary": f"{prediction} detected with {confidence:.1%} confidence. This skin condition requires professional medical evaluation for accurate diagnosis and appropriate treatment planning. The {risk_level.lower()} risk assessment guides the urgency of follow-up care.",
            "explanation": f"Professional dermatological evaluation is recommended for {prediction}. A qualified healthcare provider can perform a thorough examination, potentially including dermoscopy or biopsy if needed, to confirm the diagnosis and recommend the most appropriate treatment approach.",
            "confidence_interpretation": self._interpret_confidence(confidence),
            "risk_interpretation": self._interpret_risk(risk_level),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_ai_insights(self, prediction: str, confidence: float, risk_level: str) -> Dict[str, Any]:
        """Generate enhanced AI insights using GROQ API"""
        
        try:
            return await self.api_service.groq.generate_medical_summary(
                prediction=prediction,
                confidence=confidence,
                risk_level=risk_level,
                analysis_type="skin"
            )
        except Exception as e:
            logger.error(f"GROQ API failed: {e}")
            return self._generate_immediate_summary(prediction, confidence, risk_level)
    
    async def _fetch_medical_resources(self, prediction: str) -> Dict[str, Any]:
        """Fetch medical resources using Tavily API"""
        
        try:
            return await self.api_service.tavily.fetch_medical_resources(
                condition=prediction,
                analysis_type="skin"
            )
        except Exception as e:
            logger.error(f"Tavily API failed: {e}")
            return self._get_fallback_resources(prediction)
    
    async def _extract_keywords(self, prediction: str, recommendations: List[str]) -> Dict[str, Any]:
        """Extract keywords using Keyword AI"""
        
        try:
            text_content = [prediction] + recommendations
            return await self.api_service.keyword_ai.extract_medical_keywords(
                text_content=text_content,
                analysis_type="skin"
            )
        except Exception as e:
            logger.error(f"Keyword AI failed: {e}")
            return self._get_fallback_keywords(prediction, recommendations)
    
    def _interpret_confidence(self, confidence: float) -> str:
        """Interpret confidence level"""
        if confidence >= 0.8:
            return f"High confidence ({confidence:.1%}) indicates strong certainty in the AI assessment based on clear diagnostic features."
        elif confidence >= 0.6:
            return f"Good confidence ({confidence:.1%}) shows reasonable certainty, with professional confirmation recommended."
        elif confidence >= 0.4:
            return f"Moderate confidence ({confidence:.1%}) suggests some uncertainty, making professional evaluation important."
        else:
            return f"Low confidence ({confidence:.1%}) indicates significant uncertainty, requiring professional medical assessment."
    
    def _interpret_risk(self, risk_level: str) -> str:
        """Interpret risk level"""
        interpretations = {
            "HIGH": "High risk indicates features that may suggest a serious condition requiring immediate medical attention.",
            "MEDIUM": "Medium risk indicates features that warrant professional evaluation within a reasonable timeframe.",
            "LOW": "Low risk indicates features that appear benign but should still be monitored regularly.",
            "CRITICAL": "Critical risk indicates features requiring emergency medical evaluation."
        }
        return interpretations.get(risk_level.upper(), "Professional medical evaluation is recommended.")
    
    def _get_fallback_resources(self, prediction: str) -> Dict[str, Any]:
        """Get fallback medical resources"""
        
        return {
            "reference_images": [],
            "medical_articles": [
                {
                    "title": f"Understanding {prediction}: Medical Overview",
                    "url": "https://www.mayoclinic.org/diseases-conditions/skin-cancer",
                    "source": "Mayo Clinic",
                    "snippet": f"Comprehensive medical information about {prediction} including symptoms, diagnosis, and treatment options.",
                    "relevance_score": 0.9
                },
                {
                    "title": "Dermatology Guidelines and Best Practices",
                    "url": "https://www.aad.org/public/diseases/skin-cancer",
                    "source": "American Academy of Dermatology",
                    "snippet": f"Professional guidelines for {prediction} diagnosis, treatment, and patient care from leading dermatology experts.",
                    "relevance_score": 0.85
                },
                {
                    "title": "When to See a Dermatologist",
                    "url": "https://www.aad.org/public/everyday-care/when-to-see-dermatologist",
                    "source": "American Academy of Dermatology",
                    "snippet": "Guidelines for when to seek professional dermatological care and evaluation.",
                    "relevance_score": 0.8
                }
            ],
            "fetched_at": datetime.utcnow().isoformat()
        }
    
    def _get_fallback_keywords(self, prediction: str, recommendations: List[str]) -> Dict[str, Any]:
        """Get fallback keywords"""
        
        # Extract basic keywords from prediction and recommendations
        condition_keywords = [prediction.lower()]
        treatment_keywords = []
        procedure_keywords = []
        
        # Extract keywords from recommendations
        for rec in recommendations:
            rec_lower = rec.lower()
            if "dermatologist" in rec_lower:
                procedure_keywords.append("dermatological consultation")
            if "biopsy" in rec_lower:
                procedure_keywords.append("biopsy")
            if "monitor" in rec_lower:
                treatment_keywords.append("monitoring")
            if "treatment" in rec_lower:
                treatment_keywords.append("medical treatment")
        
        return {
            "conditions": condition_keywords,
            "symptoms": ["skin lesion", "skin growth"],
            "treatments": treatment_keywords or ["medical evaluation"],
            "procedures": procedure_keywords or ["clinical examination"],
            "general": ["dermatology", "skin health", "medical diagnosis"],
            "extracted_at": datetime.utcnow().isoformat()
        }
