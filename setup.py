#!/usr/bin/env python3
"""
Setup script for LM Studio Local Chatbot
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command: str, description: str):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def setup_environment():
    """Set up the Python environment and install dependencies"""
    print("🚀 Setting up LM Studio Local Chatbot")
    print("=" * 50)
    
    # Check if Python is available
    try:
        python_version = subprocess.check_output([sys.executable, "--version"], text=True).strip()
        print(f"✅ Found Python: {python_version}")
    except Exception as e:
        print(f"❌ Python not found: {e}")
        return False
    
    # Install dependencies
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        try:
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file from .env.example")
        except Exception as e:
            print(f"⚠️  Could not create .env file: {e}")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start LM Studio and load a model")
    print("2. Start the local server in LM Studio")
    print("3. Run one of the interfaces:")
    print("   - CLI: python chatbot_cli.py")
    print("   - Web UI: streamlit run streamlit_app.py")
    
    return True

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("LM Studio Local Chatbot Setup")
        print("Usage: python setup.py")
        print("\nThis script will:")
        print("- Install required Python packages")
        print("- Create configuration files")
        print("- Prepare the environment for running the chatbot")
        return
    
    setup_environment()

if __name__ == "__main__":
    main()