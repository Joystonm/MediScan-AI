# Image preprocessing utilities
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import io
from typing import Tuple, Union

class ImagePreprocessor:
    """
    Image preprocessing utilities for medical images
    """
    
    def __init__(self):
        # Standard ImageNet normalization
        self.imagenet_mean = [0.485, 0.456, 0.406]
        self.imagenet_std = [0.229, 0.224, 0.225]
        
        # Grayscale normalization for X-rays
        self.grayscale_mean = [0.485]
        self.grayscale_std = [0.229]
    
    def preprocess_skin_image(self, image_data: bytes, size: Tuple[int, int] = (224, 224)) -> torch.Tensor:
        """
        Preprocess skin lesion image for ISIC model
        """
        # Load image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Define transforms
        transform = transforms.Compose([
            transforms.Resize(size),
            transforms.CenterCrop(size),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.imagenet_mean, std=self.imagenet_std)
        ])
        
        # Apply transforms and add batch dimension
        image_tensor = transform(image).unsqueeze(0)
        
        return image_tensor
    
    def preprocess_xray_image(self, image_data: bytes, size: Tuple[int, int] = (224, 224)) -> torch.Tensor:
        """
        Preprocess X-ray image for CheXNet model
        """
        # Load image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Apply histogram equalization for better contrast
        image = self._apply_histogram_equalization(image)
        
        # Define transforms
        transform = transforms.Compose([
            transforms.Resize(size),
            transforms.CenterCrop(size),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.grayscale_mean, std=self.grayscale_std)
        ])
        
        # Apply transforms and add batch dimension
        image_tensor = transform(image).unsqueeze(0)
        
        return image_tensor
    
    def _apply_histogram_equalization(self, image: Image.Image) -> Image.Image:
        """
        Apply histogram equalization to improve contrast
        """
        # Convert PIL to numpy
        img_array = np.array(image)
        
        # Apply histogram equalization
        hist, bins = np.histogram(img_array.flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        cdf_normalized = cdf * hist.max() / cdf.max()
        
        # Use linear interpolation to calculate new pixel values
        img_equalized = np.interp(img_array.flatten(), bins[:-1], cdf_normalized)
        img_equalized = img_equalized.reshape(img_array.shape).astype(np.uint8)
        
        return Image.fromarray(img_equalized)
    
    def validate_image(self, image_data: bytes) -> Tuple[bool, str]:
        """
        Validate image format and size
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Check format
            if image.format not in ['JPEG', 'PNG', 'BMP']:
                return False, f"Unsupported format: {image.format}"
            
            # Check size
            width, height = image.size
            if width < 64 or height < 64:
                return False, "Image too small (minimum 64x64 pixels)"
            
            if width > 4096 or height > 4096:
                return False, "Image too large (maximum 4096x4096 pixels)"
            
            return True, "Valid image"
            
        except Exception as e:
            return False, f"Invalid image: {str(e)}"
    
    def get_image_info(self, image_data: bytes) -> dict:
        """
        Get image metadata
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            return {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height
            }
        except Exception as e:
            return {"error": str(e)}

# Preprocessing configurations
SKIN_PREPROCESS_CONFIG = {
    "input_size": (224, 224),
    "mean": [0.485, 0.456, 0.406],
    "std": [0.229, 0.224, 0.225],
    "supported_formats": ["JPEG", "PNG", "BMP"],
    "min_size": (64, 64),
    "max_size": (4096, 4096)
}

XRAY_PREPROCESS_CONFIG = {
    "input_size": (224, 224),
    "mean": [0.485],
    "std": [0.229],
    "supported_formats": ["JPEG", "PNG", "BMP", "DICOM"],
    "min_size": (64, 64),
    "max_size": (4096, 4096),
    "histogram_equalization": True
}
