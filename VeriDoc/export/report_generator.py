"""
Report Generator for creating detailed compliance reports in PDF and JSON formats.
Supports both individual image reports and batch processing summaries.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import base64

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import Color, black, red, green, orange
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.platypus.flowables import PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

import cv2
import numpy as np


class ReportGenerator:
    """
    Generates comprehensive compliance reports in PDF and JSON formats.
    Includes detailed validation results, visual annotations, and recommendations.
    """
    
    def __init__(self, config_manager=None):
        """Initialize report generator."""
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not available. PDF generation will be disabled.")
        
        # Report styling configuration
        self.styles = self._setup_report_styles()
        
        # ICAO rule descriptions for detailed reporting
        self.rule_descriptions = {
            'face_detection': 'Primary face detection and positioning validation',
            'glasses_compliance': 'Glasses and eyewear compliance per ICAO standards',
            'head_covering_compliance': 'Head covering and religious exception validation',
            'expression_compliance': 'Facial expression and gaze direction validation',
            'photo_quality': 'Image quality, sharpness, and technical standards',
            'lighting_compliance': 'Lighting uniformity and shadow detection',
            'background_compliance': 'Background color and uniformity validation',
            'geometry_compliance': 'Face positioning and dimensional requirements'
        }
    
    def generate_pdf_report(self, processing_result: Dict[str, Any],
                          image_path: str, export_dir: str,
                          template: Optional[str] = None) -> Optional[str]:
        """
        Generate comprehensive PDF compliance report.
        
        Args:
            processing_result: Complete processing result data
            image_path: Path to original image
            export_dir: Directory for export files
            template: Optional report template name
            
        Returns:
            Path to generated PDF report or None if failed
        """
        if not REPORTLAB_AVAILABLE:
            self.logger.error("Cannot generate PDF report: ReportLab not available")
            return None
        
        try:
            # Create PDF filename
            base_name = Path(image_path).stem
            pdf_filename = f"{base_name}_compliance_report.pdf"
            pdf_path = os.path.join(export_dir, pdf_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story = []
            
            # Add report header
            story.extend(self._create_pdf_header(processing_result, image_path))
            
            # Add executive summary
            story.extend(self._create_executive_summary(processing_result))
            
            # Add detailed validation results
            story.extend(self._create_validation_details(processing_result))
            
            # Add recommendations section
            story.extend(self._create_recommendations(processing_result))
            
            # Add technical details
            story.extend(self._create_technical_details(processing_result))
            
            # Add image analysis if available
            if 'annotated_image_path' in processing_result:
                story.extend(self._add_image_analysis(processing_result))
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            self.logger.error(f"PDF report generation failed: {str(e)}")
            return None
    
    def generate_json_report(self, processing_result: Dict[str, Any],
                           image_path: str, export_dir: str) -> Optional[str]:
        """
        Generate detailed JSON compliance report.
        
        Args:
            processing_result: Complete processing result data
            image_path: Path to original image
            export_dir: Directory for export files
            
        Returns:
            Path to generated JSON report or None if failed
        """
        try:
            # Create JSON filename
            base_name = Path(image_path).stem
            json_filename = f"{base_name}_compliance_report.json"
            json_path = os.path.join(export_dir, json_filename)
            
            # Create comprehensive report structure
            report_data = {
                'report_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'image_path': image_path,
                    'image_name': Path(image_path).name,
                    'report_version': '1.0',
                    'generator': 'Veridoc Universal Export System'
                },
                'processing_summary': {
                    'overall_compliance': processing_result.get('overall_compliance', 0),
                    'passes_requirements': processing_result.get('passes_requirements', False),
                    'confidence_score': processing_result.get('confidence_score', 0),
                    'processing_time': processing_result.get('processing_time', 0),
                    'format_validated': processing_result.get('format_name', 'Unknown')
                },
                'validation_results': self._extract_validation_results(processing_result),
                'quality_metrics': self._extract_quality_metrics(processing_result),
                'compliance_issues': self._extract_compliance_issues(processing_result),
                'recommendations': self._extract_recommendations(processing_result),
                'technical_details': self._extract_technical_details(processing_result),
                'audit_trail': {
                    'processing_steps': processing_result.get('processing_steps', []),
                    'ai_models_used': processing_result.get('ai_models_used', []),
                    'configuration_used': processing_result.get('configuration', {})
                }
            }
            
            # Add auto-fix results if available
            if 'auto_fix_result' in processing_result:
                report_data['auto_fix_analysis'] = self._extract_autofix_results(
                    processing_result['auto_fix_result']
                )
            
            # Write JSON report
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"JSON report generated: {json_path}")
            return json_path
            
        except Exception as e:
            self.logger.error(f"JSON report generation failed: {str(e)}")
            return None
    
    def generate_batch_pdf_report(self, batch_analysis: Dict[str, Any],
                                export_dir: str, template: Optional[str] = None) -> Optional[str]:
        """Generate batch processing summary PDF report."""
        if not REPORTLAB_AVAILABLE:
            self.logger.error("Cannot generate batch PDF report: ReportLab not available")
            return None
        
        try:
            pdf_filename = "batch_processing_summary.pdf"
            pdf_path = os.path.join(export_dir, pdf_filename)
            
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story = []
            
            # Add batch report header
            story.extend(self._create_batch_pdf_header(batch_analysis))
            
            # Add batch statistics
            story.extend(self._create_batch_statistics(batch_analysis))
            
            # Add failure analysis
            story.extend(self._create_failure_analysis(batch_analysis))
            
            # Add compliance trends
            story.extend(self._create_compliance_trends(batch_analysis))
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"Batch PDF report generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            self.logger.error(f"Batch PDF report generation failed: {str(e)}")
            return None
    
    def generate_batch_json_report(self, batch_analysis: Dict[str, Any],
                                 export_dir: str) -> Optional[str]:
        """Generate batch processing summary JSON report."""
        try:
            json_filename = "batch_processing_summary.json"
            json_path = os.path.join(export_dir, json_filename)
            
            # Create comprehensive batch report
            batch_report = {
                'batch_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_images': batch_analysis.get('total_images', 0),
                    'processing_duration': batch_analysis.get('total_processing_time', 0),
                    'report_version': '1.0'
                },
                'summary_statistics': batch_analysis.get('summary_statistics', {}),
                'compliance_breakdown': batch_analysis.get('compliance_breakdown', {}),
                'failure_analysis': batch_analysis.get('failure_analysis', {}),
                'quality_trends': batch_analysis.get('quality_trends', {}),
                'performance_metrics': batch_analysis.get('performance_metrics', {}),
                'recommendations': batch_analysis.get('batch_recommendations', []),
                'individual_results': batch_analysis.get('individual_summaries', [])
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(batch_report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Batch JSON report generated: {json_path}")
            return json_path
            
        except Exception as e:
            self.logger.error(f"Batch JSON report generation failed: {str(e)}")
            return None
    
    def _setup_report_styles(self) -> Dict[str, Any]:
        """Setup PDF report styling."""
        if not REPORTLAB_AVAILABLE:
            return {}
        
        styles = getSampleStyleSheet()
        
        # Custom styles for compliance reports
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Title'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading1'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=Color(0.2, 0.2, 0.6)
        ))
        
        styles.add(ParagraphStyle(
            name='CompliancePass',
            parent=styles['Normal'],
            textColor=green,
            fontSize=10
        ))
        
        styles.add(ParagraphStyle(
            name='ComplianceFail',
            parent=styles['Normal'],
            textColor=red,
            fontSize=10
        ))
        
        styles.add(ParagraphStyle(
            name='ComplianceWarning',
            parent=styles['Normal'],
            textColor=orange,
            fontSize=10
        ))
        
        return styles
    
    def _create_pdf_header(self, processing_result: Dict[str, Any], 
                          image_path: str) -> List[Any]:
        """Create PDF report header section."""
        story = []
        
        # Title
        title = Paragraph("ICAO Compliance Report", self.styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Basic information table
        info_data = [
            ['Image File:', Path(image_path).name],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Overall Compliance:', f"{processing_result.get('overall_compliance', 0):.1f}%"],
            ['Status:', 'PASS' if processing_result.get('passes_requirements', False) else 'FAIL']
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_executive_summary(self, processing_result: Dict[str, Any]) -> List[Any]:
        """Create executive summary section."""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Overall status
        passes = processing_result.get('passes_requirements', False)
        compliance_score = processing_result.get('overall_compliance', 0)
        
        status_text = f"This image {'PASSES' if passes else 'FAILS'} ICAO compliance requirements with an overall score of {compliance_score:.1f}%."
        
        style = self.styles['CompliancePass'] if passes else self.styles['ComplianceFail']
        story.append(Paragraph(status_text, style))
        story.append(Spacer(1, 12))
        
        # Key findings
        issues = processing_result.get('compliance_issues', [])
        if issues:
            story.append(Paragraph("Key Issues Identified:", self.styles['Normal']))
            for issue in issues[:5]:  # Top 5 issues
                issue_text = f"• {issue.get('description', 'Unknown issue')} (Severity: {issue.get('severity', 'Unknown')})"
                story.append(Paragraph(issue_text, self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_validation_details(self, processing_result: Dict[str, Any]) -> List[Any]:
        """Create detailed validation results section."""
        story = []
        
        story.append(Paragraph("Detailed Validation Results", self.styles['SectionHeader']))
        
        validation_results = processing_result.get('validation_results', {})
        
        # Create validation table
        table_data = [['Validation Check', 'Result', 'Score', 'Details']]
        
        for check_name, result in validation_results.items():
            if isinstance(result, dict):
                passes = result.get('passes', False)
                score = result.get('score', 0)
                details = result.get('details', 'No details available')
                
                table_data.append([
                    self.rule_descriptions.get(check_name, check_name),
                    'PASS' if passes else 'FAIL',
                    f"{score:.1f}%",
                    details[:100] + '...' if len(details) > 100 else details
                ])
        
        if len(table_data) > 1:
            validation_table = Table(table_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 2.4*inch])
            validation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), Color(0.8, 0.8, 0.8)),
                ('TEXTCOLOR', (0, 0), (-1, 0), black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(validation_table)
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_recommendations(self, processing_result: Dict[str, Any]) -> List[Any]:
        """Create recommendations section."""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        
        recommendations = processing_result.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_text = f"{i}. {rec}"
                story.append(Paragraph(rec_text, self.styles['Normal']))
        else:
            story.append(Paragraph("No specific recommendations available.", self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_technical_details(self, processing_result: Dict[str, Any]) -> List[Any]:
        """Create technical details section."""
        story = []
        
        story.append(Paragraph("Technical Details", self.styles['SectionHeader']))
        
        # Processing metrics
        metrics = processing_result.get('processing_metrics', {})
        if metrics:
            tech_data = [
                ['Processing Time:', f"{metrics.get('total_time', 0):.2f} seconds"],
                ['AI Models Used:', ', '.join(metrics.get('models_used', []))],
                ['Image Resolution:', f"{metrics.get('image_width', 0)}x{metrics.get('image_height', 0)}"],
                ['Face Detection Confidence:', f"{metrics.get('face_confidence', 0):.2f}"]
            ]
            
            tech_table = Table(tech_data, colWidths=[2*inch, 4*inch])
            tech_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, black),
            ]))
            
            story.append(tech_table)
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_batch_pdf_header(self, batch_analysis: Dict[str, Any]) -> List[Any]:
        """Create batch report header."""
        story = []
        
        title = Paragraph("Batch Processing Summary Report", self.styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Batch summary info
        summary = batch_analysis.get('summary_statistics', {})
        info_data = [
            ['Total Images Processed:', str(summary.get('total_images', 0))],
            ['Successfully Processed:', str(summary.get('successful_images', 0))],
            ['Failed Processing:', str(summary.get('failed_images', 0))],
            ['Overall Success Rate:', f"{summary.get('success_rate', 0):.1f}%"],
            ['Average Compliance Score:', f"{summary.get('avg_compliance_score', 0):.1f}%"],
            ['Processing Duration:', f"{summary.get('total_processing_time', 0):.1f} seconds"]
        ]
        
        info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_batch_statistics(self, batch_analysis: Dict[str, Any]) -> List[Any]:
        """Create batch statistics section."""
        story = []
        
        story.append(Paragraph("Processing Statistics", self.styles['SectionHeader']))
        
        compliance_breakdown = batch_analysis.get('compliance_breakdown', {})
        if compliance_breakdown:
            stats_data = [['Compliance Level', 'Count', 'Percentage']]
            
            for level, count in compliance_breakdown.items():
                total = batch_analysis.get('summary_statistics', {}).get('total_images', 1)
                percentage = (count / total) * 100 if total > 0 else 0
                stats_data.append([level.replace('_', ' ').title(), str(count), f"{percentage:.1f}%"])
            
            stats_table = Table(stats_data, colWidths=[2*inch, 1*inch, 1.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), Color(0.8, 0.8, 0.8)),
                ('TEXTCOLOR', (0, 0), (-1, 0), black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, black),
            ]))
            
            story.append(stats_table)
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_failure_analysis(self, batch_analysis: Dict[str, Any]) -> List[Any]:
        """Create failure analysis section."""
        story = []
        
        story.append(Paragraph("Failure Analysis", self.styles['SectionHeader']))
        
        failure_analysis = batch_analysis.get('failure_analysis', {})
        common_issues = failure_analysis.get('common_issues', [])
        
        if common_issues:
            story.append(Paragraph("Most Common Issues:", self.styles['Normal']))
            for issue in common_issues[:10]:  # Top 10 issues
                issue_text = f"• {issue.get('issue', 'Unknown')} ({issue.get('count', 0)} occurrences)"
                story.append(Paragraph(issue_text, self.styles['Normal']))
        else:
            story.append(Paragraph("No significant failure patterns identified.", self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_compliance_trends(self, batch_analysis: Dict[str, Any]) -> List[Any]:
        """Create compliance trends section."""
        story = []
        
        story.append(Paragraph("Compliance Trends", self.styles['SectionHeader']))
        
        trends = batch_analysis.get('quality_trends', {})
        if trends:
            for metric, trend_data in trends.items():
                trend_text = f"{metric.replace('_', ' ').title()}: Average {trend_data.get('average', 0):.1f}%, Range {trend_data.get('min', 0):.1f}%-{trend_data.get('max', 0):.1f}%"
                story.append(Paragraph(trend_text, self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _extract_validation_results(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and format validation results for JSON report."""
        return processing_result.get('validation_results', {})
    
    def _extract_quality_metrics(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract quality metrics for JSON report."""
        return processing_result.get('quality_metrics', {})
    
    def _extract_compliance_issues(self, processing_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract compliance issues for JSON report."""
        return processing_result.get('compliance_issues', [])
    
    def _extract_recommendations(self, processing_result: Dict[str, Any]) -> List[str]:
        """Extract recommendations for JSON report."""
        return processing_result.get('recommendations', [])
    
    def _extract_technical_details(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical details for JSON report."""
        return processing_result.get('processing_metrics', {})
    
    def _extract_autofix_results(self, autofix_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract auto-fix results for JSON report."""
        return {
            'improvements_made': autofix_result.get('improvements_made', []),
            'quality_improvement': autofix_result.get('quality_improvement', 0),
            'compliance_improvement': autofix_result.get('compliance_improvement', 0),
            'processing_time': autofix_result.get('processing_time', 0)
        }
    
    def _add_image_analysis(self, processing_result: Dict[str, Any]) -> List[Any]:
        """Add image analysis section with annotated image."""
        story = []
        
        story.append(Paragraph("Visual Analysis", self.styles['SectionHeader']))
        
        # Add annotated image if available
        annotated_path = processing_result.get('annotated_image_path')
        if annotated_path and os.path.exists(annotated_path) and REPORTLAB_AVAILABLE:
            try:
                # Resize image to fit in report
                img = RLImage(annotated_path, width=4*inch, height=3*inch)
                story.append(img)
                story.append(Paragraph("Annotated image showing compliance measurements and detected issues.", self.styles['Normal']))
            except Exception as e:
                self.logger.warning(f"Could not add image to PDF report: {str(e)}")
        
        story.append(Spacer(1, 20))
        return story