#!/usr/bin/env python3
"""
FedRAMP Continuous Validation Tool - Encryption Check Script

This script is a simple wrapper around the main validation functionality
to make it easier to run from the command line.
"""

import sys
from src.main import cli

if __name__ == "__main__":
    sys.exit(cli())