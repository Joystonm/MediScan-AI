"""
Enhanced API Services for MediScan-AI
Integrates GROQ, Tavily, and Keyword AI for comprehensive medical analysis
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
import aiohttp
import json
from groq import Groq
from tavily import TavilyClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAPIServices:
    """
    Enhanced API services for medical analysis enrichment
    """
    
    def __init__(self):
        self.groq_client = None
        self.tavily_client = None
        self.keyword_ai_key = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API clients with error handling"""
        try:
            # Initialize GROQ client
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key:
                self.groq_client = Groq(api_key=groq_key)
                logger.info("GROQ client initialized successfully")
            else:
                logger.warning("GROQ_API_KEY not found")
            
            # Initialize Tavily client
            tavily_key = os.getenv("TAVILY_API_KEY")
            if tavily_key:
                self.tavily_client = TavilyClient(api_key=tavily_key)
                logger.info("Tavily client initialized successfully")
            else:
                logger.warning("TAVILY_API_KEY not found")
            
            # Store Keyword AI key
            self.keyword_ai_key = os.getenv("KEYWORD_AI_KEY")
            if self.keyword_ai_key:
                logger.info("Keyword AI key loaded successfully")
            else:
                logger.warning("KEYWORD_AI_KEY not found")
                
        except Exception as e:
            logger.error(f"Error initializing API clients: {e}")
    
    async def enhance_skin_analysis(self, analysis_result: Dict[str, Any], image_filename: str) -> Dict[str, Any]:
        """
        Enhance skin cancer analysis with GROQ, Tavily, and Keyword AI
        """
        try:
            top_prediction = analysis_result.get('top_prediction', 'Unknown condition')
            confidence = analysis_result.get('confidence', 0.0)
            risk_level = analysis_result.get('risk_level', 'unknown')
            
            # Run all API calls concurrently for better performance
            tasks = []
            
            # GROQ: Generate natural language explanation
            if self.groq_client:
                tasks.append(self._generate_skin_explanation(top_prediction, confidence, risk_level))
            
            # Tavily: Fetch medical references
            if self.tavily_client:
                tasks.append(self._fetch_skin_references(top_prediction))
            
            # Keyword AI: Extract medical terms
            if self.keyword_ai_key:
                tasks.append(self._extract_skin_keywords(analysis_result))
            
            # Execute all tasks concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                enhanced_result = analysis_result.copy()
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"API task {i} failed: {result}")
                        continue
                    
                    if i == 0 and result:  # GROQ explanation
                        enhanced_result['ai_explanation'] = result
                    elif i == 1 and result:  # Tavily references
                        enhanced_result['medical_references'] = result
                    elif i == 2 and result:  # Keyword AI terms
                        enhanced_result['medical_keywords'] = result
                
                return enhanced_result
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error enhancing skin analysis: {e}")
            return analysis_result
    
    async def enhance_radiology_analysis(self, analysis_result: Dict[str, Any], scan_type: str) -> Dict[str, Any]:
        """
        Enhance radiology analysis with GROQ, Tavily, and Keyword AI
        """
        try:
            findings = analysis_result.get('findings', [])
            urgency_level = analysis_result.get('urgency_level', 'routine')
            
            # Prepare findings summary for APIs
            findings_summary = self._prepare_radiology_summary(findings, scan_type)
            
            # Run all API calls concurrently
            tasks = []
            
            # GROQ: Generate natural language explanation
            if self.groq_client:
                tasks.append(self._generate_radiology_explanation(findings_summary, urgency_level, scan_type))
            
            # Tavily: Fetch medical insights
            if self.tavily_client:
                tasks.append(self._fetch_radiology_references(findings_summary, scan_type))
            
            # Keyword AI: Extract critical findings
            if self.keyword_ai_key:
                tasks.append(self._extract_radiology_keywords(analysis_result))
            
            # Execute all tasks concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                enhanced_result = analysis_result.copy()
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"API task {i} failed: {result}")
                        continue
                    
                    if i == 0 and result:  # GROQ explanation
                        enhanced_result['ai_explanation'] = result
                    elif i == 1 and result:  # Tavily references
                        enhanced_result['medical_references'] = result
                    elif i == 2 and result:  # Keyword AI terms
                        enhanced_result['medical_keywords'] = result
                
                return enhanced_result
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error enhancing radiology analysis: {e}")
            return analysis_result
    
    async def _generate_skin_explanation(self, condition: str, confidence: float, risk_level: str) -> Optional[Dict[str, str]]:
        """Generate natural language explanation using GROQ"""
        try:
            prompt = f"""
            As a medical AI assistant, explain the skin condition "{condition}" in simple, patient-friendly language.
            
            Context:
            - Detected condition: {condition}
            - Confidence level: {confidence:.1%}
            - Risk level: {risk_level}
            
            Please provide:
            1. A brief explanation of what this condition is
            2. What it typically looks like
            3. Whether it's concerning based on the risk level
            4. General advice (not specific medical advice)
            
            Keep the explanation clear, reassuring where appropriate, and emphasize the importance of professional medical consultation.
            Limit response to 150 words.
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                max_tokens=200,
                temperature=0.3
            )
            
            explanation = response.choices[0].message.content.strip()
            
            return {
                "summary": explanation,
                "confidence_interpretation": self._interpret_confidence(confidence),
                "risk_interpretation": self._interpret_risk_level(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Error generating GROQ explanation: {e}")
            return None
    
    async def _generate_radiology_explanation(self, findings_summary: str, urgency_level: str, scan_type: str) -> Optional[Dict[str, str]]:
        """Generate natural language explanation for radiology findings using GROQ"""
        try:
            prompt = f"""
            As a medical AI assistant, explain these {scan_type} findings in patient-friendly language:
            
            Findings: {findings_summary}
            Urgency level: {urgency_level}
            
            Please provide:
            1. A clear explanation of what was found
            2. What these findings typically mean
            3. The significance based on urgency level
            4. General next steps (emphasizing professional consultation)
            
            Keep the explanation clear, balanced, and emphasize the importance of discussing results with a healthcare provider.
            Limit response to 150 words.
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                max_tokens=200,
                temperature=0.3
            )
            
            explanation = response.choices[0].message.content.strip()
            
            return {
                "summary": explanation,
                "urgency_interpretation": self._interpret_urgency_level(urgency_level),
                "scan_type_info": self._get_scan_type_info(scan_type)
            }
            
        except Exception as e:
            logger.error(f"Error generating radiology GROQ explanation: {e}")
            return None
    
    async def _fetch_skin_references(self, condition: str) -> Optional[List[Dict[str, str]]]:
        """Fetch trusted medical references using Tavily"""
        try:
            query = f"{condition} dermatology medical information trusted sources"
            
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=3,
                include_domains=["mayoclinic.org", "webmd.com", "aad.org", "cancer.org", "nih.gov", "medlineplus.gov"]
            )
            
            references = []
            for result in response.get('results', []):
                references.append({
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "snippet": result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', ''),
                    "source": self._extract_domain(result.get('url', ''))
                })
            
            return references
            
        except Exception as e:
            logger.error(f"Error fetching Tavily references: {e}")
            return None
    
    async def _fetch_radiology_references(self, findings_summary: str, scan_type: str) -> Optional[List[Dict[str, str]]]:
        """Fetch medical insights for radiology findings using Tavily"""
        try:
            query = f"{scan_type} {findings_summary} radiology medical information"
            
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=3,
                include_domains=["radiologyinfo.org", "mayoclinic.org", "nih.gov", "medlineplus.gov", "acr.org"]
            )
            
            references = []
            for result in response.get('results', []):
                references.append({
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "snippet": result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', ''),
                    "source": self._extract_domain(result.get('url', ''))
                })
            
            return references
            
        except Exception as e:
            logger.error(f"Error fetching radiology Tavily references: {e}")
            return None
    
    async def _extract_skin_keywords(self, analysis_result: Dict[str, Any]) -> Optional[List[str]]:
        """Extract medical keywords using Keyword AI"""
        try:
            # Prepare text for keyword extraction
            text_content = f"""
            Skin condition analysis: {analysis_result.get('top_prediction', '')}
            Risk level: {analysis_result.get('risk_level', '')}
            Recommendations: {' '.join(analysis_result.get('recommendations', []))}
            """
            
            keywords = await self._call_keyword_ai(text_content, "dermatology")
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting skin keywords: {e}")
            return None
    
    async def _extract_radiology_keywords(self, analysis_result: Dict[str, Any]) -> Optional[List[str]]:
        """Extract critical findings keywords using Keyword AI"""
        try:
            # Prepare text for keyword extraction
            findings_text = ""
            for finding in analysis_result.get('findings', []):
                findings_text += f"{finding.get('condition', '')} {finding.get('description', '')} "
            
            text_content = f"""
            Radiology findings: {findings_text}
            Urgency level: {analysis_result.get('urgency_level', '')}
            Recommendations: {' '.join(analysis_result.get('recommendations', []))}
            """
            
            keywords = await self._call_keyword_ai(text_content, "radiology")
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting radiology keywords: {e}")
            return None
    
    async def _call_keyword_ai(self, text: str, domain: str) -> Optional[List[str]]:
        """Call Keyword AI API for keyword extraction"""
        try:
            url = "https://api.keywordai.co/api/extract"
            headers = {
                "Authorization": f"Bearer {self.keyword_ai_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "domain": domain,
                "max_keywords": 8,
                "min_score": 0.5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [kw.get('keyword', '') for kw in data.get('keywords', [])]
                    else:
                        logger.error(f"Keyword AI API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error calling Keyword AI: {e}")
            return None
    
    def _prepare_radiology_summary(self, findings: List[Dict], scan_type: str) -> str:
        """Prepare a summary of radiology findings"""
        if not findings:
            return f"Normal {scan_type} with no significant abnormalities"
        
        summary_parts = []
        for finding in findings:
            condition = finding.get('condition', '')
            confidence = finding.get('confidence', 0)
            if condition and condition.lower() not in ['normal', 'clear', 'no abnormalities']:
                summary_parts.append(f"{condition} (confidence: {confidence:.1%})")
        
        return ", ".join(summary_parts) if summary_parts else f"Normal {scan_type}"
    
    def _interpret_confidence(self, confidence: float) -> str:
        """Interpret confidence level for patients"""
        if confidence >= 0.8:
            return "High confidence in the analysis"
        elif confidence >= 0.6:
            return "Good confidence in the analysis"
        elif confidence >= 0.4:
            return "Moderate confidence in the analysis"
        else:
            return "Lower confidence - additional evaluation recommended"
    
    def _interpret_risk_level(self, risk_level: str) -> str:
        """Interpret risk level for patients"""
        interpretations = {
            "low": "Generally not concerning, but routine monitoring recommended",
            "medium": "May require attention - consult with a healthcare provider",
            "high": "Requires prompt medical evaluation and consultation"
        }
        return interpretations.get(risk_level.lower(), "Consult with a healthcare provider for interpretation")
    
    def _interpret_urgency_level(self, urgency_level: str) -> str:
        """Interpret urgency level for patients"""
        interpretations = {
            "routine": "No immediate action required - routine follow-up appropriate",
            "urgent": "Requires timely medical attention within 24-48 hours",
            "emergency": "Requires immediate medical attention"
        }
        return interpretations.get(urgency_level.lower(), "Consult with a healthcare provider")
    
    def _get_scan_type_info(self, scan_type: str) -> str:
        """Get information about the scan type"""
        info = {
            "chest_xray": "Chest X-rays help evaluate the lungs, heart, and chest wall",
            "ct_scan": "CT scans provide detailed cross-sectional images of internal structures",
            "mri": "MRI scans use magnetic fields to create detailed images of soft tissues"
        }
        return info.get(scan_type, "Medical imaging helps evaluate internal structures")
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return "Unknown source"

# Global instance
enhanced_api_services = EnhancedAPIServices()
