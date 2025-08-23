"""
Enhanced Triage Chat Service
Provides structured medical assessments with doctor-like questioning
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .api_integrations import APIIntegrationService
from .medical_assessment_engine import MedicalAssessmentEngine

logger = logging.getLogger(__name__)

class TriageChatService:
    """Service for structured medical triage conversations"""
    
    def __init__(self):
        self.api_service = APIIntegrationService()
        self.assessment_engine = MedicalAssessmentEngine()
        self.conversation_context = {}  # Store conversation history by session
        
    async def process_chat_message(
        self,
        message: str,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and provide structured medical assessment
        """
        
        logger.info(f"Processing triage chat message for session: {session_id}")
        
        try:
            # Initialize session context if new
            if session_id not in self.conversation_context:
                self.conversation_context[session_id] = {
                    "messages": [],
                    "assessment_data": {},
                    "created_at": datetime.utcnow().isoformat()
                }
            
            # Add user message to context
            self.conversation_context[session_id]["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Conduct structured medical assessment
            try:
                response, questions, urgency_level, assessment_data = self.assessment_engine.conduct_assessment(
                    message=message,
                    conversation_history=self.conversation_context[session_id]["messages"],
                    session_context=self.conversation_context[session_id]
                )
            except Exception as e:
                logger.error(f"Assessment engine failed: {e}")
                # Fallback to helpful error response
                return self._generate_fallback_assessment(message, session_id)
            
            # Update session context
            self.conversation_context[session_id]["assessment_data"] = assessment_data
            
            # Extract medical keywords
            try:
                keywords_result = await self._extract_medical_keywords(message)
                medical_keywords = list(set(
                    keywords_result.get("conditions", []) + 
                    keywords_result.get("symptoms", []) + 
                    keywords_result.get("treatments", [])
                ))
            except Exception as e:
                logger.warning(f"Keyword extraction failed: {e}")
                medical_keywords = []
            
            # Fetch medical resources
            try:
                medical_resources = await self._fetch_relevant_resources(
                    [assessment_data["primary_symptom"]], 
                    keywords_result.get("conditions", []) if 'keywords_result' in locals() else []
                )
            except Exception as e:
                logger.warning(f"Resource fetching failed: {e}")
                medical_resources = []
            
            # Format structured response with ONE question at a time
            if questions:
                # Take only the first question and ask it naturally
                next_question = questions[0]
                formatted_response = f"{response}\n\n{next_question}"
            else:
                # Final assessment
                formatted_response = self._generate_final_triage_response(
                    response, urgency_level, assessment_data
                )
            
            # Add AI response to context
            self.conversation_context[session_id]["messages"].append({
                "role": "assistant",
                "content": formatted_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "response": formatted_response,
                "urgency_level": urgency_level,
                "assessment_questions": questions,
                "medical_keywords": medical_keywords,
                "medical_resources": medical_resources,
                "assessment_data": assessment_data,
                "session_id": session_id,
                "conversation_length": len(self.conversation_context[session_id]["messages"]),
                "generated_at": datetime.utcnow().isoformat(),
                "ai_enhanced": True
            }
            
        except Exception as e:
            logger.error(f"Error processing triage chat message: {str(e)}")
            return self._generate_fallback_assessment(message, session_id)
    
    def _generate_fallback_assessment(self, message: str, session_id: str) -> Dict[str, Any]:
        """Generate fallback assessment when main processing fails"""
        
        # Provide helpful error response instead of generic technical difficulties
        error_response = self._generate_helpful_error_response(message)
        
        return {
            "response": error_response,
            "urgency_level": "routine",
            "assessment_questions": [
                "Can you describe your main symptom?",
                "When did your symptoms start?",
                "How severe are your symptoms on a scale of 1-10?",
                "Are you taking any medications currently?",
                "Do you have any chronic medical conditions?"
            ],
            "medical_keywords": [],
            "medical_resources": [],
            "session_id": session_id,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_final_triage_response(
        self, 
        base_response: str, 
        urgency_level: str, 
        assessment_data: Dict[str, Any]
    ) -> str:
        """Generate final triage response with clear guidance"""
        
        primary_symptom = assessment_data.get("primary_symptom", "your symptoms")
        collected_info = assessment_data.get("information_collected", {})
        red_flags = assessment_data.get("red_flags", [])
        next_steps = assessment_data.get("next_steps", [])
        
        # Build comprehensive response
        response = f"{base_response}\n\n"
        
        # Add urgency assessment
        urgency_messages = {
            "emergency": "🚨 **EMERGENCY PRIORITY** - This requires immediate medical attention.",
            "urgent": "⚠️ **URGENT PRIORITY** - This needs prompt medical evaluation.",
            "routine": "✅ **ROUTINE PRIORITY** - This can be managed with appropriate monitoring."
        }
        
        response += f"{urgency_messages.get(urgency_level, urgency_messages['routine'])}\n\n"
        
        # Add red flags if present
        if red_flags:
            response += "**Important Warning Signs Identified:**\n"
            for flag in red_flags:
                response += f"• {flag}\n"
            response += "\n"
        
        # Add collected information summary
        if collected_info:
            response += "**Based on the information you provided:**\n"
            for key, value in collected_info.items():
                if isinstance(value, list):
                    response += f"• {key.replace('_', ' ').title()}: {', '.join(value)}\n"
                else:
                    response += f"• {key.replace('_', ' ').title()}: {value}\n"
            response += "\n"
        
        # Add next steps
        if next_steps:
            response += "**Recommended Next Steps:**\n"
            for i, step in enumerate(next_steps, 1):
                response += f"{i}. {step}\n"
            response += "\n"
        
        # Add final guidance
        if urgency_level == "emergency":
            response += "**Please seek emergency medical care immediately. Do not delay.**"
        elif urgency_level == "urgent":
            response += "**Please contact your healthcare provider today or visit an urgent care center.**"
        else:
            response += "**Continue monitoring your symptoms and contact your healthcare provider if they worsen or persist.**"
        
        return response
    
    def _generate_helpful_error_response(self, message: str) -> str:
        """Generate helpful error response instead of generic technical difficulties"""
        
        message_lower = message.lower()
        
        # Try to identify symptom even in error case
        if "fever" in message_lower:
            return """I understand you're experiencing a fever. While I'm having some technical issues with my advanced features, I can still help you with basic guidance.

For fever assessment, I need to know:
1. Have you taken your temperature? What is the reading?
2. How long have you had the fever?
3. Are you experiencing chills, body aches, or sweating?
4. Have you taken any fever-reducing medication?
5. Do you have any other symptoms like difficulty breathing or severe headache?

Please provide this information and I'll do my best to guide you appropriately."""

        elif "chest pain" in message_lower:
            return """Chest pain requires careful evaluation. Even though I'm experiencing some technical difficulties, this is important.

I need to know immediately:
1. On a scale of 1-10, how severe is the chest pain?
2. Does the pain radiate to your arm, neck, jaw, or back?
3. Are you having difficulty breathing?
4. When did the pain start?
5. Can you describe the pain - sharp, dull, crushing, or pressure-like?

If you're experiencing severe chest pain, difficulty breathing, or pain radiating to your arm/jaw, please call 911 immediately."""

        elif "breathing" in message_lower or "breath" in message_lower:
            return """Breathing difficulties need prompt attention. Despite my technical issues, I want to help assess your situation.

Please tell me:
1. Are you having trouble breathing at rest or only with activity?
2. When did this start?
3. Do you have any chest pain?
4. Are you coughing or wheezing?
5. Do you have any fever?

If you're having severe difficulty breathing, please call 911 immediately."""

        else:
            return """I want to help assess your symptoms, even though I'm experiencing some technical difficulties with my advanced features.

To provide you with appropriate guidance, please tell me:
1. What is your main symptom?
2. When did it start?
3. How severe is it on a scale of 1-10?
4. Are you experiencing any other symptoms?
5. Have you taken any medications for this?

Please provide this information and I'll do my best to help guide you to appropriate care."""
    
    async def _enhance_with_groq(
        self,
        base_response: str,
        message: str,
        conversation_history: List[Dict],
        urgency_level: str
    ) -> Optional[str]:
        """Enhance response using GROQ API for natural language generation"""
        
        try:
            # Build context for GROQ
            context_messages = ""
            if conversation_history:
                for msg in conversation_history[-3:]:  # Last 3 messages
                    role = "Patient" if msg["role"] == "user" else "Medical Assistant"
                    context_messages += f"{role}: {msg['content']}\n"
            
            # Create enhanced prompt
            prompt = f"""You are a professional medical triage assistant. Based on the conversation context and the base response provided, enhance it to be more natural, empathetic, and medically accurate.

Conversation Context:
{context_messages}

Current Patient Message: {message}
Base Response: {base_response}
Urgency Level: {urgency_level}

Please enhance the base response to be:
1. More natural and conversational
2. Medically accurate and appropriate for the urgency level
3. Empathetic and reassuring when appropriate
4. Clear and actionable

Keep the response under 150 words and maintain the same medical guidance."""
            
            response = await self.api_service.groq.generate_triage_response(
                prompt=prompt,
                urgency_level=urgency_level,
                conversation_context=conversation_history
            )
            
            groq_response = response.get("response", "")
            
            # Check if GROQ response is better than base response
            if groq_response and len(groq_response) > 20 and "I understand your concern" not in groq_response:
                return groq_response
            
            return None
            
        except Exception as e:
            logger.error(f"GROQ enhancement failed: {e}")
            return None
    
    async def _extract_medical_keywords(self, message: str) -> Dict[str, List[str]]:
        """Extract medical keywords from user message"""
        
        try:
            # Try API service first
            result = await self.api_service.keyword_ai.extract_medical_keywords(
                text_content=[message],
                analysis_type="triage"
            )
            
            # If API returns valid results, use them
            if result and any(result.get(key, []) for key in ["conditions", "symptoms", "treatments", "general"]):
                return result
            else:
                # API returned empty results, use fallback
                return self._fallback_keyword_extraction(message)
                
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            # Use fallback when API fails
            return self._fallback_keyword_extraction(message)
    
    def _fallback_keyword_extraction(self, message: str) -> Dict[str, List[str]]:
        """Fallback keyword extraction using simple pattern matching"""
        
        message_lower = message.lower()
        
        # Comprehensive medical keywords
        symptom_keywords = {
            "chest_pain": {
                "keywords": ["chest pain", "chest hurt", "chest ache", "heart pain"],
                "conditions": ["chest pain", "angina", "heart attack"],
                "symptoms": ["chest discomfort", "pressure", "tightness"],
                "treatments": ["nitroglycerin", "aspirin", "emergency care"],
                "general": ["cardiac", "cardiovascular"]
            },
            "breathing": {
                "keywords": ["breathe", "breathing", "shortness of breath", "wheezing", "cough", "can't breathe"],
                "conditions": ["asthma", "pneumonia", "respiratory distress"],
                "symptoms": ["dyspnea", "wheezing", "cough"],
                "treatments": ["inhaler", "oxygen", "bronchodilator"],
                "general": ["respiratory", "pulmonary"]
            },
            "pain": {
                "keywords": ["pain", "ache", "hurt", "sore", "tender", "sharp", "dull", "throbbing"],
                "conditions": ["pain syndrome", "inflammation"],
                "symptoms": ["discomfort", "soreness", "aching"],
                "treatments": ["pain medication", "ibuprofen", "acetaminophen"],
                "general": ["analgesic", "pain management"]
            },
            "fever": {
                "keywords": ["fever", "temperature", "hot", "chills", "sweating", "feverish"],
                "conditions": ["infection", "viral syndrome", "bacterial infection"],
                "symptoms": ["hyperthermia", "chills", "sweats"],
                "treatments": ["antipyretic", "fluids", "rest"],
                "general": ["infectious", "immune response"]
            },
            "digestive": {
                "keywords": ["nausea", "vomiting", "diarrhea", "stomach", "abdominal", "belly", "gut"],
                "conditions": ["gastroenteritis", "food poisoning", "stomach flu"],
                "symptoms": ["nausea", "vomiting", "diarrhea", "cramping"],
                "treatments": ["fluids", "BRAT diet", "anti-nausea"],
                "general": ["gastrointestinal", "digestive"]
            },
            "neurological": {
                "keywords": ["headache", "dizzy", "dizziness", "confusion", "numbness", "tingling"],
                "conditions": ["migraine", "tension headache", "vertigo"],
                "symptoms": ["cephalgia", "vertigo", "paresthesia"],
                "treatments": ["pain relievers", "rest", "hydration"],
                "general": ["neurological", "nervous system"]
            },
            "cardiac": {
                "keywords": ["heart", "palpitations", "racing heart", "irregular heartbeat"],
                "conditions": ["arrhythmia", "tachycardia", "heart disease"],
                "symptoms": ["palpitations", "irregular rhythm"],
                "treatments": ["cardiac medication", "monitoring"],
                "general": ["cardiac", "cardiovascular"]
            }
        }
        
        extracted = {
            "conditions": [],
            "symptoms": [],
            "treatments": [],
            "general": []
        }
        
        # Check for matches
        for category, data in symptom_keywords.items():
            for keyword in data["keywords"]:
                if keyword in message_lower:
                    extracted["conditions"].extend(data["conditions"])
                    extracted["symptoms"].extend(data["symptoms"])
                    extracted["treatments"].extend(data["treatments"])
                    extracted["general"].extend(data["general"])
                    break
        
        # Remove duplicates and limit results
        for key in extracted:
            extracted[key] = list(set(extracted[key]))[:5]
        
        return extracted
    
    def _extract_symptoms_from_keywords(self, keywords_result: Dict[str, List[str]]) -> List[str]:
        """Extract symptom list from keyword extraction results"""
        
        symptoms = []
        symptoms.extend(keywords_result.get("symptoms", []))
        symptoms.extend(keywords_result.get("conditions", []))
        
        return list(set(symptoms))  # Remove duplicates
    
    def _assess_urgency_level(self, message: str, symptoms: List[str], conversation_context: Dict[str, Any] = None) -> str:
        """Assess urgency level based on message content, symptoms, and conversation context"""
        
        message_lower = message.lower()
        symptoms_lower = [s.lower() for s in symptoms]
        
        # Get conversation history for context
        previous_urgency = "routine"
        previous_messages = []
        if conversation_context:
            previous_urgency = conversation_context.get("urgency_level", "routine")
            for msg in conversation_context.get("messages", []):
                if msg.get("role") == "user":
                    previous_messages.append(msg.get("content", "").lower())
        
        previous_context = " ".join(previous_messages)
        
        # Emergency keywords - immediate life-threatening conditions
        emergency_keywords = [
            "can't breathe", "cannot breathe", "difficulty breathing", "shortness of breath",
            "chest pain", "heart attack", "stroke", "seizure", "unconscious", 
            "bleeding heavily", "severe bleeding", "suicide", "overdose", 
            "allergic reaction", "anaphylaxis", "severe pain", "crushing pain",
            "call 911", "emergency", "dying", "can't move"
        ]
        
        # Urgent keywords - need medical attention within 24 hours
        urgent_keywords = [
            "severe", "intense", "unbearable", "getting worse", "worsening",
            "high fever", "fever over 103", "vomiting blood", "blood in stool",
            "severe headache", "worst headache", "vision problems", "confusion",
            "severe abdominal pain", "can't keep fluids down", "dehydrated",
            "8 out of 10", "9 out of 10", "10 out of 10", "radiating", "radiate"
        ]
        
        # Check for emergency conditions in current message
        for phrase in emergency_keywords:
            if phrase in message_lower:
                return "emergency"
        
        # Check for emergency symptoms
        emergency_symptoms = ["chest pain", "dyspnea", "respiratory distress"]
        if any(symptom in symptoms_lower for symptom in emergency_symptoms):
            return "emergency"
        
        # Context-based urgency assessment
        if "chest pain" in previous_context:
            # Any follow-up to chest pain should remain emergency unless explicitly mild
            if not any(mild in message_lower for mild in ["mild", "better", "gone", "stopped"]):
                return "emergency"
        
        if "difficulty breathing" in previous_context or "shortness of breath" in previous_context:
            # Any follow-up to breathing issues should remain emergency
            if not any(mild in message_lower for mild in ["mild", "better", "gone", "stopped"]):
                return "emergency"
        
        # Check for urgent conditions in current message
        if any(keyword in message_lower for keyword in urgent_keywords):
            return "urgent"
        
        # Fever-specific urgency assessment
        if "fever" in message_lower or "fever" in previous_context:
            # Check for high fever indicators
            if any(temp in message_lower for temp in ["103", "104", "105"]):
                return "emergency"
            elif any(temp in message_lower for temp in ["102", "101"]):
                return "urgent"
            elif "fever" in previous_context and previous_urgency == "urgent":
                # Maintain urgent status for fever follow-ups unless explicitly mild
                if not any(mild in message_lower for mild in ["mild", "better", "lower", "down"]):
                    return "urgent"
        
        # Check for moderate symptoms that need attention
        moderate_keywords = [
            "fever", "pain", "nausea", "vomiting", "headache", "cough",
            "diarrhea", "rash", "swelling", "infection"
        ]
        
        if any(keyword in message_lower for keyword in moderate_keywords):
            return "urgent"
        
        # Check for mild symptoms
        mild_keywords = [
            "tired", "fatigue", "minor pain", "slight", "mild", "little",
            "dizzy", "nauseous", "upset stomach", "runny nose", "sneezing"
        ]
        
        if any(keyword in message_lower for keyword in mild_keywords):
            return "routine"
        
        # If this is a follow-up message and we don't have clear indicators, 
        # maintain the previous urgency level to avoid inconsistency
        if previous_messages and previous_urgency in ["emergency", "urgent"]:
            return previous_urgency
        
        return "routine"
    
    async def _generate_ai_response(
        self, 
        message: str, 
        context: Dict[str, Any], 
        urgency_level: str
    ) -> str:
        """Generate AI response using GROQ with improved fallback"""
        
        try:
            # Build conversation history for context
            conversation_history = context.get("messages", [])[-5:]  # Last 5 messages
            
            # Create prompt for medical triage
            prompt = self._build_triage_prompt(message, conversation_history, urgency_level)
            
            # Try GROQ API first
            response = await self.api_service.groq.generate_triage_response(
                prompt=prompt,
                urgency_level=urgency_level,
                conversation_context=conversation_history
            )
            
            # Check if we got a meaningful response from GROQ
            groq_response = response.get("response", "")
            
            # If GROQ response is generic or empty, use our improved fallback
            generic_phrases = [
                "I understand your concern about these symptoms",
                "Based on what you've described, I recommend",
                "Thank you for sharing your symptoms with me. While these don't appear",
                "Thank you for providing that additional information. Based on what you've shared so far",
                "Thank you for sharing that information with me. To provide you with the most helpful guidance"
            ]
            
            if not groq_response or any(phrase in groq_response for phrase in generic_phrases):
                logger.info("Using improved fallback response instead of generic GROQ response")
                return self._get_contextual_fallback_response(message, urgency_level, conversation_history)
            
            return groq_response
            
        except Exception as e:
            logger.error(f"GROQ response generation failed: {e}")
            return self._get_contextual_fallback_response(message, urgency_level, context.get("messages", []))
    
    def _build_triage_prompt(
        self, 
        message: str, 
        conversation_history: List[Dict], 
        urgency_level: str
    ) -> str:
        """Build detailed prompt for GROQ API"""
        
        context_messages = ""
        if conversation_history:
            context_messages = "Previous conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                role = "Patient" if msg["role"] == "user" else "Medical Assistant"
                context_messages += f"{role}: {msg['content']}\n"
            context_messages += "\n"
        
        urgency_guidance = {
            "emergency": "This is a medical emergency. Provide immediate guidance and strongly recommend calling 911 or going to the emergency room.",
            "urgent": "This requires prompt medical attention. Recommend contacting healthcare provider today or visiting urgent care.",
            "routine": "This appears to be a routine concern. Provide helpful guidance and suggest appropriate follow-up."
        }
        
        return f"""You are an experienced medical triage assistant providing compassionate, accurate guidance. 

{context_messages}Current Patient Message: "{message}"

Assessment: {urgency_level.upper()} priority - {urgency_guidance.get(urgency_level, "")}

Please provide a personalized response that:
1. Acknowledges the patient's specific symptoms mentioned
2. Provides relevant medical information about their condition
3. Gives clear, actionable next steps appropriate for the urgency level
4. Asks relevant follow-up questions to better understand their situation
5. Shows empathy and reassurance where appropriate

Be specific to their symptoms rather than generic. If they mention chest pain, address chest pain specifically. If they mention fever and headache, address that combination. Make the response feel personal and medically informed.

Keep the response conversational, professional, and under 150 words."""
    
    def _get_fallback_response(self, message: str, urgency_level: str) -> str:
        """Generate dynamic, contextual fallback response when AI fails"""
        
        message_lower = message.lower()
        
        # Emergency responses - immediate action required
        if urgency_level == "emergency":
            if "chest pain" in message_lower:
                return "Chest pain can be a sign of a heart attack or other serious cardiac condition. Please call 911 or go to the nearest emergency room immediately. Do not drive yourself - have someone else drive you or call an ambulance."
            elif "difficulty breathing" in message_lower or "can't breathe" in message_lower:
                return "Difficulty breathing is a medical emergency. Please call 911 immediately. While waiting for help, try to stay calm and sit upright. If you have a rescue inhaler, use it as prescribed."
            elif "shortness of breath" in message_lower:
                return "Shortness of breath can indicate a serious condition affecting your heart or lungs. Please seek emergency medical care immediately by calling 911 or going to the nearest emergency room."
            else:
                return "Based on your symptoms, this appears to be a medical emergency. Please call 911 or go to the nearest emergency room immediately. Do not delay seeking medical care."
        
        # Urgent responses - need medical attention soon
        elif urgency_level == "urgent":
            if "fever" in message_lower and "headache" in message_lower:
                return "The combination of fever and headache can indicate various conditions, from viral infections to more serious issues. Please contact your healthcare provider today or visit an urgent care center. Monitor your temperature and seek immediate care if it rises above 103°F or if you develop neck stiffness."
            elif "severe headache" in message_lower or "worst headache" in message_lower:
                return "A severe or unusually intense headache can be concerning. Please contact your healthcare provider immediately or visit an urgent care center. If this is the worst headache of your life, consider going to the emergency room."
            elif "high fever" in message_lower or "fever" in message_lower:
                return "A high fever indicates your body is fighting an infection. Please contact your healthcare provider today. Take your temperature regularly, stay hydrated, and seek immediate care if your fever exceeds 103°F or if you develop difficulty breathing."
            elif "severe pain" in message_lower:
                return "Severe pain should not be ignored. Please contact your healthcare provider today or visit an urgent care center. Rate your pain on a scale of 1-10 and be prepared to describe its location, quality, and what makes it better or worse."
            elif "vomiting" in message_lower and ("blood" in message_lower or "can't keep" in message_lower):
                return "Persistent vomiting, especially with blood or inability to keep fluids down, requires prompt medical attention. Please contact your healthcare provider immediately or visit an urgent care center to prevent dehydration."
            else:
                return "Based on your symptoms, I recommend contacting your healthcare provider today or visiting an urgent care center within the next few hours. Your symptoms warrant prompt medical evaluation to ensure proper diagnosis and treatment."
        
        # Specific symptom responses for routine cases
        elif "chest pain" in message_lower:
            return "Chest pain can have many causes, ranging from muscle strain to heart conditions. Can you describe the pain more specifically? Is it sharp, dull, or crushing? Does it worsen with movement or breathing? When did it start? Even if it seems mild, chest pain should be evaluated by a healthcare provider."
        
        elif "difficulty breathing" in message_lower or "shortness of breath" in message_lower:
            return "Breathing difficulties should always be taken seriously. Are you having trouble breathing at rest or only with activity? Do you have any chest pain, wheezing, or cough? Have you been exposed to any allergens? Please consider contacting your healthcare provider for evaluation."
        
        elif "headache" in message_lower:
            return "I'm sorry you're dealing with a headache. Can you describe the type of pain - is it throbbing, sharp, or a dull ache? Where is it located? How severe is it on a scale of 1-10? Have you taken any medication for it? Most headaches are manageable, but I can help you determine if you need medical attention."
        
        elif "fever" in message_lower or "temperature" in message_lower:
            return "Fever is your body's way of fighting infection. Have you taken your temperature? What reading did you get? Are you experiencing chills, body aches, or other symptoms? Stay hydrated, rest, and monitor your temperature. Contact a healthcare provider if it exceeds 101°F or persists."
        
        elif "nausea" in message_lower or "vomiting" in message_lower:
            return "Nausea and vomiting can be uncomfortable and have various causes. How long have you been experiencing this? Are you able to keep fluids down? Any abdominal pain or fever? Try small sips of clear fluids and bland foods. Seek medical care if you can't keep fluids down or if symptoms worsen."
        
        elif "dizzy" in message_lower or "dizziness" in message_lower:
            return "Dizziness can have several causes. Is it a spinning sensation (vertigo) or more like feeling lightheaded? Does it happen when you stand up or change positions? Any hearing changes or headache? Stay hydrated and avoid sudden movements. If it persists or worsens, contact your healthcare provider."
        
        elif "pain" in message_lower:
            return "I understand you're experiencing pain. Can you tell me more about it? Where exactly is the pain located? How would you rate it on a scale of 1-10? Is it constant or does it come and go? What makes it better or worse? This information will help me provide better guidance."
        
        elif "cough" in message_lower:
            return "A cough can be due to various causes. Is it a dry cough or are you bringing up mucus? How long have you had it? Any fever, shortness of breath, or chest pain? Stay hydrated and consider honey for throat irritation. If it persists over a week or you develop fever, contact your healthcare provider."
        
        elif "tired" in message_lower or "fatigue" in message_lower:
            return "Fatigue can affect daily life and has many possible causes. How long have you been feeling this way? Is it affecting your sleep or daily activities? Any other symptoms like fever, weight changes, or mood changes? Ensure you're getting adequate sleep, nutrition, and exercise. If it persists, consider discussing with your healthcare provider."
        
        elif any(greeting in message_lower for greeting in ["hello", "hi", "hey", "good morning", "good afternoon", "help"]):
            return "Hello! I'm here to help assess your symptoms and provide medical guidance. What specific symptoms or health concerns would you like to discuss today? Please describe what you're experiencing, when it started, and how it's affecting you."
        
        elif "thank" in message_lower:
            return "You're welcome! I'm glad I could help. Remember, if your symptoms worsen or you develop new concerning symptoms, don't hesitate to contact your healthcare provider. Is there anything else about your symptoms you'd like to discuss?"
        
        else:
            return "Thank you for sharing that information with me. To provide you with the most helpful guidance, could you tell me more about your specific symptoms? For example, when did they start, how severe are they, and how are they affecting your daily activities?"
    
    async def _fetch_relevant_resources(
        self, 
        symptoms: List[str], 
        conditions: List[str]
    ) -> List[Dict[str, Any]]:
        """Fetch relevant medical resources using Tavily"""
        
        if not symptoms and not conditions:
            return []
        
        try:
            # Use the most relevant symptom or condition for search
            search_terms = (symptoms + conditions)[:2]  # Top 2 terms
            
            resources = []
            for term in search_terms:
                result = await self.api_service.tavily.fetch_medical_resources(
                    condition=term,
                    analysis_type="triage"
                )
                
                articles = result.get("medical_articles", [])
                resources.extend(articles[:2])  # Top 2 articles per term
            
            return resources[:3]  # Return top 3 resources total
            
        except Exception as e:
            logger.error(f"Resource fetching failed: {e}")
            return self._get_fallback_resources(symptoms + conditions)
    
    def _get_fallback_resources(self, terms: List[str]) -> List[Dict[str, Any]]:
        """Get fallback medical resources"""
        
        if not terms:
            return []
        
        primary_term = terms[0] if terms else "general health"
        
        return [
            {
                "title": f"Understanding {primary_term.title()}",
                "url": "https://www.mayoclinic.org/diseases-conditions",
                "source": "Mayo Clinic",
                "snippet": f"Comprehensive medical information about {primary_term} including symptoms, causes, and treatment options."
            },
            {
                "title": "When to Seek Medical Care",
                "url": "https://www.healthline.com/health",
                "source": "Healthline",
                "snippet": "Guidelines for determining when symptoms require immediate medical attention versus home care."
            }
        ]
    
    def _generate_follow_up_questions(
        self, 
        message: str, 
        symptoms: List[str], 
        conversation_history: List[Dict]
    ) -> List[str]:
        """Generate contextual, specific follow-up questions that avoid repetition"""
        
        message_lower = message.lower()
        
        # Get all previous messages to avoid asking the same questions
        previous_messages = " ".join([msg.get("content", "") for msg in conversation_history])
        previous_lower = previous_messages.lower()
        
        # Track what information we already have
        has_temperature = any(temp in previous_lower for temp in ["temperature", "102", "103", "104", "101", "100", "99", "degrees"])
        has_duration = any(time in previous_lower for time in ["started", "ago", "yesterday", "today", "hours", "days", "began"])
        has_severity = any(scale in previous_lower for scale in ["scale", "1-10", "out of 10", "severe", "mild", "moderate"])
        has_location = any(loc in previous_lower for loc in ["where", "location", "chest", "head", "stomach", "arm", "leg"])
        has_associated_symptoms = any(assoc in previous_lower for assoc in ["chills", "nausea", "vomiting", "aches", "sweating"])
        
        questions = []
        
        # Fever-specific questions
        if "fever" in previous_lower:
            if not has_temperature and "temperature" not in message_lower:
                questions.append("Have you taken your temperature? What was the reading?")
            elif not has_associated_symptoms and not any(word in message_lower for word in ["chills", "aches", "sweating"]):
                questions.append("Are you experiencing chills, body aches, or sweating?")
            elif not has_duration and "started" not in message_lower:
                questions.append("How long have you had the fever?")
            elif "medication" not in previous_lower:
                questions.append("Have you taken any fever-reducing medication like acetaminophen or ibuprofen?")
        
        # Chest pain specific questions
        elif "chest pain" in previous_lower:
            if not any(desc in previous_lower for desc in ["sharp", "dull", "crushing", "pressure", "burning"]):
                questions.append("Can you describe the type of chest pain - is it sharp, dull, crushing, or pressure-like?")
            elif not any(rad in previous_lower for rad in ["radiate", "spread", "arm", "neck", "jaw", "back"]):
                questions.append("Does the pain spread or radiate to your arm, neck, jaw, or back?")
            elif not has_severity:
                questions.append("On a scale of 1-10, how severe is the chest pain?")
        
        # Breathing issues
        elif any(breath in previous_lower for breath in ["breathing", "breath", "shortness"]):
            if not any(when in previous_lower for when in ["rest", "activity", "walking", "stairs", "lying down"]):
                questions.append("Does the breathing difficulty occur at rest, with activity, or both?")
            elif not any(sound in previous_lower for sound in ["wheezing", "whistling", "rattling"]):
                questions.append("Are you hearing any wheezing, whistling, or unusual sounds when breathing?")
            elif "position" not in previous_lower:
                questions.append("Does sitting up or changing position help with your breathing?")
        
        # Headache specific questions
        elif "headache" in previous_lower:
            if not has_location and not any(loc in previous_lower for loc in ["front", "back", "side", "temple", "all over"]):
                questions.append("Where exactly is the headache located - front, back, sides, or all over?")
            elif not any(type_word in previous_lower for type_word in ["throbbing", "pounding", "sharp", "dull", "pressure"]) and not any(type_word in message_lower for type_word in ["throbbing", "pounding", "sharp", "dull", "pressure"]):
                questions.append("Is the headache throbbing, sharp, dull, or more like pressure?")
            elif not any(trigger in previous_lower for trigger in ["light", "sound", "noise", "bright"]) and not any(trigger in message_lower for trigger in ["light", "sound", "noise", "bright"]):
                questions.append("Are you sensitive to light or sound?")
        
        # General follow-up questions based on conversation stage
        if len(conversation_history) <= 2:
            # Early in conversation - ask basic questions
            if not has_duration:
                questions.append("When did your symptoms first start?")
            if not has_severity and "pain" in previous_lower:
                questions.append("How would you rate your symptoms on a scale of 1-10?")
        else:
            # Later in conversation - ask more specific questions
            if "medication" not in previous_lower and not any(med in previous_lower for med in ["taking", "pills", "prescription"]):
                questions.append("Are you currently taking any medications for this or other conditions?")
            if not any(change in previous_lower for change in ["better", "worse", "same", "improving", "worsening"]):
                questions.append("Are your symptoms getting better, worse, or staying about the same?")
            if not any(trigger in previous_lower for trigger in ["trigger", "cause", "started after", "happened when"]):
                questions.append("Did anything specific trigger these symptoms or make them start?")
        
        # Remove questions that might have already been answered in the current message
        filtered_questions = []
        for question in questions:
            question_lower = question.lower()
            # Check if the current message already answers this question
            if "temperature" in question_lower and any(temp in message_lower for temp in ["temperature", "102", "103", "104", "101", "100", "99"]):
                continue
            if "chills" in question_lower and "chills" in message_lower:
                continue
            if "started" in question_lower and any(time in message_lower for time in ["started", "ago", "yesterday", "today"]):
                continue
            if "scale" in question_lower and any(scale in message_lower for scale in ["out of 10", "scale", "/10"]):
                continue
            
            filtered_questions.append(question)
        
        # If no specific questions, provide general follow-up
        if not filtered_questions:
            if len(conversation_history) > 3:
                filtered_questions = ["Is there anything else about your symptoms you'd like to discuss?"]
            else:
                filtered_questions = ["Can you tell me more about how these symptoms are affecting you?"]
        
        return filtered_questions[:3]  # Return top 3 questions
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of conversation session"""
        
        if session_id not in self.conversation_context:
            return None
        
        context = self.conversation_context[session_id]
        
        return {
            "session_id": session_id,
            "message_count": len(context["messages"]),
            "extracted_symptoms": list(set(context["extracted_symptoms"])),
            "urgency_level": context["urgency_level"],
            "medical_keywords": list(set(context["medical_keywords"])),
            "created_at": context["created_at"],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _get_contextual_fallback_response(self, message: str, urgency_level: str, conversation_history: List[Dict]) -> str:
        """Generate contextual fallback response considering conversation history"""
        
        message_lower = message.lower()
        
        # Get previous messages for context
        previous_messages = []
        for msg in conversation_history:
            if msg.get("role") == "user":
                previous_messages.append(msg.get("content", "").lower())
        
        previous_context = " ".join(previous_messages)
        
        # Check if this is a follow-up to fever
        if "fever" in previous_context:
            # Check for temperature information first
            if any(temp in message_lower for temp in ["102", "103", "104", "101", "100", "99", "temperature"]):
                temp_value = None
                for temp in ["104", "103", "102", "101", "100", "99"]:
                    if temp in message_lower:
                        temp_value = temp
                        break
                
                if temp_value and int(temp_value) >= 103:
                    return f"A fever of {temp_value}°F is quite high and concerning. This requires immediate medical attention. Please go to the emergency room or call 911, especially if you're having difficulty breathing or other severe symptoms."
                elif temp_value and int(temp_value) >= 101:
                    return f"A fever of {temp_value}°F indicates a significant infection. Please contact your healthcare provider today or visit an urgent care center. Stay hydrated, rest, and monitor for worsening symptoms."
                else:
                    return f"Thank you for providing your temperature reading. Even a moderate fever indicates your body is fighting an infection. Continue monitoring your temperature, stay hydrated, and contact your healthcare provider if it rises or you develop other concerning symptoms."
            
            # Check for chills and body aches
            elif any(word in message_lower for word in ["chills", "sweating", "aches", "body aches", "shivering", "yes i have chills", "have chills"]):
                return f"Fever with chills and body aches is a common pattern when your body is fighting an infection. This suggests your immune system is actively responding. Please contact your healthcare provider today for evaluation and possible treatment. Stay hydrated and consider fever-reducing medication if you haven't already."
            
            # Check for duration information
            elif any(duration in message_lower for duration in ["yesterday", "today", "hours", "days", "started", "began"]):
                if "yesterday" in message_lower or "24 hours" in message_lower:
                    return f"A fever that started yesterday needs medical attention, especially if it's persisting or getting worse. Please contact your healthcare provider today to determine if you need evaluation or treatment."
                elif any(word in message_lower for word in ["today", "this morning", "few hours"]):
                    return f"Since your fever just started, monitor it closely. Take your temperature regularly, stay hydrated, and contact your healthcare provider if it rises above 101°F or if you develop other concerning symptoms."
                else:
                    return f"Thank you for that timing information. The duration of fever helps determine the urgency of care needed. Please continue monitoring your symptoms and contact your healthcare provider for guidance."
            
            # Check for medication information
            elif any(med in message_lower for med in ["haven't taken", "no medication", "not taken", "haven't used"]):
                return f"Since you haven't taken any fever-reducing medication yet, you may want to consider acetaminophen or ibuprofen to help with comfort, following package directions. However, given your fever and symptoms, please still contact your healthcare provider today for proper evaluation."
        
        # Check if this is a follow-up to chest pain
        elif "chest pain" in previous_context:
            if any(word in message_lower for word in ["started", "ago", "hours", "minutes"]):
                return f"Thank you for that additional information about when your chest pain started. Given that you're experiencing chest pain, this is still a medical emergency. Please call 911 or go to the nearest emergency room immediately, especially since chest pain can indicate a heart attack."
            
            elif any(word in message_lower for word in ["sharp", "dull", "crushing", "pressure", "8", "9", "10"]):
                if any(severe in message_lower for severe in ["8", "9", "10", "severe", "crushing"]):
                    return f"A pain level of that intensity with chest pain is very concerning and suggests this could be a heart attack or other serious cardiac emergency. Please call 911 immediately. Do not drive yourself to the hospital."
                else:
                    return f"Thank you for describing your chest pain. Even though it may not seem severe, chest pain should always be evaluated immediately. Please call 911 or go to the nearest emergency room right away."
            
            elif any(word in message_lower for word in ["radiate", "radiating", "arm", "neck", "jaw", "shoulder", "left arm", "right arm"]):
                return f"Chest pain that radiates to the arm, neck, or jaw is a classic sign of a heart attack. This is a medical emergency. Please call 911 immediately. Do not delay - time is critical for heart attack treatment."
        
        # Check if this is a follow-up to breathing issues
        elif any(breathing in previous_context for breathing in ["breathing", "breath"]):
            if any(word in message_lower for word in ["rest", "activity", "walking", "stairs"]):
                return f"Difficulty breathing, whether at rest or with activity, can indicate serious heart or lung problems. Please seek emergency medical care immediately by calling 911 or going to the nearest emergency room."
        
        # Check if this is a follow-up to headache
        elif "headache" in previous_context:
            if any(word in message_lower for word in ["worst", "severe", "10", "9", "8"]):
                return f"A severe headache, especially if it's the worst you've ever had, can be a sign of a serious condition like a stroke or brain hemorrhage. Please go to the emergency room immediately or call 911."
            
            elif any(word in message_lower for word in ["neck", "stiff", "light", "sensitive"]):
                return f"Headache with neck stiffness or light sensitivity can be signs of meningitis, which is a medical emergency. Please go to the emergency room immediately or call 911."
        
        # If no specific context matches, provide a contextual response based on the conversation
        if len(previous_messages) > 0:
            # This is a follow-up in an ongoing conversation
            return f"Thank you for providing that additional information. Based on what you've shared so far, I recommend continuing to monitor your symptoms closely. If they worsen or you develop new concerning symptoms, please contact your healthcare provider promptly."
        
        # If no specific context, use the regular fallback response
        return self._get_fallback_response(message, urgency_level)
