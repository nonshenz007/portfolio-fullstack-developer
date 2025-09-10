#!/usr/bin/env python3
"""
Example usage of the refactored VerificationEngine

This demonstrates how to use the new modular verification architecture
with configuration-driven rules and dependency injection.
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.rules_config import RulesConfig
from app.core.gst_packager import GSTPackager
from app.core.diagnostics_logger import DiagnosticsLogger
from app.core.verification_engine import VerificationEngine


def main():
    """Demonstrate the new VerificationEngine usage"""
    
    # 1. Load configuration from YAML (for demonstration)
    config_path = Path("app/config/verification_rules.yaml")
    rules_config = RulesConfig.load_from_yaml(config_path)
    
    # 2. Create dependencies (for demonstration)
    gst_packager = GSTPackager('India', 'Maharashtra')
    diagnostics_logger = DiagnosticsLogger()
    
    # 3. Initialize the verification engine
    # Note: The engine now loads configuration internally
    verification_engine = VerificationEngine(
        country='India',
        business_state='Maharashtra',
        ui_params={
            'min_items': 1,
            'max_items': 10,
            'min_bill_amount': 100,
            'max_bill_amount': 10000
        }
    )
    
    # 4. Example invoice data
    invoice_data = {
        'invoice_number': 'GST-2025-000001',
        'invoice_date': '2025-01-15',
        'customer_name': 'Example Customer Pvt Ltd',
        'invoice_type': 'gst',
        'template_type': 'gst_einvoice',
        'business_gst_number': '27AAAAA0000A1Z5',
        'place_of_supply': 'Maharashtra',
        'currency': 'INR',
        'cgst_amount': 9.0,
        'sgst_amount': 9.0,
        'igst_amount': 0.0,
        'items': [
            {
                'name': 'Software License',
                'quantity': 1,
                'unit_price': 1000.0,
                'net_amount': 1000.0,
                'tax_amount': 180.0,
                'cgst_amount': 90.0,
                'sgst_amount': 90.0,
                'igst_amount': 0.0,
                'hsn_code': '998314'
            }
        ],
        'subtotal': 1000.0,
        'tax_amount': 180.0,
        'total_amount': 1180.0
    }
    
    # 5. Verify a single invoice
    print("=== Single Invoice Verification ===")
    result = verification_engine.verify_invoice(invoice_data)
    
    print(f"Invoice: {result.invoice_number}")
    print(f"Valid: {result.is_valid}")
    print(f"Compliance Score: {result.compliance_score}")
    print(f"Risk Level: {result.risk_level.value}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Info: {len(result.info)}")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error.field}: {error.message}")
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning.field}: {warning.message}")
    
    # 6. Example batch verification
    print("\n=== Batch Verification ===")
    invoices = [
        invoice_data,
        {
            'invoice_number': 'GST-2025-000002',
            'invoice_date': '2025-01-16',
            'customer_name': 'Another Customer',
            'invoice_type': 'gst',
            'template_type': 'gst_einvoice',
            'business_gst_number': '27AAAAA0000A1Z5',
            'place_of_supply': 'Maharashtra',
            'currency': 'INR',
            'cgst_amount': 18.0,
            'sgst_amount': 18.0,
            'igst_amount': 0.0,
            'items': [
                {
                    'name': 'Consulting Services',
                    'quantity': 10,
                    'unit_price': 100.0,
                    'net_amount': 1000.0,
                    'tax_amount': 180.0,
                    'cgst_amount': 90.0,
                    'sgst_amount': 90.0,
                    'igst_amount': 0.0
                }
            ],
            'subtotal': 1000.0,
            'tax_amount': 180.0,
            'total_amount': 1180.0
        }
    ]
    
    batch_result = verification_engine.verify_invoice_batch(invoices)
    
    print(f"Total Invoices: {batch_result['total_invoices']}")
    print(f"Valid Invoices: {batch_result['valid_invoices']}")
    print(f"Invalid Invoices: {batch_result['invalid_invoices']}")
    print(f"Success Rate: {batch_result['success_rate']:.1f}%")
    print(f"Average Compliance Score: {batch_result['average_compliance_score']:.1f}")
    print(f"Risk Distribution: {batch_result['risk_distribution']}")
    
    # 7. Export validation report
    print("\n=== Exporting Validation Report ===")
    results = batch_result['results']
    verification_engine.export_validation_report(results, "validation_report.json")
    print("Validation report exported to validation_report.json")
    
    # 8. Demonstrate configuration access
    print("\n=== Configuration Examples ===")
    print(f"Max Invoice Amount: ₹{rules_config.business_rules.max_invoice_amount:,}")
    print(f"Tax Calculation Tolerance: ₹{rules_config.tax_tolerances.tax_calculation}")
    print(f"Critical Error Penalty: {rules_config.compliance_scoring.critical_error_penalty} points")
    
    # Get sample invoice number for GST
    sample_number = rules_config.get_sample_invoice_number('gst')
    print(f"Sample GST Invoice Number: {sample_number}")
    
    # Get template requirements
    template_req = rules_config.get_template_requirements('gst_einvoice')
    if template_req:
        print(f"GST E-Invoice Currency: {template_req.currency}")
        print(f"GST E-Invoice Tax Structure: {template_req.tax_structure}")
        print(f"Required Fields: {template_req.required_fields}")


if __name__ == "__main__":
    main() 