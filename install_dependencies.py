#!/usr/bin/env python3
"""
Install Missing Dependencies for MediScan-AI
Installs aiohttp and other required packages for API integrations
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🔧 Installing Missing Dependencies for MediScan-AI")
    print("=" * 60)
    
    # Required packages for API integrations
    required_packages = [
        "aiohttp==3.9.1",
        "asyncio-timeout==4.0.3",
        "python-dotenv==1.0.0"
    ]
    
    # Optional packages for full functionality
    optional_packages = [
        "groq",
        "tavily-python", 
        "torch",
        "torchvision"
    ]
    
    print("Installing required packages...")
    success_count = 0
    
    for package in required_packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installed {success_count}/{len(required_packages)} required packages")
    
    if success_count == len(required_packages):
        print("✅ All required dependencies installed successfully!")
        print("\n🚀 You can now restart the backend server:")
        print("   cd backend")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        
        print("\n💡 For full AI functionality, also install:")
        for package in optional_packages:
            print(f"   pip install {package}")
    else:
        print("⚠️ Some packages failed to install. Please install manually:")
        print("   cd backend")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
