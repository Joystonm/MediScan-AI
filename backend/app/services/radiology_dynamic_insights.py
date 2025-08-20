"""
Radiology Dynamic Insights Service
Generates prediction-based insights for radiology analysis using GROQ, Tavily, and Keyword AI
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime

from .api_integrations import APIIntegrationService

logger = logging.getLogger(__name__)

class RadiologyDynamicInsightsService:
    """Service for generating dynamic insights based on radiology AI predictions"""
    
    def __init__(self):
        self.api_service = APIIntegrationService()
        
    async def generate_radiology_insights(
        self,
        findings: List[Dict[str, Any]],
        scan_type: str,
        urgency_level: str,
        clinical_summary: str,
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights based on radiology findings
        Always returns immediate results, with API enhancements if available
        """
        
        # Get primary finding for insights (define outside try block)
        primary_finding = findings[0]["condition"] if findings else "normal study"
        primary_confidence = findings[0]["probability"] if findings else 0.85
        
        logger.info(f"Generating radiology insights for: {primary_finding} ({primary_confidence:.1%})")
        
        try:
            # Generate immediate summary based on findings (always available)
            immediate_summary = self._generate_immediate_radiology_summary(
                primary_finding, primary_confidence, urgency_level, scan_type
            )
            immediate_resources = self._get_fallback_radiology_resources(primary_finding, scan_type)
            immediate_keywords = self._get_fallback_radiology_keywords(primary_finding, recommendations, scan_type)
            
            # Try to enhance with API calls, but don't wait long
            try:
                # Start parallel API calls with short timeout
                tasks = [
                    asyncio.create_task(
                        self._generate_radiology_ai_insights(
                            primary_finding, primary_confidence, urgency_level, scan_type, clinical_summary
                        ),
                        name="radiology_ai_insights"
                    ),
                    asyncio.create_task(
                        self._fetch_radiology_medical_resources(primary_finding, scan_type),
                        name="radiology_medical_resources"
                    ),
                    asyncio.create_task(
                        self._extract_radiology_keywords(primary_finding, recommendations, clinical_summary, scan_type),
                        name="radiology_keywords"
                    )
                ]
                
                # Wait for API results with short timeout for immediate response
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=4.0  # Short timeout for immediate response
                )
                
                ai_insights, medical_resources, keywords = results
                
                # Use API results if successful, otherwise use immediate fallbacks
                final_ai_summary = ai_insights if not isinstance(ai_insights, Exception) else immediate_summary
                final_resources = medical_resources if not isinstance(medical_resources, Exception) else immediate_resources
                final_keywords = keywords if not isinstance(keywords, Exception) else immediate_keywords
                
                logger.info("Radiology API enhancements completed successfully")
                
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"Radiology API calls failed or timed out: {e}, using immediate fallbacks")
                # Use immediate fallbacks
                final_ai_summary = immediate_summary
                final_resources = immediate_resources
                final_keywords = immediate_keywords
            
            return {
                "ai_summary": final_ai_summary,
                "medical_resources": final_resources,
                "keywords": final_keywords,
                "generated_at": datetime.utcnow().isoformat(),
                "radiology_enhanced": True,
                "scan_type": scan_type,
                "primary_finding": primary_finding
            }
            
        except Exception as e:
            logger.error(f"Error generating radiology insights: {str(e)}")
            # Always return something useful
            return {
                "ai_summary": self._generate_immediate_radiology_summary(
                    primary_finding, primary_confidence, urgency_level, scan_type
                ),
                "medical_resources": self._get_fallback_radiology_resources(primary_finding, scan_type),
                "keywords": self._get_fallback_radiology_keywords(primary_finding, recommendations, scan_type),
                "generated_at": datetime.utcnow().isoformat(),
                "radiology_enhanced": True,
                "scan_type": scan_type,
                "primary_finding": primary_finding,
                "error": str(e)
            }
    
    def _generate_immediate_radiology_summary(
        self, 
        finding: str, 
        confidence: float, 
        urgency_level: str, 
        scan_type: str
    ) -> Dict[str, Any]:
        """Generate immediate summary based on radiology findings - no API calls"""
        
        # Condition-specific summaries for radiology
        summaries = {
            "pneumonia": {
                "summary": f"Pneumonia detected with {confidence:.1%} confidence on {scan_type.replace('_', ' ')}. This is a lung infection causing inflammation in the air sacs (alveoli). The {urgency_level.lower()} classification indicates prompt antibiotic treatment and respiratory monitoring are needed.",
                "explanation": "Pneumonia appears on chest imaging as areas of increased density (consolidation) in the lung tissue, often with air bronchograms visible. It can be caused by bacteria, viruses, fungi, or other microorganisms. The infection causes the air sacs to fill with fluid or pus, making breathing difficult. Early identification and appropriate treatment typically lead to good outcomes.",
                "clinical_significance": "Requires immediate antibiotic therapy based on likely pathogen, supportive respiratory care, and monitoring for complications. Hospitalization may be needed depending on severity scores and patient risk factors."
            },
            "pneumothorax": {
                "summary": f"Pneumothorax identified with {confidence:.1%} confidence on {scan_type.replace('_', ' ')}. This is a collapsed lung caused by air accumulation in the pleural space. The {urgency_level.lower()} classification emphasizes the critical need for immediate medical intervention to prevent respiratory compromise.",
                "explanation": "Pneumothorax occurs when air leaks into the space between the lung and chest wall (pleural space), causing the lung to collapse partially or completely. It can be spontaneous (occurring without trauma) or traumatic. On imaging, it appears as a dark area without lung markings, with a visible pleural edge. Treatment urgency depends on the size and patient symptoms.",
                "clinical_significance": "May require immediate chest tube insertion (thoracostomy) depending on size and symptoms. Small pneumothoraces may be managed with observation, while larger ones or those causing respiratory distress require emergency decompression."
            },
            "pleural effusion": {
                "summary": f"Pleural effusion detected with {confidence:.1%} confidence on {scan_type.replace('_', ' ')}. This is fluid accumulation in the pleural space around the lungs, which can impair breathing. The {urgency_level.lower()} assessment indicates evaluation of the underlying cause and possible drainage are needed.",
                "explanation": "Pleural effusion appears as fluid collection in the space between the lung and chest wall. It can result from various conditions including heart failure (transudative), infection, cancer, or inflammatory diseases (exudative). The fluid causes blunting of the costophrenic angles on chest X-ray and can compress lung tissue, reducing breathing capacity.",
                "clinical_significance": "May require thoracentesis (needle drainage) for both diagnostic and therapeutic purposes. Analysis of pleural fluid helps determine the underlying cause and guides treatment. Large effusions may need chest tube drainage."
            },
            "cardiomegaly": {
                "summary": f"Cardiomegaly identified with {confidence:.1%} confidence on {scan_type.replace('_', ' ')}. This is enlargement of the heart shadow, indicating the heart is larger than normal. The {urgency_level.lower()} classification suggests comprehensive cardiac evaluation is needed to determine the underlying cause.",
                "explanation": "Cardiomegaly appears as an enlarged cardiac silhouette on chest imaging, typically with a cardiothoracic ratio greater than 50% on PA chest X-ray. It can result from various conditions including heart failure, valve disease, cardiomyopathy, hypertension, or pericardial effusion. The enlargement may involve specific chambers or the entire heart.",
                "clinical_significance": "Requires echocardiography to assess cardiac function, chamber sizes, and valve function. Cardiology consultation is recommended for further evaluation and management. Treatment depends on the underlying cause and may include medications, lifestyle changes, or interventional procedures."
            },
            "pulmonary nodule": {
                "summary": f"Pulmonary nodule detected with {confidence:.1%} confidence on {scan_type.replace('_', ' ')}. This is a small, round growth in the lung tissue that requires careful evaluation. The {urgency_level.lower()} assessment guides the appropriate follow-up strategy based on size, characteristics, and patient risk factors.",
                "explanation": "Pulmonary nodules are common findings that appear as round or oval-shaped opacities in the lung. Most are benign (non-cancerous), including granulomas from old infections, but evaluation is important to rule out malignancy. Size, growth rate, morphology, and patient risk factors (smoking history, age, family history) influence management decisions.",
                "clinical_significance": "Management follows established guidelines (Fleischner Society) based on nodule size and patient risk. May require CT follow-up imaging, PET scan for metabolic activity assessment, or tissue sampling via biopsy. Pulmonology consultation is often recommended for risk stratification."
            },
            "mass": {
                "summary": f"Pulmonary mass identified with {confidence:.1%} confidence on {scan_type.replace('_', ' ')}. This is a larger lung lesion (>3cm) that requires urgent evaluation to determine its nature. The {urgency_level.lower()} classification emphasizes the need for prompt, comprehensive investigation including possible malignancy workup.",
                "explanation": "Pulmonary masses are larger than nodules (>3cm diameter) and have higher concern for malignancy. They appear as large, often irregular opacities in the lung tissue. Masses require prompt evaluation including advanced imaging (CT with contrast, PET scan) and often tissue sampling for definitive diagnosis. Associated findings like lymphadenopathy or pleural effusion may indicate advanced disease.",
                "clinical_significance": "Requires urgent multidisciplinary evaluation including oncology, pulmonology, and thoracic surgery consultation. Staging studies (CT chest/abdomen/pelvis, brain MRI, bone scan) may be needed if malignancy is suspected. Treatment planning depends on histology and staging results."
            },
            "no acute findings": {
                "summary": f"No acute findings detected with {confidence:.1%} confidence on {scan_type.replace('_', ' ')}. This indicates no immediate abnormalities requiring urgent intervention. The {urgency_level.lower()} assessment reflects the reassuring nature of these results, though clinical correlation remains important.",
                "explanation": "A normal chest X-ray shows clear lung fields with normal vascular markings, normal heart size and contour, clear costophrenic angles, and normal mediastinal structures. While reassuring, normal imaging doesn't rule out all possible conditions, especially early-stage diseases, small lesions, or conditions not visible on plain radiographs.",
                "clinical_significance": "Routine follow-up as clinically indicated based on symptoms and risk factors. Persistent or worsening symptoms despite normal imaging may warrant additional evaluation with CT or other modalities. Continue appropriate preventive care and monitoring."
            }
        }
        
        # Find matching summary
        finding_lower = finding.lower()
        for condition, content in summaries.items():
            if condition in finding_lower or finding_lower in condition:
                return {
                    **content,
                    "confidence_interpretation": self._interpret_radiology_confidence(confidence),
                    "urgency_interpretation": self._interpret_urgency(urgency_level),
                    "scan_type": scan_type.replace('_', ' ').title(),
                    "generated_at": datetime.utcnow().isoformat()
                }
        
        # Default summary for unknown conditions
        return {
            "summary": f"{finding} detected with {confidence:.1%} confidence on {scan_type.replace('_', ' ')}. This finding requires professional radiological interpretation and clinical correlation. The {urgency_level.lower()} assessment guides the appropriate follow-up timeline.",
            "explanation": f"Professional radiological evaluation is recommended for {finding}. A qualified radiologist can provide detailed interpretation and recommend appropriate follow-up or additional imaging as needed.",
            "clinical_significance": "Clinical correlation with symptoms and history is important for appropriate management decisions.",
            "confidence_interpretation": self._interpret_radiology_confidence(confidence),
            "urgency_interpretation": self._interpret_urgency(urgency_level),
            "scan_type": scan_type.replace('_', ' ').title(),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_radiology_ai_insights(
        self, 
        finding: str, 
        confidence: float, 
        urgency_level: str, 
        scan_type: str,
        clinical_summary: str
    ) -> Dict[str, Any]:
        """Generate enhanced AI insights using GROQ API for radiology"""
        
        try:
            return await self.api_service.groq.generate_radiology_summary(
                finding=finding,
                confidence=confidence,
                urgency_level=urgency_level,
                scan_type=scan_type,
                clinical_summary=clinical_summary
            )
        except Exception as e:
            logger.error(f"GROQ API failed for radiology: {e}")
            return self._generate_immediate_radiology_summary(finding, confidence, urgency_level, scan_type)
    
    async def _fetch_radiology_medical_resources(self, finding: str, scan_type: str) -> Dict[str, Any]:
        """Fetch radiology medical resources using Tavily API"""
        
        try:
            return await self.api_service.tavily.fetch_radiology_resources(
                condition=finding,
                scan_type=scan_type
            )
        except Exception as e:
            logger.error(f"Tavily API failed for radiology: {e}")
            return self._get_fallback_radiology_resources(finding, scan_type)
    
    async def _extract_radiology_keywords(
        self, 
        finding: str, 
        recommendations: List[str], 
        clinical_summary: str,
        scan_type: str = "chest_xray"
    ) -> Dict[str, Any]:
        """Extract keywords using Keyword AI for radiology"""
        
        try:
            text_content = [finding, clinical_summary] + recommendations
            return await self.api_service.keyword_ai.extract_radiology_keywords(
                text_content=text_content,
                finding=finding
            )
        except Exception as e:
            logger.error(f"Keyword AI failed for radiology: {e}")
            return self._get_fallback_radiology_keywords(finding, recommendations, scan_type)
    
    def _interpret_radiology_confidence(self, confidence: float) -> str:
        """Interpret confidence level for radiology findings"""
        if confidence >= 0.8:
            return f"High confidence ({confidence:.1%}) indicates strong certainty in the radiological assessment based on clear imaging features."
        elif confidence >= 0.6:
            return f"Good confidence ({confidence:.1%}) shows reasonable certainty, with radiologist confirmation recommended."
        elif confidence >= 0.4:
            return f"Moderate confidence ({confidence:.1%}) suggests some uncertainty, making professional radiological review important."
        else:
            return f"Low confidence ({confidence:.1%}) indicates significant uncertainty, requiring expert radiological interpretation."
    
    def _interpret_urgency(self, urgency_level: str) -> str:
        """Interpret urgency level"""
        urgency_interpretations = {
            "emergency": "Emergency - Immediate medical attention required within minutes to hours",
            "urgent": "Urgent - Medical evaluation needed within 24-48 hours",
            "routine": "Routine - Follow-up as clinically indicated, typically within days to weeks",
            "follow-up": "Follow-up - Scheduled monitoring or additional evaluation recommended"
        }
        return urgency_interpretations.get(urgency_level.lower(), f"Medical evaluation recommended based on {urgency_level} classification")
    
    def _get_fallback_radiology_resources(self, finding: str, scan_type: str) -> Dict[str, Any]:
        """Get fallback medical resources for radiology findings"""
        
        resources = {
            "educational_materials": [
                {
                    "title": f"Understanding {finding.title()}",
                    "description": f"Comprehensive guide to {finding} on {scan_type.replace('_', ' ')}",
                    "type": "educational",
                    "source": "Medical Education Database"
                },
                {
                    "title": f"{scan_type.replace('_', ' ').title()} Interpretation Guide",
                    "description": f"Professional guide to interpreting {scan_type.replace('_', ' ')} findings",
                    "type": "professional",
                    "source": "Radiology Reference"
                }
            ],
            "clinical_guidelines": [
                {
                    "title": f"Management of {finding.title()}",
                    "organization": "American College of Radiology",
                    "type": "guideline"
                },
                {
                    "title": f"{scan_type.replace('_', ' ').title()} Best Practices",
                    "organization": "Radiological Society",
                    "type": "best_practice"
                }
            ],
            "support_resources": [
                {
                    "title": "Patient Support Groups",
                    "description": "Connect with others who have similar findings",
                    "type": "support"
                },
                {
                    "title": "Questions to Ask Your Doctor",
                    "description": "Prepared questions for your medical consultation",
                    "type": "preparation"
                }
            ]
        }
        
        return resources
    
    def _get_fallback_radiology_keywords(self, finding: str, recommendations: List[str], scan_type: str = "chest_xray") -> Dict[str, Any]:
        """Get fallback keywords for radiology findings"""
        
        # Common radiology keywords by finding type
        keyword_mapping = {
            "pneumonia": {
                "conditions": ["pneumonia", "lung infection", "consolidation", "infiltrate"],
                "symptoms": ["fever", "cough", "shortness of breath", "chest pain"],
                "treatments": ["antibiotics", "oxygen therapy", "supportive care", "hospitalization"],
                "procedures": ["chest x-ray", "sputum culture", "blood culture", "pulse oximetry"]
            },
            "pneumothorax": {
                "conditions": ["pneumothorax", "collapsed lung", "air leak", "pleural air"],
                "symptoms": ["sudden chest pain", "shortness of breath", "reduced breath sounds"],
                "treatments": ["chest tube", "needle decompression", "observation", "surgery"],
                "procedures": ["thoracostomy", "chest tube insertion", "CT scan", "arterial blood gas"]
            },
            "pleural effusion": {
                "conditions": ["pleural effusion", "fluid accumulation", "transudative", "exudative"],
                "symptoms": ["shortness of breath", "chest pain", "reduced breath sounds"],
                "treatments": ["thoracentesis", "chest tube", "diuretics", "pleurodesis"],
                "procedures": ["diagnostic tap", "therapeutic drainage", "pleural fluid analysis", "ultrasound"]
            },
            "cardiomegaly": {
                "conditions": ["cardiomegaly", "heart enlargement", "cardiac dilation", "heart failure"],
                "symptoms": ["shortness of breath", "fatigue", "swelling", "chest pain"],
                "treatments": ["ACE inhibitors", "diuretics", "beta blockers", "lifestyle changes"],
                "procedures": ["echocardiogram", "ECG", "cardiac catheterization", "stress test"]
            },
            "nodule": {
                "conditions": ["pulmonary nodule", "lung spot", "solitary nodule", "granuloma"],
                "symptoms": ["usually asymptomatic", "cough", "chest pain"],
                "treatments": ["observation", "biopsy", "surgical resection", "follow-up imaging"],
                "procedures": ["CT scan", "PET scan", "bronchoscopy", "needle biopsy"]
            },
            "mass": {
                "conditions": ["pulmonary mass", "lung mass", "tumor", "malignancy"],
                "symptoms": ["cough", "weight loss", "chest pain", "hemoptysis"],
                "treatments": ["surgery", "chemotherapy", "radiation", "targeted therapy"],
                "procedures": ["biopsy", "staging studies", "bronchoscopy", "mediastinoscopy"]
            }
        }
        
        # Extract keywords based on finding
        finding_lower = finding.lower()
        extracted_keywords = {
            "conditions": [],
            "symptoms": [],
            "treatments": [],
            "procedures": []
        }
        
        for condition, keywords in keyword_mapping.items():
            if condition in finding_lower:
                for category, terms in keywords.items():
                    extracted_keywords[category].extend(terms)
                break
        
        # If no specific match, use general terms
        if not any(extracted_keywords.values()):
            extracted_keywords = {
                "conditions": [finding.lower()],
                "symptoms": ["chest symptoms", "breathing difficulty"],
                "treatments": ["medical evaluation", "follow-up care"],
                "procedures": ["imaging studies", "clinical assessment"]
            }
        
        # Add keywords from recommendations
        recommendation_keywords = []
        for rec in recommendations:
            if "follow-up" in rec.lower():
                recommendation_keywords.append("follow-up")
            if "urgent" in rec.lower() or "immediate" in rec.lower():
                recommendation_keywords.append("urgent care")
            if "specialist" in rec.lower() or "consultation" in rec.lower():
                recommendation_keywords.append("specialist consultation")
        
        return {
            "conditions": extracted_keywords["conditions"][:5],  # Top 5 conditions
            "symptoms": extracted_keywords["symptoms"][:4],      # Top 4 symptoms  
            "treatments": extracted_keywords["treatments"][:5],  # Top 5 treatments
            "procedures": extracted_keywords["procedures"][:4],  # Top 4 procedures
            "categories": [
                "radiology",
                scan_type.replace('_', ' '),
                finding.lower().replace(' ', '_')
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
