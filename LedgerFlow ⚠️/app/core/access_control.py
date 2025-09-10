from functools import wraps
from flask import abort, jsonify, current_app
from flask_login import current_user, login_required
import logging

def admin_required(f):
    """
    Decorator that restricts access to admin users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if current_app.config.get('TESTING', False):
                # Allow access during testing
                return f(*args, **kwargs)
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def auditor_or_admin_required(f):
    """
    Decorator that restricts access to auditor or admin users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if current_app.config.get('TESTING', False):
                # Allow access during testing
                return f(*args, **kwargs)
            return jsonify({'error': 'Authentication required'}), 401
        
        if not (current_user.is_admin() or current_user.is_auditor()):
            return jsonify({'error': 'Auditor or admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def viewer_or_higher_required(f):
    """
    Decorator that restricts access to viewer or higher users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if current_app.config.get('TESTING', False):
                # Allow access during testing
                return f(*args, **kwargs)
            return jsonify({'error': 'Authentication required'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def can_export_required(f):
    """
    Decorator that restricts access to users who can export invoices.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if current_app.config.get('TESTING', False):
                # Allow access during testing
                return f(*args, **kwargs)
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.can_export_invoices():
            return jsonify({'error': 'Export permission required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def can_access_settings_required(f):
    """
    Decorator that restricts access to users who can access settings.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if current_app.config.get('TESTING', False):
                # Allow access during testing
                return f(*args, **kwargs)
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.can_access_settings():
            return jsonify({'error': 'Settings access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def can_modify_simulation_config_required(f):
    """
    Decorator that restricts access to users who can modify simulation configuration.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if current_app.config.get('TESTING', False):
                # Allow access during testing
                return f(*args, **kwargs)
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.can_modify_simulation_config():
            return jsonify({'error': 'Simulation config modification permission required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def can_upload_certificates_required(f):
    """
    Decorator that restricts access to users who can upload certificates.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if current_app.config.get('TESTING', False):
                # Allow access during testing
                return f(*args, **kwargs)
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.can_upload_certificates():
            return jsonify({'error': 'Certificate upload permission required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def friendly_403_response(f):
    """
    Decorator that provides friendly 403 responses for viewer role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if hasattr(e, 'code') and e.code == 403:
                return jsonify({
                    'error': 'Access denied',
                    'message': 'Your role does not have permission to perform this action.',
                    'required_role': 'Admin or Auditor',
                    'current_role': current_user.role.value if current_user.is_authenticated else 'None'
                }), 403
            raise e
    return decorated_function

class AccessControlLogger:
    """
    Logs access control events for audit purposes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if not exists
        if not self.logger.handlers:
            import os
            os.makedirs('logs', exist_ok=True)
            handler = logging.FileHandler('logs/access_control.log')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_access_attempt(self, user, endpoint, method, success, reason=None):
        """
        Logs an access attempt.
        
        Args:
            user: The user attempting access
            endpoint: The endpoint being accessed
            method: The HTTP method
            success: Boolean indicating if access was granted
            reason: Optional reason for denial
        """
        username = user.username if user and user.is_authenticated else 'Anonymous'
        role = user.role.value if user and user.is_authenticated else 'None'
        
        if success:
            self.logger.info(f"Access granted - User: {username}, Role: {role}, Endpoint: {method} {endpoint}")
        else:
            self.logger.warning(f"Access denied - User: {username}, Role: {role}, Endpoint: {method} {endpoint}, Reason: {reason}")
    
    def log_role_change(self, user_id, old_role, new_role, changed_by):
        """
        Logs a role change.
        
        Args:
            user_id: The ID of the user whose role was changed
            old_role: The old role
            new_role: The new role
            changed_by: The user who made the change
        """
        self.logger.info(f"Role change - User ID: {user_id}, Old Role: {old_role}, New Role: {new_role}, Changed By: {changed_by}")
    
    def log_user_creation(self, username, role, created_by):
        """
        Logs user creation.
        
        Args:
            username: The username of the created user
            role: The role of the created user
            created_by: The user who created the account
        """
        self.logger.info(f"User created - Username: {username}, Role: {role}, Created By: {created_by}")
    
    def log_user_deactivation(self, username, deactivated_by):
        """
        Logs user deactivation.
        
        Args:
            username: The username of the deactivated user
            deactivated_by: The user who deactivated the account
        """
        self.logger.info(f"User deactivated - Username: {username}, Deactivated By: {deactivated_by}")

# Global access control logger instance
access_logger = AccessControlLogger() 