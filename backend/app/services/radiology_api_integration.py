"""
Enhanced Radiology API Integration Service
Provides GROQ, Tavily, and Keyword AI integration specifically for radiology analysis
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import os
from groq import Groq

logger = logging.getLogger(__name__)

class RadiologyAPIIntegration:
    def __init__(self):
        self.groq_client = None
        self.tavily_api_key = None
        self.keyword_ai_key = None
        
        # Initialize API clients
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API clients with environment variables"""
        try:
            # GROQ Client
            groq_api_key = os.getenv('GROQ_API_KEY')
            if groq_api_key:
                self.groq_client = Groq(api_key=groq_api_key)
                logger.info("GROQ client initialized for radiology")
            else:
                logger.warning("GROQ_API_KEY not found")
            
            # Tavily API Key
            self.tavily_api_key = os.getenv('TAVILY_API_KEY')
            if self.tavily_api_key:
                logger.info("Tavily API key loaded for radiology")
            else:
                logger.warning("TAVILY_API_KEY not found")
            
            # Keyword AI Key
            self.keyword_ai_key = os.getenv('KEYWORD_AI_KEY')
            if self.keyword_ai_key:
                logger.info("Keyword AI key loaded for radiology")
            else:
                logger.warning("KEYWORD_AI_KEY not found")
                
        except Exception as e:
            logger.error(f"Error initializing radiology API clients: {e}")
    
    async def enhance_radiology_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance radiology analysis with GROQ, Tavily, and Keyword AI
        """
        try:
            findings = analysis_result.get('findings', [])
            urgency_level = analysis_result.get('urgency_level', 'routine')
            scan_type = analysis_result.get('scan_type', 'chest_xray')
            
            # Prepare findings summary
            primary_finding = findings[0]['condition'] if findings else "Normal study"
            findings_summary = self._prepare_findings_summary(findings)
            
            logger.info(f"Enhancing radiology analysis for: {primary_finding}")
            
            # Run API calls concurrently
            tasks = []
            
            # GROQ: Generate AI insights
            if self.groq_client:
                tasks.append(self._generate_groq_insights(primary_finding, findings_summary, urgency_level, scan_type))
            
            # Tavily: Fetch medical resources
            if self.tavily_api_key:
                tasks.append(self._fetch_tavily_resources(primary_finding, scan_type))
            
            # Keyword AI: Extract keywords
            if self.keyword_ai_key:
                tasks.append(self._extract_keywords(findings_summary, urgency_level))
            
            # Execute all tasks with timeout
            if tasks:
                try:
                    results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=10.0  # 10 second timeout
                    )
                    
                    # Process results
                    enhanced_result = analysis_result.copy()
                    
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(f"Radiology API task {i} failed: {result}")
                            continue
                        
                        if i == 0 and result:  # GROQ insights
                            enhanced_result['ai_explanation'] = result
                        elif i == 1 and result:  # Tavily resources
                            enhanced_result['medical_references'] = result
                        elif i == 2 and result:  # Keywords
                            enhanced_result['medical_keywords'] = result
                    
                    logger.info("Radiology analysis enhanced successfully")
                    return enhanced_result
                    
                except asyncio.TimeoutError:
                    logger.warning("Radiology API enhancement timed out")
                    return analysis_result
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error enhancing radiology analysis: {e}")
            return analysis_result
    
    async def _generate_groq_insights(self, primary_finding: str, findings_summary: str, urgency_level: str, scan_type: str) -> Optional[Dict[str, Any]]:
        """Generate AI insights using GROQ"""
        try:
            prompt = f"""
            As a radiologist AI assistant, provide a comprehensive explanation of these {scan_type.replace('_', ' ')} findings:
            
            Primary Finding: {primary_finding}
            Complete Findings: {findings_summary}
            Urgency Level: {urgency_level}
            
            Please provide:
            1. SUMMARY: A clear, patient-friendly explanation of what was found (2-3 sentences)
            2. EXPLANATION: Detailed explanation of the condition and what it means (3-4 sentences)
            3. CLINICAL_SIGNIFICANCE: What this means for the patient's health (2-3 sentences)
            
            Format your response as:
            SUMMARY: [your summary here]
            EXPLANATION: [your explanation here]  
            CLINICAL_SIGNIFICANCE: [clinical significance here]
            
            Keep language clear and professional. Emphasize the importance of discussing results with healthcare providers.
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                max_tokens=400,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the structured response
            summary = ""
            explanation = ""
            clinical_significance = ""
            
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('SUMMARY:'):
                    current_section = 'summary'
                    summary = line.replace('SUMMARY:', '').strip()
                elif line.startswith('EXPLANATION:'):
                    current_section = 'explanation'
                    explanation = line.replace('EXPLANATION:', '').strip()
                elif line.startswith('CLINICAL_SIGNIFICANCE:'):
                    current_section = 'clinical_significance'
                    clinical_significance = line.replace('CLINICAL_SIGNIFICANCE:', '').strip()
                elif current_section and line:
                    if current_section == 'summary':
                        summary += ' ' + line
                    elif current_section == 'explanation':
                        explanation += ' ' + line
                    elif current_section == 'clinical_significance':
                        clinical_significance += ' ' + line
            
            return {
                "summary": summary or content[:200] + "..." if len(content) > 200 else content,
                "explanation": explanation,
                "clinical_significance": clinical_significance,
                "confidence_interpretation": self._interpret_confidence_level(urgency_level),
                "urgency_interpretation": self._interpret_urgency_level(urgency_level),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating GROQ radiology insights: {e}")
            return None
    
    async def _fetch_tavily_resources(self, primary_finding: str, scan_type: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch medical resources using Tavily"""
        try:
            # Construct search query
            query = f"{primary_finding} {scan_type.replace('_', ' ')} radiology medical information"
            
            url = "https://api.tavily.com/search"
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": 4,
                "include_domains": [
                    "radiologyinfo.org",
                    "mayoclinic.org", 
                    "nih.gov",
                    "medlineplus.gov",
                    "acr.org",
                    "lung.org",
                    "heart.org"
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        articles = []
                        for result in data.get('results', []):
                            articles.append({
                                "title": result.get('title', ''),
                                "url": result.get('url', ''),
                                "snippet": result.get('content', '')[:300] + "..." if len(result.get('content', '')) > 300 else result.get('content', ''),
                                "source": self._extract_domain(result.get('url', '')),
                                "relevance_score": 0.9  # High relevance for Tavily results
                            })
                        
                        return articles
                    else:
                        logger.error(f"Tavily API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching Tavily radiology resources: {e}")
            return None
    
    async def _extract_keywords(self, findings_summary: str, urgency_level: str) -> Optional[Dict[str, List[str]]]:
        """Extract medical keywords using Keyword AI"""
        try:
            text_content = f"""
            Radiology findings: {findings_summary}
            Urgency level: {urgency_level}
            Medical imaging analysis results
            """
            
            url = "https://api.keywordai.co/api/extract"
            headers = {
                "Authorization": f"Bearer {self.keyword_ai_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text_content,
                "domain": "radiology",
                "max_keywords": 12,
                "min_score": 0.4
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        keywords = [kw.get('keyword', '') for kw in data.get('keywords', [])]
                        
                        # Categorize keywords
                        categorized = self._categorize_radiology_keywords(keywords, findings_summary)
                        return categorized
                    else:
                        logger.error(f"Keyword AI API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error extracting radiology keywords: {e}")
            return None
    
    def _prepare_findings_summary(self, findings: List[Dict]) -> str:
        """Prepare a summary of findings for API calls"""
        if not findings:
            return "Normal study with no significant abnormalities"
        
        summary_parts = []
        for finding in findings:
            condition = finding.get('condition', '')
            confidence = finding.get('confidence', 0)
            description = finding.get('description', '')
            
            if confidence > 0.1:  # Only include significant findings
                summary_parts.append(f"{condition} ({confidence:.0%}): {description}")
        
        return "; ".join(summary_parts) if summary_parts else "Normal findings"
    
    def _categorize_radiology_keywords(self, keywords: List[str], findings_summary: str) -> Dict[str, List[str]]:
        """Categorize radiology keywords"""
        categories = {
            "conditions": [],
            "symptoms": [],
            "treatments": [],
            "procedures": [],
            "general": []
        }
        
        # Define keyword categories
        condition_terms = ['pneumonia', 'cardiomegaly', 'pneumothorax', 'effusion', 'nodule', 'consolidation', 'atelectasis']
        symptom_terms = ['chest pain', 'shortness of breath', 'cough', 'fever', 'fatigue']
        treatment_terms = ['antibiotic', 'surgery', 'drainage', 'monitoring', 'therapy', 'medication']
        procedure_terms = ['chest x-ray', 'ct scan', 'mri', 'biopsy', 'thoracentesis', 'bronchoscopy']
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            if any(term in keyword_lower for term in condition_terms):
                categories["conditions"].append(keyword)
            elif any(term in keyword_lower for term in symptom_terms):
                categories["symptoms"].append(keyword)
            elif any(term in keyword_lower for term in treatment_terms):
                categories["treatments"].append(keyword)
            elif any(term in keyword_lower for term in procedure_terms):
                categories["procedures"].append(keyword)
            else:
                categories["general"].append(keyword)
        
        # Add finding-specific keywords
        findings_lower = findings_summary.lower()
        if 'pneumonia' in findings_lower:
            categories["conditions"].extend(['pneumonia', 'lung infection'])
            categories["treatments"].extend(['antibiotic therapy', 'respiratory support'])
        if 'cardiomegaly' in findings_lower:
            categories["conditions"].extend(['cardiomegaly', 'enlarged heart'])
            categories["procedures"].extend(['echocardiogram', 'cardiac evaluation'])
        
        # Remove duplicates and empty categories
        for category in categories:
            categories[category] = list(set(categories[category]))
            if not categories[category]:
                categories[category] = ['medical evaluation', 'healthcare consultation']
        
        return categories
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.replace('www.', '')
        except:
            return 'Medical Database'
    
    def _interpret_confidence_level(self, urgency_level: str) -> str:
        """Interpret confidence based on urgency level"""
        interpretations = {
            "routine": "Standard confidence level indicates typical findings that can be addressed through routine medical care.",
            "urgent": "High confidence level indicates findings that require prompt medical attention and evaluation.",
            "emergency": "Critical confidence level indicates findings that require immediate medical intervention.",
            "follow-up": "Moderate confidence level indicates findings that require specialist evaluation and monitoring."
        }
        return interpretations.get(urgency_level.lower(), "Professional medical evaluation recommended for accurate interpretation.")
    
    def _interpret_urgency_level(self, urgency_level: str) -> str:
        """Interpret urgency level for patients"""
        interpretations = {
            "routine": "Routine urgency indicates findings that can be addressed through standard medical follow-up and do not require immediate intervention.",
            "urgent": "Urgent urgency indicates findings that require prompt medical evaluation and treatment, typically within hours to days.",
            "emergency": "Emergency urgency indicates findings that may be life-threatening and require immediate medical attention and intervention.",
            "follow-up": "Follow-up urgency indicates findings that require monitoring or additional evaluation but are not immediately concerning."
        }
        return interpretations.get(urgency_level.lower(), "Professional medical evaluation will determine the appropriate urgency and timing of follow-up care.")

# Global instance
radiology_api_integration = RadiologyAPIIntegration()
