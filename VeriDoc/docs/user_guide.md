# Veridoc Universal - User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Interface Overview](#user-interface-overview)
3. [Processing Photos](#processing-photos)
4. [Understanding Results](#understanding-results)
5. [Auto-Fix Features](#auto-fix-features)
6. [Batch Processing](#batch-processing)
7. [Export and Reports](#export-and-reports)
8. [New Processing Pipeline](#new-processing-pipeline)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Getting Started

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 18.04+
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 10GB available space
- **Processor**: 4-core CPU minimum (8-core recommended)

### First Launch

1. **Start the Application**
   - Double-click the Veridoc Universal icon
   - Wait for the AI models to load (first launch may take 2-3 minutes)
   - The main interface will appear when ready

2. **Initial Setup**
   - Select your preferred language
   - Choose default photo format (ICAO, US Visa, Schengen, etc.)
   - Configure output directory for processed photos

## User Interface Overview

### Main Window Components

```
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  View  Tools  Help                    [- □ ×]    │
├─────────────────────────────────────────────────────────────┤
│ 📁 Import Photos  📋 Process All  ⚙️ Settings  📊 Show Stats    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │                 │    │ Validation Results              │ │
│  │   Image Preview │    │                                 │ │
│  │                 │    │ ✅ Face Detection: Passed       │ │
│  │                 │    │ ⚠️  Background: Needs Fix       │ │
│  │                 │    │ ✅ Lighting: Passed             │ │
│  │                 │    │ ❌ Expression: Failed           │ │
│  │                 │    │                                 │ │
│  │                 │    │ Overall Score: 75/100          │ │
│  └─────────────────┘    │                                 │ │
│                         │ 🔧 Auto-Fix Available          │ │
│  Format: ICAO Standard  │ 📄 Generate Report             │ │
│  Status: Processing...  │ 💾 Export Image                │ │
│                         └─────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Ready | Images: 0 | Processed: 0 | Errors: 0              │
└─────────────────────────────────────────────────────────────┘
```

### Key Interface Elements

1. **Image Preview Panel**: Shows the current photo with overlay indicators
2. **Validation Results Panel**: Displays compliance check results
3. **Toolbar**: Quick access to common functions
4. **Status Bar**: Shows processing status and statistics
5. **Format Selector**: Choose photo format requirements

## Processing Photos

### Single Photo Processing

1. **Load a Photo**
   ```
   Click "📁 Import Photos" → Select photo file → Click "Open"
   ```
   - Supported formats: JPEG, PNG, TIFF, BMP
   - Maximum file size: 50MB
   - Recommended resolution: 600×800 to 2400×3000 pixels

2. **Select Format**
   ```
   Format dropdown → Choose format (ICS-UAE, ICAO, etc.)
   ```
   - **ICS-UAE**: UAE identity card photos
   - **ICAO Standard**: International passport photos

3. **Start Processing**
   ```
   Click "Process All" or select an image to process it individually
   ```
   - Processing typically takes 2-5 seconds
   - Progress bar shows current step
   - Results appear in the validation panel

### Understanding Processing Steps

The system performs these checks in order:

1. **🔍 Face Detection** (1-2 seconds)
   - Locates primary face in the image
   - Identifies facial landmarks
   - Measures face dimensions and positioning

2. **📏 Geometry Validation** (0.5 seconds)
   - Checks face height ratio (70-80% of image)
   - Verifies eye height positioning (50-60%)
   - Confirms face centering

3. **👓 Accessories Check** (0.5 seconds)
   - Detects glasses and validates compliance
   - Identifies head coverings
   - Checks for jewelry or other accessories

4. **😐 Expression Analysis** (0.5 seconds)
   - Verifies neutral expression
   - Checks for closed mouth
   - Confirms direct gaze

5. **💡 Quality Assessment** (1 second)
   - Measures image sharpness
   - Analyzes lighting uniformity
   - Checks color accuracy and contrast

6. **🎨 Background Validation** (0.5 seconds)
   - Verifies white/neutral background
   - Checks for shadows or patterns
   - Measures background uniformity

## Understanding Results

### Validation Results Panel

Each check shows one of four states:

- **✅ Passed**: Meets all requirements
- **⚠️ Warning**: Minor issues that may be acceptable
- **❌ Failed**: Does not meet requirements
- **🔧 Fixable**: Can be corrected with auto-fix

### Detailed Results

Click on any result to see detailed information:

```
Background Check: ❌ Failed
├─ Issue: Non-white background detected
├─ Measured: Light blue background (RGB: 200, 220, 255)
├─ Required: White background (RGB: 245-255, 245-255, 245-255)
├─ Confidence: 95%
├─ Auto-fix: ✅ Available
└─ Regulation: ICAO Doc 9303 Part 6 Section 1.1
```

### Overall Compliance Score

The system provides an overall score (0-100):

- **90-100**: Excellent - Meets all requirements
- **80-89**: Good - Minor issues only
- **70-79**: Acceptable - Some fixes needed
- **60-69**: Poor - Multiple issues
- **Below 60**: Unacceptable - Major problems

### Common Issues and Meanings

| Issue | Description | Auto-Fix Available |
|-------|-------------|-------------------|
| **Tinted Glasses** | Sunglasses or tinted lenses detected | ❌ No |
| **Heavy Frames** | Thick glasses frames obscuring eyes | ❌ No |
| **Smiling** | Non-neutral expression detected | ❌ No |
| **Poor Lighting** | Uneven lighting or shadows | ✅ Yes |
| **Wrong Background** | Non-white background | ✅ Yes |
| **Off-Center** | Face not properly centered | ✅ Yes |
| **Too Dark/Bright** | Image exposure issues | ✅ Yes |
| **Blurry** | Image not sharp enough | ⚠️ Limited |

## Auto-Fix Features

### When Auto-Fix is Available

The 🔧 Auto-Fix button appears when the system can automatically correct issues:

1. **Background Replacement**
   - Removes non-compliant backgrounds
   - Replaces with clean white background
   - Preserves natural edge details

2. **Lighting Correction**
   - Adjusts brightness and contrast
   - Reduces shadows and highlights
   - Improves overall exposure

3. **Geometry Correction**
   - Centers the face properly
   - Adjusts face size ratio
   - Corrects minor rotation issues

4. **Quality Enhancement**
   - Sharpens slightly blurry images
   - Reduces noise
   - Improves color accuracy

### Using Auto-Fix

1. **Review Issues**
   ```
   Check which issues are marked as "🔧 Fixable"
   ```

2. **Apply Auto-Fix**
   ```
   Click "🔧 Auto-Fix" button
   ```
   - Processing takes 3-8 seconds
   - Before/after preview shows changes
   - Original image is preserved

3. **Review Results**
   ```
   Compare original and corrected versions
   Check updated validation results
   ```

4. **Accept or Reject**
   ```
   Click "✅ Accept" to keep changes
   Click "❌ Reject" to revert to original
   ```

### Auto-Fix Limitations

**Cannot Fix:**
- Tinted glasses or sunglasses
- Heavy glasses frames
- Facial expressions (smiling, frowning)
- Eyes closed or looking away
- Multiple people in photo
- Severely blurry or out-of-focus images

**Limited Fix:**
- Very poor lighting conditions
- Complex backgrounds with people
- Extreme face angles or rotations
- Very low resolution images

## Batch Processing

### Setting Up Batch Processing

1. **Prepare Images**
   - Place all photos in a single folder
   - Ensure consistent naming convention
   - Remove any non-photo files

2. **Start Batch Mode**
   ```
   Click "📋 Process All" → Select folder → Choose format
   ```

3. **Configure Options**
   ```
   ☑️ Auto-fix when possible
   ☑️ Generate individual reports
   ☑️ Create summary report
   ☑️ Export processed images
   ```

### Batch Processing Interface

```
┌─────────────────────────────────────────────────────────────┐
│ Batch Processing - 25 images selected                      │
├─────────────────────────────────────────────────────────────┤
│ Progress: ████████████░░░░░░░░ 12/25 (48%)                 │
│                                                             │
│ Current: IMG_0012.jpg                                       │
│ Status: Processing... (Step 3/6: Expression Analysis)      │
│ Time Remaining: ~2 minutes                                  │
│                                                             │
│ Results Summary:                                            │
│ ✅ Passed: 8 images                                         │
│ 🔧 Fixed: 3 images                                          │
│ ⚠️ Warnings: 1 image                                        │
│ ❌ Failed: 0 images                                          │
│                                                             │
│ [⏸️ Pause] [⏹️ Stop] [📊 View Details]                      │
└─────────────────────────────────────────────────────────────┘
```

### Batch Results

After processing, you'll see:

1. **Summary Statistics**
   - Total images processed
   - Pass/fail breakdown
   - Average processing time
   - Auto-fix success rate

2. **Individual Results**
   - List of all processed images
   - Status for each image
   - Issues found and fixes applied

3. **Export Options**
   - Processed images folder
   - CSV report with all results
   - PDF summary report
   - Failed images list

## Export and Reports

### Export Options

1. **Single Image Export**
   ```
   Click "💾 Export Image" → Choose location → Select format
   ```
   - Original quality JPEG (recommended)
   - High-quality PNG
   - TIFF for archival purposes

2. **Batch Export**
   ```
   After batch processing → Click "📁 Export All"
   ```
   - Creates organized folder structure
   - Includes processed images
   - Adds compliance reports

### Report Types

1. **Individual Photo Report**
   ```
   Photo: IMG_001.jpg
   Format: ICAO Standard
   Processing Date: 2024-08-14 15:30:22
   
   Overall Score: 85/100 ✅ PASSED
   
   Detailed Results:
   ✅ Face Detection: Passed (Confidence: 98%)
   ✅ Geometry: Passed (Face ratio: 75%)
   ⚠️ Glasses: Warning (Clear frames detected)
   ✅ Expression: Passed (Neutral expression)
   ✅ Quality: Passed (Sharpness: Good)
   🔧 Background: Fixed (Replaced blue background)
   
   Auto-Fix Applied:
   - Background replacement
   - Minor lighting adjustment
   
   Compliance: Meets ICAO Doc 9303 requirements
   ```

2. **Batch Summary Report**
   ```
   Batch Processing Summary
   Date: 2024-08-14
   Total Images: 50
   Processing Time: 3 minutes 45 seconds
   
   Results Breakdown:
   ✅ Passed: 42 images (84%)
   🔧 Fixed: 6 images (12%)
   ❌ Failed: 2 images (4%)
   
   Common Issues:
   1. Background problems: 8 images (16%)
   2. Lighting issues: 4 images (8%)
   3. Positioning: 3 images (6%)
   
   Auto-Fix Success Rate: 75%
   
   Failed Images:
   - IMG_023.jpg: Tinted glasses
   - IMG_041.jpg: Multiple faces
   ```

3. **Compliance Certificate**
   ```
   COMPLIANCE CERTIFICATE
   
   This certifies that the processed image meets the
   requirements of ICAO Document 9303 for machine-readable
   travel documents.
   
   Image: passport_photo_final.jpg
   Processing Date: 2024-08-14
   Validation Score: 95/100
   
   Verified Compliance:
   ✅ Facial geometry and positioning
   ✅ Background and lighting standards
   ✅ Image quality and resolution
   ✅ Expression and gaze requirements
   
   Digital Signature: [Hash: a1b2c3d4...]
   ```

## New Processing Pipeline

The new processing pipeline provides a more robust and efficient way to process images. It introduces a new API layer that separates the UI from the backend, allowing for better performance and scalability.

### Key Features

- **Asynchronous Processing**: The UI remains responsive while images are being processed in the background.
- **Real-time Progress Updates**: A progress bar and status messages keep you informed about the processing status.
- **Comprehensive Error Handling**: Clear and user-friendly error messages help you troubleshoot issues.
- **Statistics and Reporting**: Track your processing statistics and generate reports.

## Troubleshooting

### Common Problems

#### 1. "No Face Detected"

**Possible Causes:**
- Face too small or large in image
- Poor lighting conditions
- Face partially obscured
- Multiple faces in image

**Solutions:**
- Ensure face occupies 70-80% of image height
- Improve lighting conditions
- Remove obstructions
- Crop to show only one person

#### 2. "Processing Failed"

**Possible Causes:**
- Corrupted image file
- Unsupported file format
- Insufficient memory
- AI model loading error

**Solutions:**
- Try a different image format (JPEG recommended)
- Restart the application
- Check available memory (8GB+ recommended)
- Verify AI models are properly installed

#### 3. "Auto-Fix Not Working"

**Possible Causes:**
- Issue cannot be automatically corrected
- Image quality too poor
- Complex background
- Hardware limitations

**Solutions:**
- Review which issues are marked as "fixable"
- Try manual photo editing first
- Use higher quality source image
- Check system resources

#### 4. Slow Processing

**Possible Causes:**
- Large image files
- Insufficient hardware
- Background applications
- AI model not optimized

**Solutions:**
- Resize images to 1200×1600 pixels maximum
- Close other applications
- Enable GPU acceleration if available
- Check CPU and memory usage

### Getting Help

1. **Built-in Help**
   ```
   Help menu → User Guide
   Help menu → Troubleshooting
   Help menu → About (version info)
   ```

2. **Log Files**
   ```
   View menu → Show Logs
   ```
   - Processing logs
   - Error messages
   - Performance metrics

3. **Diagnostic Information**
   ```
   Tools menu → System Diagnostics
   ```
   - Hardware information
   - AI model status
   - Performance metrics
   - Configuration details

## Best Practices

### Photo Preparation

1. **Lighting**
   - Use even, diffused lighting
   - Avoid harsh shadows
   - Natural daylight is best
   - Avoid flash if possible

2. **Background**
   - Use plain white or light gray background
   - Ensure background is uniform
   - Avoid patterns or textures
   - Keep background clean

3. **Positioning**
   - Center face in frame
   - Keep head straight
   - Maintain neutral expression
   - Look directly at camera

4. **Camera Settings**
   - Use highest quality setting
   - Ensure image is in focus
   - Avoid digital zoom
   - Take multiple shots

### Processing Tips

1. **Format Selection**
   - Choose correct format before processing
   - Different formats have different requirements
   - When in doubt, use ICAO Standard

2. **Auto-Fix Usage**
   - Review auto-fix results carefully
   - Compare before/after versions
   - Don't rely on auto-fix for major issues
   - Manual editing may be needed for complex problems

3. **Batch Processing**
   - Process similar images together
   - Use consistent naming convention
   - Review failed images individually
   - Keep original images as backup

4. **Quality Control**
   - Always review final results
   - Check compliance scores
   - Verify auto-fix didn't introduce artifacts
   - Test print quality if needed

### File Management

1. **Organization**
   ```
   Photos/
   ├── Original/
   │   ├── batch_001/
   │   └── batch_002/
   ├── Processed/
   │   ├── batch_001/
   │   └── batch_002/
   └── Reports/
       ├── individual/
       └── summaries/
   ```

2. **Naming Convention**
   ```
   Original: lastname_firstname_001.jpg
   Processed: lastname_firstname_001_processed.jpg
   Report: lastname_firstname_001_report.pdf
   ```

3. **Backup Strategy**
   - Keep original images safe
   - Backup processed images
   - Save compliance reports
   - Regular system backups

---

*For additional support, please refer to the troubleshooting guide or contact technical support.*