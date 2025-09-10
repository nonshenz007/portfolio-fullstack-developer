"""
Global pytest configuration and fixtures for the test suite.
"""
import pytest
import tempfile
import os
from decimal import Decimal
from typing import Dict, Any, List
from unittest.mock import Mock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.base import db
# Import these only when needed to avoid circular imports


@pytest.fixture(scope="session")
def app():
    """Create application for testing"""
    from flask import Flask
    from config import Config
    
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create test app
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def config_manager():
    """Create configuration manager for testing"""
    from app.core.config_manager import ConfigurationManager
    return ConfigurationManager()


@pytest.fixture
def tax_strategy_factory():
    """Create tax strategy factory for testing"""
    from app.core.tax_strategies.factory import TaxStrategyFactory
    return TaxStrategyFactory()


@pytest.fixture
def atomic_counter_service():
    """Create atomic counter service for testing"""
    from app.services.counter.atomic_counter_service import AtomicCounterService
    return AtomicCounterService(use_redis=False, use_postgres=False)


@pytest.fixture
def sample_products() -> List[Dict[str, Any]]:
    """Create sample products for testing"""
    return [
        {
            "name": "Laptop Computer",
            "base_price": Decimal("50000.00"),
            "category": "Electronics",
            "tax_rate": Decimal("18.00"),
            "hsn_code": "8471"
        },
        {
            "name": "Office Chair",
            "base_price": Decimal("5000.00"),
            "category": "Furniture",
            "tax_rate": Decimal("12.00"),
            "hsn_code": "9401"
        },
        {
            "name": "Mobile Phone",
            "base_price": Decimal("25000.00"),
            "category": "Electronics",
            "tax_rate": Decimal("18.00"),
            "hsn_code": "8517"
        },
        {
            "name": "Desk Lamp",
            "base_price": Decimal("1500.00"),
            "category": "Lighting",
            "tax_rate": Decimal("12.00"),
            "hsn_code": "9405"
        },
        {
            "name": "Printer",
            "base_price": Decimal("15000.00"),
            "category": "Electronics",
            "tax_rate": Decimal("18.00"),
            "hsn_code": "8443"
        }
    ]


@pytest.fixture
def sample_customers() -> List[Dict[str, Any]]:
    """Create sample customers for testing"""
    return [
        {
            "name": "Acme Corporation",
            "address": "123 Business Street, Bangalore, Karnataka",
            "gstin": "29ABCDE1234F1Z5",
            "customer_type": "business",
            "state": "Karnataka"
        },
        {
            "name": "John Doe",
            "address": "456 Residential Road, Mumbai, Maharashtra",
            "gstin": None,
            "customer_type": "individual",
            "state": "Maharashtra"
        },
        {
            "name": "Tech Solutions Pvt Ltd",
            "address": "789 Tech Park, Hyderabad, Telangana",
            "gstin": "36FGHIJ5678K2L9",
            "customer_type": "business",
            "state": "Telangana"
        }
    ]


@pytest.fixture
def gst_simulation_config() -> Dict[str, Any]:
    """Create GST simulation configuration for testing"""
    return {
        "invoice_count": 10,
        "invoice_type": "gst",
        "date_range": {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        },
        "customer_config": {
            "generate_customers": True,
            "customer_count": 5,
            "customer_types": ["individual", "business"]
        },
        "realism_profile": "basic",
        "tax_config": {
            "default_tax_rate": Decimal("18.00"),
            "tax_inclusive": False
        },
        "business_config": {
            "business_name": "Test Company Ltd",
            "business_address": "123 Test Street, Test City",
            "tax_number": "29ABCDE1234F1Z5"
        }
    }


@pytest.fixture
def vat_simulation_config() -> Dict[str, Any]:
    """Create VAT simulation configuration for testing"""
    return {
        "invoice_count": 10,
        "invoice_type": "vat",
        "date_range": {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        },
        "customer_config": {
            "generate_customers": True,
            "customer_count": 5,
            "customer_types": ["individual", "business"]
        },
        "realism_profile": "basic",
        "tax_config": {
            "default_tax_rate": Decimal("5.00"),
            "tax_inclusive": False
        },
        "business_config": {
            "business_name": "شركة الاختبار المحدودة",  # Arabic business name
            "business_address": "123 شارع الاختبار، المنامة، البحرين",
            "tax_number": "123456789"
        }
    }


@pytest.fixture
def mock_pdf_generator():
    """Create mock PDF generator for testing"""
    mock = Mock()
    mock.generate_pdf.return_value = b"fake-pdf-content"
    mock.validate_pdf.return_value = True
    return mock


@pytest.fixture
def mock_redis():
    """Create mock Redis client for testing"""
    mock = Mock()
    mock.incr.return_value = 1
    mock.get.return_value = None
    mock.set.return_value = True
    mock.ping.return_value = True
    return mock


@pytest.fixture
def mock_database():
    """Create mock database for testing"""
    mock = Mock()
    mock.execute.return_value = Mock(fetchone=lambda: (1,))
    mock.commit.return_value = None
    mock.rollback.return_value = None
    return mock


# Performance testing fixtures
@pytest.fixture
def performance_config() -> Dict[str, Any]:
    """Configuration optimized for performance testing"""
    return {
        "invoice_count": 100,
        "invoice_type": "gst",
        "date_range": {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        },
        "customer_config": {
            "generate_customers": True,
            "customer_count": 50,
            "customer_types": ["individual", "business"]
        },
        "realism_profile": "realistic",
        "tax_config": {
            "default_tax_rate": Decimal("18.00"),
            "tax_inclusive": False
        },
        "business_config": {
            "business_name": "Performance Test Company",
            "business_address": "Performance Test Address",
            "tax_number": "29PERF1234T5T6"
        },
        "performance_mode": True  # Enable optimizations for testing
    }


# Markers for test categorization
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "property: mark test as a property-based test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location and name"""
    for item in items:
        # Mark tests in perf/ directory as performance tests
        if "perf/" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        
        # Mark property-based tests
        if "property" in item.name or "test_property_based.py" in str(item.fspath):
            item.add_marker(pytest.mark.property)
        
        # Mark integration tests
        if "integration" in item.name or "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if any(keyword in item.name for keyword in ["100", "performance", "stress", "load"]):
            item.add_marker(pytest.mark.slow)
        
        # Default to unit test if no other marker
        if not any(marker.name in ["integration", "property", "performance"] 
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)