from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from fastapi.responses import JSONResponse
import uuid
import os
from PIL import Image
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import numpy as np

from app.models.schemas import (
    RadiologyAnalysisResult, RadiologyFinding, VisualOverlay,
    BoundingBox, HeatmapPoint, Language, SeverityLevel, UrgencyLevel
)
from app.services.radiology_service import RadiologyService
from app.services.translation_service import TranslationService
from app.utils.image_processing import ImageProcessor

router = APIRouter()

@router.post("/analyze")
async def analyze_radiology_scan(
    file: UploadFile = File(...),
    scan_type: str = Query(..., description="Type of scan (chest_xray, ct_scan, mri)"),
    clinical_history: Optional[str] = Query(None, description="Relevant clinical history")
):
    """
    Analyze a radiology scan for pathological findings.
    Simplified version for development.
    """
    
    # Validate scan type
    supported_scan_types = ["chest_xray", "ct_scan", "mri"]
    if scan_type not in supported_scan_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported scan type. Supported types: {', '.join(supported_scan_types)}"
        )
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.dicom', '.dcm'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Read file content
        file_content = await file.read()
        
        # Save uploaded file
        upload_path = f"uploads/radiology_{analysis_id}{file_ext}"
        with open(upload_path, "wb") as f:
            f.write(file_content)
        
        # Mock analysis results based on scan type
        if scan_type == "chest_xray":
            findings = [
                {
                    "condition": "No acute findings",
                    "probability": 0.75,
                    "severity": "low",
                    "description": "No acute cardiopulmonary abnormalities detected"
                },
                {
                    "condition": "Mild cardiomegaly",
                    "probability": 0.20,
                    "severity": "medium",
                    "description": "Borderline cardiac enlargement"
                }
            ]
            urgency_level = "routine"
        else:
            findings = [
                {
                    "condition": "Normal study",
                    "probability": 0.80,
                    "severity": "low",
                    "description": "No significant abnormalities detected"
                }
            ]
            urgency_level = "routine"
        
        result = {
            "analysis_id": analysis_id,
            "scan_type": scan_type,
            "findings": findings,
            "overall_assessment": "No acute abnormalities detected",
            "urgency_level": urgency_level,
            "clinical_summary": f"Analysis of {scan_type.replace('_', ' ')} shows no acute findings.",
            "recommendations": [
                "Clinical correlation recommended",
                "Follow-up as clinically indicated"
            ],
            "differential_diagnosis": []
        }
        
        return result
        
    except Exception as e:
        # Clean up uploaded file on error
        if 'upload_path' in locals() and os.path.exists(upload_path):
            os.remove(upload_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/supported-types")
async def get_supported_types():
    """Get supported radiology scan types and formats."""
    return {
        "supported_scan_types": ["chest_xray", "ct_scan", "mri"],
        "supported_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".dicom", ".dcm"],
        "max_file_size_mb": 50,
        "pathologies_detected": {
            "chest_xray": [
                "Pneumonia", "Pneumothorax", "Cardiomegaly", "Pleural Effusion",
                "Atelectasis", "Consolidation", "Mass", "Nodule"
            ],
            "ct_scan": [
                "Pulmonary Embolism", "Lung Cancer", "Pneumonia", "COPD"
            ]
        }
    }

@router.post("/analyze", response_model=RadiologyAnalysisResult)
async def analyze_radiology_scan(
    file: UploadFile = File(...),
    scan_type: str = Query(..., description="Type of scan (chest_xray, ct_scan, mri)"),
    clinical_history: Optional[str] = Query(None, description="Relevant clinical history"),
    language: Language = Query(default=Language.EN, description="Response language")
):
    """
    Analyze a radiology scan for pathological findings.
    
    Supports multiple scan types with comprehensive pathology detection.
    """
    
    # Validate scan type
    if scan_type not in SUPPORTED_SCAN_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported scan type. Supported types: {', '.join(SUPPORTED_SCAN_TYPES)}"
        )
    
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
        upload_path = f"uploads/radiology_{analysis_id}{file_ext}"
        with open(upload_path, "wb") as f:
            f.write(file_content)
        
        # Load and preprocess image
        if file_ext in ['.dicom', '.dcm']:
            image = image_processor.load_dicom(upload_path)
        else:
            image = Image.open(upload_path).convert('RGB')
        
        processed_image = image_processor.preprocess_radiology_image(image, scan_type)
        
        # Run AI analysis
        analysis_results = await radiology_service.analyze_scan(
            processed_image, scan_type, clinical_history
        )
        
        # Generate findings with locations
        findings = await _generate_radiology_findings(
            analysis_results, "patient", language
        )
        
        # Generate visual overlays
        visual_overlay = await _generate_radiology_visual_overlay(
            image, analysis_results, findings, analysis_id
        )
        
        # Generate clinical assessment
        overall_assessment, urgency_level = await _generate_clinical_assessment(
            findings, scan_type, "patient"
        )
        
        # Generate clinical summary and recommendations
        clinical_summary, recommendations, differential_diagnosis = await _generate_clinical_content(
            findings, scan_type, clinical_history, "patient", language
        )
        
        # Create analysis result
        result = RadiologyAnalysisResult(
            analysis_id=analysis_id,
            scan_type=scan_type,
            findings=findings,
            overall_assessment=overall_assessment,
            urgency_level=urgency_level,
            visual_overlay=visual_overlay,
            clinical_summary=clinical_summary,
            recommendations=recommendations,
            differential_diagnosis=differential_diagnosis
        )
        
        # Store analysis result
        await _store_radiology_result(analysis_id, result, None, clinical_history)
        
        return result
        
    except Exception as e:
        # Clean up uploaded file on error
        if 'upload_path' in locals() and os.path.exists(upload_path):
            os.remove(upload_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/analysis/{analysis_id}", response_model=RadiologyAnalysisResult)
async def get_radiology_analysis(
    analysis_id: str
):
    """Retrieve a previous radiology analysis result."""
    
    result = await _load_radiology_result(analysis_id, None)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return result

@router.get("/analysis/{analysis_id}/overlay-image")
async def get_radiology_overlay_image(
    analysis_id: str
):
    """Get the visual overlay image for a radiology analysis."""
    
    overlay_path = f"uploads/radiology_{analysis_id}_overlay.png"
    if not os.path.exists(overlay_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Overlay image not found"
        )
    
    return FileResponse(overlay_path, media_type="image/png")

@router.get("/analysis/{analysis_id}/original-image")
async def get_original_radiology_image(
    analysis_id: str
):
    """Get the original radiology image."""
    
    # Find the original file
    for ext in SUPPORTED_FORMATS:
        original_path = f"uploads/radiology_{analysis_id}{ext}"
        if os.path.exists(original_path):
            media_type = "image/png" if ext in ['.png'] else "image/jpeg"
            return FileResponse(original_path, media_type=media_type)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Original image not found"
    )

async def _generate_radiology_findings(
    analysis_results: dict,
    user_role: str,
    language: Language
) -> List[RadiologyFinding]:
    """Generate structured findings from AI analysis results."""
    
    findings = []
    predictions = analysis_results.get("predictions", {})
    
    for condition, probability in predictions.items():
        if probability > 0.1:  # Only include significant findings
            
            # Determine severity based on condition and probability
            severity = _determine_finding_severity(condition, probability)
            
            # Get location if available
            location = None
            if condition in analysis_results.get("localizations", {}):
                loc_data = analysis_results["localizations"][condition]
                location = BoundingBox(
                    x=loc_data["x"],
                    y=loc_data["y"],
                    width=loc_data["width"],
                    height=loc_data["height"],
                    confidence=loc_data["confidence"],
                    label=condition
                )
            
            # Generate description based on user role
            if user_role == UserRole.DOCTOR.value:
                description = await _get_clinical_description(condition, probability)
            else:
                description = await _get_patient_description(condition, probability)
            
            # Translate if needed
            if language != Language.EN:
                description = await translation_service.translate_text(description, language.value)
            
            finding = RadiologyFinding(
                condition=condition,
                probability=probability,
                location=location,
                severity=severity,
                description=description
            )
            
            findings.append(finding)
    
    # Sort findings by probability (highest first)
    findings.sort(key=lambda x: x.probability, reverse=True)
    
    return findings

def _determine_finding_severity(condition: str, probability: float) -> SeverityLevel:
    """Determine severity level based on condition type and probability."""
    
    # Critical conditions
    critical_conditions = [
        "pneumothorax", "massive_pleural_effusion", "tension_pneumothorax",
        "acute_pulmonary_edema", "large_mass"
    ]
    
    # High severity conditions
    high_severity_conditions = [
        "pneumonia", "pulmonary_embolism", "lung_cancer", "cardiomegaly",
        "pleural_effusion", "consolidation"
    ]
    
    condition_lower = condition.lower()
    
    if any(crit in condition_lower for crit in critical_conditions):
        return SeverityLevel.CRITICAL if probability > 0.7 else SeverityLevel.HIGH
    elif any(high in condition_lower for high in high_severity_conditions):
        return SeverityLevel.HIGH if probability > 0.6 else SeverityLevel.MEDIUM
    else:
        return SeverityLevel.MEDIUM if probability > 0.5 else SeverityLevel.LOW

async def _get_clinical_description(condition: str, probability: float) -> str:
    """Generate clinical description for healthcare professionals."""
    
    descriptions = {
        "pneumonia": f"Radiographic findings consistent with pneumonia (confidence: {probability:.1%}). "
                    "Consolidation pattern suggests infectious process requiring clinical correlation.",
        
        "pneumothorax": f"Pneumothorax identified with {probability:.1%} confidence. "
                       "Immediate clinical assessment recommended to determine extent and need for intervention.",
        
        "cardiomegaly": f"Cardiac silhouette enlargement detected (confidence: {probability:.1%}). "
                       "Cardiothoracic ratio assessment and echocardiography may be indicated.",
        
        "pleural_effusion": f"Pleural fluid collection identified with {probability:.1%} confidence. "
                           "Consider thoracentesis if clinically indicated.",
        
        "mass": f"Mass lesion detected (confidence: {probability:.1%}). "
               "Further imaging with CT and possible tissue sampling recommended.",
        
        "nodule": f"Pulmonary nodule identified with {probability:.1%} confidence. "
                 "Follow-up imaging per Fleischner Society guidelines recommended."
    }
    
    return descriptions.get(condition.lower(), 
                          f"{condition} detected with {probability:.1%} confidence. "
                          "Clinical correlation recommended.")

async def _get_patient_description(condition: str, probability: float) -> str:
    """Generate patient-friendly description."""
    
    descriptions = {
        "pneumonia": "Signs of lung infection detected. This may require antibiotic treatment.",
        
        "pneumothorax": "Air around the lung detected. This condition may need immediate medical attention.",
        
        "cardiomegaly": "The heart appears enlarged. This may indicate a heart condition that needs evaluation.",
        
        "pleural_effusion": "Fluid around the lungs detected. This may cause breathing difficulties.",
        
        "mass": "An abnormal growth has been detected. Further testing will be needed to determine what this is.",
        
        "nodule": "A small spot on the lung has been detected. Most lung spots are benign, but follow-up is important."
    }
    
    return descriptions.get(condition.lower(), 
                          f"An abnormality ({condition}) has been detected that requires medical evaluation.")

async def _generate_radiology_visual_overlay(
    image: Image.Image,
    analysis_results: dict,
    findings: List[RadiologyFinding],
    analysis_id: str
) -> VisualOverlay:
    """Generate visual overlay with pathology highlighting."""
    
    # Generate attention heatmap
    attention_map = analysis_results.get("attention_map", np.zeros((224, 224)))
    heatmap_points = []
    
    # Convert attention map to heatmap points
    h, w = attention_map.shape
    for y in range(0, h, 8):  # Sample for performance
        for x in range(0, w, 8):
            if attention_map[y, x] > 0.2:
                heatmap_points.append(HeatmapPoint(
                    x=int(x * image.width / w),
                    y=int(y * image.height / h),
                    intensity=float(attention_map[y, x])
                ))
    
    # Extract bounding boxes from findings
    bounding_boxes = [f.location for f in findings if f.location is not None]
    
    # Create overlay image
    overlay_image = await _create_radiology_overlay_image(
        image, attention_map, findings, analysis_id
    )
    
    return VisualOverlay(
        bounding_boxes=bounding_boxes,
        heatmap=heatmap_points,
        overlay_image_url=f"/api/v1/radiology/analysis/{analysis_id}/overlay-image"
    )

async def _create_radiology_overlay_image(
    original_image: Image.Image,
    attention_map: np.ndarray,
    findings: List[RadiologyFinding],
    analysis_id: str
) -> str:
    """Create and save radiology overlay image with pathology highlighting."""
    
    # Convert PIL to OpenCV format
    cv_image = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)
    
    # Resize attention map to match image size
    attention_resized = cv2.resize(attention_map, (original_image.width, original_image.height))
    
    # Create heatmap overlay
    heatmap_colored = cv2.applyColorMap(
        (attention_resized * 255).astype(np.uint8), 
        cv2.COLORMAP_HOT
    )
    
    # Blend original image with heatmap
    overlay = cv2.addWeighted(cv_image, 0.8, heatmap_colored, 0.2, 0)
    
    # Define colors for different severity levels
    severity_colors = {
        SeverityLevel.CRITICAL: (0, 0, 255),    # Red
        SeverityLevel.HIGH: (0, 165, 255),      # Orange
        SeverityLevel.MEDIUM: (0, 255, 255),    # Yellow
        SeverityLevel.LOW: (0, 255, 0)          # Green
    }
    
    # Draw bounding boxes for findings
    for finding in findings:
        if finding.location:
            bbox = finding.location
            color = severity_colors.get(finding.severity, (255, 255, 255))
            
            x1 = int(bbox.x * original_image.width)
            y1 = int(bbox.y * original_image.height)
            x2 = int((bbox.x + bbox.width) * original_image.width)
            y2 = int((bbox.y + bbox.height) * original_image.height)
            
            # Draw rectangle with thickness based on severity
            thickness = 3 if finding.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH] else 2
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, thickness)
            
            # Add label with background
            label_text = f"{finding.condition}: {finding.probability:.2f}"
            label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            
            # Draw label background
            cv2.rectangle(overlay, (x1, y1-25), (x1+label_size[0]+10, y1), color, -1)
            
            # Draw label text
            cv2.putText(overlay, label_text, (x1+5, y1-8), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Add legend
    legend_y = 30
    for severity, color in severity_colors.items():
        cv2.rectangle(overlay, (10, legend_y), (30, legend_y+15), color, -1)
        cv2.putText(overlay, severity.value.title(), (35, legend_y+12), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        legend_y += 25
    
    # Save overlay image
    overlay_path = f"uploads/radiology_{analysis_id}_overlay.png"
    cv2.imwrite(overlay_path, overlay)
    
    return overlay_path

async def _generate_clinical_assessment(
    findings: List[RadiologyFinding],
    scan_type: str,
    user_role: str
) -> tuple[str, UrgencyLevel]:
    """Generate overall clinical assessment and urgency level."""
    
    # Determine urgency based on findings
    max_severity = SeverityLevel.LOW
    critical_findings = []
    
    for finding in findings:
        if finding.severity.value > max_severity.value:
            max_severity = finding.severity
        
        if finding.severity == SeverityLevel.CRITICAL:
            critical_findings.append(finding.condition)
    
    # Determine urgency level
    if max_severity == SeverityLevel.CRITICAL:
        urgency = UrgencyLevel.EMERGENCY
    elif max_severity == SeverityLevel.HIGH:
        urgency = UrgencyLevel.URGENT
    else:
        urgency = UrgencyLevel.ROUTINE
    
    # Generate assessment text
    if user_role == UserRole.DOCTOR.value:
        if critical_findings:
            assessment = f"Critical findings identified: {', '.join(critical_findings)}. Immediate intervention may be required."
        elif max_severity == SeverityLevel.HIGH:
            assessment = "Significant pathological findings requiring prompt clinical attention."
        elif findings:
            assessment = "Abnormal findings detected requiring clinical correlation and follow-up."
        else:
            assessment = "No significant acute pathological findings identified on this study."
    else:
        if critical_findings:
            assessment = "Urgent medical findings detected that require immediate attention."
        elif max_severity == SeverityLevel.HIGH:
            assessment = "Important findings detected that need medical evaluation soon."
        elif findings:
            assessment = "Some abnormalities detected that should be discussed with your doctor."
        else:
            assessment = "No major abnormalities detected in this scan."
    
    return assessment, urgency

async def _generate_clinical_content(
    findings: List[RadiologyFinding],
    scan_type: str,
    clinical_history: Optional[str],
    user_role: str,
    language: Language
) -> tuple[str, List[str], List[str]]:
    """Generate clinical summary, recommendations, and differential diagnosis."""
    
    # Generate clinical summary
    if user_role == UserRole.DOCTOR.value:
        summary = await _generate_doctor_summary(findings, scan_type, clinical_history)
        recommendations = await _generate_doctor_recommendations(findings, scan_type)
        differential = await _generate_differential_diagnosis(findings, clinical_history)
    else:
        summary = await _generate_patient_summary(findings, scan_type)
        recommendations = await _generate_patient_recommendations(findings)
        differential = []  # Patients don't need differential diagnosis
    
    # Translate if needed
    if language != Language.EN:
        summary = await translation_service.translate_text(summary, language.value)
        recommendations = await translation_service.translate_list(recommendations, language.value)
        if differential:
            differential = await translation_service.translate_list(differential, language.value)
    
    return summary, recommendations, differential

async def _generate_doctor_summary(
    findings: List[RadiologyFinding],
    scan_type: str,
    clinical_history: Optional[str]
) -> str:
    """Generate detailed clinical summary for doctors."""
    
    summary_parts = []
    
    # Add clinical history if provided
    if clinical_history:
        summary_parts.append(f"Clinical History: {clinical_history}")
    
    # Add scan type and technique
    summary_parts.append(f"Study: {scan_type.replace('_', ' ').title()}")
    
    # Add findings
    if findings:
        summary_parts.append("Findings:")
        for finding in findings[:5]:  # Top 5 findings
            summary_parts.append(f"- {finding.description}")
    else:
        summary_parts.append("No significant pathological findings identified.")
    
    # Add impression
    if findings:
        high_prob_findings = [f for f in findings if f.probability > 0.6]
        if high_prob_findings:
            conditions = [f.condition for f in high_prob_findings]
            summary_parts.append(f"Impression: Findings consistent with {', '.join(conditions)}.")
    
    return "\n\n".join(summary_parts)

async def _generate_patient_summary(
    findings: List[RadiologyFinding],
    scan_type: str
) -> str:
    """Generate patient-friendly summary."""
    
    scan_name = scan_type.replace('_', ' ').title()
    
    if not findings:
        return f"Your {scan_name} shows no major abnormalities. This is good news!"
    
    summary_parts = [f"Results from your {scan_name}:"]
    
    # Group findings by severity
    critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL]
    high_findings = [f for f in findings if f.severity == SeverityLevel.HIGH]
    other_findings = [f for f in findings if f.severity in [SeverityLevel.MEDIUM, SeverityLevel.LOW]]
    
    if critical_findings:
        summary_parts.append("Important findings that need immediate attention:")
        for finding in critical_findings:
            summary_parts.append(f"- {finding.description}")
    
    if high_findings:
        summary_parts.append("Findings that need medical evaluation:")
        for finding in high_findings:
            summary_parts.append(f"- {finding.description}")
    
    if other_findings:
        summary_parts.append("Other findings noted:")
        for finding in other_findings[:3]:  # Limit to avoid overwhelming
            summary_parts.append(f"- {finding.description}")
    
    return "\n\n".join(summary_parts)

async def _generate_doctor_recommendations(
    findings: List[RadiologyFinding],
    scan_type: str
) -> List[str]:
    """Generate clinical recommendations for doctors."""
    
    recommendations = []
    
    # Severity-based recommendations
    critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL]
    high_findings = [f for f in findings if f.severity == SeverityLevel.HIGH]
    
    if critical_findings:
        recommendations.extend([
            "Immediate clinical evaluation required",
            "Consider emergency intervention if clinically indicated",
            "Notify attending physician immediately"
        ])
    
    if high_findings:
        recommendations.extend([
            "Urgent clinical correlation recommended",
            "Consider additional imaging if clinically indicated",
            "Follow-up within 24-48 hours"
        ])
    
    # Condition-specific recommendations
    conditions = [f.condition.lower() for f in findings]
    
    if "pneumonia" in conditions:
        recommendations.append("Consider antibiotic therapy and supportive care")
    
    if "pneumothorax" in conditions:
        recommendations.append("Assess need for chest tube placement")
    
    if "mass" in conditions or "nodule" in conditions:
        recommendations.extend([
            "Consider CT chest for further characterization",
            "Multidisciplinary team discussion recommended"
        ])
    
    if "cardiomegaly" in conditions:
        recommendations.append("Echocardiography recommended")
    
    if not findings:
        recommendations.append("Routine follow-up as clinically indicated")
    
    return recommendations

async def _generate_patient_recommendations(findings: List[RadiologyFinding]) -> List[str]:
    """Generate patient-friendly recommendations."""
    
    if not findings:
        return [
            "Continue with your regular healthcare routine",
            "Follow up with your doctor as scheduled",
            "Maintain healthy lifestyle habits"
        ]
    
    recommendations = []
    
    # Urgency-based recommendations
    critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL]
    high_findings = [f for f in findings if f.severity == SeverityLevel.HIGH]
    
    if critical_findings:
        recommendations.extend([
            "Contact your doctor immediately",
            "Go to the emergency room if you have severe symptoms",
            "Don't delay seeking medical care"
        ])
    elif high_findings:
        recommendations.extend([
            "Schedule an appointment with your doctor soon",
            "Monitor your symptoms closely",
            "Seek medical care if symptoms worsen"
        ])
    else:
        recommendations.extend([
            "Discuss these findings with your doctor",
            "Follow your doctor's treatment plan",
            "Attend all follow-up appointments"
        ])
    
    # General health recommendations
    recommendations.extend([
        "Take all medications as prescribed",
        "Follow a healthy diet and exercise routine",
        "Don't smoke and limit alcohol consumption"
    ])
    
    return recommendations

async def _generate_differential_diagnosis(
    findings: List[RadiologyFinding],
    clinical_history: Optional[str]
) -> List[str]:
    """Generate differential diagnosis list for doctors."""
    
    if not findings:
        return []
    
    # This would typically use medical knowledge bases
    # For now, we'll generate based on common associations
    
    differential = []
    conditions = [f.condition.lower() for f in findings]
    
    if "pneumonia" in conditions:
        differential.extend([
            "Bacterial pneumonia",
            "Viral pneumonia", 
            "Atypical pneumonia",
            "Aspiration pneumonia"
        ])
    
    if "mass" in conditions:
        differential.extend([
            "Primary lung carcinoma",
            "Metastatic disease",
            "Benign lung tumor",
            "Inflammatory pseudotumor"
        ])
    
    if "nodule" in conditions:
        differential.extend([
            "Benign granuloma",
            "Primary lung cancer",
            "Metastatic nodule",
            "Infectious nodule"
        ])
    
    if "cardiomegaly" in conditions:
        differential.extend([
            "Congestive heart failure",
            "Cardiomyopathy",
            "Valvular heart disease",
            "Pericardial effusion"
        ])
    
    return list(set(differential))  # Remove duplicates

async def _store_radiology_result(
    analysis_id: str, 
    result: RadiologyAnalysisResult, 
    user_id: int,
    clinical_history: Optional[str]
):
    """Store radiology analysis result."""
    
    os.makedirs("analysis_results", exist_ok=True)
    
    result_data = {
        "analysis_id": analysis_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "clinical_history": clinical_history,
        "result": result.dict()
    }
    
    with open(f"analysis_results/radiology_{analysis_id}.json", "w") as f:
        json.dump(result_data, f, indent=2)

async def _load_radiology_result(analysis_id: str, user_id: int) -> Optional[RadiologyAnalysisResult]:
    """Load stored radiology analysis result."""
    
    try:
        with open(f"analysis_results/radiology_{analysis_id}.json", "r") as f:
            data = json.load(f)
        
        # Verify user access
        if data["user_id"] != user_id:
            return None
        
        return RadiologyAnalysisResult(**data["result"])
    
    except FileNotFoundError:
        return None
