"""
Data validation module for validating data records and fields.
Provides comprehensive validation rules and error reporting.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from data.models import ValidationResult
# from core.exceptions import ValidationError


class DataValidator:
    """Data validator class for validating records and fields."""
    
    def __init__(self):
        """Initialize data validator."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Common validation patterns
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        self.phone_pattern = re.compile(
            r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
        )
    
    def validate_record(self, record: Dict[str, Any]) -> ValidationResult:
        """
        Validate a complete data record.
        
        Args:
            record: Data record to validate
            
        Returns:
            ValidationResult object with validation status and errors
        """
        errors = []
        
        # Check for required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if not self._has_value(record, field):
                errors.append({
                    'field': field,
                    'message': f"Required field '{field}' is missing or empty"
                })
        
        # Validate individual fields
        if 'email' in record and self._has_value(record, 'email'):
            if not self.validate_email(record['email']):
                errors.append({
                    'field': 'email',
                    'message': f"Invalid email format: {record['email']}"
                })
        
        if 'age' in record and self._has_value(record, 'age'):
            age_error = self.validate_age(record['age'])
            if age_error:
                errors.append({
                    'field': 'age',
                    'message': age_error
                })
        
        if 'phone' in record and self._has_value(record, 'phone'):
            if not self.validate_phone(record['phone']):
                errors.append({
                    'field': 'phone',
                    'message': f"Invalid phone format: {record['phone']}"
                })
        
        if 'date_of_birth' in record and self._has_value(record, 'date_of_birth'):
            date_error = self.validate_date(record['date_of_birth'])
            if date_error:
                errors.append({
                    'field': 'date_of_birth',
                    'message': date_error
                })
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def _has_value(self, record: Dict[str, Any], field: str) -> bool:
        """Check if a field has a non-empty value."""
        value = record.get(field)
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == '':
            return False
        return True
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(email, str):
            return False
        
        return bool(self.email_pattern.match(email.strip()))
    
    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(phone, str):
            return False
        
        return bool(self.phone_pattern.match(phone.strip()))
    
    def validate_age(self, age: Any) -> Optional[str]:
        """
        Validate age value.
        
        Args:
            age: Age value to validate
            
        Returns:
            Error message if invalid, None if valid
        """
        try:
            age_int = int(age)
            if age_int < 0:
                return "Age cannot be negative"
            if age_int > 150:
                return "Age cannot be greater than 150"
            return None
        except (ValueError, TypeError):
            return f"Age must be a number, got: {age}"
    
    def validate_date(self, date_str: str, date_format: str = "%Y-%m-%d") -> Optional[str]:
        """
        Validate date string format.
        
        Args:
            date_str: Date string to validate
            date_format: Expected date format
            
        Returns:
            Error message if invalid, None if valid
        """
        if not isinstance(date_str, str):
            return f"Date must be a string, got: {type(date_str).__name__}"
        
        try:
            parsed_date = datetime.strptime(date_str.strip(), date_format)
            
            # Check if date is not in the future
            if parsed_date > datetime.now():
                return "Date cannot be in the future"
            
            # Check if date is reasonable (not too old)
            if parsed_date.year < 1900:
                return "Date cannot be before year 1900"
            
            return None
        except ValueError as e:
            return f"Invalid date format. Expected {date_format}, got: {date_str}"
    
    def validate_required_fields(self, record: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        Validate that all required fields are present and non-empty.
        
        Args:
            record: Data record to validate
            required_fields: List of required field names
            
        Returns:
            List of missing field names
        """
        missing_fields = []
        
        for field in required_fields:
            if not self._has_value(record, field):
                missing_fields.append(field)
        
        return missing_fields
    
    def validate_data_types(self, record: Dict[str, Any], type_mapping: Dict[str, type]) -> List[str]:
        """
        Validate data types for specified fields.
        
        Args:
            record: Data record to validate
            type_mapping: Dictionary mapping field names to expected types
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        for field, expected_type in type_mapping.items():
            if field in record and record[field] is not None:
                value = record[field]
                
                # Try to convert string values to expected type
                if isinstance(value, str) and expected_type != str:
                    try:
                        if expected_type == int:
                            int(value)
                        elif expected_type == float:
                            float(value)
                        elif expected_type == bool:
                            value.lower() in ['true', '1', 'yes', 'on']
                    except ValueError:
                        errors.append(
                            f"Field '{field}' should be {expected_type.__name__}, got: {value}"
                        )
                elif not isinstance(value, expected_type) and not isinstance(value, str):
                    errors.append(
                        f"Field '{field}' should be {expected_type.__name__}, "
                        f"got: {type(value).__name__}"
                    )
        
        return errors
