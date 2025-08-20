"""
Enhanced Tavily Service with Comprehensive Medical Resources and Fallbacks
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)

class EnhancedTavilyService:
    """Enhanced Tavily service with comprehensive medical resources and fallbacks"""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com"
        
    async def fetch_medical_resources(
        self, 
        condition: str, 
        analysis_type: str = "skin"
    ) -> Dict[str, Any]:
        """Fetch comprehensive medical resources with robust fallbacks"""
        
        try:
            if self.api_key and self.api_key != "your_tavily_api_key_here":
                # Try API call first
                api_result = await self._call_tavily_api(condition, analysis_type)
                if api_result and (api_result.get("reference_images") or api_result.get("medical_articles")):
                    return api_result
            
            # Fallback to comprehensive local resources
            return self._generate_comprehensive_fallback_resources(condition, analysis_type)
            
        except Exception as e:
            logger.error(f"Error in Tavily service: {str(e)}")
            return self._generate_comprehensive_fallback_resources(condition, analysis_type)
    
    async def _call_tavily_api(self, condition: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Call Tavily API with proper error handling"""
        
        try:
            # Fetch both images and articles concurrently
            images_task = self._fetch_reference_images(condition, analysis_type)
            articles_task = self._fetch_medical_articles(condition, analysis_type)
            
            images, articles = await asyncio.gather(images_task, articles_task, return_exceptions=True)
            
            # Handle exceptions
            if isinstance(images, Exception):
                logger.error(f"Error fetching images: {images}")
                images = []
            
            if isinstance(articles, Exception):
                logger.error(f"Error fetching articles: {articles}")
                articles = []
            
            return {
                "reference_images": images or [],
                "medical_articles": articles or [],
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "tavily_api"
            }
            
        except Exception as e:
            logger.error(f"Tavily API call failed: {str(e)}")
            return None
    
    async def _fetch_reference_images(self, condition: str, analysis_type: str) -> List[Dict[str, Any]]:
        """Fetch reference medical images"""
        
        try:
            query = f"{condition} {analysis_type} medical images dermatology clinical examples"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": query,
                    "search_depth": "basic",
                    "include_images": True,
                    "max_results": 8,
                    "include_domains": [
                        "dermnetnz.org",
                        "aad.org", 
                        "mayoclinic.org",
                        "webmd.com",
                        "healthline.com",
                        "medlineplus.gov",
                        "skincancer.org"
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
                        
                        for result in data.get("images", [])[:4]:  # Limit to 4 images
                            images.append({
                                "url": result.get("url"),
                                "title": result.get("title", f"Clinical example of {condition}"),
                                "source": result.get("source", "Medical database"),
                                "description": result.get("description", f"Reference image showing {condition}"),
                                "alt_text": f"Medical reference image of {condition}"
                            })
                        
                        return images
                    else:
                        logger.warning(f"Tavily images API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching reference images: {str(e)}")
            return []
    
    async def _fetch_medical_articles(self, condition: str, analysis_type: str) -> List[Dict[str, Any]]:
        """Fetch relevant medical articles and research"""
        
        try:
            query = f"{condition} {analysis_type} treatment diagnosis medical research dermatology"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": query,
                    "search_depth": "advanced",
                    "include_images": False,
                    "max_results": 10,
                    "include_domains": [
                        "pubmed.ncbi.nlm.nih.gov",
                        "dermnetnz.org",
                        "aad.org",
                        "mayoclinic.org",
                        "cancer.org",
                        "skincancer.org",
                        "nejm.org",
                        "jamanetwork.com",
                        "medlineplus.gov",
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
                        articles = []
                        
                        for result in data.get("results", [])[:6]:  # Limit to 6 articles
                            articles.append({
                                "title": result.get("title"),
                                "url": result.get("url"),
                                "source": result.get("source", "Medical journal"),
                                "snippet": result.get("content", "")[:250] + "..." if result.get("content") else f"Medical information about {condition}",
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
    
    def _generate_comprehensive_fallback_resources(self, condition: str, analysis_type: str) -> Dict[str, Any]:
        """Generate comprehensive fallback medical resources"""
        
        # Comprehensive medical articles database
        fallback_articles = self._get_condition_specific_articles(condition)
        
        # Add general dermatology resources
        general_articles = [
            {
                "title": "Skin Cancer Prevention and Early Detection",
                "url": "https://www.cancer.org/cancer/skin-cancer/prevention-and-early-detection.html",
                "source": "American Cancer Society",
                "snippet": "Learn about skin cancer prevention, risk factors, and the importance of early detection through regular skin examinations.",
                "published_date": None,
                "relevance_score": 0.9,
                "content_type": "educational_resource"
            },
            {
                "title": "Dermatology Guidelines and Best Practices",
                "url": "https://www.aad.org/public/diseases/skin-cancer",
                "source": "American Academy of Dermatology",
                "snippet": "Comprehensive guidelines for skin cancer diagnosis, treatment, and patient care from leading dermatology experts.",
                "published_date": None,
                "relevance_score": 0.85,
                "content_type": "clinical_guidelines"
            },
            {
                "title": "Understanding Your Skin: A Patient's Guide",
                "url": "https://www.mayoclinic.org/diseases-conditions/skin-cancer/symptoms-causes/syc-20377605",
                "source": "Mayo Clinic",
                "snippet": "Patient-friendly information about skin health, common conditions, and when to seek medical attention.",
                "published_date": None,
                "relevance_score": 0.8,
                "content_type": "patient_education"
            }
        ]
        
        # Combine condition-specific and general articles
        all_articles = fallback_articles + general_articles
        
        # Generate reference images (placeholder data for educational purposes)
        reference_images = self._get_educational_image_references(condition)
        
        return {
            "reference_images": reference_images,
            "medical_articles": all_articles,
            "fetched_at": datetime.utcnow().isoformat(),
            "source": "comprehensive_fallback",
            "note": "These resources are provided for educational purposes. Always consult healthcare professionals for medical advice."
        }
    
    def _get_condition_specific_articles(self, condition: str) -> List[Dict[str, Any]]:
        """Get condition-specific medical articles"""
        
        condition_articles = {
            "melanoma": [
                {
                    "title": "Melanoma: Diagnosis, Treatment, and Prognosis",
                    "url": "https://www.cancer.org/cancer/melanoma-skin-cancer.html",
                    "source": "American Cancer Society",
                    "snippet": "Comprehensive guide to melanoma including risk factors, symptoms, diagnosis methods, staging, and treatment options.",
                    "published_date": "2024",
                    "relevance_score": 0.95,
                    "content_type": "medical_guide"
                },
                {
                    "title": "Early Detection of Melanoma: ABCDE Guidelines",
                    "url": "https://www.skincancer.org/skin-cancer-information/melanoma/",
                    "source": "Skin Cancer Foundation",
                    "snippet": "Learn the ABCDE criteria for melanoma detection and the importance of regular skin self-examinations.",
                    "published_date": "2024",
                    "relevance_score": 0.9,
                    "content_type": "screening_guidelines"
                }
            ],
            
            "basal cell carcinoma": [
                {
                    "title": "Basal Cell Carcinoma: The Most Common Skin Cancer",
                    "url": "https://www.skincancer.org/skin-cancer-information/basal-cell-carcinoma/",
                    "source": "Skin Cancer Foundation",
                    "snippet": "Understanding basal cell carcinoma, its appearance, risk factors, and highly effective treatment options.",
                    "published_date": "2024",
                    "relevance_score": 0.95,
                    "content_type": "medical_guide"
                },
                {
                    "title": "Treatment Options for Basal Cell Carcinoma",
                    "url": "https://www.aad.org/public/diseases/skin-cancer/basal-cell-carcinoma",
                    "source": "American Academy of Dermatology",
                    "snippet": "Comprehensive overview of BCC treatment methods including surgery, topical treatments, and radiation therapy.",
                    "published_date": "2024",
                    "relevance_score": 0.9,
                    "content_type": "treatment_guide"
                }
            ],
            
            "squamous cell carcinoma": [
                {
                    "title": "Squamous Cell Carcinoma: Diagnosis and Treatment",
                    "url": "https://www.cancer.org/cancer/skin-cancer/squamous-cell-carcinoma.html",
                    "source": "American Cancer Society",
                    "snippet": "Detailed information about squamous cell carcinoma including symptoms, staging, and treatment approaches.",
                    "published_date": "2024",
                    "relevance_score": 0.95,
                    "content_type": "medical_guide"
                }
            ],
            
            "actinic keratosis": [
                {
                    "title": "Actinic Keratosis: Precancerous Skin Lesions",
                    "url": "https://www.aad.org/public/diseases/scaly-skin/actinic-keratosis",
                    "source": "American Academy of Dermatology",
                    "snippet": "Understanding actinic keratosis as a precancerous condition and available treatment options.",
                    "published_date": "2024",
                    "relevance_score": 0.9,
                    "content_type": "medical_guide"
                }
            ],
            
            "seborrheic keratosis": [
                {
                    "title": "Seborrheic Keratosis: Benign Skin Growths",
                    "url": "https://www.mayoclinic.org/diseases-conditions/seborrheic-keratosis/symptoms-causes/syc-20353878",
                    "source": "Mayo Clinic",
                    "snippet": "Information about seborrheic keratosis, including appearance, causes, and when treatment may be needed.",
                    "published_date": "2024",
                    "relevance_score": 0.85,
                    "content_type": "medical_guide"
                }
            ]
        }
        
        condition_lower = condition.lower()
        for key, articles in condition_articles.items():
            if key in condition_lower:
                return articles
        
        # Generic fallback articles
        return [
            {
                "title": f"Understanding {condition}: Medical Overview",
                "url": "https://www.dermnetnz.org/",
                "source": "DermNet NZ",
                "snippet": f"Comprehensive medical information about {condition} including symptoms, diagnosis, and treatment options.",
                "published_date": "2024",
                "relevance_score": 0.8,
                "content_type": "medical_reference"
            }
        ]
    
    def _get_educational_image_references(self, condition: str) -> List[Dict[str, Any]]:
        """Get educational image references (placeholder for actual medical images)"""
        
        # Note: In a real implementation, these would be actual medical reference images
        # For now, we provide educational placeholders
        
        base_images = [
            {
                "url": "https://example.com/medical-reference-placeholder.jpg",
                "title": f"Clinical Example of {condition}",
                "source": "Medical Education Database",
                "description": f"Educational reference showing typical presentation of {condition}",
                "alt_text": f"Medical reference image of {condition}",
                "note": "Placeholder for educational reference image"
            },
            {
                "url": "https://example.com/dermoscopy-placeholder.jpg", 
                "title": f"Dermoscopic View of {condition}",
                "source": "Dermatology Atlas",
                "description": f"Dermoscopic features commonly seen in {condition}",
                "alt_text": f"Dermoscopic image of {condition}",
                "note": "Placeholder for dermoscopic reference image"
            }
        ]
        
        return base_images
