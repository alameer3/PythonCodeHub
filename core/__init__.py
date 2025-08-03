"""
Core application package.
Contains the main application logic, exceptions, and core functionality.
"""

from .application import Application
from .exceptions import ApplicationError, ConfigurationError, DataProcessingError

__all__ = ['Application', 'ApplicationError', 'ConfigurationError', 'DataProcessingError']
