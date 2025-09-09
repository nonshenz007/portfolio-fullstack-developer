"""
Format Detection Utility for VeriDoc Universal

This module provides intelligent format detection capabilities that work
with the Format Rule Engine to automatically identify the best format
match for uploaded images.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ExifTags
import logging

from rules.format_rule_engine import FormatRuleEngine, FormatMatchResult

logger = logging.getLogger(__name__)


class FormatDetector:
    """
    Intelligent format detector that analyzes images and suggests
    the most appropriate format configuration.
    """
    
    def __init__(self, format_engine: Optional[FormatRuleEngine] = None):
        """
        Initialize the Format Detector.
        
        Args:
            format_engine: Optional FormatRuleEngine instance
        """
        self.format_engine = format_engine or FormatRuleEngine()
        
        # Common format indicators in filenames
        self.filename_indicators = {
            'us': ['us_visa', 'usa', 'american', 'us-visa'],
            'uae': ['ics_uae', 'uae', 'emirates', 'ics-uae'],
            'schengen': ['schengen', 'eu', 'europe', 'european'],
            'india': ['india', 'indian', 'passport'],
            'canada': ['canada', 'canadian', 'pr', 'canada-pr']
        }
        
        # Common aspect ratios for different formats
        self.aspect_ratio_hints = {
            1.0: ['us_visa', 'india_passport'],
            0.7778: ['ics_uae', 'schengen_visa'],
            0.875: ['canada_pr']
        }
    
    def detect_format(self, image_path: str, 
                     confidence_threshold: float = 0.3) -> List[FormatMatchResult]:
        """
        Detect the most likely format for an image.
        
        Args:
            image_path: Path to the image file
            confidence_threshold: Minimum confidence for results
            
        Returns:
            List of FormatMatchResult sorted by confidence
        """
        try:
            # Get image information
            image_info = self._analyze_image(image_path)
            
            # Extract metadata hints
            metadata = self._extract_metadata_hints(image_path, image_info)
            
            # Use format engine for detection
            results = self.format_engine.auto_detect_format(
                image_path=image_path,
                image_dimensions=image_info['dimensions'],
                metadata=metadata
            )
            
            # Filter by confidence threshold
            filtered_results = [r for r in results if r.confidence >= confidence_threshold]
            
            # Add additional analysis
            for result in filtered_results:
                result.quality_indicators.update(
                    self._analyze_format_quality_indicators(image_info, result.format_id)
                )
            
            logger.info(f"Format detection for {image_path}: {len(filtered_results)} candidates")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error detecting format for {image_path}: {e}")
            return []
    
    def get_best_format_match(self, image_path: str) -> Optional[FormatMatchResult]:
        """
        Get the single best format match for an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Best FormatMatchResult or None if no good match
        """
        results = self.detect_format(image_path)
        return results[0] if results else None
    
    def suggest_format_improvements(self, image_path: str, 
                                  target_format: str) -> Dict[str, Any]:
        """
        Analyze an image against a target format and suggest improvements.
        
        Args:
            image_path: Path to the image file
            target_format: Target format ID
            
        Returns:
            Dictionary with improvement suggestions
        """
        try:
            image_info = self._analyze_image(image_path)
            format_rule = self.format_engine.get_format_rule(target_format)
            
            if not format_rule:
                return {'error': f'Format {target_format} not found'}
            
            suggestions = {
                'format_id': target_format,
                'format_name': format_rule.display_name,
                'current_image': image_info,
                'improvements': [],
                'auto_fix_available': format_rule.auto_fix_enabled
            }
            
            # Check dimensions
            if format_rule.dimensions:
                dim_suggestions = self._suggest_dimension_improvements(
                    image_info['dimensions'], format_rule.dimensions
                )
                suggestions['improvements'].extend(dim_suggestions)
            
            # Check file specifications
            if format_rule.file_specs:
                file_suggestions = self._suggest_file_improvements(
                    image_info, format_rule.file_specs
                )
                suggestions['improvements'].extend(file_suggestions)
            
            # Check quality requirements
            if format_rule.quality_thresholds:
                quality_suggestions = self._suggest_quality_improvements(
                    image_info, format_rule.quality_thresholds
                )
                suggestions['improvements'].extend(quality_suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting improvements for {image_path}: {e}")
            return {'error': str(e)}
    
    def _analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image properties and metadata."""
        info = {
            'path': image_path,
            'filename': os.path.basename(image_path),
            'file_size_mb': 0,
            'dimensions': (0, 0),
            'format': '',
            'mode': '',
            'has_exif': False,
            'exif_data': {}
        }
        
        try:
            # Get file size
            info['file_size_mb'] = os.path.getsize(image_path) / (1024 * 1024)
            
            # Open image and get basic info
            with Image.open(image_path) as img:
                info['dimensions'] = img.size
                info['format'] = img.format or ''
                info['mode'] = img.mode or ''
                
                # Extract EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    info['has_exif'] = True
                    exif = img._getexif()
                    if exif:
                        for tag_id, value in exif.items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            info['exif_data'][tag] = value
        
        except Exception as e:
            logger.warning(f"Error analyzing image {image_path}: {e}")
        
        return info
    
    def _extract_metadata_hints(self, image_path: str, 
                               image_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata hints for format detection."""
        metadata = {
            'filename': image_info['filename'].lower(),
            'file_size_mb': image_info['file_size_mb'],
            'format': image_info['format'].lower(),
            'dimensions': image_info['dimensions']
        }
        
        # Extract country/format hints from filename
        filename_lower = metadata['filename']
        for country, indicators in self.filename_indicators.items():
            for indicator in indicators:
                if indicator in filename_lower:
                    metadata['country_hint'] = country
                    break
            if 'country_hint' in metadata:
                break
        
        # Extract hints from EXIF data
        exif_data = image_info.get('exif_data', {})
        if exif_data:
            # Look for software/camera hints
            software = exif_data.get('Software', '').lower()
            if software:
                metadata['software'] = software
            
            # Look for creation date
            datetime_original = exif_data.get('DateTimeOriginal')
            if datetime_original:
                metadata['creation_date'] = str(datetime_original)
        
        # Add aspect ratio hint
        width, height = image_info['dimensions']
        if height > 0:
            aspect_ratio = width / height
            metadata['aspect_ratio'] = aspect_ratio
            
            # Find closest standard aspect ratio
            closest_ratio = min(self.aspect_ratio_hints.keys(), 
                              key=lambda x: abs(x - aspect_ratio))
            if abs(closest_ratio - aspect_ratio) < 0.05:
                metadata['aspect_ratio_hint'] = closest_ratio
        
        return metadata
    
    def _analyze_format_quality_indicators(self, image_info: Dict[str, Any], 
                                         format_id: str) -> Dict[str, float]:
        """Analyze quality indicators specific to a format."""
        indicators = {}
        
        # File size indicator
        file_size = image_info['file_size_mb']
        if file_size > 0:
            if file_size < 0.5:
                indicators['file_size_quality'] = 0.3  # Too small
            elif file_size > 10:
                indicators['file_size_quality'] = 0.7  # Large but manageable
            else:
                indicators['file_size_quality'] = 1.0  # Good size
        
        # Resolution indicator
        width, height = image_info['dimensions']
        min_dimension = min(width, height)
        if min_dimension >= 600:
            indicators['resolution_quality'] = 1.0
        elif min_dimension >= 400:
            indicators['resolution_quality'] = 0.8
        elif min_dimension >= 200:
            indicators['resolution_quality'] = 0.5
        else:
            indicators['resolution_quality'] = 0.2
        
        # Format indicator
        image_format = image_info['format'].upper()
        if image_format in ['JPEG', 'JPG']:
            indicators['format_quality'] = 1.0
        elif image_format == 'PNG':
            indicators['format_quality'] = 0.9
        elif image_format in ['BMP', 'TIFF']:
            indicators['format_quality'] = 0.7
        else:
            indicators['format_quality'] = 0.5
        
        return indicators
    
    def _suggest_dimension_improvements(self, current_dims: Tuple[int, int], 
                                      target_dims: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest dimension improvements."""
        suggestions = []
        width, height = current_dims
        
        target_width = target_dims.get('width', 0)
        target_height = target_dims.get('height', 0)
        
        if target_width > 0 and target_height > 0:
            if width != target_width or height != target_height:
                suggestions.append({
                    'category': 'dimensions',
                    'issue': f'Image dimensions {width}x{height} do not match target {target_width}x{target_height}',
                    'suggestion': f'Resize image to {target_width}x{target_height} pixels',
                    'auto_fixable': True,
                    'priority': 'high'
                })
        
        # Check aspect ratio
        if 'aspect_ratio' in target_dims:
            target_ratio = target_dims['aspect_ratio']
            current_ratio = width / height if height > 0 else 1.0
            tolerance = target_dims.get('aspect_tolerance', 0.02)
            
            if abs(current_ratio - target_ratio) > tolerance:
                suggestions.append({
                    'category': 'aspect_ratio',
                    'issue': f'Aspect ratio {current_ratio:.3f} does not match target {target_ratio:.3f}',
                    'suggestion': f'Crop or resize to achieve aspect ratio of {target_ratio:.3f}',
                    'auto_fixable': True,
                    'priority': 'high'
                })
        
        return suggestions
    
    def _suggest_file_improvements(self, image_info: Dict[str, Any], 
                                 file_specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest file specification improvements."""
        suggestions = []
        
        # Check file size
        max_size = file_specs.get('max_size_mb', 0)
        if max_size > 0 and image_info['file_size_mb'] > max_size:
            suggestions.append({
                'category': 'file_size',
                'issue': f'File size {image_info["file_size_mb"]:.1f}MB exceeds maximum {max_size}MB',
                'suggestion': f'Reduce file size to under {max_size}MB by adjusting quality or dimensions',
                'auto_fixable': True,
                'priority': 'medium'
            })
        
        # Check format
        target_format = file_specs.get('format', '').upper()
        current_format = image_info['format'].upper()
        if target_format and current_format != target_format:
            suggestions.append({
                'category': 'file_format',
                'issue': f'File format {current_format} does not match required {target_format}',
                'suggestion': f'Convert image to {target_format} format',
                'auto_fixable': True,
                'priority': 'medium'
            })
        
        return suggestions
    
    def _suggest_quality_improvements(self, image_info: Dict[str, Any], 
                                    quality_specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest quality improvements (placeholder for now)."""
        suggestions = []
        
        # This would require actual image quality analysis
        # For now, just check basic requirements
        width, height = image_info['dimensions']
        min_resolution = quality_specs.get('min_resolution', 0)
        
        if min_resolution > 0 and min(width, height) < min_resolution:
            suggestions.append({
                'category': 'resolution',
                'issue': f'Image resolution {min(width, height)}px is below minimum {min_resolution}px',
                'suggestion': f'Use a higher resolution image (minimum {min_resolution}px)',
                'auto_fixable': False,
                'priority': 'high'
            })
        
        return suggestions
    
    def get_format_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Generate a compatibility matrix showing how well different formats
        match against each other.
        
        Returns:
            Dictionary mapping format pairs to compatibility scores
        """
        formats = self.format_engine.get_available_formats()
        matrix = {}
        
        for format1 in formats:
            matrix[format1] = {}
            rule1 = self.format_engine.get_format_rule(format1)
            
            for format2 in formats:
                if format1 == format2:
                    matrix[format1][format2] = 1.0
                    continue
                
                rule2 = self.format_engine.get_format_rule(format2)
                compatibility = self._calculate_format_compatibility(rule1, rule2)
                matrix[format1][format2] = compatibility
        
        return matrix
    
    def _calculate_format_compatibility(self, rule1, rule2) -> float:
        """Calculate compatibility score between two format rules."""
        if not rule1 or not rule2:
            return 0.0
        
        score = 0.0
        comparisons = 0
        
        # Compare dimensions
        if rule1.dimensions and rule2.dimensions:
            dim1 = rule1.dimensions
            dim2 = rule2.dimensions
            
            if 'aspect_ratio' in dim1 and 'aspect_ratio' in dim2:
                ratio_diff = abs(dim1['aspect_ratio'] - dim2['aspect_ratio'])
                score += max(0, 1.0 - ratio_diff * 5)  # Penalize ratio differences
                comparisons += 1
        
        # Compare face requirements
        if rule1.face_requirements and rule2.face_requirements:
            face1 = rule1.face_requirements
            face2 = rule2.face_requirements
            
            if 'height_ratio' in face1 and 'height_ratio' in face2:
                # Check overlap of height ratio ranges
                range1 = face1['height_ratio']
                range2 = face2['height_ratio']
                overlap = max(0, min(range1[1], range2[1]) - max(range1[0], range2[0]))
                total_range = max(range1[1], range2[1]) - min(range1[0], range2[0])
                score += overlap / total_range if total_range > 0 else 0
                comparisons += 1
        
        # Compare background requirements
        if rule1.background and rule2.background:
            bg1 = rule1.background
            bg2 = rule2.background
            
            if bg1.get('color') == bg2.get('color'):
                score += 1.0
                comparisons += 1
        
        return score / comparisons if comparisons > 0 else 0.0