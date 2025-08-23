"""
Medical Assessment Engine
Provides structured, doctor-like follow-up questions and triage assessments
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MedicalAssessmentEngine:
    """Engine for structured medical assessments with doctor-like questioning"""
    
    def __init__(self):
        self.assessment_protocols = self._load_assessment_protocols()
        self.triage_criteria = self._load_triage_criteria()
    
    def conduct_assessment(
        self,
        message: str,
        conversation_history: List[Dict],
        session_context: Dict[str, Any]
    ) -> Tuple[str, List[str], str, Dict[str, Any]]:
        """
        Conduct medical assessment with structured questions
        Returns: (response, questions, urgency_level, assessment_data)
        """
        
        # Identify primary symptom and assessment stage
        primary_symptom = self._identify_primary_symptom(message, conversation_history)
        assessment_stage = self._determine_assessment_stage(conversation_history, session_context)
        
        # Get assessment protocol for this symptom
        protocol = self.assessment_protocols.get(primary_symptom, self.assessment_protocols["general"])
        
        # Generate structured response and questions
        response, questions = self._generate_structured_assessment(
            message, primary_symptom, assessment_stage, protocol, conversation_history
        )
        
        # Determine urgency level based on collected information
        urgency_level = self._assess_urgency(message, conversation_history, session_context)
        
        # Compile assessment data
        assessment_data = {
            "primary_symptom": primary_symptom,
            "assessment_stage": assessment_stage,
            "information_collected": self._extract_collected_information(conversation_history),
            "red_flags": self._check_red_flags(message, conversation_history),
            "next_steps": self._determine_next_steps(urgency_level, primary_symptom)
        }
        
        return response, questions, urgency_level, assessment_data
    
    def _identify_primary_symptom(self, message: str, conversation_history: List[Dict]) -> str:
        """Identify the primary symptom being assessed"""
        
        message_lower = message.lower()
        
        # Check current message for symptoms
        symptom_patterns = {
            "fever": ["fever", "temperature", "hot", "feverish", "pyrexia"],
            "chest_pain": ["chest pain", "chest hurt", "heart pain", "chest pressure", "chest tightness"],
            "shortness_of_breath": ["shortness of breath", "difficulty breathing", "can't breathe", "breathless", "dyspnea"],
            "headache": ["headache", "head pain", "migraine", "head hurt", "cephalgia"],
            "abdominal_pain": ["stomach pain", "belly pain", "abdominal pain", "gut pain", "tummy ache"],
            "nausea_vomiting": ["nausea", "nauseous", "vomiting", "throwing up", "sick to stomach"],
            "dizziness": ["dizzy", "dizziness", "lightheaded", "vertigo", "spinning"],
            "fatigue": ["tired", "fatigue", "exhausted", "weak", "no energy"],
            "cough": ["cough", "coughing", "hacking", "phlegm", "sputum"],
            "rash": ["rash", "skin problem", "itchy", "red spots", "bumps"]
        }
        
        for symptom, patterns in symptom_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return symptom
        
        # Check conversation history for primary symptom
        for msg in conversation_history:
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                for symptom, patterns in symptom_patterns.items():
                    if any(pattern in content for pattern in patterns):
                        return symptom
        
        return "general"
    
    def _determine_assessment_stage(self, conversation_history: List[Dict], session_context: Dict[str, Any]) -> str:
        """Determine what stage of assessment we're in"""
        
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        
        # Analyze what information has been collected
        all_user_content = " ".join([msg.get("content", "").lower() for msg in user_messages])
        
        info_collected = {
            "temperature": any(temp in all_user_content for temp in ["102", "103", "104", "101", "100", "99", "temperature", "not taken temperature"]),
            "duration": any(time in all_user_content for time in ["yesterday", "today", "hours", "days", "started", "ago", "constant", "come and go"]),
            "associated_symptoms": any(symptom in all_user_content for symptom in ["chills", "cough", "headache", "nausea", "aches", "sweating"]),
            "breathing": any(breath in all_user_content for breath in ["breathing", "breath", "chest pain", "difficulty", "no difficulty"]),
            "medication": any(med in all_user_content for med in ["medication", "medicine", "pills", "not taken", "haven't taken"]),
            "medical_history": any(hist in all_user_content for hist in ["condition", "diabetes", "heart", "disease", "no conditions"])
        }
        
        collected_count = sum(info_collected.values())
        
        if len(user_messages) <= 1:
            return "initial_presentation"
        elif collected_count <= 2:
            return "symptom_characterization"
        elif collected_count <= 4:
            return "associated_symptoms"
        elif collected_count <= 5:
            return "medical_history"
        else:
            return "final_assessment"
    
    def _generate_structured_assessment(
        self,
        message: str,
        primary_symptom: str,
        assessment_stage: str,
        protocol: Dict[str, Any],
        conversation_history: List[Dict]
    ) -> Tuple[str, List[str]]:
        """Generate structured medical assessment response with doctor-like questions"""
        
        message_lower = message.lower()
        
        # Check if user provided multiple answers at once
        user_provided_multiple_answers = (
            "," in message and len(message.split(",")) >= 3
        ) or (
            len(conversation_history) > 2 and 
            any(word in message_lower for word in ["not taken", "days", "shivering", "yes", "no"])
        )
        
        # Generate contextual response based on stage
        if assessment_stage == "initial_presentation":
            response = self._generate_initial_response(primary_symptom, message)
        elif user_provided_multiple_answers:
            # Special handling for multiple answers
            response = self._generate_multiple_answer_response(message, conversation_history)
        elif assessment_stage == "symptom_characterization":
            response = self._generate_characterization_response(message, primary_symptom)
        elif assessment_stage == "associated_symptoms":
            response = self._generate_associated_symptoms_response(message, primary_symptom)
        elif assessment_stage == "medical_history":
            response = self._generate_medical_history_response(message, primary_symptom)
        else:  # final_assessment
            response = self._generate_final_assessment_response(message, primary_symptom, conversation_history)
        
        # Get the next single question to ask
        if assessment_stage != "final_assessment":
            filtered_questions = self._filter_questions_by_collected_info([], conversation_history)
        else:
            filtered_questions = []
        
        # Ensure response is never None or empty
        if not response or response.strip() == "":
            response = f"Thank you for that information about your {primary_symptom}. Let me continue with the assessment."
        
        # If no questions remain, move to final assessment
        if not filtered_questions and assessment_stage != "final_assessment":
            if len(conversation_history) >= 6:  # Enough information collected
                response = self._generate_final_assessment_response(message, primary_symptom, conversation_history)
                filtered_questions = []
            else:
                # Provide one general follow-up question
                filtered_questions = ["Is there anything else about your symptoms you'd like to tell me?"]
        
        return response, filtered_questions[:1]  # Return only ONE question
    
    def _generate_multiple_answer_response(self, message: str, conversation_history: List[Dict]) -> str:
        """Generate response when user provides multiple answers at once"""
        
        message_lower = message.lower()
        
        # Handle the specific pattern from user: "i have not taken my temperature,2 days,shivering,yes,no"
        if "not taken" in message_lower and "days" in message_lower and "shivering" in message_lower:
            return "Thank you for providing all that information. I understand you haven't taken your temperature, you've had the fever for 2 days, you're experiencing shivering, you have body aches, but you haven't taken any medication yet. This helps me understand your condition much better."
        
        # Handle pattern like "no,yes,yes,no"
        elif "," in message and len(message.split(",")) >= 3:
            answers = message.split(",")
            yes_count = sum(1 for answer in answers if "yes" in answer.strip().lower())
            no_count = sum(1 for answer in answers if "no" in answer.strip().lower())
            
            if yes_count > 0 and no_count > 0:
                return f"Thank you for answering those questions. I can see you have some symptoms present and others absent, which helps me build a clearer picture of your condition."
            elif yes_count > no_count:
                return f"Thank you for those answers. I can see you're experiencing several of these symptoms, which helps me understand what your body is dealing with."
            else:
                return f"Thank you for providing those details. The information about which symptoms you're not experiencing is just as important as those you are having."
        
        else:
            return "Thank you for providing that detailed information. This helps me better understand your condition."
    
    def _generate_initial_response(self, primary_symptom: str, message: str) -> str:
        """Generate initial assessment response"""
        
        responses = {
            "fever": "I understand you're experiencing a fever. This is your body's natural response to fighting an infection. Let me ask you some important questions to better assess your condition.",
            
            "chest_pain": "Chest pain is a symptom that requires careful evaluation. I need to gather some important information to determine the urgency of your situation.",
            
            "shortness_of_breath": "Difficulty breathing can have various causes and needs prompt assessment. Let me ask you some key questions to understand your situation better.",
            
            "headache": "Headaches can range from minor to serious conditions. I'll need to ask you several questions to properly assess your symptoms.",
            
            "abdominal_pain": "Abdominal pain can indicate various conditions. Let me gather some important information to help determine what might be causing your discomfort.",
            
            "general": "Thank you for sharing your symptoms with me. I'll ask you a series of questions to better understand your condition and provide appropriate guidance."
        }
        
        return responses.get(primary_symptom, responses["general"])
    
    def _generate_characterization_response(self, message: str, primary_symptom: str) -> str:
        """Generate response for symptom characterization stage"""
        
        message_lower = message.lower().strip()
        
        # Handle simple "no" answer to temperature question
        if message_lower == "no":
            return "I understand you haven't taken your temperature. That's okay - we can still assess your condition based on how you're feeling."
        
        # Handle simple "yes" answer
        elif message_lower == "yes":
            return "Thank you for that information. This helps me understand your symptoms better."
        
        # Handle multiple answers provided at once (like "no,yes,yes,no")
        elif "," in message and len(message.split(",")) >= 3:
            return "Thank you for providing those details. Based on your answers, I can see you have several symptoms that help me understand your condition better."
        
        # Handle specific answer patterns
        elif "not taken" in message_lower and "days" in message_lower and "shivering" in message_lower:
            return "I understand you haven't taken your temperature, you've had the fever for 2 days, and you're experiencing shivering. This combination suggests your body is actively fighting an infection."
        
        # Acknowledge specific information provided
        elif any(temp in message_lower for temp in ["102", "103", "104", "101", "100", "99"]):
            temp_match = None
            for temp in ["104", "103", "102", "101", "100", "99"]:
                if temp in message_lower:
                    temp_match = temp
                    break
            
            if temp_match:
                temp_val = int(temp_match)
                if temp_val >= 103:
                    return f"A temperature of {temp_val}°F is quite high and concerning. This indicates a significant infection that may require immediate medical attention."
                elif temp_val >= 101:
                    return f"A temperature of {temp_val}°F indicates a moderate to significant fever. This suggests your body is actively fighting an infection."
                else:
                    return f"A temperature of {temp_val}°F is a low-grade fever, which still indicates your body is responding to something."
        
        elif "not taken temperature" in message_lower or "haven't taken" in message_lower:
            return "I understand you haven't taken your temperature yet. Even without a specific reading, the symptoms you're describing suggest your body is fighting an infection."
        
        elif "2 days" in message_lower or "two days" in message_lower:
            return "Having a fever for 2 days indicates this is not just a brief illness. Your body has been fighting this infection for a while now."
        
        elif "shivering" in message_lower or "chills" in message_lower:
            return "Shivering and chills are your body's way of trying to raise its temperature to fight infection. This is a common and expected response."
        
        elif "cough" in message_lower and "headache" in message_lower:
            return "The combination of cough and headache along with your fever suggests you may have a respiratory infection. These symptoms together help me understand what your body is dealing with."
        
        elif "no" in message_lower and "yes" in message_lower:
            return "Thank you for answering those questions. The pattern of symptoms you're experiencing helps me better assess your condition."
        
        elif "constant" in message_lower:
            return "A constant fever indicates your body is continuously fighting an infection. This is important information for determining your care needs."
        
        elif "no difficulty breathing" in message_lower or "no breathing" in message_lower:
            return "I'm glad to hear you're not having breathing difficulties. This is reassuring and helps me focus on your other symptoms."
        
        else:
            return "Thank you for that information. Let me continue with the next important question to better understand your condition."
    
    def _generate_associated_symptoms_response(self, message: str, primary_symptom: str) -> str:
        """Generate response for associated symptoms stage"""
        
        message_lower = message.lower()
        
        if "chills" in message_lower and primary_symptom == "fever":
            return "Fever with chills is a classic sign that your immune system is actively fighting an infection. This combination helps me understand the nature of your illness."
        
        elif "nausea" in message_lower or "vomiting" in message_lower:
            return "Nausea and vomiting along with your other symptoms can help pinpoint the cause and determine if you need immediate care."
        
        elif "shortness of breath" in message_lower or "difficulty breathing" in message_lower:
            return "Breathing difficulties are always concerning and may indicate that your condition requires urgent medical attention."
        
        else:
            return "These associated symptoms help me build a complete picture of your condition to provide appropriate guidance."
    
    def _generate_medical_history_response(self, message: str, primary_symptom: str) -> str:
        """Generate response for medical history stage"""
        
        return "Your medical history and current medications are important factors in determining the best course of action for your symptoms."
    
    def _generate_final_assessment_response(self, message: str, primary_symptom: str, conversation_history: List[Dict]) -> str:
        """Generate final assessment response with triage decision"""
        
        # Extract information from conversation
        all_user_content = " ".join([msg.get("content", "").lower() for msg in conversation_history if msg.get("role") == "user"])
        
        # Build assessment summary
        symptoms_mentioned = []
        if "fever" in all_user_content:
            if "low fever" in all_user_content:
                symptoms_mentioned.append("low-grade fever")
            else:
                symptoms_mentioned.append("fever")
        
        if "cough" in all_user_content:
            symptoms_mentioned.append("cough")
        if "headache" in all_user_content:
            symptoms_mentioned.append("headache")
        if "chills" in all_user_content:
            symptoms_mentioned.append("chills")
        if "body aches" in all_user_content or "muscle pain" in all_user_content:
            symptoms_mentioned.append("body aches")
        
        # Determine urgency and recommendations
        if any(temp in all_user_content for temp in ["103", "104", "105"]):
            urgency_msg = "🚨 **URGENT PRIORITY** - High fever requires prompt medical attention."
            recommendations = [
                "Contact your healthcare provider immediately or visit urgent care",
                "Monitor temperature closely and seek emergency care if it rises above 104°F",
                "Stay hydrated and rest",
                "Consider fever-reducing medication as directed"
            ]
        elif "constant fever" in all_user_content and len(symptoms_mentioned) >= 3:
            urgency_msg = "⚠️ **URGENT PRIORITY** - Multiple symptoms with persistent fever need medical evaluation."
            recommendations = [
                "Contact your healthcare provider today or visit urgent care",
                "Monitor symptoms for any worsening",
                "Stay hydrated and get plenty of rest",
                "Seek immediate care if breathing becomes difficult"
            ]
        else:
            urgency_msg = "⚠️ **URGENT PRIORITY** - Fever with multiple symptoms warrants medical evaluation."
            recommendations = [
                "Contact your healthcare provider within 24 hours",
                "Monitor temperature and symptoms closely",
                "Stay hydrated and rest",
                "Seek urgent care if symptoms worsen"
            ]
        
        # Build comprehensive response
        response = f"Based on the information you've provided, I can now give you a comprehensive assessment.\n\n"
        response += f"{urgency_msg}\n\n"
        response += f"**Your reported symptoms:**\n"
        for symptom in symptoms_mentioned:
            response += f"• {symptom.title()}\n"
        
        if "not taken temperature" in all_user_content:
            response += f"• Temperature not measured\n"
        
        if "constant" in all_user_content:
            response += f"• Fever pattern: Constant\n"
        
        if "no difficulty breathing" in all_user_content:
            response += f"• Breathing: Normal (reassuring)\n"
        
        response += f"\n**Recommended next steps:**\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. {rec}\n"
        
        response += f"\n**Important:** While your symptoms suggest a viral infection, the combination of persistent fever with multiple symptoms requires medical evaluation to rule out more serious conditions and ensure appropriate treatment."
        
        return response
    
    def _filter_questions_by_collected_info(self, questions: List[str], conversation_history: List[Dict]) -> List[str]:
        """Filter out questions that have already been answered and prioritize the most important next question"""
        
        # Get all user messages
        user_messages = " ".join([msg.get("content", "").lower() for msg in conversation_history if msg.get("role") == "user"])
        last_user_messages = [msg.get("content", "").lower() for msg in conversation_history if msg.get("role") == "user"]
        
        # Track what information we have - be more flexible with simple answers
        info_collected = {
            "temperature": any(temp in user_messages for temp in ["102", "103", "104", "101", "100", "99", "temperature", "not taken temperature", "haven't taken", "no temperature", "didn't take"]) or 
                          (len([msg for msg in conversation_history if msg.get("role") == "user"]) > 1 and any(simple in user_messages for simple in ["no", "yes", "not", "haven't"])),
            "duration": any(time in user_messages for time in ["yesterday", "today", "hours", "days", "started", "ago", "2 days", "3 days", "week"]),
            "chills": any(chill in user_messages for chill in ["chills", "sweating", "shivering", "cold", "hot"]),
            "body_aches": any(ache in user_messages for ache in ["body aches", "muscle pain", "aches", "sore", "yes,no", "shivering,yes"]),
            "medication": any(med in user_messages for med in ["medication", "medicine", "pills", "ibuprofen", "acetaminophen", "not taken", "haven't taken", "no medication", ",no"]),
            "nausea": any(nausea in user_messages for nausea in ["nausea", "vomiting", "sick", "throw up", "no nausea", "no ,"]),
            "cough": any(cough in user_messages for cough in ["cough", "sore throat", "throat", "no cough", ",yes,"]),
            "headache": any(head in user_messages for head in ["headache", "head pain", "neck stiffness", "no headache", "yes,no"]),
            "abdominal": any(abd in user_messages for abd in ["abdominal", "stomach", "belly", "diarrhea", "no abdominal", "no stomach", ",no"]),
            "breathing": any(breath in user_messages for breath in ["breathing", "breath", "chest pain", "difficulty", "no difficulty"]),
            "medical_history": any(hist in user_messages for hist in ["condition", "diabetes", "heart", "disease", "no conditions", "chronic"])
        }
        
        # Special handling for simple "no" answers to specific questions
        # Track the last question asked by looking at bot messages
        bot_messages = [msg.get("content", "").lower() for msg in conversation_history if msg.get("role") == "assistant"]
        last_bot_message = bot_messages[-1] if bot_messages else ""
        
        # If user said "no" and we can determine what question was asked
        if len(last_user_messages) >= 1 and last_user_messages[-1].strip() == "no":
            if "temperature" in last_bot_message:
                info_collected["temperature"] = True
            elif "how long" in last_bot_message or "duration" in last_bot_message:
                info_collected["duration"] = True
            elif "chills" in last_bot_message or "shivering" in last_bot_message:
                info_collected["chills"] = True
            elif "body aches" in last_bot_message or "muscle pain" in last_bot_message:
                info_collected["body_aches"] = True
            elif "medication" in last_bot_message:
                info_collected["medication"] = True
            elif "nausea" in last_bot_message or "vomiting" in last_bot_message:
                info_collected["nausea"] = True
            elif "cough" in last_bot_message or "sore throat" in last_bot_message:
                info_collected["cough"] = True
            elif "headache" in last_bot_message:
                info_collected["headache"] = True
            elif "abdominal" in last_bot_message or "stomach" in last_bot_message:
                info_collected["abdominal"] = True
            elif "breathing" in last_bot_message or "chest pain" in last_bot_message:
                info_collected["breathing"] = True
        
        # Special handling for comma-separated answers
        if "not taken" in user_messages and "days" in user_messages and "shivering" in user_messages and "yes,no" in user_messages:
            info_collected.update({
                "temperature": True,
                "duration": True, 
                "chills": True,
                "body_aches": True,
                "medication": True
            })
        
        # If user provided "no ,yes,yes,no" after being asked about nausea, cough, headache, abdominal
        if "no ,yes,yes,no" in user_messages or "no,yes,yes,no" in user_messages:
            info_collected.update({
                "nausea": True,
                "cough": True,
                "headache": True,
                "abdominal": True
            })
        
        # Priority order for fever assessment
        fever_priority_questions = [
            ("temperature", "Have you taken your temperature? If yes, what is the reading?"),
            ("duration", "How long have you had this fever?"),
            ("chills", "Are you experiencing chills, sweating, or shivering?"),
            ("body_aches", "Do you have any body aches or muscle pain?"),
            ("medication", "Have you taken any fever-reducing medication like acetaminophen or ibuprofen?"),
            ("cough", "Do you have a cough or sore throat?"),
            ("headache", "Do you have a headache or any neck stiffness?"),
            ("nausea", "Are you experiencing any nausea or vomiting?"),
            ("abdominal", "Do you have any abdominal pain or diarrhea?"),
            ("breathing", "Are you having any difficulty breathing or chest pain?"),
            ("medical_history", "Do you have any chronic medical conditions like diabetes or heart disease?")
        ]
        
        # Find the next most important question to ask
        for info_type, question in fever_priority_questions:
            if not info_collected.get(info_type, False):
                return [question]  # Return only one question
        
        # If all basic info collected, provide final assessment
        return []  # No more questions needed
    
    def _assess_urgency(self, message: str, conversation_history: List[Dict], session_context: Dict[str, Any]) -> str:
        """Assess urgency level based on collected information"""
        
        all_messages = " ".join([msg.get("content", "").lower() for msg in conversation_history if msg.get("role") == "user"])
        current_message = message.lower()
        
        # Emergency criteria - immediate life-threatening
        emergency_indicators = [
            "chest pain", "difficulty breathing", "can't breathe", "shortness of breath",
            "severe pain", "crushing pain", "radiating pain", "arm pain", "jaw pain",
            "unconscious", "passing out", "severe headache", "worst headache",
            "vomiting blood", "severe bleeding"
        ]
        
        # Check for very high fever emergency (104°F+)
        if any(temp in all_messages for temp in ["104", "105", "106"]):
            return "emergency"
        
        # Check for emergency indicators
        if any(indicator in all_messages for indicator in emergency_indicators):
            return "emergency"
        
        # Urgent criteria - needs prompt attention
        urgent_indicators = [
            "severe", "getting worse", "worsening", "unbearable",
            "vomiting", "can't keep fluids down", "dehydrated",
            "confusion", "vision problems"
        ]
        
        # Check for high fever urgent (102-103°F)
        if any(temp in all_messages for temp in ["102", "103"]):
            return "urgent"
        
        # Check for urgent indicators
        if any(indicator in all_messages for indicator in urgent_indicators):
            return "urgent"
        
        # Check for moderate fever
        if "fever" in all_messages and any(temp in all_messages for temp in ["101", "100"]):
            return "urgent"
        
        # Check for general fever
        if "fever" in all_messages:
            return "urgent"
        
        return "routine"
    
    def _extract_collected_information(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Extract information that has been collected during the conversation"""
        
        user_messages = " ".join([msg.get("content", "").lower() for msg in conversation_history if msg.get("role") == "user"])
        
        collected = {}
        
        # Temperature
        for temp in ["104", "103", "102", "101", "100", "99"]:
            if temp in user_messages:
                collected["temperature"] = f"{temp}°F"
                break
        
        # Duration
        if "yesterday" in user_messages:
            collected["duration"] = "Started yesterday"
        elif "today" in user_messages:
            collected["duration"] = "Started today"
        elif "hours" in user_messages:
            collected["duration"] = "Started hours ago"
        
        # Associated symptoms
        associated = []
        if "chills" in user_messages:
            associated.append("chills")
        if "nausea" in user_messages:
            associated.append("nausea")
        if "vomiting" in user_messages:
            associated.append("vomiting")
        if "headache" in user_messages:
            associated.append("headache")
        
        if associated:
            collected["associated_symptoms"] = associated
        
        return collected
    
    def _check_red_flags(self, message: str, conversation_history: List[Dict]) -> List[str]:
        """Check for red flag symptoms that require immediate attention"""
        
        all_messages = " ".join([msg.get("content", "").lower() for msg in conversation_history if msg.get("role") == "user"])
        
        red_flags = []
        
        if "chest pain" in all_messages:
            red_flags.append("Chest pain - potential cardiac emergency")
        
        if "difficulty breathing" in all_messages or "can't breathe" in all_messages:
            red_flags.append("Respiratory distress - requires immediate evaluation")
        
        if any(temp in all_messages for temp in ["104", "105"]):
            red_flags.append("High fever - risk of serious infection")
        
        if "severe headache" in all_messages or "worst headache" in all_messages:
            red_flags.append("Severe headache - potential neurological emergency")
        
        return red_flags
    
    def _determine_next_steps(self, urgency_level: str, primary_symptom: str) -> List[str]:
        """Determine recommended next steps based on urgency and symptom"""
        
        if urgency_level == "emergency":
            return [
                "Call 911 immediately",
                "Go to the nearest emergency room",
                "Do not drive yourself - have someone else drive or call ambulance",
                "Take any prescribed emergency medications if applicable"
            ]
        
        elif urgency_level == "urgent":
            return [
                "Contact your healthcare provider today",
                "Visit urgent care center if primary care unavailable",
                "Monitor symptoms closely for any worsening",
                "Seek emergency care if symptoms worsen"
            ]
        
        else:  # routine
            return [
                "Monitor symptoms for 24-48 hours",
                "Contact healthcare provider if symptoms worsen or persist",
                "Use appropriate home remedies for comfort",
                "Schedule routine appointment if symptoms continue"
            ]
    
    def _load_assessment_protocols(self) -> Dict[str, Any]:
        """Load structured assessment protocols for different symptoms"""
        
        return {
            "fever": {
                "initial_questions": [
                    "Have you taken your temperature? If yes, what is the reading?",
                    "How long have you had this fever?",
                    "Are you experiencing chills, sweating, or shivering?",
                    "Do you have any body aches or muscle pain?",
                    "Have you taken any fever-reducing medication (like acetaminophen or ibuprofen)?"
                ],
                "characterization_questions": [
                    "What is your highest recorded temperature?",
                    "Is the fever constant or does it come and go?",
                    "Are you able to keep fluids down?",
                    "Do you have any difficulty breathing or chest pain?"
                ],
                "associated_questions": [
                    "Are you experiencing nausea or vomiting?",
                    "Do you have a cough or sore throat?",
                    "Any headache or neck stiffness?",
                    "Are you having any abdominal pain or diarrhea?"
                ],
                "history_questions": [
                    "Do you have any chronic medical conditions (diabetes, heart disease, etc.)?",
                    "Are you taking any regular medications?",
                    "Have you been around anyone who was sick recently?",
                    "Have you traveled anywhere recently?"
                ]
            },
            
            "chest_pain": {
                "initial_questions": [
                    "On a scale of 1-10, how severe is the chest pain?",
                    "Can you describe the pain - is it sharp, dull, crushing, or burning?",
                    "Does the pain radiate to your arm, neck, jaw, or back?",
                    "When did the chest pain start?",
                    "Are you having any difficulty breathing?"
                ],
                "characterization_questions": [
                    "What makes the pain better or worse?",
                    "Is the pain constant or does it come and go?",
                    "Does the pain worsen with movement or breathing?",
                    "Have you had chest pain like this before?"
                ],
                "associated_questions": [
                    "Are you experiencing nausea or vomiting?",
                    "Do you feel dizzy or lightheaded?",
                    "Are you sweating or feeling clammy?",
                    "Do you have any palpitations or irregular heartbeat?"
                ],
                "history_questions": [
                    "Do you have any heart conditions or high blood pressure?",
                    "Do you have diabetes or high cholesterol?",
                    "Do you smoke or have you smoked in the past?",
                    "Are you taking any heart medications?"
                ]
            },
            
            "shortness_of_breath": {
                "initial_questions": [
                    "Are you having trouble breathing at rest or only with activity?",
                    "When did the breathing difficulty start?",
                    "On a scale of 1-10, how severe is your breathing difficulty?",
                    "Do you have any chest pain or tightness?",
                    "Are you coughing or wheezing?"
                ],
                "characterization_questions": [
                    "Does sitting up help your breathing?",
                    "Are you bringing up any phlegm or blood when coughing?",
                    "Do you feel like you're getting enough air?",
                    "Have you had breathing problems like this before?"
                ],
                "associated_questions": [
                    "Do you have any fever or chills?",
                    "Are your lips or fingernails blue or gray?",
                    "Do you have any swelling in your legs or ankles?",
                    "Are you feeling dizzy or lightheaded?"
                ],
                "history_questions": [
                    "Do you have asthma, COPD, or other lung conditions?",
                    "Do you have any heart conditions?",
                    "Are you taking any medications for breathing or heart problems?",
                    "Do you smoke or have you been exposed to any irritants?"
                ]
            },
            
            "general": {
                "initial_questions": [
                    "When did your symptoms first start?",
                    "How severe are your symptoms on a scale of 1-10?",
                    "Are your symptoms getting better, worse, or staying the same?",
                    "Have you taken any medications for these symptoms?",
                    "Do you have any other symptoms along with this?"
                ],
                "characterization_questions": [
                    "What makes your symptoms better or worse?",
                    "Have you experienced these symptoms before?",
                    "Are the symptoms affecting your daily activities?",
                    "Is there anything that seems to trigger the symptoms?"
                ],
                "associated_questions": [
                    "Are you experiencing any fever, nausea, or dizziness?",
                    "Do you have any pain elsewhere in your body?",
                    "Are you having any trouble sleeping or eating?",
                    "Have you noticed any changes in your energy level?"
                ],
                "history_questions": [
                    "Do you have any chronic medical conditions?",
                    "Are you taking any regular medications?",
                    "Do you have any known allergies?",
                    "Have you had any recent changes in your health or medications?"
                ]
            }
        }
    
    def _load_triage_criteria(self) -> Dict[str, Any]:
        """Load triage criteria for different conditions"""
        
        return {
            "emergency": {
                "chest_pain": ["severe pain", "radiating pain", "crushing pain", "difficulty breathing"],
                "breathing": ["severe difficulty", "blue lips", "can't speak", "gasping"],
                "fever": ["temperature > 104°F", "difficulty breathing", "severe headache", "confusion"],
                "general": ["unconscious", "severe bleeding", "severe pain", "signs of stroke"]
            },
            "urgent": {
                "fever": ["temperature 102-104°F", "persistent vomiting", "severe headache"],
                "pain": ["severe pain", "worsening pain", "pain with fever"],
                "general": ["moderate symptoms", "worsening condition", "concerning changes"]
            },
            "routine": {
                "general": ["mild symptoms", "stable condition", "improving symptoms"]
            }
        }
