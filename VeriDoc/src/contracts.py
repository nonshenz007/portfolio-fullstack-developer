"""
Government-Grade VeriDoc Contracts

This module defines the core interfaces and contracts for the government-grade
VeriDoc system. These interfaces MUST NOT be broken as they form the 
architectural foundation.

DO NOT MODIFY these interfaces without explicit approval.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Protocol
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import numpy as np
from pathlib import Path


# =================== CORE DATA MODELS ===================

class SecurityLevel(Enum):
    """Security classification levels"""
    UNCLASSIFIED = "UNCLASSIFIED"
    CONFIDENTIAL = "CONFIDENTIAL"
    SECRET = "SECRET"
    TOP_SECRET = "TOP_SECRET"


class ProcessingResult(Enum):
    """Processing operation results"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    WARNING = "WARNING"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"


@dataclass
class Point:
    """2D coordinate point"""
    x: float
    y: float


@dataclass
class BoundingBox:
    """Rectangular bounding box"""
    x: float
    y: float
    width: float
    height: float
    confidence: float = 1.0


@dataclass
class Rotation3D:
    """3D rotation angles"""
    yaw: float
    pitch: float
    roll: float


@dataclass
class SecurityContext:
    """Security context for operations"""
    user_id: str
    session_id: str
    security_level: SecurityLevel
    permissions: List[str]
    timestamp: datetime
    source_ip: Optional[str] = None


@dataclass
class ValidationIssue:
    """Validation issue description"""
    severity: str  # CRITICAL, ERROR, WARNING, INFO
    category: str  # GEOMETRY, QUALITY, COMPLIANCE, SECURITY
    code: str
    message: str
    details: Dict[str, Any]
    suggested_fix: Optional[str] = None


@dataclass
class ComplianceResult:
    """Compliance validation result"""
    passed: bool
    score: float  # 0.0 to 1.0
    issues: List[ValidationIssue]
    requirements_met: Dict[str, bool]
    measurements: Dict[str, float]
    timestamp: datetime


@dataclass
class ProcessingMetrics:
    """Processing performance metrics"""
    processing_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    operations_performed: List[str]
    ai_model_inference_times: Dict[str, float]


# =================== SECURITY INTERFACES ===================

class IEncryptionManager(ABC):
    """Interface for encryption operations"""
    
    @abstractmethod
    def encrypt_data(self, data: bytes, context: SecurityContext) -> bytes:
        """Encrypt data using AES-256"""
        pass
    
    @abstractmethod
    def decrypt_data(self, encrypted_data: bytes, context: SecurityContext) -> bytes:
        """Decrypt data using AES-256"""
        pass
    
    @abstractmethod
    def generate_signature(self, data: bytes, context: SecurityContext) -> str:
        """Generate digital signature"""
        pass
    
    @abstractmethod
    def verify_signature(self, data: bytes, signature: str, context: SecurityContext) -> bool:
        """Verify digital signature"""
        pass


class IAuditLogger(ABC):
    """Interface for tamper-proof audit logging"""
    
    @abstractmethod
    def log_security_event(self, event_type: str, resource: str, action: str, 
                          result: ProcessingResult, context: SecurityContext,
                          details: Dict[str, Any]) -> str:
        """Log security event with tamper-proof signature"""
        pass
    
    @abstractmethod
    def log_processing_event(self, operation: str, resource: str, 
                           result: ProcessingResult, metrics: ProcessingMetrics,
                           context: SecurityContext) -> str:
        """Log processing event"""
        pass
    
    @abstractmethod
    def verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify audit log integrity"""
        pass


class IAccessControl(ABC):
    """Interface for Role-Based Access Control"""
    
    @abstractmethod
    def authenticate_user(self, user_id: str, credentials: Dict[str, Any]) -> Optional[SecurityContext]:
        """Authenticate user and create security context"""
        pass
    
    @abstractmethod
    def authorize_operation(self, context: SecurityContext, resource: str, action: str) -> bool:
        """Check if user is authorized for operation"""
        pass
    
    @abstractmethod
    def create_session(self, user_id: str) -> str:
        """Create secure session"""
        pass
    
    @abstractmethod
    def validate_session(self, session_id: str) -> Optional[SecurityContext]:
        """Validate session and return context"""
        pass


# =================== AI MODEL INTERFACES ===================

@dataclass
class FaceDetectionResult:
    """Face detection result"""
    face_found: bool
    confidence: float
    bounding_box: Optional[BoundingBox]
    landmarks_68: List[Point]  # Standard 68-point landmarks
    landmarks_468: List[Point]  # High-resolution MediaPipe landmarks
    face_angle: Rotation3D
    quality_metrics: Dict[str, float]


@dataclass
class SegmentationResult:
    """Background segmentation result"""
    mask: np.ndarray  # Binary mask
    confidence_map: np.ndarray  # Per-pixel confidence
    subject_area: float  # Percentage of image that is subject
    background_uniformity: float
    quality_score: float


@dataclass
class EnhancementResult:
    """Image enhancement result"""
    enhanced_image: np.ndarray
    operations_applied: List[str]
    quality_improvement: float
    processing_time_ms: float
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]


class IFaceDetector(ABC):
    """Interface for face detection engines"""
    
    @abstractmethod
    def detect_face(self, image: np.ndarray, context: SecurityContext) -> FaceDetectionResult:
        """Detect face with landmarks using YOLOv8 + MediaPipe"""
        pass
    
    @abstractmethod
    def validate_face_geometry(self, result: FaceDetectionResult, 
                             format_rules: Dict[str, Any]) -> ComplianceResult:
        """Validate face geometry against ICAO/format rules"""
        pass


class IBackgroundProcessor(ABC):
    """Interface for background processing engines"""
    
    @abstractmethod
    def segment_background(self, image: np.ndarray, context: SecurityContext) -> SegmentationResult:
        """Segment background using SAM + U2Net"""
        pass
    
    @abstractmethod
    def replace_background(self, image: np.ndarray, mask: np.ndarray,
                          target_color: tuple, context: SecurityContext) -> np.ndarray:
        """Replace background while preserving subject"""
        pass
    
    @abstractmethod
    def validate_background(self, image: np.ndarray, mask: np.ndarray,
                          format_rules: Dict[str, Any]) -> ComplianceResult:
        """Validate background compliance"""
        pass


class IEnhancementEngine(ABC):
    """Interface for AI-powered enhancement"""
    
    @abstractmethod
    def enhance_image(self, image: np.ndarray, enhancement_type: str,
                     context: SecurityContext) -> EnhancementResult:
        """Enhance image using ESRGAN/NAFNet"""
        pass
    
    @abstractmethod
    def auto_fix_issues(self, image: np.ndarray, issues: List[ValidationIssue],
                       context: SecurityContext) -> EnhancementResult:
        """Automatically fix detected issues"""
        pass


# =================== VALIDATION INTERFACES ===================

class IQualityAnalyzer(ABC):
    """Interface for image quality analysis"""
    
    @abstractmethod
    def analyze_sharpness(self, image: np.ndarray) -> float:
        """Analyze image sharpness (Laplacian variance)"""
        pass
    
    @abstractmethod
    def analyze_lighting(self, image: np.ndarray, face_region: BoundingBox) -> Dict[str, float]:
        """Analyze lighting quality and uniformity"""
        pass
    
    @abstractmethod
    def analyze_compression(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze compression artifacts"""
        pass
    
    @abstractmethod
    def comprehensive_quality_check(self, image: np.ndarray) -> ComplianceResult:
        """Comprehensive quality analysis"""
        pass


class IComplianceValidator(ABC):
    """Interface for compliance validation"""
    
    @abstractmethod
    def validate_icao_compliance(self, image: np.ndarray, face_result: FaceDetectionResult,
                                context: SecurityContext) -> ComplianceResult:
        """Validate against ICAO Doc 9303 requirements"""
        pass
    
    @abstractmethod
    def validate_format_compliance(self, image: np.ndarray, format_spec: Dict[str, Any],
                                  context: SecurityContext) -> ComplianceResult:
        """Validate against specific format requirements"""
        pass
    
    @abstractmethod
    def generate_compliance_certificate(self, results: List[ComplianceResult],
                                      context: SecurityContext) -> Dict[str, Any]:
        """Generate digitally signed compliance certificate"""
        pass


# =================== PIPELINE INTERFACES ===================

@dataclass
class ProcessingJob:
    """Processing job definition"""
    job_id: str
    input_path: Path
    output_path: Path
    format_specification: str
    processing_options: Dict[str, Any]
    context: SecurityContext
    priority: int = 5  # 1-10, higher is more priority
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ProcessingReport:
    """Comprehensive processing report"""
    job_id: str
    success: bool
    processing_time_ms: float
    face_detection: Optional[FaceDetectionResult]
    segmentation: Optional[SegmentationResult]
    enhancements: List[EnhancementResult]
    quality_analysis: ComplianceResult
    compliance_results: List[ComplianceResult]
    issues: List[ValidationIssue]
    metrics: ProcessingMetrics
    security_signature: str
    context: SecurityContext


class IProcessingPipeline(ABC):
    """Interface for the main processing pipeline"""
    
    @abstractmethod
    def process_image(self, job: ProcessingJob) -> ProcessingReport:
        """Process single image through complete pipeline"""
        pass
    
    @abstractmethod
    def process_batch(self, jobs: List[ProcessingJob]) -> List[ProcessingReport]:
        """Process batch of images with concurrency"""
        pass
    
    @abstractmethod
    def get_processing_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of processing job"""
        pass
    
    @abstractmethod
    def cancel_job(self, job_id: str, context: SecurityContext) -> bool:
        """Cancel processing job"""
        pass


class IProcessingController(ABC):
    """Interface for processing orchestration"""
    
    @abstractmethod
    def submit_job(self, job: ProcessingJob) -> str:
        """Submit job to processing queue"""
        pass
    
    @abstractmethod
    def get_queue_status(self) -> Dict[str, Any]:
        """Get processing queue status"""
        pass
    
    @abstractmethod
    def set_concurrency_limit(self, limit: int) -> None:
        """Set maximum concurrent processing jobs"""
        pass
    
    @abstractmethod
    def emergency_shutdown(self, context: SecurityContext) -> bool:
        """Emergency shutdown of all processing"""
        pass


# =================== PERFORMANCE INTERFACES ===================

class IPerformanceMonitor(ABC):
    """Interface for performance monitoring"""
    
    @abstractmethod
    def start_monitoring(self, operation: str) -> str:
        """Start monitoring operation"""
        pass
    
    @abstractmethod
    def stop_monitoring(self, monitor_id: str) -> ProcessingMetrics:
        """Stop monitoring and get metrics"""
        pass
    
    @abstractmethod
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        pass
    
    @abstractmethod
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize memory usage and garbage collection"""
        pass


# =================== ERROR HANDLING INTERFACES ===================

@dataclass
class ErrorContext:
    """Error context information"""
    operation: str
    component: str
    error_type: str
    error_message: str
    stack_trace: str
    security_context: SecurityContext
    timestamp: datetime
    system_state: Dict[str, Any]


class IErrorHandler(ABC):
    """Interface for comprehensive error handling"""
    
    @abstractmethod
    def handle_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Handle error with recovery attempt"""
        pass
    
    @abstractmethod
    def classify_error(self, error: Exception) -> str:
        """Classify error type and severity"""
        pass
    
    @abstractmethod
    def suggest_recovery(self, error_context: ErrorContext) -> List[str]:
        """Suggest recovery actions"""
        pass
    
    @abstractmethod
    def log_error_for_analysis(self, error_context: ErrorContext) -> str:
        """Log error for analysis and debugging"""
        pass


# =================== CONFIGURATION INTERFACES ===================

class IConfigurationManager(ABC):
    """Interface for configuration management"""
    
    @abstractmethod
    def load_configuration(self, config_type: str, context: SecurityContext) -> Dict[str, Any]:
        """Load encrypted configuration"""
        pass
    
    @abstractmethod
    def save_configuration(self, config_type: str, config_data: Dict[str, Any],
                          context: SecurityContext) -> bool:
        """Save encrypted configuration"""
        pass
    
    @abstractmethod
    def hot_reload_configuration(self, config_type: str, context: SecurityContext) -> bool:
        """Hot reload configuration without restart"""
        pass
    
    @abstractmethod
    def validate_configuration(self, config_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate configuration data"""
        pass


# =================== UI INTERFACES ===================

class IUIController(ABC):
    """Interface for UI controller (government-grade UI support)"""
    
    @abstractmethod
    def update_processing_status(self, job_id: str, status: Dict[str, Any]) -> None:
        """Update UI with processing status"""
        pass
    
    @abstractmethod
    def display_compliance_overlay(self, image_path: str, 
                                  compliance_result: ComplianceResult) -> None:
        """Display compliance overlay on image"""
        pass
    
    @abstractmethod
    def show_security_alert(self, alert_type: str, message: str, 
                           context: SecurityContext) -> None:
        """Show security alert to user"""
        pass
    
    @abstractmethod
    def request_user_confirmation(self, operation: str, context: SecurityContext) -> bool:
        """Request user confirmation for sensitive operation"""
        pass


# =================== PROTOCOL DEFINITIONS ===================

class ModelProvider(Protocol):
    """Protocol for AI model providers"""
    
    def load_model(self, model_path: str, device: str) -> Any:
        """Load AI model"""
        ...
    
    def predict(self, model: Any, input_data: np.ndarray) -> Any:
        """Run model prediction"""
        ...
    
    def get_model_info(self, model: Any) -> Dict[str, Any]:
        """Get model information"""
        ...


class StorageProvider(Protocol):
    """Protocol for secure storage providers"""
    
    def store_encrypted(self, key: str, data: bytes, context: SecurityContext) -> bool:
        """Store encrypted data"""
        ...
    
    def retrieve_encrypted(self, key: str, context: SecurityContext) -> Optional[bytes]:
        """Retrieve and decrypt data"""
        ...
    
    def delete_secure(self, key: str, context: SecurityContext) -> bool:
        """Securely delete data"""
        ...


# =================== FACTORY INTERFACES ===================

class IServiceFactory(ABC):
    """Factory for creating service instances"""
    
    @abstractmethod
    def create_face_detector(self) -> IFaceDetector:
        """Create face detector instance"""
        pass
    
    @abstractmethod
    def create_background_processor(self) -> IBackgroundProcessor:
        """Create background processor instance"""
        pass
    
    @abstractmethod
    def create_enhancement_engine(self) -> IEnhancementEngine:
        """Create enhancement engine instance"""
        pass
    
    @abstractmethod
    def create_compliance_validator(self) -> IComplianceValidator:
        """Create compliance validator instance"""
        pass
    
    @abstractmethod
    def create_processing_pipeline(self) -> IProcessingPipeline:
        """Create processing pipeline instance"""
        pass


# =================== CONSTANTS ===================

class SecurityConstants:
    """Security-related constants"""
    AES_KEY_LENGTH = 256
    RSA_KEY_LENGTH = 4096
    SESSION_TIMEOUT_MINUTES = 30
    MAX_FAILED_ATTEMPTS = 3
    AUDIT_RETENTION_DAYS = 2555  # 7 years
    
    # Permission levels
    PERMISSION_READ = "READ"
    PERMISSION_WRITE = "WRITE"
    PERMISSION_ADMIN = "ADMIN"
    PERMISSION_SECURITY = "SECURITY"


class ProcessingConstants:
    """Processing-related constants"""
    MAX_IMAGE_SIZE_MB = 50
    MAX_BATCH_SIZE = 1000
    DEFAULT_TIMEOUT_SECONDS = 300
    MAX_CONCURRENT_JOBS = 10
    
    # Quality thresholds
    MIN_SHARPNESS_LAPLACIAN = 120.0
    MIN_FACE_CONFIDENCE = 0.85
    MIN_COMPLIANCE_SCORE = 0.95


class AIModelConstants:
    """AI model constants"""
    YOLO_INPUT_SIZE = (640, 640)
    SAM_INPUT_SIZE = (1024, 1024)
    ESRGAN_MAX_INPUT_SIZE = (2048, 2048)
    
    # Model confidence thresholds
    FACE_DETECTION_THRESHOLD = 0.5
    SEGMENTATION_THRESHOLD = 0.3
    QUALITY_THRESHOLD = 0.7
