"""
Enhanced API Integration Services with Comprehensive Fallbacks
Handles GROQ, Tavily, and Keyword AI integrations with robust error handling
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

class EnhancedGroqService:
    """Enhanced GROQ service with comprehensive fallbacks"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama3-8b-8192"
        
    async def generate_medical_summary(
        self, 
        prediction: str, 
        confidence: float, 
        risk_level: str,
        analysis_type: str = "skin"
    ) -> Dict[str, Any]:
        """Generate comprehensive medical summary with fallbacks"""
        
        try:
            if self.api_key and self.api_key != "your_groq_api_key_here":
                # Try API call first
                api_result = await self._call_groq_api(prediction, confidence, risk_level, analysis_type)
                if api_result:
                    return api_result
            
            # Fallback to enhanced local generation
            return self._generate_enhanced_fallback_summary(prediction, confidence, risk_level, analysis_type)
            
        except Exception as e:
            logger.error(f"Error in GROQ service: {str(e)}")
            return self._generate_enhanced_fallback_summary(prediction, confidence, risk_level, analysis_type)
    
    async def _call_groq_api(self, prediction: str, confidence: float, risk_level: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Call GROQ API with proper error handling"""
        
        try:
            prompt = self._build_comprehensive_prompt(prediction, confidence, risk_level, analysis_type)
            
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
                            "content": "You are a medical AI assistant providing clear, accurate explanations of diagnostic results. Always include appropriate medical disclaimers and be precise with medical terminology."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 600,
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
                        summary = data["choices"][0]["message"]["content"]
                        
                        # Generate detailed explanation
                        explanation = await self._generate_condition_explanation(prediction)
                        
                        return {
                            "summary": summary,
                            "explanation": explanation,
                            "confidence_interpretation": self._interpret_confidence(confidence),
                            "risk_interpretation": self._interpret_risk_level(risk_level),
                            "generated_at": datetime.utcnow().isoformat(),
                            "source": "groq_api"
                        }
                    else:
                        logger.warning(f"GROQ API returned status {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"GROQ API call failed: {str(e)}")
            return None
    
    def _build_comprehensive_prompt(self, prediction: str, confidence: float, risk_level: str, analysis_type: str) -> str:
        """Build comprehensive prompt for medical summary"""
        
        return f"""
        Generate a comprehensive medical summary for the following {analysis_type} analysis results:
        
        **Analysis Results:**
        - Condition: {prediction}
        - Confidence Level: {confidence:.1%}
        - Risk Assessment: {risk_level}
        - Analysis Type: {analysis_type.title()}
        
        **Please provide:**
        1. A clear, professional summary explaining what this diagnosis means
        2. The clinical significance of the confidence level
        3. What the risk level indicates for the patient
        4. Appropriate next steps and recommendations
        5. Important considerations for this condition
        
        **Requirements:**
        - Use clear, patient-friendly language while maintaining medical accuracy
        - Include appropriate medical disclaimers
        - Explain the urgency level based on the risk assessment
        - Provide context about the condition's typical presentation and prognosis
        - Keep the tone professional but reassuring where appropriate
        
        **Important:** Always emphasize that this is AI-assisted analysis and professional medical evaluation is required for diagnosis and treatment decisions.
        """
    
    async def _generate_condition_explanation(self, condition: str) -> str:
        """Generate detailed condition explanation"""
        
        if self.api_key and self.api_key != "your_groq_api_key_here":
            try:
                prompt = f"""
                Provide a detailed, patient-friendly explanation of the medical condition: {condition}
                
                Include:
                1. What this condition is (definition and characteristics)
                2. How common it is
                3. Typical symptoms and appearance
                4. Common causes or risk factors
                5. General prognosis and treatment outlook
                6. Why professional medical evaluation is important
                
                Keep it informative but not alarming. Use clear, accessible language.
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
                            
            except Exception as e:
                logger.error(f"Error generating condition explanation: {str(e)}")
        
        # Fallback to local explanation
        return self._get_enhanced_condition_explanation(condition)
    
    def _generate_enhanced_fallback_summary(self, prediction: str, confidence: float, risk_level: str, analysis_type: str) -> Dict[str, Any]:
        """Generate enhanced fallback summary with detailed medical information"""
        
        # Enhanced summary templates
        risk_descriptions = {
            "HIGH": {
                "urgency": "requires immediate medical attention",
                "action": "Please contact a healthcare provider as soon as possible",
                "timeline": "within 24-48 hours"
            },
            "MEDIUM": {
                "urgency": "warrants professional evaluation", 
                "action": "Schedule an appointment with a dermatologist",
                "timeline": "within 1-2 weeks"
            },
            "LOW": {
                "urgency": "appears to be low risk but should be monitored",
                "action": "Continue regular monitoring and routine check-ups",
                "timeline": "at your next scheduled appointment"
            }
        }
        
        risk_info = risk_descriptions.get(risk_level.upper(), risk_descriptions["MEDIUM"])
        
        # Generate comprehensive summary
        summary = f"""
        The AI analysis has identified {prediction.lower()} with {confidence:.1%} confidence. 
        This {risk_level.lower()} risk finding {risk_info['urgency']}.
        
        **Confidence Level Interpretation:**
        A {confidence:.1%} confidence level indicates {'high' if confidence > 0.7 else 'moderate' if confidence > 0.4 else 'low'} certainty in the AI's assessment. 
        {'This suggests the features are clearly characteristic of the identified condition.' if confidence > 0.7 else 'Additional professional evaluation is recommended to confirm the diagnosis.' if confidence > 0.4 else 'The features are less definitive, requiring professional assessment for accurate diagnosis.'}
        
        **Recommended Action:**
        {risk_info['action']} {risk_info['timeline']}.
        
        **Important Medical Disclaimer:**
        This AI analysis is for informational and educational purposes only. It should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical concerns. In case of emergency, call emergency services immediately.
        """
        
        explanation = self._get_enhanced_condition_explanation(prediction)
        
        return {
            "summary": summary.strip(),
            "explanation": explanation,
            "confidence_interpretation": self._interpret_confidence(confidence),
            "risk_interpretation": self._interpret_risk_level(risk_level),
            "generated_at": datetime.utcnow().isoformat(),
            "source": "enhanced_fallback"
        }
    
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
    
    def _get_enhanced_condition_explanation(self, condition: str) -> str:
        """Enhanced condition explanations with detailed medical information"""
        
        explanations = {
            "melanoma": """
            Melanoma is a type of skin cancer that develops from melanocytes, the cells that produce melanin (skin pigment). 
            It is the most serious type of skin cancer but is highly treatable when detected early.
            
            **Key Facts:**
            • Most dangerous form of skin cancer but accounts for only about 1% of skin cancers
            • Can develop anywhere on the body, including areas not exposed to sun
            • Early detection is crucial - 5-year survival rate is over 99% when caught early
            • Often appears as a new mole or changes in existing moles
            • Risk factors include UV exposure, fair skin, family history, and multiple moles
            
            **Why Professional Evaluation Matters:**
            Only a dermatologist can definitively diagnose melanoma through clinical examination and, if necessary, biopsy. 
            Early professional evaluation and treatment significantly improve outcomes.
            """,
            
            "basal cell carcinoma": """
            Basal cell carcinoma (BCC) is the most common type of skin cancer, developing from basal cells in the skin's outer layer.
            It grows slowly and rarely spreads to other parts of the body, making it highly treatable.
            
            **Key Facts:**
            • Most common form of skin cancer (about 80% of cases)
            • Grows slowly and rarely metastasizes (spreads)
            • Usually appears on sun-exposed areas like face, neck, and arms
            • Often looks like a small, shiny bump or a flat, scaly patch
            • Caused primarily by cumulative UV exposure over time
            
            **Treatment Outlook:**
            BCC is highly curable with various treatment options including surgical removal, 
            topical medications, or other procedures. Early treatment prevents growth and potential complications.
            """,
            
            "squamous cell carcinoma": """
            Squamous cell carcinoma (SCC) is the second most common type of skin cancer, developing from squamous cells 
            in the skin's upper layers. It can be more aggressive than basal cell carcinoma but is still highly treatable when caught early.
            
            **Key Facts:**
            • Second most common skin cancer (about 20% of cases)
            • Can spread to other parts of the body if left untreated
            • Often appears as a firm, red nodule or flat lesion with a scaly surface
            • Commonly develops on sun-exposed areas
            • Risk increases with age, UV exposure, and immunosuppression
            
            **Importance of Treatment:**
            While more aggressive than BCC, SCC is still highly curable with prompt treatment. 
            Early intervention prevents potential spread and ensures the best outcomes.
            """,
            
            "actinic keratosis": """
            Actinic keratosis (AK) is a precancerous skin condition caused by sun damage. While not cancer itself, 
            it can develop into squamous cell carcinoma if left untreated.
            
            **Key Facts:**
            • Precancerous condition, not cancer itself
            • Caused by cumulative sun damage over years
            • Appears as rough, scaly patches on sun-exposed skin
            • About 5-10% may progress to squamous cell carcinoma
            • More common in fair-skinned individuals and those with significant sun exposure
            
            **Prevention and Treatment:**
            AK can be effectively treated with various methods including topical medications, 
            cryotherapy, or other procedures. Sun protection helps prevent new lesions.
            """,
            
            "seborrheic keratosis": """
            Seborrheic keratosis is a common, benign (non-cancerous) skin growth that appears as people age. 
            These growths are typically harmless but should be evaluated to rule out other conditions.
            
            **Key Facts:**
            • Benign (non-cancerous) skin growth
            • Very common, especially after age 50
            • Often appears as brown, black, or tan growths with a "stuck-on" appearance
            • Can occur anywhere on the body except palms and soles
            • Not caused by sun exposure, though may be more noticeable on sun-damaged skin
            
            **When to Seek Evaluation:**
            While generally harmless, any changing skin growth should be evaluated by a dermatologist 
            to ensure accurate diagnosis and rule out other conditions.
            """,
            
            "nevus": """
            A nevus (mole) is a common, usually benign skin growth made up of melanocytes (pigment cells). 
            Most moles are harmless, but changes in appearance should be evaluated.
            
            **Key Facts:**
            • Most moles are benign and remain stable throughout life
            • Can be present at birth (congenital) or develop later (acquired)
            • Normal moles are usually uniform in color, round or oval, and smaller than 6mm
            • Changes in size, color, shape, or texture warrant evaluation
            • People with many moles have higher risk of melanoma
            
            **Monitoring Guidelines:**
            Regular self-examination using the ABCDE criteria (Asymmetry, Border, Color, Diameter, Evolution) 
            helps identify changes that should be evaluated by a dermatologist.
            """,
            
            "dermatofibroma": """
            Dermatofibroma is a common, benign skin growth that typically appears as a small, firm bump. 
            These growths are generally harmless but can be removed if bothersome.
            
            **Key Facts:**
            • Benign (non-cancerous) skin growth
            • Often appears as a small, firm, brownish bump
            • More common in women and on the legs
            • May develop after minor skin injuries like insect bites
            • Usually painless but may be itchy or tender
            
            **Treatment Options:**
            While treatment is not necessary for medical reasons, dermatofibromas can be removed 
            if they are bothersome, frequently irritated, or for cosmetic reasons.
            """
        }
        
        condition_lower = condition.lower()
        for key, explanation in explanations.items():
            if key in condition_lower:
                return explanation.strip()
        
        # Generic fallback
        return f"""
        {condition} is a skin condition that requires professional medical evaluation for proper diagnosis and treatment recommendations.
        
        **Important Steps:**
        • Schedule an appointment with a dermatologist for proper evaluation
        • Bring any relevant medical history and current medications
        • Ask questions about treatment options and follow-up care
        • Follow professional medical advice for the best outcomes
        
        **General Information:**
        A dermatologist can provide accurate diagnosis through clinical examination and, if necessary, 
        additional tests such as dermoscopy or biopsy. Professional evaluation ensures appropriate 
        treatment and monitoring recommendations.
        """
