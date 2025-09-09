#!/usr/bin/env python3
"""
Simple test to create a test image and run the VeriDoc CLI processing pipeline
"""

import numpy as np
import cv2
import os
from pathlib import Path

def create_test_image():
    """Create a simple test image"""
    # Create a 600x800 test image (passport photo dimensions)
    img = np.ones((800, 600, 3), dtype=np.uint8) * 240  # Light gray background
    
    # Draw a simple face-like circle
    center = (300, 300)
    cv2.circle(img, center, 100, (200, 180, 160), -1)  # Face
    cv2.circle(img, (270, 280), 10, (50, 50, 50), -1)  # Left eye
    cv2.circle(img, (330, 280), 10, (50, 50, 50), -1)  # Right eye
    cv2.ellipse(img, (300, 320), (20, 10), 0, 0, 180, (100, 100, 100), 2)  # Mouth
    
    # Add some text
    cv2.putText(img, 'VeriDoc Test', (200, 750), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    return img

def main():
    print("🧪 Creating test image for VeriDoc PPP...")
    
    # Create directories
    os.makedirs("temp/test_input", exist_ok=True)
    os.makedirs("temp/test_output", exist_ok=True)
    
    # Create and save test image
    test_img = create_test_image()
    test_path = "temp/test_input/test_photo.jpg"
    cv2.imwrite(test_path, test_img)
    print(f"✅ Test image created: {test_path}")
    
    print("\n🚀 Now run the VeriDoc CLI processing:")
    print("source venv/bin/activate")
    print("python tools/validate_cli.py --input temp/test_input --format ICS-UAE --out temp/test_output --no-ai")
    print("\n📁 Results will be in temp/test_output/")

if __name__ == "__main__":
    main()
