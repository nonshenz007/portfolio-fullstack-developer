"""
ENHANCED COMPREHENSIVE VERIFICATION ENGINE for LedgerFlow invoices

This is the refactored version with modular architecture and dependency injection.
The public API remains compatible with the original implementation.
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .rules_config import RulesConfig
from .gst_packager import GSTPackager
from .diagnostics_logger import DiagnosticsLogger
from .verification.models import ValidationResult, ValidationError, ValidationContext, Severity, RiskLevel, asdict
from .verification.validators import (
    StructureValidator,
    InvoiceNumberValidator,
    DatesValidator,
    CustomerValidator,
    ItemsValidator,
    TaxValidator,
    TotalsValidator,
    TemplateValidator,
    ComplianceValidator,
    BusinessLogicValidator
)


class VerificationEngine:
    """
    ENHANCED COMPREHENSIVE VERIFICATION ENGINE for LedgerFlow invoices
    
    Features:
    - Multi-layer verification system with modular validators
    - Template-specific validation (GST E-Invoice, Bahrain VAT, Plain Cash)
    - Complete UI parameter compliance verification
    - Advanced business logic validation
    - Government-grade compliance checking
    - Statistical pattern analysis
    - Revenue target validation
    - Product selection compliance
    - Reality control verification
    - Audit trail generation with forensic-level detail
    """
    
    def __init__(self, country: str = 'India', business_state: str = 'Maharashtra', ui_params: Dict[str, Any] = None):
        # Load configuration
        config_path = Path("app/config/verification_rules.yaml")
        self.rules_config = RulesConfig.load_from_yaml(config_path)
        
        # Initialize dependencies
        self.country = country
        self.business_state = business_state
        self.gst_packager = GSTPackager(country, business_state)
        self.diagnostics = DiagnosticsLogger()
        self.ui_params = ui_params or {}
        
        # Initialize validators
        self.validators = [
            StructureValidator(self.rules_config, self.diagnostics),
            InvoiceNumberValidator(self.rules_config, self.diagnostics),
            DatesValidator(self.rules_config, self.diagnostics),
            CustomerValidator(self.rules_config, self.diagnostics),
            ItemsValidator(self.rules_config, self.diagnostics),
            TaxValidator(self.rules_config, self.gst_packager, self.diagnostics),
            TotalsValidator(self.rules_config, self.diagnostics),
            TemplateValidator(self.rules_config, self.diagnostics),
            ComplianceValidator(self.rules_config, self.diagnostics),
            BusinessLogicValidator(self.rules_config, self.diagnostics)
        ]
        
        # Initialize verification statistics
        self.verification_stats = {
            'total_verified': 0,
            'template_compliance': {},
            'parameter_compliance': {},
            'pattern_analysis': {}
        }
    
    def verify_invoice(self, invoice_data: Dict[str, Any]) -> ValidationResult:
        """
        Comprehensive verification of a single invoice
        
        Args:
            invoice_data: Dictionary containing invoice information
            
        Returns:
            ValidationResult with all validation details
        """
        # Handle None or invalid data gracefully
        if invoice_data is None:
            return ValidationResult(
                invoice_number='UNKNOWN',
                is_valid=False,
                errors=[ValidationError(
                    error_type='data_error',
                    severity=Severity.CRITICAL,
                    field='invoice_data',
                    message='Invoice data is None',
                    current_value='None',
                    suggestion='Provide valid invoice data'
                )],
                warnings=[],
                info=[],
                compliance_score=0.0,
                risk_level=RiskLevel.CRITICAL,
                validation_timestamp=datetime.now(),
                hash_signature=''
            )
        
        # Ensure invoice_data is a dictionary
        if not isinstance(invoice_data, dict):
            return ValidationResult(
                invoice_number='UNKNOWN',
                is_valid=False,
                errors=[ValidationError(
                    error_type='data_error',
                    severity=Severity.CRITICAL,
                    field='invoice_data',
                    message='Invoice data must be a dictionary',
                    current_value=str(type(invoice_data)),
                    suggestion='Provide valid invoice data as dictionary'
                )],
                warnings=[],
                info=[],
                compliance_score=0.0,
                risk_level=RiskLevel.CRITICAL,
                validation_timestamp=datetime.now(),
                hash_signature=''
            )
        
        # Create validation context
        context = ValidationContext(
            country=self.country,
            business_state=self.business_state,
            invoice_type=invoice_data.get('invoice_type', 'gst'),
            template_type=invoice_data.get('template_type'),
            ui_params=self.ui_params
        )
        
        # Collect all validation errors
        all_errors = []
        
        for validator in self.validators:
            try:
                errors = validator.validate(invoice_data, context)
                all_errors.extend(errors)
            except Exception as e:
                self.diagnostics.error(f"Validator {validator.__class__.__name__} failed: {str(e)}")
                all_errors.append(ValidationError(
                    error_type='validator_error',
                    severity=Severity.CRITICAL,
                    field='validation',
                    message=f"Validator {validator.__class__.__name__} failed",
                    current_value=str(e),
                    suggestion="Check validator implementation"
                ))
        
        # Separate errors by severity
        critical_errors = [e for e in all_errors if e.severity == Severity.CRITICAL]
        warnings = [e for e in all_errors if e.severity == Severity.WARNING]
        info = [e for e in all_errors if e.severity == Severity.INFO]
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(critical_errors, warnings, info)
        
        # Determine risk level
        risk_level = self._determine_risk_level(compliance_score, critical_errors)
        
        # Generate hash signature
        hash_signature = self._generate_hash_signature(invoice_data)
        
        # Create validation result
        result = ValidationResult(
            invoice_number=invoice_data.get('invoice_number', 'UNKNOWN'),
            is_valid=len(critical_errors) == 0,
            errors=critical_errors,
            warnings=warnings,
            info=info,
            compliance_score=compliance_score,
            risk_level=risk_level,
            validation_timestamp=datetime.now(),
            hash_signature=hash_signature
        )
        
        # Update verification statistics
        self._update_verification_stats(result, invoice_data)
        
        # Log validation result
        self._log_validation_result(result)
        
        return result
    
    def verify_invoice_batch(self, invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify a batch of invoices and generate summary
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            Batch verification summary
        """
        batch_results = []
        
        # Verify each invoice
        for invoice in invoices:
            result = self.verify_invoice(invoice)
            batch_results.append(result)
        
        # Create batch summary
        total_invoices = len(batch_results)
        valid_invoices = len([r for r in batch_results if r.is_valid])
        invalid_invoices = total_invoices - valid_invoices
        
        # Calculate risk distribution
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for result in batch_results:
            risk_distribution[result.risk_level.value] += 1
        
        # Calculate average compliance score
        avg_compliance = sum(r.compliance_score for r in batch_results) / total_invoices if total_invoices > 0 else 0
        
        # Check sequence integrity
        sequence_errors = self._validate_invoice_sequence(invoices)
        
        return {
            'total_invoices': total_invoices,
            'valid_invoices': valid_invoices,
            'invalid_invoices': invalid_invoices,
            'success_rate': (valid_invoices / total_invoices * 100) if total_invoices > 0 else 0,
            'average_compliance_score': avg_compliance,
            'risk_distribution': risk_distribution,
            'sequence_errors': sequence_errors,
            'batch_errors': [r.invoice_number for r in batch_results if not r.is_valid],
            'validation_timestamp': datetime.now(),
            'results': batch_results
        }
    
    def _calculate_compliance_score(self, critical_errors: List[ValidationError], 
                                  warnings: List[ValidationError], info: List[ValidationError]) -> float:
        """Calculate compliance score (0-100)"""
        scoring = self.rules_config.compliance_scoring
        base_score = scoring.base_score
        
        # Deduct points for errors
        for error in critical_errors:
            base_score -= scoring.critical_error_penalty
        
        for error in warnings:
            base_score -= scoring.warning_penalty
        
        # Cap at 0
        return max(0.0, base_score)
    
    def _determine_risk_level(self, compliance_score: float, critical_errors: List[ValidationError]) -> RiskLevel:
        """Determine risk level based on compliance score and errors"""
        risk_levels = self.rules_config.risk_levels
        
        if len(critical_errors) > 0:
            return RiskLevel.CRITICAL
        elif compliance_score < risk_levels.high_threshold:
            return RiskLevel.HIGH
        elif compliance_score < risk_levels.medium_threshold:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_hash_signature(self, invoice_data: Dict[str, Any]) -> str:
        """Generate hash signature for invoice"""
        # Create a normalized string representation
        normalized_data = {
            'invoice_number': invoice_data.get('invoice_number'),
            'invoice_date': invoice_data.get('invoice_date'),
            'customer_name': invoice_data.get('customer_name'),
            'total_amount': invoice_data.get('total_amount'),
            'items_count': len(invoice_data.get('items', []))
        }
        
        data_string = json.dumps(normalized_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _validate_invoice_sequence(self, invoices: List[Dict[str, Any]]) -> List[ValidationError]:
        """Validate invoice number sequence"""
        errors = []
        
        # Sort invoices by number
        try:
            sorted_invoices = sorted(invoices, key=lambda x: x.get('invoice_number', ''))
            
            # Check for duplicates
            numbers = [inv.get('invoice_number') for inv in invoices]
            duplicates = [num for num in set(numbers) if numbers.count(num) > 1]
            
            for duplicate in duplicates:
                errors.append(ValidationError(
                    error_type='duplicate_invoice_number',
                    severity=Severity.CRITICAL,
                    field='invoice_number',
                    message=f"Duplicate invoice number found: {duplicate}",
                    current_value=duplicate,
                    suggestion="Ensure invoice numbers are unique"
                ))
            
        except Exception as e:
            errors.append(ValidationError(
                error_type='sequence_validation_error',
                severity=Severity.WARNING,
                field='invoice_sequence',
                message=f"Error validating sequence: {str(e)}",
                current_value=None,
                suggestion="Check invoice number formats"
            ))
        
        return errors
    
    def _update_verification_stats(self, result: ValidationResult, invoice_data: Dict[str, Any]):
        """Update comprehensive verification statistics"""
        self.verification_stats['total_verified'] += 1
        
        # Template compliance stats
        template_type = invoice_data.get('template_type', 'unknown')
        if template_type not in self.verification_stats['template_compliance']:
            self.verification_stats['template_compliance'][template_type] = {
                'total': 0, 'passed': 0, 'failed': 0
            }
        
        self.verification_stats['template_compliance'][template_type]['total'] += 1
        if result.is_valid:
            self.verification_stats['template_compliance'][template_type]['passed'] += 1
        else:
            self.verification_stats['template_compliance'][template_type]['failed'] += 1
        
        # Parameter compliance stats
        for error in result.errors:
            error_type = error.error_type
            if error_type not in self.verification_stats['parameter_compliance']:
                self.verification_stats['parameter_compliance'][error_type] = 0
            self.verification_stats['parameter_compliance'][error_type] += 1
    
    def _log_validation_result(self, result: ValidationResult):
        """Log validation result"""
        if not result.is_valid:
            self.diagnostics.error(f"Invoice validation failed: {result.invoice_number} - {len(result.errors)} errors")
        elif len(result.warnings) > 0:
            self.diagnostics.warning(f"Invoice validation warnings: {result.invoice_number} - {len(result.warnings)} warnings")
        else:
            self.diagnostics.info(f"Invoice validation passed: {result.invoice_number} - Score: {result.compliance_score}")
    
    def export_validation_report(self, results: List[ValidationResult], output_path: str):
        """Export detailed validation report"""
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'total_invoices': len(results),
            'validation_summary': {
                'valid_invoices': len([r for r in results if r.is_valid]),
                'invalid_invoices': len([r for r in results if not r.is_valid]),
                'average_compliance_score': sum(r.compliance_score for r in results) / len(results) if results else 0,
                'risk_distribution': self._calculate_risk_distribution(results)
            },
            'detailed_results': [asdict(result) for result in results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.diagnostics.info(f"Validation report exported to: {output_path}")
    
    def _calculate_risk_distribution(self, results: List[ValidationResult]) -> Dict[str, int]:
        """Calculate risk level distribution"""
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        for result in results:
            distribution[result.risk_level.value] += 1
        
        return distribution
    
    def get_comprehensive_verification_report(self) -> Dict[str, Any]:
        """Generate comprehensive verification report with all statistics"""
        return {
            'verification_stats': self.verification_stats,
            'ui_params': self.ui_params,
            'template_requirements': self.rules_config.template_requirements,
            'timestamp': datetime.now().isoformat()
        }
    
    def verify_batch_comprehensive(self, invoices: List[Dict[str, Any]], ui_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        ULTIMATE COMPREHENSIVE BATCH VERIFICATION
        This is the main method that validates everything against UI parameters
        """
        # Update UI parameters for this batch
        self.ui_params = ui_params
        
        # Reset statistics
        self.verification_stats = {
            'total_verified': 0,
            'template_compliance': {},
            'parameter_compliance': {},
            'pattern_analysis': {}
        }
        
        # Verify each invoice
        batch_results = []
        for invoice in invoices:
            result = self.verify_invoice(invoice)
            batch_results.append(result)
        
        # Batch-level validations
        batch_errors = []
        
        # Validate invoice count
        expected_count = ui_params.get('invoice_count', 100)
        actual_count = len(invoices)
        if actual_count != expected_count:
            batch_errors.append({
                'error_type': 'invoice_count_mismatch',
                'severity': 'critical',
                'message': f"Generated {actual_count} invoices but UI requested {expected_count}",
                'current_value': actual_count,
                'expected_value': expected_count
            })
        
        # Validate revenue target
        revenue_target = ui_params.get('revenue_target')
        if revenue_target:
            actual_revenue = sum(float(inv.get('total_amount', 0)) for inv in invoices)
            revenue_tolerance = revenue_target * 0.1  # 10% tolerance
            if abs(actual_revenue - revenue_target) > revenue_tolerance:
                batch_errors.append({
                    'error_type': 'revenue_target_mismatch',
                    'severity': 'critical',
                    'message': f"Revenue target not achieved within tolerance",
                    'current_value': actual_revenue,
                    'expected_value': revenue_target,
                    'tolerance': revenue_tolerance
                })
        
        # Validate template consistency
        expected_template = ui_params.get('template_type')
        if expected_template:
            template_mismatches = [inv for inv in invoices if inv.get('template_type') != expected_template]
            if template_mismatches:
                batch_errors.append({
                    'error_type': 'template_consistency_failure',
                    'severity': 'critical',
                    'message': f"{len(template_mismatches)} invoices have wrong template",
                    'current_value': f"{len(template_mismatches)} mismatches",
                    'expected_value': f"All {expected_template}"
                })
        
        # Calculate comprehensive statistics
        total_invoices = len(batch_results)
        passed_invoices = len([r for r in batch_results if r.is_valid])
        failed_invoices = total_invoices - passed_invoices
        success_rate = (passed_invoices / total_invoices * 100) if total_invoices > 0 else 0
        
        # Generate comprehensive report
        return {
            'total_invoices': total_invoices,
            'passed_invoices': passed_invoices,
            'failed_invoices': failed_invoices,
            'success_rate': success_rate,
            'batch_errors': batch_errors,
            'individual_results': batch_results,
            'verification_stats': self.verification_stats,
            'ui_parameter_compliance': self._analyze_ui_parameter_compliance(invoices, ui_params),
            'template_compliance': self._analyze_template_compliance(invoices, ui_params),
            'pattern_analysis': self._analyze_patterns(invoices),
            'comprehensive_report': self.get_comprehensive_verification_report()
        }
    
    def _analyze_ui_parameter_compliance(self, invoices: List[Dict[str, Any]], ui_params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well invoices comply with UI parameters"""
        compliance_report = {
            'business_name_compliance': 0,
            'amount_range_compliance': 0,
            'item_count_compliance': 0,
            'template_compliance': 0,
            'overall_compliance': 0
        }
        
        total_invoices = len(invoices)
        if total_invoices == 0:
            return compliance_report
        
        # Check business name compliance
        expected_business_name = ui_params.get('business_name', '')
        if expected_business_name:
            compliant_business_name = sum(1 for inv in invoices 
                                        if expected_business_name in inv.get('business_name', ''))
            compliance_report['business_name_compliance'] = (compliant_business_name / total_invoices) * 100
        
        # Check amount range compliance
        min_amount = ui_params.get('min_bill_amount', 0)
        max_amount = ui_params.get('max_bill_amount', float('inf'))
        compliant_amounts = sum(1 for inv in invoices 
                              if min_amount <= float(inv.get('total_amount', 0)) <= max_amount)
        compliance_report['amount_range_compliance'] = (compliant_amounts / total_invoices) * 100
        
        # Check item count compliance
        min_items = ui_params.get('min_items', 1)
        max_items = ui_params.get('max_items', 50)
        compliant_items = sum(1 for inv in invoices 
                            if min_items <= len(inv.get('items', [])) <= max_items)
        compliance_report['item_count_compliance'] = (compliant_items / total_invoices) * 100
        
        # Check template compliance
        expected_template = ui_params.get('template_type')
        if expected_template:
            compliant_templates = sum(1 for inv in invoices 
                                    if inv.get('template_type') == expected_template)
            compliance_report['template_compliance'] = (compliant_templates / total_invoices) * 100
        
        # Calculate overall compliance
        compliance_scores = [
            compliance_report['business_name_compliance'],
            compliance_report['amount_range_compliance'],
            compliance_report['item_count_compliance'],
            compliance_report['template_compliance']
        ]
        compliance_report['overall_compliance'] = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
        
        return compliance_report
    
    def _analyze_template_compliance(self, invoices: List[Dict[str, Any]], ui_params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze template-specific compliance"""
        template_analysis = {}
        
        for invoice in invoices:
            template_type = invoice.get('template_type', 'unknown')
            if template_type not in template_analysis:
                template_analysis[template_type] = {
                    'count': 0,
                    'required_fields_present': 0,
                    'currency_correct': 0,
                    'tax_structure_correct': 0
                }
            
            template_analysis[template_type]['count'] += 1
            
            # Check required fields
            if template_type in self.rules_config.template_requirements:
                req = self.rules_config.template_requirements[template_type]
                fields_present = all(field in invoice for field in req.required_fields)
                if fields_present:
                    template_analysis[template_type]['required_fields_present'] += 1
                
                # Check currency
                if invoice.get('currency') == req.currency:
                    template_analysis[template_type]['currency_correct'] += 1
                
                # Check tax structure
                tax_correct = False
                if req.tax_structure == 'gst':
                    tax_correct = any([
                        invoice.get('cgst_amount', 0) > 0,
                        invoice.get('sgst_amount', 0) > 0,
                        invoice.get('igst_amount', 0) > 0
                    ])
                elif req.tax_structure == 'vat':
                    tax_correct = invoice.get('vat_amount', 0) > 0
                elif req.tax_structure == 'none':
                    tax_correct = invoice.get('tax_amount', 0) == 0
                
                if tax_correct:
                    template_analysis[template_type]['tax_structure_correct'] += 1
        
        return template_analysis
    
    def _analyze_patterns(self, invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in the generated invoices"""
        if not invoices:
            return {}
        
        amounts = [float(inv.get('total_amount', 0)) for inv in invoices]
        item_counts = [len(inv.get('items', [])) for inv in invoices]
        
        return {
            'amount_statistics': {
                'min': min(amounts),
                'max': max(amounts),
                'average': sum(amounts) / len(amounts),
                'total': sum(amounts)
            },
            'item_count_statistics': {
                'min': min(item_counts),
                'max': max(item_counts),
                'average': sum(item_counts) / len(item_counts)
            },
            'template_distribution': self._get_template_distribution(invoices),
            'date_distribution': self._get_date_distribution(invoices)
        }
    
    def _get_template_distribution(self, invoices: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of templates used"""
        distribution = {}
        for invoice in invoices:
            template = invoice.get('template_type', 'unknown')
            distribution[template] = distribution.get(template, 0) + 1
        return distribution
    
    def _get_date_distribution(self, invoices: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of invoice dates"""
        distribution = {}
        for invoice in invoices:
            date_str = invoice.get('invoice_date', 'unknown')
            distribution[date_str] = distribution.get(date_str, 0) + 1
        return distribution