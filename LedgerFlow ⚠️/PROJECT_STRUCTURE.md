# LedgerFlow Project Structure

## Overview
LedgerFlow is a professional invoice generation system with Excel import capabilities, PDF export, and comprehensive business management features.

## Directory Structure

```
LedgerFlow/
├── app/                          # Main application package
│   ├── __init__.py              # App initialization
│   ├── api/                     # API routes and endpoints
│   ├── core/                    # Core business logic modules
│   │   ├── __init__.py
│   │   ├── access_control.py    # Role-based access control
│   │   ├── auth_controller.py   # Authentication management
│   │   ├── certificate_manager.py # Digital certificate handling
│   │   ├── comparison_engine.py # Data comparison utilities
│   │   ├── customer_name_generator.py # Customer name generation
│   │   ├── diagnostic_controller.py # System diagnostics
│   │   ├── diagnostics_logger.py # Logging system
│   │   ├── excel_importer.py    # Excel file import logic
│   │   ├── excel_template.py    # Excel template generation
│   │   ├── export_controller.py # Export management
│   │   ├── export_manager.py    # File export handling
│   │   ├── fix_engine.py        # Data correction utilities
│   │   ├── gst_packager.py      # GST compliance packaging
│   │   ├── invoice_simulator.py # Invoice simulation engine
│   │   ├── json_generator.py    # JSON data generation
│   │   ├── master_simulation_engine.py # Main simulation engine
│   │   ├── pdf_signer.py        # PDF digital signing
│   │   ├── pdf_template_engine.py # PDF template system (consolidated)
│   │   ├── product_catalog.py   # Product management
│   │   ├── security_manager.py  # Security management
│   │   ├── simulation_config_manager.py # Simulation configuration
│   │   ├── timeflow_engine.py   # Time-based data generation
│   │   ├── verichain_engine.py  # Verification chain system
│   │   └── verification_engine.py # Data verification
│   ├── data/                    # Data storage
│   │   ├── uploads/             # File uploads
│   │   ├── exports/             # Export files
│   │   └── passcode.hash        # Security hash
│   ├── exports/                 # Generated exports
│   ├── logs/                    # Application logs
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── base.py              # Base model class
│   │   ├── customer.py          # Customer model
│   │   ├── invoice.py           # Invoice model
│   │   ├── product.py           # Product model
│   │   ├── security.py          # Security model
│   │   ├── settings.py          # Settings model
│   │   ├── template_type.py     # Template model
│   │   └── user.py              # User model
│   ├── services/                # Business services
│   │   ├── __init__.py
│   │   ├── excel_exporter.py    # Excel export service
│   │   ├── excel_importer.py    # Excel import service
│   │   ├── invoice_generator.py # Invoice generation service
│   │   └── pdf_exporter.py      # PDF export service
│   ├── static/                  # Static assets
│   │   ├── assets/              # Images and other assets
│   │   │   └── logo.png         # Application logo
│   │   ├── css/                 # Stylesheets
│   │   │   ├── apple.css        # Apple-style framework
│   │   │   ├── style.css        # Main styles
│   │   │   └── tailwind.css     # Tailwind utilities
│   │   └── js/                  # JavaScript files
│   │       ├── form-submission.js # Form handling
│   │       ├── main.js          # Main application logic
│   │       ├── settings.js      # Settings management
│   │       ├── toast.js         # Toast notifications
│   │       └── ui.js            # UI utilities
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── security.py          # Security utilities
├── templates/                   # HTML templates
│   ├── base.html               # Base template
│   ├── dashboard.html          # Dashboard page
│   ├── export.html             # Export page
│   ├── generate.html           # Invoice generation page
│   ├── header.html             # Header component
│   ├── home.html               # Home page
│   ├── import.html             # Import page
│   ├── index.html              # Index page
│   ├── login.html              # Login page
│   ├── manual.html             # Manual invoice page
│   ├── onboarding.html         # Onboarding page
│   ├── pdf/                    # PDF templates
│   │   ├── bahrain_vat.html    # Bahrain VAT template
│   │   ├── gst_einvoice.html   # GST e-invoice template
│   │   └── plain_cash.html     # Plain cash template
│   ├── settings.html           # Settings page
│   └── sidebar.html            # Sidebar component
├── tests/                      # Test files
│   ├── test_import.py          # Import functionality tests
│   └── test_import_functionality.py # Excel import tests
├── docs/                       # Documentation
│   ├── CHANGELOG.md            # Change log
│   └── VAT_TAX_FIX.md          # VAT tax fixes
├── schemas/                    # XML schemas
│   ├── bahrain_nbr_1.0.xsd     # Bahrain NBR schema
│   └── gst_irp_1.1.xsd         # GST IRP schema
├── spec/                       # Specifications
│   ├── design.md               # Design specifications
│   ├── requirements.md         # Requirements
│   └── tasks.md                # Task specifications
├── instance/                   # Instance-specific files
│   └── certificates/           # Digital certificates
├── logs/                       # Application logs
├── venv/                       # Virtual environment
├── .venv/                      # Alternative virtual environment
├── .git/                       # Git repository
├── .vscode/                    # VS Code configuration
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── debug_app.py                # Debug application
├── .gitignore                  # Git ignore rules
├── PROJECT_STRUCTURE.md        # This file
└── README.md                   # Project readme
```

## Key Features

### Excel Import Functionality
- **File Upload**: Supports .xlsx and .xls files
- **Column Mapping**: Automatically maps common column names
- **Data Validation**: Validates required fields and data types
- **Template Download**: Provides downloadable Excel template
- **Batch Processing**: Handles large product catalogs efficiently

### Required Excel Columns
- **Product Name** (required): Product name/description
- **Base Price** (required): Product selling price
- **SKU/HSN** (optional): Product code or HSN code
- **Category** (optional): Product category
- **GST Rate** (optional): GST percentage (default: 18%)
- **VAT Rate** (optional): VAT percentage (default: 10%)
- **Unit** (optional): Unit of measurement (default: Nos)
- **Quantity** (optional): Stock quantity

### API Endpoints

#### Import Related
- `POST /api/products/import` - Import products from Excel
- `GET /api/products` - Get all products
- `POST /api/products/delete-all` - Delete all products
- `DELETE /api/products/<id>` - Delete specific product
- `GET /api/template/download` - Download Excel template

#### Authentication
- `POST /api/verify-passcode` - Verify user passcode
- `GET /login` - Login page
- `GET /logout` - Logout

#### Pages
- `GET /import` - Import page
- `GET /generate` - Invoice generation page
- `GET /export` - Export page
- `GET /settings` - Settings page
- `GET /dashboard` - Dashboard page

## Security Features
- Passcode-based authentication
- Role-based access control
- Digital certificate support
- Audit logging
- Data integrity verification

## File Organization
- **Clean Structure**: Removed all test files from root directory
- **Proper Separation**: Tests moved to dedicated `tests/` directory
- **Asset Organization**: Static files properly organized
- **Template Structure**: HTML templates with clear hierarchy

## Development Setup
1. Activate virtual environment: `source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run application: `python app.py`
4. Access application: `http://localhost:5000`

## Testing
- Excel import functionality tested and verified
- All API endpoints properly configured
- Frontend-backend integration working
- File upload/download functionality operational 