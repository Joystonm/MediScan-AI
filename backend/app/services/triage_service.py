import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TriageService:
    """Simplified triage service for development."""
    
    def __init__(self):
        logger.info("Triage service initialized (mock mode)")
    
    async def analyze_symptoms(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock symptom analysis."""
        return {
            "urgency_score": 0.4,
            "conditions": {"Common cold": 0.6, "Flu": 0.3},
            "confidence": 0.7,
            "red_flags": [],
            "suggested_questions": ["How long have you had these symptoms?"]
        }
    
    async def chat_response(self, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock chat response."""
        return {
            "response": "I understand you're experiencing some symptoms. Can you tell me more about them?",
            "urgency_score": 0.4,
            "suggested_questions": ["How severe is your discomfort on a scale of 1-10?"]
        }
