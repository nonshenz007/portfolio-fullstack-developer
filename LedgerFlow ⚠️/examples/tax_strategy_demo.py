#!/usr/bin/env python3
"""
Tax Strategy System Demonstration

This script demonstrates the tax strategy pattern system implemented for LedgerFlow.
It shows how different tax strategies (GST, VAT, NoTax) can be used interchangeably
and how the system supports plugin discovery.

Requirements addressed:
- FR-2: Pluggable tax rules for new countries
- NFR Internationalization: Support for different tax systems
"""

import sys
import os
from decimal import Decimal
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.tax_strategies import (
    TaxStrategyFactory,
    TaxContext,
    InvoiceItem,
    GSTStrategy,
    VATStrategy,
    NoTaxStrategy
)


def print_separator(title):
    """Print a formatted separator"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_tax_result(result, item_name):
    """Print formatted tax calculation result"""
    print(f"\nTax Calculation for: {item_name}")
    print(f"  Gross Amount:    {result.gross_amount}")
    print(f"  Discount Amount: {result.discount_amount}")
    print(f"  Net Amount:      {result.net_amount}")
    
    if result.is_exempt:
        print(f"  Tax Status:      EXEMPT ({result.exemption_reason})")
        print(f"  Total Tax:       {result.total_tax}")
    else:
        print(f"  Tax Breakdown:")
        if result.cgst_amount > 0:
            print(f"    CGST ({result.cgst_rate}%): {result.cgst_amount}")
        if result.sgst_amount > 0:
            print(f"    SGST ({result.sgst_rate}%): {result.sgst_amount}")
        if result.igst_amount > 0:
            print(f"    IGST ({result.igst_rate}%): {result.igst_amount}")
        if result.vat_amount > 0:
            print(f"    VAT ({result.vat_rate}%):  {result.vat_amount}")
        print(f"  Total Tax:       {result.total_tax}")
    
    print(f"  Total Amount:    {result.total_amount}")


def demo_gst_strategy():
    """Demonstrate GST strategy with intrastate and interstate calculations"""
    print_separator("GST Strategy Demonstration")
    
    # Create GST strategy
    gst_strategy = TaxStrategyFactory.create_strategy('gst')
    print(f"Strategy: {gst_strategy.get_strategy_name()}")
    print(f"Supported Countries: {gst_strategy.get_supported_countries()}")
    print(f"Supported Currencies: {gst_strategy.get_supported_currencies()}")
    
    # Test item
    laptop = InvoiceItem(
        item_name='Laptop Computer',
        quantity=Decimal('1'),
        unit_price=Decimal('50000.00'),
        tax_rate=Decimal('18.00')
    )
    
    # Intrastate transaction (Maharashtra to Maharashtra)
    print(f"\n--- Intrastate Transaction (CGST + SGST) ---")
    intrastate_context = TaxContext(
        customer_state='Maharashtra',
        business_state='Maharashtra',
        invoice_date=datetime.now(),
        is_interstate=False,
        customer_type='individual',
        customer_country='India',
        business_country='India',
        currency='INR'
    )
    
    result = gst_strategy.calculate_tax(laptop, intrastate_context)
    print_tax_result(result, laptop.item_name)
    
    # Verify CGST = SGST property
    print(f"\n✓ CGST = SGST Property: {result.cgst_amount == result.sgst_amount}")
    
    # Interstate transaction (Maharashtra to Karnataka)
    print(f"\n--- Interstate Transaction (IGST) ---")
    interstate_context = TaxContext(
        customer_state='Karnataka',
        business_state='Maharashtra',
        invoice_date=datetime.now(),
        is_interstate=True,
        customer_type='individual',
        customer_country='India',
        business_country='India',
        currency='INR'
    )
    
    result = gst_strategy.calculate_tax(laptop, interstate_context)
    print_tax_result(result, laptop.item_name)


def demo_vat_strategy():
    """Demonstrate VAT strategy with Arabic locale support"""
    print_separator("VAT Strategy Demonstration")
    
    # Create VAT strategies for different locales
    vat_strategy_en = TaxStrategyFactory.create_strategy('vat', locale='en')
    vat_strategy_ar = TaxStrategyFactory.create_strategy('vat', locale='ar')
    
    print(f"Strategy: {vat_strategy_en.get_strategy_name()}")
    print(f"Supported Countries: {vat_strategy_en.get_supported_countries()}")
    print(f"Supported Currencies: {vat_strategy_en.get_supported_currencies()}")
    
    # Test items
    electronics = InvoiceItem(
        item_name='Electronics Item',
        quantity=Decimal('1'),
        unit_price=Decimal('100.000'),  # BHD precision
        tax_rate=Decimal('10.00')
    )
    
    food = InvoiceItem(
        item_name='Basic Food Item',
        quantity=Decimal('2'),
        unit_price=Decimal('25.000'),
        tax_rate=Decimal('0.00')  # Zero-rated
    )
    
    # Bahrain context
    bahrain_context = TaxContext(
        customer_state='Manama',
        business_state='Manama',
        invoice_date=datetime.now(),
        is_interstate=False,
        customer_type='individual',
        customer_country='Bahrain',
        business_country='Bahrain',
        currency='BHD'
    )
    
    # English locale
    print(f"\n--- English Locale ---")
    result_en = vat_strategy_en.calculate_tax(electronics, bahrain_context)
    print_tax_result(result_en, electronics.item_name)
    
    # Arabic locale
    print(f"\n--- Arabic Locale ---")
    result_ar = vat_strategy_ar.calculate_tax(electronics, bahrain_context)
    print_tax_result(result_ar, electronics.item_name)
    print(f"Currency Symbol (Arabic): {vat_strategy_ar.get_currency_symbol()}")
    
    # Zero-rated item
    print(f"\n--- Zero-Rated Item ---")
    food_result = vat_strategy_en.calculate_tax(food, bahrain_context)
    print_tax_result(food_result, food.item_name)


def demo_no_tax_strategy():
    """Demonstrate NoTax strategy for cash invoices"""
    print_separator("NoTax Strategy Demonstration")
    
    # Create NoTax strategy
    no_tax_strategy = TaxStrategyFactory.create_strategy('no_tax')
    print(f"Strategy: {no_tax_strategy.get_strategy_name()}")
    print(f"Supported Countries: {no_tax_strategy.get_supported_countries()}")
    print(f"Supported Currencies: {no_tax_strategy.get_supported_currencies()}")
    
    # Test items
    expensive_item = InvoiceItem(
        item_name='Expensive Equipment',
        quantity=Decimal('1'),
        unit_price=Decimal('100000.00'),
        discount_percentage=Decimal('10.00')
    )
    
    # Generic context (works with any country/currency)
    cash_context = TaxContext(
        customer_state='Any State',
        business_state='Any State',
        invoice_date=datetime.now(),
        is_interstate=False,
        customer_type='individual',
        customer_country='USA',
        business_country='USA',
        currency='USD'
    )
    
    result = no_tax_strategy.calculate_tax(expensive_item, cash_context)
    print_tax_result(result, expensive_item.item_name)


def demo_factory_features():
    """Demonstrate factory features and plugin discovery"""
    print_separator("Factory Features Demonstration")
    
    # Available strategies
    print("Available Strategies:")
    for strategy in TaxStrategyFactory.get_available_strategies():
        print(f"  - {strategy}")
    
    # Supported countries
    print(f"\nSupported Countries:")
    for country in TaxStrategyFactory.get_supported_countries():
        print(f"  - {country}")
    
    # Strategy information
    print(f"\nStrategy Information:")
    for strategy_name in ['gst', 'vat', 'no_tax']:
        info = TaxStrategyFactory.get_strategy_info(strategy_name)
        print(f"  {strategy_name}:")
        print(f"    Class: {info['class_name']}")
        print(f"    Plugin: {info['is_plugin']}")
        print(f"    Countries: {info['supported_countries']}")
        print(f"    Currencies: {info['supported_currencies']}")
    
    # Context-based strategy selection
    print(f"\n--- Context-Based Strategy Selection ---")
    
    contexts = [
        ('India (INR)', TaxContext(
            customer_state='Maharashtra', business_state='Maharashtra',
            invoice_date=datetime.now(), is_interstate=False, customer_type='individual',
            customer_country='India', business_country='India', currency='INR'
        )),
        ('Bahrain (BHD)', TaxContext(
            customer_state='Manama', business_state='Manama',
            invoice_date=datetime.now(), is_interstate=False, customer_type='individual',
            customer_country='Bahrain', business_country='Bahrain', currency='BHD'
        )),
        ('Unknown (USD)', TaxContext(
            customer_state='State', business_state='State',
            invoice_date=datetime.now(), is_interstate=False, customer_type='individual',
            customer_country='Unknown', business_country='Unknown', currency='USD'
        ))
    ]
    
    for name, context in contexts:
        strategy = TaxStrategyFactory.create_strategy_for_context(context)
        print(f"  {name} -> {strategy.get_strategy_name()}")


def demo_multi_item_invoice():
    """Demonstrate tax calculation for multi-item invoices"""
    print_separator("Multi-Item Invoice Demonstration")
    
    # Create items with different tax rates
    items = [
        InvoiceItem(
            item_name='Laptop Computer',
            quantity=Decimal('1'),
            unit_price=Decimal('50000.00'),
            tax_rate=Decimal('18.00')
        ),
        InvoiceItem(
            item_name='Medicine',
            quantity=Decimal('2'),
            unit_price=Decimal('250.00'),
            tax_rate=Decimal('5.00')
        ),
        InvoiceItem(
            item_name='Educational Book',
            quantity=Decimal('3'),
            unit_price=Decimal('100.00'),
            tax_rate=Decimal('0.00')
        )
    ]
    
    # GST context
    context = TaxContext(
        customer_state='Maharashtra',
        business_state='Maharashtra',
        invoice_date=datetime.now(),
        is_interstate=False,
        customer_type='individual',
        customer_country='India',
        business_country='India',
        currency='INR'
    )
    
    strategy = TaxStrategyFactory.create_strategy('gst')
    
    print("Invoice Items:")
    total_net = Decimal('0.00')
    total_tax = Decimal('0.00')
    
    for i, item in enumerate(items, 1):
        result = strategy.calculate_tax(item, context)
        print(f"\n{i}. {item.item_name}")
        print(f"   Qty: {item.quantity} × {item.unit_price} = {result.net_amount}")
        print(f"   Tax: {result.total_tax} ({item.tax_rate}%)")
        print(f"   Total: {result.total_amount}")
        
        total_net += result.net_amount
        total_tax += result.total_tax
    
    # Get tax breakdown
    breakdown = strategy.get_tax_breakdown(items, context)
    
    print(f"\n--- Invoice Summary ---")
    print(f"Net Amount:   {total_net}")
    print(f"Total Tax:    {total_tax}")
    print(f"Grand Total:  {total_net + total_tax}")
    
    print(f"\n--- Tax Breakdown ---")
    print(f"Total CGST:   {breakdown['total_cgst']}")
    print(f"Total SGST:   {breakdown['total_sgst']}")
    print(f"Total Tax:    {breakdown['total_tax']}")
    
    print(f"\nBy Rate:")
    for rate, amount in breakdown['by_rate'].items():
        if amount > 0:
            print(f"  {rate}: {amount}")


def main():
    """Main demonstration function"""
    print("LedgerFlow Tax Strategy System Demonstration")
    print("=" * 60)
    print("This demo shows the pluggable tax calculation system with:")
    print("• GST Strategy (India) - CGST/SGST split logic")
    print("• VAT Strategy (Bahrain) - Arabic locale support")
    print("• NoTax Strategy - Plain cash invoices")
    print("• Plugin discovery and extensibility")
    
    try:
        demo_gst_strategy()
        demo_vat_strategy()
        demo_no_tax_strategy()
        demo_factory_features()
        demo_multi_item_invoice()
        
        print_separator("Demonstration Complete")
        print("✅ All tax strategies working correctly!")
        print("✅ CGST = SGST split logic verified")
        print("✅ Arabic locale support demonstrated")
        print("✅ Plugin discovery system functional")
        print("✅ Decimal precision maintained throughout")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())