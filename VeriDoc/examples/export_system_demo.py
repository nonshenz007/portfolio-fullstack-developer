"""
Demonstration of the comprehensive Export and Reporting system.
Shows how to use all export features including PDF/JSON reports, 
visual annotations, metadata embedding, and batch analysis.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export.export_engine import ExportEngine, ExportOptions
from export.report_generator import ReportGenerator
from export.audit_logger import AuditLogger
from export.metadata_embedder import MetadataEmbedder
from export.visual_annotator import VisualAnnotator
from export.batch_analyzer import BatchAnalyzer

import numpy as np
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV not available - some features will be limited")


def create_sample_image(path: str, size: tuple = (400, 300)) -> None:
    """Create a sample image for testing."""
    if CV2_AVAILABLE:
        # Create a simple test image with a face-like pattern
        image = np.ones((size[1], size[0], 3), dtype=np.uint8) * 240
        
        # Add a simple face-like pattern
        center_x, center_y = size[0] // 2, size[1] // 2
        
        # Face outline
        cv2.ellipse(image, (center_x, center_y), (80, 100), 0, 0, 360, (200, 200, 200), -1)
        
        # Eyes
        cv2.circle(image, (center_x - 25, center_y - 20), 8, (100, 100, 100), -1)
        cv2.circle(image, (center_x + 25, center_y - 20), 8, (100, 100, 100), -1)
        
        # Mouth
        cv2.ellipse(image, (center_x, center_y + 20), (15, 8), 0, 0, 180, (100, 100, 100), 2)
        
        cv2.imwrite(path, image)
    else:
        # Fallback: create a minimal file
        with open(path, 'wb') as f:
            f.write(b'fake_image_data')


def create_mock_processing_result(image_path: str, compliance_score: float = 85.5) -> dict:
    """Create a mock processing result for demonstration."""
    return {
        'success': True,
        'image_path': image_path,
        'overall_compliance': compliance_score,
        'passes_requirements': compliance_score >= 70,
        'confidence_score': min(95.0, compliance_score + 10),
        'processing_time': np.random.uniform(1.5, 4.0),
        'format_name': 'ICAO',
        'face_detection': {
            'bbox': {'x': 160, 'y': 100, 'width': 80, 'height': 100},
            'confidence': 0.95
        },
        'face_landmarks': {
            'eye_positions': [(185, 120), (215, 120)],
            'mouth_position': (200, 140)
        },
        'validation_results': {
            'face_detection': {
                'passes': True,
                'score': 95.0,
                'details': 'Face detected successfully with high confidence'
            },
            'glasses_compliance': {
                'passes': compliance_score >= 80,
                'score': max(60, compliance_score - 5),
                'details': 'No tinted glasses detected' if compliance_score >= 80 else 'Potential glare detected'
            },
            'background_compliance': {
                'passes': compliance_score >= 75,
                'score': max(50, compliance_score - 10),
                'details': 'Background uniformity acceptable' if compliance_score >= 75 else 'Background not uniform'
            },
            'expression_compliance': {
                'passes': compliance_score >= 85,
                'score': max(70, compliance_score),
                'details': 'Neutral expression detected' if compliance_score >= 85 else 'Expression needs improvement'
            },
            'photo_quality': {
                'passes': compliance_score >= 80,
                'score': max(65, compliance_score - 3),
                'details': 'Image quality meets standards' if compliance_score >= 80 else 'Quality could be improved'
            }
        },
        'quality_metrics': {
            'sharpness': max(60, compliance_score - 5),
            'lighting': max(55, compliance_score - 10),
            'color_accuracy': max(70, compliance_score + 5),
            'noise_level': max(5, 25 - (compliance_score - 60) / 2)
        },
        'compliance_issues': [
            {
                'category': 'background_compliance',
                'severity': 'minor' if compliance_score >= 75 else 'major',
                'description': 'Background uniformity could be improved',
                'fix_suggestion': 'Use plain white background',
                'auto_fixable': True,
                'regulation_reference': 'ICAO Doc 9303 Part 6 Section 1.1'
            },
            {
                'category': 'lighting_compliance',
                'severity': 'minor',
                'description': 'Slight shadow detected on left side',
                'fix_suggestion': 'Improve lighting setup',
                'auto_fixable': True,
                'regulation_reference': 'ICAO Doc 9303 Part 6 Section 2.1'
            }
        ] if compliance_score < 90 else [],
        'recommendations': [
            'Improve background uniformity for better compliance',
            'Ensure even lighting to minimize shadows',
            'Consider using professional photo setup'
        ] if compliance_score < 90 else [
            'Excellent compliance - no improvements needed'
        ],
        'processing_metrics': {
            'total_time': np.random.uniform(1.5, 4.0),
            'models_used': ['YOLOv8', 'MediaPipe', 'BackgroundSegmenter'],
            'image_width': 400,
            'image_height': 300,
            'face_confidence': 0.95
        }
    }


def demo_single_image_export():
    """Demonstrate single image export with all features."""
    print("\n" + "="*60)
    print("SINGLE IMAGE EXPORT DEMONSTRATION")
    print("="*60)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Working directory: {temp_dir}")
    
    try:
        # Create sample image
        image_path = os.path.join(temp_dir, 'sample_photo.jpg')
        create_sample_image(image_path)
        print(f"Created sample image: {image_path}")
        
        # Create mock processing result
        processing_result = create_mock_processing_result(image_path, compliance_score=87.5)
        print(f"Mock processing result created - Compliance: {processing_result['overall_compliance']:.1f}%")
        
        # Initialize export engine
        export_engine = ExportEngine()
        
        # Configure export options
        export_options = ExportOptions(
            include_pdf_report=True,
            include_json_report=True,
            embed_metadata=True,
            create_visual_annotations=True,
            include_audit_trail=True,
            export_directory=temp_dir,
            annotation_style="comprehensive"
        )
        
        print("\nExporting with comprehensive options...")
        
        # Perform export
        export_result = export_engine.export_single_result(
            processing_result,
            image_path,
            export_options
        )
        
        # Display results
        if export_result.success:
            print(f"✅ Export successful!")
            print(f"   Export directory: {export_result.export_path}")
            print(f"   Generated files: {len(export_result.generated_files)}")
            print(f"   Processing time: {export_result.processing_time:.2f}s")
            
            for file_path in export_result.generated_files:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                print(f"   - {file_name} ({file_size} bytes)")
            
            # Demonstrate individual components
            print("\n" + "-"*40)
            print("COMPONENT DEMONSTRATIONS")
            print("-"*40)
            
            # JSON Report content
            if export_result.json_report_path and os.path.exists(export_result.json_report_path):
                print("\n📄 JSON Report Sample:")
                with open(export_result.json_report_path, 'r') as f:
                    import json
                    report_data = json.load(f)
                    print(f"   Overall Compliance: {report_data['processing_summary']['overall_compliance']:.1f}%")
                    print(f"   Validation Status: {'PASS' if report_data['processing_summary']['passes_requirements'] else 'FAIL'}")
                    print(f"   Issues Found: {len(report_data.get('compliance_issues', []))}")
            
            # Metadata demonstration
            print("\n🏷️  Metadata Embedding:")
            metadata_embedder = MetadataEmbedder()
            if export_result.annotated_image_path:
                metadata_summary = metadata_embedder.create_metadata_summary(export_result.annotated_image_path)
                if metadata_summary:
                    print("   ✅ Metadata successfully embedded")
                    print(f"   File size: {metadata_summary['image_info']['file_size']} bytes")
                else:
                    print("   ⚠️  Metadata embedding limited (PIL/piexif not available)")
            
            # Audit trail
            print("\n📋 Audit Trail:")
            audit_logger = export_engine.audit_logger
            audit_trail = audit_logger.get_audit_trail(image_path=image_path)
            print(f"   Events logged: {len(audit_trail)}")
            for event in audit_trail[-3:]:  # Show last 3 events
                print(f"   - {event['event_type']}: {event['timestamp']}")
        
        else:
            print(f"❌ Export failed: {export_result.error_message}")
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up temporary directory: {temp_dir}")


def demo_batch_processing_export():
    """Demonstrate batch processing export and analysis."""
    print("\n" + "="*60)
    print("BATCH PROCESSING EXPORT DEMONSTRATION")
    print("="*60)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Working directory: {temp_dir}")
    
    try:
        # Create multiple sample images with varying compliance scores
        batch_results = []
        compliance_scores = [92.5, 78.3, 65.1, 88.7, 45.2, 91.8, 72.4, 83.9]
        
        print("Creating sample batch images...")
        for i, score in enumerate(compliance_scores):
            image_path = os.path.join(temp_dir, f'batch_image_{i+1}.jpg')
            create_sample_image(image_path, size=(300 + i*10, 250 + i*5))
            
            processing_result = create_mock_processing_result(image_path, compliance_score=score)
            batch_results.append(processing_result)
            
            print(f"   Image {i+1}: {score:.1f}% compliance")
        
        # Initialize export engine
        export_engine = ExportEngine()
        
        # Configure batch export options
        export_options = ExportOptions(
            include_pdf_report=True,
            include_json_report=True,
            embed_metadata=False,  # Skip for batch demo
            create_visual_annotations=True,
            include_audit_trail=True,
            export_directory=temp_dir,
            annotation_style="detailed"
        )
        
        print(f"\nProcessing batch of {len(batch_results)} images...")
        
        # Perform batch export
        batch_export_result = export_engine.export_batch_results(
            batch_results,
            export_options
        )
        
        # Display batch results
        if batch_export_result.success:
            print(f"✅ Batch export successful!")
            print(f"   Export directory: {batch_export_result.export_path}")
            print(f"   Generated files: {len(batch_export_result.generated_files)}")
            print(f"   Processing time: {batch_export_result.processing_time:.2f}s")
            
            # Demonstrate batch analysis
            print("\n" + "-"*40)
            print("BATCH ANALYSIS RESULTS")
            print("-"*40)
            
            # Load and display batch analysis
            if batch_export_result.json_report_path and os.path.exists(batch_export_result.json_report_path):
                with open(batch_export_result.json_report_path, 'r') as f:
                    import json
                    batch_report = json.load(f)
                    
                    # Summary statistics
                    summary = batch_report.get('summary_statistics', {})
                    print(f"\n📊 Summary Statistics:")
                    print(f"   Total Images: {summary.get('total_images', 0)}")
                    print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
                    print(f"   Pass Rate: {summary.get('pass_rate', 0):.1f}%")
                    print(f"   Average Compliance: {summary.get('avg_compliance_score', 0):.1f}%")
                    print(f"   Processing Time: {summary.get('total_processing_time', 0):.2f}s")
                    
                    # Compliance breakdown
                    breakdown = batch_report.get('compliance_breakdown', {})
                    print(f"\n📈 Compliance Breakdown:")
                    for level, count in breakdown.items():
                        level_name = level.replace('_', ' ').title()
                        print(f"   {level_name}: {count} images")
                    
                    # Common issues
                    failure_analysis = batch_report.get('failure_analysis', {})
                    common_issues = failure_analysis.get('common_issues', [])
                    if common_issues:
                        print(f"\n⚠️  Common Issues:")
                        for issue in common_issues[:3]:  # Top 3 issues
                            print(f"   - {issue['issue']} ({issue['count']} occurrences)")
                    
                    # Recommendations
                    recommendations = batch_report.get('recommendations', [])
                    if recommendations:
                        print(f"\n💡 Batch Recommendations:")
                        for rec in recommendations[:3]:  # Top 3 recommendations
                            print(f"   - {rec}")
            
            # Export statistics
            print("\n📈 Export Statistics:")
            export_stats = export_engine.get_export_statistics()
            print(f"   Total Exports: {export_stats.get('total_exports', 0)}")
            print(f"   Success Rate: {export_stats.get('export_success_rate', 0):.1f}%")
            print(f"   Average Processing Time: {export_stats.get('average_processing_time', 0):.2f}s")
        
        else:
            print(f"❌ Batch export failed: {batch_export_result.error_message}")
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up temporary directory: {temp_dir}")


def demo_individual_components():
    """Demonstrate individual export system components."""
    print("\n" + "="*60)
    print("INDIVIDUAL COMPONENTS DEMONSTRATION")
    print("="*60)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create sample data
        image_path = os.path.join(temp_dir, 'component_test.jpg')
        create_sample_image(image_path)
        processing_result = create_mock_processing_result(image_path, compliance_score=82.3)
        
        print("Testing individual components...")
        
        # 1. Report Generator
        print("\n1️⃣  Report Generator:")
        report_gen = ReportGenerator()
        
        json_report = report_gen.generate_json_report(
            processing_result, image_path, temp_dir
        )
        if json_report:
            print(f"   ✅ JSON report generated: {os.path.basename(json_report)}")
        else:
            print("   ❌ JSON report generation failed")
        
        # 2. Audit Logger
        print("\n2️⃣  Audit Logger:")
        audit_logger = AuditLogger(log_directory=temp_dir)
        
        event_id = audit_logger.log_processing_start(image_path, 'ICAO')
        audit_logger.log_processing_complete(image_path, event_id, processing_result)
        
        audit_trail = audit_logger.get_audit_trail(image_path=image_path)
        print(f"   ✅ Audit events logged: {len(audit_trail)}")
        
        # 3. Metadata Embedder
        print("\n3️⃣  Metadata Embedder:")
        metadata_embedder = MetadataEmbedder()
        
        # Create a copy for metadata testing
        metadata_test_path = os.path.join(temp_dir, 'metadata_test.jpg')
        shutil.copy2(image_path, metadata_test_path)
        
        embed_success = metadata_embedder.embed_compliance_metadata(
            processing_result, metadata_test_path
        )
        if embed_success:
            print("   ✅ Metadata embedded successfully")
            
            # Test metadata extraction
            extracted = metadata_embedder.extract_compliance_metadata(metadata_test_path)
            if extracted:
                print(f"   ✅ Metadata extracted: {len(extracted)} fields")
            else:
                print("   ⚠️  Metadata extraction limited")
        else:
            print("   ⚠️  Metadata embedding limited (dependencies not available)")
        
        # 4. Visual Annotator
        print("\n4️⃣  Visual Annotator:")
        visual_annotator = VisualAnnotator()
        
        if CV2_AVAILABLE:
            annotated_path = visual_annotator.create_annotated_image(
                processing_result, image_path, temp_dir, style='comprehensive'
            )
            if annotated_path:
                print(f"   ✅ Annotated image created: {os.path.basename(annotated_path)}")
            else:
                print("   ❌ Annotation creation failed")
        else:
            print("   ⚠️  Visual annotation requires OpenCV")
        
        # 5. Batch Analyzer
        print("\n5️⃣  Batch Analyzer:")
        batch_analyzer = BatchAnalyzer()
        
        # Create mini batch for testing
        mini_batch = [
            processing_result,
            create_mock_processing_result(image_path, 75.5),
            create_mock_processing_result(image_path, 91.2)
        ]
        
        batch_analysis = batch_analyzer.analyze_batch_results(mini_batch)
        print(f"   ✅ Batch analysis completed")
        print(f"   Total images analyzed: {batch_analysis['summary_statistics']['total_images']}")
        print(f"   Average compliance: {batch_analysis['summary_statistics']['avg_compliance_score']:.1f}%")
        print(f"   Recommendations generated: {len(batch_analysis['batch_recommendations'])}")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up temporary directory: {temp_dir}")


def demo_integration_with_external_systems():
    """Demonstrate integration capabilities with external systems."""
    print("\n" + "="*60)
    print("EXTERNAL SYSTEM INTEGRATION DEMONSTRATION")
    print("="*60)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Simulate integration scenarios
        print("Simulating external system integration scenarios...")
        
        # 1. Quality Management System Integration
        print("\n1️⃣  Quality Management System Integration:")
        
        # Create sample processing results
        image_path = os.path.join(temp_dir, 'qms_test.jpg')
        create_sample_image(image_path)
        processing_result = create_mock_processing_result(image_path, 88.7)
        
        # Export with QMS-compatible format
        export_engine = ExportEngine()
        export_options = ExportOptions(
            include_json_report=True,
            include_audit_trail=True,
            export_directory=temp_dir
        )
        
        export_result = export_engine.export_single_result(
            processing_result, image_path, export_options
        )
        
        if export_result.success and export_result.json_report_path:
            # Simulate QMS data extraction
            with open(export_result.json_report_path, 'r') as f:
                import json
                qms_data = json.load(f)
                
                # Extract QMS-relevant fields
                qms_record = {
                    'image_id': os.path.basename(image_path),
                    'compliance_score': qms_data['processing_summary']['overall_compliance'],
                    'validation_status': qms_data['processing_summary']['passes_requirements'],
                    'processing_timestamp': qms_data['report_metadata']['generated_at'],
                    'quality_metrics': qms_data['quality_metrics'],
                    'issues_count': len(qms_data.get('compliance_issues', [])),
                    'audit_trail_available': True
                }
                
                print("   ✅ QMS integration data prepared:")
                print(f"      Image ID: {qms_record['image_id']}")
                print(f"      Compliance: {qms_record['compliance_score']:.1f}%")
                print(f"      Status: {'PASS' if qms_record['validation_status'] else 'FAIL'}")
                print(f"      Issues: {qms_record['issues_count']}")
        
        # 2. Compliance Reporting System
        print("\n2️⃣  Compliance Reporting System:")
        
        # Create batch for compliance reporting
        batch_results = []
        for i in range(5):
            img_path = os.path.join(temp_dir, f'compliance_test_{i}.jpg')
            create_sample_image(img_path)
            result = create_mock_processing_result(img_path, 70 + i * 5)
            batch_results.append(result)
        
        # Generate compliance report
        batch_analyzer = BatchAnalyzer()
        compliance_analysis = batch_analyzer.analyze_batch_results(batch_results)
        
        # Extract compliance metrics for reporting
        compliance_report = {
            'report_period': datetime.now().strftime('%Y-%m-%d'),
            'total_processed': compliance_analysis['summary_statistics']['total_images'],
            'compliance_rate': compliance_analysis['summary_statistics']['pass_rate'],
            'average_score': compliance_analysis['summary_statistics']['avg_compliance_score'],
            'quality_trends': compliance_analysis['quality_trends'],
            'common_violations': [
                issue['issue'] for issue in 
                compliance_analysis['failure_analysis'].get('common_issues', [])[:3]
            ],
            'recommendations': compliance_analysis['batch_recommendations'][:3]
        }
        
        print("   ✅ Compliance report generated:")
        print(f"      Period: {compliance_report['report_period']}")
        print(f"      Images Processed: {compliance_report['total_processed']}")
        print(f"      Compliance Rate: {compliance_report['compliance_rate']:.1f}%")
        print(f"      Average Score: {compliance_report['average_score']:.1f}%")
        
        # 3. Document Management System
        print("\n3️⃣  Document Management System:")
        
        # Simulate DMS metadata requirements
        dms_metadata = {
            'document_type': 'passport_photo_compliance_report',
            'classification': 'official',
            'retention_period': '7_years',
            'access_level': 'restricted',
            'compliance_verified': True,
            'processing_system': 'veridoc_universal_v2',
            'quality_assurance': 'automated_validation'
        }
        
        # Add DMS metadata to export
        enhanced_processing_result = {
            **processing_result,
            'dms_metadata': dms_metadata
        }
        
        dms_export = export_engine.export_single_result(
            enhanced_processing_result, image_path, export_options
        )
        
        if dms_export.success:
            print("   ✅ DMS-compatible export created:")
            print(f"      Document Type: {dms_metadata['document_type']}")
            print(f"      Classification: {dms_metadata['classification']}")
            print(f"      Retention: {dms_metadata['retention_period']}")
        
        # 4. Performance Monitoring System
        print("\n4️⃣  Performance Monitoring System:")
        
        # Get export statistics for monitoring
        export_stats = export_engine.get_export_statistics()
        
        # Simulate performance metrics
        performance_metrics = {
            'system_uptime': '99.8%',
            'average_processing_time': export_stats.get('average_processing_time', 0),
            'throughput_per_hour': 3600 / max(1, export_stats.get('average_processing_time', 1)),
            'error_rate': 100 - export_stats.get('export_success_rate', 100),
            'compliance_accuracy': 'N/A - requires validation dataset',
            'resource_utilization': 'Normal'
        }
        
        print("   ✅ Performance metrics available:")
        print(f"      Avg Processing Time: {performance_metrics['average_processing_time']:.2f}s")
        print(f"      Estimated Throughput: {performance_metrics['throughput_per_hour']:.0f} images/hour")
        print(f"      Error Rate: {performance_metrics['error_rate']:.1f}%")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up temporary directory: {temp_dir}")


def main():
    """Run all export system demonstrations."""
    print("VERIDOC UNIVERSAL - EXPORT AND REPORTING SYSTEM DEMO")
    print("=" * 60)
    print("This demonstration shows the comprehensive export and reporting")
    print("capabilities of the Veridoc Universal system, including:")
    print("• PDF and JSON report generation")
    print("• Visual annotation and comparison images")
    print("• EXIF metadata embedding")
    print("• Comprehensive audit logging")
    print("• Batch processing analysis")
    print("• External system integration")
    
    try:
        # Run demonstrations
        demo_single_image_export()
        demo_batch_processing_export()
        demo_individual_components()
        demo_integration_with_external_systems()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print("All export and reporting features have been demonstrated.")
        print("The system is ready for production use with comprehensive")
        print("export capabilities, detailed reporting, and audit trails.")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()