#!/usr/bin/env python3
"""
Government Standards Calibration Tool
Analyzes government-approved photos to set perfect scoring thresholds
"""

import os
import sys
import glob
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.unified_ai_engine import get_unified_engine

def analyze_government_photos():
    """Analyze all government-approved photos and calibrate scoring"""
    
    print("🎯 GOVERNMENT STANDARDS CALIBRATION")
    print("=" * 50)
    
    # Initialize unified engine
    engine = get_unified_engine()
    if not engine:
        print("❌ Failed to initialize unified engine")
        return
    
    # Find all government-approved photos
    gov_photos_dir = "work/samples/gov_approved"
    photo_patterns = ["*.jpg", "*.jpeg", "*.png"]
    
    all_photos = []
    for pattern in photo_patterns:
        all_photos.extend(glob.glob(os.path.join(gov_photos_dir, pattern)))
    
    if not all_photos:
        print(f"❌ No photos found in {gov_photos_dir}")
        return
    
    print(f"📸 Found {len(all_photos)} government-approved photos")
    print()
    
    # Analyze each photo
    scores = []
    for photo_path in all_photos:
        photo_name = os.path.basename(photo_path)
        print(f"📋 Analyzing: {photo_name}")
        
        try:
            # Process with unified engine
            result = engine.process_image(photo_path, "ICS-UAE")
            
            print(f"   Score: {result.compliance_score:.1f}%")
            print(f"   Face Detected: {result.face_detected}")
            print(f"   Overall Pass: {result.overall_pass}")
            print()
            
            scores.append(result.compliance_score)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
    
    if scores:
        min_score = min(scores)
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        
        print("📊 GOVERNMENT PHOTO ANALYSIS:")
        print(f"   Minimum Score: {min_score:.1f}%")
        print(f"   Maximum Score: {max_score:.1f}%") 
        print(f"   Average Score: {avg_score:.1f}%")
        print()
        
        print("🎯 RECOMMENDED CALIBRATION:")
        print(f"   Set 100% threshold at: {min_score:.0f}%")
        print(f"   (All gov photos will score 100%)")
        
        return min_score
    
    return None

if __name__ == "__main__":
    analyze_government_photos()
