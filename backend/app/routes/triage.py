from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json
import logging

from app.models.schemas import (
    TriageResult, ChatResponse, SymptomInput, ChatMessage, 
    UrgencyLevel, Language, SuccessResponse
)
from app.services.triage_service import TriageService
from app.services.triage_chat_service import TriageChatService
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
triage_service = TriageService()
triage_chat_service = TriageChatService()
translation_service = TranslationService()

# In-memory storage for chat sessions (use database in production)
chat_sessions: Dict[str, Dict[str, Any]] = {}

@router.post("/chat")
async def chat_with_triage_assistant(message: ChatMessage):
    """
    Enhanced chat with the virtual triage assistant using AI integrations.
    Integrates GROQ, Tavily, and Keyword AI for intelligent responses.
    """
    
    try:
        logger.info(f"Processing triage chat message: {message.message[:50]}...")
        
        # Process the message with AI integrations
        result = await triage_chat_service.process_chat_message(
            message=message.message,
            session_id=message.session_id or str(uuid.uuid4()),
            user_context=getattr(message, 'context', None)
        )
        
        # Format response for frontend with backward compatibility
        response = {
            "message": result["response"],
            "response": result["response"],  # Backward compatibility
            "session_id": result["session_id"],
            "urgency_level": result["urgency_level"],
            "extracted_symptoms": result.get("extracted_symptoms", []),
            "medical_keywords": result.get("medical_keywords", []),
            "follow_up_questions": result.get("assessment_questions", result.get("follow_up_questions", [])),
            "medical_resources": result.get("medical_resources", []),
            "conversation_length": result.get("conversation_length", 1),
            "timestamp": result.get("generated_at", datetime.utcnow().isoformat()),
            "ai_enhanced": result.get("ai_enhanced", True),
            "assessment_data": result.get("assessment_data", {})
        }
        
        logger.info(f"Triage chat response generated successfully - urgency: {result.get('urgency_level', 'unknown')}")
        return response
        
    except Exception as e:
        logger.error(f"Triage chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )

@router.get("/chat/session/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session summary and history."""
    
    try:
        session_summary = triage_chat_service.get_session_summary(session_id)
        
        if not session_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        return session_summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat session: {str(e)}"
        )

@router.post("/assess")
async def perform_triage_assessment(symptom_input: SymptomInput):
    """
    Perform triage assessment based on patient symptoms.
    Simplified version for development.
    """
    
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Mock triage analysis based on symptoms
        symptoms_lower = symptom_input.symptoms.lower()
        
        # Simple keyword-based urgency assessment
        if any(keyword in symptoms_lower for keyword in ["chest pain", "difficulty breathing", "severe", "emergency"]):
            urgency_level = "emergency"
            confidence = 0.8
            possible_conditions = [
                {
                    "name": "Chest Pain Syndrome",
                    "probability": 0.7,
                    "description": "Chest discomfort that may require immediate evaluation"
                }
            ]
            recommendations = [
                "Seek immediate medical attention",
                "Call emergency services if symptoms are severe",
                "Do not drive yourself to the hospital"
            ]
            next_steps = [
                "Call 911 or go to emergency room",
                "Take any prescribed heart medications",
                "Stay calm and avoid exertion"
            ]
        elif any(keyword in symptoms_lower for keyword in ["fever", "pain", "headache", "nausea"]):
            urgency_level = "urgent"
            confidence = 0.6
            possible_conditions = [
                {
                    "name": "Viral Syndrome",
                    "probability": 0.6,
                    "description": "Common viral infection with flu-like symptoms"
                }
            ]
            recommendations = [
                "Schedule appointment with healthcare provider",
                "Monitor symptoms for changes",
                "Stay hydrated and rest"
            ]
            next_steps = [
                "Contact your doctor within 24 hours",
                "Take over-the-counter medications as needed",
                "Monitor temperature and symptoms"
            ]
        else:
            urgency_level = "routine"
            confidence = 0.5
            possible_conditions = [
                {
                    "name": "Minor Symptoms",
                    "probability": 0.5,
                    "description": "Mild symptoms that may resolve on their own"
                }
            ]
            recommendations = [
                "Monitor symptoms for a few days",
                "Try home remedies and rest",
                "Contact doctor if symptoms worsen"
            ]
            next_steps = [
                "Continue self-care measures",
                "Schedule routine appointment if needed",
                "Watch for any worsening symptoms"
            ]
        
        result = {
            "analysis_id": analysis_id,
            "urgency_level": urgency_level,
            "confidence": confidence,
            "possible_conditions": possible_conditions,
            "recommendations": recommendations,
            "next_steps": next_steps,
            "red_flags": [],
            "estimated_wait_time": "Varies based on urgency",
            "care_level": f"{urgency_level.title()} Care"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Triage assessment failed: {str(e)}"
        )

@router.post("/chat")
async def chat_with_triage_assistant(message: ChatMessage):
    """
    Chat with the virtual triage assistant.
    Simplified version for development.
    """
    
    try:
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        # Mock chat response
        user_message = message.message.lower()
        
        if any(keyword in user_message for keyword in ["pain", "hurt", "ache"]):
            response = "I understand you're experiencing pain. Can you describe where the pain is located and rate it on a scale of 1-10?"
            follow_up_questions = [
                "Where exactly is the pain located?",
                "How would you rate the pain from 1-10?",
                "When did the pain start?"
            ]
        elif any(keyword in user_message for keyword in ["fever", "temperature", "hot"]):
            response = "Fever can be a sign of infection. Have you taken your temperature? Any other symptoms like chills or body aches?"
            follow_up_questions = [
                "What is your current temperature?",
                "Do you have any chills or body aches?",
                "How long have you had the fever?"
            ]
        else:
            response = "Thank you for sharing that information. Can you tell me more about your symptoms and when they started?"
            follow_up_questions = [
                "When did your symptoms first start?",
                "Have you tried any treatments so far?",
                "Do you have any other symptoms?"
            ]
        
        chat_response = {
            "response": response,
            "follow_up_questions": follow_up_questions,
            "session_id": session_id,
            "urgency_update": None,
            "additional_info_needed": []
        }
        
        return chat_response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )

@router.get("/emergency-guidelines")
async def get_emergency_guidelines():
    """Get emergency guidelines and when to seek immediate care."""
    
    return {
        "emergency_signs": [
            "Chest pain or pressure",
            "Difficulty breathing or shortness of breath",
            "Severe bleeding that won't stop",
            "Signs of stroke (face drooping, arm weakness, speech difficulty)",
            "Loss of consciousness",
            "Severe allergic reaction"
        ],
        "when_to_call_911": [
            "Life-threatening emergency",
            "Severe injury or illness",
            "Person is unconscious",
            "Severe difficulty breathing",
            "Chest pain with sweating or nausea"
        ],
        "urgent_care_situations": [
            "High fever (over 103°F/39.4°C)",
            "Persistent vomiting or diarrhea",
            "Severe pain",
            "Suspected fracture",
            "Deep cuts that may need stitches"
        ]
    }

@router.post("/assess", response_model=TriageResult)
async def perform_triage_assessment(
    symptom_input: SymptomInput
):
    """
    Perform comprehensive triage assessment based on patient symptoms.
    
    Analyzes symptoms using AI and provides urgency level, possible conditions,
    and recommendations tailored to user role and language.
    """
    
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Translate symptoms to English if needed for AI processing
        symptoms_for_ai = symptom_input.symptoms
        if symptom_input.language != Language.EN:
            symptoms_for_ai = await translation_service.translate_text(
                symptom_input.symptoms, "en"
            )
        
        # Prepare context for AI analysis
        context = {
            "symptoms": symptoms_for_ai,
            "duration": symptom_input.duration,
            "severity_self_assessment": symptom_input.severity_self_assessment,
            "age": symptom_input.age,
            "gender": symptom_input.gender,
            "medical_history": symptom_input.medical_history,
            "current_medications": symptom_input.current_medications,
            "user_role": "patient"
        }
        
        # Run AI triage analysis
        ai_analysis = await triage_service.analyze_symptoms(context)
        
        # Determine urgency level
        urgency_level = await _determine_urgency_level(ai_analysis, context)
        
        # Generate possible conditions
        possible_conditions = await _generate_possible_conditions(
            ai_analysis, context, "patient"
        )
        
        # Generate recommendations and next steps
        recommendations, next_steps = await _generate_triage_recommendations(
            urgency_level, possible_conditions, context, "patient"
        )
        
        # Identify red flags
        red_flags = await _identify_red_flags(ai_analysis, context)
        
        # Estimate appropriate wait time and care level
        estimated_wait_time, care_level = await _determine_care_requirements(
            urgency_level, possible_conditions
        )
        
        # Translate results if needed
        if symptom_input.language != Language.EN:
            recommendations = await translation_service.translate_list(
                recommendations, symptom_input.language.value
            )
            next_steps = await translation_service.translate_list(
                next_steps, symptom_input.language.value
            )
            red_flags = await translation_service.translate_list(
                red_flags, symptom_input.language.value
            )
            
            # Translate condition descriptions
            for condition in possible_conditions:
                if "description" in condition:
                    condition["description"] = await translation_service.translate_text(
                        condition["description"], symptom_input.language.value
                    )
        
        # Create triage result
        result = TriageResult(
            analysis_id=analysis_id,
            urgency_level=urgency_level,
            confidence=ai_analysis.get("confidence", 0.7),
            possible_conditions=possible_conditions,
            recommendations=recommendations,
            next_steps=next_steps,
            red_flags=red_flags,
            estimated_wait_time=estimated_wait_time,
            care_level=care_level
        )
        
        # Store triage result
        await _store_triage_result(analysis_id, result, symptom_input, None)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Triage assessment failed: {str(e)}"
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_triage_assistant(
    message: ChatMessage,
    session_id: Optional[str] = Query(None, description="Chat session ID")
):
    """
    Interactive chat with the virtual triage assistant.
    
    Maintains conversation context and provides follow-up questions
    and updated assessments based on additional information.
    """
    
    try:
        # Create or retrieve chat session
        if not session_id:
            session_id = str(uuid.uuid4())
            chat_sessions[session_id] = {
                "user_id": "anonymous",
                "created_at": datetime.utcnow(),
                "messages": [],
                "current_assessment": None,
                "language": message.language
            }
        
        session = chat_sessions.get(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Add user message to session
        session["messages"].append({
            "role": "user",
            "content": message.message,
            "timestamp": datetime.utcnow().isoformat(),
            "context": message.context
        })
        
        # Translate message to English if needed for AI processing
        message_for_ai = message.message
        if message.language != Language.EN:
            message_for_ai = await translation_service.translate_text(
                message.message, "en"
            )
        
        # Prepare conversation context
        conversation_context = {
            "current_message": message_for_ai,
            "conversation_history": session["messages"][-10:],  # Last 10 messages
            "current_assessment": session.get("current_assessment"),
            "user_role": "patient",
            "additional_context": message.context
        }
        
        # Generate AI response
        ai_response = await triage_service.chat_response(conversation_context)
        
        # Generate follow-up questions
        follow_up_questions = await _generate_follow_up_questions(
            ai_response, conversation_context, "patient"
        )
        
        # Check if urgency level needs updating
        urgency_update = await _check_urgency_update(
            ai_response, session.get("current_assessment")
        )
        
        # Identify additional information needed
        additional_info_needed = await _identify_additional_info_needed(
            ai_response, conversation_context
        )
        
        # Translate response if needed
        response_text = ai_response.get("response", "I'm here to help with your health concerns.")
        if message.language != Language.EN:
            response_text = await translation_service.translate_text(
                response_text, message.language.value
            )
            follow_up_questions = await translation_service.translate_list(
                follow_up_questions, message.language.value
            )
            additional_info_needed = await translation_service.translate_list(
                additional_info_needed, message.language.value
            )
        
        # Create chat response
        chat_response = ChatResponse(
            response=response_text,
            follow_up_questions=follow_up_questions,
            urgency_update=urgency_update,
            additional_info_needed=additional_info_needed
        )
        
        # Add AI response to session
        session["messages"].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "follow_up_questions": follow_up_questions,
            "urgency_update": urgency_update.value if urgency_update else None
        })
        
        # Update current assessment if urgency changed
        if urgency_update:
            session["current_assessment"] = {
                "urgency_level": urgency_update.value,
                "updated_at": datetime.utcnow().isoformat()
            }
        
        return chat_response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )

@router.get("/chat/{session_id}/history")
async def get_chat_history(
    session_id: str
):
    """Get chat session history."""
    
    session = chat_sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return {
        "session_id": session_id,
        "created_at": session["created_at"],
        "language": session["language"],
        "message_count": len(session["messages"]),
        "messages": session["messages"],
        "current_assessment": session.get("current_assessment")
    }

@router.delete("/chat/{session_id}")
async def delete_chat_session(
    session_id: str
):
    """Delete a chat session."""
    
    session = chat_sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    del chat_sessions[session_id]
    
    return SuccessResponse(
        message="Chat session deleted successfully",
        data={"session_id": session_id}
    )

@router.get("/analysis/{analysis_id}", response_model=TriageResult)
async def get_triage_analysis(
    analysis_id: str
):
    """Retrieve a previous triage analysis result."""
    
    result = await _load_triage_result(analysis_id, None)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Triage analysis not found"
        )
    
    return result

@router.get("/emergency-guidelines")
async def get_emergency_guidelines(
    language: Language = Query(default=Language.EN, description="Response language")
):
    """Get emergency guidelines and when to seek immediate care."""
    
    guidelines = {
        "emergency_signs": [
            "Chest pain or pressure",
            "Difficulty breathing or shortness of breath",
            "Severe bleeding that won't stop",
            "Signs of stroke (face drooping, arm weakness, speech difficulty)",
            "Loss of consciousness",
            "Severe allergic reaction",
            "Severe burns",
            "Suspected poisoning",
            "Severe head injury",
            "Suicidal thoughts or behavior"
        ],
        "when_to_call_911": [
            "Life-threatening emergency",
            "Severe injury or illness",
            "Person is unconscious",
            "Severe difficulty breathing",
            "Chest pain with sweating or nausea",
            "Signs of heart attack or stroke",
            "Severe bleeding",
            "Suspected overdose or poisoning"
        ],
        "urgent_care_situations": [
            "High fever (over 103°F/39.4°C)",
            "Persistent vomiting or diarrhea",
            "Severe pain",
            "Suspected fracture",
            "Deep cuts that may need stitches",
            "Eye injuries",
            "Severe allergic reactions (not life-threatening)",
            "Urinary tract infections"
        ],
        "routine_care_situations": [
            "Minor cuts and scrapes",
            "Common cold symptoms",
            "Mild headaches",
            "Minor skin rashes",
            "Routine check-ups",
            "Prescription refills",
            "Preventive care"
        ]
    }
    
    # Translate if needed
    if language != Language.EN:
        for category, items in guidelines.items():
            guidelines[category] = await translation_service.translate_list(items, language.value)
    
    return guidelines

async def _determine_urgency_level(ai_analysis: dict, context: dict) -> UrgencyLevel:
    """Determine urgency level based on AI analysis and context."""
    
    # Check for emergency keywords in symptoms
    emergency_keywords = [
        "chest pain", "difficulty breathing", "unconscious", "severe bleeding",
        "stroke", "heart attack", "overdose", "poisoning", "severe burn"
    ]
    
    urgent_keywords = [
        "severe pain", "high fever", "persistent vomiting", "severe headache",
        "difficulty swallowing", "severe allergic reaction"
    ]
    
    symptoms_lower = context["symptoms"].lower()
    
    # Check AI confidence and predictions
    ai_urgency = ai_analysis.get("urgency_score", 0.3)
    
    # Emergency conditions
    if (any(keyword in symptoms_lower for keyword in emergency_keywords) or 
        ai_urgency > 0.8 or
        context.get("severity_self_assessment", 0) >= 9):
        return UrgencyLevel.EMERGENCY
    
    # Urgent conditions
    elif (any(keyword in symptoms_lower for keyword in urgent_keywords) or
          ai_urgency > 0.6 or
          context.get("severity_self_assessment", 0) >= 7):
        return UrgencyLevel.URGENT
    
    # Routine conditions
    else:
        return UrgencyLevel.ROUTINE

async def _generate_possible_conditions(
    ai_analysis: dict, 
    context: dict, 
    user_role: str
) -> List[Dict[str, Any]]:
    """Generate list of possible medical conditions."""
    
    conditions = []
    ai_predictions = ai_analysis.get("conditions", {})
    
    for condition, probability in ai_predictions.items():
        if probability > 0.1:  # Only include significant possibilities
            
            # Get condition information from medical knowledge base
            condition_info = await medical_kb.get_condition_info(condition)
            
            # Generate description based on user role
            if user_role == UserRole.DOCTOR.value:
                description = condition_info.get("clinical_description", condition)
            else:
                description = condition_info.get("patient_description", condition)
            
            condition_data = {
                "name": condition,
                "probability": probability,
                "description": description,
                "severity": condition_info.get("typical_severity", "medium"),
                "common_symptoms": condition_info.get("symptoms", []),
                "typical_duration": condition_info.get("duration", "varies")
            }
            
            conditions.append(condition_data)
    
    # Sort by probability
    conditions.sort(key=lambda x: x["probability"], reverse=True)
    
    return conditions[:5]  # Return top 5 conditions

async def _generate_triage_recommendations(
    urgency_level: UrgencyLevel,
    possible_conditions: List[Dict[str, Any]],
    context: dict,
    user_role: str
) -> tuple[List[str], List[str]]:
    """Generate recommendations and next steps based on triage assessment."""
    
    recommendations = []
    next_steps = []
    
    if urgency_level == UrgencyLevel.EMERGENCY:
        if user_role == UserRole.DOCTOR.value:
            recommendations.extend([
                "Immediate medical evaluation required",
                "Consider emergency department referral",
                "Monitor vital signs closely",
                "Prepare for potential interventions"
            ])
            next_steps.extend([
                "Activate emergency protocols",
                "Ensure IV access if needed",
                "Contact specialist if required",
                "Document thoroughly"
            ])
        else:
            recommendations.extend([
                "Seek emergency medical care immediately",
                "Call 911 or go to the nearest emergency room",
                "Do not drive yourself if possible",
                "Bring a list of current medications"
            ])
            next_steps.extend([
                "Call emergency services now",
                "Have someone drive you to hospital",
                "Gather important medical information",
                "Stay calm and follow emergency instructions"
            ])
    
    elif urgency_level == UrgencyLevel.URGENT:
        if user_role == UserRole.DOCTOR.value:
            recommendations.extend([
                "Prompt medical evaluation within 24 hours",
                "Consider urgent care or same-day appointment",
                "Monitor symptom progression",
                "Provide symptomatic relief as appropriate"
            ])
            next_steps.extend([
                "Schedule urgent appointment",
                "Consider diagnostic testing",
                "Provide patient education",
                "Plan follow-up care"
            ])
        else:
            recommendations.extend([
                "See a healthcare provider within 24 hours",
                "Consider urgent care if primary doctor unavailable",
                "Monitor symptoms closely",
                "Seek immediate care if symptoms worsen"
            ])
            next_steps.extend([
                "Call your doctor's office",
                "Visit urgent care if needed",
                "Keep track of symptoms",
                "Have emergency plan ready"
            ])
    
    else:  # ROUTINE
        if user_role == UserRole.DOCTOR.value:
            recommendations.extend([
                "Routine medical evaluation appropriate",
                "Schedule within 1-2 weeks if symptoms persist",
                "Provide symptomatic care",
                "Patient education on warning signs"
            ])
            next_steps.extend([
                "Schedule routine appointment",
                "Consider conservative management",
                "Provide self-care instructions",
                "Plan appropriate follow-up"
            ])
        else:
            recommendations.extend([
                "Schedule appointment with your regular doctor",
                "Monitor symptoms for changes",
                "Try appropriate self-care measures",
                "Seek care sooner if symptoms worsen"
            ])
            next_steps.extend([
                "Call doctor's office for appointment",
                "Continue monitoring symptoms",
                "Follow self-care recommendations",
                "Know when to seek urgent care"
            ])
    
    return recommendations, next_steps

async def _identify_red_flags(ai_analysis: dict, context: dict) -> List[str]:
    """Identify red flag symptoms that require immediate attention."""
    
    red_flags = []
    symptoms = context["symptoms"].lower()
    
    # Define red flag patterns
    red_flag_patterns = {
        "chest pain with radiation": ["chest pain", "arm pain", "jaw pain"],
        "neurological symptoms": ["weakness", "numbness", "confusion", "slurred speech"],
        "respiratory distress": ["difficulty breathing", "shortness of breath", "wheezing"],
        "severe pain": ["severe", "excruciating", "unbearable"],
        "bleeding": ["bleeding", "blood", "hemorrhage"],
        "altered consciousness": ["dizzy", "faint", "unconscious", "confused"]
    }
    
    for flag_name, keywords in red_flag_patterns.items():
        if any(keyword in symptoms for keyword in keywords):
            red_flags.append(f"Warning: {flag_name.replace('_', ' ').title()} detected")
    
    # Add AI-identified red flags
    ai_red_flags = ai_analysis.get("red_flags", [])
    red_flags.extend(ai_red_flags)
    
    return list(set(red_flags))  # Remove duplicates

async def _determine_care_requirements(
    urgency_level: UrgencyLevel,
    possible_conditions: List[Dict[str, Any]]
) -> tuple[Optional[str], str]:
    """Determine estimated wait time and appropriate care level."""
    
    if urgency_level == UrgencyLevel.EMERGENCY:
        return "Immediate", "Emergency Department"
    elif urgency_level == UrgencyLevel.URGENT:
        return "Within 24 hours", "Urgent Care or Primary Care"
    else:
        return "1-2 weeks", "Primary Care"

async def _generate_follow_up_questions(
    ai_response: dict,
    conversation_context: dict,
    user_role: str
) -> List[str]:
    """Generate relevant follow-up questions based on conversation."""
    
    # This would typically use NLP to analyze the conversation
    # and generate contextually relevant questions
    
    base_questions = [
        "How long have you been experiencing these symptoms?",
        "Have you tried any treatments or medications?",
        "Do you have any other symptoms?",
        "Has anyone in your family had similar symptoms?",
        "Are you taking any medications currently?"
    ]
    
    # Filter questions based on what's already been asked/answered
    asked_topics = set()
    for message in conversation_context.get("conversation_history", []):
        content = message.get("content", "").lower()
        if "how long" in content or "duration" in content:
            asked_topics.add("duration")
        if "medication" in content or "treatment" in content:
            asked_topics.add("medications")
        if "family" in content:
            asked_topics.add("family_history")
    
    # Generate contextual questions
    follow_up_questions = []
    
    if "duration" not in asked_topics:
        follow_up_questions.append("How long have you been experiencing these symptoms?")
    
    if "medications" not in asked_topics:
        follow_up_questions.append("Are you currently taking any medications?")
    
    if "severity" not in asked_topics:
        follow_up_questions.append("On a scale of 1-10, how would you rate your pain/discomfort?")
    
    # Add AI-suggested questions
    ai_questions = ai_response.get("suggested_questions", [])
    follow_up_questions.extend(ai_questions)
    
    return follow_up_questions[:3]  # Limit to 3 questions

async def _check_urgency_update(
    ai_response: dict,
    current_assessment: Optional[dict]
) -> Optional[UrgencyLevel]:
    """Check if urgency level needs to be updated based on new information."""
    
    new_urgency_score = ai_response.get("urgency_score", 0.3)
    
    # Determine new urgency level
    if new_urgency_score > 0.8:
        new_urgency = UrgencyLevel.EMERGENCY
    elif new_urgency_score > 0.6:
        new_urgency = UrgencyLevel.URGENT
    else:
        new_urgency = UrgencyLevel.ROUTINE
    
    # Check if urgency has increased
    if current_assessment:
        current_urgency = current_assessment.get("urgency_level", "routine")
        urgency_levels = {"routine": 1, "urgent": 2, "emergency": 3}
        
        if urgency_levels.get(new_urgency.value, 1) > urgency_levels.get(current_urgency, 1):
            return new_urgency
    
    return None

async def _identify_additional_info_needed(
    ai_response: dict,
    conversation_context: dict
) -> List[str]:
    """Identify what additional information would be helpful."""
    
    info_needed = []
    
    # Check what information is missing
    current_message = conversation_context.get("current_message", "")
    
    # Basic information gaps
    if not any(word in current_message.lower() for word in ["age", "years old"]):
        info_needed.append("Patient age")
    
    if not any(word in current_message.lower() for word in ["male", "female", "gender"]):
        info_needed.append("Patient gender")
    
    if not any(word in current_message.lower() for word in ["medication", "drug", "pill"]):
        info_needed.append("Current medications")
    
    if not any(word in current_message.lower() for word in ["allergy", "allergic"]):
        info_needed.append("Known allergies")
    
    # Add AI-suggested information needs
    ai_info_needed = ai_response.get("information_needed", [])
    info_needed.extend(ai_info_needed)
    
    return info_needed[:3]  # Limit to 3 items

async def _store_triage_result(
    analysis_id: str,
    result: TriageResult,
    symptom_input: SymptomInput,
    user_id: int
):
    """Store triage analysis result."""
    
    os.makedirs("analysis_results", exist_ok=True)
    
    result_data = {
        "analysis_id": analysis_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "symptom_input": symptom_input.dict(),
        "result": result.dict()
    }
    
    with open(f"analysis_results/triage_{analysis_id}.json", "w") as f:
        json.dump(result_data, f, indent=2)

async def _load_triage_result(analysis_id: str, user_id: int) -> Optional[TriageResult]:
    """Load stored triage analysis result."""
    
    try:
        with open(f"analysis_results/triage_{analysis_id}.json", "r") as f:
            data = json.load(f)
        
        # Verify user access
        if data["user_id"] != user_id:
            return None
        
        return TriageResult(**data["result"])
    
    except FileNotFoundError:
        return None
