"""
Data processing module for handling various data operations.
Provides functionality for processing, transforming, and analyzing data.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from config.settings import Settings
from data.validator import DataValidator
from data.models import DataRecord, ValidationResult
# from core.exceptions import DataProcessingError


class DataProcessor:
    """Main data processor class for handling data operations."""
    
    def __init__(self, settings: Settings):
        """
        Initialize data processor with configuration.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validator = DataValidator()
        
    def process_dataset(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a dataset by cleaning, transforming, and enriching data.
        
        Args:
            data: List of data records as dictionaries
            
        Returns:
            Processed data with transformations applied
        """
        self.logger.info(f"Processing dataset with {len(data)} records")
        
        processed_data = []
        errors = []
        
        for i, record in enumerate(data):
            try:
                processed_record = self._process_record(record, i)
                processed_data.append(processed_record)
            except Exception as e:
                error_msg = f"Error processing record {i}: {e}"
                self.logger.warning(error_msg)
                errors.append({"row": i, "error": str(e)})
        
        self.logger.info(f"Processed {len(processed_data)} records successfully, {len(errors)} errors")
        
        if errors:
            self.logger.warning(f"Processing completed with {len(errors)} errors")
        
        return processed_data
    
    def _process_record(self, record: Dict[str, Any], row_index: int) -> Dict[str, Any]:
        """
        Process a single data record.
        
        Args:
            record: Data record as dictionary
            row_index: Index of the record for error reporting
            
        Returns:
            Processed record
        """
        try:
            # Create a copy to avoid modifying original
            processed = record.copy()
            
            # Clean and normalize data
            processed = self._clean_record(processed)
            
            # Apply transformations
            processed = self._transform_record(processed)
            
            # Add metadata
            processed['_processed_at'] = datetime.now().isoformat()
            processed['_row_index'] = row_index
            
            return processed
            
        except Exception as e:
            raise RuntimeError(f"Failed to process record {row_index}: {e}")
    
    def _clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize record data."""
        cleaned = {}
        
        for key, value in record.items():
            # Clean key: lowercase and replace spaces with underscores
            clean_key = key.lower().replace(' ', '_').replace('-', '_')
            
            # Clean value: strip whitespace, handle empty values
            if isinstance(value, str):
                clean_value = value.strip()
                # Convert empty strings to None
                clean_value = None if clean_value == '' else clean_value
            else:
                clean_value = value
            
            cleaned[clean_key] = clean_value
        
        return cleaned
    
    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transformations to record data."""
        transformed = record.copy()
        
        # Transform age to integer if present
        if 'age' in transformed and transformed['age'] is not None:
            try:
                transformed['age'] = int(transformed['age'])
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid age value: {transformed['age']}")
                transformed['age'] = None
        
        # Normalize email to lowercase
        if 'email' in transformed and transformed['email'] is not None:
            transformed['email'] = transformed['email'].lower()
        
        # Capitalize name fields
        for field in ['name', 'first_name', 'last_name']:
            if field in transformed and transformed[field] is not None:
                transformed[field] = transformed[field].title()
        
        # Add derived fields
        if 'age' in transformed and transformed['age'] is not None:
            transformed['age_category'] = self._categorize_age(transformed['age'])
        
        return transformed
    
    def _categorize_age(self, age: int) -> str:
        """Categorize age into groups."""
        if age < 18:
            return 'Minor'
        elif age < 30:
            return 'Young Adult'
        elif age < 50:
            return 'Adult'
        elif age < 65:
            return 'Middle Aged'
        else:
            return 'Senior'
    
    def validate_dataset(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a dataset and return validation results.
        
        Args:
            data: List of data records
            
        Returns:
            Validation results summary
        """
        self.logger.info(f"Validating dataset with {len(data)} records")
        
        validation_results = {
            'total_records': len(data),
            'valid_records': 0,
            'invalid_records': 0,
            'errors': []
        }
        
        for i, record in enumerate(data):
            try:
                result = self.validator.validate_record(record)
                if result.is_valid:
                    validation_results['valid_records'] += 1
                else:
                    validation_results['invalid_records'] += 1
                    for error in result.errors:
                        validation_results['errors'].append({
                            'row': i + 1,
                            'field': error.get('field', 'unknown'),
                            'message': error.get('message', 'Validation error')
                        })
            except Exception as e:
                validation_results['invalid_records'] += 1
                validation_results['errors'].append({
                    'row': i + 1,
                    'field': 'general',
                    'message': f"Validation error: {e}"
                })
        
        self.logger.info(
            f"Validation complete: {validation_results['valid_records']} valid, "
            f"{validation_results['invalid_records']} invalid"
        )
        
        return validation_results
    
    def analyze_dataset(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze dataset and return statistics.
        
        Args:
            data: List of data records
            
        Returns:
            Dataset analysis results
        """
        self.logger.info(f"Analyzing dataset with {len(data)} records")
        
        if not data:
            return {'total_records': 0, 'fields': [], 'statistics': {}}
        
        # Get all unique fields
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        analysis = {
            'total_records': len(data),
            'fields': list(all_fields),
            'statistics': {}
        }
        
        # Analyze each field
        for field in all_fields:
            field_stats = self._analyze_field(data, field)
            analysis['statistics'][field] = field_stats
        
        return analysis
    
    def _analyze_field(self, data: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
        """Analyze a specific field across all records."""
        values = [record.get(field) for record in data]
        non_null_values = [v for v in values if v is not None]
        
        stats = {
            'total_count': len(values),
            'non_null_count': len(non_null_values),
            'null_count': len(values) - len(non_null_values),
            'unique_count': len(set(non_null_values)) if non_null_values else 0
        }
        
        if non_null_values:
            # Check if values are numeric
            numeric_values = []
            for value in non_null_values:
                try:
                    numeric_values.append(float(value))
                except (ValueError, TypeError):
                    pass
            
            if numeric_values:
                stats['min'] = min(numeric_values)
                stats['max'] = max(numeric_values)
                stats['mean'] = sum(numeric_values) / len(numeric_values)
        
        return stats
