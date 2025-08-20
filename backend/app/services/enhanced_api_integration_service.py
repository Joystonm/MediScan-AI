"""
Main Enhanced API Integration Service
Coordinates GROQ, Tavily, and Keyword AI services with comprehensive fallbacks
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .enhanced_api_integrations import EnhancedGroqService
from .enhanced_tavily_service import EnhancedTavilyService
from .enhanced_keyword_service import EnhancedKeywordAIService

logger = logging.getLogger(__name__)

class EnhancedAPIIntegrationService:
    """Main service that coordinates all enhanced API integrations with comprehensive fallbacks"""
    
    def __init__(self):
        self.groq = EnhancedGroqService()
        self.tavily = EnhancedTavilyService()
        self.keyword_ai = EnhancedKeywordAIService()
    
    async def enhance_analysis_results(
        self,
        prediction: str,
        confidence: float,
        risk_level: str,
        recommendations: List[str],
        analysis_type: str = "skin"
    ) -> Dict[str, Any]:
        """Enhance analysis results with comprehensive AI-generated content and fallbacks"""
        
        try:
            logger.info(f"Starting enhanced analysis for {prediction} with {confidence:.2%} confidence")
            
            # Run all API calls concurrently for better performance
            summary_task = self.groq.generate_medical_summary(
                prediction, confidence, risk_level, analysis_type
            )
            
            resources_task = self.tavily.fetch_medical_resources(
                prediction, analysis_type
            )
            
            # Prepare text content for keyword extraction
            text_content = [prediction] + recommendations
            keywords_task = self.keyword_ai.extract_medical_keywords(
                text_content, analysis_type
            )
            
            # Wait for all tasks to complete with timeout
            try:
                summary_data, resources_data, keywords_data = await asyncio.wait_for(
                    asyncio.gather(summary_task, resources_task, keywords_task),
                    timeout=45.0  # 45 second timeout
                )
            except asyncio.TimeoutError:
                logger.warning("API calls timed out, using fallback data")
                # Generate fallback data if APIs timeout
                summary_data = await self._generate_fallback_summary(prediction, confidence, risk_level, analysis_type)
                resources_data = await self._generate_fallback_resources(prediction, analysis_type)
                keywords_data = await self._generate_fallback_keywords(text_content, analysis_type)
            
            # Validate and enhance the results
            enhanced_result = {
                "ai_summary": self._validate_summary_data(summary_data),
                "medical_resources": self._validate_resources_data(resources_data),
                "keywords": self._validate_keywords_data(keywords_data),
                "enhancement_timestamp": datetime.utcnow().isoformat(),
                "enhancement_status": "success"
            }
            
            # Add metadata about data sources
            enhanced_result["data_sources"] = {
                "summary_source": summary_data.get("source", "fallback"),
                "resources_source": resources_data.get("source", "fallback"),
                "keywords_source": keywords_data.get("source", "fallback")
            }
            
            logger.info(f"Enhancement completed successfully for {prediction}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error enhancing analysis results: {str(e)}")
            
            # Return comprehensive fallback data
            return await self._generate_comprehensive_fallback(
                prediction, confidence, risk_level, recommendations, analysis_type
            )
    
    def _validate_summary_data(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure summary data has required fields"""
        
        validated = {
            "summary": summary_data.get("summary", "Analysis summary unavailable"),
            "explanation": summary_data.get("explanation", "Detailed explanation unavailable"),
            "confidence_interpretation": summary_data.get("confidence_interpretation", "Confidence interpretation unavailable"),
            "risk_interpretation": summary_data.get("risk_interpretation", "Risk interpretation unavailable"),
            "generated_at": summary_data.get("generated_at", datetime.utcnow().isoformat()),
            "source": summary_data.get("source", "fallback")
        }
        
        return validated
    
    def _validate_resources_data(self, resources_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure resources data has required fields"""
        
        validated = {
            "reference_images": resources_data.get("reference_images", []),
            "medical_articles": resources_data.get("medical_articles", []),
            "fetched_at": resources_data.get("fetched_at", datetime.utcnow().isoformat()),
            "source": resources_data.get("source", "fallback")
        }
        
        # Ensure we have at least some resources
        if not validated["reference_images"] and not validated["medical_articles"]:
            validated["medical_articles"] = [
                {
                    "title": "General Medical Information",
                    "url": "https://www.mayoclinic.org/diseases-conditions",
                    "source": "Mayo Clinic",
                    "snippet": "Comprehensive medical information and resources for patients and healthcare providers.",
                    "relevance_score": 0.7,
                    "content_type": "general_resource"
                }
            ]
        
        return validated
    
    def _validate_keywords_data(self, keywords_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure keywords data has required fields"""
        
        validated = {
            "conditions": keywords_data.get("conditions", []),
            "symptoms": keywords_data.get("symptoms", []),
            "treatments": keywords_data.get("treatments", []),
            "procedures": keywords_data.get("procedures", []),
            "anatomy": keywords_data.get("anatomy", []),
            "general": keywords_data.get("general", []),
            "extracted_at": keywords_data.get("extracted_at", datetime.utcnow().isoformat()),
            "source": keywords_data.get("source", "fallback")
        }
        
        # Ensure we have at least some keywords
        total_keywords = sum(len(v) for v in validated.values() if isinstance(v, list))
        if total_keywords == 0:
            validated["general"] = ["medical analysis", "healthcare", "diagnosis"]
        
        return validated
    
    async def _generate_fallback_summary(self, prediction: str, confidence: float, risk_level: str, analysis_type: str) -> Dict[str, Any]:
        """Generate fallback summary data"""
        
        return await self.groq.generate_medical_summary(prediction, confidence, risk_level, analysis_type)
    
    async def _generate_fallback_resources(self, prediction: str, analysis_type: str) -> Dict[str, Any]:
        """Generate fallback resources data"""
        
        return await self.tavily.fetch_medical_resources(prediction, analysis_type)
    
    async def _generate_fallback_keywords(self, text_content: List[str], analysis_type: str) -> Dict[str, Any]:
        """Generate fallback keywords data"""
        
        return await self.keyword_ai.extract_medical_keywords(text_content, analysis_type)
    
    async def _generate_comprehensive_fallback(
        self,
        prediction: str,
        confidence: float,
        risk_level: str,
        recommendations: List[str],
        analysis_type: str
    ) -> Dict[str, Any]:
        """Generate comprehensive fallback data when all services fail"""
        
        logger.warning("Generating comprehensive fallback data")
        
        # Generate basic summary
        risk_descriptions = {
            "HIGH": "requires immediate medical attention",
            "MEDIUM": "warrants professional evaluation",
            "LOW": "appears to be low risk but should be monitored"
        }
        
        summary = f"""
        The AI analysis has identified {prediction.lower()} with {confidence:.1%} confidence. 
        This {risk_level.lower()} risk finding {risk_descriptions.get(risk_level.upper(), 'requires evaluation')}.
        
        Please consult with a qualified healthcare provider for proper evaluation and treatment recommendations.
        This AI analysis is for informational purposes only and should not replace professional medical advice.
        """
        
        # Generate basic resources
        basic_articles = [
            {
                "title": f"Understanding {prediction}",
                "url": "https://www.mayoclinic.org/diseases-conditions",
                "source": "Mayo Clinic",
                "snippet": f"Medical information about {prediction} and related conditions.",
                "relevance_score": 0.8,
                "content_type": "medical_reference"
            },
            {
                "title": "When to See a Dermatologist",
                "url": "https://www.aad.org/public/everyday-care/when-to-see-dermatologist",
                "source": "American Academy of Dermatology",
                "snippet": "Guidelines for when to seek professional dermatological care and evaluation.",
                "relevance_score": 0.75,
                "content_type": "healthcare_guidance"
            }
        ]
        
        # Generate basic keywords
        text_content = [prediction] + recommendations
        combined_text = " ".join(text_content).lower()
        
        basic_keywords = {
            "conditions": [prediction] if prediction else [],
            "symptoms": [],
            "treatments": [],
            "procedures": ["medical evaluation", "dermatological consultation"],
            "anatomy": [],
            "general": ["healthcare", "medical diagnosis", "professional consultation"]
        }
        
        # Extract some keywords from recommendations
        if "dermatologist" in combined_text:
            basic_keywords["procedures"].append("dermatologist consultation")
        if "biopsy" in combined_text:
            basic_keywords["procedures"].append("biopsy")
        if "monitor" in combined_text:
            basic_keywords["general"].append("monitoring")
        
        return {
            "ai_summary": {
                "summary": summary.strip(),
                "explanation": f"Professional medical evaluation is recommended for {prediction}.",
                "confidence_interpretation": f"The AI shows {confidence:.1%} confidence in this assessment.",
                "risk_interpretation": f"This {risk_level.lower()} risk level indicates the need for appropriate medical follow-up.",
                "generated_at": datetime.utcnow().isoformat(),
                "source": "comprehensive_fallback"
            },
            "medical_resources": {
                "reference_images": [],
                "medical_articles": basic_articles,
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "comprehensive_fallback"
            },
            "keywords": {
                **basic_keywords,
                "extracted_at": datetime.utcnow().isoformat(),
                "source": "comprehensive_fallback"
            },
            "enhancement_timestamp": datetime.utcnow().isoformat(),
            "enhancement_status": "fallback",
            "data_sources": {
                "summary_source": "comprehensive_fallback",
                "resources_source": "comprehensive_fallback", 
                "keywords_source": "comprehensive_fallback"
            }
        }
