#!/usr/bin/env python3
"""
Simple runner script for compatibility with existing workflows
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main
from main import main

if __name__ == "__main__":
    sys.exit(main())