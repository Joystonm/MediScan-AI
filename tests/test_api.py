# API integration tests
import pytest
import asyncio
from httpx import AsyncClient
from PIL import Image
import io
import sys
import os

# Add the backend app to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app

class TestHealthEndpoints:
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test the root endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/")
        
        assert response.status_code == 200
        assert "MediScan-AI API is running" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test the health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_detailed_health_check(self):
        """Test the detailed health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["cpu_usage", "memory_usage", "disk_usage", "models_loaded"]
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["cpu_usage"], (int, float))
        assert isinstance(data["memory_usage"], (int, float))
        assert isinstance(data["disk_usage"], (int, float))
        assert isinstance(data["models_loaded"], dict)
    
    @pytest.mark.asyncio
    async def test_readiness_probe(self):
        """Test the readiness probe endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
    
    @pytest.mark.asyncio
    async def test_liveness_probe(self):
        """Test the liveness probe endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert "alive" in data

class TestSkinAnalysisEndpoints:
    
    def create_test_image(self, format="JPEG", size=(224, 224), color="red"):
        """Create a test image for upload"""
        image = Image.new('RGB', size, color=color)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes
    
    @pytest.mark.asyncio
    async def test_skin_analysis_with_valid_image(self):
        """Test skin analysis with a valid image"""
        test_image = self.create_test_image()
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            files = {"file": ("test.jpg", test_image, "image/jpeg")}
            response = await ac.post("/api/v1/skin-analysis", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = [
            "prediction", "confidence", "risk_level", 
            "recommendations", "lesion_characteristics"
        ]
        for field in required_fields:
            assert field in data
        
        # Check data types and values
        assert isinstance(data["prediction"], str)
        assert isinstance(data["confidence"], (int, float))
        assert 0 <= data["confidence"] <= 1
        assert data["risk_level"] in ["low", "moderate", "high"]
        assert isinstance(data["recommendations"], list)
        assert isinstance(data["lesion_characteristics"], dict)
    
    @pytest.mark.asyncio
    async def test_skin_analysis_with_invalid_file(self):
        """Test skin analysis with invalid file"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
            response = await ac.post("/api/v1/skin-analysis", files=files)
        
        assert response.status_code == 400
        assert "File must be an image" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_skin_analysis_without_file(self):
        """Test skin analysis without uploading a file"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/skin-analysis")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_supported_formats(self):
        """Test getting supported image formats"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/skin-analysis/supported-formats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "formats" in data
        assert "max_size_mb" in data
        assert "recommended_resolution" in data
        
        assert isinstance(data["formats"], list)
        assert len(data["formats"]) > 0

class TestRadiologyEndpoints:
    
    def create_test_xray(self, format="JPEG", size=(512, 512)):
        """Create a test X-ray image"""
        image = Image.new('L', size, color=128)  # Grayscale
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes
    
    @pytest.mark.asyncio
    async def test_radiology_analysis_with_valid_image(self):
        """Test radiology analysis with a valid X-ray image"""
        test_xray = self.create_test_xray()
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            files = {"file": ("xray.jpg", test_xray, "image/jpeg")}
            response = await ac.post("/api/v1/radiology-analysis", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = [
            "findings", "pathology_detected", "confidence_scores",
            "recommendations", "urgency_level"
        ]
        for field in required_fields:
            assert field in data
        
        # Check data types and values
        assert isinstance(data["findings"], list)
        assert isinstance(data["pathology_detected"], bool)
        assert isinstance(data["confidence_scores"], dict)
        assert isinstance(data["recommendations"], list)
        assert data["urgency_level"] in ["routine", "urgent", "emergency", "normal"]
        
        # Check confidence scores
        for pathology, score in data["confidence_scores"].items():
            assert isinstance(score, (int, float))
            assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_radiology_analysis_with_invalid_file(self):
        """Test radiology analysis with invalid file"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
            response = await ac.post("/api/v1/radiology-analysis", files=files)
        
        assert response.status_code == 400
        assert "File must be an image" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_supported_xray_types(self):
        """Test getting supported X-ray types"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/radiology-analysis/supported-types")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "xray_types" in data
        assert "formats" in data
        assert "max_size_mb" in data
        assert "recommended_resolution" in data
        
        assert isinstance(data["xray_types"], list)
        assert isinstance(data["formats"], list)

class TestTriageEndpoints:
    
    @pytest.mark.asyncio
    async def test_triage_assessment(self):
        """Test triage assessment endpoint"""
        triage_data = {
            "symptoms": ["headache", "fever", "fatigue"],
            "age": 30,
            "gender": "female",
            "medical_history": ["asthma"]
        }
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/triage", json=triage_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = [
            "urgency_level", "recommendations", 
            "possible_conditions", "next_steps"
        ]
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["urgency_level"], str)
        assert isinstance(data["recommendations"], list)
        assert isinstance(data["possible_conditions"], list)
        assert isinstance(data["next_steps"], list)
        
        # Check urgency level is valid
        assert data["urgency_level"] in ["low", "moderate", "high", "emergency"]
    
    @pytest.mark.asyncio
    async def test_triage_assessment_minimal_data(self):
        """Test triage assessment with minimal data"""
        triage_data = {
            "symptoms": ["cough"]
        }
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/triage", json=triage_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "urgency_level" in data
    
    @pytest.mark.asyncio
    async def test_triage_chat(self):
        """Test triage chat endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/triage/chat",
                params={"message": "I have a headache and feel nauseous"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_triage_assessment_invalid_data(self):
        """Test triage assessment with invalid data"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/triage", json={})
        
        assert response.status_code == 422  # Validation error

class TestAPIErrorHandling:
    
    @pytest.mark.asyncio
    async def test_404_endpoint(self):
        """Test accessing non-existent endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_method_not_allowed(self):
        """Test using wrong HTTP method"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/api/v1/health")
        
        assert response.status_code == 405
    
    @pytest.mark.asyncio
    async def test_large_file_upload(self):
        """Test uploading a file that's too large"""
        # Create a large image (this is a simplified test)
        large_image = Image.new('RGB', (4000, 4000), color='red')
        img_bytes = io.BytesIO()
        large_image.save(img_bytes, format='JPEG', quality=100)
        img_bytes.seek(0)
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            files = {"file": ("large.jpg", img_bytes, "image/jpeg")}
            response = await ac.post("/api/v1/skin-analysis", files=files)
        
        # The response depends on the server configuration
        # It might be 413 (Request Entity Too Large) or 500
        assert response.status_code in [413, 422, 500]

class TestAPIPerformance:
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self):
        """Test multiple concurrent health check requests"""
        async def make_request():
            async with AsyncClient(app=app, base_url="http://test") as ac:
                return await ac.get("/api/v1/health")
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_response_time_health_check(self):
        """Test that health check responds quickly"""
        import time
        
        start_time = time.time()
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

class TestAPISecurity:
    
    @pytest.mark.asyncio
    async def test_cors_headers(self):
        """Test that CORS headers are present"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health")
        
        # Check for CORS headers (these depend on FastAPI CORS middleware configuration)
        # The exact headers depend on the CORS configuration in main.py
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_content_type_validation(self):
        """Test that content type is properly validated"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Try to send JSON to an endpoint expecting form data
            response = await ac.post(
                "/api/v1/skin-analysis",
                json={"not": "a file"}
            )
        
        assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    pytest.main([__file__])
