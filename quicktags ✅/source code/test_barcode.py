#!/usr/bin/env python3
"""
Test script to verify improved barcode generation works properly
"""

import sys
import os
from PIL import Image

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_barcode_generation():
    """Test barcode generation with different methods"""
    
    print("Testing improved barcode generation...")
    
    # Test 1: New thermal-optimized barcode generation
    try:
        from quicktags import BarcodeGenerator
        import logging
        
        # Create logger
        logger = logging.getLogger('test')
        logger.setLevel(logging.INFO)
        
        # Create barcode generator
        barcode_gen = BarcodeGenerator(logger)
        barcode_gen.set_dimensions("38x25mm")
        
        test_code = "123456789012"  # 12 digits (check digit will be calculated)
        
        # Generate thermal-optimized barcode
        barcode_image = barcode_gen.create_thermal_optimized_barcode(test_code)
        
        # Save test image
        barcode_image.save('test_barcode_thermal_optimized.png')
        print("✅ Thermal-optimized barcode test: PASSED")
        
    except Exception as e:
        print(f"❌ Thermal-optimized barcode test: FAILED - {e}")
    
    # Test 2: Improved python-barcode library
    try:
        import barcode
        from barcode.writer import ImageWriter
        
        test_code = "1234567890123"  # 13 digits for EAN-13
        
        # Create EAN-13 barcode with improved settings
        ean = barcode.get('ean13', test_code, writer=ImageWriter())
        
        # Generate image with thermal printer optimized settings
        barcode_image = ean.render({
            'module_width': 0.4,      # Wider bars for better scanning
            'module_height': 20.0,     # Taller bars for better scanning
            'quiet_zone': 10.0,        # Larger quiet zone
            'font_size': 1,            # Minimal font size (will be removed later)
            'text_distance': 0,        # No text distance
            'background': 'white',
            'foreground': 'black'
        })
        
        # Convert to 1-bit mode
        if barcode_image.mode != '1':
            barcode_image = barcode_image.convert('1')
        
        # Save test image
        barcode_image.save('test_barcode_python_barcode_improved.png')
        print("✅ Improved python-barcode library test: PASSED")
        
    except Exception as e:
        print(f"❌ Improved python-barcode library test: FAILED - {e}")
    
    # Test 3: Improved simple barcode
    try:
        from quicktags import BarcodeGenerator
        import logging
        
        # Create logger
        logger = logging.getLogger('test')
        logger.setLevel(logging.INFO)
        
        # Create barcode generator
        barcode_gen = BarcodeGenerator(logger)
        barcode_gen.set_dimensions("38x25mm")
        
        test_code = "1234567890123"
        
        # Generate improved simple barcode
        barcode_image = barcode_gen.create_simple_barcode(test_code)
        
        # Save test image
        barcode_image.save('test_barcode_simple_improved.png')
        print("✅ Improved simple barcode test: PASSED")
        
    except Exception as e:
        print(f"❌ Improved simple barcode test: FAILED - {e}")
    
    # Test 4: Check digit calculation
    try:
        from quicktags import BarcodeGenerator
        import logging
        
        # Create logger
        logger = logging.getLogger('test')
        logger.setLevel(logging.INFO)
        
        # Create barcode generator
        barcode_gen = BarcodeGenerator(logger)
        
        test_code = "123456789012"
        check_digit = barcode_gen.calculate_ean13_check_digit(test_code)
        expected_check = 8  # For 123456789012, check digit should be 8
        
        if check_digit == expected_check:
            print("✅ Check digit calculation test: PASSED")
        else:
            print(f"❌ Check digit calculation test: FAILED - Expected {expected_check}, got {check_digit}")
        
    except Exception as e:
        print(f"❌ Check digit calculation test: FAILED - {e}")
    
    print("\nBarcode generation tests completed!")
    print("Check the generated PNG files to verify barcode quality.")
    print("The thermal-optimized barcode should be much more readable!")

if __name__ == "__main__":
    test_barcode_generation() 