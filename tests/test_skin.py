# Unit tests for skin cancer detection
import pytest
import torch
import numpy as np
from PIL import Image
import io
import sys
import os

# Add the backend app to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.skin_service import SkinCancerService
from app.models.skin_model import ISICSkinModel
from app.utils.preprocess import ImagePreprocessor

class TestSkinCancerService:
    
    @pytest.fixture
    def skin_service(self):
        """Create a SkinCancerService instance for testing"""
        return SkinCancerService()
    
    @pytest.fixture
    def sample_image_bytes(self):
        """Create a sample image as bytes for testing"""
        # Create a simple RGB image
        image = Image.new('RGB', (224, 224), color='red')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    def test_service_initialization(self, skin_service):
        """Test that the service initializes correctly"""
        assert skin_service is not None
        assert hasattr(skin_service, 'class_names')
        assert len(skin_service.class_names) == 7
    
    @pytest.mark.asyncio
    async def test_analyze_lesion_with_valid_image(self, skin_service, sample_image_bytes):
        """Test lesion analysis with a valid image"""
        result = await skin_service.analyze_lesion(sample_image_bytes)
        
        # Check that result has expected structure
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'risk_level' in result
        assert 'recommendations' in result
        assert 'lesion_characteristics' in result
        
        # Check data types
        assert isinstance(result['prediction'], str)
        assert isinstance(result['confidence'], (int, float))
        assert isinstance(result['risk_level'], str)
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['lesion_characteristics'], dict)
        
        # Check value ranges
        assert 0 <= result['confidence'] <= 1
        assert result['risk_level'] in ['low', 'moderate', 'high']
        assert result['prediction'] in skin_service.class_names
    
    @pytest.mark.asyncio
    async def test_analyze_lesion_with_invalid_image(self, skin_service):
        """Test lesion analysis with invalid image data"""
        invalid_data = b"not an image"
        
        with pytest.raises(Exception):
            await skin_service.analyze_lesion(invalid_data)
    
    def test_preprocess_image(self, skin_service, sample_image_bytes):
        """Test image preprocessing"""
        processed = skin_service._preprocess_image(sample_image_bytes)
        
        assert isinstance(processed, np.ndarray)
        assert processed.shape == (224, 224, 3)  # RGB image
        assert processed.dtype == np.float64
        assert 0 <= processed.min() and processed.max() <= 1  # Normalized
    
    def test_get_risk_level(self, skin_service):
        """Test risk level determination"""
        # Test high-risk condition
        risk = skin_service._get_risk_level("Melanoma", 0.8)
        assert risk == "high"
        
        # Test low-risk condition with high confidence
        risk = skin_service._get_risk_level("Benign keratosis", 0.9)
        assert risk == "low"
        
        # Test moderate risk due to low confidence
        risk = skin_service._get_risk_level("Melanoma", 0.5)
        assert risk == "moderate"

class TestISICSkinModel:
    
    @pytest.fixture
    def skin_model(self):
        """Create an ISICSkinModel instance for testing"""
        return ISICSkinModel()
    
    def test_model_initialization(self, skin_model):
        """Test model initialization"""
        assert skin_model is not None
        assert skin_model.num_classes == 7
        assert len(skin_model.class_names) == 7
        assert skin_model.device is not None
    
    def test_model_info(self, skin_model):
        """Test model information retrieval"""
        info = skin_model.get_model_info()
        
        assert 'model_type' in info
        assert 'dataset' in info
        assert 'num_classes' in info
        assert 'class_names' in info
        assert 'input_size' in info
        assert 'device' in info
        assert 'loaded' in info
        
        assert info['num_classes'] == 7
        assert info['input_size'] == (224, 224)

class TestImagePreprocessor:
    
    @pytest.fixture
    def preprocessor(self):
        """Create an ImagePreprocessor instance"""
        return ImagePreprocessor()
    
    @pytest.fixture
    def sample_image_bytes(self):
        """Create sample image bytes"""
        image = Image.new('RGB', (300, 300), color='blue')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def test_preprocess_skin_image(self, preprocessor, sample_image_bytes):
        """Test skin image preprocessing"""
        tensor = preprocessor.preprocess_skin_image(sample_image_bytes)
        
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (1, 3, 224, 224)  # Batch, Channels, Height, Width
        assert tensor.dtype == torch.float32
    
    def test_validate_image_valid(self, preprocessor, sample_image_bytes):
        """Test image validation with valid image"""
        is_valid, message = preprocessor.validate_image(sample_image_bytes)
        
        assert is_valid is True
        assert message == "Valid image"
    
    def test_validate_image_invalid(self, preprocessor):
        """Test image validation with invalid data"""
        invalid_data = b"not an image"
        is_valid, message = preprocessor.validate_image(invalid_data)
        
        assert is_valid is False
        assert "Invalid image" in message
    
    def test_get_image_info(self, preprocessor, sample_image_bytes):
        """Test image information extraction"""
        info = preprocessor.get_image_info(sample_image_bytes)
        
        assert 'format' in info
        assert 'mode' in info
        assert 'size' in info
        assert 'width' in info
        assert 'height' in info
        
        assert info['format'] == 'PNG'
        assert info['mode'] == 'RGB'
        assert info['width'] == 300
        assert info['height'] == 300

# Integration tests
class TestSkinAnalysisIntegration:
    
    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self):
        """Test the complete skin analysis pipeline"""
        # Create test image
        image = Image.new('RGB', (224, 224), color='red')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        image_data = img_bytes.getvalue()
        
        # Initialize service
        service = SkinCancerService()
        
        # Run analysis
        result = await service.analyze_lesion(image_data)
        
        # Verify complete result structure
        expected_keys = [
            'prediction', 'confidence', 'risk_level', 
            'recommendations', 'lesion_characteristics'
        ]
        
        for key in expected_keys:
            assert key in result
        
        # Verify recommendations are meaningful
        assert len(result['recommendations']) > 0
        assert all(isinstance(rec, str) for rec in result['recommendations'])
        
        # Verify lesion characteristics
        characteristics = result['lesion_characteristics']
        expected_char_keys = ['asymmetry', 'border_irregularity', 'color_variation', 'diameter']
        
        for key in expected_char_keys:
            assert key in characteristics

if __name__ == "__main__":
    pytest.main([__file__])
