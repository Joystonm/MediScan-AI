# Logging utility for MediScan-AI
import logging
import sys
from datetime import datetime
from typing import Optional
import os
import json

class MediScanLogger:
    """
    Custom logger for MediScan-AI application
    """
    
    def __init__(self, name: str = "mediscan", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """
        Setup logging handlers for console and file output
        """
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # File handler
        log_dir = os.getenv("LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"mediscan_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Formatters
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, extra_data: Optional[dict] = None):
        """Log info message"""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data)}"
        self.logger.info(message)
    
    def error(self, message: str, error: Optional[Exception] = None, extra_data: Optional[dict] = None):
        """Log error message"""
        if error:
            message = f"{message} | Error: {str(error)}"
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data)}"
        self.logger.error(message, exc_info=error is not None)
    
    def warning(self, message: str, extra_data: Optional[dict] = None):
        """Log warning message"""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data)}"
        self.logger.warning(message)
    
    def debug(self, message: str, extra_data: Optional[dict] = None):
        """Log debug message"""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data)}"
        self.logger.debug(message)
    
    def log_api_request(self, endpoint: str, method: str, user_id: Optional[str] = None, 
                       request_data: Optional[dict] = None):
        """Log API request"""
        log_data = {
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "request_data": request_data
        }
        self.info(f"API Request: {method} {endpoint}", log_data)
    
    def log_model_prediction(self, model_type: str, prediction: dict, confidence: float,
                           processing_time: float):
        """Log model prediction"""
        log_data = {
            "model_type": model_type,
            "prediction": prediction,
            "confidence": confidence,
            "processing_time_ms": processing_time * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.info(f"Model Prediction: {model_type}", log_data)
    
    def log_error_with_context(self, error: Exception, context: dict):
        """Log error with additional context"""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.error("Application Error", error, error_data)

# Global logger instances
api_logger = MediScanLogger("mediscan.api")
model_logger = MediScanLogger("mediscan.models")
service_logger = MediScanLogger("mediscan.services")

# Utility functions
def log_function_call(func_name: str, args: dict = None, result: dict = None):
    """Decorator-friendly function call logger"""
    log_data = {
        "function": func_name,
        "args": args,
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    }
    service_logger.debug(f"Function Call: {func_name}", log_data)

def log_performance_metric(metric_name: str, value: float, unit: str = "ms"):
    """Log performance metrics"""
    log_data = {
        "metric": metric_name,
        "value": value,
        "unit": unit,
        "timestamp": datetime.utcnow().isoformat()
    }
    service_logger.info(f"Performance Metric: {metric_name} = {value}{unit}", log_data)

# Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "detailed",
            "filename": "logs/mediscan.log"
        }
    },
    "loggers": {
        "mediscan": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        }
    }
}
