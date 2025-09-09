"""
Format Rule Engine Demonstration

This script demonstrates the capabilities of the Format Rule Engine,
including format configuration, inheritance, auto-detection, validation,
and hot-reload functionality.
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import numpy as np

# Import our format rule engine components
from rules.format_rule_engine import FormatRuleEngine
from utils.format_detector import FormatDetector
from config.hot_reload_manager import HotReloadManager, setup_hot_reload


def create_demo_configurations(config_dir: Path):
    """Create demonstration format configurations."""
    print("Creating demonstration format configurations...")
    
    # Base ICAO format
    base_icao = {
        "format_id": "demo_base_icao",
        "display_name": "Demo Base ICAO Standard",
        "version": "2023.1",
        "authority": "ICAO",
        "regulation_references": [
            "ICAO Doc 9303 Machine Readable Travel Documents"
        ],
        "last_updated": "2023-01-01",
        
        "dimensions": {
            "width": 600,
            "height": 600,
            "unit": "pixels",
            "aspect_ratio": 1.0,
            "aspect_tolerance": 0.02,
            "tolerance": 0.05,
            "regulation_reference": "ICAO Doc 9303 Part 7 Section 1.1"
        },
        
        "face_requirements": {
            "height_ratio": [0.70, 0.80],
            "eye_height_ratio": [0.50, 0.60],
            "centering_tolerance": 0.05,
            "max_rotation_deg": 5.0,
            "regulation_reference": "ICAO Doc 9303 Part 4 Section 2.1"
        },
        
        "background": {
            "color": "white",
            "rgb_values": [255, 255, 255],
            "tolerance": 10,
            "uniformity_threshold": 0.9,
            "regulation_reference": "ICAO Doc 9303 Part 6 Section 1.1"
        },
        
        "quality_thresholds": {
            "min_brightness": 80,
            "max_brightness": 200,
            "min_sharpness": 100,
            "max_blur_variance": 50,
            "regulation_reference": "ICAO Doc 9303 Part 5"
        },
        
        "icao_rules": {
            "glasses": {
                "tinted_lenses_allowed": False,
                "max_frame_width_ratio": 0.15,
                "max_glare_intensity": 0.2
            },
            "expression": {
                "neutral_required": True,
                "mouth_closed_required": True,
                "direct_gaze_required": True
            }
        },
        
        "detection_criteria": {
            "min_resolution": 600,
            "max_file_size_mb": 10,
            "target_aspect_ratio": 1.0,
            "aspect_ratio_tolerance": 0.05
        },
        
        "validation_strictness": "standard",
        "auto_fix_enabled": True
    }
    
    # US Visa format (inherits from base)
    us_visa = {
        "format_id": "demo_us_visa",
        "display_name": "Demo US Visa Photo",
        "inherits_from": "demo_base_icao",
        "version": "2023.2",
        "country": "United States",
        "authority": "US Department of State",
        "regulation_references": [
            "ICAO Doc 9303 Machine Readable Travel Documents",
            "US Department of State Photo Requirements"
        ],
        "last_updated": "2023-06-01",
        
        # Override face requirements for stricter US standards
        "face_requirements": {
            "height_ratio": [0.69, 0.80],
            "eye_height_ratio": [0.56, 0.69]
        },
        
        # Stricter quality requirements
        "quality_thresholds": {
            "min_brightness": 60,
            "max_brightness": 190,
            "min_sharpness": 120,
            "max_blur_variance": 40
        },
        
        # Stricter ICAO rules
        "icao_rules": {
            "glasses": {
                "prescription_glasses_allowed": False,
                "max_glare_intensity": 0.15
            },
            "expression": {
                "smile_detection_max": 0.1
            }
        },
        
        "validation_strictness": "strict"
    }
    
    # ICS UAE format (inherits from base)
    ics_uae = {
        "format_id": "demo_ics_uae",
        "display_name": "Demo ICS (UAE)",
        "inherits_from": "demo_base_icao",
        "country": "United Arab Emirates",
        "authority": "ICS UAE",
        "regulation_references": [
            "ICAO Doc 9303 Machine Readable Travel Documents",
            "ICS UAE Photo Specifications"
        ],
        
        # Different dimensions for UAE format
        "dimensions": {
            "width": 413,
            "height": 531,
            "aspect_ratio": 0.7778,
            "aspect_tolerance": 0.020
        },
        
        # Different face requirements
        "face_requirements": {
            "height_ratio": [0.62, 0.69],
            "eye_height_ratio": [0.33, 0.36],
            "max_rotation_deg": 2.0
        },
        
        # Adjusted quality thresholds
        "quality_thresholds": {
            "min_brightness": 55,
            "max_brightness": 190,
            "min_sharpness": 120
        },
        
        # Different detection criteria
        "detection_criteria": {
            "min_resolution": 400,
            "target_aspect_ratio": 0.7778,
            "aspect_ratio_tolerance": 0.03
        }
    }
    
    # Write configuration files
    formats = {
        "demo_base_icao": base_icao,
        "demo_us_visa": us_visa,
        "demo_ics_uae": ics_uae
    }
    
    for format_id, config in formats.items():
        config_path = config_dir / f"{format_id}.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"  Created: {config_path}")


def create_demo_images(temp_dir: Path):
    """Create demonstration images for testing."""
    print("\nCreating demonstration images...")
    
    images = [
        {"name": "square_600x600.jpg", "size": (600, 600), "color": (200, 200, 200)},
        {"name": "portrait_413x531.jpg", "size": (413, 531), "color": (180, 180, 180)},
        {"name": "large_800x800.jpg", "size": (800, 800), "color": (220, 220, 220)},
        {"name": "us_visa_sample.jpg", "size": (600, 600), "color": (190, 190, 190)}
    ]
    
    for img_info in images:
        # Create a simple colored image
        img_array = np.full((*img_info["size"][::-1], 3), img_info["color"], dtype=np.uint8)
        img = Image.fromarray(img_array, 'RGB')
        
        img_path = temp_dir / img_info["name"]
        img.save(img_path, 'JPEG', quality=90)
        print(f"  Created: {img_path}")
    
    return [temp_dir / img["name"] for img in images]


def demonstrate_format_loading(engine: FormatRuleEngine):
    """Demonstrate format loading and inheritance."""
    print("\n" + "="*60)
    print("DEMONSTRATING FORMAT LOADING AND INHERITANCE")
    print("="*60)
    
    # Show available formats
    formats = engine.get_available_formats()
    print(f"\nAvailable formats: {formats}")
    
    # Show format display names
    display_names = engine.get_format_display_names()
    print(f"\nFormat display names:")
    for format_id, display_name in display_names.items():
        print(f"  {format_id}: {display_name}")
    
    # Demonstrate inheritance
    print(f"\nDemonstrating inheritance:")
    
    base_rule = engine.get_format_rule("demo_base_icao")
    us_visa_rule = engine.get_format_rule("demo_us_visa")
    
    if base_rule and us_visa_rule:
        print(f"\nBase ICAO dimensions: {base_rule.dimensions['width']}x{base_rule.dimensions['height']}")
        print(f"US Visa dimensions: {us_visa_rule.dimensions['width']}x{us_visa_rule.dimensions['height']}")
        
        print(f"\nBase ICAO face height ratio: {base_rule.face_requirements['height_ratio']}")
        print(f"US Visa face height ratio: {us_visa_rule.face_requirements['height_ratio']}")
        
        print(f"\nBase ICAO background color: {base_rule.background['color']}")
        print(f"US Visa background color: {us_visa_rule.background['color']} (inherited)")
        
        print(f"\nBase ICAO validation strictness: {base_rule.validation_strictness}")
        print(f"US Visa validation strictness: {us_visa_rule.validation_strictness} (overridden)")


def demonstrate_auto_detection(detector: FormatDetector, image_paths: list):
    """Demonstrate automatic format detection."""
    print("\n" + "="*60)
    print("DEMONSTRATING AUTO-DETECTION")
    print("="*60)
    
    for image_path in image_paths:
        print(f"\nAnalyzing: {image_path.name}")
        
        try:
            results = detector.detect_format(str(image_path), confidence_threshold=0.1)
            
            if results:
                print(f"  Found {len(results)} potential matches:")
                for i, result in enumerate(results[:3], 1):  # Show top 3
                    print(f"    {i}. {result.format_id} (confidence: {result.confidence:.3f})")
                    print(f"       Reasons: {', '.join(result.match_reasons)}")
                    print(f"       Dimension match: {result.dimension_match}")
                    print(f"       Aspect ratio match: {result.aspect_ratio_match}")
            else:
                print("  No format matches found")
        
        except Exception as e:
            print(f"  Error analyzing image: {e}")


def demonstrate_validation(engine: FormatRuleEngine):
    """Demonstrate format-specific validation."""
    print("\n" + "="*60)
    print("DEMONSTRATING FORMAT VALIDATION")
    print("="*60)
    
    # Create sample validation data
    validation_data = {
        "dimensions": {"width": 600, "height": 600},
        "face_analysis": {
            "height_ratio": 0.75,
            "eye_height_ratio": 0.55,
            "center_offset": 0.03
        },
        "background_analysis": {
            "dominant_color": [250, 250, 250],
            "uniformity": 0.95
        },
        "quality_analysis": {
            "sharpness": 150,
            "brightness": 120
        }
    }
    
    formats_to_test = ["demo_base_icao", "demo_us_visa", "demo_ics_uae"]
    
    for format_id in formats_to_test:
        print(f"\nValidating against {format_id}:")
        
        result = engine.validate_format_compliance(format_id, validation_data)
        
        if result["success"]:
            print(f"  Overall compliance: {result['overall_compliance']:.3f}")
            print(f"  Validation strictness: {result['validation_strictness']}")
            print(f"  Rule results:")
            
            for rule_result in result["rule_results"]:
                status = "PASS" if rule_result["passes"] else "FAIL"
                print(f"    {rule_result['category']}: {status} (score: {rule_result['score']:.3f})")
                if rule_result["details"]:
                    for detail in rule_result["details"][:2]:  # Show first 2 details
                        print(f"      - {detail}")
        else:
            print(f"  Validation failed: {result.get('error', 'Unknown error')}")


def demonstrate_hot_reload(engine: FormatRuleEngine, config_dir: Path):
    """Demonstrate hot-reload functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING HOT-RELOAD")
    print("="*60)
    
    # Set up hot-reload manager
    hot_reload = setup_hot_reload(engine, [str(config_dir)], auto_start=False)
    
    # Track reload events
    reload_events = []
    
    def track_reload(message):
        reload_events.append(message)
        print(f"  Reload event: {message}")
    
    hot_reload.add_change_handler(track_reload)
    
    print(f"\nInitial formats: {engine.get_available_formats()}")
    
    # Create a new format configuration
    new_format = {
        "format_id": "demo_dynamic",
        "display_name": "Demo Dynamic Format",
        "inherits_from": "demo_base_icao",
        "dimensions": {
            "width": 500,
            "height": 700
        },
        "validation_strictness": "lenient"
    }
    
    new_config_path = config_dir / "demo_dynamic.json"
    print(f"\nAdding new format configuration: {new_config_path}")
    
    with open(new_config_path, 'w') as f:
        json.dump(new_format, f, indent=2)
    
    # Force reload to simulate file change detection
    print("Forcing configuration reload...")
    success = hot_reload.force_reload()
    
    if success:
        print("Reload successful!")
        updated_formats = engine.get_available_formats()
        print(f"Updated formats: {updated_formats}")
        
        # Test the new format
        if "demo_dynamic" in updated_formats:
            new_rule = engine.get_format_rule("demo_dynamic")
            print(f"New format details:")
            print(f"  Display name: {new_rule.display_name}")
            print(f"  Dimensions: {new_rule.dimensions['width']}x{new_rule.dimensions['height']}")
            print(f"  Background color: {new_rule.background['color']} (inherited)")
            print(f"  Validation strictness: {new_rule.validation_strictness}")
    else:
        print("Reload failed!")
    
    # Show reload statistics
    stats = hot_reload.get_reload_statistics()
    print(f"\nReload statistics:")
    print(f"  Total reloads: {stats['total_reloads']}")
    print(f"  Successful reloads: {stats['successful_reloads']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    
    # Clean up
    hot_reload.stop_watching()


def demonstrate_format_suggestions(detector: FormatDetector, image_paths: list):
    """Demonstrate format improvement suggestions."""
    print("\n" + "="*60)
    print("DEMONSTRATING FORMAT IMPROVEMENT SUGGESTIONS")
    print("="*60)
    
    # Test suggestions for different format targets
    test_cases = [
        {"image": image_paths[0], "target": "demo_us_visa"},
        {"image": image_paths[1], "target": "demo_ics_uae"}
    ]
    
    for case in test_cases:
        print(f"\nAnalyzing {case['image'].name} for {case['target']}:")
        
        try:
            suggestions = detector.suggest_format_improvements(
                str(case['image']), 
                case['target']
            )
            
            if 'error' not in suggestions:
                print(f"  Target format: {suggestions['format_name']}")
                print(f"  Auto-fix available: {suggestions['auto_fix_available']}")
                
                if suggestions['improvements']:
                    print(f"  Suggested improvements:")
                    for improvement in suggestions['improvements']:
                        priority = improvement.get('priority', 'medium').upper()
                        fixable = "Auto-fixable" if improvement.get('auto_fixable') else "Manual fix required"
                        print(f"    [{priority}] {improvement['issue']}")
                        print(f"             {improvement['suggestion']} ({fixable})")
                else:
                    print("  No improvements needed!")
            else:
                print(f"  Error: {suggestions['error']}")
        
        except Exception as e:
            print(f"  Error analyzing image: {e}")


def demonstrate_validation_context(engine: FormatRuleEngine):
    """Demonstrate validation context creation and usage."""
    print("\n" + "="*60)
    print("DEMONSTRATING VALIDATION CONTEXT")
    print("="*60)
    
    # Create validation contexts for different scenarios
    contexts = [
        {
            "format_id": "demo_us_visa",
            "image_path": "/demo/us_visa_photo.jpg",
            "dimensions": (600, 600),
            "options": {"quality": "high", "auto_fix": True}
        },
        {
            "format_id": "demo_ics_uae",
            "image_path": "/demo/ics_uae_photo.jpg", 
            "dimensions": (413, 531),
            "options": {"quality": "standard", "batch_mode": True}
        }
    ]
    
    for ctx_info in contexts:
        print(f"\nCreating validation context for {ctx_info['format_id']}:")
        
        context = engine.create_validation_context(
            ctx_info['format_id'],
            image_path=ctx_info['image_path'],
            image_dimensions=ctx_info['dimensions'],
            processing_options=ctx_info['options']
        )
        
        if context:
            print(f"  Format: {context.format_rule.display_name}")
            print(f"  Country: {context.format_rule.country}")
            print(f"  Authority: {context.format_rule.authority}")
            print(f"  Image path: {context.image_path}")
            print(f"  Dimensions: {context.image_dimensions}")
            print(f"  Processing options: {context.processing_options}")
            print(f"  Validation strictness: {context.format_rule.validation_strictness}")
            print(f"  Auto-fix enabled: {context.format_rule.auto_fix_enabled}")
        else:
            print(f"  Failed to create context for {ctx_info['format_id']}")


def main():
    """Main demonstration function."""
    print("Format Rule Engine Demonstration")
    print("="*60)
    
    # Create temporary directory for demo
    temp_dir = Path(tempfile.mkdtemp(prefix="format_demo_"))
    config_dir = temp_dir / "formats"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create demo configurations and images
        create_demo_configurations(config_dir)
        image_paths = create_demo_images(temp_dir)
        
        # Initialize components
        print(f"\nInitializing Format Rule Engine with config directory: {config_dir}")
        engine = FormatRuleEngine(str(config_dir))
        detector = FormatDetector(engine)
        
        # Run demonstrations
        demonstrate_format_loading(engine)
        demonstrate_auto_detection(detector, image_paths)
        demonstrate_validation(engine)
        demonstrate_format_suggestions(detector, image_paths)
        demonstrate_validation_context(engine)
        demonstrate_hot_reload(engine, config_dir)
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("="*60)
        print(f"\nDemo files created in: {temp_dir}")
        print("You can examine the configuration files and modify them to test hot-reload.")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up (optional - comment out to keep files for inspection)
        try:
            shutil.rmtree(temp_dir)
            print(f"\nCleaned up temporary directory: {temp_dir}")
        except:
            print(f"\nNote: Temporary directory not cleaned up: {temp_dir}")


if __name__ == "__main__":
    main()