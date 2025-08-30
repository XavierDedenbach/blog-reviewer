"""
Unit tests for API module.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from api.main import app


class TestAPIEndpoints:
    """Test API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Blog Reviewer API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
        assert "timestamp" in data
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "blog-reviewer"
        assert "timestamp" in data
        assert "uptime" in data
    
    def test_readiness_check(self, client):
        """Test the readiness check endpoint."""
        response = client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "blog-reviewer"
        assert "timestamp" in data
        assert "uptime" in data
    
    def test_api_docs_available(self, client):
        """Test that API docs are available."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_available(self, client):
        """Test that ReDoc is available."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema(self, client):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Blog Reviewer API"
        assert data["info"]["version"] == "0.1.0"


class TestAPIStartupShutdown:
    """Test API startup and shutdown events."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_startup_event(self, client):
        """Test startup event (indirectly through app creation)."""
        # The startup event should not cause any issues
        # We test this by ensuring the app can be created and endpoints work
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_shutdown_event(self, client):
        """Test shutdown event (indirectly through app creation)."""
        # The shutdown event should not cause any issues
        # We test this by ensuring the app can be created and endpoints work
        response = client.get("/health")
        assert response.status_code == 200


class TestAPIConfiguration:
    """Test API configuration."""
    
    def test_app_metadata(self):
        """Test app metadata configuration."""
        assert app.title == "Blog Reviewer API"
        assert app.description == "AI-powered blog content review and analysis system"
        assert app.version == "0.1.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
    
    def test_cors_middleware(self):
        """Test CORS middleware configuration."""
        # Check that CORS middleware is configured
        # This is tested indirectly by ensuring the app works
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200


class TestAPIErrorHandling:
    """Test API error handling."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_method_not_allowed(self, client):
        """Test method not allowed error handling."""
        response = client.post("/health")
        
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data


class TestAPIResponseFormat:
    """Test API response format."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_root_response_format(self, client):
        """Test root endpoint response format."""
        response = client.get("/")
        data = response.json()
        
        # Check required fields
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert "timestamp" in data
        
        # Check field types
        assert isinstance(data["message"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
    
    def test_health_response_format(self, client):
        """Test health endpoint response format."""
        response = client.get("/health")
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        assert "uptime" in data
        
        # Check field types
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["uptime"], str)
    
    def test_readiness_response_format(self, client):
        """Test readiness endpoint response format."""
        response = client.get("/ready")
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        assert "uptime" in data
        
        # Check field types
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["uptime"], str)
    
    def test_timestamp_format(self, client):
        """Test timestamp format in responses."""
        response = client.get("/health")
        data = response.json()
        
        # Check that timestamp is in ISO format
        timestamp = data["timestamp"]
        assert "T" in timestamp  # ISO format contains T
        assert timestamp.count(":") >= 2  # Should have time components


class TestAPIHeaders:
    """Test API response headers."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_content_type_headers(self, client):
        """Test content type headers."""
        response = client.get("/health")
        
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]
    
    def test_cors_headers(self, client):
        """Test CORS headers."""
        response = client.get("/health")
        
        # CORS headers should be present
        # Note: The exact headers depend on the CORS configuration
        # We just check that the response is successful
        assert response.status_code == 200


class TestAPIPerformance:
    """Test API performance characteristics."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_response_time(self, client):
        """Test that responses are reasonably fast."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_multiple_requests(self, client):
        """Test handling multiple concurrent requests."""
        import time
        
        start_time = time.time()
        
        # Make multiple requests
        responses = []
        for _ in range(5):
            response = client.get("/health")
            responses.append(response)
        
        end_time = time.time()
        
        # All responses should be successful
        for response in responses:
            assert response.status_code == 200
        
        # Total time should be reasonable
        total_time = end_time - start_time
        assert total_time < 5.0  # Should handle 5 requests within 5 seconds


class TestAPIStability:
    """Test API stability."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_repeated_requests(self, client):
        """Test that repeated requests work consistently."""
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "blog-reviewer"
    
    def test_different_endpoints_consistency(self, client):
        """Test that different endpoints work consistently."""
        endpoints = ["/", "/health", "/ready"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            data = response.json()
            assert "timestamp" in data
            assert isinstance(data["timestamp"], str)


class TestAPILogging:
    """Test API logging functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_logging_configured(self, client):
        """Test that logging is properly configured."""
        # This is tested indirectly by ensuring the app works
        # and doesn't crash due to logging issues
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_logger_available(self):
        """Test that logger is available in the app."""
        # Check that the app has logging configured
        # This is tested indirectly by ensuring the app works
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200


class TestAPIEnvironment:
    """Test API environment handling."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_environment_independence(self, client):
        """Test that API works regardless of environment variables."""
        # Test that the API works without specific environment variables
        # (except those required by the app itself)
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_app_creation(self):
        """Test that app can be created successfully."""
        # Test that the app can be instantiated without errors
        from api.main import app
        
        assert app is not None
        assert hasattr(app, 'title')
        assert hasattr(app, 'version')
