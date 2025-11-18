#!/usr/bin/env python3
"""
Run script for DSPy Liquid Invoice Parser
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit application."""
    # Check if we're in the right directory
    if not Path("src/invoice_parser_ui/app.py").exists():
        print("Error: Please run this script from the project root directory")
        sys.exit(1)

    # Check for .env file
    if not Path(".env").exists():
        print("Warning: No .env file found. Please create one with your API keys.")
        print("See README.md for configuration instructions.")

    # Run Streamlit
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", "src/invoice_parser_ui/app.py"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
