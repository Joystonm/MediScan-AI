"""
API Integration Services for MediScan-AI
Handles GROQ, Tavily, and Keyword AI integrations with parallel processing
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GroqService:
    """Service for GROQ API integration - AI summaries and explanations"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama3-8b-8192"
        logger.info(f"GROQ API key configured: {bool(self.api_key and self.api_key != 'your_groq_api_key_here')}")
        
    async def generate_medical_summary(
        self, 
        prediction: str, 
        confidence: float, 
        risk_level: str,
        analysis_type: str = "skin"
    ) -> Dict[str, str]:
        """Generate natural language summary of medical analysis results"""
        
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            logger.warning("GROQ API key not configured properly")
            return self._get_fallback_summary(prediction, confidence, risk_level, analysis_type)
        
        try:
            logger.info(f"Calling GROQ API for {prediction}")
            prompt = self._build_summary_prompt(prediction, confidence, risk_level, analysis_type)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a medical AI assistant providing clear, accurate explanations of diagnostic results. Always include appropriate medical disclaimers."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.3
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15)  # Reduced timeout for faster response
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        summary = data["choices"][0]["message"]["content"]
                        explanation = await self._generate_condition_explanation(prediction)
                        
                        logger.info("GROQ API call successful")
                        return {
                            "summary": summary,
                            "explanation": explanation,
                            "confidence_interpretation": self._interpret_confidence(confidence),
                            "risk_interpretation": self._interpret_risk_level(risk_level),
                            "generated_at": datetime.utcnow().isoformat()
                        }
                    else:
                        logger.error(f"GROQ API error: {response.status}")
                        error_text = await response.text()
                        logger.error(f"GROQ API error details: {error_text}")
                        return self._get_fallback_summary(prediction, confidence, risk_level, analysis_type)
                        
        except asyncio.TimeoutError:
            logger.error("GROQ API timeout")
            return self._get_fallback_summary(prediction, confidence, risk_level, analysis_type)
        except Exception as e:
            logger.error(f"Error calling GROQ API: {str(e)}")
            return self._get_fallback_summary(prediction, confidence, risk_level, analysis_type)

    def _interpret_confidence(self, confidence: float) -> str:
        """Interpret confidence level for patients"""
        if confidence >= 0.8:
            return f"High confidence ({confidence:.1%}) - The AI model is very certain about this assessment based on clear diagnostic features."
        elif confidence >= 0.6:
            return f"Good confidence ({confidence:.1%}) - The AI model shows good certainty, but professional confirmation is recommended."
        elif confidence >= 0.4:
            return f"Moderate confidence ({confidence:.1%}) - The AI model shows some uncertainty, professional evaluation is important."
        else:
            return f"Low confidence ({confidence:.1%}) - The AI model is uncertain, professional medical assessment is essential."

    def _interpret_risk_level(self, risk_level: str) -> str:
        """Interpret risk level for patients"""
        interpretations = {
            "HIGH": "High risk indicates features that may suggest a serious condition requiring immediate medical attention.",
            "MEDIUM": "Medium risk indicates features that warrant professional evaluation within a reasonable timeframe.",
            "LOW": "Low risk indicates features that appear benign but should still be monitored regularly.",
            "CRITICAL": "Critical risk indicates features requiring emergency medical evaluation."
        }
        return interpretations.get(risk_level.upper(), "Professional medical evaluation is recommended.")

    async def _generate_condition_explanation(self, condition: str) -> str:
        """Generate detailed condition explanation with timeout"""
        
        if self.api_key and self.api_key != "your_groq_api_key_here":
            try:
                prompt = f"""
                Provide a brief, patient-friendly explanation of the medical condition: {condition}
                
                Include:
                1. What this condition is (definition)
                2. How common it is
                3. Typical symptoms and appearance
                4. Why professional medical evaluation is important
                
                Keep it informative but not alarming. Use clear, accessible language. Maximum 200 words.
                """
                
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a medical educator providing clear, accurate information about medical conditions to patients."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 300,
                        "temperature": 0.2
                    }
                    
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10)  # Short timeout for explanation
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            return data["choices"][0]["message"]["content"]
                            
            except Exception as e:
                logger.error(f"Error generating condition explanation: {str(e)}")
        
        # Fallback to local explanation
        return self._get_fallback_explanation(condition)

    def _get_fallback_explanation(self, condition: str) -> str:
        """Get fallback explanation for conditions"""
        explanations = {
            "melanoma": "Melanoma is a type of skin cancer that develops from melanocytes. It is the most serious type of skin cancer but is highly treatable when detected early. Professional evaluation is crucial for accurate diagnosis and treatment planning.",
            "basal cell carcinoma": "Basal cell carcinoma is the most common type of skin cancer. It grows slowly and rarely spreads to other parts of the body, making it highly treatable with early intervention.",
            "squamous cell carcinoma": "Squamous cell carcinoma is the second most common type of skin cancer. It can be more aggressive than basal cell carcinoma but is still highly treatable when caught early.",
            "actinic keratosis": "Actinic keratosis is a precancerous skin condition caused by sun damage. While not cancer itself, it can develop into squamous cell carcinoma if left untreated.",
            "seborrheic keratosis": "Seborrheic keratosis is a common, benign skin growth that appears as people age. These growths are typically harmless but should be evaluated to rule out other conditions.",
            "nevus": "A nevus (mole) is a common, usually benign skin growth. Most moles are harmless, but changes in appearance should be evaluated by a dermatologist.",
            "dermatofibroma": "Dermatofibroma is a common, benign skin growth that typically appears as a small, firm bump. These growths are generally harmless but can be removed if bothersome."
        }
        
        condition_lower = condition.lower()
        for key, explanation in explanations.items():
            if key in condition_lower:
                return explanation
        
        return f"Professional medical evaluation is recommended for {condition} to ensure accurate diagnosis and appropriate treatment planning."

    def _build_summary_prompt(self, prediction: str, confidence: float, risk_level: str, analysis_type: str) -> str:
        """Build prompt for medical summary"""
        return f"""
        Generate a concise medical summary for this {analysis_type} analysis:
        
        **Results:**
        - Condition: {prediction}
        - Confidence: {confidence:.1%}
        - Risk Level: {risk_level}
        
        **Provide:**
        1. Clear explanation of what this diagnosis means
        2. The significance of the confidence level
        3. What the risk level indicates
        4. Appropriate next steps
        
        **Requirements:**
        - Use clear, patient-friendly language
        - Include medical disclaimer
        - Keep under 400 words
        - Be professional but reassuring where appropriate
        """

    def _get_fallback_summary(self, prediction: str, confidence: float, risk_level: str, analysis_type: str) -> Dict[str, str]:
        """Generate fallback summary when API is unavailable"""
        
        risk_descriptions = {
            "HIGH": "requires immediate medical attention",
            "MEDIUM": "warrants professional evaluation",
            "LOW": "appears to be low risk but should be monitored"
        }
        
        summary = f"""
        The AI analysis has identified {prediction} with {confidence:.1%} confidence. 
        This {risk_level.lower()} risk finding {risk_descriptions.get(risk_level.upper(), 'requires evaluation')}.
        
        A {confidence:.1%} confidence level indicates {'high certainty' if confidence > 0.7 else 'moderate certainty' if confidence > 0.4 else 'low certainty'} in the AI's assessment. 
        Professional medical evaluation is recommended for accurate diagnosis and treatment planning.
        
        **Important:** This AI analysis is for informational purposes only and should not replace professional medical advice.
        """
        
        return {
            "summary": summary.strip(),
            "explanation": self._get_fallback_explanation(prediction),
            "confidence_interpretation": self._interpret_confidence(confidence),
            "risk_interpretation": self._interpret_risk_level(risk_level),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_condition_explanation(self, condition: str) -> str:
        """Generate detailed explanation of the medical condition"""
        
        if not self.api_key:
            return self._get_fallback_explanation(condition)
        
        try:
            prompt = f"""
            Provide a clear, patient-friendly explanation of the medical condition: {condition}
            
            Include:
            1. What this condition is
            2. Common characteristics
            3. Typical causes or risk factors
            4. General prognosis
            5. Why medical evaluation is important
            
            Keep it informative but not alarming. Always emphasize the need for professional medical evaluation.
            """
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a medical educator providing clear, accurate information about medical conditions to patients."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 400,
                    "temperature": 0.2
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        return self._get_fallback_explanation(condition)
                        
        except Exception as e:
            logger.error(f"Error generating condition explanation: {str(e)}")
            return self._get_fallback_explanation(condition)
    
    def _build_summary_prompt(self, prediction: str, confidence: float, risk_level: str, analysis_type: str) -> str:
        """Build prompt for medical summary generation"""
        
        return f"""
        Generate a clear, professional medical summary for the following analysis results:
        
        Analysis Type: {analysis_type.title()} Analysis
        Top Prediction: {prediction}
        Confidence Level: {confidence:.1%}
        Risk Assessment: {risk_level}
        
        Please provide:
        1. A natural language summary of what this means
        2. The significance of the confidence level
        3. What the risk level indicates
        4. Appropriate next steps
        
        Important: Always include a medical disclaimer that this is AI-assisted analysis and professional medical evaluation is required for diagnosis and treatment decisions.
        
        Keep the tone professional but accessible to patients.
        """
    
    def _get_fallback_summary(self, prediction: str, confidence: float, risk_level: str, analysis_type: str) -> Dict[str, str]:
        """Fallback summary when API is unavailable"""
        
        risk_descriptions = {
            "HIGH": "requires immediate medical attention",
            "MEDIUM": "warrants professional evaluation",
            "LOW": "appears to be low risk but should be monitored"
        }
        
        summary = f"""
        The AI analysis suggests {prediction.lower()} with {confidence:.1%} confidence. 
        This {risk_level.lower()} risk finding {risk_descriptions.get(risk_level, 'requires evaluation')}.
        
        Please note: This is an AI-assisted analysis tool and should not replace professional medical diagnosis. 
        Always consult with qualified healthcare professionals for proper evaluation and treatment decisions.
        """
        
        explanation = self._get_fallback_explanation(prediction)
        
        return {
            "summary": summary.strip(),
            "explanation": explanation,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_fallback_explanation(self, condition: str) -> str:
        """Fallback explanation when API is unavailable"""
        
        explanations = {
            "melanoma": "Melanoma is a type of skin cancer that develops from melanocytes (pigment-producing cells). Early detection and treatment are crucial for the best outcomes.",
            "basal cell carcinoma": "Basal cell carcinoma is the most common type of skin cancer. It typically grows slowly and rarely spreads to other parts of the body when treated early.",
            "squamous cell carcinoma": "Squamous cell carcinoma is a common form of skin cancer that can be more aggressive than basal cell carcinoma but is highly treatable when caught early.",
            "actinic keratosis": "Actinic keratosis is a precancerous skin condition caused by sun damage. While not cancer itself, it can develop into squamous cell carcinoma if left untreated.",
            "seborrheic keratosis": "Seborrheic keratosis is a common, benign (non-cancerous) skin growth. These growths are typically harmless but should be evaluated to rule out other conditions.",
            "nevus": "A nevus (mole) is a common, usually benign skin growth. Most moles are harmless, but changes in size, color, or shape should be evaluated by a dermatologist.",
            "dermatofibroma": "Dermatofibroma is a common, benign skin growth that typically appears as a small, firm bump. These are generally harmless but can be removed if bothersome."
        }
        
        condition_lower = condition.lower()
        for key, explanation in explanations.items():
            if key in condition_lower:
                return explanation
        
        return f"{condition} is a skin condition that requires professional medical evaluation for proper diagnosis and treatment recommendations."


class TavilyService:
    """Service for Tavily API integration - Medical images and articles"""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com"
        logger.info(f"Tavily API key configured: {bool(self.api_key and self.api_key != 'your_tavily_api_key_here')}")
        
    async def fetch_medical_resources(
        self, 
        condition: str, 
        analysis_type: str = "skin"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch relevant medical images and articles with optimized performance"""
        
        if not self.api_key or self.api_key == "your_tavily_api_key_here":
            logger.warning("Tavily API key not configured properly")
            return self._get_fallback_resources(condition, analysis_type)
        
        try:
            logger.info(f"Calling Tavily API for {condition}")
            
            # Only fetch articles for faster response - images can be added later if needed
            articles_task = self._fetch_medical_articles(condition, analysis_type)
            
            # Use timeout for faster response
            try:
                articles = await asyncio.wait_for(articles_task, timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("Tavily API timeout, using fallback")
                articles = []
            
            logger.info(f"Tavily API call completed: {len(articles)} articles")
            return {
                "reference_images": [],  # Skip images for faster loading
                "medical_articles": articles,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching medical resources: {str(e)}")
            return self._get_fallback_resources(condition, analysis_type)
    
    async def _fetch_medical_articles(self, condition: str, analysis_type: str) -> List[Dict[str, Any]]:
        """Fetch relevant medical articles with optimized query"""
        
        try:
            # Optimized query for faster, more relevant results
            query = f"{condition} dermatology treatment diagnosis"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": query,
                    "search_depth": "basic",  # Use basic for faster response
                    "include_images": False,
                    "max_results": 5,  # Reduced for faster response
                    "include_domains": [
                        "mayoclinic.org",
                        "aad.org",
                        "dermnetnz.org",
                        "skincancer.org"
                    ]
                }
                
                async with session.post(
                    f"{self.base_url}/search",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=8)  # Reduced timeout
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for result in data.get("results", [])[:4]:  # Limit to 4 articles
                            articles.append({
                                "title": result.get("title", f"Medical Information: {condition}"),
                                "url": result.get("url"),
                                "source": result.get("source", "Medical Source"),
                                "snippet": result.get("content", "")[:200] + "..." if result.get("content") else f"Medical information about {condition}",
                                "published_date": result.get("published_date"),
                                "relevance_score": result.get("score", 0.8),
                                "content_type": "medical_article"
                            })
                        
                        return articles
                    else:
                        logger.warning(f"Tavily articles API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching medical articles: {str(e)}")
            return []
    
    def _get_fallback_resources(self, condition: str, analysis_type: str) -> Dict[str, List[Dict[str, Any]]]:
        """Generate fallback medical resources"""
        
        # High-quality fallback articles
        fallback_articles = [
            {
                "title": f"Understanding {condition}: Medical Overview",
                "url": "https://www.mayoclinic.org/diseases-conditions/skin-cancer/symptoms-causes/syc-20377605",
                "source": "Mayo Clinic",
                "snippet": f"Comprehensive medical information about {condition} including symptoms, diagnosis, and treatment options from Mayo Clinic medical experts.",
                "relevance_score": 0.9,
                "content_type": "medical_reference"
            },
            {
                "title": "Dermatology Guidelines and Best Practices",
                "url": "https://www.aad.org/public/diseases/skin-cancer",
                "source": "American Academy of Dermatology",
                "snippet": f"Professional guidelines for {condition} diagnosis, treatment, and patient care from leading dermatology experts.",
                "relevance_score": 0.85,
                "content_type": "clinical_guidelines"
            },
            {
                "title": "Skin Health and Prevention",
                "url": "https://www.skincancer.org/",
                "source": "Skin Cancer Foundation",
                "snippet": "Educational resources about skin health, prevention strategies, and when to seek professional medical evaluation.",
                "relevance_score": 0.8,
                "content_type": "patient_education"
            }
        ]
        
        return {
            "reference_images": [],
            "medical_articles": fallback_articles,
            "fetched_at": datetime.utcnow().isoformat()
        }
    
    async def _fetch_reference_images(self, condition: str, analysis_type: str) -> List[Dict[str, Any]]:
        """Fetch reference medical images"""
        
        try:
            query = f"{condition} {analysis_type} medical images dermatology"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": query,
                    "search_depth": "basic",
                    "include_images": True,
                    "max_results": 5,
                    "include_domains": [
                        "dermnetnz.org",
                        "aad.org", 
                        "mayoclinic.org",
                        "webmd.com",
                        "healthline.com"
                    ]
                }
                
                async with session.post(
                    f"{self.base_url}/search",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        images = []
                        
                        for result in data.get("images", [])[:3]:  # Limit to 3 images
                            images.append({
                                "url": result.get("url"),
                                "title": result.get("title", f"Reference image of {condition}"),
                                "source": result.get("source", "Medical database"),
                                "description": result.get("description", f"Clinical example of {condition}")
                            })
                        
                        return images
                    else:
                        logger.error(f"Tavily images API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching reference images: {str(e)}")
            return []
    
    async def _fetch_medical_articles(self, condition: str, analysis_type: str) -> List[Dict[str, Any]]:
        """Fetch relevant medical articles and research"""
        
        try:
            query = f"{condition} {analysis_type} treatment diagnosis medical research"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": query,
                    "search_depth": "advanced",
                    "include_images": False,
                    "max_results": 8,
                    "include_domains": [
                        "pubmed.ncbi.nlm.nih.gov",
                        "dermnetnz.org",
                        "aad.org",
                        "mayoclinic.org",
                        "cancer.org",
                        "skincancer.org",
                        "nejm.org",
                        "jamanetwork.com"
                    ]
                }
                
                async with session.post(
                    f"{self.base_url}/search",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for result in data.get("results", [])[:5]:  # Limit to 5 articles
                            articles.append({
                                "title": result.get("title"),
                                "url": result.get("url"),
                                "source": result.get("source", "Medical journal"),
                                "snippet": result.get("content", "")[:200] + "...",
                                "published_date": result.get("published_date"),
                                "relevance_score": result.get("score", 0)
                            })
                        
                        return articles
                    else:
                        logger.error(f"Tavily articles API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching medical articles: {str(e)}")
            return []
    
    def _get_fallback_resources(self, condition: str, analysis_type: str) -> Dict[str, List[Dict[str, Any]]]:
        """Fallback resources when API is unavailable"""
        
        fallback_articles = [
            {
                "title": f"Understanding {condition}: Diagnosis and Treatment",
                "url": "https://www.aad.org/public/diseases/skin-cancer",
                "source": "American Academy of Dermatology",
                "snippet": f"Comprehensive information about {condition}, including symptoms, diagnosis, and treatment options.",
                "published_date": None,
                "relevance_score": 0.9
            },
            {
                "title": f"{condition} - Mayo Clinic",
                "url": "https://www.mayoclinic.org/diseases-conditions",
                "source": "Mayo Clinic",
                "snippet": f"Expert medical information about {condition} from Mayo Clinic specialists.",
                "published_date": None,
                "relevance_score": 0.85
            }
        ]
        
        return {
            "reference_images": [],
            "medical_articles": fallback_articles,
            "fetched_at": datetime.utcnow().isoformat()
        }


class KeywordAIService:
    """Service for Keyword AI integration - Medical term extraction"""
    
    def __init__(self):
        self.api_key = os.getenv("KEYWORD_AI_KEY")
        self.base_url = "https://api.keywordai.co"
        logger.info(f"Keyword AI key configured: {bool(self.api_key and self.api_key != 'your_keyword_ai_key_here')}")
        
    async def extract_medical_keywords(
        self, 
        text_content: List[str],
        analysis_type: str = "skin"
    ) -> Dict[str, List[str]]:
        """Extract relevant medical keywords and terms with optimized performance"""
        
        # Always use fallback for faster response - it's more reliable and faster
        return self._get_fallback_keywords(text_content, analysis_type)
    
    def _get_fallback_keywords(self, text_content: List[str], analysis_type: str) -> Dict[str, List[str]]:
        """Generate comprehensive medical keywords using local processing"""
        
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
        
        # Limit keywords per category for better UX and faster processing
        for category in extracted_keywords:
            extracted_keywords[category] = extracted_keywords[category][:6]
        
        return {
            **extracted_keywords,
            "extracted_at": datetime.utcnow().isoformat()
        }
    
    def _keyword_matches(self, keyword: str, text: str) -> bool:
        """Check if keyword matches in text with various patterns"""
        
        # Direct match
        if keyword in text:
            return True
        
        # Word boundary match for compound terms
        if len(keyword.split()) > 1:
            words = keyword.split()
            if all(word in text for word in words):
                return True
        
        return False
    
    def _get_comprehensive_medical_keywords(self, analysis_type: str) -> Dict[str, List[str]]:
        """Get comprehensive medical keyword database optimized for skin analysis"""
        
        if analysis_type == "skin":
            return {
                "conditions": [
                    "melanoma", "basal cell carcinoma", "squamous cell carcinoma",
                    "actinic keratosis", "seborrheic keratosis", "dermatofibroma",
                    "nevus", "mole", "lesion", "carcinoma", "keratosis",
                    "skin cancer", "atypical nevus", "dysplastic nevus"
                ],
                "symptoms": [
                    "asymmetry", "border irregularity", "color variation",
                    "diameter", "evolution", "bleeding", "itching",
                    "crusting", "scaling", "ulceration", "pigmentation"
                ],
                "treatments": [
                    "excision", "biopsy", "cryotherapy", "electrodesiccation",
                    "Mohs surgery", "radiation therapy", "topical chemotherapy",
                    "surgical removal", "wide local excision"
                ],
                "procedures": [
                    "dermoscopy", "dermatoscopy", "biopsy", "histopathology",
                    "punch biopsy", "shave biopsy", "excisional biopsy",
                    "immunohistochemistry", "staging"
                ],
                "general": [
                    "dermatology", "oncology", "pathology", "diagnosis",
                    "prognosis", "surveillance", "follow-up", "prevention",
                    "sun protection", "risk factors"
                ]
            }
        
        # Default/general medical keywords
        return {
            "conditions": ["condition", "disease", "disorder"],
            "symptoms": ["symptom", "sign", "manifestation"],
            "treatments": ["treatment", "therapy", "medication"],
            "procedures": ["procedure", "examination", "test"],
            "general": ["medical", "clinical", "healthcare", "diagnosis"]
        }
    
    def _extract_context_keywords(self, text: str, analysis_type: str) -> Dict[str, List[str]]:
        """Extract context-specific keywords based on the analysis content"""
        
        context_keywords = {
            "conditions": [],
            "symptoms": [],
            "treatments": [],
            "procedures": [],
            "general": []
        }
        
        # Risk level keywords
        if "high risk" in text or "urgent" in text:
            context_keywords["general"].extend(["high risk", "urgent care"])
        elif "medium risk" in text or "moderate" in text:
            context_keywords["general"].extend(["medium risk", "professional evaluation"])
        elif "low risk" in text:
            context_keywords["general"].extend(["low risk", "monitoring"])
        
        # Recommendation keywords
        if "dermatologist" in text:
            context_keywords["procedures"].append("dermatological consultation")
        if "biopsy" in text:
            context_keywords["procedures"].append("tissue biopsy")
        if "monitor" in text:
            context_keywords["general"].append("clinical monitoring")
        
        return context_keywords
    
    def _get_fallback_keywords(self, text_content: List[str], analysis_type: str) -> Dict[str, List[str]]:
        """Fallback keyword extraction using simple text processing"""
        
        # Predefined medical keywords for different analysis types
        skin_keywords = {
            "conditions": ["melanoma", "carcinoma", "lesion", "mole", "keratosis", "dermatitis"],
            "symptoms": ["asymmetry", "border irregularity", "color variation", "diameter", "evolution"],
            "treatments": ["biopsy", "excision", "cryotherapy", "topical treatment"],
            "procedures": ["dermoscopy", "histopathology", "surgical removal"],
            "general": ["dermatology", "skin cancer", "diagnosis", "monitoring"]
        }
        
        radiology_keywords = {
            "conditions": ["pneumonia", "pneumothorax", "cardiomegaly", "infiltrate"],
            "symptoms": ["opacity", "consolidation", "effusion", "nodule"],
            "treatments": ["antibiotics", "drainage", "surgery"],
            "procedures": ["chest x-ray", "CT scan", "bronchoscopy"],
            "general": ["radiology", "imaging", "diagnosis", "pathology"]
        }
        
        base_keywords = skin_keywords if analysis_type == "skin" else radiology_keywords
        
        # Extract keywords that appear in the text content
        combined_text = " ".join(text_content).lower()
        extracted_keywords = {}
        
        for category, keywords in base_keywords.items():
            extracted_keywords[category] = [
                keyword for keyword in keywords 
                if keyword.lower() in combined_text
            ]
        
        extracted_keywords["extracted_at"] = datetime.utcnow().isoformat()
        return extracted_keywords


class APIIntegrationService:
    """Main service that coordinates all API integrations with optimized parallel processing"""
    
    def __init__(self):
        self.groq = GroqService()
        self.tavily = TavilyService()
        self.keyword_ai = KeywordAIService()
        logger.info("API Integration Service initialized with optimized processing")
    
    async def enhance_analysis_results(
        self,
        prediction: str,
        confidence: float,
        risk_level: str,
        recommendations: List[str],
        analysis_type: str = "skin"
    ) -> Dict[str, Any]:
        """Enhance analysis results with AI-generated content using optimized parallel processing"""
        
        try:
            logger.info(f"Starting optimized API enhancement for {prediction}")
            start_time = datetime.utcnow()
            
            # Prepare text content for keyword extraction
            text_content = [prediction] + recommendations
            
            # Run all API calls in parallel with individual timeouts
            tasks = [
                asyncio.create_task(
                    self._safe_groq_call(prediction, confidence, risk_level, analysis_type),
                    name="groq_summary"
                ),
                asyncio.create_task(
                    self._safe_tavily_call(prediction, analysis_type),
                    name="tavily_resources"
                ),
                asyncio.create_task(
                    self._safe_keyword_call(text_content, analysis_type),
                    name="keyword_extraction"
                )
            ]
            
            # Wait for all tasks with a global timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=20.0  # Reduced global timeout for faster response
                )
                
                summary_data, resources_data, keywords_data = results
                
                # Handle any exceptions in individual tasks
                if isinstance(summary_data, Exception):
                    logger.error(f"GROQ task failed: {summary_data}")
                    summary_data = self._get_emergency_summary(prediction, confidence, risk_level)
                
                if isinstance(resources_data, Exception):
                    logger.error(f"Tavily task failed: {resources_data}")
                    resources_data = self._get_emergency_resources(prediction)
                
                if isinstance(keywords_data, Exception):
                    logger.error(f"Keyword task failed: {keywords_data}")
                    keywords_data = self._get_emergency_keywords(prediction)
                
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"All API calls completed in {processing_time:.2f} seconds")
                
            except asyncio.TimeoutError:
                logger.warning("Global API timeout, using emergency fallbacks")
                # Cancel remaining tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                
                # Use emergency fallbacks
                summary_data = self._get_emergency_summary(prediction, confidence, risk_level)
                resources_data = self._get_emergency_resources(prediction)
                keywords_data = self._get_emergency_keywords(prediction)
            
            return {
                "ai_summary": summary_data,
                "medical_resources": resources_data,
                "keywords": keywords_data,
                "enhancement_timestamp": datetime.utcnow().isoformat(),
                "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error enhancing analysis results: {str(e)}")
            # Return emergency fallback data
            return {
                "ai_summary": self._get_emergency_summary(prediction, confidence, risk_level),
                "medical_resources": self._get_emergency_resources(prediction),
                "keywords": self._get_emergency_keywords(prediction),
                "enhancement_timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def _safe_groq_call(self, prediction: str, confidence: float, risk_level: str, analysis_type: str) -> Dict[str, Any]:
        """Safely call GROQ API with timeout"""
        try:
            return await asyncio.wait_for(
                self.groq.generate_medical_summary(prediction, confidence, risk_level, analysis_type),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            logger.warning("GROQ API timeout")
            return self._get_emergency_summary(prediction, confidence, risk_level)
        except Exception as e:
            logger.error(f"GROQ API error: {e}")
            return self._get_emergency_summary(prediction, confidence, risk_level)
    
    async def _safe_tavily_call(self, prediction: str, analysis_type: str) -> Dict[str, Any]:
        """Safely call Tavily API with timeout"""
        try:
            return await asyncio.wait_for(
                self.tavily.fetch_medical_resources(prediction, analysis_type),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            logger.warning("Tavily API timeout")
            return self._get_emergency_resources(prediction)
        except Exception as e:
            logger.error(f"Tavily API error: {e}")
            return self._get_emergency_resources(prediction)
    
    async def _safe_keyword_call(self, text_content: List[str], analysis_type: str) -> Dict[str, Any]:
        """Safely call Keyword AI with timeout"""
        try:
            return await asyncio.wait_for(
                self.keyword_ai.extract_medical_keywords(text_content, analysis_type),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            logger.warning("Keyword AI timeout")
            return self._get_emergency_keywords(text_content[0] if text_content else "skin condition")
        except Exception as e:
            logger.error(f"Keyword AI error: {e}")
            return self._get_emergency_keywords(text_content[0] if text_content else "skin condition")
    
    def _get_emergency_summary(self, prediction: str, confidence: float, risk_level: str) -> Dict[str, Any]:
        """Get emergency fallback summary"""
        return {
            "summary": f"Analysis identified {prediction} with {confidence:.1%} confidence. This {risk_level.lower()} risk finding requires professional medical evaluation for accurate diagnosis and treatment planning.",
            "explanation": f"Professional dermatological evaluation is recommended for {prediction}. Early detection and appropriate medical care are important for optimal outcomes.",
            "confidence_interpretation": f"The AI shows {confidence:.1%} confidence in this assessment.",
            "risk_interpretation": f"This {risk_level.lower()} risk level indicates the need for appropriate medical follow-up.",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_emergency_resources(self, prediction: str) -> Dict[str, Any]:
        """Get emergency fallback resources"""
        return {
            "reference_images": [],
            "medical_articles": [
                {
                    "title": f"Medical Information: {prediction}",
                    "url": "https://www.mayoclinic.org/diseases-conditions/skin-cancer",
                    "source": "Mayo Clinic",
                    "snippet": f"Comprehensive medical information about {prediction} and related skin conditions.",
                    "relevance_score": 0.8
                },
                {
                    "title": "Dermatology Care Guidelines",
                    "url": "https://www.aad.org/public/diseases/skin-cancer",
                    "source": "American Academy of Dermatology",
                    "snippet": "Professional guidelines for skin condition evaluation and treatment.",
                    "relevance_score": 0.75
                }
            ],
            "fetched_at": datetime.utcnow().isoformat()
        }
    
    def _get_emergency_keywords(self, prediction: str) -> Dict[str, Any]:
        """Get emergency fallback keywords"""
        return {
            "conditions": [prediction, "skin condition"],
            "symptoms": ["lesion", "skin growth"],
            "treatments": ["medical evaluation", "dermatological consultation"],
            "procedures": ["clinical examination", "professional assessment"],
            "general": ["dermatology", "healthcare", "medical diagnosis"],
            "extracted_at": datetime.utcnow().isoformat()
        }


# Add radiology-specific methods to existing services
class GroqService(GroqService):
    """Extended GROQ service with radiology support"""
    
    async def generate_radiology_summary(
        self, 
        finding: str, 
        confidence: float, 
        urgency_level: str,
        scan_type: str,
        clinical_summary: str
    ) -> Dict[str, str]:
        """Generate natural language summary of radiology analysis results"""
        
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            logger.warning("GROQ API key not configured properly")
            return self._get_fallback_radiology_summary(finding, confidence, urgency_level, scan_type)
        
        try:
            logger.info(f"Calling GROQ API for radiology finding: {finding}")
            prompt = self._build_radiology_summary_prompt(finding, confidence, urgency_level, scan_type, clinical_summary)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a medical AI assistant specializing in radiology. Provide clear, accurate explanations of imaging findings. Always include appropriate medical disclaimers and emphasize the need for professional medical evaluation."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 600,
                    "temperature": 0.3
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        summary = data["choices"][0]["message"]["content"]
                        explanation = await self._generate_radiology_explanation(finding, scan_type)
                        
                        logger.info("GROQ API call successful for radiology")
                        return {
                            "summary": summary,
                            "explanation": explanation,
                            "confidence_interpretation": self._interpret_radiology_confidence(confidence),
                            "urgency_interpretation": self._interpret_urgency_level(urgency_level),
                            "clinical_significance": await self._get_clinical_significance(finding, urgency_level),
                            "generated_at": datetime.utcnow().isoformat()
                        }
                    else:
                        logger.error(f"GROQ API error for radiology: {response.status}")
                        return self._get_fallback_radiology_summary(finding, confidence, urgency_level, scan_type)
                        
        except Exception as e:
            logger.error(f"Error calling GROQ API for radiology: {str(e)}")
            return self._get_fallback_radiology_summary(finding, confidence, urgency_level, scan_type)

    def _build_radiology_summary_prompt(
        self, 
        finding: str, 
        confidence: float, 
        urgency_level: str, 
        scan_type: str,
        clinical_summary: str
    ) -> str:
        """Build prompt for radiology summary generation"""
        
        return f"""
        Please provide a clear, patient-friendly explanation of this radiology finding:
        
        Finding: {finding}
        Confidence: {confidence:.1%}
        Urgency Level: {urgency_level}
        Scan Type: {scan_type.replace('_', ' ').title()}
        Clinical Summary: {clinical_summary}
        
        Please explain:
        1. What this finding means in simple terms
        2. Why this finding is classified as {urgency_level.lower()} priority
        3. What patients should expect for next steps
        4. Any important considerations or precautions
        
        Keep the explanation clear, reassuring where appropriate, but medically accurate.
        Include a disclaimer that this is AI-generated information and professional medical evaluation is essential.
        """

    async def _generate_radiology_explanation(self, finding: str, scan_type: str) -> str:
        """Generate detailed explanation of radiology finding"""
        
        explanations = {
            "pneumonia": f"Pneumonia on {scan_type.replace('_', ' ')} appears as areas of increased density in the lung tissue, indicating inflammation and infection. This condition affects the air sacs in the lungs and typically requires antibiotic treatment.",
            
            "pneumothorax": f"Pneumothorax on {scan_type.replace('_', ' ')} shows air in the pleural space, causing partial or complete lung collapse. This condition can be life-threatening and may require immediate intervention.",
            
            "pleural effusion": f"Pleural effusion on {scan_type.replace('_', ' ')} indicates fluid accumulation around the lungs. This can result from various conditions and may cause breathing difficulties.",
            
            "cardiomegaly": f"Cardiomegaly on {scan_type.replace('_', ' ')} shows an enlarged heart shadow, which may indicate underlying heart disease requiring cardiac evaluation.",
            
            "pulmonary nodule": f"A pulmonary nodule on {scan_type.replace('_', ' ')} appears as a small, round spot in the lung. Most nodules are benign, but evaluation is important to rule out malignancy.",
            
            "mass": f"A pulmonary mass on {scan_type.replace('_', ' ')} is a larger lesion that requires urgent evaluation to determine its nature and appropriate treatment."
        }
        
        finding_lower = finding.lower()
        for condition, explanation in explanations.items():
            if condition in finding_lower:
                return explanation
        
        return f"This finding on {scan_type.replace('_', ' ')} requires professional radiological interpretation to determine its clinical significance and appropriate management."

    def _get_fallback_radiology_summary(
        self, 
        finding: str, 
        confidence: float, 
        urgency_level: str, 
        scan_type: str
    ) -> Dict[str, str]:
        """Get fallback summary for radiology findings"""
        
        return {
            "summary": f"Radiology analysis identified {finding} with {confidence:.1%} confidence on {scan_type.replace('_', ' ')}. This {urgency_level.lower()} priority finding requires appropriate medical evaluation and follow-up care.",
            "explanation": f"Professional radiological interpretation is recommended for {finding}. A qualified radiologist can provide detailed analysis and recommend appropriate next steps.",
            "confidence_interpretation": self._interpret_radiology_confidence(confidence),
            "urgency_interpretation": self._interpret_urgency_level(urgency_level),
            "clinical_significance": f"This {urgency_level.lower()} priority finding requires medical attention according to established clinical guidelines.",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _interpret_radiology_confidence(self, confidence: float) -> str:
        """Interpret confidence level for radiology findings"""
        if confidence >= 0.8:
            return f"High confidence ({confidence:.1%}) - The AI model shows strong certainty based on clear imaging features."
        elif confidence >= 0.6:
            return f"Good confidence ({confidence:.1%}) - The assessment shows reasonable certainty with professional confirmation recommended."
        elif confidence >= 0.4:
            return f"Moderate confidence ({confidence:.1%}) - Some uncertainty exists, making professional radiological review important."
        else:
            return f"Low confidence ({confidence:.1%}) - Significant uncertainty requires expert radiological interpretation."

    def _interpret_urgency_level(self, urgency_level: str) -> str:
        """Interpret urgency level for patients"""
        urgency_interpretations = {
            "emergency": "Emergency - Immediate medical attention required within minutes to hours",
            "urgent": "Urgent - Medical evaluation needed within 24-48 hours", 
            "routine": "Routine - Follow-up as clinically indicated, typically within days to weeks",
            "follow-up": "Follow-up - Scheduled monitoring or additional evaluation recommended"
        }
        return urgency_interpretations.get(urgency_level.lower(), f"Medical evaluation recommended based on {urgency_level} classification")

    async def _get_clinical_significance(self, finding: str, urgency_level: str) -> str:
        """Get clinical significance of the finding"""
        
        significance_map = {
            "pneumonia": "Requires prompt antibiotic treatment and respiratory monitoring",
            "pneumothorax": "May require emergency chest tube placement depending on severity",
            "pleural effusion": "May need thoracentesis for diagnosis and symptom relief",
            "cardiomegaly": "Requires cardiac evaluation and possible echocardiography",
            "pulmonary nodule": "Needs follow-up imaging per established guidelines",
            "mass": "Requires urgent multidisciplinary evaluation and possible biopsy"
        }
        
        finding_lower = finding.lower()
        for condition, significance in significance_map.items():
            if condition in finding_lower:
                return significance
        
        return f"Clinical significance depends on patient symptoms and history - {urgency_level.lower()} priority evaluation recommended"


class TavilyService(TavilyService):
    """Extended Tavily service with radiology support"""
    
    async def fetch_radiology_resources(self, condition: str, scan_type: str) -> Dict[str, Any]:
        """Fetch radiology-specific medical resources"""
        
        if not self.api_key or self.api_key == "your_tavily_api_key_here":
            logger.warning("Tavily API key not configured properly")
            return self._get_fallback_radiology_resources(condition, scan_type)
        
        try:
            logger.info(f"Fetching radiology resources for {condition} on {scan_type}")
            
            # Fetch medical articles with radiology focus
            articles = await self._fetch_radiology_articles(condition, scan_type)
            
            logger.info(f"Tavily radiology API call completed: {len(articles)} articles")
            return {
                "reference_images": [],  # Skip images for faster loading
                "medical_articles": articles,
                "educational_resources": self._get_radiology_educational_resources(condition, scan_type),
                "fetched_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching radiology resources: {str(e)}")
            return self._get_fallback_radiology_resources(condition, scan_type)

    async def _fetch_radiology_articles(self, condition: str, scan_type: str) -> List[Dict[str, Any]]:
        """Fetch radiology-specific medical articles"""
        
        try:
            # Optimized query for radiology resources
            query = f"{condition} {scan_type} radiology imaging diagnosis treatment"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": query,
                    "search_depth": "basic",
                    "include_images": False,
                    "max_results": 5,
                    "include_domains": [
                        "radiologyinfo.org",
                        "acr.org",
                        "mayoclinic.org",
                        "medlineplus.gov",
                        "healthline.com"
                    ]
                }
                
                async with session.post(
                    f"{self.base_url}/search",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for result in data.get("results", [])[:4]:
                            articles.append({
                                "title": result.get("title", f"Radiology Information: {condition}"),
                                "url": result.get("url"),
                                "source": result.get("source", "Medical Source"),
                                "snippet": result.get("content", "")[:200] + "..." if result.get("content") else f"Radiology information about {condition}",
                                "published_date": result.get("published_date"),
                                "relevance_score": result.get("score", 0.8),
                                "content_type": "radiology_article"
                            })
                        
                        return articles
                    else:
                        logger.warning(f"Tavily radiology API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching radiology articles: {str(e)}")
            return []

    def _get_radiology_educational_resources(self, condition: str, scan_type: str) -> List[Dict[str, Any]]:
        """Get educational resources for radiology findings"""
        
        return [
            {
                "title": f"Understanding {scan_type.replace('_', ' ').title()} Results",
                "description": f"Patient guide to interpreting {scan_type.replace('_', ' ')} findings",
                "type": "patient_education",
                "source": "Radiology Patient Education"
            },
            {
                "title": f"{condition.title()} - What You Need to Know",
                "description": f"Comprehensive information about {condition} and treatment options",
                "type": "condition_guide",
                "source": "Medical Education Database"
            },
            {
                "title": "Questions to Ask Your Doctor",
                "description": "Prepared questions for discussing your radiology results",
                "type": "consultation_prep",
                "source": "Patient Advocacy Resources"
            }
        ]

    def _get_fallback_radiology_resources(self, condition: str, scan_type: str) -> Dict[str, Any]:
        """Get fallback radiology resources"""
        
        fallback_articles = [
            {
                "title": f"Understanding {condition} on {scan_type.replace('_', ' ').title()}",
                "url": "https://www.radiologyinfo.org/",
                "source": "RadiologyInfo.org",
                "snippet": f"Comprehensive information about {condition} findings on {scan_type.replace('_', ' ')} imaging.",
                "relevance_score": 0.9,
                "content_type": "radiology_reference"
            },
            {
                "title": f"{scan_type.replace('_', ' ').title()} Imaging Guide",
                "url": "https://www.acr.org/",
                "source": "American College of Radiology",
                "snippet": f"Professional guidelines for {scan_type.replace('_', ' ')} interpretation and patient care.",
                "relevance_score": 0.85,
                "content_type": "clinical_guidelines"
            }
        ]
        
        return {
            "reference_images": [],
            "medical_articles": fallback_articles,
            "educational_resources": self._get_radiology_educational_resources(condition, scan_type),
            "fetched_at": datetime.utcnow().isoformat()
        }


class KeywordAIService(KeywordAIService):
    """Extended Keyword AI service with radiology support"""
    
    async def extract_radiology_keywords(
        self, 
        text_content: List[str],
        finding: str
    ) -> Dict[str, List[str]]:
        """Extract radiology-specific medical keywords"""
        
        # Use optimized fallback for faster response
        return self._get_fallback_radiology_keywords(text_content, finding)
    
    def _get_fallback_radiology_keywords(self, text_content: List[str], finding: str) -> Dict[str, List[str]]:
        """Generate radiology-specific keywords using local processing"""
        
        # Combine all text content
        combined_text = " ".join(text_content).lower()
        
        # Radiology-specific keyword database
        radiology_keywords = {
            "conditions": [
                "pneumonia", "pneumothorax", "pleural effusion", "cardiomegaly",
                "pulmonary nodule", "mass", "consolidation", "atelectasis",
                "infiltrate", "opacity", "lesion", "abnormality"
            ],
            "symptoms": [
                "opacity", "consolidation", "air space disease", "ground glass",
                "nodular", "mass-like", "cystic", "cavitary", "bilateral",
                "unilateral", "upper lobe", "lower lobe", "hilar", "peripheral"
            ],
            "treatments": [
                "antibiotics", "chest tube", "thoracentesis", "drainage",
                "surgery", "biopsy", "bronchoscopy", "intubation",
                "oxygen therapy", "mechanical ventilation"
            ],
            "procedures": [
                "chest x-ray", "CT scan", "MRI", "ultrasound", "fluoroscopy",
                "angiography", "biopsy", "thoracentesis", "bronchoscopy",
                "chest tube insertion", "VATS", "thoracotomy"
            ],
            "general": [
                "radiology", "imaging", "diagnostic", "pathology", "anatomy",
                "physiology", "respiratory", "cardiac", "thoracic", "pulmonary",
                "mediastinal", "pleural", "parenchymal"
            ]
        }
        
        # Extract keywords that appear in the text content
        extracted_keywords = {
            "conditions": [],
            "symptoms": [],
            "treatments": [],
            "procedures": [],
            "general": []
        }
        
        # Extract keywords by category
        for category, keywords in radiology_keywords.items():
            for keyword in keywords:
                if self._keyword_matches(keyword.lower(), combined_text):
                    if keyword not in extracted_keywords[category]:
                        extracted_keywords[category].append(keyword)
        
        # Add finding-specific keywords
        finding_keywords = self._get_finding_specific_keywords(finding.lower())
        for category, keywords in finding_keywords.items():
            extracted_keywords[category].extend(keywords)
            # Remove duplicates while preserving order
            extracted_keywords[category] = list(dict.fromkeys(extracted_keywords[category]))
        
        # Limit keywords per category
        for category in extracted_keywords:
            extracted_keywords[category] = extracted_keywords[category][:6]
        
        return {
            **extracted_keywords,
            "extracted_at": datetime.utcnow().isoformat()
        }
    
    def _get_finding_specific_keywords(self, finding: str) -> Dict[str, List[str]]:
        """Get keywords specific to the radiology finding"""
        
        finding_keywords = {
            "pneumonia": {
                "conditions": ["bacterial pneumonia", "viral pneumonia", "community acquired"],
                "symptoms": ["consolidation", "air bronchograms", "infiltrate"],
                "treatments": ["antibiotics", "supportive care", "oxygen"],
                "procedures": ["sputum culture", "blood culture", "chest CT"]
            },
            "pneumothorax": {
                "conditions": ["spontaneous pneumothorax", "tension pneumothorax"],
                "symptoms": ["lung collapse", "pleural air", "mediastinal shift"],
                "treatments": ["chest tube", "needle decompression", "surgery"],
                "procedures": ["chest tube insertion", "thoracostomy", "VATS"]
            },
            "pleural effusion": {
                "conditions": ["transudative", "exudative", "bilateral effusion"],
                "symptoms": ["blunted costophrenic angles", "fluid level"],
                "treatments": ["thoracentesis", "chest tube", "pleurodesis"],
                "procedures": ["diagnostic tap", "therapeutic drainage"]
            }
        }
        
        # Find matching keywords
        for condition, keywords in finding_keywords.items():
            if condition in finding:
                return keywords
        
        return {"conditions": [], "symptoms": [], "treatments": [], "procedures": []}
