from .base import db, BaseModel
from datetime import datetime, timedelta
import bcrypt
import secrets

class SecurityConfig(BaseModel):
    """Security configuration and access control"""
    __tablename__ = 'security_config'
    
    # Passcode Management
    passcode_hash = db.Column(db.String(255))
    admin_passcode_hash = db.Column(db.String(255))
    recovery_code = db.Column(db.String(100))
    
    # License Management
    license_key = db.Column(db.String(255))
    license_expiry = db.Column(db.DateTime)
    license_type = db.Column(db.String(50))  # trial, basic, premium, enterprise
    
    # Remote Control
    remote_lockout_enabled = db.Column(db.Boolean, default=False)
    lockout_message = db.Column(db.Text)
    last_license_check = db.Column(db.DateTime)
    
    # Tamper Detection
    app_hash = db.Column(db.String(64))  # SHA-256 of app files
    last_integrity_check = db.Column(db.DateTime)
    tamper_detected = db.Column(db.Boolean, default=False)
    
    # Session Management
    max_sessions = db.Column(db.Integer, default=1)
    session_timeout_minutes = db.Column(db.Integer, default=30)
    
    def __repr__(self):
        return f'<SecurityConfig {self.id}>'
    
    @classmethod
    def set_passcode(cls, passcode, is_admin=False):
        """Set user or admin passcode"""
        config = cls.query.first()
        if not config:
            config = cls()
            db.session.add(config)
        
        # Hash the passcode
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(passcode.encode('utf-8'), salt)
        
        if is_admin:
            config.admin_passcode_hash = hashed.decode('utf-8')
        else:
            config.passcode_hash = hashed.decode('utf-8')
        
        # Generate recovery code
        if not config.recovery_code:
            config.recovery_code = secrets.token_urlsafe(16)
        
        db.session.commit()
        return config.recovery_code
    
    @classmethod
    def verify_passcode(cls, passcode, is_admin=False):
        """Verify user or admin passcode"""
        config = cls.query.first()
        if not config:
            return False
        
        stored_hash = config.admin_passcode_hash if is_admin else config.passcode_hash
        if not stored_hash:
            return False
        
        return bcrypt.checkpw(passcode.encode('utf-8'), stored_hash.encode('utf-8'))
    
    @classmethod
    def check_license(cls):
        """Check license validity and remote lockout"""
        config = cls.query.first()
        if not config:
            return True, "No license configured"
        
        # Check expiry
        if config.license_expiry and config.license_expiry < datetime.utcnow():
            return False, "License expired"
        
        # Check remote lockout
        if config.remote_lockout_enabled:
            return False, config.lockout_message or "Application locked by administrator"
        
        # Update last check time
        config.last_license_check = datetime.utcnow()
        db.session.commit()
        
        return True, "License valid"
    
    @classmethod
    def verify_integrity(cls, current_hash):
        """Verify application integrity"""
        config = cls.query.first()
        if not config or not config.app_hash:
            # First run, store the hash
            if not config:
                config = cls()
                db.session.add(config)
            config.app_hash = current_hash
            config.last_integrity_check = datetime.utcnow()
            db.session.commit()
            return True
        
        # Check if hash matches
        if config.app_hash != current_hash:
            config.tamper_detected = True
            db.session.commit()
            return False
        
        config.last_integrity_check = datetime.utcnow()
        db.session.commit()
        return True


class AccessLog(BaseModel):
    """Track access attempts and sessions"""
    __tablename__ = 'access_logs'
    
    # Access Information
    access_type = db.Column(db.String(50))  # login, logout, failed_login, api_call
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    
    # Session Information
    session_id = db.Column(db.String(100))
    is_successful = db.Column(db.Boolean, default=True)
    failure_reason = db.Column(db.String(200))
    
    # Additional Data
    endpoint = db.Column(db.String(200))  # For API calls
    method = db.Column(db.String(10))  # GET, POST, etc.
    response_code = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<AccessLog {self.access_type} from {self.ip_address}>'
    
    @classmethod
    def log_access(cls, access_type, ip_address, user_agent=None, 
                   session_id=None, is_successful=True, failure_reason=None):
        """Log an access attempt"""
        log = cls(
            access_type=access_type,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            is_successful=is_successful,
            failure_reason=failure_reason
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
    
    @classmethod
    def check_brute_force(cls, ip_address, window_minutes=15, max_attempts=5):
        """Check for brute force attempts"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        failed_attempts = cls.query.filter(
            cls.ip_address == ip_address,
            cls.access_type == 'failed_login',
            cls.created_at > cutoff_time,
            cls.is_successful == False
        ).count()
        
        return failed_attempts >= max_attempts
    
    @classmethod
    def get_active_sessions(cls):
        """Get count of active sessions"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        
        return cls.query.filter(
            cls.access_type == 'login',
            cls.created_at > cutoff_time,
            cls.is_successful == True
        ).distinct(cls.session_id).count() 