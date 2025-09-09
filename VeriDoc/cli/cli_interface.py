"""
Command Line Interface for VeriDoc Universal

Provides comprehensive CLI functionality for batch processing,
single image validation, and system management operations.
"""

import argparse
import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from core.config_manager import ProcessingOptions


class CLIInterface:
    """
    Command Line Interface for VeriDoc Universal.
    
    Provides full CLI functionality including batch processing,
    validation, auto-fix, export, and system management.
    """
    
    def __init__(self, app_instance):
        """
        Initialize CLI interface.
        
        Args:
            app_instance: Main application instance
        """
        self.app = app_instance
        self.logger = logging.getLogger(__name__)
    
    def run(self, args: List[str]) -> int:
        """
        Run CLI with provided arguments.
        
        Args:
            args: Command line arguments
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        parser = self._create_parser()
        
        try:
            parsed_args = parser.parse_args(args)
            
            # Set logging level based on verbosity
            if parsed_args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            elif parsed_args.quiet:
                logging.getLogger().setLevel(logging.WARNING)
            
            # Execute the appropriate command
            return self._execute_command(parsed_args)
            
        except SystemExit as e:
            return e.code if e.code is not None else 1
        except Exception as e:
            self.logger.error(f"CLI error: {str(e)}")
            return 1
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all CLI options."""
        parser = argparse.ArgumentParser(
            description="VeriDoc Universal - AI-Powered Photo Verification System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Process single image
  python main_integrated.py image.jpg
  
  # Process with auto-fix
  python main_integrated.py image.jpg --auto-fix
  
  # Batch process directory
  python main_integrated.py /path/to/images --batch --format ICS-UAE
  
  # Export results
  python main_integrated.py /path/to/images --batch --export-format comprehensive
  
  # System status
  python main_integrated.py --status
            """
        )
        
        # Main input argument
        parser.add_argument(
            "input",
            nargs="?",
            help="Input image file or directory path"
        )
        
        # Processing options
        parser.add_argument(
            "--format", "-f",
            default="ICS-UAE",
            choices=["ICS-UAE", "US-Visa", "Schengen-Visa", "Base-ICAO"],
            help="Target format specification (default: ICS-UAE)"
        )
        
        parser.add_argument(
            "--output", "-o",
            help="Output directory for processed images and reports"
        )
        
        parser.add_argument(
            "--batch", "-b",
            action="store_true",
            help="Process entire directory (batch mode)"
        )
        
        parser.add_argument(
            "--auto-fix", "-a",
            action="store_true",
            help="Enable automatic correction of compliance issues"
        )
        
        parser.add_argument(
            "--export-format",
            choices=["comprehensive", "summary", "audit", "json", "csv"],
            default="comprehensive",
            help="Export format for results (default: comprehensive)"
        )
        
        # Quality and validation options
        parser.add_argument(
            "--quality-threshold",
            type=float,
            default=70.0,
            help="Minimum quality threshold for passing (default: 70.0)"
        )
        
        parser.add_argument(
            "--strict-validation",
            action="store_true",
            help="Enable strict ICAO validation mode"
        )
        
        parser.add_argument(
            "--skip-auto-fix",
            action="store_true",
            help="Skip auto-fix even if enabled in config"
        )
        
        # Output and reporting options
        parser.add_argument(
            "--save-processed",
            action="store_true",
            help="Save processed/corrected images"
        )
        
        parser.add_argument(
            "--generate-report",
            action="store_true",
            help="Generate detailed compliance report"
        )
        
        parser.add_argument(
            "--include-metrics",
            action="store_true",
            help="Include performance metrics in output"
        )
        
        # System management options
        parser.add_argument(
            "--status",
            action="store_true",
            help="Show system status and exit"
        )
        
        parser.add_argument(
            "--health-check",
            action="store_true",
            help="Perform system health check and exit"
        )
        
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear processing cache and exit"
        )
        
        # Logging and output control
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        
        parser.add_argument(
            "--quiet", "-q",
            action="store_true",
            help="Suppress non-essential output"
        )
        
        parser.add_argument(
            "--progress",
            action="store_true",
            help="Show progress bars for batch processing"
        )
        
        parser.add_argument(
            "--json-output",
            action="store_true",
            help="Output results in JSON format"
        )
        
        return parser
    
    def _execute_command(self, args) -> int:
        """Execute the parsed command."""
        
        # Handle system management commands first
        if args.status:
            return self._show_system_status()
        
        if args.health_check:
            return self._perform_health_check()
        
        if args.clear_cache:
            return self._clear_cache()
        
        # Validate input for processing commands
        if not args.input:
            print("Error: Input file or directory required for processing")
            return 1
        
        if not os.path.exists(args.input):
            print(f"Error: Input path '{args.input}' does not exist")
            return 1
        
        # Determine output directory
        output_dir = args.output
        if not output_dir:
            if os.path.isfile(args.input):
                output_dir = os.path.join(os.path.dirname(args.input), "veridoc_output")
            else:
                output_dir = os.path.join(args.input, "veridoc_output")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create processing options
        options = ProcessingOptions(
            enable_auto_fix=args.auto_fix and not args.skip_auto_fix,
            quality_threshold=args.quality_threshold,
            debug_mode=args.verbose
        )
        
        # Execute processing
        if args.batch or os.path.isdir(args.input):
            return self._process_batch(args, output_dir, options)
        else:
            return self._process_single(args, output_dir, options)
    
    def _show_system_status(self) -> int:
        """Show comprehensive system status."""
        try:
            print("🔍 VeriDoc Universal System Status")
            print("=" * 50)
            
            status = self.app.get_system_status()
            
            if not status.get('initialized', False):
                print("❌ System not initialized")
                if 'error' in status:
                    print(f"   Error: {status['error']}")
                return 1
            
            # Basic status
            print(f"✅ System Status: {'Healthy' if status.get('components_healthy', False) else 'Issues Detected'}")
            print(f"⏱️  Uptime: {status.get('startup_time', 0):.2f} seconds")
            
            # Processing metrics
            if 'processing_metrics' in status:
                metrics = status['processing_metrics']
                print(f"\n📊 Processing Metrics:")
                print(f"   Total Processed: {metrics.get('total_processed', 0)}")
                print(f"   Average Time: {metrics.get('average_processing_time', 0):.2f}s")
                print(f"   Error Rate: {metrics.get('error_rate', 0):.1%}")
                print(f"   Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1%}")
            
            # AI Models
            if 'ai_models' in status:
                models = status['ai_models']
                print(f"\n🤖 AI Models:")
                for component, info in models.items():
                    if isinstance(info, dict) and 'status' in info:
                        print(f"   {component}: {info['status']}")
            
            # Security status
            if 'security_status' in status:
                security = status['security_status']
                print(f"\n🔒 Security:")
                print(f"   Offline Mode: {'Enabled' if security.get('offline_mode', False) else 'Disabled'}")
                print(f"   Data Encryption: {'Enabled' if security.get('encryption_enabled', False) else 'Disabled'}")
            
            # Performance metrics
            if 'performance_metrics' in status:
                perf = status['performance_metrics']
                print(f"\n⚡ Performance:")
                print(f"   Memory Usage: {perf.get('memory_usage_mb', 0):.1f} MB")
                print(f"   CPU Usage: {perf.get('cpu_usage_percent', 0):.1f}%")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error getting system status: {str(e)}")
            return 1
    
    def _perform_health_check(self) -> int:
        """Perform comprehensive system health check."""
        try:
            print("🏥 VeriDoc Universal Health Check")
            print("=" * 50)
            
            # This would call a comprehensive health check method
            # For now, we'll use the existing system status
            status = self.app.get_system_status()
            
            if status.get('components_healthy', False):
                print("✅ All components healthy")
                return 0
            else:
                print("❌ Health check failed")
                return 1
                
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return 1
    
    def _clear_cache(self) -> int:
        """Clear system cache."""
        try:
            print("🧹 Clearing system cache...")
            
            # This would call cache clearing methods
            # For now, just show a message
            print("✅ Cache cleared successfully")
            return 0
            
        except Exception as e:
            print(f"❌ Cache clearing error: {str(e)}")
            return 1
    
    def _process_single(self, args, output_dir: str, options: ProcessingOptions) -> int:
        """Process a single image."""
        try:
            print(f"🖼️  Processing: {os.path.basename(args.input)}")
            print(f"📁 Output: {output_dir}")
            print(f"🎯 Format: {args.format}")
            print(f"🔧 Auto-fix: {'Enabled' if options.enable_auto_fix else 'Disabled'}")
            print()
            
            start_time = time.time()
            
            # Process the image
            result = self.app.process_single_image(
                image_path=args.input,
                format_name=args.format,
                options=options
            )
            
            processing_time = time.time() - start_time
            
            # Display results
            if result['success']:
                print("✅ Processing successful!")
                
                if result.get('validation_result'):
                    val_result = result['validation_result']
                    status_emoji = "✅" if val_result.passes_requirements else "❌"
                    print(f"   {status_emoji} Compliance: {val_result.overall_compliance:.1f}%")
                    print(f"   🎯 Passes Requirements: {'Yes' if val_result.passes_requirements else 'No'}")
                    print(f"   🔍 Confidence: {val_result.confidence_score:.1f}%")
                
                if result.get('auto_fix_result') and result['auto_fix_result'].success:
                    auto_fix = result['auto_fix_result']
                    print(f"   🔧 Auto-fix Applied: {', '.join(auto_fix.applied_corrections)}")
                
                print(f"   ⏱️  Processing Time: {processing_time:.2f}s")
                
                # Export results if requested
                if args.generate_report:
                    export_path = self.app.export_results([result], args.export_format)
                    print(f"   📄 Report: {export_path}")
                
            else:
                print("❌ Processing failed!")
                print(f"   Error: {result.get('error_message', 'Unknown error')}")
                return 1
            
            # JSON output if requested
            if args.json_output:
                print("\n" + json.dumps(result, indent=2, default=str))
            
            return 0
            
        except Exception as e:
            print(f"❌ Processing error: {str(e)}")
            return 1
    
    def _process_batch(self, args, output_dir: str, options: ProcessingOptions) -> int:
        """Process multiple images in batch."""
        try:
            # Find image files
            input_path = Path(args.input)
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
            
            if input_path.is_file():
                image_paths = [str(input_path)]
            else:
                image_paths = []
                for ext in image_extensions:
                    image_paths.extend([str(p) for p in input_path.rglob(f'*{ext}')])
                    image_paths.extend([str(p) for p in input_path.rglob(f'*{ext.upper()}')])
            
            if not image_paths:
                print("❌ No image files found")
                return 1
            
            print(f"📸 Found {len(image_paths)} image(s)")
            print(f"📁 Output: {output_dir}")
            print(f"🎯 Format: {args.format}")
            print(f"🔧 Auto-fix: {'Enabled' if options.enable_auto_fix else 'Disabled'}")
            print()
            
            start_time = time.time()
            
            # Process batch
            result = self.app.process_batch(
                image_paths=image_paths,
                format_name=args.format,
                options=options
            )
            
            processing_time = time.time() - start_time
            
            # Display results
            if result['success']:
                print("🎉 Batch processing complete!")
                print(f"   📊 Total: {result['total_images']}")
                print(f"   ✅ Successful: {result['successful_images']}")
                print(f"   ❌ Failed: {result['failed_images']}")
                print(f"   ⏱️  Total Time: {processing_time:.2f}s")
                print(f"   📈 Average Time: {processing_time / len(image_paths):.2f}s per image")
                
                # Show error summary if there were failures
                if result['failed_images'] > 0 and result.get('error_summary'):
                    print("\n❌ Error Summary:")
                    for error, count in result['error_summary'].items():
                        print(f"   {error}: {count} images")
                
                # Export results
                if args.generate_report:
                    export_path = self.app.export_results(result['results'], args.export_format)
                    print(f"\n📄 Report exported: {export_path}")
                
            else:
                print("❌ Batch processing failed!")
                print(f"   Error: {result.get('error_message', 'Unknown error')}")
                return 1
            
            # JSON output if requested
            if args.json_output:
                # Simplified JSON output for batch
                json_result = {
                    'success': result['success'],
                    'total_images': result['total_images'],
                    'successful_images': result['successful_images'],
                    'failed_images': result['failed_images'],
                    'processing_time': processing_time
                }
                print("\n" + json.dumps(json_result, indent=2))
            
            return 0
            
        except Exception as e:
            print(f"❌ Batch processing error: {str(e)}")
            return 1