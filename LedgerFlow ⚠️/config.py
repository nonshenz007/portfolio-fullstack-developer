import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App Configuration
    APP_NAME = "LedgerFlow"
    APP_VERSION = "1.0.0"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ledgerflow-secret-key-change-in-production'
    
    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "app/data/ledgerflow.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app/data/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    
    # Export Settings
    EXPORT_FOLDER = os.path.join(BASE_DIR, 'app/exports')
    PDF_TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'app/templates/pdf')
    
    # Invoice Generation Settings
    DEFAULT_INVOICE_COUNT = 100
    MAX_INVOICE_COUNT = 10000
    DEFAULT_DATE_RANGE_DAYS = 30
    
    # Realism Parameters (Default Values)
    DEFAULT_REALITY_BUFFER = 85  # 0-100, how closely to stick to realistic distribution
    DEFAULT_BELIEVABILITY_STRESS = 15  # 0-100, edge of legitimate appearance
    DEFAULT_DEVIATION_CONTROL = {
        'price_variance': 0.05,  # 5% price variance
        'quantity_min': 1,
        'quantity_max': 50,
        'customer_frequency_variance': 0.3
    }
    
    # Business Style Presets
    BUSINESS_STYLES = {
        'retail_shop': {
            'avg_items_per_invoice': 5,
            'price_range': (10, 5000),
            'customer_repeat_rate': 0.3
        },
        'distributor': {
            'avg_items_per_invoice': 15,
            'price_range': (100, 50000),
            'customer_repeat_rate': 0.7
        },
        'exporter': {
            'avg_items_per_invoice': 25,
            'price_range': (1000, 500000),
            'customer_repeat_rate': 0.6
        },
        'pharmacy': {
            'avg_items_per_invoice': 8,
            'price_range': (20, 2000),
            'customer_repeat_rate': 0.5
        },
        'it_service': {
            'avg_items_per_invoice': 3,
            'price_range': (5000, 200000),
            'customer_repeat_rate': 0.4
        }
    }
    
    # Tax Configuration
    GST_RATES = [0, 5, 12, 18, 28]  # Indian GST rates
    VAT_RATES = [0, 10]  # Bahrain VAT rates
    
    # Security & Admin
    ADMIN_PASSCODE_HASH = None  # Set during first run
    DEV_LICENSE_URL = os.environ.get('DEV_LICENSE_URL')
    ENABLE_REMOTE_LOCKOUT = True
    ENABLE_TAMPER_DETECTION = True
    
    # Logging
    LOG_FOLDER = os.path.join(BASE_DIR, 'app/logs')
    LOG_LEVEL = 'INFO'
    
    # Performance
    ENABLE_CACHING = True
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # UI Settings
    DEFAULT_THEME = 'light'
    ENABLE_ANIMATIONS = True
    PREVIEW_UPDATE_DELAY = 500  # milliseconds 