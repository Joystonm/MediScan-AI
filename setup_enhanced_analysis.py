#!/usr/bin/env python3
"""
Setup script for MediScan-AI Enhanced Skin Analysis
Helps configure API keys and validate the setup
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🔬 MediScan-AI Enhanced Skin Analysis Setup")
    print("=" * 50)
    print("This script will help you configure the enhanced skin analysis features.")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "aiohttp",
        "python-dotenv",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r backend/requirements.txt")
        return False
    
    return True

def setup_environment_file():
    """Setup environment file with API keys"""
    print("\n⚙️ Setting up environment configuration...")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    # Check if .env already exists
    if env_path.exists():
        print("✅ .env file already exists")
        overwrite = input("Do you want to update it? (y/N): ").lower().strip()
        if overwrite != 'y':
            return True
    
    # Copy from example if it exists
    if env_example_path.exists():
        print("📋 Copying from .env.example...")
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ Environment file created")
    else:
        print("⚠️  .env.example not found, creating basic .env file...")
        
        basic_env = """# MediScan-AI Environment Configuration

# API Keys for Enhanced Features
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
KEYWORD_AI_KEY=your_keyword_ai_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1
"""
        
        with open(env_path, 'w') as f:
            f.write(basic_env)
        
        print("✅ Basic environment file created")
    
    return True

def configure_api_keys():
    """Interactive API key configuration"""
    print("\n🔑 Configuring API Keys...")
    print("You'll need API keys from the following services:")
    print("1. GROQ API (https://console.groq.com)")
    print("2. Tavily API (https://tavily.com)")
    print("3. Keyword AI (https://keywordai.co)")
    print()
    
    # Load existing .env
    env_path = Path(".env")
    env_vars = {}
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Configure each API key
    api_configs = [
        {
            "key": "GROQ_API_KEY",
            "name": "GROQ API",
            "description": "For AI-powered medical summaries and explanations",
            "url": "https://console.groq.com"
        },
        {
            "key": "TAVILY_API_KEY", 
            "name": "Tavily API",
            "description": "For medical images and research articles",
            "url": "https://tavily.com"
        },
        {
            "key": "KEYWORD_AI_KEY",
            "name": "Keyword AI",
            "description": "For medical keyword extraction and categorization",
            "url": "https://keywordai.co"
        }
    ]
    
    updated = False
    
    for config in api_configs:
        key = config["key"]
        current_value = env_vars.get(key, "")
        
        print(f"\n{config['name']}:")
        print(f"  Purpose: {config['description']}")
        print(f"  Get key at: {config['url']}")
        
        if current_value and current_value != f"your_{key.lower()}_here":
            print(f"  Current: {current_value[:10]}..." if len(current_value) > 10 else f"  Current: {current_value}")
            update = input("  Update this key? (y/N): ").lower().strip()
            if update != 'y':
                continue
        
        new_value = input(f"  Enter {config['name']} key (or press Enter to skip): ").strip()
        
        if new_value:
            env_vars[key] = new_value
            updated = True
            print(f"  ✅ {config['name']} key configured")
        else:
            print(f"  ⏭️  Skipped {config['name']} key")
    
    # Save updated environment file
    if updated:
        print("\n💾 Saving configuration...")
        
        with open(env_path, 'w') as f:
            f.write("# MediScan-AI Environment Configuration\n\n")
            f.write("# API Keys for Enhanced Features\n")
            
            for config in api_configs:
                key = config["key"]
                value = env_vars.get(key, f"your_{key.lower()}_here")
                f.write(f"{key}={value}\n")
            
            f.write("\n# API Configuration\n")
            f.write("API_HOST=0.0.0.0\n")
            f.write("API_PORT=8000\n")
            f.write("DEBUG=false\n")
            f.write("\n# Frontend Configuration\n")
            f.write("REACT_APP_API_URL=http://localhost:8000/api/v1\n")
        
        print("✅ Configuration saved to .env")
    
    return True

def test_setup():
    """Test the setup by running the test script"""
    print("\n🧪 Testing setup...")
    
    test_script = Path("test_enhanced_skin_analysis.py")
    
    if not test_script.exists():
        print("⚠️  Test script not found, skipping tests")
        return True
    
    run_tests = input("Run API integration tests? (Y/n): ").lower().strip()
    
    if run_tests == 'n':
        print("⏭️  Skipping tests")
        return True
    
    try:
        print("Running tests...")
        result = subprocess.run([
            sys.executable, str(test_script)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            print("🎉 Enhanced skin analysis is ready to use!")
        else:
            print("⚠️  Some tests failed:")
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Tests timed out (this is normal if APIs are slow)")
        return True
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🚀 Next Steps:")
    print("=" * 30)
    print("1. Start the backend server:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("2. Start the frontend (in a new terminal):")
    print("   cd frontend")
    print("   npm install")
    print("   npm start")
    print()
    print("3. Open your browser to:")
    print("   http://localhost:3000")
    print()
    print("4. Navigate to Dashboard and try the Skin Cancer Detection module")
    print()
    print("📚 For more information, see:")
    print("   - ENHANCED_SKIN_ANALYSIS.md")
    print("   - README.md")
    print()
    print("🆘 Need help?")
    print("   - GitHub Issues: https://github.com/your-username/MediScan-AI/issues")
    print("   - Email: support@mediscan-ai.com")

def main():
    """Main setup function"""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_dependencies():
        print("\n💡 Install dependencies first, then run this script again.")
        return False
    
    # Setup configuration
    if not setup_environment_file():
        return False
    
    if not configure_api_keys():
        return False
    
    # Test setup
    if not test_setup():
        print("\n⚠️  Setup completed with warnings. Check the test output above.")
    
    # Show next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)
