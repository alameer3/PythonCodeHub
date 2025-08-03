"""
Application settings and configuration management.
Handles loading configuration from files and environment variables.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """Application settings manager with support for file and environment configuration."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize settings with optional configuration file.
        
        Args:
            config_file: Path to configuration file. Defaults to resources/config.json
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_file = config_file or self._get_default_config_path()
        self._config: Dict[str, Any] = {}
        self._load_configuration()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        project_root = Path(__file__).parent.parent
        return str(project_root / "resources" / "config.json")
    
    def _load_configuration(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from file first
        self._load_from_file()
        
        # Override with environment variables
        self._load_from_environment()
        
        self.logger.info(f"Configuration loaded from {self.config_file}")
    
    def _load_from_file(self) -> None:
        """Load configuration from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                self.logger.debug(f"Loaded configuration from {self.config_file}")
            else:
                self.logger.warning(f"Configuration file not found: {self.config_file}")
                self._config = {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {self.config_file}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading config file {self.config_file}: {e}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'APP_NAME': 'app.name',
            'APP_VERSION': 'app.version',
            'LOG_LEVEL': 'logging.level',
            'DATA_DIR': 'data.directory',
            'API_KEY': 'api.key',
            'API_BASE_URL': 'api.base_url'
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(config_path, value)
                self.logger.debug(f"Loaded {config_path} from environment variable {env_var}")
    
    def _set_nested_value(self, path: str, value: Any) -> None:
        """Set a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'app.name')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        current = self._config
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        self._set_nested_value(key, value)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self._config.copy()
    
    # Convenience properties for commonly used settings
    @property
    def app_name(self) -> str:
        """Get application name."""
        return self.get('app.name', 'Python Best Practices Demo')
    
    @property
    def app_version(self) -> str:
        """Get application version."""
        return self.get('app.version', '1.0.0')
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get('logging.level', 'INFO')
    
    @property
    def data_directory(self) -> str:
        """Get data directory path."""
        return self.get('data.directory', 'data')
    
    @property
    def api_key(self) -> str:
        """Get API key."""
        return self.get('api.key', os.getenv('API_KEY', ''))
    
    @property
    def api_base_url(self) -> str:
        """Get API base URL."""
        return self.get('api.base_url', 'https://api.example.com')
