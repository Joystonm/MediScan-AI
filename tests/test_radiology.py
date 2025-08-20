# Unit tests for radiology analysis
import pytest
import torch
import numpy as np
from PIL import Image
import io
import sys
import os

# Add the backend app to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.radiology_service import RadiologyService
from app.models.radiology_model import CheXNetModel
from app.utils.preprocess import ImagePreprocessor

class TestRadiologyService:
    
    @pytest.fixture
    def radiology_service(self):
        """Create a RadiologyService instance for testing"""
        return RadiologyService()
    
    @pytest.fixture
    def sample_xray_bytes(self):
        """Create a sample X-ray image as bytes for testing"""
        # Create a grayscale image simulating an X-ray
        image = Image.new('L', (512, 512), color=128)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    def test_service_initialization(self, radiology_service):
        """Test that the service initializes correctly"""
        assert radiology_service is not None
        assert hasattr(radiology_service, 'pathology_classes')
        assert len(radiology_service.pathology_classes) == 14
    
    @pytest.mark.asyncio
    async def test_analyze_xray_with_valid_image(self, radiology_service, sample_xray_bytes):
        """Test X-ray analysis with a valid image"""
        result = await radiology_service.analyze_xray(sample_xray_bytes)
        
        # Check that result has expected structure
        assert 'findings' in result
        assert 'pathology_detected' in result
        assert 'confidence_scores' in result
        assert 'recommendations' in result
        assert 'urgency_level' in result
        
        # Check data types
        assert isinstance(result['findings'], list)
        assert isinstance(result['pathology_detected'], bool)
        assert isinstance(result['confidence_scores'], dict)
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['urgency_level'], str)
        
        # Check confidence scores
        for pathology, score in result['confidence_scores'].items():
            assert pathology in radiology_service.pathology_classes + ['Normal']
            assert 0 <= score <= 1
        
        # Check urgency level
        assert result['urgency_level'] in ['routine', 'urgent', 'emergency']
    
    @pytest.mark.asyncio
    async def test_analyze_xray_with_invalid_image(self, radiology_service):
        """Test X-ray analysis with invalid image data"""
        invalid_data = b"not an image"
        
        with pytest.raises(Exception):
            await radiology_service.analyze_xray(invalid_data)
    
    def test_preprocess_image(self, radiology_service, sample_xray_bytes):
        """Test image preprocessing"""
        processed = radiology_service._preprocess_image(sample_xray_bytes)
        
        assert isinstance(processed, np.ndarray)
        assert processed.shape == (224, 224)  # Grayscale image
        assert processed.dtype == np.float64
        assert 0 <= processed.min() and processed.max() <= 1  # Normalized
    
    def test_determine_urgency(self, radiology_service):
        """Test urgency level determination"""
        # Test emergency condition
        findings = ["Pneumothorax"]
        confidence_scores = {"Pneumothorax": 0.8, "Normal": 0.2}
        urgency = radiology_service._determine_urgency(findings, confidence_scores)
        assert urgency == "emergency"
        
        # Test urgent condition
        findings = ["Pneumonia"]
        confidence_scores = {"Pneumonia": 0.7, "Normal": 0.3}
        urgency = radiology_service._determine_urgency(findings, confidence_scores)
        assert urgency == "urgent"
        
        # Test routine condition
        findings = ["Cardiomegaly"]
        confidence_scores = {"Cardiomegaly": 0.5, "Normal": 0.5}
        urgency = radiology_service._determine_urgency(findings, confidence_scores)
        assert urgency == "routine"
        
        # Test normal condition
        findings = []
        confidence_scores = {"Normal": 0.9}
        urgency = radiology_service._determine_urgency(findings, confidence_scores)
        assert urgency == "routine"
    
    def test_generate_findings(self, radiology_service):
        """Test findings generation"""
        # Test with pathologies detected
        confidence_scores = {
            "Pneumonia": 0.7,
            "Effusion": 0.6,
            "Normal": 0.2
        }
        findings = radiology_service._generate_findings(confidence_scores)
        
        assert len(findings) >= 1
        assert any("pneumonia" in finding.lower() for finding in findings)
        assert any("effusion" in finding.lower() for finding in findings)
        
        # Test with no pathologies
        confidence_scores = {"Normal": 0.9, "Pneumonia": 0.1}
        findings = radiology_service._generate_findings(confidence_scores)
        
        assert len(findings) == 1
        assert "no acute abnormalities" in findings[0].lower()

class TestCheXNetModel:
    
    @pytest.fixture
    def chexnet_model(self):
        """Create a CheXNetModel instance for testing"""
        return CheXNetModel()
    
    def test_model_initialization(self, chexnet_model):
        """Test model initialization"""
        assert chexnet_model is not None
        assert chexnet_model.num_classes == 14
        assert len(chexnet_model.class_names) == 14
        assert chexnet_model.device is not None
    
    def test_model_info(self, chexnet_model):
        """Test model information retrieval"""
        info = chexnet_model.get_model_info()
        
        assert 'model_type' in info
        assert 'dataset' in info
        assert 'num_classes' in info
        assert 'class_names' in info
        assert 'input_size' in info
        assert 'device' in info
        assert 'loaded' in info
        assert 'classification_type' in info
        
        assert info['num_classes'] == 14
        assert info['input_size'] == (224, 224)
        assert info['classification_type'] == 'multi-label'
    
    def test_get_findings_report(self, chexnet_model):
        """Test findings report generation"""
        # Test with pathologies detected
        predictions = {
            "detected_pathologies": ["Pneumonia", "Effusion"],
            "confidence_scores": {
                "Pneumonia": 0.8,
                "Effusion": 0.6,
                "Normal": 0.2
            },
            "pathology_detected": True
        }
        
        findings = chexnet_model.get_findings_report(predictions)
        
        assert len(findings) == 2
        assert any("pneumonia" in finding.lower() for finding in findings)
        assert any("effusion" in finding.lower() for finding in findings)
        
        # Test with no pathologies
        predictions = {
            "detected_pathologies": [],
            "confidence_scores": {"Normal": 0.9},
            "pathology_detected": False
        }
        
        findings = chexnet_model.get_findings_report(predictions)
        
        assert len(findings) == 1
        assert "no acute cardiopulmonary abnormality" in findings[0].lower()

class TestRadiologyPreprocessing:
    
    @pytest.fixture
    def preprocessor(self):
        """Create an ImagePreprocessor instance"""
        return ImagePreprocessor()
    
    @pytest.fixture
    def sample_xray_bytes(self):
        """Create sample X-ray image bytes"""
        image = Image.new('L', (512, 512), color=100)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def test_preprocess_xray_image(self, preprocessor, sample_xray_bytes):
        """Test X-ray image preprocessing"""
        tensor = preprocessor.preprocess_xray_image(sample_xray_bytes)
        
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (1, 1, 224, 224)  # Batch, Channels, Height, Width
        assert tensor.dtype == torch.float32
    
    def test_histogram_equalization(self, preprocessor):
        """Test histogram equalization"""
        # Create a low-contrast image
        image = Image.new('L', (100, 100), color=100)
        
        # Apply histogram equalization
        equalized = preprocessor._apply_histogram_equalization(image)
        
        assert isinstance(equalized, Image.Image)
        assert equalized.mode == 'L'
        assert equalized.size == image.size

# Integration tests
class TestRadiologyIntegration:
    
    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self):
        """Test the complete radiology analysis pipeline"""
        # Create test X-ray image
        image = Image.new('L', (512, 512), color=128)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        image_data = img_bytes.getvalue()
        
        # Initialize service
        service = RadiologyService()
        
        # Run analysis
        result = await service.analyze_xray(image_data)
        
        # Verify complete result structure
        expected_keys = [
            'findings', 'pathology_detected', 'confidence_scores',
            'recommendations', 'urgency_level'
        ]
        
        for key in expected_keys:
            assert key in result
        
        # Verify findings are meaningful
        assert len(result['findings']) > 0
        assert all(isinstance(finding, str) for finding in result['findings'])
        
        # Verify confidence scores for all pathologies
        assert len(result['confidence_scores']) >= 14
        
        # Verify recommendations
        assert len(result['recommendations']) > 0
        assert all(isinstance(rec, str) for rec in result['recommendations'])
    
    @pytest.mark.asyncio
    async def test_emergency_detection(self):
        """Test emergency condition detection"""
        # This would require a mock model that returns high confidence for emergency conditions
        # For now, we'll test the urgency determination logic
        
        service = RadiologyService()
        
        # Test emergency urgency
        findings = ["Pneumothorax"]
        confidence_scores = {"Pneumothorax": 0.9}
        urgency = service._determine_urgency(findings, confidence_scores)
        
        assert urgency == "emergency"
    
    def test_pathology_classification_coverage(self):
        """Test that all expected pathologies are covered"""
        service = RadiologyService()
        
        expected_pathologies = [
            "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
            "Mass", "Nodule", "Pneumonia", "Pneumothorax",
            "Consolidation", "Edema", "Emphysema", "Fibrosis",
            "Pleural_Thickening", "Hernia"
        ]
        
        assert len(service.pathology_classes) == len(expected_pathologies)
        
        for pathology in expected_pathologies:
            assert pathology in service.pathology_classes

if __name__ == "__main__":
    pytest.main([__file__])
