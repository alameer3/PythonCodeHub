"""
Command handlers for the CLI interface.
Contains implementations for various command-line commands.
"""

import logging
from argparse import Namespace
from typing import Dict, Any, Callable

from config.settings import Settings
from data.processor import DataProcessor
from services.file_service import FileService
from utils.helpers import format_duration, validate_email


class CommandHandler:
    """Handler for CLI commands."""
    
    def __init__(self, settings: Settings):
        """
        Initialize command handler with settings.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self.file_service = FileService(settings)
        self.data_processor = DataProcessor(settings)
        
        # Map command names to handler methods
        self.command_map: Dict[str, Callable] = {
            'process': self.handle_process,
            'validate': self.handle_validate,
            'info': self.handle_info,
            'demo': self.handle_demo,
            'analyze': self.handle_analyze,
            'convert': self.handle_convert
        }
    
    def execute(self, args: Namespace) -> int:
        """
        Execute command based on parsed arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        command = args.command
        
        if command not in self.command_map:
            self.logger.error(f"Unknown command: {command}")
            print(f"Error: Unknown command '{command}'")
            return 1
        
        try:
            return self.command_map[command](args)
        except Exception as e:
            self.logger.error(f"Command '{command}' failed: {e}")
            print(f"Error: Command failed - {e}")
            return 1
    
    def handle_process(self, args: Namespace) -> int:
        """Handle the process command."""
        print(f"📊 Processing data file: {args.file}")
        
        if not self.file_service.exists(args.file):
            print(f"❌ Error: File '{args.file}' not found")
            return 1
        
        try:
            # Read input data
            print("📖 Reading input data...")
            data = self.file_service.read_csv(args.file)
            print(f"✅ Read {len(data)} records")
            
            # Process data
            print("🔄 Processing data...")
            processed_data = self.data_processor.process_dataset(data)
            print(f"✅ Processed {len(processed_data)} records")
            
            # Determine output file
            output_file = args.output or f"processed_{args.file}"
            
            # Write output
            print(f"💾 Writing results to: {output_file}")
            self.file_service.write_csv(output_file, processed_data)
            print("✅ Processing completed successfully")
            
            return 0
            
        except Exception as e:
            print(f"❌ Processing failed: {e}")
            return 1
    
    def handle_validate(self, args: Namespace) -> int:
        """Handle the validate command."""
        print(f"🔍 Validating data file: {args.file}")
        
        if not self.file_service.exists(args.file):
            print(f"❌ Error: File '{args.file}' not found")
            return 1
        
        try:
            # Read and validate data
            data = self.file_service.read_csv(args.file)
            results = self.data_processor.validate_dataset(data)
            
            # Display results
            total = results['total_records']
            valid = results['valid_records']
            invalid = results['invalid_records']
            
            print(f"\n📋 Validation Results:")
            print(f"   Total records: {total}")
            print(f"   Valid records: {valid} ({valid/total*100:.1f}%)")
            print(f"   Invalid records: {invalid} ({invalid/total*100:.1f}%)")
            
            if results['errors']:
                print(f"\n❌ Validation Errors ({len(results['errors'])} total):")
                
                # Show first 10 errors
                for i, error in enumerate(results['errors'][:10]):
                    print(f"   {i+1}. Row {error['row']}: {error['message']}")
                
                if len(results['errors']) > 10:
                    remaining = len(results['errors']) - 10
                    print(f"   ... and {remaining} more errors")
                
                if args.output:
                    # Save detailed error report
                    error_report = {
                        'summary': {
                            'total_records': total,
                            'valid_records': valid,
                            'invalid_records': invalid
                        },
                        'errors': results['errors']
                    }
                    self.file_service.write_json(args.output, error_report)
                    print(f"\n📄 Detailed error report saved to: {args.output}")
            else:
                print("\n✅ All records are valid!")
            
            return 0 if invalid == 0 else 1
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return 1
    
    def handle_info(self, args: Namespace) -> int:
        """Handle the info command."""
        print(f"ℹ️  {self.settings.app_name} v{self.settings.app_version}")
        print("=" * 60)
        
        print("\n🔧 Configuration:")
        config = self.settings.get_all()
        self._print_config(config, indent=3)
        
        print(f"\n🗂️  Data Directory: {self.settings.data_directory}")
        print(f"📊 Log Level: {self.settings.log_level}")
        
        if args.verbose:
            print("\n🌐 System Information:")
            import sys
            import os
            print(f"   Python Version: {sys.version}")
            print(f"   Platform: {sys.platform}")
            print(f"   Working Directory: {os.getcwd()}")
        
        return 0
    
    def handle_demo(self, args: Namespace) -> int:
        """Handle the demo command."""
        print("🚀 Python Best Practices Demo")
        print("=" * 60)
        
        # Email validation demo
        print("\n📧 Email Validation Demo:")
        test_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk", 
            "invalid-email",
            "another@test.com"
        ]
        
        for email in test_emails:
            is_valid = validate_email(email)
            status = "✅ Valid" if is_valid else "❌ Invalid"
            print(f"   {email:<30} {status}")
        
        # Duration formatting demo
        print("\n⏱️  Duration Formatting Demo:")
        durations = [30, 90, 3661, 86400, 259200]
        for duration in durations:
            formatted = format_duration(duration)
            print(f"   {duration:>6} seconds = {formatted}")
        
        # File operations demo
        print("\n📁 File Operations Demo:")
        sample_file = "resources/sample_data.csv"
        
        if self.file_service.exists(sample_file):
            try:
                data = self.file_service.read_csv(sample_file)
                print(f"   ✅ Successfully read {len(data)} records from {sample_file}")
                
                if data:
                    print("   📄 Sample records:")
                    for i, record in enumerate(data[:3]):
                        print(f"      {i+1}. {record}")
                
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
        else:
            print(f"   ⚠️  Sample file not found: {sample_file}")
            print("   💡 You can create sample data using the 'convert' command")
        
        # Data processing demo
        print("\n🔄 Data Processing Demo:")
        sample_data = [
            {"name": "John Doe", "age": "30", "email": "john@example.com"},
            {"name": "jane smith", "age": "25", "email": "JANE@EXAMPLE.COM"},
            {"name": "Bob Johnson", "age": "invalid", "email": "not-an-email"},
            {"name": "", "age": "35", "email": "missing@name.com"}
        ]
        
        print(f"   📊 Processing {len(sample_data)} sample records...")
        
        # Validate sample data
        validation_results = self.data_processor.validate_dataset(sample_data)
        print(f"   📈 Validation Results:")
        print(f"      Total: {validation_results['total_records']}")
        print(f"      Valid: {validation_results['valid_records']}")
        print(f"      Invalid: {validation_results['invalid_records']}")
        
        if validation_results['errors']:
            print(f"   ❌ Sample validation errors:")
            for error in validation_results['errors'][:3]:
                print(f"      - Row {error['row']}: {error['message']}")
        
        print("\n✨ Demo completed successfully!")
        print("💡 Try running with actual data files using other commands")
        
        return 0
    
    def handle_analyze(self, args: Namespace) -> int:
        """Handle the analyze command."""
        print(f"📊 Analyzing data file: {args.file}")
        
        if not self.file_service.exists(args.file):
            print(f"❌ Error: File '{args.file}' not found")
            return 1
        
        try:
            # Read and analyze data
            data = self.file_service.read_csv(args.file)
            analysis = self.data_processor.analyze_dataset(data)
            
            print(f"\n📈 Analysis Results:")
            print(f"   Total Records: {analysis['total_records']}")
            print(f"   Fields: {len(analysis['fields'])}")
            
            print(f"\n🏷️  Field Analysis:")
            for field in analysis['fields']:
                stats = analysis['statistics'][field]
                print(f"   {field}:")
                print(f"      Non-null: {stats['non_null_count']}/{stats['total_count']}")
                print(f"      Unique values: {stats['unique_count']}")
                
                if 'min' in stats:
                    print(f"      Range: {stats['min']:.2f} - {stats['max']:.2f}")
                    print(f"      Average: {stats['mean']:.2f}")
            
            if args.output:
                self.file_service.write_json(args.output, analysis)
                print(f"\n💾 Analysis saved to: {args.output}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return 1
    
    def handle_convert(self, args: Namespace) -> int:
        """Handle the convert command."""
        print(f"🔄 Converting file: {args.input} -> {args.output}")
        
        if not self.file_service.exists(args.input):
            print(f"❌ Error: Input file '{args.input}' not found")
            return 1
        
        try:
            input_ext = args.input.lower().split('.')[-1]
            output_ext = args.output.lower().split('.')[-1]
            
            # Read input file
            if input_ext == 'csv':
                data = self.file_service.read_csv(args.input)
            elif input_ext == 'json':
                raw_data = self.file_service.read_json(args.input)
                # Convert to list of dicts if needed
                if isinstance(raw_data, list):
                    data = raw_data
                else:
                    data = [raw_data]
            else:
                print(f"❌ Error: Unsupported input format: {input_ext}")
                return 1
            
            # Write output file
            if output_ext == 'csv':
                self.file_service.write_csv(args.output, data)
            elif output_ext == 'json':
                self.file_service.write_json(args.output, data)
            else:
                print(f"❌ Error: Unsupported output format: {output_ext}")
                return 1
            
            print(f"✅ Successfully converted {len(data)} records")
            print(f"📄 Output saved to: {args.output}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
            return 1
    
    def _print_config(self, config: Dict[str, Any], indent: int = 0) -> None:
        """Print configuration dictionary with indentation."""
        for key, value in config.items():
            if isinstance(value, dict):
                print(" " * indent + f"{key}:")
                self._print_config(value, indent + 3)
            else:
                print(" " * indent + f"{key}: {value}")
