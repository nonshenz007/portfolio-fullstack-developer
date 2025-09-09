"""
Data models for face detection system.
"""
from dataclasses import dataclass
from typing import Optional, List, Tuple
import numpy as np


@dataclass
class Point:
    """Represents a 2D point."""
    x: float
    y: float


@dataclass
class BoundingBox:
    """Represents a rectangular bounding box."""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center_x(self) -> float:
        """Get the center x coordinate."""
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        """Get the center y coordinate."""
        return self.y + self.height / 2
    
    @property
    def area(self) -> int:
        """Get the area of the bounding box."""
        return self.width * self.height


@dataclass
class FacialLandmarks:
    """Represents facial landmarks detected by MediaPipe."""
    left_eye: Tuple[float, float]
    right_eye: Tuple[float, float]
    nose_tip: Tuple[float, float]
    mouth_left: Tuple[float, float]
    mouth_right: Tuple[float, float]
    chin: Tuple[float, float]
    
    @property
    def eye_center(self) -> Tuple[float, float]:
        """Get the center point between the eyes."""
        return (
            (self.left_eye[0] + self.right_eye[0]) / 2,
            (self.left_eye[1] + self.right_eye[1]) / 2
        )
    
    @property
    def eye_distance(self) -> float:
        """Get the distance between the eyes."""
        return np.sqrt(
            (self.right_eye[0] - self.left_eye[0]) ** 2 +
            (self.right_eye[1] - self.left_eye[1]) ** 2
        )


@dataclass
class FaceMetrics:
    """Calculated metrics for face positioning and compliance checks."""
    face_height_ratio: float  # Face height / image height
    eye_height_ratio: float   # Eye level / image height
    face_center_x: float      # Face center x / image width
    face_center_y: float      # Face center y / image height
    eye_distance: float       # Distance between eyes in pixels
    face_angle: float         # Face rotation angle in degrees
    eyes_open: bool          # Whether eyes appear to be open
    mouth_closed: bool       # Whether mouth appears to be closed
    
    def is_centered(self, tolerance: float = 0.1) -> bool:
        """Check if face is reasonably centered."""
        return (
            abs(self.face_center_x - 0.5) < tolerance and
            abs(self.face_center_y - 0.5) < tolerance
        )
    
    def is_straight(self, max_angle: float = 5.0) -> bool:
        """Check if face is reasonably straight."""
        return abs(self.face_angle) < max_angle


@dataclass
class FaceDetectionResult:
    """Result of face detection operation."""
    face_found: bool
    confidence: float
    bounding_box: Optional[BoundingBox]
    landmarks: Optional[FacialLandmarks]
    face_metrics: Optional[FaceMetrics]
    multiple_faces: bool = False
    processing_time: float = 0.0
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Whether detection was successful."""
        return self.face_found and self.error_message is None


@dataclass
class LandmarkResult:
    """Result of facial landmark detection."""
    success: bool
    landmarks: Optional[FacialLandmarks]
    confidence: float
    error_message: Optional[str] = None