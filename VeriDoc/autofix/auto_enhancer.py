"""
Auto-Enhancement Engine for VeriDoc
Automatically fixes common issues in passport photos to meet government standards.
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict, Any
from pathlib import Path


class AutoEnhancer:
    """Automatically enhance passport photos to meet compliance standards."""
    
    def __init__(self):
        """Initialize the auto-enhancer."""
        self.enhancement_history = []
    
    def enhance_photo(self, image: np.ndarray, issues: List[str]) -> Tuple[np.ndarray, List[str]]:
        """
        Automatically enhance a photo to fix compliance issues.
        
        Args:
            image: Input image as numpy array
            issues: List of issue descriptions to fix
            
        Returns:
            Tuple of (enhanced_image, operations_performed)
        """
        enhanced = image.copy()
        operations = []
        
        for issue in issues:
            issue_lower = issue.lower()
            
            # Fix brightness issues
            if 'too bright' in issue_lower:
                enhanced = self._fix_brightness(enhanced, target='darker')
                operations.append('Reduced brightness')
            elif 'too dark' in issue_lower:
                enhanced = self._fix_brightness(enhanced, target='brighter')
                operations.append('Increased brightness')
            
            # Fix contrast issues
            if 'low contrast' in issue_lower or 'contrast' in issue_lower:
                enhanced = self._enhance_contrast(enhanced)
                operations.append('Enhanced contrast')
            
            # Fix background uniformity
            if 'background not uniform' in issue_lower:
                enhanced = self._normalize_background(enhanced)
                operations.append('Normalized background')
            
            # Fix sharpness
            if 'blurry' in issue_lower or 'blur' in issue_lower:
                enhanced = self._enhance_sharpness(enhanced)
                operations.append('Enhanced sharpness')
        
        return enhanced, operations
    
    def _fix_brightness(self, image: np.ndarray, target: str = 'optimal') -> np.ndarray:
        """Fix image brightness."""
        try:
            # Convert to LAB color space for better brightness control
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            current_brightness = np.mean(l)
            
            if target == 'darker':
                # Reduce brightness by 15%
                l = np.clip(l * 0.85, 0, 255).astype(np.uint8)
            elif target == 'brighter':
                # Increase brightness by 15%
                l = np.clip(l * 1.15, 0, 255).astype(np.uint8)
            else:
                # Optimize to target brightness (around 140 in LAB L channel)
                target_brightness = 140
                adjustment = target_brightness / current_brightness
                l = np.clip(l * adjustment, 0, 255).astype(np.uint8)
            
            # Merge back and convert to BGR
            enhanced_lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception:
            # Fallback: simple brightness adjustment
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            if target == 'darker':
                v = np.clip(v * 0.9, 0, 255).astype(np.uint8)
            elif target == 'brighter':
                v = np.clip(v * 1.1, 0, 255).astype(np.uint8)
            
            enhanced_hsv = cv2.merge([h, s, v])
            return cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast."""
        try:
            # Convert to LAB and enhance L channel contrast
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge back
            enhanced_lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception:
            # Fallback: simple contrast enhancement
            return cv2.convertScaleAbs(image, alpha=1.2, beta=0)
    
    def _normalize_background(self, image: np.ndarray) -> np.ndarray:
        """Normalize background to be more uniform."""
        try:
            # Detect face region to preserve it
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Create a mask for background (everything except face)
            mask = np.ones(gray.shape, dtype=np.uint8) * 255
            
            for (x, y, w, h) in faces:
                # Expand face region slightly
                padding = 20
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(image.shape[1], x + w + padding)
                y2 = min(image.shape[0], y + h + padding)
                mask[y1:y2, x1:x2] = 0  # Exclude face from background processing
            
            # Apply Gaussian blur to background areas only
            blurred = cv2.GaussianBlur(image, (15, 15), 0)
            
            # Blend original face with smoothed background
            enhanced = image.copy()
            for c in range(3):
                enhanced[:, :, c] = np.where(mask == 255, blurred[:, :, c], image[:, :, c])
            
            return enhanced
            
        except Exception:
            # Fallback: gentle overall blur
            return cv2.GaussianBlur(image, (3, 3), 0)
    
    def _enhance_sharpness(self, image: np.ndarray) -> np.ndarray:
        """Enhance image sharpness."""
        try:
            # Create sharpening kernel
            kernel = np.array([[-1, -1, -1],
                             [-1, 9, -1],
                             [-1, -1, -1]])
            
            # Apply sharpening
            sharpened = cv2.filter2D(image, -1, kernel)
            
            # Blend with original to avoid over-sharpening
            enhanced = cv2.addWeighted(image, 0.7, sharpened, 0.3, 0)
            
            return enhanced
            
        except Exception:
            # Fallback: unsharp mask
            blurred = cv2.GaussianBlur(image, (9, 9), 0)
            enhanced = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)
            return np.clip(enhanced, 0, 255).astype(np.uint8)
    
    def auto_fix_image(self, input_path: str, output_path: str, 
                       target_format: str = 'ICS-UAE') -> Dict[str, Any]:
        """
        Automatically fix an image to meet format requirements.
        
        Args:
            input_path: Path to input image
            output_path: Path to save fixed image
            target_format: Target format for compliance
            
        Returns:
            Dictionary with fix results
        """
        try:
            # Load image
            image = cv2.imread(input_path)
            if image is None:
                return {'success': False, 'error': 'Could not load image'}
            
            # Get current validation issues
            from validation.format_validator import FormatValidator
            validator = FormatValidator()
            validation_result = validator.validate_image(input_path, target_format)
            
            if validation_result.score >= 80:
                return {
                    'success': True,
                    'message': 'Image already compliant',
                    'original_score': validation_result.score,
                    'final_score': validation_result.score,
                    'operations': []
                }
            
            # Extract issue messages
            issue_messages = [issue.message for issue in validation_result.issues if issue.auto_fixable]
            
            # Apply enhancements
            enhanced_image, operations = self.enhance_photo(image, issue_messages)
            
            # Save enhanced image
            cv2.imwrite(output_path, enhanced_image)
            
            # Validate enhanced image
            final_validation = validator.validate_image(output_path, target_format)
            
            improvement = final_validation.score - validation_result.score
            
            return {
                'success': True,
                'original_score': validation_result.score,
                'final_score': final_validation.score,
                'improvement': improvement,
                'operations': operations,
                'remaining_issues': len(final_validation.issues),
                'output_path': output_path
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


def quick_auto_fix(image_path: str, output_dir: str = 'output/auto_fixed') -> Dict[str, Any]:
    """
    Quick auto-fix function for immediate use.
    
    Args:
        image_path: Path to image to fix
        output_dir: Directory to save fixed image
        
    Returns:
        Fix results dictionary
    """
    enhancer = AutoEnhancer()
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    input_file = Path(image_path)
    output_file = Path(output_dir) / f"{input_file.stem}_fixed{input_file.suffix}"
    
    return enhancer.auto_fix_image(str(input_file), str(output_file))


if __name__ == "__main__":
    # Test the auto-enhancer
    print("🔧 Testing Auto-Enhancement System...")
    
    # This would be used with actual images
    print("Auto-enhancement system ready!")
    print("Use quick_auto_fix(image_path) to automatically fix compliance issues.")
