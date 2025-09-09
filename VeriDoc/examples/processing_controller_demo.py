#!/usr/bin/env python3
"""
Processing Controller Demo

Demonstrates the unified Processing Controller functionality including:
- Single image processing
- Progress tracking
- Batch processing
- Error handling
- Performance metrics
"""

import sys
import time
import tempfile
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.processing_controller import ProcessingController, ProcessingOptions
from core.config_manager import ConfigManager


def create_sample_images(temp_dir: Path, count: int = 3):
    """Create sample test images"""
    image_paths = []
    
    for i in range(count):
        # Create a simple test image with face-like pattern
        image = np.zeros((600, 600, 3), dtype=np.uint8)
        
        # Add background
        image[:, :] = (240, 240, 240)  # Light gray background
        
        # Add a simple face-like pattern
        cv2.rectangle(image, (200, 150), (400, 350), (255, 220, 180), -1)  # Face
        cv2.circle(image, (250, 200), 15, (50, 50, 50), -1)  # Left eye
        cv2.circle(image, (350, 200), 15, (50, 50, 50), -1)  # Right eye
        cv2.rectangle(image, (280, 280), (320, 300), (100, 50, 50), -1)  # Mouth
        
        # Add some variation
        if i == 1:
            # Add glasses
            cv2.rectangle(image, (230, 180), (270, 220), (0, 0, 0), 2)
            cv2.rectangle(image, (330, 180), (370, 220), (0, 0, 0), 2)
            cv2.line(image, (270, 200), (330, 200), (0, 0, 0), 2)
        elif i == 2:
            # Make it slightly blurry
            image = cv2.GaussianBlur(image, (5, 5), 0)
        
        image_path = temp_dir / f"sample_image_{i+1}.jpg"
        cv2.imwrite(str(image_path), image)
        image_paths.append(str(image_path))
        print(f"Created sample image: {image_path}")
    
    return image_paths


def setup_mock_controller():
    """Set up a Processing Controller with mocked dependencies for demo"""
    
    # Mock configuration manager
    config_manager = Mock(spec=ConfigManager)
    config_manager.get_processing_options.return_value = ProcessingOptions(
        enable_auto_fix=True,
        quality_threshold=0.7,
        debug_mode=True
    )
    config_manager.get_model_config.return_value = Mock(model_cache_dir="models")
    config_manager.get_formats_config.return_value = {
        'formats': {
            'DEMO_FORMAT': {
                'name': 'Demo Format',
                'dimensions': {'width': 600, 'height': 600},
                'dpi': 300,
                'background_color': 'white',
                'face_height_ratio': [0.70, 0.80],
                'quality_requirements': {
                    'min_sharpness': 100,
                    'max_noise': 0.1
                }
            }
        }
    }
    config_manager.config_dir = Path("config")
    config_manager.shutdown = Mock()
    
    # Set up mocked controller
    with patch('core.processing_controller.ModelManager'), \
         patch('core.processing_controller.CacheManager') as mock_cache, \
         patch('ai.ai_engine.AIEngine') as mock_ai, \
         patch('rules.icao_rules_engine.ICAORulesEngine') as mock_rules:
        
        # Mock Cache Manager
        mock_cache_instance = Mock()
        mock_cache_instance.get_statistics.return_value = {
            'total_requests': 10,
            'hits': 8
        }
        mock_cache.return_value = mock_cache_instance
        
        # Mock AI Engine with realistic responses
        mock_ai_instance = Mock()
        
        class MockFace:
            def __init__(self, bbox, confidence):
                self.bbox = bbox
                self.confidence = confidence
        
        def mock_detect_faces(image):
            # Simulate different detection results
            if image.shape[0] > 500:  # Large image
                return [MockFace((200, 150, 200, 200), 0.95)]
            else:
                return [MockFace((100, 75, 100, 100), 0.85)]
        
        mock_ai_instance.detect_faces.side_effect = mock_detect_faces
        mock_ai_instance.analyze_face_landmarks.return_value = Mock()
        mock_ai_instance.extract_face_features.return_value = Mock(
            glasses_detected=False,
            head_covering_detected=False
        )
        mock_ai_instance.segment_background.return_value = Mock(
            uniformity_score=0.9
        )
        mock_ai_instance.assess_image_quality.return_value = Mock(
            overall_score=0.8
        )
        mock_ai_instance.enhance_image_for_detection.return_value = np.zeros((600, 600, 3))
        mock_ai.return_value = mock_ai_instance
        
        # Mock Rules Engine
        mock_rules_instance = Mock()
        mock_rules_instance.get_all_rules.return_value = [
            Mock(rule_id="DEMO.1.1", name="face_detection", severity=Mock(value="critical")),
            Mock(rule_id="DEMO.2.1", name="background_uniformity", severity=Mock(value="major")),
            Mock(rule_id="DEMO.3.1", name="image_quality", severity=Mock(value="major")),
        ]
        mock_rules.return_value = mock_rules_instance
        
        controller = ProcessingController(config_manager)
        return controller


def demo_progress_tracking(controller, image_path):
    """Demonstrate progress tracking functionality"""
    print("\n" + "="*60)
    print("DEMO: Progress Tracking")
    print("="*60)
    
    progress_updates = []
    
    def progress_callback(session_id, progress):
        progress_updates.append({
            'session_id': session_id,
            'stage': progress.stage.value,
            'progress': progress.progress_percent,
            'step': progress.current_step,
            'status': progress.status.value
        })
        print(f"Progress: {progress.stage.value} - {progress.progress_percent:.1f}% - {progress.current_step}")
    
    controller.add_progress_callback(progress_callback)
    
    print(f"Processing image with progress tracking: {Path(image_path).name}")
    result = controller.process_image(image_path, "DEMO_FORMAT")
    
    controller.remove_progress_callback(progress_callback)
    
    print(f"\nProcessing completed: {'SUCCESS' if result.success else 'FAILED'}")
    print(f"Total progress updates received: {len(progress_updates)}")
    
    if result.validation_result:
        print(f"Compliance score: {result.validation_result.overall_compliance:.1f}%")
        print(f"Passes requirements: {result.validation_result.passes_requirements}")
    
    return result


def demo_single_image_processing(controller, image_path):
    """Demonstrate single image processing"""
    print("\n" + "="*60)
    print("DEMO: Single Image Processing")
    print("="*60)
    
    print(f"Processing image: {Path(image_path).name}")
    
    start_time = time.time()
    result = controller.process_image(image_path, "DEMO_FORMAT")
    processing_time = time.time() - start_time
    
    print(f"Processing completed in {processing_time:.3f} seconds")
    print(f"Result: {'SUCCESS' if result.success else 'FAILED'}")
    
    if result.success:
        print(f"Original image shape: {result.original_image.shape}")
        
        if result.validation_result:
            val = result.validation_result
            print(f"Validation Results:")
            print(f"  - Overall compliance: {val.overall_compliance:.1f}%")
            print(f"  - Passes requirements: {val.passes_requirements}")
            print(f"  - Confidence score: {val.confidence_score:.1f}%")
            print(f"  - Rule results: {len(val.rule_results)}")
            print(f"  - Issues found: {len(val.issue_summary)}")
        
        if result.auto_fix_result:
            auto_fix = result.auto_fix_result
            print(f"Auto-fix Results:")
            print(f"  - Success: {auto_fix.success}")
            print(f"  - Applied fixes: {len(auto_fix.applied_fixes)}")
            print(f"  - Quality change: {auto_fix.quality_change:.3f}")
    else:
        print(f"Error: {result.error_message}")
    
    # Show processing metrics
    metrics = result.processing_metrics
    print(f"Performance Metrics:")
    print(f"  - Total time: {metrics.total_processing_time:.3f}s")
    print(f"  - Memory usage: {metrics.memory_usage_mb:.1f} MB")
    print(f"  - Peak memory: {metrics.peak_memory_mb:.1f} MB")
    print(f"  - Cache hit rate: {metrics.cache_hit_rate:.1%}")
    
    return result


def demo_batch_processing(controller, image_paths):
    """Demonstrate batch processing"""
    print("\n" + "="*60)
    print("DEMO: Batch Processing")
    print("="*60)
    
    print(f"Processing {len(image_paths)} images in batch...")
    
    start_time = time.time()
    batch_result = controller.batch_process(image_paths, "DEMO_FORMAT")
    processing_time = time.time() - start_time
    
    print(f"Batch processing completed in {processing_time:.3f} seconds")
    print(f"Results:")
    print(f"  - Total images: {batch_result.total_images}")
    print(f"  - Successful: {batch_result.successful_images}")
    print(f"  - Failed: {batch_result.failed_images}")
    print(f"  - Average time per image: {batch_result.average_processing_time:.3f}s")
    
    if batch_result.error_summary:
        print(f"Error Summary:")
        for error_type, count in batch_result.error_summary.items():
            print(f"  - {error_type}: {count} occurrences")
    
    # Show individual results
    print(f"\nIndividual Results:")
    for i, result in enumerate(batch_result.results):
        image_name = Path(result.image_path).name
        status = "SUCCESS" if result.success else "FAILED"
        compliance = "N/A"
        if result.validation_result:
            compliance = f"{result.validation_result.overall_compliance:.1f}%"
        print(f"  {i+1}. {image_name}: {status} (Compliance: {compliance})")
    
    return batch_result


def demo_performance_metrics(controller):
    """Demonstrate performance metrics collection"""
    print("\n" + "="*60)
    print("DEMO: Performance Metrics")
    print("="*60)
    
    metrics = controller.get_processing_metrics()
    
    print(f"Overall Performance Metrics:")
    print(f"  - Total processed: {metrics['total_processed']}")
    print(f"  - Average processing time: {metrics['average_processing_time']:.3f}s")
    print(f"  - Average memory usage: {metrics['average_memory_usage']:.1f} MB")
    print(f"  - Peak memory usage: {metrics['peak_memory_usage']:.1f} MB")
    print(f"  - Error rate: {metrics['error_rate']:.1%}")
    print(f"  - Cache hit rate: {metrics['cache_hit_rate']:.1%}")
    print(f"  - Current memory: {metrics['current_memory_mb']:.1f} MB")
    print(f"  - Current CPU: {metrics['current_cpu_percent']:.1f}%")
    
    if 'stage_metrics' in metrics:
        print(f"\nStage-specific Metrics:")
        for stage, stage_metrics in metrics['stage_metrics'].items():
            if stage_metrics['average_time'] > 0:
                print(f"  - {stage}:")
                print(f"    * Average: {stage_metrics['average_time']:.4f}s")
                print(f"    * Min: {stage_metrics['min_time']:.4f}s")
                print(f"    * Max: {stage_metrics['max_time']:.4f}s")


def demo_error_handling(controller, temp_dir):
    """Demonstrate error handling capabilities"""
    print("\n" + "="*60)
    print("DEMO: Error Handling")
    print("="*60)
    
    # Test with non-existent file
    print("1. Testing with non-existent file...")
    result = controller.process_image("nonexistent_file.jpg", "DEMO_FORMAT")
    print(f"   Result: {'SUCCESS' if result.success else 'FAILED'}")
    if not result.success:
        print(f"   Error: {result.error_message}")
    
    # Test with invalid format
    print("\n2. Testing with invalid format...")
    # Create a valid image first
    image = np.zeros((300, 300, 3), dtype=np.uint8)
    test_image_path = temp_dir / "error_test.jpg"
    cv2.imwrite(str(test_image_path), image)
    
    result = controller.process_image(str(test_image_path), "INVALID_FORMAT")
    print(f"   Result: {'SUCCESS' if result.success else 'FAILED'}")
    if result.validation_result and result.validation_result.issue_summary:
        print(f"   Issues found: {len(result.validation_result.issue_summary)}")
        for issue in result.validation_result.issue_summary[:2]:  # Show first 2 issues
            print(f"   - {issue.get('description', 'Unknown issue')}")


def main():
    """Main demo function"""
    print("Processing Controller Demo")
    print("=" * 60)
    print("This demo showcases the unified Processing Controller functionality")
    print("including single image processing, batch processing, progress tracking,")
    print("performance metrics, and error handling.")
    
    # Create temporary directory and sample images
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"\nCreating sample images in: {temp_path}")
        
        image_paths = create_sample_images(temp_path, count=3)
        
        # Set up controller with mocked dependencies
        print("\nInitializing Processing Controller...")
        controller = setup_mock_controller()
        
        try:
            # Demo 1: Single image processing
            demo_single_image_processing(controller, image_paths[0])
            
            # Demo 2: Progress tracking
            demo_progress_tracking(controller, image_paths[1])
            
            # Demo 3: Batch processing
            demo_batch_processing(controller, image_paths)
            
            # Demo 4: Performance metrics
            demo_performance_metrics(controller)
            
            # Demo 5: Error handling
            demo_error_handling(controller, temp_path)
            
        finally:
            # Clean up
            print("\n" + "="*60)
            print("Shutting down Processing Controller...")
            controller.shutdown()
            print("Demo completed successfully!")


if __name__ == "__main__":
    main()