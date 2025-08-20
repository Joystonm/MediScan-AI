from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums
class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UrgencyLevel(str, Enum):
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class AnalysisType(str, Enum):
    SKIN_LESION = "skin_lesion"
    CHEST_XRAY = "chest_xray"
    CT_SCAN = "ct_scan"
    TRIAGE = "triage"

class Language(str, Enum):
    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    IT = "it"
    PT = "pt"
    ZH = "zh"
    JA = "ja"
    KO = "ko"

# Analysis Models
class BoundingBox(BaseModel):
    x: float = Field(..., ge=0, le=1, description="X coordinate (normalized)")
    y: float = Field(..., ge=0, le=1, description="Y coordinate (normalized)")
    width: float = Field(..., ge=0, le=1, description="Width (normalized)")
    height: float = Field(..., ge=0, le=1, description="Height (normalized)")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    label: str = Field(..., description="Detection label")

class HeatmapPoint(BaseModel):
    x: int = Field(..., description="X pixel coordinate")
    y: int = Field(..., description="Y pixel coordinate")
    intensity: float = Field(..., ge=0, le=1, description="Heatmap intensity")

class VisualOverlay(BaseModel):
    bounding_boxes: List[BoundingBox] = Field(default=[], description="Detected bounding boxes")
    heatmap: List[HeatmapPoint] = Field(default=[], description="Attention heatmap")
    overlay_image_url: Optional[str] = Field(None, description="URL to overlay image")

# Skin Analysis Models
class SkinLesionCharacteristics(BaseModel):
    asymmetry_score: float = Field(..., ge=0, le=1, description="Asymmetry assessment")
    border_irregularity: float = Field(..., ge=0, le=1, description="Border irregularity")
    color_variation: float = Field(..., ge=0, le=1, description="Color variation")
    diameter_mm: Optional[float] = Field(None, description="Lesion diameter in mm")
    evolution_risk: float = Field(..., ge=0, le=1, description="Evolution risk score")

class SkinAnalysisResult(BaseModel):
    analysis_id: str = Field(..., description="Unique analysis ID")
    predictions: Dict[str, float] = Field(..., description="Classification probabilities")
    top_prediction: str = Field(..., description="Most likely condition")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence")
    risk_level: SeverityLevel = Field(..., description="Risk assessment")
    characteristics: Optional[SkinLesionCharacteristics] = Field(None, description="Lesion characteristics (optional)")
    visual_overlay: VisualOverlay = Field(..., description="Visual analysis overlay")
    recommendations: List[str] = Field(..., description="Medical recommendations")
    next_steps: List[str] = Field(..., description="Suggested next steps")
    
    # API Enhancement Fields
    ai_summary: Optional[Dict[str, Any]] = Field(None, description="AI-generated summary and explanation")
    medical_resources: Optional[Dict[str, Any]] = Field(None, description="Reference images and articles")
    keywords: Optional[Dict[str, Any]] = Field(None, description="Extracted medical keywords")
    enhancement_timestamp: Optional[str] = Field(None, description="When enhancements were generated")

# Radiology Analysis Models
class RadiologyFinding(BaseModel):
    condition: str = Field(..., description="Medical condition")
    probability: float = Field(..., ge=0, le=1, description="Detection probability")
    location: Optional[BoundingBox] = Field(None, description="Finding location")
    severity: SeverityLevel = Field(..., description="Finding severity")
    description: str = Field(..., description="Clinical description")

class RadiologyAnalysisResult(BaseModel):
    analysis_id: str = Field(..., description="Unique analysis ID")
    scan_type: str = Field(..., description="Type of scan (chest_xray, ct_scan)")
    findings: List[RadiologyFinding] = Field(..., description="Detected findings")
    overall_assessment: str = Field(..., description="Overall radiological assessment")
    urgency_level: UrgencyLevel = Field(..., description="Clinical urgency")
    visual_overlay: VisualOverlay = Field(..., description="Visual analysis overlay")
    clinical_summary: str = Field(..., description="Clinical summary")
    recommendations: List[str] = Field(..., description="Clinical recommendations")
    differential_diagnosis: List[str] = Field(default=[], description="Differential diagnoses")

# Triage Models
class SymptomInput(BaseModel):
    symptoms: str = Field(..., description="Patient symptom description")
    duration: Optional[str] = Field(None, description="Symptom duration")
    severity_self_assessment: Optional[int] = Field(None, ge=1, le=10, description="Self-assessed severity (1-10)")
    age: Optional[int] = Field(None, ge=0, le=150, description="Patient age")
    gender: Optional[str] = Field(None, description="Patient gender")
    medical_history: Optional[str] = Field(None, description="Relevant medical history")
    current_medications: Optional[str] = Field(None, description="Current medications")
    language: Language = Field(default=Language.EN, description="Preferred language")

class TriageResult(BaseModel):
    analysis_id: str = Field(..., description="Unique analysis ID")
    urgency_level: UrgencyLevel = Field(..., description="Triage urgency level")
    confidence: float = Field(..., ge=0, le=1, description="Assessment confidence")
    possible_conditions: List[Dict[str, Any]] = Field(..., description="Possible medical conditions")
    recommendations: List[str] = Field(..., description="Triage recommendations")
    next_steps: List[str] = Field(..., description="Immediate next steps")
    red_flags: List[str] = Field(default=[], description="Warning signs identified")
    estimated_wait_time: Optional[str] = Field(None, description="Estimated appropriate wait time")
    care_level: str = Field(..., description="Recommended level of care")

class ChatMessage(BaseModel):
    message: str = Field(..., description="Chat message")
    language: Language = Field(default=Language.EN, description="Message language")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    follow_up_questions: List[str] = Field(default=[], description="Suggested follow-up questions")
    urgency_update: Optional[UrgencyLevel] = Field(None, description="Updated urgency if changed")
    additional_info_needed: List[str] = Field(default=[], description="Additional information needed")

# Report Models
class ReportRequest(BaseModel):
    analysis_ids: List[str] = Field(..., description="Analysis IDs to include in report")
    report_type: str = Field(default="comprehensive", description="Type of report")
    include_images: bool = Field(default=True, description="Include images in report")
    language: Language = Field(default=Language.EN, description="Report language")
    doctor_notes: Optional[str] = Field(None, description="Additional doctor notes")

class ReportResponse(BaseModel):
    report_id: str = Field(..., description="Generated report ID")
    pdf_url: str = Field(..., description="URL to download PDF report")
    json_url: str = Field(..., description="URL to download JSON report")
    created_at: datetime = Field(..., description="Report creation timestamp")
    expires_at: datetime = Field(..., description="Report expiration timestamp")

# Annotation Models
class AnnotationCreate(BaseModel):
    analysis_id: str = Field(..., description="Analysis ID to annotate")
    annotation_type: str = Field(..., description="Type of annotation")
    coordinates: Optional[Dict[str, Any]] = Field(None, description="Annotation coordinates")
    text: str = Field(..., description="Annotation text")
    confidence_adjustment: Optional[float] = Field(None, ge=0, le=1, description="Confidence adjustment")

class AnnotationResponse(BaseModel):
    id: int
    analysis_id: str
    annotation_type: str
    coordinates: Optional[Dict[str, Any]]
    text: str
    confidence_adjustment: Optional[float]
    created_at: datetime
    updated_at: datetime

# System Models
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: float

class DetailedHealthCheck(HealthCheck):
    database_status: str
    ai_models_status: Dict[str, str]
    external_apis_status: Dict[str, str]
    memory_usage: float
    cpu_usage: float
    disk_usage: float

# Error Models
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: Optional[str] = None

# Success Response
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
