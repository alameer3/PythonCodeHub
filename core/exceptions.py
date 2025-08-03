"""
Custom exceptions for the application.
Provides specific exception types for different error conditions.
"""


class ApplicationError(Exception):
    """Base exception for application-specific errors."""
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize application error.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(ApplicationError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")


class DataProcessingError(ApplicationError):
    """Exception raised for data processing errors."""
    
    def __init__(self, message: str, row_number: int = None):
        super().__init__(message, "DATA_ERROR")
        self.row_number = row_number
    
    def __str__(self) -> str:
        if self.row_number is not None:
            return f"[{self.error_code}] Row {self.row_number}: {self.message}"
        return super().__str__()


class ValidationError(ApplicationError):
    """Exception raised for data validation errors."""
    
    def __init__(self, message: str, field_name: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field_name = field_name
    
    def __str__(self) -> str:
        if self.field_name:
            return f"[{self.error_code}] Field '{self.field_name}': {self.message}"
        return super().__str__()


class FileOperationError(ApplicationError):
    """Exception raised for file operation errors."""
    
    def __init__(self, message: str, file_path: str = None):
        super().__init__(message, "FILE_ERROR")
        self.file_path = file_path
    
    def __str__(self) -> str:
        if self.file_path:
            return f"[{self.error_code}] File '{self.file_path}': {self.message}"
        return super().__str__()


class APIError(ApplicationError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: str = None):
        super().__init__(message, "API_ERROR")
        self.status_code = status_code
        self.response_data = response_data
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.error_code}] HTTP {self.status_code}: {self.message}"
        return super().__str__()
