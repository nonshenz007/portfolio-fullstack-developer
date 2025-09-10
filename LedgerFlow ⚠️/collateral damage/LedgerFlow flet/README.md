# LedgerFlow - Invoice Generator

A professional desktop invoice generator app for Indian and Bahrain businesses. Generate realistic batch invoices with proper GST/VAT calculations.

## Features

✅ **3 Invoice Templates**
- **Plain Invoice**: Simple cash transactions, no tax calculations
- **GST Invoice**: Indian businesses with CGST+SGST breakdown, HSN codes
- **VAT Invoice**: Bahrain businesses with 0%/10% VAT rates, BHD currency

✅ **Smart Generation**
- Revenue target accuracy (±5% variance)
- Realistic business catalogs (Medical, Grocery, Textile, etc.)
- Indian/Muslim customer names database
- Proper tax calculations and compliance

✅ **Professional UI**
- 3-step workflow (Template → Catalog → Generate)
- Live preview with summary statistics
- Export options (PDF, Excel, CSV)

## Quick Start

### Windows Users (Recommended)

**Option 1: Use the Windows Launcher**
```cmd
run_ledgerflow.bat
```

**Option 2: Python Launcher**
```cmd
python run_app.py
```

### All Platforms

**Standard Method:**
```bash
python main.py
```

## Requirements

- Python 3.8+
- Required packages: `flet`

### Installation

1. **Clone or Download**
   ```bash
   git clone <repository-url>
   cd LedgerFlow
   ```

2. **Install Dependencies**
   ```bash
   pip install flet
   ```

3. **Run Application**
   ```bash
   # Windows (recommended)
   run_ledgerflow.bat
   
   # Or standard Python
   python main.py
   ```

## Usage Guide

### Step 1: Choose Template
- **Plain**: For simple cash transactions
- **GST**: For Indian businesses (₹ currency, tax calculations)
- **VAT**: For Bahrain businesses (BD currency, VAT rates)

### Step 2: Product Catalog
- **Upload Excel/CSV**: Custom product list with Name, Price, Category
- **Use Defaults**: Built-in catalogs for different business types

### Step 3: Generate Invoices
- Set revenue target
- Choose date range
- Select business style
- Click "Generate Invoices"

### Export Options
- **PDF**: Professional invoice documents
- **Excel**: Spreadsheet format for analysis
- **CSV**: Raw data for import/processing

## Business Styles

| Style | Description | Typical Items |
|-------|-------------|---------------|
| Desi Medical | Medical supplies & medicines | Tablets, Syrups, Equipment |
| Grocery | Food & daily essentials | Rice, Dal, Oil, Spices |
| Textile | Clothing & fabric | Sarees, Kurtas, Bed sheets |
| Wholesale | Bulk business | Large quantities |
| Retail | Consumer electronics | Phones, Gadgets |
| Casual | Office supplies | Stationery, Cables |
| Luxury | High-end items | Jewelry, Premium goods |

## Tax Calculations

### GST Invoice (India)
- **5%**: Essential medicines, food items
- **12%**: Medical equipment, processed foods, textiles
- **18%**: Standard rate for most items
- **28%**: Luxury items
- **Split**: CGST + SGST (50/50)

### VAT Invoice (Bahrain)
- **0%**: Essential items (milk, medicine, etc.)
- **10%**: Standard VAT rate
- **Currency**: Bahrain Dinar (BD)

## Troubleshooting

### Common Issues

**❌ "Event loop is closed" Error (Windows)**
- **Solution**: Use `run_app.py` or `run_ledgerflow.bat`
- **Cause**: Windows asyncio compatibility issue

**❌ "No business style selected"**
- **Solution**: Dropdown now defaults to "Desi Medical"
- **Check**: Make sure you're using the latest version

**❌ Import errors**
- **Solution**: Install Flet: `pip install flet`
- **Check**: Python version 3.8+

**❌ Application won't start**
- **Try**: Use the batch file on Windows
- **Check**: Python is in system PATH
- **Fallback**: Run `python -m flet run main.py`

### Windows-Specific Solutions

1. **Use the launcher script**: `python run_app.py`
2. **Use the batch file**: `run_ledgerflow.bat`
3. **Check Python PATH**: Ensure Python is accessible from command line

### Debug Mode

To see detailed logs:
```bash
python main.py --verbose
```

## File Structure

```
LedgerFlow/
├── main.py              # Main application entry
├── run_app.py           # Windows-optimized launcher  
├── run_ledgerflow.bat   # Windows batch launcher
├── pages/
│   ├── dashboard.py     # Main UI & invoice generation
│   ├── invoices.py      # Invoice management
│   └── settings.py      # App settings
├── utils/
│   ├── invoice_generator.py  # Core generation engine
│   └── formatter.py     # Data formatting utilities
├── components/          # Reusable UI components
├── templates/           # Invoice templates
└── data/               # Sample data files
```

## Development

### Testing Invoice Generation
```python
from utils.invoice_generator import test_generator
test_generator()  # Tests all 3 template types
```

### Adding New Templates
1. Update `generate_plain_invoices()` in `utils/invoice_generator.py`
2. Add template selection in `pages/dashboard.py`
3. Implement export logic for new format

## License

This project is for educational and business use. Please ensure compliance with local tax regulations when using generated invoices.

## Support

For issues:
1. Check this troubleshooting guide
2. Ensure you're using Python 3.8+
3. Try the Windows launcher scripts
4. Check console output for specific errors

---

**Version**: 1.0  
**Platform**: Windows, macOS, Linux  
**Python**: 3.8+ 