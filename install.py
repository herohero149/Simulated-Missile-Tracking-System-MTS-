#!/usr/bin/env python3
"""
Installation script for Missile Tracking System
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Installing {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {description}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"✗ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor} is compatible")
    return True

def main():
    print("Missile Tracking System - Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Upgrade pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "pip upgrade"):
        print("Warning: Could not upgrade pip, continuing...")
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "dependencies"):
        print("✗ Failed to install dependencies")
        sys.exit(1)
    
    # Test installation
    print("\nTesting installation...")
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Installation test passed")
        else:
            print("⚠ Installation test had issues:")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"⚠ Could not run test: {e}")
    
    print("\n" + "=" * 50)
    print("Installation complete!")
    print("\nQuick start:")
    print("  python test_system.py       # Test components")
    print("  python main.py              # Start with webcam")
    print("  python run.py --help        # See all options")
    print("\nFor detailed usage, see README.md")

if __name__ == "__main__":
    main()