from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from fastapi.responses import JSONResponse
import uuid
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch
import torchvision.transforms as transforms
from typing import Optional
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from app.models.schemas import (
    SkinAnalysisResult, SkinLesionCharacteristics, VisualOverlay,
    BoundingBox, HeatmapPoint, Language, SeverityLevel
)
from app.services.skin_analysis_service import SkinAnalysisService
from app.services.translation_service import TranslationService
from app.utils.image_processing import ImageProcessor

router = APIRouter()

# Initialize services
skin_service = SkinAnalysisService()
translation_service = TranslationService()
image_processor = ImageProcessor()

# Supported file formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.get("/supported-formats")
async def get_supported_formats():
    """Get supported image formats for skin analysis."""
    return {
        "supported_formats": list(SUPPORTED_FORMATS),
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "recommended_resolution": "512x512 to 1024x1024 pixels",
        "image_requirements": [
            "Clear, well-lit image of the skin lesion",
            "Lesion should be centered in the image",
            "Avoid shadows and reflections",
            "Include a reference object (coin, ruler) if possible"
        ]
    }

@router.post("/analyze", response_model=SkinAnalysisResult)
async def analyze_skin_lesion(
    file: UploadFile = File(...),
    language: Language = Query(default=Language.EN, description="Response language")
):
    """
    Analyze a skin lesion image for potential skin cancer.
    
    Provides detailed analysis results for medical assessment.
    """
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB"
        )
    
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Save uploaded file
        upload_path = f"uploads/skin_{analysis_id}{file_ext}"
        with open(upload_path, "wb") as f:
            f.write(file_content)
        
        # Load and preprocess image
        image = Image.open(upload_path).convert('RGB')
        processed_image = image_processor.preprocess_skin_image(image)
        
        # Run AI analysis
        predictions = await skin_service.analyze_lesion(processed_image)
        
        # Generate visual overlays
        visual_overlay = await _generate_skin_visual_overlay(
            image, predictions, analysis_id
        )
        
        # Generate visual overlay (optional)
        visual_overlay = await _generate_visual_overlay(image, predictions)
        
        # Determine risk level and recommendations
        risk_level, recommendations, next_steps = await _generate_skin_recommendations(
            predictions, None, "patient", language  # No characteristics needed
        )
        
        # Generate dynamic insights based on top prediction
        from app.services.dynamic_insights_service import DynamicInsightsService
        insights_service = DynamicInsightsService()
        
        logger.info(f"Generating dynamic insights for {predictions['top_class']} ({predictions['confidence']:.1%})")
        
        # Generate prediction-based insights
        insights = await insights_service.generate_prediction_insights(
            top_prediction=predictions["top_class"],
            confidence=predictions["confidence"],
            risk_level=risk_level.value,
            recommendations=recommendations
        )
        
        logger.info("Dynamic insights generation completed")
        
        # Create analysis result without ABCDE characteristics
        result = SkinAnalysisResult(
            analysis_id=analysis_id,
            predictions=predictions["probabilities"],
            top_prediction=predictions["top_class"],
            confidence=predictions["confidence"],
            risk_level=risk_level,
            characteristics=None,  # Remove ABCDE characteristics
            visual_overlay=visual_overlay,
            recommendations=recommendations,
            next_steps=next_steps,
            # Enhanced insights based on prediction
            ai_summary=insights.get("ai_summary", {}),
            medical_resources=insights.get("medical_resources", {}),
            keywords=insights.get("keywords", {}),
            enhancement_timestamp=insights.get("generated_at", datetime.utcnow().isoformat())
        )
        
        # Store analysis result
        await _store_analysis_result(analysis_id, result, None)
        
        return result
        
    except Exception as e:
        # Clean up uploaded file on error
        if 'upload_path' in locals() and os.path.exists(upload_path):
            os.remove(upload_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/analysis/{analysis_id}", response_model=SkinAnalysisResult)
async def get_skin_analysis(
    analysis_id: str
):
    """Retrieve a previous skin analysis result."""
    
    result = await _load_analysis_result(analysis_id, None)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return result

@router.get("/analysis/{analysis_id}/overlay-image")
async def get_overlay_image(
    analysis_id: str
):
    """Get the visual overlay image for an analysis."""
    
    overlay_path = f"uploads/skin_{analysis_id}_overlay.png"
    if not os.path.exists(overlay_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Overlay image not found"
        )
    
    from fastapi.responses import FileResponse
    return FileResponse(overlay_path, media_type="image/png")

async def _generate_skin_visual_overlay(
    image: Image.Image, 
    predictions: dict, 
    analysis_id: str
) -> VisualOverlay:
    """Generate visual overlay with attention maps and annotations."""
    
    # Generate attention heatmap
    attention_map = predictions.get("attention_map", np.zeros((224, 224)))
    heatmap_points = []
    
    # Convert attention map to heatmap points
    h, w = attention_map.shape
    for y in range(0, h, 4):  # Sample every 4th pixel for performance
        for x in range(0, w, 4):
            if attention_map[y, x] > 0.1:  # Only include significant attention
                heatmap_points.append(HeatmapPoint(
                    x=int(x * image.width / w),
                    y=int(y * image.height / h),
                    intensity=float(attention_map[y, x])
                ))
    
    # Generate bounding boxes for regions of interest
    bounding_boxes = []
    if predictions.get("roi_boxes"):
        for box in predictions["roi_boxes"]:
            bounding_boxes.append(BoundingBox(
                x=box["x"],
                y=box["y"],
                width=box["width"],
                height=box["height"],
                confidence=box["confidence"],
                label=box["label"]
            ))
    
    # Create overlay image
    overlay_image = await _create_overlay_image(
        image, attention_map, bounding_boxes, analysis_id
    )
    
    return VisualOverlay(
        bounding_boxes=bounding_boxes,
        heatmap=heatmap_points,
        overlay_image_url=f"/api/v1/skin-analysis/analysis/{analysis_id}/overlay-image"
    )

async def _create_overlay_image(
    original_image: Image.Image,
    attention_map: np.ndarray,
    bounding_boxes: list,
    analysis_id: str
) -> str:
    """Create and save overlay image with heatmap and annotations."""
    
    # Resize attention map to match image size
    attention_resized = cv2.resize(attention_map, (original_image.width, original_image.height))
    
    # Convert PIL to OpenCV format
    cv_image = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)
    
    # Create heatmap overlay
    heatmap_colored = cv2.applyColorMap(
        (attention_resized * 255).astype(np.uint8), 
        cv2.COLORMAP_JET
    )
    
    # Blend original image with heatmap
    overlay = cv2.addWeighted(cv_image, 0.7, heatmap_colored, 0.3, 0)
    
    # Draw bounding boxes
    for bbox in bounding_boxes:
        x1 = int(bbox.x * original_image.width)
        y1 = int(bbox.y * original_image.height)
        x2 = int((bbox.x + bbox.width) * original_image.width)
        y2 = int((bbox.y + bbox.height) * original_image.height)
        
        # Draw rectangle
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Add label
        label_text = f"{bbox.label}: {bbox.confidence:.2f}"
        cv2.putText(overlay, label_text, (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Save overlay image
    overlay_path = f"uploads/skin_{analysis_id}_overlay.png"
    cv2.imwrite(overlay_path, overlay)
    
    return overlay_path

async def _generate_skin_recommendations(
    predictions: dict,
    characteristics: Optional[SkinLesionCharacteristics],
    user_role: str,
    language: Language
) -> tuple[SeverityLevel, list[str], list[str]]:
    """Generate risk assessment and recommendations based on user role."""
    
    confidence = predictions.get("confidence", 0.5)
    top_class = predictions.get("top_class", "unknown")
    
    # Determine risk level
    if confidence > 0.8 and "melanoma" in top_class.lower():
        risk_level = SeverityLevel.HIGH
    elif confidence > 0.6 and any(term in top_class.lower() for term in ["carcinoma", "malignant"]):
        risk_level = SeverityLevel.MEDIUM
    elif confidence > 0.4:
        risk_level = SeverityLevel.LOW
    else:
        risk_level = SeverityLevel.LOW
    
    # Generate role-appropriate recommendations
    if user_role == UserRole.DOCTOR.value:
        recommendations = await _get_doctor_recommendations(predictions, characteristics, risk_level)
        next_steps = await _get_doctor_next_steps(risk_level)
    else:
        recommendations = await _get_patient_recommendations(predictions, risk_level)
        next_steps = await _get_patient_next_steps(risk_level)
    
    # Translate if needed
    if language != Language.EN:
        recommendations = await translation_service.translate_list(recommendations, language.value)
        next_steps = await translation_service.translate_list(next_steps, language.value)
    
    return risk_level, recommendations, next_steps

async def _get_doctor_recommendations(
    predictions: dict, 
    characteristics: SkinLesionCharacteristics, 
    risk_level: SeverityLevel
) -> list[str]:
    """Generate detailed medical recommendations for doctors."""
    
    recommendations = []
    
    if risk_level == SeverityLevel.HIGH:
        recommendations.extend([
            "Immediate dermatological consultation recommended",
            "Consider urgent biopsy for histopathological examination",
            "Document lesion characteristics and monitor for changes",
            "Review patient's family history of skin cancer",
            "Perform full-body skin examination"
        ])
    elif risk_level == SeverityLevel.MEDIUM:
        recommendations.extend([
            "Dermatological evaluation within 2-4 weeks",
            "Consider dermoscopy for detailed examination",
            "Monitor lesion for ABCDE changes",
            "Patient education on skin self-examination"
        ])
    else:
        recommendations.extend([
            "Routine monitoring recommended",
            "Annual skin examination",
            "Patient education on sun protection",
            "Document baseline characteristics"
        ])
    
    # Add specific characteristic-based recommendations
    if characteristics.asymmetry_score > 0.7:
        recommendations.append("High asymmetry score warrants closer examination")
    
    if characteristics.border_irregularity > 0.7:
        recommendations.append("Irregular borders suggest need for dermoscopic evaluation")
    
    return recommendations

async def _get_patient_recommendations(
    predictions: dict, 
    risk_level: SeverityLevel
) -> list[str]:
    """Generate patient-friendly recommendations."""
    
    recommendations = []
    
    if risk_level == SeverityLevel.HIGH:
        recommendations.extend([
            "Please see a dermatologist as soon as possible",
            "This lesion shows concerning features that need professional evaluation",
            "Don't delay - early detection is important for skin health",
            "Bring this analysis report to your appointment"
        ])
    elif risk_level == SeverityLevel.MEDIUM:
        recommendations.extend([
            "Schedule an appointment with a dermatologist within the next few weeks",
            "Monitor the lesion for any changes in size, color, or shape",
            "Take photos to track changes over time",
            "Protect the area from sun exposure"
        ])
    else:
        recommendations.extend([
            "This appears to be a low-risk lesion",
            "Continue regular skin self-examinations",
            "Use sun protection to prevent skin damage",
            "See a dermatologist if you notice any changes"
        ])
    
    return recommendations

async def _get_doctor_next_steps(risk_level: SeverityLevel) -> list[str]:
    """Generate clinical next steps for doctors."""
    
    if risk_level == SeverityLevel.HIGH:
        return [
            "Urgent dermatology referral",
            "Biopsy planning",
            "Patient counseling",
            "Documentation in medical record"
        ]
    elif risk_level == SeverityLevel.MEDIUM:
        return [
            "Dermatology referral",
            "Dermoscopy evaluation",
            "Follow-up in 3-6 months",
            "Patient education"
        ]
    else:
        return [
            "Routine monitoring",
            "Annual examination",
            "Patient education",
            "Baseline documentation"
        ]

async def _get_patient_next_steps(risk_level: SeverityLevel) -> list[str]:
    """Generate patient-friendly next steps."""
    
    if risk_level == SeverityLevel.HIGH:
        return [
            "Call dermatologist today",
            "Schedule urgent appointment",
            "Prepare questions for doctor",
            "Bring this report to appointment"
        ]
    elif risk_level == SeverityLevel.MEDIUM:
        return [
            "Schedule dermatologist appointment",
            "Monitor lesion daily",
            "Take reference photos",
            "Avoid sun exposure on lesion"
        ]
    else:
        return [
            "Continue self-monitoring",
            "Schedule routine check-up",
            "Practice sun safety",
            "Learn about skin changes to watch for"
        ]

async def _store_analysis_result(analysis_id: str, result: SkinAnalysisResult, user_id: int):
    """Store analysis result for future retrieval."""
    
    # Create storage directory if it doesn't exist
    os.makedirs("analysis_results", exist_ok=True)
    
    # Store as JSON file (in production, use database)
    result_data = {
        "analysis_id": analysis_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "result": result.dict()
    }
    
    with open(f"analysis_results/skin_{analysis_id}.json", "w") as f:
        json.dump(result_data, f, indent=2)

async def _load_analysis_result(analysis_id: str, user_id: int) -> Optional[SkinAnalysisResult]:
    """Load stored analysis result."""
    
    try:
        with open(f"analysis_results/skin_{analysis_id}.json", "r") as f:
            data = json.load(f)
        
        # Verify user access
        if data["user_id"] != user_id:
            return None
        
        return SkinAnalysisResult(**data["result"])
    
    except FileNotFoundError:
        return None
