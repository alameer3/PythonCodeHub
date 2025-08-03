"""
Data models for the application.
Defines data structures and classes used throughout the application.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DataRecord:
    """Represents a data record with metadata."""
    
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    source: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def update(self, new_data: Dict[str, Any]) -> None:
        """Update the record with new data."""
        self.data.update(new_data)
        self.updated_at = datetime.now()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the data."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the data."""
        self.data[key] = value
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return {
            'data': self.data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'source': self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataRecord':
        """Create DataRecord from dictionary."""
        return cls(
            data=data.get('data', {}),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            source=data.get('source')
        )


@dataclass
class ValidationResult:
    """Represents the result of a validation operation."""
    
    is_valid: bool
    errors: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[Dict[str, str]] = field(default_factory=list)
    
    def add_error(self, field: str, message: str) -> None:
        """Add an error to the result."""
        self.errors.append({'field': field, 'message': message})
        self.is_valid = False
    
    def add_warning(self, field: str, message: str) -> None:
        """Add a warning to the result."""
        self.warnings.append({'field': field, 'message': message})
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_error_messages(self) -> List[str]:
        """Get list of error messages."""
        return [error['message'] for error in self.errors]
    
    def get_warning_messages(self) -> List[str]:
        """Get list of warning messages."""
        return [warning['message'] for warning in self.warnings]


@dataclass
class ProcessingResult:
    """Represents the result of a data processing operation."""
    
    success: bool
    processed_count: int
    error_count: int
    processing_time: float
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, row: int, message: str, data: Any = None) -> None:
        """Add an error to the processing result."""
        self.errors.append({
            'row': row,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        self.error_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'success': self.success,
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'processing_time': self.processing_time,
            'errors': self.errors,
            'metadata': self.metadata
        }


@dataclass
class APIResponse:
    """Represents an API response."""
    
    status_code: int
    data: Any
    headers: Dict[str, str] = field(default_factory=dict)
    response_time: float = 0.0
    
    @property
    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return 200 <= self.status_code < 300
    
    @property
    def is_error(self) -> bool:
        """Check if the response indicates an error."""
        return self.status_code >= 400
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'status_code': self.status_code,
            'data': self.data,
            'headers': self.headers,
            'response_time': self.response_time,
            'is_success': self.is_success,
            'is_error': self.is_error
        }
