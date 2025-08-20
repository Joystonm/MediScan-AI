import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class RadiologyService:
    """Simplified radiology service for development."""
    
    def __init__(self):
        self.chest_pathologies = [
            "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
            "Mass", "Nodule", "Pneumonia", "Pneumothorax"
        ]
        logger.info("Radiology service initialized (mock mode)")
    
    async def analyze_scan(self, image, scan_type: str, clinical_history: Optional[str] = None) -> Dict[str, Any]:
        """Mock radiology analysis."""
        # Return mock results for development
        predictions = {
            "No Finding": 0.70,
            "Cardiomegaly": 0.15,
            "Pneumonia": 0.10,
            "Atelectasis": 0.05
        }
        
        return {
            "predictions": predictions,
            "attention_map": np.zeros((224, 224)),
            "localizations": {},
            "urgency_score": 0.3,
            "scan_type": scan_type
        }
