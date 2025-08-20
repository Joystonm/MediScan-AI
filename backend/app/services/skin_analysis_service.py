import logging
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class SkinAnalysisService:
    """Simplified skin analysis service for development."""
    
    def __init__(self):
        self.class_names = [
            "Melanoma",
            "Melanocytic nevus", 
            "Basal cell carcinoma",
            "Actinic keratosis",
            "Benign keratosis",
            "Dermatofibroma",
            "Vascular lesion",
            "Squamous cell carcinoma"
        ]
        logger.info("Skin analysis service initialized (mock mode)")
    
    async def analyze_lesion(self, image) -> Dict[str, Any]:
        """Mock skin lesion analysis."""
        # Return mock results for development
        prob_dict = {
            "Benign keratosis": 0.65,
            "Melanocytic nevus": 0.20,
            "Melanoma": 0.10,
            "Basal cell carcinoma": 0.03,
            "Actinic keratosis": 0.02
        }
        
        return {
            "probabilities": prob_dict,
            "top_class": "Benign keratosis",
            "confidence": 0.65,
            "attention_map": np.zeros((224, 224)),
            "roi_boxes": []
        }
