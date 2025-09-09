"""
Metadata Embedder for embedding compliance information in image EXIF data.
Supports comprehensive metadata embedding with compliance scores and validation results.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import piexif
    PIEXIF_AVAILABLE = True
except ImportError:
    PIEXIF_AVAILABLE = False


class MetadataEmbedder:
    """
    Embeds comprehensive compliance metadata in image EXIF data.
    Supports both PIL and piexif for maximum compatibility.
    """
    
    def __init__(self):
        """Initialize metadata embedder."""
        self.logger = logging.getLogger(__name__)
        
        if not PIL_AVAILABLE:
            self.logger.warning("PIL not available. Metadata embedding will be limited.")
        
        if not PIEXIF_AVAILABLE:
            self.logger.warning("piexif not available. Advanced EXIF editing will be limited.")
        
        # Custom EXIF tags for compliance data
        self.compliance_tags = {
            'VeriDocVersion': 'Veridoc Universal v2.0',
            'ComplianceScore': 'Overall compliance score (0-100)',
            'ValidationStatus': 'PASS/FAIL validation status',
            'ProcessingDate': 'Date and time of processing',
            'ICAOCompliance': 'ICAO standard compliance details',
            'QualityMetrics': 'Image quality assessment results',
            'ValidationResults': 'Detailed validation results',
            'ProcessingMetrics': 'Processing performance metrics'
        }
    
    def embed_compliance_metadata(self, processing_result: Dict[str, Any], 
                                image_path: str) -> bool:
        """
        Embed comprehensive compliance metadata in image EXIF data.
        
        Args:
            processing_result: Complete processing result with validation data
            image_path: Path to the image file to modify
            
        Returns:
            True if metadata was successfully embedded, False otherwise
        """
        if not PIL_AVAILABLE:
            self.logger.error("Cannot embed metadata: PIL not available")
            return False
        
        try:
            # Load image
            with Image.open(image_path) as img:
                # Get existing EXIF data
                exif_dict = self._get_existing_exif(img)
                
                # Add compliance metadata
                self._add_compliance_metadata(exif_dict, processing_result)
                
                # Convert back to bytes
                if PIEXIF_AVAILABLE:
                    exif_bytes = piexif.dump(exif_dict)
                    
                    # Save image with new EXIF data
                    img.save(image_path, exif=exif_bytes, quality=95, optimize=True)
                else:
                    # Fallback to PIL-only approach (more limited)
                    self._embed_with_pil_only(img, processing_result, image_path)
                
                self.logger.info(f"Compliance metadata embedded in {image_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to embed metadata in {image_path}: {str(e)}")
            return False
    
    def extract_compliance_metadata(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract compliance metadata from image EXIF data.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing compliance metadata or None if not found
        """
        if not PIL_AVAILABLE:
            self.logger.error("Cannot extract metadata: PIL not available")
            return None
        
        try:
            with Image.open(image_path) as img:
                exif_data = img.getexif()
                
                if not exif_data:
                    return None
                
                compliance_metadata = {}
                
                # Extract standard compliance fields
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    
                    # Look for our custom compliance tags
                    if isinstance(tag_name, str) and 'VeriDoc' in tag_name:
                        compliance_metadata[tag_name] = value
                
                # Extract from UserComment if available
                user_comment = exif_data.get(ExifTags.Base.UserComment.value)
                if user_comment:
                    try:
                        # Try to parse as JSON
                        if isinstance(user_comment, bytes):
                            user_comment = user_comment.decode('utf-8', errors='ignore')
                        
                        if user_comment.startswith('VeriDoc:'):
                            json_data = user_comment[8:]  # Remove 'VeriDoc:' prefix
                            compliance_data = json.loads(json_data)
                            compliance_metadata.update(compliance_data)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
                
                return compliance_metadata if compliance_metadata else None
                
        except Exception as e:
            self.logger.error(f"Failed to extract metadata from {image_path}: {str(e)}")
            return None
    
    def embed_batch_metadata(self, batch_results: List[Dict[str, Any]], 
                           export_directory: str) -> Dict[str, bool]:
        """
        Embed metadata in multiple images from batch processing.
        
        Args:
            batch_results: List of processing results
            export_directory: Directory containing processed images
            
        Returns:
            Dictionary mapping image paths to success status
        """
        results = {}
        
        for result in batch_results:
            image_path = result.get('image_path')
            if not image_path:
                continue
            
            # Look for processed image in export directory
            processed_path = self._find_processed_image(image_path, export_directory)
            if processed_path:
                success = self.embed_compliance_metadata(result, processed_path)
                results[processed_path] = success
            else:
                results[image_path] = False
                self.logger.warning(f"Processed image not found for {image_path}")
        
        return results
    
    def create_metadata_summary(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Create a human-readable summary of embedded metadata.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing formatted metadata summary
        """
        metadata = self.extract_compliance_metadata(image_path)
        if not metadata:
            return None
        
        try:
            summary = {
                'image_info': {
                    'file_name': Path(image_path).name,
                    'file_size': os.path.getsize(image_path),
                    'last_modified': datetime.fromtimestamp(
                        os.path.getmtime(image_path)
                    ).isoformat()
                },
                'compliance_summary': {},
                'validation_details': {},
                'processing_info': {}
            }
            
            # Parse compliance data
            if 'ComplianceScore' in metadata:
                summary['compliance_summary']['overall_score'] = metadata['ComplianceScore']
            
            if 'ValidationStatus' in metadata:
                summary['compliance_summary']['status'] = metadata['ValidationStatus']
            
            if 'ProcessingDate' in metadata:
                summary['processing_info']['processed_at'] = metadata['ProcessingDate']
            
            # Parse detailed validation results if available
            if 'ValidationResults' in metadata:
                try:
                    validation_data = json.loads(metadata['ValidationResults'])
                    summary['validation_details'] = validation_data
                except json.JSONDecodeError:
                    summary['validation_details'] = {'raw_data': metadata['ValidationResults']}
            
            # Parse quality metrics if available
            if 'QualityMetrics' in metadata:
                try:
                    quality_data = json.loads(metadata['QualityMetrics'])
                    summary['quality_metrics'] = quality_data
                except json.JSONDecodeError:
                    summary['quality_metrics'] = {'raw_data': metadata['QualityMetrics']}
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to create metadata summary: {str(e)}")
            return None
    
    def validate_metadata_integrity(self, image_path: str) -> Dict[str, Any]:
        """
        Validate the integrity and completeness of embedded metadata.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing validation results
        """
        validation_result = {
            'is_valid': False,
            'has_compliance_data': False,
            'metadata_complete': False,
            'issues': [],
            'metadata_fields': []
        }
        
        try:
            metadata = self.extract_compliance_metadata(image_path)
            
            if not metadata:
                validation_result['issues'].append("No compliance metadata found")
                return validation_result
            
            validation_result['has_compliance_data'] = True
            validation_result['metadata_fields'] = list(metadata.keys())
            
            # Check for required fields
            required_fields = ['ComplianceScore', 'ValidationStatus', 'ProcessingDate']
            missing_fields = [field for field in required_fields if field not in metadata]
            
            if missing_fields:
                validation_result['issues'].append(f"Missing required fields: {missing_fields}")
            else:
                validation_result['metadata_complete'] = True
            
            # Validate data formats
            if 'ComplianceScore' in metadata:
                try:
                    score = float(metadata['ComplianceScore'])
                    if not 0 <= score <= 100:
                        validation_result['issues'].append("Compliance score out of valid range (0-100)")
                except (ValueError, TypeError):
                    validation_result['issues'].append("Invalid compliance score format")
            
            if 'ValidationStatus' in metadata:
                if metadata['ValidationStatus'] not in ['PASS', 'FAIL']:
                    validation_result['issues'].append("Invalid validation status (must be PASS or FAIL)")
            
            # Check JSON fields
            json_fields = ['ValidationResults', 'QualityMetrics', 'ProcessingMetrics']
            for field in json_fields:
                if field in metadata:
                    try:
                        json.loads(metadata[field])
                    except json.JSONDecodeError:
                        validation_result['issues'].append(f"Invalid JSON format in {field}")
            
            validation_result['is_valid'] = len(validation_result['issues']) == 0
            
            return validation_result
            
        except Exception as e:
            validation_result['issues'].append(f"Validation error: {str(e)}")
            return validation_result
    
    def _get_existing_exif(self, img: Image.Image) -> Dict[str, Any]:
        """Get existing EXIF data from image."""
        if PIEXIF_AVAILABLE:
            try:
                exif_dict = piexif.load(img.info.get('exif', b''))
                return exif_dict
            except Exception:
                # Return empty EXIF structure
                return {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        else:
            # Fallback for PIL-only
            return {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    
    def _add_compliance_metadata(self, exif_dict: Dict[str, Any], 
                               processing_result: Dict[str, Any]) -> None:
        """Add compliance metadata to EXIF dictionary."""
        if not PIEXIF_AVAILABLE:
            return
        
        try:
            # Add basic compliance information to EXIF
            exif_dict["0th"][piexif.ImageIFD.Software] = "Veridoc Universal v2.0"
            exif_dict["0th"][piexif.ImageIFD.DateTime] = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            
            # Create comprehensive compliance data for UserComment
            compliance_data = {
                'compliance_score': processing_result.get('overall_compliance', 0),
                'validation_status': 'PASS' if processing_result.get('passes_requirements', False) else 'FAIL',
                'processing_date': datetime.now().isoformat(),
                'format_validated': processing_result.get('format_name', 'Unknown'),
                'confidence_score': processing_result.get('confidence_score', 0),
                'processing_time': processing_result.get('processing_time', 0)
            }
            
            # Add validation results summary
            validation_results = processing_result.get('validation_results', {})
            if validation_results:
                compliance_data['validation_summary'] = {
                    rule: {
                        'passes': result.get('passes', False),
                        'score': result.get('score', 0)
                    }
                    for rule, result in validation_results.items()
                    if isinstance(result, dict)
                }
            
            # Add quality metrics summary
            quality_metrics = processing_result.get('quality_metrics', {})
            if quality_metrics:
                compliance_data['quality_summary'] = {
                    'sharpness': quality_metrics.get('sharpness', 0),
                    'lighting': quality_metrics.get('lighting', 0),
                    'color_accuracy': quality_metrics.get('color_accuracy', 0),
                    'noise_level': quality_metrics.get('noise_level', 0)
                }
            
            # Add compliance issues summary
            issues = processing_result.get('compliance_issues', [])
            if issues:
                compliance_data['issues_summary'] = [
                    {
                        'category': issue.get('category', 'Unknown'),
                        'severity': issue.get('severity', 'Unknown'),
                        'description': issue.get('description', '')[:100]  # Truncate for EXIF
                    }
                    for issue in issues[:5]  # Limit to top 5 issues
                ]
            
            # Embed as JSON in UserComment
            json_data = json.dumps(compliance_data, separators=(',', ':'))
            user_comment = f"VeriDoc:{json_data}"
            
            # Encode for EXIF
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment.encode('utf-8')
            
            # Add processing metadata to ImageDescription
            description = f"ICAO Compliance: {compliance_data['compliance_score']:.1f}% - {compliance_data['validation_status']}"
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description
            
        except Exception as e:
            self.logger.error(f"Failed to add compliance metadata to EXIF: {str(e)}")
    
    def _embed_with_pil_only(self, img: Image.Image, processing_result: Dict[str, Any], 
                           image_path: str) -> None:
        """Fallback method using PIL only (limited functionality)."""
        try:
            # Create basic metadata dictionary
            metadata = {
                'Software': 'Veridoc Universal v2.0',
                'DateTime': datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
                'ImageDescription': f"ICAO Compliance: {processing_result.get('overall_compliance', 0):.1f}%"
            }
            
            # Save with basic metadata
            img.save(image_path, quality=95, optimize=True)
            
            self.logger.warning("Limited metadata embedding (PIL only)")
            
        except Exception as e:
            self.logger.error(f"PIL-only metadata embedding failed: {str(e)}")
    
    def _find_processed_image(self, original_path: str, export_directory: str) -> Optional[str]:
        """Find processed image in export directory."""
        base_name = Path(original_path).stem
        
        # Common processed image patterns
        patterns = [
            f"{base_name}_processed.jpg",
            f"{base_name}_compliant.jpg",
            f"{base_name}.jpg",
            f"{base_name}_annotated.jpg"
        ]
        
        for pattern in patterns:
            processed_path = os.path.join(export_directory, pattern)
            if os.path.exists(processed_path):
                return processed_path
        
        return None