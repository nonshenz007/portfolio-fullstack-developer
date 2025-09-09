"""
Batch Analyzer for comprehensive analysis of batch processing results.
Provides statistical analysis, failure patterns, and trend identification.
"""

import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter, defaultdict
import statistics


class BatchAnalyzer:
    """
    Analyzes batch processing results to identify patterns, trends, and issues.
    Provides comprehensive statistical analysis and failure pattern detection.
    """
    
    def __init__(self):
        """Initialize batch analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_batch_results(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of batch processing results.
        
        Args:
            batch_results: List of individual processing results
            
        Returns:
            Dictionary containing comprehensive batch analysis
        """
        try:
            analysis = {
                'analysis_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_results': len(batch_results),
                    'analysis_version': '1.0'
                },
                'summary_statistics': self._calculate_summary_statistics(batch_results),
                'compliance_breakdown': self._analyze_compliance_breakdown(batch_results),
                'failure_analysis': self._analyze_failures(batch_results),
                'quality_trends': self._analyze_quality_trends(batch_results),
                'performance_metrics': self._analyze_performance_metrics(batch_results),
                'validation_patterns': self._analyze_validation_patterns(batch_results),
                'batch_recommendations': self._generate_batch_recommendations(batch_results),
                'individual_summaries': self._create_individual_summaries(batch_results)
            }
            
            self.logger.info(f"Batch analysis completed for {len(batch_results)} results")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Batch analysis failed: {str(e)}")
            return self._create_empty_analysis()
    
    def _calculate_summary_statistics(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall summary statistics."""
        total_images = len(batch_results)
        successful_images = sum(1 for result in batch_results if result.get('success', False))
        failed_images = total_images - successful_images
        
        # Calculate compliance scores for successful images
        compliance_scores = [
            result.get('overall_compliance', 0) 
            for result in batch_results 
            if result.get('success', False) and 'overall_compliance' in result
        ]
        
        # Calculate processing times
        processing_times = [
            result.get('processing_time', 0) 
            for result in batch_results 
            if 'processing_time' in result
        ]
        
        # Calculate pass/fail rates
        passing_images = sum(
            1 for result in batch_results 
            if result.get('passes_requirements', False)
        )
        
        return {
            'total_images': total_images,
            'successful_images': successful_images,
            'failed_images': failed_images,
            'success_rate': (successful_images / total_images * 100) if total_images > 0 else 0,
            'passing_images': passing_images,
            'pass_rate': (passing_images / total_images * 100) if total_images > 0 else 0,
            'avg_compliance_score': statistics.mean(compliance_scores) if compliance_scores else 0,
            'median_compliance_score': statistics.median(compliance_scores) if compliance_scores else 0,
            'min_compliance_score': min(compliance_scores) if compliance_scores else 0,
            'max_compliance_score': max(compliance_scores) if compliance_scores else 0,
            'compliance_std_dev': statistics.stdev(compliance_scores) if len(compliance_scores) > 1 else 0,
            'avg_processing_time': statistics.mean(processing_times) if processing_times else 0,
            'total_processing_time': sum(processing_times) if processing_times else 0,
            'min_processing_time': min(processing_times) if processing_times else 0,
            'max_processing_time': max(processing_times) if processing_times else 0
        }
    
    def _analyze_compliance_breakdown(self, batch_results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze compliance score distribution."""
        compliance_ranges = {
            'excellent_90_100': 0,
            'good_80_89': 0,
            'acceptable_70_79': 0,
            'poor_60_69': 0,
            'failing_below_60': 0,
            'processing_failed': 0
        }
        
        for result in batch_results:
            if not result.get('success', False):
                compliance_ranges['processing_failed'] += 1
                continue
            
            compliance_score = result.get('overall_compliance', 0)
            
            if compliance_score >= 90:
                compliance_ranges['excellent_90_100'] += 1
            elif compliance_score >= 80:
                compliance_ranges['good_80_89'] += 1
            elif compliance_score >= 70:
                compliance_ranges['acceptable_70_79'] += 1
            elif compliance_score >= 60:
                compliance_ranges['poor_60_69'] += 1
            else:
                compliance_ranges['failing_below_60'] += 1
        
        return compliance_ranges
    
    def _analyze_failures(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze failure patterns and common issues."""
        failed_results = [
            result for result in batch_results 
            if not result.get('success', False) or not result.get('passes_requirements', False)
        ]
        
        # Collect all compliance issues
        all_issues = []
        for result in batch_results:
            issues = result.get('compliance_issues', [])
            all_issues.extend(issues)
        
        # Count issue types
        issue_counter = Counter()
        severity_counter = Counter()
        category_counter = Counter()
        
        for issue in all_issues:
            issue_desc = issue.get('description', 'Unknown issue')
            issue_category = issue.get('category', 'unknown')
            issue_severity = issue.get('severity', 'unknown')
            
            issue_counter[issue_desc] += 1
            category_counter[issue_category] += 1
            severity_counter[issue_severity] += 1
        
        # Analyze error messages
        error_messages = [
            result.get('error_message', '') 
            for result in batch_results 
            if result.get('error_message')
        ]
        error_counter = Counter(error_messages)
        
        # Find common failure patterns
        common_issues = [
            {'issue': issue, 'count': count, 'percentage': (count / len(batch_results)) * 100}
            for issue, count in issue_counter.most_common(10)
        ]
        
        return {
            'total_failed_images': len(failed_results),
            'failure_rate': (len(failed_results) / len(batch_results) * 100) if batch_results else 0,
            'common_issues': common_issues,
            'issue_categories': dict(category_counter.most_common()),
            'issue_severities': dict(severity_counter.most_common()),
            'common_errors': dict(error_counter.most_common(5)),
            'failure_patterns': self._identify_failure_patterns(failed_results)
        }
    
    def _analyze_quality_trends(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality metric trends across the batch."""
        quality_metrics = defaultdict(list)
        
        # Collect quality metrics
        for result in batch_results:
            if result.get('success', False):
                metrics = result.get('quality_metrics', {})
                for metric_name, value in metrics.items():
                    if isinstance(value, (int, float)):
                        quality_metrics[metric_name].append(value)
        
        # Calculate trends for each metric
        trends = {}
        for metric_name, values in quality_metrics.items():
            if values:
                trends[metric_name] = {
                    'average': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                    'count': len(values),
                    'trend_direction': self._calculate_trend_direction(values)
                }
        
        return trends
    
    def _analyze_performance_metrics(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze processing performance metrics."""
        processing_times = []
        memory_usage = []
        ai_model_performance = defaultdict(list)
        
        for result in batch_results:
            # Processing times
            if 'processing_time' in result:
                processing_times.append(result['processing_time'])
            
            # Memory usage if available
            processing_metrics = result.get('processing_metrics', {})
            if 'memory_usage' in processing_metrics:
                memory_usage.append(processing_metrics['memory_usage'])
            
            # AI model performance
            models_used = processing_metrics.get('models_used', [])
            for model in models_used:
                if isinstance(model, dict) and 'performance' in model:
                    ai_model_performance[model.get('name', 'unknown')].append(
                        model['performance']
                    )
        
        performance_analysis = {
            'processing_time_analysis': self._analyze_metric_distribution(processing_times),
            'throughput': len(batch_results) / sum(processing_times) if processing_times else 0,
            'performance_consistency': self._calculate_performance_consistency(processing_times)
        }
        
        if memory_usage:
            performance_analysis['memory_usage_analysis'] = self._analyze_metric_distribution(memory_usage)
        
        if ai_model_performance:
            performance_analysis['ai_model_performance'] = {
                model: self._analyze_metric_distribution(performances)
                for model, performances in ai_model_performance.items()
            }
        
        return performance_analysis
    
    def _analyze_validation_patterns(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze validation rule performance patterns."""
        rule_performance = defaultdict(list)
        rule_failures = defaultdict(int)
        
        for result in batch_results:
            validation_results = result.get('validation_results', {})
            
            for rule_name, rule_result in validation_results.items():
                if isinstance(rule_result, dict):
                    score = rule_result.get('score', 0)
                    passes = rule_result.get('passes', False)
                    
                    rule_performance[rule_name].append(score)
                    if not passes:
                        rule_failures[rule_name] += 1
        
        # Analyze each rule
        rule_analysis = {}
        for rule_name, scores in rule_performance.items():
            if scores:
                failure_rate = (rule_failures[rule_name] / len(scores)) * 100
                
                rule_analysis[rule_name] = {
                    'average_score': statistics.mean(scores),
                    'median_score': statistics.median(scores),
                    'min_score': min(scores),
                    'max_score': max(scores),
                    'failure_rate': failure_rate,
                    'total_evaluations': len(scores),
                    'difficulty_level': self._assess_rule_difficulty(scores, failure_rate)
                }
        
        return {
            'rule_performance': rule_analysis,
            'most_challenging_rules': sorted(
                rule_analysis.items(),
                key=lambda x: x[1]['failure_rate'],
                reverse=True
            )[:5],
            'best_performing_rules': sorted(
                rule_analysis.items(),
                key=lambda x: x[1]['average_score'],
                reverse=True
            )[:5]
        }
    
    def _generate_batch_recommendations(self, batch_results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on batch analysis."""
        recommendations = []
        
        # Analyze overall performance
        total_images = len(batch_results)
        successful_images = sum(1 for result in batch_results if result.get('success', False))
        passing_images = sum(1 for result in batch_results if result.get('passes_requirements', False))
        
        success_rate = (successful_images / total_images * 100) if total_images > 0 else 0
        pass_rate = (passing_images / total_images * 100) if total_images > 0 else 0
        
        # Success rate recommendations
        if success_rate < 80:
            recommendations.append(
                f"Low processing success rate ({success_rate:.1f}%). "
                "Consider checking image quality and format compatibility."
            )
        
        # Pass rate recommendations
        if pass_rate < 60:
            recommendations.append(
                f"Low compliance pass rate ({pass_rate:.1f}%). "
                "Review image capture guidelines and quality requirements."
            )
        
        # Analyze common issues
        all_issues = []
        for result in batch_results:
            all_issues.extend(result.get('compliance_issues', []))
        
        issue_counter = Counter(issue.get('category', 'unknown') for issue in all_issues)
        
        # Category-specific recommendations
        for category, count in issue_counter.most_common(3):
            percentage = (count / len(all_issues) * 100) if all_issues else 0
            
            if category == 'glasses_compliance' and percentage > 20:
                recommendations.append(
                    "High rate of glasses compliance issues. "
                    "Ensure subjects remove tinted glasses and minimize glare."
                )
            elif category == 'lighting_compliance' and percentage > 20:
                recommendations.append(
                    "Frequent lighting issues detected. "
                    "Improve lighting setup to reduce shadows and ensure even illumination."
                )
            elif category == 'background_compliance' and percentage > 20:
                recommendations.append(
                    "Background compliance issues common. "
                    "Use plain white backgrounds and ensure uniformity."
                )
            elif category == 'photo_quality' and percentage > 20:
                recommendations.append(
                    "Image quality issues prevalent. "
                    "Check camera settings, focus, and resolution requirements."
                )
        
        # Performance recommendations
        processing_times = [
            result.get('processing_time', 0) 
            for result in batch_results 
            if 'processing_time' in result
        ]
        
        if processing_times:
            avg_time = statistics.mean(processing_times)
            if avg_time > 5.0:
                recommendations.append(
                    f"Average processing time is high ({avg_time:.1f}s). "
                    "Consider optimizing image sizes or system resources."
                )
        
        # Quality trend recommendations
        compliance_scores = [
            result.get('overall_compliance', 0) 
            for result in batch_results 
            if result.get('success', False)
        ]
        
        if compliance_scores:
            avg_compliance = statistics.mean(compliance_scores)
            if avg_compliance < 70:
                recommendations.append(
                    f"Average compliance score is low ({avg_compliance:.1f}%). "
                    "Review capture procedures and consider additional training."
                )
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _create_individual_summaries(self, batch_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create summary for each individual result."""
        summaries = []
        
        for i, result in enumerate(batch_results):
            summary = {
                'index': i,
                'image_path': result.get('image_path', f'Image_{i+1}'),
                'success': result.get('success', False),
                'passes_requirements': result.get('passes_requirements', False),
                'overall_compliance': result.get('overall_compliance', 0),
                'processing_time': result.get('processing_time', 0),
                'major_issues': []
            }
            
            # Extract major issues
            issues = result.get('compliance_issues', [])
            major_issues = [
                issue.get('description', 'Unknown issue')
                for issue in issues
                if issue.get('severity') in ['critical', 'major']
            ]
            summary['major_issues'] = major_issues[:3]  # Top 3 major issues
            
            summaries.append(summary)
        
        return summaries
    
    def _identify_failure_patterns(self, failed_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify common failure patterns."""
        patterns = []
        
        # Group by similar error messages
        error_groups = defaultdict(list)
        for result in failed_results:
            error_msg = result.get('error_message', 'Unknown error')
            # Simplify error message for grouping
            simplified_error = self._simplify_error_message(error_msg)
            error_groups[simplified_error].append(result)
        
        # Analyze each pattern
        for error_type, results in error_groups.items():
            if len(results) >= 2:  # Only patterns with multiple occurrences
                pattern = {
                    'pattern_type': error_type,
                    'occurrence_count': len(results),
                    'percentage': (len(results) / len(failed_results)) * 100,
                    'common_characteristics': self._find_common_characteristics(results)
                }
                patterns.append(pattern)
        
        return sorted(patterns, key=lambda x: x['occurrence_count'], reverse=True)
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        if len(values) < 3:
            return 'insufficient_data'
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        correlation = np.corrcoef(x, values)[0, 1] if len(values) > 1 else 0
        
        if correlation > 0.3:
            return 'improving'
        elif correlation < -0.3:
            return 'declining'
        else:
            return 'stable'
    
    def _analyze_metric_distribution(self, values: List[float]) -> Dict[str, Any]:
        """Analyze distribution of metric values."""
        if not values:
            return {'count': 0}
        
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'percentile_25': np.percentile(values, 25),
            'percentile_75': np.percentile(values, 75),
            'range': max(values) - min(values)
        }
    
    def _calculate_performance_consistency(self, processing_times: List[float]) -> Dict[str, Any]:
        """Calculate performance consistency metrics."""
        if not processing_times:
            return {'consistency_score': 0}
        
        mean_time = statistics.mean(processing_times)
        std_dev = statistics.stdev(processing_times) if len(processing_times) > 1 else 0
        
        # Coefficient of variation as consistency measure
        cv = (std_dev / mean_time) if mean_time > 0 else 0
        
        # Consistency score (lower CV = higher consistency)
        consistency_score = max(0, 100 - (cv * 100))
        
        return {
            'consistency_score': consistency_score,
            'coefficient_of_variation': cv,
            'mean_processing_time': mean_time,
            'std_deviation': std_dev,
            'consistency_level': self._classify_consistency(consistency_score)
        }
    
    def _assess_rule_difficulty(self, scores: List[float], failure_rate: float) -> str:
        """Assess difficulty level of a validation rule."""
        avg_score = statistics.mean(scores)
        
        if failure_rate > 50 or avg_score < 60:
            return 'very_difficult'
        elif failure_rate > 30 or avg_score < 70:
            return 'difficult'
        elif failure_rate > 15 or avg_score < 80:
            return 'moderate'
        else:
            return 'easy'
    
    def _simplify_error_message(self, error_msg: str) -> str:
        """Simplify error message for pattern grouping."""
        # Remove specific file paths and numbers
        import re
        simplified = re.sub(r'/[^\s]+', '<path>', error_msg)
        simplified = re.sub(r'\d+', '<number>', simplified)
        simplified = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<uuid>', simplified)
        
        return simplified[:100]  # Truncate for grouping
    
    def _find_common_characteristics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find common characteristics among failed results."""
        characteristics = {}
        
        # Common image properties
        image_sizes = [
            result.get('image_size', 0) 
            for result in results 
            if 'image_size' in result
        ]
        if image_sizes:
            characteristics['avg_image_size'] = statistics.mean(image_sizes)
        
        # Common processing times
        processing_times = [
            result.get('processing_time', 0) 
            for result in results 
            if 'processing_time' in result
        ]
        if processing_times:
            characteristics['avg_processing_time'] = statistics.mean(processing_times)
        
        # Common formats
        formats = [
            result.get('format_name', 'unknown') 
            for result in results 
            if 'format_name' in result
        ]
        if formats:
            format_counter = Counter(formats)
            characteristics['most_common_format'] = format_counter.most_common(1)[0][0]
        
        return characteristics
    
    def _classify_consistency(self, consistency_score: float) -> str:
        """Classify consistency level based on score."""
        if consistency_score >= 90:
            return 'excellent'
        elif consistency_score >= 80:
            return 'good'
        elif consistency_score >= 70:
            return 'fair'
        else:
            return 'poor'
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create empty analysis structure for error cases."""
        return {
            'analysis_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_results': 0,
                'analysis_version': '1.0',
                'error': 'Analysis failed'
            },
            'summary_statistics': {},
            'compliance_breakdown': {},
            'failure_analysis': {},
            'quality_trends': {},
            'performance_metrics': {},
            'validation_patterns': {},
            'batch_recommendations': ['Analysis could not be completed due to errors'],
            'individual_summaries': []
        }