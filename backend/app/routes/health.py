# Health check/status endpoints
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import psutil
import os

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: str

class SystemStatus(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    models_loaded: dict

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        uptime="0d 0h 0m"  # TODO: Calculate actual uptime
    )

@router.get("/health/detailed", response_model=SystemStatus)
async def detailed_health_check():
    """
    Detailed system status including resource usage
    """
    return SystemStatus(
        cpu_usage=psutil.cpu_percent(),
        memory_usage=psutil.virtual_memory().percent,
        disk_usage=psutil.disk_usage('/').percent,
        models_loaded={
            "skin_model": False,  # TODO: Check actual model status
            "radiology_model": False,
            "triage_model": False
        }
    )

@router.get("/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    """
    # TODO: Add actual readiness checks (DB connection, model loading, etc.)
    return {"ready": True}

@router.get("/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    """
    return {"alive": True}
