#!/usr/bin/env python3
"""
Test runner script for LedgerFlow comprehensive testing framework.
Provides easy interface to run different test suites with quality gates.
"""
import sys
import subprocess
import argparse
import time
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True)
    duration = time.time() - start_time
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully in {duration:.2f}s")
        return True
    else:
        print(f"❌ {description} failed after {duration:.2f}s")
        return False


def main():
    parser = argparse.ArgumentParser(description="LedgerFlow Test Runner")
    parser.add_argument(
        "--suite", 
        choices=["unit", "integration", "property", "performance", "all", "quality"],
        default="all",
        help="Test suite to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--fail-fast", "-x",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--parallel", "-n",
        type=int,
        help="Run tests in parallel (number of workers)"
    )
    
    args = parser.parse_args()
    
    # Build base pytest command
    pytest_cmd = "pytest"
    if args.verbose:
        pytest_cmd += " -v"
    if args.fail_fast:
        pytest_cmd += " -x"
    if args.parallel:
        pytest_cmd += f" -n {args.parallel}"
    
    success = True
    
    # Quality gates (always run first)
    if args.suite in ["all", "quality"]:
        print("\n🔍 Running Quality Gates...")
        
        # Ruff linting
        if not run_command("ruff check app/ tests/", "Ruff Linting"):
            success = False
            if args.fail_fast:
                sys.exit(1)
        
        # Ruff formatting check
        if not run_command("ruff format --check app/ tests/", "Code Formatting Check"):
            success = False
            if args.fail_fast:
                sys.exit(1)
        
        # MyPy type checking
        if not run_command("mypy app/ --strict", "Type Checking"):
            success = False
            if args.fail_fast:
                sys.exit(1)
    
    # Unit tests
    if args.suite in ["unit", "all"]:
        cmd = f'{pytest_cmd} tests/ -m "not slow and not integration and not performance"'
        if args.coverage:
            cmd += " --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=90"
        
        if not run_command(cmd, "Unit Tests"):
            success = False
            if args.fail_fast:
                sys.exit(1)
    
    # Integration tests
    if args.suite in ["integration", "all"]:
        cmd = f'{pytest_cmd} tests/ -m "integration"'
        if not run_command(cmd, "Integration Tests"):
            success = False
            if args.fail_fast:
                sys.exit(1)
    
    # Property-based tests
    if args.suite in ["property", "all"]:
        cmd = f'{pytest_cmd} tests/test_property_based.py -m "property"'
        if not run_command(cmd, "Property-Based Tests"):
            success = False
            if args.fail_fast:
                sys.exit(1)
    
    # Performance tests
    if args.suite in ["performance", "all"]:
        cmd = f'{pytest_cmd} tests/perf/ -m "performance" --tb=short'
        if not run_command(cmd, "Performance Tests"):
            success = False
            if args.fail_fast:
                sys.exit(1)
    
    # Generate coverage report if requested
    if args.coverage and args.suite != "quality":
        run_command(
            "coverage html && coverage report", 
            "Coverage Report Generation"
        )
        print(f"\n📊 Coverage report generated in htmlcov/index.html")
    
    # Final summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests passed successfully!")
        print("✅ Quality gates: PASSED")
        print("✅ Test suites: PASSED")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        print("❌ Check the output above for details")
        sys.exit(1)


if __name__ == "__main__":
    main()