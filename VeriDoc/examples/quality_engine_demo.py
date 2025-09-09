#!/usr/bin/env python3
"""
Quality Engine Demo

This script demonstrates the comprehensive quality assessment capabilities
of the Advanced Quality Engine including sharpness, lighting, color accuracy,
noise, and resolution analysis.
"""

import numpy as np
import cv2
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quality.quality_engine import QualityEngine


def create_test_images():
    """Create various test images to demonstrate quality assessment."""
    
    # 1. Sharp, high-quality image
    sharp_image = np.zeros((600, 800, 3), dtype=np.uint8)
    sharp_image[:] = (128, 128, 128)  # Gray background
    
    # Add sharp geometric shapes
    cv2.rectangle(sharp_image, (100, 100), (300, 300), (255, 255, 255), -1)
    cv2.circle(sharp_image, (500, 200), 80, (0, 0, 255), -1)
    cv2.line(sharp_image, (100, 400), (700, 400), (0, 255, 0), 5)
    
    # Add text
    cv2.putText(sharp_image, 'HIGH QUALITY', (200, 500), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    # 2. Blurry image
    blurry_image = cv2.GaussianBlur(sharp_image, (21, 21), 8.0)
    
    # 3. Noisy image
    noise = np.random.normal(0, 30, sharp_image.shape).astype(np.int16)
    noisy_image = np.clip(sharp_image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # 4. Low resolution image
    low_res_temp = cv2.resize(sharp_image, (200, 150))
    low_res_image = cv2.resize(low_res_temp, (600, 800), interpolation=cv2.INTER_NEAREST)
    
    # 5. Poor lighting image (too dark)
    dark_image = (sharp_image * 0.3).astype(np.uint8)
    
    # 6. Color cast image (warm cast)
    color_cast_image = sharp_image.copy()
    color_cast_image[:, :, 0] = np.clip(color_cast_image[:, :, 0] * 0.8, 0, 255)  # Reduce blue
    color_cast_image[:, :, 2] = np.clip(color_cast_image[:, :, 2] * 1.3, 0, 255)  # Increase red
    
    return {
        'high_quality': sharp_image,
        'blurry': blurry_image,
        'noisy': noisy_image,
        'low_resolution': low_res_image,
        'poor_lighting': dark_image,
        'color_cast': color_cast_image
    }


def analyze_image_quality(engine, image, image_name):
    """Analyze and display quality metrics for an image."""
    print(f"\n{'='*60}")
    print(f"QUALITY ANALYSIS: {image_name.upper()}")
    print(f"{'='*60}")
    
    # Perform quality assessment
    result = engine.assess_image_quality(image)
    
    # Display overall results
    print(f"Overall Quality Score: {result.overall_score:.2f}/100")
    print(f"Quality Grade: {engine._score_to_grade(result.overall_score).upper()}")
    
    # Display individual component scores
    print(f"\nComponent Scores:")
    print(f"  • Sharpness:   {result.sharpness_score:.2f}/100")
    print(f"  • Lighting:    {result.lighting_score:.2f}/100")
    print(f"  • Color:       {result.color_score:.2f}/100")
    print(f"  • Noise:       {result.noise_score:.2f}/100")
    print(f"  • Resolution:  {result.resolution_score:.2f}/100")
    
    # Display issues detected
    if result.issues:
        print(f"\nIssues Detected ({len(result.issues)}):")
        for i, issue in enumerate(result.issues, 1):
            print(f"  {i}. {issue}")
    else:
        print(f"\nNo significant issues detected!")
    
    # Display suggestions
    if result.suggestions:
        print(f"\nRecommendations ({len(result.suggestions)}):")
        for i, suggestion in enumerate(result.suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    # Display detailed metrics for high-quality image
    if image_name == 'high_quality':
        print(f"\nDetailed Analysis:")
        
        # Sharpness details
        sharpness_details = result.detailed_metrics['sharpness']
        print(f"  Sharpness Algorithms:")
        for method, score in sharpness_details['normalized_scores'].items():
            print(f"    - {method.capitalize()}: {score:.2f}")
        
        # Lighting details
        lighting_details = result.detailed_metrics['lighting']
        brightness = lighting_details['brightness_metrics']['mean_brightness']
        print(f"  Lighting Analysis:")
        print(f"    - Mean Brightness: {brightness:.1f}")
        print(f"    - Lighting Quality: {lighting_details['lighting_quality']}")
        
        # Color details
        color_details = result.detailed_metrics['color']
        print(f"  Color Analysis:")
        print(f"    - Color Quality: {color_details['color_quality']}")
        if color_details['white_balance_metrics']['is_balanced']:
            print(f"    - White Balance: Good")
        else:
            print(f"    - White Balance: Needs adjustment")
        
        # Noise details
        noise_details = result.detailed_metrics['noise']
        print(f"  Noise Analysis:")
        print(f"    - Noise Quality: {noise_details['noise_quality']}")
        print(f"    - SNR: {noise_details['snr_metrics']['snr_simple']:.1f} dB")
        
        # Resolution details
        resolution_details = result.detailed_metrics['resolution']
        pixel_metrics = resolution_details['pixel_metrics']
        print(f"  Resolution Analysis:")
        print(f"    - Dimensions: {pixel_metrics['width']}x{pixel_metrics['height']}")
        print(f"    - Megapixels: {pixel_metrics['megapixels']:.2f}")
        print(f"    - Resolution Quality: {resolution_details['resolution_quality']}")


def demonstrate_quality_comparison(engine, images):
    """Demonstrate quality comparison between different image types."""
    print(f"\n{'='*80}")
    print(f"QUALITY COMPARISON SUMMARY")
    print(f"{'='*80}")
    
    results = {}
    for name, image in images.items():
        result = engine.assess_image_quality(image)
        results[name] = result.overall_score
    
    # Sort by quality score
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    
    print(f"{'Rank':<6} {'Image Type':<20} {'Quality Score':<15} {'Grade'}")
    print(f"{'-'*60}")
    
    for rank, (name, score) in enumerate(sorted_results, 1):
        grade = engine._score_to_grade(score).upper()
        print(f"{rank:<6} {name.replace('_', ' ').title():<20} {score:<15.2f} {grade}")
    
    # Generate overall quality score for multiple assessments
    all_metrics = []
    for name, image in images.items():
        result = engine.assess_image_quality(image)
        all_metrics.append(result)
    
    overall_quality = engine.generate_quality_score(all_metrics)
    
    print(f"\nBatch Analysis Summary:")
    print(f"  • Average Quality Score: {overall_quality.score:.2f}/100")
    print(f"  • Overall Grade: {overall_quality.grade.upper()}")
    print(f"  • Confidence: {overall_quality.confidence:.2f}")
    print(f"  • Passes Threshold: {'Yes' if overall_quality.passes_threshold else 'No'}")


def main():
    """Main demo function."""
    print("Advanced Quality Engine Demo")
    print("=" * 50)
    print("This demo showcases comprehensive image quality assessment")
    print("including sharpness, lighting, color, noise, and resolution analysis.")
    
    # Initialize Quality Engine
    print("\nInitializing Quality Engine...")
    engine = QualityEngine()
    print("✓ Quality Engine initialized successfully!")
    
    # Create test images
    print("\nCreating test images...")
    images = create_test_images()
    print(f"✓ Created {len(images)} test images")
    
    # Analyze each image
    for name, image in images.items():
        analyze_image_quality(engine, image, name)
    
    # Demonstrate quality comparison
    demonstrate_quality_comparison(engine, images)
    
    print(f"\n{'='*80}")
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("The Quality Engine provides comprehensive analysis of:")
    print("• Sharpness using multiple algorithms (Laplacian, Sobel, FFT, etc.)")
    print("• Lighting analysis with shadow and highlight detection")
    print("• Color accuracy assessment with skin tone validation")
    print("• Noise measurement and compression artifact detection")
    print("• Resolution validation and print quality assessment")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()