from .base import db, BaseModel
from datetime import datetime, timedelta
import json

class Settings(BaseModel):
    """Application settings and configuration"""
    __tablename__ = 'settings'
    
    # General Settings
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(50))  # string, integer, float, boolean, json
    category = db.Column(db.String(50))  # general, invoice, security, export
    
    # Metadata
    description = db.Column(db.Text)
    is_system = db.Column(db.Boolean, default=False)  # System settings can't be deleted
    is_encrypted = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Setting {self.setting_key}>'
    
    @classmethod
    def get_value(cls, key, default=None):
        """Get setting value with type conversion"""
        setting = cls.query.filter_by(setting_key=key).first()
        if not setting:
            return default
        
        value = setting.setting_value
        
        if setting.setting_type == 'integer':
            return int(value)
        elif setting.setting_type == 'float':
            return float(value)
        elif setting.setting_type == 'boolean':
            return value.lower() in ('true', '1', 'yes', 'on')
        elif setting.setting_type == 'json':
            return json.loads(value)
        else:
            return value
    
    @classmethod
    def set_value(cls, key, value, setting_type='string', category='general', description=''):
        """Set or update setting value"""
        setting = cls.query.filter_by(setting_key=key).first()
        
        if not setting:
            setting = cls(
                setting_key=key,
                category=category,
                setting_type=setting_type,
                description=description
            )
            db.session.add(setting)
        
        # Convert value based on type
        if setting_type == 'json':
            value = json.dumps(value)
        else:
            value = str(value)
        
        setting.setting_value = value
        setting.setting_type = setting_type
        
        db.session.commit()
        return setting
    
    @classmethod
    def initialize_defaults(cls):
        """Initialize default settings"""
        defaults = [
            # Business Information
            ('business_name', 'Your Business Name', 'string', 'business', 'Company name for invoices'),
            ('business_address', 'Your Business Address', 'string', 'business', 'Company address'),
            ('business_gst', '', 'string', 'business', 'GST number for Indian invoices'),
            ('business_vat', '', 'string', 'business', 'VAT number for Bahrain invoices'),
            ('business_phone', '', 'string', 'business', 'Business contact number'),
            ('business_email', '', 'string', 'business', 'Business email'),
            
            # Invoice Generation
            ('default_invoice_prefix', 'INV', 'string', 'invoice', 'Default invoice number prefix'),
            ('default_business_style', 'retail_shop', 'string', 'invoice', 'Default business style'),
            ('default_reality_buffer', '85', 'integer', 'invoice', 'Default realism level (0-100)'),
            ('default_believability_stress', '15', 'integer', 'invoice', 'Default stress level (0-100)'),
            ('enable_smart_entropy', 'true', 'boolean', 'invoice', 'Enable AI-driven anomalies'),
            ('customer_web_density', '0.7', 'float', 'invoice', 'Customer repeat rate density'),
            
            # Export Settings
            ('pdf_page_size', 'A4', 'string', 'export', 'PDF page size'),
            ('pdf_include_watermark', 'false', 'boolean', 'export', 'Include watermark in PDFs'),
            ('excel_color_coding', 'true', 'boolean', 'export', 'Enable color coding in Excel'),
            ('zip_folder_structure', 'date_based', 'string', 'export', 'ZIP folder organization'),
            
            # Security
            ('require_passcode', 'true', 'boolean', 'security', 'Require passcode on startup'),
            ('session_timeout_minutes', '30', 'integer', 'security', 'Session timeout in minutes'),
            ('enable_audit_log', 'true', 'boolean', 'security', 'Enable audit logging'),
            ('enable_verichain', 'true', 'boolean', 'security', 'Enable tamper detection'),
            
            # UI Settings
            ('theme', 'light', 'string', 'ui', 'UI theme (light/dark)'),
            ('enable_animations', 'true', 'boolean', 'ui', 'Enable UI animations'),
            ('preview_auto_refresh', 'true', 'boolean', 'ui', 'Auto-refresh preview'),
            ('show_tooltips', 'true', 'boolean', 'ui', 'Show helpful tooltips'),
        ]
        
        for key, value, type_, category, description in defaults:
            existing = cls.query.filter_by(setting_key=key).first()
            if not existing:
                cls.set_value(key, value, type_, category, description)


class AuditLog(BaseModel):
    """Audit trail for tracking system activities"""
    __tablename__ = 'audit_logs'
    
    # Log Information
    action = db.Column(db.String(100), nullable=False)  # login, generate_invoices, export, etc.
    module = db.Column(db.String(50))  # InvoCodex, BillForge, etc.
    severity = db.Column(db.String(20), default='info')  # info, warning, error, critical
    
    # User Information
    user_id = db.Column(db.Integer)
    user_ip = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    
    # Action Details
    details = db.Column(db.JSON)
    affected_records = db.Column(db.Integer, default=0)
    
    # Results
    status = db.Column(db.String(20), default='success')  # success, failure, partial
    error_message = db.Column(db.Text)
    
    # Performance
    execution_time = db.Column(db.Float)  # in seconds
    
    def __repr__(self):
        return f'<AuditLog {self.action} at {self.created_at}>'
    
    @classmethod
    def log_action(cls, action, module=None, details=None, status='success', 
                   error_message=None, severity='info', execution_time=None):
        """Create audit log entry"""
        # Convert datetime objects to strings for JSON serialization
        if details:
            details = cls._serialize_details(details)
        
        log = cls(
            action=action,
            module=module,
            severity=severity,
            details=details,
            status=status,
            error_message=error_message,
            execution_time=execution_time
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
    
    @classmethod
    def _serialize_details(cls, details):
        """Convert datetime objects to strings for JSON serialization"""
        if isinstance(details, dict):
            serialized = {}
            for key, value in details.items():
                if hasattr(value, 'isoformat'):  # datetime object
                    serialized[key] = value.isoformat()
                elif isinstance(value, dict):
                    # Recursively handle nested dictionaries
                    serialized[key] = cls._serialize_details(value)
                elif isinstance(value, list):
                    # Handle lists that may contain datetime objects or nested structures
                    serialized[key] = [
                        item.isoformat() if hasattr(item, 'isoformat') 
                        else cls._serialize_details(item) if isinstance(item, (dict, list))
                        else item 
                        for item in value
                    ]
                else:
                    serialized[key] = value
            return serialized
        elif isinstance(details, list):
            # Handle lists at the top level
            return [
                item.isoformat() if hasattr(item, 'isoformat')
                else cls._serialize_details(item) if isinstance(item, (dict, list))
                else item
                for item in details
            ]
        else:
            # Handle single values
            return details.isoformat() if hasattr(details, 'isoformat') else details
    
    @classmethod
    def get_recent_logs(cls, limit=100, severity=None, module=None):
        """Get recent audit logs with optional filtering"""
        query = cls.query.order_by(cls.created_at.desc())
        
        if severity:
            query = query.filter_by(severity=severity)
        
        if module:
            query = query.filter_by(module=module)
        
        return query.limit(limit).all()
    
    @classmethod
    def cleanup_old_logs(cls, days_to_keep=90):
        """Remove old audit logs"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        deleted = cls.query.filter(cls.created_at < cutoff_date).delete()
        db.session.commit()
        
        return deleted 