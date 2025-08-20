import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MedicalKnowledgeBase:
    """Simplified medical knowledge base for development."""
    
    def __init__(self):
        logger.info("Medical knowledge base initialized (mock mode)")
    
    async def get_condition_info(self, condition_name: str) -> Dict[str, Any]:
        """Mock condition information."""
        return {
            "category": "general",
            "clinical_description": f"Clinical information about {condition_name}",
            "patient_description": f"Patient-friendly information about {condition_name}",
            "typical_severity": "medium",
            "symptoms": [],
            "duration": "varies",
            "risk_factors": [],
            "treatment_urgency": "routine"
        }
