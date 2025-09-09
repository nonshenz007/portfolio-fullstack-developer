"""
Default configuration for VeriDoc ICS (UAE) format only.
Provides ICS-specific configuration for government-grade photo validation.
"""

from typing import Dict, Any


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration for ICS (UAE) government format only.
    
    Returns:
        Dict[str, Any]: Default ICS configuration dictionary
    """
    return {
        "formats": {
            "ICS-UAE": {
                "display_name": "ICS (UAE) - Government Standard",
                "dimensions": {
                    "width": 413,
                    "height": 531,
                    "unit": "pixels",
                    "dpi": 300
                },
                "face_requirements": {
                    # ICS UAE government specification
                    "height_ratio": [0.62, 0.69],
                    "eye_height_ratio": [0.33, 0.36],
                    "centering_tolerance": 0.05,
                    "max_rotation_deg": 2.0,
                    "max_yaw_deg": 6.0,
                    "min_eyes_open_ratio": 0.28,
                    "max_mouth_open_ratio": 0.06,
                    "single_face_only": True
                },
                "background": {
                    "color": "light_grey",
                    "rgb_values": [240, 240, 240],
                    "tolerance": 12
                },
                "file_specs": {
                    "format": "JPEG",
                    "max_size_mb": 2,
                    "quality": 95
                },
                "quality_thresholds": {
                    "min_brightness": 55,
                    "max_brightness": 190,
                    "min_sharpness": 120,
                    "max_blur_variance": 45
                }
            }
        },
        "global_settings": {
            "temp_directory": "temp/saved/",
            "export_directory": "export/",
            "log_file": "logs/veridoc_ics_log.csv",
            "trial_watermark": "VERIDOC ICS TRIAL",
            "supported_input_formats": ["jpg", "jpeg", "png", "bmp", "tiff"],
            "max_log_size_mb": 10,
            "log_rotation_count": 5,
            "default_format": "ICS-UAE",
            "government_grade": True,
            "security_enabled": True
        }
    }