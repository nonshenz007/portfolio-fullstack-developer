from functools import wraps
from flask import session, redirect, url_for, jsonify, request
import hashlib
import os
from datetime import datetime, timedelta

def require_passcode(f):
    """Decorator to require passcode authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"DEBUG: require_passcode called for {f.__name__}")
        print(f"DEBUG: Session authenticated: {'authenticated' in session}")
        print(f"DEBUG: X-Passcode header: {request.headers.get('X-Passcode')}")
        
        # Check session authentication first
        if 'authenticated' in session:
            print("DEBUG: Using session authentication")
            return f(*args, **kwargs)
        
        # Check X-Passcode header as fallback
        passcode_header = request.headers.get('X-Passcode')
        if passcode_header:
            print(f"DEBUG: Attempting header authentication with: {passcode_header}")
            try:
                from app.core.security_manager import SecurityManager
                stored_hash = SecurityManager.load_passcode_hash()
                print(f"DEBUG: Stored hash loaded: {stored_hash is not None}")
                if stored_hash and SecurityManager.verify_passcode(passcode_header, stored_hash):
                    print("DEBUG: Header authentication successful")
                    return f(*args, **kwargs)
                else:
                    print(f"DEBUG: Passcode verification failed for: {passcode_header}")
            except Exception as e:
                print(f"DEBUG: Error in passcode verification: {e}")
                return jsonify({'error': f'Authentication error: {str(e)}'}), 500
        
        # Neither authentication method worked
        print("DEBUG: No authentication method worked")
        if request.is_json:
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('login'))
    return decorated_function

def check_integrity():
    """Calculate application integrity hash"""
    app_files = []
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Files to include in integrity check
    check_patterns = [
        '*.py',
        'templates/*.html',
        'static/js/*.js'
    ]
    
    hasher = hashlib.sha256()
    
    for root, dirs, files in os.walk(app_dir):
        # Skip data and export directories
        if any(skip in root for skip in ['data', 'exports', 'logs', '__pycache__']):
            continue
            
        for file in sorted(files):
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'rb') as f:
                        hasher.update(f.read())
                except:
                    pass
    
    return hasher.hexdigest()

def generate_license_key(company_name, license_type='basic', days_valid=365):
    """Generate a license key for the application"""
    import secrets
    from datetime import datetime, timedelta
    
    # Create license components
    prefix = license_type.upper()[:3]
    timestamp = int(datetime.now().timestamp())
    company_hash = hashlib.md5(company_name.encode()).hexdigest()[:8]
    random_part = secrets.token_hex(4)
    
    # Combine parts
    license_key = f"{prefix}-{company_hash}-{random_part}-{timestamp}"
    
    # Calculate expiry
    expiry_date = datetime.now() + timedelta(days=days_valid)
    
    return license_key.upper(), expiry_date

def validate_license_key(license_key):
    """Validate a license key format"""
    parts = license_key.split('-')
    
    if len(parts) != 4:
        return False
    
    # Check prefix
    valid_prefixes = ['BAS', 'PRE', 'ENT', 'TRI']  # Basic, Premium, Enterprise, Trial
    if parts[0] not in valid_prefixes:
        return False
    
    # Check timestamp
    try:
        timestamp = int(parts[3])
        # License can't be from the future
        if timestamp > int(datetime.now().timestamp()):
            return False
    except:
        return False
    
    return True 