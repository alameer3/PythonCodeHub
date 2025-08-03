"""
Command line argument parser for the application.
Defines all available commands and their arguments.
"""

import argparse
from typing import Optional


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the main argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='python-best-practices',
        description='Python Best Practices Demo Application - A well-structured Python project demonstrating code organization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s process data.csv                    # Process a CSV file
  %(prog)s process data.csv -o output.csv      # Process with custom output
  %(prog)s validate data.csv                   # Validate data file
  %(prog)s validate data.csv -o errors.json    # Validate with error report
  %(prog)s info                                # Show application info
  %(prog)s info --verbose                      # Show detailed system info
  %(prog)s demo                                # Run feature demonstration
  %(prog)s analyze data.csv                    # Analyze data statistics
  %(prog)s convert data.csv data.json          # Convert between formats

For more information, visit: https://github.com/your-repo/python-best-practices
        """
    )
    
    # Global options
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (default: resources/config.json)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set logging level (overrides config)'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest='command',
        title='Available Commands',
        description='Choose a command to execute',
        help='Command to run'
    )
    
    # Process command
    process_parser = subparsers.add_parser(
        'process',
        help='Process data file with cleaning and transformation',
        description='Process a data file by applying cleaning, validation, and transformation operations'
    )
    process_parser.add_argument(
        'file',
        type=str,
        help='Input data file to process (CSV format)'
    )
    process_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (default: processed_<input_file>)'
    )
    process_parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip data validation step'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate data file for correctness',
        description='Validate data file and report any issues found'
    )
    validate_parser.add_argument(
        'file',
        type=str,
        help='Data file to validate (CSV format)'
    )
    validate_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file for detailed error report (JSON format)'
    )
    validate_parser.add_argument(
        '--strict',
        action='store_true',
        help='Use strict validation rules'
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Display application and system information',
        description='Show application configuration and system details'
    )
    info_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed system information'
    )
    
    # Demo command
    demo_parser = subparsers.add_parser(
        'demo',
        help='Run application feature demonstration',
        description='Demonstrate various features and capabilities of the application'
    )
    demo_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run interactive demo with user input'
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze data file and generate statistics',
        description='Perform statistical analysis on data file and generate insights'
    )
    analyze_parser.add_argument(
        'file',
        type=str,
        help='Data file to analyze (CSV format)'
    )
    analyze_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file for analysis results (JSON format)'
    )
    analyze_parser.add_argument(
        '--include-nulls',
        action='store_true',
        help='Include null value analysis'
    )
    
    # Convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert between different file formats',
        description='Convert data files between CSV and JSON formats'
    )
    convert_parser.add_argument(
        'input',
        type=str,
        help='Input file path (CSV or JSON)'
    )
    convert_parser.add_argument(
        'output',
        type=str,
        help='Output file path (CSV or JSON)'
    )
    convert_parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )
    
    # Set default command if none specified
    parser.set_defaults(command='demo')
    
    return parser


def validate_arguments(args: argparse.Namespace) -> Optional[str]:
    """
    Validate parsed arguments for consistency and requirements.
    
    Args:
        args: Parsed arguments from ArgumentParser
        
    Returns:
        Error message if validation fails, None if valid
    """
    # Validate file extensions for convert command
    if args.command == 'convert':
        input_ext = args.input.lower().split('.')[-1]
        output_ext = args.output.lower().split('.')[-1]
        
        supported_formats = ['csv', 'json']
        
        if input_ext not in supported_formats:
            return f"Unsupported input format: .{input_ext}. Supported: {', '.join(supported_formats)}"
        
        if output_ext not in supported_formats:
            return f"Unsupported output format: .{output_ext}. Supported: {', '.join(supported_formats)}"
        
        if input_ext == output_ext:
            return "Input and output formats cannot be the same"
    
    # Validate output file extensions for specific commands
    if hasattr(args, 'output') and args.output:
        if args.command == 'validate' and not args.output.lower().endswith('.json'):
            return "Validation output file must have .json extension"
        
        if args.command == 'analyze' and not args.output.lower().endswith('.json'):
            return "Analysis output file must have .json extension"
        
        if args.command == 'process' and not args.output.lower().endswith('.csv'):
            return "Process output file must have .csv extension"
    
    return None


def add_custom_help_formatter() -> type:
    """
    Create custom help formatter for better command help display.
    
    Returns:
        Custom formatter class
    """
    class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
        def _format_action(self, action):
            # Add extra spacing for subcommands
            if action.dest == 'command':
                return super()._format_action(action) + '\n'
            return super()._format_action(action)
        
        def _format_usage(self, usage, actions, groups, prefix):
            # Customize usage line
            if prefix is None:
                prefix = 'Usage: '
            return super()._format_usage(usage, actions, groups, prefix)
    
    return CustomHelpFormatter


def print_help_for_command(parser: argparse.ArgumentParser, command: str) -> None:
    """
    Print help for a specific command.
    
    Args:
        parser: Main argument parser
        command: Command name to show help for
    """
    subparsers_actions = [
        action for action in parser._actions 
        if isinstance(action, argparse._SubParsersAction)
    ]
    
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == command:
                subparser.print_help()
                return
    
    print(f"Unknown command: {command}")
    parser.print_help()
