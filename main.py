#!/usr/bin/env python3
"""
Main entry point for the Python project demonstrating best practices.
This file serves as the application launcher and coordinates all modules.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.logging_config import setup_logging
from config.settings import Settings
from core.application import Application
from cli.parser import create_argument_parser
# from core.exceptions import ApplicationError


def main():
    """Main application entry point."""
    try:
        # Setup logging first
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Python Best Practices Demo Application")
        
        # Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Load configuration
        settings = Settings()
        
        # Create and run application
        app = Application(settings)
        result = app.run(args)
        
        logger.info("Application completed successfully")
        return result
        
    except (RuntimeError, FileNotFoundError, ValueError) as e:
        logging.error(f"Application error: {e}")
        return 1
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
        return 130
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
