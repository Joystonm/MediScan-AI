# Radiology model loader and configuration (CheXNet)
import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, Any, List
import os

class CheXNetModel:
    """
    CheXNet chest X-ray pathology detection model wrapper
    """
    
    def __init__(self, model_path: str = None, num_classes: int = 14):
        self.model_path = model_path or os.getenv("RADIOLOGY_MODEL_PATH", "models/chexnet_model.pth")
        self.num_classes = num_classes
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Pathology classes from ChestX-ray14 dataset
        self.class_names = [
            "Atelectasis",
            "Cardiomegaly", 
            "Effusion",
            "Infiltration",
            "Mass",
            "Nodule",
            "Pneumonia",
            "Pneumothorax",
            "Consolidation",
            "Edema",
            "Emphysema",
            "Fibrosis",
            "Pleural_Thickening",
            "Hernia"
        ]
    
    def load_model(self) -> bool:
        """
        Load the pretrained CheXNet model
        """
        try:
            # Create model architecture (DenseNet-121 based)
            self.model = models.densenet121(pretrained=False)
            
            # Modify final layer for multi-label classification
            num_features = self.model.classifier.in_features
            self.model.classifier = nn.Linear(num_features, self.num_classes)
            
            # Load pretrained weights if available
            if os.path.exists(self.model_path):
                checkpoint = torch.load(self.model_path, map_location=self.device)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                print(f"Loaded CheXNet model from {self.model_path}")
            else:
                print(f"Model file not found at {self.model_path}. Using randomly initialized weights.")
            
            self.model.to(self.device)
            self.model.eval()
            return True
            
        except Exception as e:
            print(f"Error loading CheXNet model: {str(e)}")
            return False
    
    def predict(self, image_tensor: torch.Tensor, threshold: float = 0.5) -> Dict[str, Any]:
        """
        Make prediction on preprocessed image tensor
        Multi-label classification for pathology detection
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            outputs = self.model(image_tensor)
            probabilities = torch.sigmoid(outputs)  # Multi-label classification
            
            # Get predictions above threshold
            predictions = (probabilities > threshold).cpu().numpy()[0]
            prob_scores = probabilities.cpu().numpy()[0]
            
            detected_pathologies = [
                self.class_names[i] for i, pred in enumerate(predictions) if pred
            ]
            
            confidence_scores = {
                class_name: float(prob_scores[i]) 
                for i, class_name in enumerate(self.class_names)
            }
            
            return {
                "detected_pathologies": detected_pathologies,
                "confidence_scores": confidence_scores,
                "max_confidence": float(max(prob_scores)),
                "pathology_detected": len(detected_pathologies) > 0
            }
    
    def get_findings_report(self, predictions: Dict[str, Any]) -> List[str]:
        """
        Generate clinical findings report from predictions
        """
        findings = []
        
        if not predictions["pathology_detected"]:
            findings.append("No acute cardiopulmonary abnormality detected")
        else:
            for pathology in predictions["detected_pathologies"]:
                confidence = predictions["confidence_scores"][pathology]
                findings.append(f"Possible {pathology.lower()} (confidence: {confidence:.2f})")
        
        return findings
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information and metadata
        """
        return {
            "model_type": "DenseNet-121",
            "dataset": "ChestX-ray14",
            "num_classes": self.num_classes,
            "class_names": self.class_names,
            "input_size": (224, 224),
            "device": str(self.device),
            "loaded": self.model is not None,
            "classification_type": "multi-label"
        }

# Model configuration
RADIOLOGY_MODEL_CONFIG = {
    "input_size": (224, 224),
    "mean": [0.485],  # Grayscale normalization
    "std": [0.229],
    "num_classes": 14,
    "model_architecture": "densenet121",
    "threshold": 0.5,
    "image_mode": "grayscale"
}
