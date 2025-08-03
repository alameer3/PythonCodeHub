"""
Main application class that orchestrates all components.
This is the central hub that coordinates different modules and services.
"""

import logging
from typing import Any, Dict
from argparse import Namespace

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config.settings import Settings

from data.processor import DataProcessor
from services.file_service import FileService
from services.api_service import APIService
from utils.helpers import format_duration, validate_email


class Application:
    """Main application class that coordinates all components."""
    
    def __init__(self, settings):
        """
        Initialize the application with configuration.
        
        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize services
        self.file_service = FileService(settings)
        self.api_service = APIService(settings)
        self.data_processor = DataProcessor(settings)
        
        self.logger.info(f"Application initialized: {settings.app_name} v{settings.app_version}")
    
    def run(self, args: Namespace) -> int:
        """
        Run the application with given arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            self.logger.info(f"Running command: {args.command}")
            
            # Route to appropriate handler based on command
            if args.command == 'process':
                return self._handle_process_command(args)
            elif args.command == 'validate':
                return self._handle_validate_command(args)
            elif args.command == 'info':
                return self._handle_info_command(args)
            elif args.command == 'demo':
                return self._handle_demo_command(args)
            else:
                raise RuntimeError(f"Unknown command: {args.command}")
                
        except Exception as e:
            self.logger.error(f"Error running application: {e}")
            raise RuntimeError(f"Application execution failed: {e}")
    
    def _handle_process_command(self, args: Namespace) -> int:
        """Handle the process command."""
        self.logger.info(f"Processing file: {args.file}")
        
        # Check if file exists
        if not self.file_service.exists(args.file):
            raise FileNotFoundError(f"File not found: {args.file}")
        
        # Read and process data
        data = self.file_service.read_csv(args.file)
        processed_data = self.data_processor.process_dataset(data)
        
        # Generate output filename if not provided
        output_file = args.output or f"processed_{args.file}"
        
        # Save processed data
        self.file_service.write_csv(output_file, processed_data)
        
        self.logger.info(f"Data processed successfully. Output saved to: {output_file}")
        print(f"✓ Processed {len(data)} records")
        print(f"✓ Output saved to: {output_file}")
        
        return 0
    
    def _handle_validate_command(self, args: Namespace) -> int:
        """Handle the validate command."""
        self.logger.info(f"Validating file: {args.file}")
        
        # Check if file exists
        if not self.file_service.exists(args.file):
            raise FileNotFoundError(f"File not found: {args.file}")
        
        # Read and validate data
        data = self.file_service.read_csv(args.file)
        validation_results = self.data_processor.validate_dataset(data)
        
        # Display validation results
        print(f"Validation Results for {args.file}:")
        print(f"Total records: {validation_results['total_records']}")
        print(f"Valid records: {validation_results['valid_records']}")
        print(f"Invalid records: {validation_results['invalid_records']}")
        
        if validation_results['errors']:
            print("\nValidation Errors:")
            for error in validation_results['errors'][:10]:  # Show first 10 errors
                print(f"  - Row {error['row']}: {error['message']}")
            
            if len(validation_results['errors']) > 10:
                print(f"  ... and {len(validation_results['errors']) - 10} more errors")
        
        return 0 if validation_results['invalid_records'] == 0 else 1
    
    def _handle_info_command(self, args: Namespace) -> int:
        """Handle the info command."""
        print(f"{self.settings.app_name} v{self.settings.app_version}")
        print("=" * 50)
        print("Configuration:")
        
        config = self.settings.get_all()
        self._print_dict(config, indent=2)
        
        print("\nSystem Information:")
        print(f"  Log Level: {self.settings.log_level}")
        print(f"  Data Directory: {self.settings.data_directory}")
        
        return 0
    
    def _handle_demo_command(self, args: Namespace) -> int:
        """Handle the demo command to showcase application features."""
        print(f"🚀 {self.settings.app_name} Demo")
        print("=" * 50)
        
        # Demonstrate utility functions
        print("\n📧 Email Validation Demo:")
        test_emails = ["user@example.com", "invalid-email", "test@domain.co.uk"]
        for email in test_emails:
            is_valid = validate_email(email)
            status = "✓ Valid" if is_valid else "✗ Invalid"
            print(f"  {email}: {status}")
        
        # Demonstrate duration formatting
        print("\n⏱️ Duration Formatting Demo:")
        durations = [45, 150, 3661, 86400]
        for duration in durations:
            formatted = format_duration(duration)
            print(f"  {duration} seconds = {formatted}")
        
        # Demonstrate file operations
        print("\n📁 File Operations Demo:")
        sample_file = "resources/sample_data.csv"
        if self.file_service.exists(sample_file):
            data = self.file_service.read_csv(sample_file)
            print(f"  ✓ Read {len(data)} records from {sample_file}")
            
            # Show first few records
            print("  Sample data:")
            for i, record in enumerate(data[:3]):
                print(f"    Row {i+1}: {record}")
        else:
            print(f"  ⚠️ Sample file not found: {sample_file}")
        
        # Demonstrate data processing
        print("\n🔄 Data Processing Demo:")
        sample_data = [
            {"name": "John Doe", "age": "30", "email": "john@example.com"},
            {"name": "Jane Smith", "age": "25", "email": "jane@example.com"},
            {"name": "Bob Johnson", "age": "invalid", "email": "not-an-email"}
        ]
        
        validation_results = self.data_processor.validate_dataset(sample_data)
        print(f"  Total records: {validation_results['total_records']}")
        print(f"  Valid records: {validation_results['valid_records']}")
        print(f"  Invalid records: {validation_results['invalid_records']}")
        
        print("\n✨ Demo completed successfully!")
        return 0
    
    def _print_dict(self, d: Dict[str, Any], indent: int = 0) -> None:
        """Recursively print dictionary with indentation."""
        for key, value in d.items():
            if isinstance(value, dict):
                print(" " * indent + f"{key}:")
                self._print_dict(value, indent + 2)
            else:
                print(" " * indent + f"{key}: {value}")
