"""
Configuration management for the Blog Reviewer application.

This module handles environment variable loading, validation, and provides
configuration objects for different environments.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


class EnvironmentConfig:
    """Manages environment variable loading and validation."""
    
    def __init__(self, env_file_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            env_file_path: Optional path to .env file. If None, looks for .env in project root.
        """
        self.project_root = self._get_project_root()
        self.env_file_path = env_file_path or self.project_root / ".env"
        self.config = {}
        
        # Load environment variables
        self._load_env_file()
        self._load_environment_variables()
        
    def _get_project_root(self) -> Path:
        """Get the project root directory by looking for requirements.txt."""
        current_dir = Path(__file__).parent
        
        # Go up directories until we find requirements.txt
        while current_dir != current_dir.parent:
            if (current_dir / "requirements.txt").exists():
                return current_dir
            current_dir = current_dir.parent
        
        # Fallback to parent of current file's directory
        return Path(__file__).parent.parent
        
    def _load_env_file(self) -> None:
        """Load environment variables from .env file if it exists."""
        if self.env_file_path.exists():
            if load_dotenv:
                load_dotenv(self.env_file_path)
            else:
                # Manual loading if python-dotenv is not available
                self._manual_load_env_file()
                
    def _manual_load_env_file(self) -> None:
        """Manually load .env file without python-dotenv."""
        try:
            with open(self.env_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key not in os.environ:
                            os.environ[key] = value
        except Exception as e:
            # Don't fail if .env file can't be read
            pass
            
    def _load_environment_variables(self) -> None:
        """Load and validate environment variables."""
        self.config = {
            # MongoDB Configuration
            'mongodb_url': self._get_env_var('MONGODB_URL', 'mongodb://localhost:27017'),
            'mongodb_database': self._get_env_var('MONGODB_DATABASE', 'blog_reviewer'),
            
            # Environment Settings
            'environment': self._get_env_var('ENVIRONMENT', 'development'),
            'testing': self._get_env_var('TESTING', 'false').lower() == 'true',
            'log_level': self._get_env_var('LOG_LEVEL', 'INFO'),
            
            # API Configuration
            'api_host': self._get_env_var('API_HOST', '0.0.0.0'),
            'api_port': int(self._get_env_var('API_PORT', '8000')),
            
            # Security
            'secret_key': self._get_env_var('SECRET_KEY', None),
        }
        
        # Validate configuration
        self._validate_configuration()
        
    def _get_env_var(self, key: str, default: Any = None) -> str:
        """Get environment variable with optional default."""
        return os.environ.get(key, default)
        
    def _validate_configuration(self) -> None:
        """Validate the loaded configuration."""
        errors = []
        
        # Validate MongoDB URL
        if not self._is_valid_mongodb_url(self.config['mongodb_url']):
            errors.append(f"Invalid MongoDB URL: {self.config['mongodb_url']}")
            
        # Validate database name
        if not self._is_valid_database_name(self.config['mongodb_database']):
            errors.append(f"Invalid database name: {self.config['mongodb_database']}")
            
        # Validate environment
        valid_environments = ['development', 'test', 'testing', 'production']
        if self.config['environment'] not in valid_environments:
            errors.append(f"Invalid environment: {self.config['environment']}. Must be one of: {valid_environments}")
            
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.config['log_level'].upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {self.config['log_level']}. Must be one of: {valid_log_levels}")
            
        if errors:
            raise ConfigurationError("Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
            
    def _is_valid_mongodb_url(self, url: str) -> bool:
        """Validate MongoDB URL format."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ('mongodb', 'mongodb+srv') and bool(parsed.netloc)
        except Exception:
            return False
            
    def _is_valid_database_name(self, name: str) -> bool:
        """Validate MongoDB database name."""
        if not name or not isinstance(name, str):
            return False
        
        # MongoDB database name restrictions
        invalid_chars = {'/', '\\', '.', '"', '*', '<', '>', ':', '|', '?', ' '}
        return not any(char in name for char in invalid_chars) and len(name) <= 64
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
        
    def get_mongodb_config(self) -> Dict[str, str]:
        """Get MongoDB-specific configuration."""
        return {
            'url': self.config['mongodb_url'],
            'database': self.config['mongodb_database']
        }
        
    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.config['testing'] or self.config['environment'] in ('test', 'testing')
        
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.config['environment'] == 'development'
        
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.config['environment'] == 'production'


# Global configuration instance
_config = None


def get_config() -> EnvironmentConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = EnvironmentConfig()
    return _config


def reload_config(env_file_path: Optional[Path] = None) -> EnvironmentConfig:
    """Reload the global configuration instance."""
    global _config
    _config = EnvironmentConfig(env_file_path)
    return _config