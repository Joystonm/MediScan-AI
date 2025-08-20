# Output formatting and postprocessing utilities
from typing import Dict, List, Any, Tuple
import json
from datetime import datetime

class OutputFormatter:
    """
    Utilities for formatting and postprocessing model outputs
    """
    
    def __init__(self):
        self.risk_thresholds = {
            "low": 0.3,
            "moderate": 0.6,
            "high": 0.8
        }
    
    def format_skin_analysis_result(self, prediction: Dict[str, Any], image_info: Dict = None) -> Dict:
        """
        Format skin cancer analysis results for API response
        """
        predicted_class = prediction.get("predicted_class", "Unknown")
        confidence = prediction.get("confidence", 0.0)
        all_probabilities = prediction.get("all_probabilities", {})
        
        # Determine risk level
        risk_level = self._determine_skin_risk_level(predicted_class, confidence)
        
        # Generate recommendations
        recommendations = self._generate_skin_recommendations(predicted_class, risk_level)
        
        # Analyze lesion characteristics
        lesion_characteristics = self._analyze_lesion_characteristics(all_probabilities)
        
        return {
            "prediction": predicted_class,
            "confidence": round(confidence, 3),
            "risk_level": risk_level,
            "recommendations": recommendations,
            "lesion_characteristics": lesion_characteristics,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "image_info": image_info or {}
        }
    
    def format_radiology_result(self, prediction: Dict[str, Any], image_info: Dict = None) -> Dict:
        """
        Format radiology analysis results for API response
        """
        detected_pathologies = prediction.get("detected_pathologies", [])
        confidence_scores = prediction.get("confidence_scores", {})
        pathology_detected = prediction.get("pathology_detected", False)
        
        # Generate findings
        findings = self._generate_radiology_findings(detected_pathologies, confidence_scores)
        
        # Determine urgency level
        urgency_level = self._determine_radiology_urgency(detected_pathologies, confidence_scores)
        
        # Generate recommendations
        recommendations = self._generate_radiology_recommendations(urgency_level, detected_pathologies)
        
        return {
            "findings": findings,
            "pathology_detected": pathology_detected,
            "confidence_scores": {k: round(v, 3) for k, v in confidence_scores.items()},
            "recommendations": recommendations,
            "urgency_level": urgency_level,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "image_info": image_info or {}
        }
    
    def format_triage_result(self, assessment: Dict[str, Any]) -> Dict:
        """
        Format triage assessment results
        """
        return {
            "urgency_level": assessment.get("urgency_level", "moderate"),
            "recommendations": assessment.get("recommendations", []),
            "possible_conditions": assessment.get("possible_conditions", []),
            "next_steps": assessment.get("next_steps", []),
            "assessment_timestamp": datetime.utcnow().isoformat(),
            "disclaimer": "This assessment is for informational purposes only and should not replace professional medical advice."
        }
    
    def _determine_skin_risk_level(self, predicted_class: str, confidence: float) -> str:
        """
        Determine risk level for skin lesion
        """
        high_risk_conditions = ["Melanoma", "Basal cell carcinoma"]
        moderate_risk_conditions = ["Actinic keratosis"]
        
        if predicted_class in high_risk_conditions:
            return "high" if confidence > 0.7 else "moderate"
        elif predicted_class in moderate_risk_conditions:
            return "moderate" if confidence > 0.6 else "low"
        else:
            return "low" if confidence > 0.8 else "moderate"
    
    def _generate_skin_recommendations(self, predicted_class: str, risk_level: str) -> List[str]:
        """
        Generate recommendations based on skin analysis
        """
        base_recommendations = [
            "Use broad-spectrum sunscreen (SPF 30+) daily",
            "Perform regular self-examinations",
            "Monitor for changes in size, color, or shape"
        ]
        
        if risk_level == "high":
            base_recommendations.extend([
                "Seek immediate dermatological evaluation",
                "Consider biopsy if recommended by dermatologist",
                "Avoid sun exposure until evaluated"
            ])
        elif risk_level == "moderate":
            base_recommendations.extend([
                "Schedule dermatology appointment within 2-4 weeks",
                "Document lesion with photos for monitoring",
                "Avoid picking or scratching the lesion"
            ])
        else:
            base_recommendations.extend([
                "Schedule routine dermatology checkup",
                "Continue regular skin monitoring",
                "Maintain good sun protection habits"
            ])
        
        return base_recommendations
    
    def _analyze_lesion_characteristics(self, probabilities: Dict[str, float]) -> Dict[str, str]:
        """
        Analyze lesion characteristics based on probabilities
        """
        # This is a simplified analysis - in practice, you'd use more sophisticated methods
        melanoma_prob = probabilities.get("Melanoma", 0)
        bcc_prob = probabilities.get("Basal cell carcinoma", 0)
        
        return {
            "asymmetry": "high" if melanoma_prob > 0.5 else "low",
            "border_irregularity": "high" if melanoma_prob > 0.4 else "moderate",
            "color_variation": "high" if melanoma_prob > 0.3 else "low",
            "diameter": "concerning" if (melanoma_prob + bcc_prob) > 0.4 else "normal"
        }
    
    def _generate_radiology_findings(self, pathologies: List[str], confidence_scores: Dict[str, float]) -> List[str]:
        """
        Generate clinical findings from radiology analysis
        """
        if not pathologies:
            return ["No acute cardiopulmonary abnormality detected"]
        
        findings = []
        for pathology in pathologies:
            confidence = confidence_scores.get(pathology, 0)
            if confidence > 0.7:
                findings.append(f"Findings consistent with {pathology.lower()}")
            else:
                findings.append(f"Possible {pathology.lower()} - clinical correlation recommended")
        
        return findings
    
    def _determine_radiology_urgency(self, pathologies: List[str], confidence_scores: Dict[str, float]) -> str:
        """
        Determine urgency level for radiology findings
        """
        emergency_conditions = ["Pneumothorax", "Mass"]
        urgent_conditions = ["Pneumonia", "Consolidation", "Effusion"]
        
        for condition in emergency_conditions:
            if condition in pathologies and confidence_scores.get(condition, 0) > 0.7:
                return "emergency"
        
        for condition in urgent_conditions:
            if condition in pathologies and confidence_scores.get(condition, 0) > 0.6:
                return "urgent"
        
        if pathologies:
            return "routine"
        
        return "normal"
    
    def _generate_radiology_recommendations(self, urgency_level: str, pathologies: List[str]) -> List[str]:
        """
        Generate recommendations based on radiology findings
        """
        if urgency_level == "emergency":
            return [
                "Immediate clinical evaluation required",
                "Consider emergency department consultation",
                "Urgent follow-up imaging may be needed"
            ]
        elif urgency_level == "urgent":
            return [
                "Clinical correlation recommended within 24-48 hours",
                "Consider antibiotic therapy if indicated",
                "Follow-up imaging in 1-2 weeks"
            ]
        elif urgency_level == "routine":
            return [
                "Routine clinical follow-up as indicated",
                "Correlate with clinical symptoms",
                "Consider comparison with prior studies"
            ]
        else:
            return [
                "No immediate action required",
                "Routine follow-up as clinically indicated",
                "Maintain regular health monitoring"
            ]

# Response templates
RESPONSE_TEMPLATES = {
    "skin_analysis": {
        "high_risk": "High-risk lesion detected. Immediate dermatological evaluation recommended.",
        "moderate_risk": "Moderate-risk lesion identified. Schedule dermatology appointment within 2-4 weeks.",
        "low_risk": "Low-risk lesion. Continue routine monitoring and sun protection."
    },
    "radiology": {
        "emergency": "Urgent findings detected. Immediate medical attention required.",
        "urgent": "Significant findings identified. Clinical evaluation within 24-48 hours recommended.",
        "routine": "Findings noted. Routine clinical follow-up as indicated.",
        "normal": "No acute abnormalities detected."
    }
}
