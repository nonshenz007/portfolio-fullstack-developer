"""
Automated Test Suite for Continuous Integration
Comprehensive test suite designed for CI/CD pipeline execution.
"""

import pytest
import numpy as np
import cv2
import json
import time
import tempfile
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, List, Any
import psutil
import os

# Import all test modules for comprehensive coverage
from tests.test_comprehensive_suite import *
from tests.test_integration_pipeline import *
from tests.test_icao_compliance import *
from tests.test_performance_benchmarks import *
from tests.test_accuracy_validation import *
from tests.test_edge_cases_error_handling import *


class CITestRunner:
    """Test runner optimized for CI/CD environments"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.coverage_data = {}
        self.start_time = None
        self.end_time = None
    
    def run_test_suite(self, test_categories: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive test suite for CI"""
        self.start_time = time.time()
        
        if test_categories is None:
            test_categories = [
                'unit_tests',
                'integration_tests',
                'compliance_tests',
                'performance_tests',
                'accuracy_tests',
                'edge_case_tests'
            ]
        
        results = {}
        
        for category in test_categories:
            print(f"Running {category}...")
            category_result = self._run_test_category(category)
            results[category] = category_result
            
            # Early exit on critical failures
            if category_result['critical_failures'] > 0:
                print(f"Critical failures detected in {category}, stopping execution")
                break
        
        self.end_time = time.time()
        self.test_results = results
        
        return self._generate_ci_report()
    
    def _run_test_category(self, category: str) -> Dict[str, Any]:
        """Run specific test category"""
        category_mapping = {
            'unit_tests': self._run_unit_tests,
            'integration_tests': self._run_integration_tests,
            'compliance_tests': self._run_compliance_tests,
            'performance_tests': self._run_performance_tests,
            'accuracy_tests': self._run_accuracy_tests,
            'edge_case_tests': self._run_edge_case_tests
        }
        
        if category not in category_mapping:
            return {'error': f'Unknown test category: {category}'}
        
        try:
            return category_mapping[category]()
        except Exception as e:
            return {
                'error': str(e),
                'critical_failures': 1,
                'passed': 0,
                'failed': 1,
                'skipped': 0
            }
    
    def _run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        return self._execute_pytest_category('test_comprehensive_suite.py')
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        return self._execute_pytest_category('test_integration_pipeline.py')
    
    def _run_compliance_tests(self) -> Dict[str, Any]:
        """Run ICAO compliance tests"""
        return self._execute_pytest_category('test_icao_compliance.py')
    
    def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        return self._execute_pytest_category('test_performance_benchmarks.py')
    
    def _run_accuracy_tests(self) -> Dict[str, Any]:
        """Run accuracy validation tests"""
        return self._execute_pytest_category('test_accuracy_validation.py')
    
    def _run_edge_case_tests(self) -> Dict[str, Any]:
        """Run edge case tests"""
        return self._execute_pytest_category('test_edge_cases_error_handling.py')
    
    def _execute_pytest_category(self, test_file: str) -> Dict[str, Any]:
        """Execute pytest for specific test file"""
        try:
            # Run pytest with JSON report
            cmd = [
                sys.executable, '-m', 'pytest',
                f'tests/{test_file}',
                '--json-report',
                '--json-report-file=test_report.json',
                '-v',
                '--tb=short'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse results
            if Path('test_report.json').exists():
                with open('test_report.json', 'r') as f:
                    report_data = json.load(f)
                
                return {
                    'passed': report_data.get('summary', {}).get('passed', 0),
                    'failed': report_data.get('summary', {}).get('failed', 0),
                    'skipped': report_data.get('summary', {}).get('skipped', 0),
                    'critical_failures': report_data.get('summary', {}).get('failed', 0),
                    'duration': report_data.get('duration', 0),
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                return {
                    'passed': 0,
                    'failed': 1,
                    'skipped': 0,
                    'critical_failures': 1,
                    'duration': 0,
                    'error': 'No test report generated'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'critical_failures': 1,
                'duration': 300,
                'error': 'Test execution timeout'
            }
        except Exception as e:
            return {
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'critical_failures': 1,
                'duration': 0,
                'error': str(e)
            }
    
    def _generate_ci_report(self) -> Dict[str, Any]:
        """Generate comprehensive CI report"""
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        # Aggregate results
        total_passed = sum(result.get('passed', 0) for result in self.test_results.values())
        total_failed = sum(result.get('failed', 0) for result in self.test_results.values())
        total_skipped = sum(result.get('skipped', 0) for result in self.test_results.values())
        total_critical = sum(result.get('critical_failures', 0) for result in self.test_results.values())
        
        # Calculate success rate
        total_tests = total_passed + total_failed + total_skipped
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Determine overall status
        if total_critical > 0:
            status = 'CRITICAL_FAILURE'
        elif total_failed > 0:
            status = 'FAILURE'
        elif total_passed > 0:
            status = 'SUCCESS'
        else:
            status = 'NO_TESTS'
        
        return {
            'status': status,
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'skipped': total_skipped,
                'critical_failures': total_critical,
                'success_rate': success_rate,
                'duration': total_duration
            },
            'category_results': self.test_results,
            'performance_metrics': self.performance_metrics,
            'coverage_data': self.coverage_data,
            'timestamp': time.time(),
            'environment': self._get_environment_info()
        }
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get CI environment information"""
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            'disk_free': psutil.disk_usage('.').free / 1024 / 1024 / 1024,  # GB
            'ci_environment': os.environ.get('CI', 'false'),
            'github_actions': os.environ.get('GITHUB_ACTIONS', 'false')
        }


class TestCIIntegration:
    """Test CI/CD integration functionality"""
    
    def test_ci_test_runner_initialization(self):
        """Test CI test runner initialization"""
        runner = CITestRunner()
        assert runner is not None
        assert runner.test_results == {}
        assert runner.performance_metrics == {}
    
    def test_environment_info_collection(self):
        """Test environment information collection"""
        runner = CITestRunner()
        env_info = runner._get_environment_info()
        
        assert 'python_version' in env_info
        assert 'platform' in env_info
        assert 'cpu_count' in env_info
        assert 'memory_total' in env_info
        assert env_info['cpu_count'] > 0
        assert env_info['memory_total'] > 0
    
    def test_test_category_execution(self):
        """Test individual test category execution"""
        runner = CITestRunner()
        
        # Mock pytest execution
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout='', stderr='', returncode=0)
            
            # Mock test report
            test_report = {
                'summary': {
                    'passed': 10,
                    'failed': 0,
                    'skipped': 1
                },
                'duration': 5.2
            }
            
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('builtins.open', mock_open_json(test_report)):
                
                result = runner._run_unit_tests()
                
                assert result['passed'] == 10
                assert result['failed'] == 0
                assert result['skipped'] == 1
                assert result['critical_failures'] == 0
    
    def test_ci_report_generation(self):
        """Test CI report generation"""
        runner = CITestRunner()
        runner.start_time = time.time()
        runner.end_time = runner.start_time + 30
        
        # Mock test results
        runner.test_results = {
            'unit_tests': {'passed': 15, 'failed': 0, 'skipped': 2, 'critical_failures': 0},
            'integration_tests': {'passed': 8, 'failed': 1, 'skipped': 0, 'critical_failures': 0},
            'compliance_tests': {'passed': 12, 'failed': 0, 'skipped': 1, 'critical_failures': 0}
        }
        
        report = runner._generate_ci_report()
        
        assert report['status'] == 'FAILURE'  # Due to 1 failed test
        assert report['summary']['total_tests'] == 39
        assert report['summary']['passed'] == 35
        assert report['summary']['failed'] == 1
        assert report['summary']['skipped'] == 3
        assert report['summary']['success_rate'] > 85
        assert 'environment' in report


class TestCIPerformanceMonitoring:
    """Test performance monitoring in CI environment"""
    
    def test_performance_threshold_validation(self):
        """Test performance threshold validation for CI"""
        # Define performance thresholds for CI
        thresholds = {
            'max_test_duration': 600,  # 10 minutes max
            'max_memory_usage': 2048,  # 2GB max
            'min_success_rate': 95,    # 95% min success rate
            'max_critical_failures': 0  # No critical failures allowed
        }
        
        # Mock test results
        test_results = {
            'duration': 450,
            'peak_memory_mb': 1200,
            'success_rate': 97.5,
            'critical_failures': 0
        }
        
        # Validate against thresholds
        for metric, threshold in thresholds.items():
            if metric.startswith('max_'):
                actual_metric = metric.replace('max_', '')
                if actual_metric == 'test_duration':
                    assert test_results['duration'] <= threshold
                elif actual_metric == 'memory_usage':
                    assert test_results['peak_memory_mb'] <= threshold
                elif actual_metric == 'critical_failures':
                    assert test_results['critical_failures'] <= threshold
            elif metric.startswith('min_'):
                actual_metric = metric.replace('min_', '')
                if actual_metric == 'success_rate':
                    assert test_results['success_rate'] >= threshold
    
    def test_ci_resource_monitoring(self):
        """Test resource monitoring during CI execution"""
        # Monitor system resources
        initial_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Simulate test execution
        time.sleep(0.1)
        
        # Check resource usage
        final_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        final_cpu = psutil.cpu_percent(interval=1)
        
        memory_increase = final_memory - initial_memory
        
        # Resource usage should be reasonable
        assert memory_increase < 500  # Less than 500MB increase
        assert final_cpu < 90  # Less than 90% CPU usage
    
    def test_ci_timeout_handling(self):
        """Test timeout handling in CI environment"""
        runner = CITestRunner()
        
        # Mock long-running test
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('pytest', 300)
            
            result = runner._execute_pytest_category('test_long_running.py')
            
            assert result['critical_failures'] == 1
            assert 'timeout' in result['error'].lower()
            assert result['duration'] == 300


class TestCIReporting:
    """Test CI reporting functionality"""
    
    def test_junit_xml_generation(self):
        """Test JUnit XML report generation for CI"""
        # Mock test results
        test_results = [
            {'name': 'test_face_detection', 'status': 'passed', 'duration': 1.2},
            {'name': 'test_icao_validation', 'status': 'failed', 'duration': 2.1, 'error': 'Assertion failed'},
            {'name': 'test_quality_assessment', 'status': 'skipped', 'duration': 0.0}
        ]
        
        # Generate JUnit XML
        junit_xml = self._generate_junit_xml(test_results)
        
        assert '<testsuite' in junit_xml
        assert 'tests="3"' in junit_xml
        assert 'failures="1"' in junit_xml
        assert 'skipped="1"' in junit_xml
        assert '<testcase name="test_face_detection"' in junit_xml
        assert '<failure' in junit_xml
    
    def test_coverage_report_generation(self):
        """Test coverage report generation"""
        # Mock coverage data
        coverage_data = {
            'total_lines': 1000,
            'covered_lines': 850,
            'coverage_percentage': 85.0,
            'missing_lines': ['ai/ai_engine.py:45-50', 'validation/icao_validator.py:120']
        }
        
        coverage_report = self._generate_coverage_report(coverage_data)
        
        assert coverage_report['coverage_percentage'] == 85.0
        assert coverage_report['total_lines'] == 1000
        assert coverage_report['covered_lines'] == 850
        assert len(coverage_report['missing_lines']) == 2
    
    def test_slack_notification_format(self):
        """Test Slack notification format for CI results"""
        # Mock CI results
        ci_results = {
            'status': 'SUCCESS',
            'summary': {
                'total_tests': 150,
                'passed': 148,
                'failed': 2,
                'success_rate': 98.7,
                'duration': 420
            }
        }
        
        slack_message = self._format_slack_notification(ci_results)
        
        assert 'SUCCESS' in slack_message
        assert '148/150' in slack_message
        assert '98.7%' in slack_message
        assert '7m 0s' in slack_message  # 420 seconds formatted
    
    def _generate_junit_xml(self, test_results: List[Dict]) -> str:
        """Generate JUnit XML format"""
        total_tests = len(test_results)
        failures = sum(1 for t in test_results if t['status'] == 'failed')
        skipped = sum(1 for t in test_results if t['status'] == 'skipped')
        duration = sum(t['duration'] for t in test_results)
        
        xml = f'<testsuite tests="{total_tests}" failures="{failures}" skipped="{skipped}" time="{duration}">\n'
        
        for test in test_results:
            xml += f'  <testcase name="{test["name"]}" time="{test["duration"]}"'
            
            if test['status'] == 'failed':
                xml += f'>\n    <failure message="{test.get("error", "Test failed")}"/>\n  </testcase>\n'
            elif test['status'] == 'skipped':
                xml += '>\n    <skipped/>\n  </testcase>\n'
            else:
                xml += '/>\n'
        
        xml += '</testsuite>'
        return xml
    
    def _generate_coverage_report(self, coverage_data: Dict) -> Dict:
        """Generate coverage report"""
        return {
            'coverage_percentage': coverage_data['coverage_percentage'],
            'total_lines': coverage_data['total_lines'],
            'covered_lines': coverage_data['covered_lines'],
            'missing_lines': coverage_data['missing_lines'],
            'status': 'GOOD' if coverage_data['coverage_percentage'] >= 80 else 'POOR'
        }
    
    def _format_slack_notification(self, ci_results: Dict) -> str:
        """Format Slack notification message"""
        status = ci_results['status']
        summary = ci_results['summary']
        
        # Format duration
        duration_seconds = int(summary['duration'])
        duration_minutes = duration_seconds // 60
        duration_seconds = duration_seconds % 60
        duration_str = f"{duration_minutes}m {duration_seconds}s"
        
        # Status emoji
        emoji = "✅" if status == "SUCCESS" else "❌"
        
        message = f"{emoji} CI Build {status}\n"
        message += f"Tests: {summary['passed']}/{summary['total_tests']} passed "
        message += f"({summary['success_rate']:.1f}%)\n"
        message += f"Duration: {duration_str}"
        
        if summary['failed'] > 0:
            message += f"\nFailed: {summary['failed']}"
        
        return message


class TestCIArtifacts:
    """Test CI artifact generation and management"""
    
    def test_test_artifact_collection(self):
        """Test collection of test artifacts"""
        artifacts = {
            'test_reports': ['junit.xml', 'coverage.xml'],
            'performance_reports': ['performance_benchmark.json'],
            'log_files': ['test_execution.log', 'error.log'],
            'screenshots': ['failed_test_screenshot.png']
        }
        
        # Verify artifact structure
        assert 'test_reports' in artifacts
        assert 'performance_reports' in artifacts
        assert 'log_files' in artifacts
        
        # Verify required artifacts exist
        required_artifacts = ['junit.xml', 'coverage.xml']
        for artifact in required_artifacts:
            assert artifact in artifacts['test_reports']
    
    def test_artifact_upload_preparation(self):
        """Test preparation of artifacts for upload"""
        # Mock artifact files
        artifact_files = [
            'test_results/junit.xml',
            'test_results/coverage.xml',
            'test_results/performance.json',
            'logs/test_execution.log'
        ]
        
        # Prepare for upload
        upload_manifest = self._prepare_artifact_upload(artifact_files)
        
        assert 'files' in upload_manifest
        assert 'metadata' in upload_manifest
        assert len(upload_manifest['files']) == len(artifact_files)
        assert upload_manifest['metadata']['total_size'] > 0
    
    def _prepare_artifact_upload(self, files: List[str]) -> Dict:
        """Prepare artifacts for upload"""
        total_size = 0
        file_info = []
        
        for file_path in files:
            # Mock file size calculation
            mock_size = len(file_path) * 100  # Mock size based on path length
            total_size += mock_size
            
            file_info.append({
                'path': file_path,
                'size': mock_size,
                'type': Path(file_path).suffix
            })
        
        return {
            'files': file_info,
            'metadata': {
                'total_size': total_size,
                'file_count': len(files),
                'timestamp': time.time()
            }
        }


def mock_open_json(data):
    """Helper function to mock JSON file opening"""
    from unittest.mock import mock_open
    return mock_open(read_data=json.dumps(data))


# CI Entry Point
def run_ci_tests():
    """Main entry point for CI test execution"""
    runner = CITestRunner()
    
    # Run all test categories
    results = runner.run_test_suite()
    
    # Generate reports
    with open('ci_test_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\nCI Test Results:")
    print(f"Status: {results['status']}")
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
    print(f"Duration: {results['summary']['duration']:.1f}s")
    
    # Exit with appropriate code
    if results['status'] in ['SUCCESS']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    # Check if running in CI mode
    if len(sys.argv) > 1 and sys.argv[1] == '--ci':
        run_ci_tests()
    else:
        # Run as pytest
        pytest.main([__file__, "-v"])