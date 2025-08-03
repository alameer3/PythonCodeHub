"""
Configuration package for the application.
This package handles all configuration-related functionality including
settings management, environment variables, and logging configuration.
"""

from .settings import Settings
from .logging_config import setup_logging

__all__ = ['Settings', 'setup_logging']
