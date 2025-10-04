#!/usr/bin/env python3
# Wrapper to provide main() entry point for test_validation.py

import subprocess
import sys
import os

def main():
    """Run validation tests."""
    test_file = os.path.join(os.path.dirname(__file__), "test_validation.py")
    result = subprocess.run([sys.executable, test_file], capture_output=False)
    return result.returncode == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
