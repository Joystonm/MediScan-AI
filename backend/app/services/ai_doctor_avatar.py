"""
AI Doctor Avatar with Emotional Intelligence
Revolutionary feature for Medi-Hacks 2025
"""

import cv2
import numpy as np
from typing import Dict, List, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class AIDoctorAvatar:
    """AI Doctor Avatar with emotional intelligence and real-time interaction"""
    
    def __init__(self):
        self.emotion_model = self._load_emotion_model()
        self.avatar_responses = self._load_avatar_responses()
        self.conversation_context = {}
        
    async def analyze_patient_emotion(self, video_frame: np.ndarray) -> Dict[str, Any]:
        """Analyze patient's emotional state from video feed"""
        
        try:
            # Detect faces in the frame
            faces = self._detect_faces(video_frame)
            
            if not faces:
                return {"emotion": "neutral", "confidence": 0.0, "recommendations": []}
            
            # Analyze emotion for the primary face
            primary_face = faces[0]
            emotion_data = self._analyze_facial_emotion(primary_face)
            
            # Generate appropriate avatar response
            avatar_response = self._generate_avatar_response(emotion_data)
            
            return {
                "emotion": emotion_data["primary_emotion"],
                "confidence": emotion_data["confidence"],
                "emotional_state": emotion_data["detailed_emotions"],
                "avatar_response": avatar_response,
                "recommendations": self._get_emotion_based_recommendations(emotion_data),
                "therapy_suggestions": self._get_therapy_suggestions(emotion_data)
            }
            
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return {
                "emotion": "neutral",
                "confidence": 0.0,
                "avatar_response": "I'm here to help you. Please tell me how you're feeling.",
                "recommendations": ["Take deep breaths", "Stay hydrated", "Rest when needed"]
            }
    
    def _detect_faces(self, frame: np.ndarray) -> List[np.ndarray]:
        """Detect faces in video frame"""
        
        # Use OpenCV Haar Cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        face_regions = []
        for (x, y, w, h) in faces:
            face_region = frame[y:y+h, x:x+w]
            face_regions.append(face_region)
        
        return face_regions
    
    def _analyze_facial_emotion(self, face_region: np.ndarray) -> Dict[str, Any]:
        """Analyze emotions from facial features"""
        
        # Simulate advanced emotion detection (in real implementation, use trained models)
        emotions = {
            "happy": np.random.uniform(0.1, 0.9),
            "sad": np.random.uniform(0.1, 0.9),
            "angry": np.random.uniform(0.0, 0.3),
            "fear": np.random.uniform(0.0, 0.4),
            "surprise": np.random.uniform(0.0, 0.5),
            "disgust": np.random.uniform(0.0, 0.2),
            "neutral": np.random.uniform(0.2, 0.8)
        }
        
        primary_emotion = max(emotions, key=emotions.get)
        confidence = emotions[primary_emotion]
        
        return {
            "primary_emotion": primary_emotion,
            "confidence": confidence,
            "detailed_emotions": emotions
        }
    
    def _generate_avatar_response(self, emotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate avatar response based on detected emotion"""
        
        emotion = emotion_data["primary_emotion"]
        confidence = emotion_data["confidence"]
        
        responses = {
            "happy": {
                "text": "I can see you're feeling positive today! That's wonderful. How can I help you maintain your good health?",
                "avatar_expression": "smiling",
                "voice_tone": "warm_encouraging"
            },
            "sad": {
                "text": "I notice you might be feeling down. I'm here to support you. Would you like to talk about what's troubling you?",
                "avatar_expression": "concerned_caring",
                "voice_tone": "gentle_supportive"
            },
            "angry": {
                "text": "I can sense some frustration. Let's work together to address your concerns. Take a deep breath with me.",
                "avatar_expression": "calm_understanding",
                "voice_tone": "soothing_patient"
            },
            "fear": {
                "text": "I understand you might be feeling anxious about your health. That's completely normal. Let me help ease your concerns.",
                "avatar_expression": "reassuring",
                "voice_tone": "calm_confident"
            },
            "neutral": {
                "text": "Hello! I'm Dr. AI, your virtual healthcare assistant. I'm here to help with your medical concerns today.",
                "avatar_expression": "professional_friendly",
                "voice_tone": "professional_warm"
            }
        }
        
        return responses.get(emotion, responses["neutral"])
    
    def _get_emotion_based_recommendations(self, emotion_data: Dict[str, Any]) -> List[str]:
        """Get health recommendations based on emotional state"""
        
        emotion = emotion_data["primary_emotion"]
        
        recommendations = {
            "happy": [
                "Continue your positive lifestyle habits",
                "Consider sharing your good mood with others",
                "Maintain regular exercise and healthy eating"
            ],
            "sad": [
                "Consider speaking with a mental health professional",
                "Engage in activities you enjoy",
                "Reach out to friends and family for support",
                "Practice mindfulness or meditation"
            ],
            "angry": [
                "Try deep breathing exercises",
                "Consider physical exercise to release tension",
                "Practice progressive muscle relaxation",
                "Identify and address sources of stress"
            ],
            "fear": [
                "Practice grounding techniques (5-4-3-2-1 method)",
                "Consider cognitive behavioral therapy techniques",
                "Speak with a healthcare provider about your concerns",
                "Try relaxation exercises"
            ],
            "neutral": [
                "Maintain regular health check-ups",
                "Continue healthy lifestyle habits",
                "Stay hydrated and get adequate sleep"
            ]
        }
        
        return recommendations.get(emotion, recommendations["neutral"])
    
    def _get_therapy_suggestions(self, emotion_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get therapy suggestions based on emotional analysis"""
        
        emotion = emotion_data["primary_emotion"]
        confidence = emotion_data["confidence"]
        
        if confidence < 0.3:
            return [{"type": "general", "suggestion": "Continue monitoring your emotional well-being"}]
        
        therapy_suggestions = {
            "sad": [
                {"type": "CBT", "suggestion": "Cognitive Behavioral Therapy for mood improvement"},
                {"type": "mindfulness", "suggestion": "Mindfulness-based stress reduction"},
                {"type": "activity", "suggestion": "Behavioral activation therapy"}
            ],
            "angry": [
                {"type": "anger_management", "suggestion": "Anger management techniques"},
                {"type": "stress_reduction", "suggestion": "Stress reduction therapy"},
                {"type": "communication", "suggestion": "Communication skills training"}
            ],
            "fear": [
                {"type": "exposure", "suggestion": "Gradual exposure therapy"},
                {"type": "relaxation", "suggestion": "Progressive muscle relaxation training"},
                {"type": "CBT", "suggestion": "Cognitive restructuring for anxiety"}
            ]
        }
        
        return therapy_suggestions.get(emotion, [{"type": "general", "suggestion": "Regular mental health check-ins"}])
    
    def _load_emotion_model(self):
        """Load pre-trained emotion recognition model"""
        # In real implementation, load actual trained model
        return "emotion_model_placeholder"
    
    def _load_avatar_responses(self):
        """Load avatar response templates"""
        return {
            "greetings": ["Hello! I'm Dr. AI, your virtual healthcare assistant."],
            "empathy": ["I understand how you're feeling.", "That must be difficult for you."],
            "encouragement": ["You're taking the right steps for your health.", "I'm here to support you."]
        }

class AvatarAnimationEngine:
    """3D Avatar Animation Engine"""
    
    def __init__(self):
        self.avatar_models = self._load_avatar_models()
        self.animation_states = {}
    
    async def animate_avatar(self, emotion: str, text: str) -> Dict[str, Any]:
        """Generate avatar animation based on emotion and text"""
        
        animation_config = {
            "happy": {
                "facial_expression": "smile",
                "eye_movement": "bright_engaged",
                "head_movement": "slight_nod",
                "hand_gestures": "open_welcoming"
            },
            "concerned": {
                "facial_expression": "concerned_eyebrows",
                "eye_movement": "focused_caring",
                "head_movement": "slight_tilt",
                "hand_gestures": "supportive"
            },
            "professional": {
                "facial_expression": "neutral_confident",
                "eye_movement": "direct_professional",
                "head_movement": "stable",
                "hand_gestures": "explanatory"
            }
        }
        
        return {
            "animation_sequence": animation_config.get(emotion, animation_config["professional"]),
            "duration": len(text) * 0.1,  # Approximate speaking time
            "voice_synthesis": {
                "text": text,
                "tone": emotion,
                "speed": "normal",
                "pitch": "professional"
            }
        }
    
    def _load_avatar_models(self):
        """Load 3D avatar models"""
        return {
            "doctor_male": "models/doctor_male_3d.obj",
            "doctor_female": "models/doctor_female_3d.obj",
            "nurse": "models/nurse_3d.obj"
        }

# Integration with main triage system
class EmotionalTriageIntegration:
    """Integration between emotional AI and medical triage"""
    
    def __init__(self):
        self.avatar = AIDoctorAvatar()
        self.animation_engine = AvatarAnimationEngine()
    
    async def enhanced_triage_with_emotion(
        self, 
        message: str, 
        video_frame: np.ndarray = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """Enhanced triage assessment with emotional intelligence"""
        
        # Standard medical triage
        from .triage_chat_service import TriageChatService
        triage_service = TriageChatService()
        medical_response = await triage_service.process_chat_message(message, session_id)
        
        # Emotional analysis if video provided
        emotional_data = {}
        avatar_animation = {}
        
        if video_frame is not None:
            emotional_data = await self.avatar.analyze_patient_emotion(video_frame)
            avatar_animation = await self.animation_engine.animate_avatar(
                emotional_data.get("emotion", "neutral"),
                medical_response["response"]
            )
        
        return {
            **medical_response,
            "emotional_analysis": emotional_data,
            "avatar_animation": avatar_animation,
            "enhanced_recommendations": self._combine_medical_emotional_recommendations(
                medical_response, emotional_data
            )
        }
    
    def _combine_medical_emotional_recommendations(
        self, 
        medical_response: Dict[str, Any], 
        emotional_data: Dict[str, Any]
    ) -> List[str]:
        """Combine medical and emotional recommendations"""
        
        medical_recs = medical_response.get("recommendations", [])
        emotional_recs = emotional_data.get("recommendations", [])
        
        combined = medical_recs + emotional_recs
        
        # Add holistic recommendations
        if emotional_data.get("emotion") == "sad" and medical_response.get("urgency_level") == "routine":
            combined.append("Consider the connection between physical and mental health")
        
        return list(set(combined))  # Remove duplicates
