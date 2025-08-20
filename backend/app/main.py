# FastAPI entry point for MedAI Copilot
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
# Try .env.local first (for development), then fall back to .env
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
    print("Loaded environment from .env.local")
else:
    load_dotenv('.env')
    print("Loaded environment from .env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize model manager
    logger.info("Starting MedAI Copilot API...")
    try:
        # Try to import model manager, but don't fail if PyTorch is missing
        try:
            from app.services.model_manager import model_manager
            logger.info("Model manager initialized successfully")
            
            # Log model information
            model_info = model_manager.get_model_info()
            logger.info(f"Models loaded: {model_info.get('models_loaded', [])}")
            logger.info(f"Device: {model_info.get('device', 'unknown')}")
            if model_info.get('gpu_available'):
                logger.info(f"GPU: {model_info.get('gpu_name', 'unknown')}")
        except ImportError as e:
            logger.warning(f"Model manager not available (missing dependencies): {e}")
            logger.info("Running in mock mode - install PyTorch for full functionality")
        
    except Exception as e:
        logger.error(f"Failed to initialize model manager: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MedAI Copilot API...")

# Create FastAPI app with lifespan events
app = FastAPI(
    title="MedAI Copilot API",
    description="AI-powered healthcare assistant with skin cancer detection, radiology analysis, and virtual triage",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for file storage
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="uploads"), name="static")
    app.mount("/reports", StaticFiles(directory="reports"), name="reports")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Import routes - only import existing ones
try:
    from app.routes import health
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    logger.info("Health routes loaded")
except ImportError as e:
    logger.warning(f"Could not import health routes: {e}")

try:
    from app.routes import triage
    app.include_router(triage.router, prefix="/api/v1/triage", tags=["triage"])
    logger.info("Triage routes loaded")
except ImportError as e:
    logger.warning(f"Could not import triage routes: {e}")

try:
    from app.routes import skin_cancer
    app.include_router(skin_cancer.router, prefix="/api/v1/skin-analysis", tags=["skin-analysis"])
    logger.info("Skin analysis routes loaded")
except ImportError as e:
    logger.warning(f"Could not import skin_cancer routes: {e}")

try:
    # Try optimized radiology route first
    try:
        from app.routes import radiology_optimized
        app.include_router(radiology_optimized.router, prefix="/api/v1/radiology", tags=["radiology"])
        logger.info("Optimized radiology routes loaded")
    except ImportError:
        # Fallback to basic radiology route
        from app.routes import radiology
        app.include_router(radiology.router, prefix="/api/v1/radiology", tags=["radiology"])
        logger.info("Basic radiology routes loaded")
except ImportError as e:
    logger.warning(f"Could not import radiology routes: {e}")

try:
    from app.routes import reports
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
    logger.info("Reports routes loaded")
except ImportError as e:
    logger.warning(f"Could not import reports routes: {e}")

@app.get("/")
async def root():
    return {
        "message": "MedAI Copilot API is running",
        "version": "2.0.0",
        "status": "optimized",
        "features": [
            "Skin Cancer Detection (Optimized)",
            "Radiology Analysis (Optimized)", 
            "Virtual Triage Assistant",
            "Multi-language Support",
            "PDF Report Generation",
            "GPU Acceleration",
            "Model Caching",
            "Async Processing"
        ],
        "performance": {
            "model_caching": "enabled",
            "gpu_acceleration": "auto-detected",
            "async_processing": "enabled",
            "typical_analysis_time": "1-3 seconds"
        },
        "authentication": "disabled"
    }

@app.get("/api/v1/system/status")
async def get_system_status():
    """Get comprehensive system status including model information"""
    try:
        try:
            from app.services.model_manager import model_manager
            model_info = model_manager.get_model_info()
            
            return {
                "status": "healthy",
                "version": "2.0.0",
                "models": model_info,
                "optimizations": {
                    "model_caching": True,
                    "gpu_acceleration": model_info.get("gpu_available", False),
                    "async_processing": True,
                    "image_preprocessing": True
                },
                "endpoints": {
                    "skin_analysis": "/api/v1/skin-analysis/analyze",
                    "radiology_analysis": "/api/v1/radiology/analyze",
                    "triage_assessment": "/api/v1/triage/assess",
                    "health_check": "/api/v1/health"
                }
            }
        except ImportError:
            return {
                "status": "healthy",
                "version": "2.0.0",
                "mode": "mock",
                "message": "Running in mock mode - install PyTorch for full AI functionality",
                "endpoints": {
                    "skin_analysis": "/api/v1/skin-analysis/analyze",
                    "radiology_analysis": "/api/v1/radiology/analyze", 
                    "triage_assessment": "/api/v1/triage/assess",
                    "health_check": "/api/v1/health"
                }
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
