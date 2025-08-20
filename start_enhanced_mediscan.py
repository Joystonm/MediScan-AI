#!/usr/bin/env python3
"""
Enhanced MediScan-AI Startup Script
Starts the backend with enhanced API integrations
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    try:
        import uvicorn
        import fastapi
        import aiohttp
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install -r backend/requirements.txt")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    print("🔑 Checking API keys...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    keyword_key = os.getenv("KEYWORD_AI_KEY")
    
    keys_status = {
        "GROQ": bool(groq_key and groq_key != "your_groq_api_key_here"),
        "Tavily": bool(tavily_key and tavily_key != "your_tavily_api_key_here"),
        "Keyword AI": bool(keyword_key and keyword_key != "your_keyword_ai_key_here")
    }
    
    for service, configured in keys_status.items():
        status = "✅ Configured" if configured else "⚠️ Not configured"
        print(f"  {service}: {status}")
    
    configured_count = sum(keys_status.values())
    print(f"\n📊 API Status: {configured_count}/3 services configured")
    
    if configured_count == 0:
        print("⚠️ No API keys configured - will use fallback responses")
    elif configured_count < 3:
        print("⚠️ Some API keys missing - partial functionality available")
    else:
        print("🎉 All API keys configured - full functionality available")
    
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("\n🚀 Starting Enhanced MediScan-AI Backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        
        print("📡 Server starting at: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/api/docs")
        print("🧪 Test Endpoints: http://localhost:8000/api/v1/test/test-api-integrations")
        print("\n🔄 Server is starting... (Press Ctrl+C to stop)")
        
        # Start the server
        subprocess.run(cmd)
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {str(e)}")
        return False

def main():
    """Main startup function"""
    print("🏥 Enhanced MediScan-AI Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check API keys
    if not check_api_keys():
        return False
    
    # Start backend
    if not start_backend():
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
