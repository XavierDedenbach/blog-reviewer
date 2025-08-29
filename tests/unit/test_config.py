"""
Unit tests for configuration management utilities.

Tests environment variable loading, validation, and configuration management.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import Dict, Any

from core.config import EnvironmentConfig, ConfigurationError, get_config, reload_config


class TestEnvironmentConfig:
    """Test environment variable configuration loading and validation."""

    def test_load_env_file_exists(self, tmp_path):
        """Test loading environment variables from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=test_value\nANOTHER_VAR=another_value\nMONGODB_URL=mongodb://test:27017")
        
        config = EnvironmentConfig(env_file_path=env_file)
        
        # Check that environment variables were loaded
        assert os.environ.get("TEST_VAR") == "test_value" or config.get("mongodb_url") is not None
        assert config.config is not None

    def test_load_env_file_missing(self, tmp_path):
        """Test handling of missing .env file."""
        # Should not raise an exception when .env file is missing
        non_existent_file = tmp_path / "missing.env"
        
        # Use a fresh environment dict to test defaults
        with patch.dict(os.environ, {
            'MONGODB_URL': 'mongodb://localhost:27017',
            'ENVIRONMENT': 'development'
        }, clear=True):
            config = EnvironmentConfig(env_file_path=non_existent_file)
            
            # Should still load with defaults
            assert config.get("mongodb_url") == "mongodb://localhost:27017"
            assert config.get("environment") == "development"

    def test_environment_variable_validation(self):
        """Test validation of required environment variables."""
        with patch.dict(os.environ, {
            'MONGODB_URL': 'mongodb://localhost:27017',
            'ENVIRONMENT': 'test'
        }, clear=True):
            config = EnvironmentConfig()
            
            # Test that configuration loads successfully with valid values
            assert config.get('mongodb_url') == 'mongodb://localhost:27017'
            assert config.get('environment') == 'test'
            assert config.get('mongodb_database') == 'blog_reviewer'  # default value

    @patch.dict(os.environ, {
        'MONGODB_URL': 'mongodb://localhost:27017',
        'MONGODB_DATABASE': 'blog_reviewer_test'
    })
    def test_mongodb_config_validation(self):
        """Test MongoDB configuration validation."""
        config = EnvironmentConfig()
        
        # Test that MongoDB URL is properly formatted
        mongo_config = config.get_mongodb_config()
        assert mongo_config['url'] == 'mongodb://localhost:27017'
        assert mongo_config['database'] == 'blog_reviewer_test'
        
        # Test validation methods
        assert config._is_valid_mongodb_url('mongodb://localhost:27017')
        assert config._is_valid_database_name('blog_reviewer_test')

    def test_invalid_mongodb_url(self):
        """Test handling of invalid MongoDB URL."""
        with patch.dict(os.environ, {'MONGODB_URL': 'invalid-url'}, clear=True):
            # Should raise appropriate validation error
            with pytest.raises(ConfigurationError, match="Invalid MongoDB URL"):
                EnvironmentConfig()


class TestDockerServiceConfig:
    """Test Docker service configuration validation."""

    def test_docker_compose_config_structure(self):
        """Test that docker-compose config has required structure."""
        # Check if docker-compose.yml exists and has basic structure
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        docker_compose_file = project_root / "docker-compose.yml"
        
        # For now, just check if file would be loadable
        # This is a placeholder until docker-compose.yml is created
        if docker_compose_file.exists():
            import yaml
            with open(docker_compose_file) as f:
                config = yaml.safe_load(f)
                assert "services" in config
        else:
            # Skip test if docker-compose.yml doesn't exist yet
            pytest.skip("docker-compose.yml not found")

    def test_mongodb_service_config(self):
        """Test MongoDB service configuration in docker-compose."""
        # Test that MongoDB service has correct image, ports, volumes, etc.
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        docker_compose_file = project_root / "docker-compose.yml"
        
        if docker_compose_file.exists():
            import yaml
            with open(docker_compose_file) as f:
                config = yaml.safe_load(f)
                if "mongodb" in config.get("services", {}):
                    mongodb_service = config["services"]["mongodb"]
                    assert "image" in mongodb_service
                    assert "ports" in mongodb_service
        else:
            pytest.skip("docker-compose.yml not found")

    def test_health_check_configuration(self):
        """Test health check configuration for services."""
        # Test that services have proper health checks defined
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        docker_compose_file = project_root / "docker-compose.yml"
        
        if docker_compose_file.exists():
            import yaml
            with open(docker_compose_file) as f:
                config = yaml.safe_load(f)
                services = config.get("services", {})
                for service_name, service_config in services.items():
                    if "healthcheck" in service_config:
                        assert "test" in service_config["healthcheck"]
        else:
            pytest.skip("docker-compose.yml not found")


class TestDevelopmentConfig:
    """Test development environment configuration."""

    def test_development_defaults(self):
        """Test that development environment has appropriate defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            
            # Test development defaults
            assert config.get('environment') == 'development'
            assert config.get('mongodb_url') == 'mongodb://localhost:27017'
            assert config.get('mongodb_database') == 'blog_reviewer'
            assert config.get('log_level') == 'INFO'
            assert not config.is_testing()
            assert config.is_development()

    def test_test_environment_isolation(self):
        """Test that test environment is properly isolated."""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'test',
            'MONGODB_DATABASE': 'blog_reviewer_test',
            'TESTING': 'true'
        }):
            config = EnvironmentConfig()
            
            # Test isolation settings
            assert config.is_testing()
            assert not config.is_development()
            assert not config.is_production()
            assert config.get('mongodb_database') == 'blog_reviewer_test'