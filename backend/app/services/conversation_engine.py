"""
Enhanced Conversation Engine for Dynamic Triage Chat
Implements intelligent question flow and context-aware responses
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ConversationEngine:
    """Advanced conversation engine for dynamic medical triage"""
    
    def __init__(self):
        self.conversation_templates = self._load_conversation_templates()
        self.question_flows = self._load_question_flows()
    
    def generate_dynamic_response(
        self,
        message: str,
        conversation_history: List[Dict],
        extracted_symptoms: List[str],
        urgency_level: str,
        medical_keywords: Dict[str, List[str]]
    ) -> Tuple[str, List[str]]:
        """
        Generate dynamic response with embedded follow-up questions
        Returns: (response_text, next_questions)
        """
        
        message_lower = message.lower()
        
        # Determine conversation stage and context
        conversation_context = self._analyze_conversation_context(conversation_history)
        primary_symptom = self._identify_primary_symptom(message, extracted_symptoms, conversation_context)
        
        # Generate contextual response with embedded questions
        if len(conversation_history) <= 2:
            # Initial symptom assessment
            response, questions = self._generate_initial_assessment(
                message, primary_symptom, urgency_level, medical_keywords
            )
        else:
            # Follow-up conversation
            response, questions = self._generate_follow_up_response(
                message, conversation_context, primary_symptom, urgency_level, medical_keywords
            )
        
        return response, questions
    
    def _analyze_conversation_context(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation to understand current context and stage"""
        
        context = {
            "primary_symptoms": [],
            "mentioned_details": {},
            "stage": "initial",
            "information_gathered": {},
            "urgency_progression": []
        }
        
        for msg in conversation_history:
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                
                # Track symptoms mentioned
                symptoms = self._extract_symptoms_from_text(content)
                context["primary_symptoms"].extend(symptoms)
                
                # Track specific details
                if any(temp in content for temp in ["102", "103", "104", "101", "100", "99", "temperature"]):
                    context["information_gathered"]["temperature"] = True
                
                if any(time in content for time in ["yesterday", "today", "hours", "days", "started", "ago"]):
                    context["information_gathered"]["duration"] = True
                
                if any(sev in content for sev in ["scale", "out of 10", "/10", "severe", "mild"]):
                    context["information_gathered"]["severity"] = True
                
                if any(med in content for med in ["medication", "medicine", "pills", "taken", "ibuprofen", "acetaminophen"]):
                    context["information_gathered"]["medication"] = True
        
        # Determine conversation stage
        if len(conversation_history) <= 2:
            context["stage"] = "initial"
        elif len(context["information_gathered"]) < 2:
            context["stage"] = "gathering_basics"
        elif len(context["information_gathered"]) < 4:
            context["stage"] = "detailed_assessment"
        else:
            context["stage"] = "comprehensive_evaluation"
        
        return context
    
    def _identify_primary_symptom(
        self, 
        message: str, 
        extracted_symptoms: List[str], 
        context: Dict[str, Any]
    ) -> str:
        """Identify the primary symptom being discussed"""
        
        message_lower = message.lower()
        
        # Check for explicit symptoms in current message
        symptom_keywords = {
            "fever": ["fever", "temperature", "hot", "chills"],
            "chest_pain": ["chest pain", "chest hurt", "heart pain"],
            "breathing": ["breathing", "breath", "shortness", "wheezing"],
            "headache": ["headache", "head hurt", "migraine"],
            "nausea": ["nausea", "nauseous", "vomiting", "sick"],
            "pain": ["pain", "hurt", "ache", "sore"],
            "fatigue": ["tired", "fatigue", "exhausted", "weak"]
        }
        
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return symptom
        
        # Check conversation context for primary symptom
        if context["primary_symptoms"]:
            return context["primary_symptoms"][0]
        
        # Check extracted symptoms
        if extracted_symptoms:
            return extracted_symptoms[0].lower()
        
        return "general"
    
    def _generate_initial_assessment(
        self,
        message: str,
        primary_symptom: str,
        urgency_level: str,
        medical_keywords: Dict[str, List[str]]
    ) -> Tuple[str, List[str]]:
        """Generate initial assessment response with embedded questions"""
        
        templates = self.conversation_templates.get(primary_symptom, self.conversation_templates["general"])
        
        # Select appropriate template based on urgency
        if urgency_level == "emergency":
            base_response = templates["emergency"]["initial"]
            follow_up_template = templates["emergency"]["questions"]
        elif urgency_level == "urgent":
            base_response = templates["urgent"]["initial"]
            follow_up_template = templates["urgent"]["questions"]
        else:
            base_response = templates["routine"]["initial"]
            follow_up_template = templates["routine"]["questions"]
        
        # Generate contextual response
        response = base_response.format(symptom=primary_symptom)
        
        # Add embedded questions naturally
        questions = follow_up_template["initial"]
        if questions:
            response += f"\n\nTo better assist you: {questions[0]}"
        
        return response, questions[1:] if len(questions) > 1 else []
    
    def _generate_follow_up_response(
        self,
        message: str,
        context: Dict[str, Any],
        primary_symptom: str,
        urgency_level: str,
        medical_keywords: Dict[str, List[str]]
    ) -> Tuple[str, List[str]]:
        """Generate follow-up response based on conversation context"""
        
        message_lower = message.lower()
        stage = context["stage"]
        gathered_info = context["information_gathered"]
        
        # Generate contextual response based on new information
        response = self._generate_contextual_response(message, primary_symptom, context, urgency_level)
        
        # Determine next questions based on missing information
        next_questions = self._determine_next_questions(primary_symptom, gathered_info, stage, message_lower)
        
        # Embed the most important question naturally
        if next_questions:
            response += f"\n\n{next_questions[0]}"
        
        return response, next_questions[1:] if len(next_questions) > 1 else []
    
    def _generate_contextual_response(
        self,
        message: str,
        primary_symptom: str,
        context: Dict[str, Any],
        urgency_level: str
    ) -> str:
        """Generate contextual response based on user input"""
        
        message_lower = message.lower()
        
        # Temperature-specific responses
        if any(temp in message_lower for temp in ["102", "103", "104", "101", "100", "99"]):
            temp_value = None
            for temp in ["104", "103", "102", "101", "100", "99"]:
                if temp in message_lower:
                    temp_value = int(temp)
                    break
            
            if temp_value and temp_value >= 103:
                return f"A fever of {temp_value}°F is quite high and concerning. This requires immediate medical attention. Please go to the emergency room or call 911."
            elif temp_value and temp_value >= 101:
                return f"A fever of {temp_value}°F indicates a significant infection. Please contact your healthcare provider today or visit an urgent care center."
            else:
                return f"Thank you for providing your temperature reading. A fever of {temp_value}°F suggests your body is fighting an infection."
        
        # Duration-specific responses
        elif any(time in message_lower for time in ["yesterday", "today", "hours", "days", "started", "ago"]):
            if "yesterday" in message_lower:
                return f"Since your {primary_symptom} started yesterday, it's important to monitor how it's progressing. Symptoms that persist or worsen need medical evaluation."
            elif "today" in message_lower or "this morning" in message_lower:
                return f"Since your {primary_symptom} just started today, let's gather more information to determine the best course of action."
            else:
                return f"Thank you for that timing information. Understanding when symptoms started helps determine urgency and appropriate care."
        
        # Severity-specific responses
        elif any(sev in message_lower for sev in ["8", "9", "10", "severe", "unbearable"]):
            return f"A severity level that high is very concerning and indicates you need prompt medical attention. Please don't delay in seeking care."
        elif any(sev in message_lower for sev in ["1", "2", "3", "mild", "slight"]):
            return f"While your symptoms seem mild, it's still important to monitor them and understand what might be causing them."
        
        # Associated symptoms
        elif "chills" in message_lower and "fever" in str(context["primary_symptoms"]):
            return f"Fever with chills is a common pattern when your body is fighting an infection. This suggests your immune system is actively responding."
        elif "nausea" in message_lower:
            return f"Nausea along with your other symptoms can help us understand what might be causing your condition."
        
        # Medication responses
        elif any(med in message_lower for med in ["haven't taken", "no medication", "not taken"]):
            return f"Since you haven't taken any medication yet, we can discuss appropriate options based on your symptoms and their severity."
        elif any(med in message_lower for med in ["ibuprofen", "acetaminophen", "tylenol", "advil"]):
            return f"Thank you for letting me know what medication you've taken. This helps me understand how your symptoms are responding to treatment."
        
        # Default contextual response
        else:
            return f"Thank you for that additional information about your {primary_symptom}. This helps me better understand your situation."
    
    def _determine_next_questions(
        self,
        primary_symptom: str,
        gathered_info: Dict[str, bool],
        stage: str,
        message_lower: str
    ) -> List[str]:
        """Determine the next logical questions to ask"""
        
        questions = []
        
        # Priority questions based on symptom type
        if primary_symptom == "fever":
            if not gathered_info.get("temperature") and "temperature" not in message_lower:
                questions.append("Have you taken your temperature? If so, what was the reading?")
            elif not gathered_info.get("duration") and "started" not in message_lower:
                questions.append("When did your fever start?")
            elif "chills" not in message_lower and "aches" not in message_lower:
                questions.append("Are you experiencing chills, body aches, or sweating?")
            elif not gathered_info.get("medication"):
                questions.append("Have you taken any fever-reducing medication like acetaminophen or ibuprofen?")
        
        elif primary_symptom == "chest_pain":
            if "radiate" not in message_lower and "arm" not in message_lower:
                questions.append("Does the chest pain spread to your arm, neck, jaw, or back?")
            elif not gathered_info.get("severity"):
                questions.append("On a scale of 1-10, how severe is the chest pain?")
            elif "sharp" not in message_lower and "dull" not in message_lower:
                questions.append("Can you describe the type of pain - is it sharp, dull, crushing, or pressure-like?")
        
        elif primary_symptom == "breathing":
            if "rest" not in message_lower and "activity" not in message_lower:
                questions.append("Does the breathing difficulty occur at rest, with activity, or both?")
            elif "wheezing" not in message_lower:
                questions.append("Are you hearing any wheezing, whistling, or unusual sounds when breathing?")
            elif "position" not in message_lower:
                questions.append("Does sitting up or changing position help with your breathing?")
        
        elif primary_symptom == "headache":
            if "location" not in message_lower and "where" not in message_lower:
                questions.append("Where exactly is the headache located - front, back, sides, or all over?")
            elif "throbbing" not in message_lower and "sharp" not in message_lower:
                questions.append("Is the headache throbbing, sharp, dull, or more like pressure?")
            elif "light" not in message_lower and "sound" not in message_lower:
                questions.append("Are you sensitive to light or sound?")
        
        # General follow-up questions
        if not questions:
            if not gathered_info.get("severity"):
                questions.append("How would you rate your symptoms on a scale of 1-10?")
            elif not gathered_info.get("duration"):
                questions.append("When did these symptoms first start?")
            elif not gathered_info.get("medication"):
                questions.append("Are you currently taking any medications for this or other conditions?")
            else:
                questions.append("Is there anything else about your symptoms you'd like to discuss?")
        
        return questions[:3]  # Return top 3 questions
    
    def _extract_symptoms_from_text(self, text: str) -> List[str]:
        """Extract symptoms from text"""
        
        symptoms = []
        symptom_keywords = {
            "fever": ["fever", "temperature", "hot"],
            "chest_pain": ["chest pain", "chest hurt"],
            "breathing": ["breathing", "breath", "shortness"],
            "headache": ["headache", "head hurt"],
            "nausea": ["nausea", "vomiting"],
            "pain": ["pain", "hurt", "ache"],
            "fatigue": ["tired", "fatigue", "exhausted"]
        }
        
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in text for keyword in keywords):
                symptoms.append(symptom)
        
        return symptoms
    
    def _load_conversation_templates(self) -> Dict[str, Any]:
        """Load conversation templates for different symptoms and urgency levels"""
        
        return {
            "fever": {
                "emergency": {
                    "initial": "A high fever can be serious, especially if it's very high or accompanied by other concerning symptoms. Please seek immediate medical attention.",
                    "questions": {
                        "initial": [
                            "What is your current temperature?",
                            "Are you having difficulty breathing or chest pain?",
                            "Do you have severe headache or neck stiffness?"
                        ]
                    }
                },
                "urgent": {
                    "initial": "A fever indicates your body is fighting an infection. Let me gather some information to help determine the best course of action.",
                    "questions": {
                        "initial": [
                            "Have you taken your temperature? What was the reading?",
                            "When did your fever start?",
                            "Are you experiencing chills, body aches, or sweating?"
                        ]
                    }
                },
                "routine": {
                    "initial": "I understand you're feeling feverish. Let's gather some information about your symptoms.",
                    "questions": {
                        "initial": [
                            "Have you taken your temperature?",
                            "When did you first notice feeling feverish?",
                            "Any other symptoms like body aches or chills?"
                        ]
                    }
                }
            },
            "chest_pain": {
                "emergency": {
                    "initial": "Chest pain can be a medical emergency. Please call 911 or go to the nearest emergency room immediately.",
                    "questions": {
                        "initial": [
                            "Are you having difficulty breathing?",
                            "Does the pain radiate to your arm, neck, or jaw?",
                            "On a scale of 1-10, how severe is the pain?"
                        ]
                    }
                },
                "urgent": {
                    "initial": "Chest pain should be evaluated promptly. Let me gather some important information.",
                    "questions": {
                        "initial": [
                            "Can you describe the type of pain - sharp, dull, or crushing?",
                            "Does the pain spread to other areas?",
                            "When did the chest pain start?"
                        ]
                    }
                },
                "routine": {
                    "initial": "I understand you're experiencing chest discomfort. Let's learn more about what you're feeling.",
                    "questions": {
                        "initial": [
                            "Can you describe the chest discomfort?",
                            "What makes it better or worse?",
                            "When did you first notice it?"
                        ]
                    }
                }
            },
            "general": {
                "emergency": {
                    "initial": "Based on your symptoms, this may require immediate medical attention. Please consider calling 911 or going to the emergency room.",
                    "questions": {
                        "initial": [
                            "Are your symptoms getting worse right now?",
                            "Are you having trouble breathing?",
                            "On a scale of 1-10, how severe are your symptoms?"
                        ]
                    }
                },
                "urgent": {
                    "initial": "I understand you're experiencing concerning symptoms. Let me help assess your situation.",
                    "questions": {
                        "initial": [
                            "When did your symptoms first start?",
                            "How severe are they on a scale of 1-10?",
                            "Have you taken any medication for this?"
                        ]
                    }
                },
                "routine": {
                    "initial": "Thank you for sharing your symptoms with me. Let's gather some information to better understand your situation.",
                    "questions": {
                        "initial": [
                            "When did you first notice these symptoms?",
                            "How are they affecting your daily activities?",
                            "Have you experienced anything like this before?"
                        ]
                    }
                }
            }
        }
    
    def _load_question_flows(self) -> Dict[str, Any]:
        """Load question flow patterns for different symptoms"""
        
        return {
            "fever": [
                "temperature_reading",
                "duration",
                "associated_symptoms",
                "medication_status",
                "severity_impact"
            ],
            "chest_pain": [
                "pain_description",
                "radiation_pattern",
                "severity_scale",
                "duration",
                "triggers"
            ],
            "breathing": [
                "rest_vs_activity",
                "sound_quality",
                "position_effect",
                "duration",
                "associated_symptoms"
            ],
            "headache": [
                "location",
                "pain_type",
                "light_sound_sensitivity",
                "severity",
                "triggers"
            ]
        }
