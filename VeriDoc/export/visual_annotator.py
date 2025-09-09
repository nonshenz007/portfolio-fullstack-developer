"""
Visual Annotator for creating annotated images showing compliance measurements.
Provides comprehensive visual feedback with overlay indicators and measurements.
"""

import os
import cv2
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class VisualAnnotator:
    """
    Creates visually annotated images showing compliance measurements and issues.
    Supports multiple annotation styles and comprehensive visual feedback.
    """
    
    def __init__(self):
        """Initialize visual annotator."""
        self.logger = logging.getLogger(__name__)
        
        if not PIL_AVAILABLE:
            self.logger.warning("PIL not available. Visual annotations will use OpenCV only.")
        
        # Color scheme for annotations
        self.colors = {
            'pass': (0, 255, 0),      # Green
            'fail': (0, 0, 255),      # Red
            'warning': (0, 165, 255), # Orange
            'info': (255, 255, 0),    # Cyan
            'background': (255, 255, 255),  # White
            'text': (0, 0, 0),        # Black
            'overlay': (0, 0, 0, 128) # Semi-transparent black
        }
        
        # Annotation styles
        self.annotation_styles = {
            'minimal': self._create_minimal_annotations,
            'detailed': self._create_detailed_annotations,
            'comprehensive': self._create_comprehensive_annotations
        }
        
        # Font settings
        self.font_scale = 0.6
        self.font_thickness = 2
        self.line_thickness = 2
    
    def create_annotated_image(self, processing_result: Dict[str, Any],
                             image_path: str, export_dir: str,
                             style: str = "detailed") -> Optional[str]:
        """
        Create annotated image showing compliance measurements and issues.
        
        Args:
            processing_result: Complete processing result with validation data
            image_path: Path to original image
            export_dir: Directory for export files
            style: Annotation style ('minimal', 'detailed', 'comprehensive')
            
        Returns:
            Path to annotated image or None if failed
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Could not load image: {image_path}")
                return None
            
            # Create annotations based on style
            annotation_func = self.annotation_styles.get(style, self._create_detailed_annotations)
            annotated_image = annotation_func(image.copy(), processing_result)
            
            # Create output filename
            base_name = Path(image_path).stem
            output_filename = f"{base_name}_annotated.jpg"
            output_path = os.path.join(export_dir, output_filename)
            
            # Save annotated image
            cv2.imwrite(output_path, annotated_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            self.logger.info(f"Annotated image created: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to create annotated image: {str(e)}")
            return None
    
    def create_comparison_image(self, original_path: str, processed_path: str,
                              processing_result: Dict[str, Any],
                              export_dir: str) -> Optional[str]:
        """
        Create side-by-side comparison image showing before and after.
        
        Args:
            original_path: Path to original image
            processed_path: Path to processed image
            processing_result: Processing result data
            export_dir: Directory for export files
            
        Returns:
            Path to comparison image or None if failed
        """
        try:
            # Load images
            original = cv2.imread(original_path)
            processed = cv2.imread(processed_path)
            
            if original is None or processed is None:
                self.logger.error("Could not load comparison images")
                return None
            
            # Resize images to same height
            height = min(original.shape[0], processed.shape[0], 800)
            original_resized = self._resize_image(original, height)
            processed_resized = self._resize_image(processed, height)
            
            # Create side-by-side comparison
            comparison = np.hstack([original_resized, processed_resized])
            
            # Add labels
            comparison = self._add_comparison_labels(comparison, processing_result)
            
            # Add improvement metrics
            comparison = self._add_improvement_metrics(comparison, processing_result)
            
            # Create output filename
            base_name = Path(original_path).stem
            output_filename = f"{base_name}_comparison.jpg"
            output_path = os.path.join(export_dir, output_filename)
            
            # Save comparison image
            cv2.imwrite(output_path, comparison, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            self.logger.info(f"Comparison image created: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to create comparison image: {str(e)}")
            return None
    
    def create_batch_summary_visualization(self, batch_analysis: Dict[str, Any],
                                         export_dir: str) -> Optional[str]:
        """
        Create visual summary of batch processing results.
        
        Args:
            batch_analysis: Batch analysis results
            export_dir: Directory for export files
            
        Returns:
            Path to summary visualization or None if failed
        """
        try:
            # Create canvas for summary
            canvas_width = 1200
            canvas_height = 800
            canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
            
            # Add title
            title = "Batch Processing Summary"
            canvas = self._add_text(canvas, title, (canvas_width // 2, 50), 
                                  font_scale=1.2, color=self.colors['text'], center=True)
            
            # Add statistics
            canvas = self._add_batch_statistics(canvas, batch_analysis)
            
            # Add compliance breakdown chart
            canvas = self._add_compliance_chart(canvas, batch_analysis)
            
            # Add common issues
            canvas = self._add_common_issues(canvas, batch_analysis)
            
            # Create output filename
            output_filename = "batch_summary_visualization.jpg"
            output_path = os.path.join(export_dir, output_filename)
            
            # Save summary visualization
            cv2.imwrite(output_path, canvas, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            self.logger.info(f"Batch summary visualization created: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to create batch summary visualization: {str(e)}")
            return None
    
    def _create_minimal_annotations(self, image: np.ndarray, 
                                  processing_result: Dict[str, Any]) -> np.ndarray:
        """Create minimal annotations showing only overall status."""
        # Add overall compliance status
        compliance_score = processing_result.get('overall_compliance', 0)
        passes = processing_result.get('passes_requirements', False)
        
        status_text = f"{'PASS' if passes else 'FAIL'} - {compliance_score:.1f}%"
        status_color = self.colors['pass'] if passes else self.colors['fail']
        
        # Add status overlay
        overlay = image.copy()
        cv2.rectangle(overlay, (10, 10), (300, 60), status_color, -1)
        image = cv2.addWeighted(image, 0.8, overlay, 0.2, 0)
        
        # Add status text
        image = self._add_text(image, status_text, (20, 40), 
                             color=(255, 255, 255), font_scale=0.8)
        
        return image
    
    def _create_detailed_annotations(self, image: np.ndarray,
                                   processing_result: Dict[str, Any]) -> np.ndarray:
        """Create detailed annotations showing key measurements and issues."""
        # Add face detection overlay
        image = self._add_face_detection_overlay(image, processing_result)
        
        # Add compliance status
        image = self._add_compliance_status_overlay(image, processing_result)
        
        # Add key measurements
        image = self._add_key_measurements(image, processing_result)
        
        # Add issue indicators
        image = self._add_issue_indicators(image, processing_result)
        
        return image
    
    def _create_comprehensive_annotations(self, image: np.ndarray,
                                        processing_result: Dict[str, Any]) -> np.ndarray:
        """Create comprehensive annotations with all available information."""
        # Start with detailed annotations
        image = self._create_detailed_annotations(image, processing_result)
        
        # Add detailed validation results
        image = self._add_detailed_validation_results(image, processing_result)
        
        # Add quality metrics overlay
        image = self._add_quality_metrics_overlay(image, processing_result)
        
        # Add recommendations
        image = self._add_recommendations_overlay(image, processing_result)
        
        return image
    
    def _add_face_detection_overlay(self, image: np.ndarray,
                                  processing_result: Dict[str, Any]) -> np.ndarray:
        """Add face detection bounding box and landmarks."""
        face_data = processing_result.get('face_detection', {})
        
        if 'bbox' in face_data:
            bbox = face_data['bbox']
            x, y, w, h = bbox.get('x', 0), bbox.get('y', 0), bbox.get('width', 0), bbox.get('height', 0)
            
            # Draw face bounding box
            cv2.rectangle(image, (x, y), (x + w, y + h), self.colors['info'], 2)
            
            # Add confidence score
            confidence = face_data.get('confidence', 0)
            confidence_text = f"Face: {confidence:.2f}"
            image = self._add_text(image, confidence_text, (x, y - 10), 
                                 color=self.colors['info'], font_scale=0.5)
        
        # Add eye positions if available
        landmarks = processing_result.get('face_landmarks', {})
        if 'eye_positions' in landmarks:
            eye_positions = landmarks['eye_positions']
            for i, (ex, ey) in enumerate(eye_positions):
                cv2.circle(image, (int(ex), int(ey)), 3, self.colors['pass'], -1)
                image = self._add_text(image, f"E{i+1}", (int(ex) + 5, int(ey)), 
                                     color=self.colors['pass'], font_scale=0.4)
        
        return image
    
    def _add_compliance_status_overlay(self, image: np.ndarray,
                                     processing_result: Dict[str, Any]) -> np.ndarray:
        """Add overall compliance status overlay."""
        h, w = image.shape[:2]
        
        # Create status panel
        panel_height = 120
        panel = np.ones((panel_height, w, 3), dtype=np.uint8) * 240
        
        # Add overall status
        compliance_score = processing_result.get('overall_compliance', 0)
        passes = processing_result.get('passes_requirements', False)
        confidence = processing_result.get('confidence_score', 0)
        
        status_text = f"Overall Status: {'PASS' if passes else 'FAIL'}"
        score_text = f"Compliance Score: {compliance_score:.1f}%"
        confidence_text = f"Confidence: {confidence:.1f}%"
        
        status_color = self.colors['pass'] if passes else self.colors['fail']
        
        panel = self._add_text(panel, status_text, (10, 25), color=status_color, font_scale=0.7)
        panel = self._add_text(panel, score_text, (10, 50), color=self.colors['text'], font_scale=0.6)
        panel = self._add_text(panel, confidence_text, (10, 75), color=self.colors['text'], font_scale=0.6)
        
        # Add processing info
        processing_time = processing_result.get('processing_time', 0)
        format_name = processing_result.get('format_name', 'Unknown')
        
        time_text = f"Processing Time: {processing_time:.2f}s"
        format_text = f"Format: {format_name}"
        
        panel = self._add_text(panel, time_text, (w // 2, 25), color=self.colors['text'], font_scale=0.6)
        panel = self._add_text(panel, format_text, (w // 2, 50), color=self.colors['text'], font_scale=0.6)
        
        # Combine with original image
        combined = np.vstack([panel, image])
        
        return combined
    
    def _add_key_measurements(self, image: np.ndarray,
                            processing_result: Dict[str, Any]) -> np.ndarray:
        """Add key measurement annotations."""
        validation_results = processing_result.get('validation_results', {})
        
        y_offset = 30
        for rule_name, result in validation_results.items():
            if isinstance(result, dict) and 'score' in result:
                score = result['score']
                passes = result.get('passes', False)
                
                # Format rule name
                display_name = rule_name.replace('_', ' ').title()
                measurement_text = f"{display_name}: {score:.1f}%"
                
                color = self.colors['pass'] if passes else self.colors['fail']
                image = self._add_text(image, measurement_text, (10, y_offset), 
                                     color=color, font_scale=0.5)
                y_offset += 25
        
        return image
    
    def _add_issue_indicators(self, image: np.ndarray,
                            processing_result: Dict[str, Any]) -> np.ndarray:
        """Add visual indicators for compliance issues."""
        issues = processing_result.get('compliance_issues', [])
        
        if not issues:
            return image
        
        h, w = image.shape[:2]
        
        # Add issue markers
        for i, issue in enumerate(issues[:5]):  # Limit to top 5 issues
            severity = issue.get('severity', 'minor')
            category = issue.get('category', 'unknown')
            
            # Choose color based on severity
            if severity == 'critical':
                color = self.colors['fail']
            elif severity == 'major':
                color = self.colors['warning']
            else:
                color = self.colors['info']
            
            # Add issue marker
            marker_x = w - 50 - (i * 60)
            marker_y = 50
            
            cv2.circle(image, (marker_x, marker_y), 20, color, -1)
            cv2.circle(image, (marker_x, marker_y), 20, (0, 0, 0), 2)
            
            # Add issue number
            image = self._add_text(image, str(i + 1), (marker_x - 5, marker_y + 5), 
                                 color=(255, 255, 255), font_scale=0.6)
        
        return image
    
    def _add_detailed_validation_results(self, image: np.ndarray,
                                       processing_result: Dict[str, Any]) -> np.ndarray:
        """Add detailed validation results panel."""
        validation_results = processing_result.get('validation_results', {})
        
        if not validation_results:
            return image
        
        h, w = image.shape[:2]
        
        # Create results panel
        panel_width = 400
        panel_height = min(len(validation_results) * 30 + 40, h // 2)
        panel = np.ones((panel_height, panel_width, 3), dtype=np.uint8) * 250
        
        # Add title
        panel = self._add_text(panel, "Validation Results", (10, 25), 
                             color=self.colors['text'], font_scale=0.7)
        
        # Add results
        y_offset = 50
        for rule_name, result in validation_results.items():
            if isinstance(result, dict):
                passes = result.get('passes', False)
                score = result.get('score', 0)
                
                display_name = rule_name.replace('_', ' ').title()[:25]  # Truncate long names
                result_text = f"{display_name}: {score:.1f}%"
                
                color = self.colors['pass'] if passes else self.colors['fail']
                panel = self._add_text(panel, result_text, (10, y_offset), 
                                     color=color, font_scale=0.5)
                
                # Add pass/fail indicator
                indicator = "✓" if passes else "✗"
                panel = self._add_text(panel, indicator, (panel_width - 30, y_offset), 
                                     color=color, font_scale=0.6)
                
                y_offset += 25
        
        # Overlay panel on image
        overlay_x = w - panel_width - 10
        overlay_y = 10
        
        # Create overlay with transparency
        overlay = image.copy()
        overlay[overlay_y:overlay_y + panel_height, overlay_x:overlay_x + panel_width] = panel
        image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)
        
        return image
    
    def _add_quality_metrics_overlay(self, image: np.ndarray,
                                   processing_result: Dict[str, Any]) -> np.ndarray:
        """Add quality metrics overlay."""
        quality_metrics = processing_result.get('quality_metrics', {})
        
        if not quality_metrics:
            return image
        
        h, w = image.shape[:2]
        
        # Create quality panel
        panel_width = 300
        panel_height = 150
        panel = np.ones((panel_height, panel_width, 3), dtype=np.uint8) * 245
        
        # Add title
        panel = self._add_text(panel, "Quality Metrics", (10, 25), 
                             color=self.colors['text'], font_scale=0.7)
        
        # Add metrics
        metrics = [
            ('Sharpness', quality_metrics.get('sharpness', 0)),
            ('Lighting', quality_metrics.get('lighting', 0)),
            ('Color', quality_metrics.get('color_accuracy', 0)),
            ('Noise', quality_metrics.get('noise_level', 0))
        ]
        
        y_offset = 50
        for metric_name, value in metrics:
            metric_text = f"{metric_name}: {value:.1f}"
            
            # Color based on quality level
            if value >= 80:
                color = self.colors['pass']
            elif value >= 60:
                color = self.colors['warning']
            else:
                color = self.colors['fail']
            
            panel = self._add_text(panel, metric_text, (10, y_offset), 
                                 color=color, font_scale=0.5)
            y_offset += 25
        
        # Overlay panel on image
        overlay_x = 10
        overlay_y = h - panel_height - 10
        
        overlay = image.copy()
        overlay[overlay_y:overlay_y + panel_height, overlay_x:overlay_x + panel_width] = panel
        image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)
        
        return image
    
    def _add_recommendations_overlay(self, image: np.ndarray,
                                   processing_result: Dict[str, Any]) -> np.ndarray:
        """Add recommendations overlay."""
        recommendations = processing_result.get('recommendations', [])
        
        if not recommendations:
            return image
        
        h, w = image.shape[:2]
        
        # Create recommendations panel
        panel_width = min(w - 20, 500)
        panel_height = min(len(recommendations) * 25 + 40, 200)
        panel = np.ones((panel_height, panel_width, 3), dtype=np.uint8) * 240
        
        # Add title
        panel = self._add_text(panel, "Recommendations", (10, 25), 
                             color=self.colors['text'], font_scale=0.7)
        
        # Add recommendations
        y_offset = 50
        for i, rec in enumerate(recommendations[:6]):  # Limit to 6 recommendations
            rec_text = f"{i+1}. {rec[:60]}..."  # Truncate long recommendations
            panel = self._add_text(panel, rec_text, (10, y_offset), 
                                 color=self.colors['text'], font_scale=0.4)
            y_offset += 25
        
        # Overlay panel at bottom center
        overlay_x = (w - panel_width) // 2
        overlay_y = h - panel_height - 10
        
        overlay = image.copy()
        overlay[overlay_y:overlay_y + panel_height, overlay_x:overlay_x + panel_width] = panel
        image = cv2.addWeighted(image, 0.8, overlay, 0.2, 0)
        
        return image
    
    def _add_text(self, image: np.ndarray, text: str, position: Tuple[int, int],
                 color: Tuple[int, int, int] = (0, 0, 0), font_scale: float = 0.6,
                 center: bool = False) -> np.ndarray:
        """Add text to image with proper formatting."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = max(1, int(font_scale * 2))
        
        if center:
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            position = (position[0] - text_size[0] // 2, position[1])
        
        # Add text shadow for better visibility
        cv2.putText(image, text, (position[0] + 1, position[1] + 1), 
                   font, font_scale, (0, 0, 0), thickness + 1)
        cv2.putText(image, text, position, font, font_scale, color, thickness)
        
        return image
    
    def _resize_image(self, image: np.ndarray, target_height: int) -> np.ndarray:
        """Resize image maintaining aspect ratio."""
        h, w = image.shape[:2]
        aspect_ratio = w / h
        target_width = int(target_height * aspect_ratio)
        
        return cv2.resize(image, (target_width, target_height))
    
    def _add_comparison_labels(self, image: np.ndarray,
                             processing_result: Dict[str, Any]) -> np.ndarray:
        """Add labels to comparison image."""
        h, w = image.shape[:2]
        
        # Add "Original" and "Processed" labels
        label_y = 30
        image = self._add_text(image, "Original", (w // 4, label_y), 
                             color=self.colors['text'], font_scale=0.8, center=True)
        image = self._add_text(image, "Processed", (3 * w // 4, label_y), 
                             color=self.colors['text'], font_scale=0.8, center=True)
        
        return image
    
    def _add_improvement_metrics(self, image: np.ndarray,
                               processing_result: Dict[str, Any]) -> np.ndarray:
        """Add improvement metrics to comparison image."""
        autofix_result = processing_result.get('auto_fix_result', {})
        
        if not autofix_result:
            return image
        
        h, w = image.shape[:2]
        
        # Add improvement panel
        panel_height = 80
        panel = np.ones((panel_height, w, 3), dtype=np.uint8) * 250
        
        # Add improvement metrics
        quality_improvement = autofix_result.get('quality_improvement', 0)
        compliance_improvement = autofix_result.get('compliance_improvement', 0)
        
        improvement_text = f"Quality Improvement: +{quality_improvement:.1f}%"
        compliance_text = f"Compliance Improvement: +{compliance_improvement:.1f}%"
        
        panel = self._add_text(panel, improvement_text, (10, 30), 
                             color=self.colors['pass'], font_scale=0.6)
        panel = self._add_text(panel, compliance_text, (10, 55), 
                             color=self.colors['pass'], font_scale=0.6)
        
        # Combine with comparison image
        combined = np.vstack([image, panel])
        
        return combined
    
    def _add_batch_statistics(self, canvas: np.ndarray,
                            batch_analysis: Dict[str, Any]) -> np.ndarray:
        """Add batch statistics to summary canvas."""
        stats = batch_analysis.get('summary_statistics', {})
        
        y_offset = 100
        stats_items = [
            f"Total Images: {stats.get('total_images', 0)}",
            f"Successful: {stats.get('successful_images', 0)}",
            f"Failed: {stats.get('failed_images', 0)}",
            f"Success Rate: {stats.get('success_rate', 0):.1f}%",
            f"Average Compliance: {stats.get('avg_compliance_score', 0):.1f}%"
        ]
        
        for stat in stats_items:
            canvas = self._add_text(canvas, stat, (50, y_offset), 
                                  color=self.colors['text'], font_scale=0.7)
            y_offset += 30
        
        return canvas
    
    def _add_compliance_chart(self, canvas: np.ndarray,
                            batch_analysis: Dict[str, Any]) -> np.ndarray:
        """Add compliance breakdown chart."""
        compliance_breakdown = batch_analysis.get('compliance_breakdown', {})
        
        if not compliance_breakdown:
            return canvas
        
        # Simple bar chart
        chart_x = 400
        chart_y = 150
        bar_width = 60
        max_height = 200
        
        total_images = sum(compliance_breakdown.values())
        if total_images == 0:
            return canvas
        
        x_offset = chart_x
        for level, count in compliance_breakdown.items():
            bar_height = int((count / total_images) * max_height)
            
            # Draw bar
            cv2.rectangle(canvas, (x_offset, chart_y + max_height - bar_height),
                         (x_offset + bar_width, chart_y + max_height),
                         self.colors['info'], -1)
            
            # Add label
            canvas = self._add_text(canvas, level.replace('_', ' ').title(),
                                  (x_offset + bar_width // 2, chart_y + max_height + 20),
                                  color=self.colors['text'], font_scale=0.4, center=True)
            
            # Add count
            canvas = self._add_text(canvas, str(count),
                                  (x_offset + bar_width // 2, chart_y + max_height - bar_height - 10),
                                  color=self.colors['text'], font_scale=0.5, center=True)
            
            x_offset += bar_width + 20
        
        return canvas
    
    def _add_common_issues(self, canvas: np.ndarray,
                         batch_analysis: Dict[str, Any]) -> np.ndarray:
        """Add common issues section."""
        failure_analysis = batch_analysis.get('failure_analysis', {})
        common_issues = failure_analysis.get('common_issues', [])
        
        if not common_issues:
            return canvas
        
        # Add title
        canvas = self._add_text(canvas, "Common Issues", (50, 450), 
                              color=self.colors['text'], font_scale=0.8)
        
        # Add issues
        y_offset = 480
        for i, issue in enumerate(common_issues[:8]):  # Top 8 issues
            issue_text = f"{i+1}. {issue.get('issue', 'Unknown')} ({issue.get('count', 0)} times)"
            canvas = self._add_text(canvas, issue_text, (70, y_offset), 
                                  color=self.colors['text'], font_scale=0.5)
            y_offset += 25
        
        return canvas