# Skin cancer model loader and configuration
import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, Any
import os

class ISICSkinModel:
    """
    ISIC skin cancer detection model wrapper
    """
    
    def __init__(self, model_path: str = None, num_classes: int = 7):
        self.model_path = model_path or os.getenv("SKIN_MODEL_PATH", "models/isic_model.pth")
        self.num_classes = num_classes
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Class names for ISIC dataset
        self.class_names = [
            "Melanoma",
            "Melanocytic nevus", 
            "Basal cell carcinoma",
            "Actinic keratosis",
            "Benign keratosis",
            "Dermatofibroma",
            "Vascular lesion"
        ]
    
    def load_model(self) -> bool:
        """
        Load the pretrained ISIC model
        """
        try:
            # Create model architecture (ResNet-50 based)
            self.model = models.resnet50(pretrained=False)
            
            # Modify final layer for skin cancer classification
            num_features = self.model.fc.in_features
            self.model.fc = nn.Linear(num_features, self.num_classes)
            
            # Load pretrained weights if available
            if os.path.exists(self.model_path):
                checkpoint = torch.load(self.model_path, map_location=self.device)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                print(f"Loaded skin cancer model from {self.model_path}")
            else:
                print(f"Model file not found at {self.model_path}. Using randomly initialized weights.")
            
            self.model.to(self.device)
            self.model.eval()
            return True
            
        except Exception as e:
            print(f"Error loading skin cancer model: {str(e)}")
            return False
    
    def predict(self, image_tensor: torch.Tensor) -> Dict[str, Any]:
        """
        Make prediction on preprocessed image tensor
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
            return {
                "predicted_class": self.class_names[predicted.item()],
                "confidence": confidence.item(),
                "all_probabilities": {
                    class_name: prob.item() 
                    for class_name, prob in zip(self.class_names, probabilities[0])
                }
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information and metadata
        """
        return {
            "model_type": "ResNet-50",
            "dataset": "ISIC 2019",
            "num_classes": self.num_classes,
            "class_names": self.class_names,
            "input_size": (224, 224),
            "device": str(self.device),
            "loaded": self.model is not None
        }

# Model configuration
SKIN_MODEL_CONFIG = {
    "input_size": (224, 224),
    "mean": [0.485, 0.456, 0.406],  # ImageNet normalization
    "std": [0.229, 0.224, 0.225],
    "num_classes": 7,
    "model_architecture": "resnet50"
}
