#!/usr/bin/env python3
"""
Startup script for LM Studio Repository Interface
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['flask', 'requests', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--upgrade'
            ] + missing_packages)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def check_port_available(port: int) -> bool:
    """Check if port is available"""
    try:
        response = requests.get(f"http://localhost:{port}/api/health", timeout=2)
        return False  # Port is in use
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return True  # Port is available

def start_repository_interface():
    """Start the repository interface server"""
    load_dotenv()
    
    port = int(os.getenv('REPO_INTERFACE_PORT', 8080))
    
    print("🚀 Starting LM Studio Repository Interface")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check port availability
    if not check_port_available(port):
        print(f"⚠️  Port {port} is already in use")
        print(f"🔄 Checking if Repository Interface is already running...")
        try:
            response = requests.get(f"http://localhost:{port}/api/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('service') == 'LM Studio Repository Interface':
                    print(f"✅ Repository Interface is already running on port {port}")
                    return True
        except:
            pass
        
        print(f"❌ Port {port} is occupied by another service")
        print("Please change REPO_INTERFACE_PORT in your .env file or stop the other service")
        return False
    
    # Start the server
    try:
        print(f"🌐 Starting server on http://localhost:{port}")
        print("📁 Repository interface will be available for LM Studio")
        print("\nAvailable endpoints:")
        print(f"  - Health Check: http://localhost:{port}/api/health")
        print(f"  - Repository Structure: http://localhost:{port}/api/repository/structure")
        print(f"  - File Operations: http://localhost:{port}/api/repository/file")
        print(f"  - Search: http://localhost:{port}/api/repository/search")
        print(f"  - Tests: http://localhost:{port}/api/repository/tests")
        print(f"  - Git Status: http://localhost:{port}/api/repository/git/status")
        print("\n📋 To use with LM Studio:")
        print("  1. Import the tool configuration: lm_studio_tools.json")
        print("  2. Use the system prompt: system_prompt.md")
        print("  3. Start chatting with repository access!")
        print("\n⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Import and run the repository interface
        from repository_interface import main as run_interface
        run_interface()
        
    except KeyboardInterrupt:
        print("\n👋 Repository Interface stopped")
        return True
    except Exception as e:
        print(f"❌ Failed to start Repository Interface: {e}")
        return False

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("LM Studio Repository Interface Launcher")
            print("Usage: python start_repo_interface.py [options]")
            print("\nOptions:")
            print("  --help    Show this help message")
            print("  --test    Test connection to running interface")
            print("\nEnvironment Variables:")
            print("  REPO_INTERFACE_PORT   Port for the interface (default: 8080)")
            print("  DEBUG                 Enable debug mode (default: false)")
            return
        
        elif sys.argv[1] == '--test':
            load_dotenv()
            port = int(os.getenv('REPO_INTERFACE_PORT', 8080))
            
            print(f"🧪 Testing connection to Repository Interface on port {port}")
            try:
                response = requests.get(f"http://localhost:{port}/api/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Repository Interface is running")
                    print(f"Status: {data.get('status')}")
                    print(f"Service: {data.get('service')}")
                else:
                    print(f"❌ Unexpected response: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"❌ Cannot connect to Repository Interface on port {port}")
                print("Make sure the interface is running with: python start_repo_interface.py")
            except Exception as e:
                print(f"❌ Test failed: {e}")
            return
    
    # Start the interface
    success = start_repository_interface()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()