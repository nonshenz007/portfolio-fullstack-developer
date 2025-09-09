#!/usr/bin/env python3
"""
AutoFix Engine Demo

This script demonstrates the AutoFix Engine capabilities for intelligent
photo compliance corrections.
"""

import sys
import os
import numpy as np
import cv2
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autofix.autofix_engine import AutoFixEngine, ComplianceIssue, ValidationResult
from ai.ai_engine import AIEngine
from validation.icao_validator import ICAOValidator


def create_sample_validation_result() -> ValidationResult:
    """Create a sample validation result with fixable issues."""
    issues = [
        ComplianceIssue(
            category="background",
            severity="major",
            description="Background is not uniform white",
            fix_suggestion="Replace with uniform white background",
            auto_fixable=True,
            regulation_reference="ICAO.6.1.1"
        ),
        ComplianceIssue(
            category="lighting",
            severity="minor",
            description="Uneven lighting detected",
            fix_suggestion="Adjust lighting uniformity",
            auto_fixable=True,
            regulation_reference="ICAO.5.2.1"
        ),
        ComplianceIssue(
            category="glasses",
            severity="critical",
            description="Tinted glasses detected",
            fix_suggestion="Remove tinted glasses",
            auto_fixable=False,
            regulation_reference="ICAO.3.2.1"
        )
    ]
    
    return ValidationResult(
        overall_compliance=65.0,
        passes_requirements=False,
        rule_results=[],
        issue_summary=issues,
        improvement_suggestions=["Fix background", "Improve lighting"],
        confidence_score=0.85
    )


def create_test_image() -> np.ndarray:
    """Create a test image for demonstration."""
    # Create a simple test image with a face-like region
    image = np.random.randint(100, 200, (400, 300, 3), dtype=np.uint8)
    
    # Add a darker background to simulate non-compliant background
    image[:, :200] = [180, 180, 180]  # Light gray background
    image[:, 200:] = [220, 220, 220]  # Slightly different background
    
    # Add a face-like region
    cv2.ellipse(image, (150, 200), (60, 80), 0, 0, 360, (200, 180, 160), -1)
    
    return image


def main():
    """Main demo function."""
    print("AutoFix Engine Demo")
    print("=" * 50)
    
    # Initialize components
    print("Initializing AI Engine and AutoFix Engine...")
    ai_engine = AIEngine()
    autofix_engine = AutoFixEngine(ai_engine)
    
    # Create test data
    print("Creating test image and validation result...")
    test_image = create_test_image()
    validation_result = create_sample_validation_result()
    
    print(f"Original compliance score: {validation_result.overall_compliance:.1f}%")
    print(f"Issues found: {len(validation_result.issue_summary)}")
    
    # Analyze issues
    print("\nAnalyzing compliance issues...")
    issue_analysis = autofix_engine.analyze_issues(validation_result, test_image)
    
    print(f"Fixable issues: {len(issue_analysis.fixable_issues)}")
    print(f"Unfixable issues: {len(issue_analysis.unfixable_issues)}")
    print(f"Estimated improvement: {issue_analysis.estimated_improvement:.1f}%")
    print(f"Quality risk: {issue_analysis.quality_risk_assessment}")
    print(f"Recommended approach: {issue_analysis.recommended_approach}")
    
    # Plan corrections
    print("\nPlanning corrections...")
    correction_plan = autofix_engine.plan_corrections(issue_analysis, test_image)
    
    print(f"Planned corrections: {len(correction_plan.corrections)}")
    for correction in correction_plan.corrections:
        print(f"  - {correction['operation']}: {correction['method']}")
    
    # Apply corrections
    print("\nApplying corrections...")
    autofix_result = autofix_engine.apply_corrections(
        test_image, correction_plan, validation_result
    )
    
    print(f"Auto-fix success: {autofix_result.success}")
    print(f"Applied corrections: {len(autofix_result.applied_corrections)}")
    print(f"Quality preserved: {autofix_result.quality_preserved}")
    print(f"Processing time: {autofix_result.processing_time:.3f}s")
    
    if autofix_result.after_validation:
        improvement = (autofix_result.after_validation.overall_compliance - 
                      validation_result.overall_compliance)
        print(f"Compliance improvement: +{improvement:.1f}%")
    
    # Display warnings and recommendations
    if autofix_result.warnings:
        print("\nWarnings:")
        for warning in autofix_result.warnings:
            print(f"  - {warning}")
    
    if autofix_result.recommendations:
        print("\nRecommendations:")
        for recommendation in autofix_result.recommendations:
            print(f"  - {recommendation}")
    
    # Save results if corrected image is available
    if autofix_result.corrected_image is not None:
        output_dir = Path("temp/autofix_demo")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save original and corrected images
        cv2.imwrite(str(output_dir / "original.jpg"), test_image)
        cv2.imwrite(str(output_dir / "corrected.jpg"), autofix_result.corrected_image)
        
        print(f"\nImages saved to: {output_dir}")
        print("  - original.jpg: Original test image")
        print("  - corrected.jpg: Auto-fixed image")
    
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    main()