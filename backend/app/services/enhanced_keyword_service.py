"""
Enhanced Keyword AI Service with Comprehensive Medical Term Extraction and Fallbacks
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class EnhancedKeywordAIService:
    """Enhanced Keyword AI service with comprehensive medical term extraction and fallbacks"""
    
    def __init__(self):
        self.api_key = os.getenv("KEYWORD_AI_KEY")
        self.base_url = "https://api.keywordai.co"
        
    async def extract_medical_keywords(
        self, 
        text_content: List[str],
        analysis_type: str = "skin"
    ) -> Dict[str, Any]:
        """Extract comprehensive medical keywords with robust fallbacks"""
        
        try:
            if self.api_key and self.api_key != "your_keyword_ai_key_here":
                # Try API call first
                api_result = await self._call_keyword_api(text_content, analysis_type)
                if api_result and any(api_result.get(key, []) for key in ["conditions", "symptoms", "treatments", "procedures"]):
                    return api_result
            
            # Fallback to comprehensive local extraction
            return self._extract_comprehensive_fallback_keywords(text_content, analysis_type)
            
        except Exception as e:
            logger.error(f"Error in Keyword AI service: {str(e)}")
            return self._extract_comprehensive_fallback_keywords(text_content, analysis_type)
    
    async def _call_keyword_api(self, text_content: List[str], analysis_type: str) -> Optional[Dict[str, Any]]:
        """Call Keyword AI API with proper error handling"""
        
        try:
            # Combine all text content
            combined_text = " ".join(text_content)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "text": combined_text,
                    "domain": "medical",
                    "max_keywords": 20,
                    "include_phrases": True,
                    "filter_categories": [
                        "medical_conditions",
                        "symptoms", 
                        "treatments",
                        "anatomy",
                        "procedures",
                        "diagnostics"
                    ]
                }
                
                async with session.post(
                    f"{self.base_url}/extract",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Categorize keywords
                        keywords = {
                            "conditions": [],
                            "symptoms": [],
                            "treatments": [],
                            "procedures": [],
                            "anatomy": [],
                            "general": []
                        }
                        
                        for keyword_data in data.get("keywords", []):
                            keyword = keyword_data.get("term", "")
                            category = keyword_data.get("category", "general")
                            confidence = keyword_data.get("confidence", 0)
                            
                            if confidence > 0.5:  # Only include high-confidence keywords
                                if category in keywords:
                                    keywords[category].append(keyword)
                                else:
                                    keywords["general"].append(keyword)
                        
                        return {
                            **keywords,
                            "extracted_at": datetime.utcnow().isoformat(),
                            "source": "keyword_api"
                        }
                    else:
                        logger.warning(f"Keyword AI API returned status {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Keyword AI API call failed: {str(e)}")
            return None
    
    def _extract_comprehensive_fallback_keywords(self, text_content: List[str], analysis_type: str) -> Dict[str, Any]:
        """Extract comprehensive medical keywords using local processing"""
        
        # Combine all text content
        combined_text = " ".join(text_content).lower()
        
        # Comprehensive medical keyword databases
        medical_keywords = self._get_comprehensive_medical_keywords(analysis_type)
        
        # Extract keywords that appear in the text content
        extracted_keywords = {
            "conditions": [],
            "symptoms": [],
            "treatments": [],
            "procedures": [],
            "anatomy": [],
            "general": []
        }
        
        # Extract keywords by category
        for category, keywords in medical_keywords.items():
            for keyword in keywords:
                if self._keyword_matches(keyword.lower(), combined_text):
                    if keyword not in extracted_keywords[category]:
                        extracted_keywords[category].append(keyword)
        
        # Add context-specific keywords based on the analysis
        context_keywords = self._extract_context_keywords(combined_text, analysis_type)
        for category, keywords in context_keywords.items():
            extracted_keywords[category].extend(keywords)
            # Remove duplicates while preserving order
            extracted_keywords[category] = list(dict.fromkeys(extracted_keywords[category]))
        
        # Limit keywords per category for better UX
        for category in extracted_keywords:
            extracted_keywords[category] = extracted_keywords[category][:8]
        
        return {
            **extracted_keywords,
            "extracted_at": datetime.utcnow().isoformat(),
            "source": "comprehensive_fallback"
        }
    
    def _keyword_matches(self, keyword: str, text: str) -> bool:
        """Check if keyword matches in text with various patterns"""
        
        # Direct match
        if keyword in text:
            return True
        
        # Word boundary match
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            return True
        
        # Partial match for compound terms
        if len(keyword.split()) > 1:
            words = keyword.split()
            if all(word in text for word in words):
                return True
        
        return False
    
    def _get_comprehensive_medical_keywords(self, analysis_type: str) -> Dict[str, List[str]]:
        """Get comprehensive medical keyword database"""
        
        if analysis_type == "skin":
            return {
                "conditions": [
                    "melanoma", "basal cell carcinoma", "squamous cell carcinoma",
                    "actinic keratosis", "seborrheic keratosis", "dermatofibroma",
                    "nevus", "mole", "lesion", "carcinoma", "keratosis",
                    "skin cancer", "malignant melanoma", "BCC", "SCC",
                    "atypical nevus", "dysplastic nevus", "lentigo",
                    "dermatitis", "eczema", "psoriasis", "rosacea"
                ],
                "symptoms": [
                    "asymmetry", "border irregularity", "color variation",
                    "diameter", "evolution", "bleeding", "itching",
                    "crusting", "scaling", "ulceration", "nodule",
                    "papule", "macule", "plaque", "erosion",
                    "pigmentation", "discoloration", "growth",
                    "texture change", "surface change"
                ],
                "treatments": [
                    "excision", "biopsy", "cryotherapy", "electrodesiccation",
                    "curettage", "Mohs surgery", "radiation therapy",
                    "topical chemotherapy", "immunotherapy", "laser therapy",
                    "photodynamic therapy", "surgical removal",
                    "wide local excision", "sentinel lymph node biopsy"
                ],
                "procedures": [
                    "dermoscopy", "dermatoscopy", "biopsy", "histopathology",
                    "punch biopsy", "shave biopsy", "excisional biopsy",
                    "frozen section", "immunohistochemistry",
                    "molecular testing", "genetic testing",
                    "lymph node mapping", "staging"
                ],
                "anatomy": [
                    "epidermis", "dermis", "subcutaneous", "melanocyte",
                    "keratinocyte", "basal layer", "stratum corneum",
                    "hair follicle", "sebaceous gland", "sweat gland",
                    "lymph node", "blood vessel", "nerve"
                ],
                "general": [
                    "dermatology", "oncology", "pathology", "diagnosis",
                    "prognosis", "staging", "metastasis", "recurrence",
                    "surveillance", "follow-up", "prevention",
                    "sun protection", "UV exposure", "risk factors"
                ]
            }
        
        elif analysis_type == "radiology":
            return {
                "conditions": [
                    "pneumonia", "pneumothorax", "pleural effusion",
                    "cardiomegaly", "atelectasis", "consolidation",
                    "infiltrate", "nodule", "mass", "opacity",
                    "emphysema", "fibrosis", "edema"
                ],
                "symptoms": [
                    "opacity", "consolidation", "air bronchogram",
                    "ground glass", "honeycombing", "reticular pattern",
                    "nodular pattern", "cavitation", "calcification"
                ],
                "treatments": [
                    "antibiotics", "bronchodilators", "steroids",
                    "oxygen therapy", "mechanical ventilation",
                    "chest tube", "thoracentesis", "surgery"
                ],
                "procedures": [
                    "chest X-ray", "CT scan", "MRI", "ultrasound",
                    "bronchoscopy", "biopsy", "thoracentesis",
                    "chest tube insertion"
                ],
                "anatomy": [
                    "lung", "pleura", "mediastinum", "heart",
                    "diaphragm", "ribs", "clavicle", "trachea",
                    "bronchi", "alveoli"
                ],
                "general": [
                    "radiology", "imaging", "diagnosis", "pathology",
                    "respiratory", "pulmonary", "cardiac", "thoracic"
                ]
            }
        
        # Default/general medical keywords
        return {
            "conditions": ["condition", "disease", "disorder", "syndrome"],
            "symptoms": ["symptom", "sign", "manifestation"],
            "treatments": ["treatment", "therapy", "medication"],
            "procedures": ["procedure", "examination", "test"],
            "anatomy": ["organ", "tissue", "structure"],
            "general": ["medical", "clinical", "healthcare", "diagnosis"]
        }
    
    def _extract_context_keywords(self, text: str, analysis_type: str) -> Dict[str, List[str]]:
        """Extract context-specific keywords based on the analysis content"""
        
        context_keywords = {
            "conditions": [],
            "symptoms": [],
            "treatments": [],
            "procedures": [],
            "anatomy": [],
            "general": []
        }
        
        # Risk level keywords
        if "high risk" in text or "urgent" in text:
            context_keywords["general"].extend(["high risk", "urgent care", "immediate attention"])
        elif "medium risk" in text or "moderate" in text:
            context_keywords["general"].extend(["medium risk", "professional evaluation"])
        elif "low risk" in text:
            context_keywords["general"].extend(["low risk", "monitoring", "routine care"])
        
        # Confidence level keywords
        if "confidence" in text:
            context_keywords["general"].append("diagnostic confidence")
        
        # Recommendation keywords
        if "dermatologist" in text:
            context_keywords["procedures"].append("dermatological consultation")
        if "biopsy" in text:
            context_keywords["procedures"].append("tissue biopsy")
        if "monitor" in text:
            context_keywords["general"].append("clinical monitoring")
        
        # Time-sensitive keywords
        if "immediate" in text or "emergency" in text:
            context_keywords["general"].extend(["emergency care", "immediate evaluation"])
        if "schedule" in text or "appointment" in text:
            context_keywords["general"].append("medical appointment")
        
        # Prevention keywords
        if "sun protection" in text or "prevention" in text:
            context_keywords["general"].extend(["prevention", "sun protection"])
        
        return context_keywords
