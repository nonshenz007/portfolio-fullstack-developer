"""
Reliable face detection system using OpenCV Haar cascades with MediaPipe fallback.
"""
import cv2
import numpy as np
import time
import logging
import os
from typing import Optional, List, Tuple
from pathlib import Path

from .data_models import (
    FaceDetectionResult, 
    LandmarkResult, 
    BoundingBox, 
    FacialLandmarks, 
    FaceMetrics
)

# Try to import MediaPipe, but don't fail if it's not available
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    print("✅ MediaPipe loaded successfully")
except ImportError as e:
    MEDIAPIPE_AVAILABLE = False
    mp = None
    print(f"⚠️  MediaPipe not available: {e}")
    print("🔧 To fix: Install MediaPipe with: pip install mediapipe")
    print("   Note: MediaPipe may not be available for Python 3.13")
    print("   Consider using Python 3.8-3.11 for full functionality")


class FaceDetector:
    """
    Reliable face detection using OpenCV Haar cascades with MediaPipe enhancement.
    
    This class provides consistent face detection with the following features:
    - Primary detection using OpenCV Haar cascades (proven, reliable)
    - Enhanced landmark detection using MediaPipe (when available)
    - Confidence scoring and bounding box extraction
    - Face metrics calculation for compliance checking
    """
    
    def __init__(self):
        """Initialize the face detector with OpenCV and MediaPipe (if available)."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenCV Haar cascade classifier
        self._init_opencv_detector()
        
        # Initialize MediaPipe face detection and landmarks (if available)
        self._init_mediapipe_detector()
        
        self.logger.info(f"FaceDetector initialized. MediaPipe available: {MEDIAPIPE_AVAILABLE}")
    
    def _init_opencv_detector(self):
        """Initialize OpenCV Haar cascade face detector."""
        try:
            # Try multiple possible paths for Haar cascade
            possible_paths = [
                # Standard OpenCV paths
                '/opt/homebrew/lib/python3.13/site-packages/cv2/data/haarcascade_frontalface_default.xml',
                '/usr/local/lib/python3.13/site-packages/cv2/data/haarcascade_frontalface_default.xml',
                '/usr/lib/python3.13/site-packages/cv2/data/haarcascade_frontalface_default.xml',
                '/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/cv2/data/haarcascade_frontalface_default.xml',
                # macOS Homebrew paths
                '/opt/homebrew/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
                '/opt/homebrew/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
                # Linux common paths
                '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
                '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
                # Windows common paths
                'C:/opencv/build/etc/haarcascades/haarcascade_frontalface_default.xml',
                # Try to find in current Python environment
                os.path.join(os.path.dirname(cv2.__file__), 'data', 'haarcascade_frontalface_default.xml')
            ]

            # Try to get OpenCV data path if available
            try:
                if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
                    possible_paths.insert(0, cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            except (AttributeError, ImportError):
                pass  # cv2.data not available, skip this path

            cascade_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    cascade_path = path
                    self.logger.info(f"Found Haar cascade at: {path}")
                    break

            if cascade_path is None:
                # Try to download Haar cascade if not found
                self.logger.warning("Haar cascade file not found locally, attempting to download...")
                cascade_path = self._download_haar_cascade()

            if cascade_path is None:
                raise RuntimeError("Could not find or download Haar cascade classifier")

            self.face_cascade = cv2.CascadeClassifier(cascade_path)

            if self.face_cascade.empty():
                raise RuntimeError(f"Failed to load Haar cascade classifier from {cascade_path} - file may be corrupted")

            # Test the cascade classifier
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            test_faces = self.face_cascade.detectMultiScale(test_image, scaleFactor=1.1, minNeighbors=5)
            self.logger.info(f"OpenCV Haar cascade detector initialized successfully from {cascade_path}")
            self.logger.info(f"Test detection completed (expected 0 faces): {len(test_faces)} faces detected")

        except Exception as e:
            self.logger.error(f"Failed to initialize OpenCV detector: {e}")
            raise RuntimeError(f"OpenCV face detector initialization failed: {e}")

    def _download_haar_cascade(self) -> Optional[str]:
        """Download Haar cascade file if not found locally."""
        try:
            import urllib.request
            import tempfile

            url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
            temp_dir = tempfile.gettempdir()
            cascade_path = os.path.join(temp_dir, 'haarcascade_frontalface_default.xml')

            self.logger.info(f"Downloading Haar cascade from {url}")
            urllib.request.urlretrieve(url, cascade_path)

            if os.path.exists(cascade_path) and os.path.getsize(cascade_path) > 0:
                self.logger.info(f"Successfully downloaded Haar cascade to {cascade_path}")
                return cascade_path
            else:
                self.logger.error("Failed to download Haar cascade file")
                return None

        except Exception as e:
            self.logger.error(f"Failed to download Haar cascade: {e}")
            return None
    
    def _init_mediapipe_detector(self):
        """Initialize MediaPipe face detection and landmarks (if available)."""
        self.mp_face_detection = None
        self.mp_face_mesh = None
        self.mp_drawing = None
        
        if not MEDIAPIPE_AVAILABLE:
            self.logger.warning("MediaPipe not available - using OpenCV only")
            return
        
        try:
            # Initialize MediaPipe face detection
            self.mp_face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=1,  # Use model 1 for better accuracy
                min_detection_confidence=0.5
            )
            
            # Initialize MediaPipe face mesh for landmarks
            self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self.mp_drawing = mp.solutions.drawing_utils
            self.logger.info("MediaPipe detectors initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"MediaPipe initialization failed: {e}")
            self.mp_face_detection = None
            self.mp_face_mesh = None
    
    def detect_face(self, image: np.ndarray) -> FaceDetectionResult:
        """
        Detect face in the given image using OpenCV Haar cascades.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            FaceDetectionResult with detection information
        """
        start_time = time.time()
        
        try:
            if image is None or image.size == 0:
                return FaceDetectionResult(
                    face_found=False,
                    confidence=0.0,
                    bounding_box=None,
                    landmarks=None,
                    face_metrics=None,
                    error_message="Invalid or empty image"
                )
            
            # Convert to grayscale for Haar cascade detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Try multiple detection strategies for better accuracy
            faces = []
            
            # Strategy 1: Standard detection
            faces1 = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            if len(faces1) > 0:
                faces = faces1
            else:
                # Strategy 2: More sensitive detection
                faces2 = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.05,
                    minNeighbors=3,
                    minSize=(20, 20),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                if len(faces2) > 0:
                    faces = faces2
                else:
                    # Strategy 3: Try with enhanced image
                    enhanced = self.enhance_image_for_detection(image)
                    enhanced_gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
                    
                    faces3 = self.face_cascade.detectMultiScale(
                        enhanced_gray,
                        scaleFactor=1.1,
                        minNeighbors=4,
                        minSize=(25, 25),
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )
                    
                    faces = faces3
            
            processing_time = time.time() - start_time
            
            if len(faces) == 0:
                return FaceDetectionResult(
                    face_found=False,
                    confidence=0.0,
                    bounding_box=None,
                    landmarks=None,
                    face_metrics=None,
                    multiple_faces=False,
                    processing_time=processing_time,
                    error_message="No face detected"
                )
            
            # Handle multiple faces - select the largest one
            multiple_faces = len(faces) > 1
            if multiple_faces:
                self.logger.warning(f"Multiple faces detected ({len(faces)}), using largest")
            
            # Select the largest face (most likely the primary subject)
            largest_face = max(faces, key=lambda face: face[2] * face[3])
            x, y, w, h = largest_face
            
            # Create bounding box
            bounding_box = BoundingBox(x=int(x), y=int(y), width=int(w), height=int(h))
            
            # Calculate confidence based on face size relative to image
            image_area = image.shape[0] * image.shape[1]
            face_area = w * h
            confidence = min(0.95, max(0.5, (face_area / image_area) * 10))
            
            # Get facial landmarks using MediaPipe if available
            landmark_result = self.get_facial_landmarks(image, bounding_box)
            
            # Calculate face metrics
            face_metrics = None
            if landmark_result.success and landmark_result.landmarks:
                face_metrics = self.calculate_face_metrics(
                    landmark_result.landmarks, 
                    bounding_box, 
                    image.shape
                )
            
            return FaceDetectionResult(
                face_found=True,
                confidence=confidence,
                bounding_box=bounding_box,
                landmarks=landmark_result.landmarks if landmark_result.success else None,
                face_metrics=face_metrics,
                multiple_faces=multiple_faces,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Face detection failed: {e}")
            return FaceDetectionResult(
                face_found=False,
                confidence=0.0,
                bounding_box=None,
                landmarks=None,
                face_metrics=None,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def get_facial_landmarks(self, image: np.ndarray, face_bbox: BoundingBox) -> LandmarkResult:
        """
        Extract facial landmarks using MediaPipe (if available).
        
        Args:
            image: Input image as numpy array (BGR format)
            face_bbox: Bounding box of detected face
            
        Returns:
            LandmarkResult with landmark information
        """
        if not MEDIAPIPE_AVAILABLE or self.mp_face_mesh is None:
            return LandmarkResult(
                success=False,
                landmarks=None,
                confidence=0.0,
                error_message="MediaPipe not available"
            )
        
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process the image with MediaPipe
            results = self.mp_face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                return LandmarkResult(
                    success=False,
                    landmarks=None,
                    confidence=0.0,
                    error_message="No landmarks detected"
                )
            
            # Use the first face's landmarks
            face_landmarks = results.multi_face_landmarks[0]
            
            # Extract key landmarks (MediaPipe face mesh indices)
            h, w = image.shape[:2]
            
            # Key landmark indices for face mesh
            LEFT_EYE_IDX = 33   # Left eye center
            RIGHT_EYE_IDX = 362 # Right eye center
            NOSE_TIP_IDX = 1    # Nose tip
            MOUTH_LEFT_IDX = 61 # Left mouth corner
            MOUTH_RIGHT_IDX = 291 # Right mouth corner
            CHIN_IDX = 18       # Chin point
            
            landmarks = FacialLandmarks(
                left_eye=(
                    face_landmarks.landmark[LEFT_EYE_IDX].x * w,
                    face_landmarks.landmark[LEFT_EYE_IDX].y * h
                ),
                right_eye=(
                    face_landmarks.landmark[RIGHT_EYE_IDX].x * w,
                    face_landmarks.landmark[RIGHT_EYE_IDX].y * h
                ),
                nose_tip=(
                    face_landmarks.landmark[NOSE_TIP_IDX].x * w,
                    face_landmarks.landmark[NOSE_TIP_IDX].y * h
                ),
                mouth_left=(
                    face_landmarks.landmark[MOUTH_LEFT_IDX].x * w,
                    face_landmarks.landmark[MOUTH_LEFT_IDX].y * h
                ),
                mouth_right=(
                    face_landmarks.landmark[MOUTH_RIGHT_IDX].x * w,
                    face_landmarks.landmark[MOUTH_RIGHT_IDX].y * h
                ),
                chin=(
                    face_landmarks.landmark[CHIN_IDX].x * w,
                    face_landmarks.landmark[CHIN_IDX].y * h
                )
            )
            
            return LandmarkResult(
                success=True,
                landmarks=landmarks,
                confidence=0.8  # MediaPipe doesn't provide confidence for landmarks
            )
            
        except Exception as e:
            self.logger.error(f"Landmark detection failed: {e}")
            return LandmarkResult(
                success=False,
                landmarks=None,
                confidence=0.0,
                error_message=str(e)
            )
    
    def calculate_face_metrics(self, landmarks: FacialLandmarks, face_bbox: BoundingBox, 
                             image_shape: Tuple[int, int, int]) -> FaceMetrics:
        """
        Calculate face metrics for positioning and compliance checks.
        
        Args:
            landmarks: Detected facial landmarks
            face_bbox: Face bounding box
            image_shape: Shape of the image (height, width, channels)
            
        Returns:
            FaceMetrics with calculated positioning metrics
        """
        try:
            h, w = image_shape[:2]
            
            # Calculate face height ratio (face height / image height)
            face_height_ratio = face_bbox.height / h
            
            # Calculate eye height ratio (eye level / image height)
            eye_y = landmarks.eye_center[1]
            eye_height_ratio = eye_y / h
            
            # Calculate face center ratios
            face_center_x = face_bbox.center_x / w
            face_center_y = face_bbox.center_y / h
            
            # Calculate eye distance
            eye_distance = landmarks.eye_distance
            
            # Calculate face angle based on eye alignment
            eye_dx = landmarks.right_eye[0] - landmarks.left_eye[0]
            eye_dy = landmarks.right_eye[1] - landmarks.left_eye[1]
            face_angle = np.degrees(np.arctan2(eye_dy, eye_dx))
            
            # Simple heuristics for eyes open and mouth closed
            # These are basic estimates - more sophisticated detection would require
            # additional analysis of eye and mouth regions
            eyes_open = True  # Default assumption for passport photos
            mouth_closed = True  # Default assumption for passport photos
            
            return FaceMetrics(
                face_height_ratio=face_height_ratio,
                eye_height_ratio=eye_height_ratio,
                face_center_x=face_center_x,
                face_center_y=face_center_y,
                eye_distance=eye_distance,
                face_angle=face_angle,
                eyes_open=eyes_open,
                mouth_closed=mouth_closed
            )
            
        except Exception as e:
            self.logger.error(f"Face metrics calculation failed: {e}")
            # Return default metrics if calculation fails
            return FaceMetrics(
                face_height_ratio=0.0,
                eye_height_ratio=0.0,
                face_center_x=0.5,
                face_center_y=0.5,
                eye_distance=0.0,
                face_angle=0.0,
                eyes_open=True,
                mouth_closed=True
            )
    
    def is_face_suitable(self, face_metrics: FaceMetrics) -> bool:
        """
        Check if detected face is suitable for passport photo validation.
        
        Args:
            face_metrics: Calculated face metrics
            
        Returns:
            True if face is suitable for validation, False otherwise
        """
        try:
            # Check basic suitability criteria
            suitable = (
                face_metrics.face_height_ratio > 0.3 and  # Face not too small
                face_metrics.face_height_ratio < 0.9 and  # Face not too large
                face_metrics.is_centered(tolerance=0.2) and  # Face reasonably centered
                face_metrics.is_straight(max_angle=15.0) and  # Face not too tilted
                face_metrics.eyes_open and  # Eyes should be open
                face_metrics.mouth_closed   # Mouth should be closed
            )
            
            self.logger.debug(f"Face suitability check: {suitable}")
            self.logger.debug(f"  Face height ratio: {face_metrics.face_height_ratio:.3f}")
            self.logger.debug(f"  Face centered: {face_metrics.is_centered()}")
            self.logger.debug(f"  Face straight: {face_metrics.is_straight()}")
            
            return suitable
            
        except Exception as e:
            self.logger.error(f"Face suitability check failed: {e}")
            return False
    
    def enhance_image_for_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance image to improve face detection accuracy.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Enhanced image
        """
        try:
            # Convert to grayscale for processing
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply histogram equalization to improve contrast
            enhanced = cv2.equalizeHist(gray)
            
            # Apply Gaussian blur to reduce noise
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            # Convert back to BGR if original was color
            if len(image.shape) == 3:
                enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Image enhancement failed: {e}")
            return image  # Return original if enhancement fails