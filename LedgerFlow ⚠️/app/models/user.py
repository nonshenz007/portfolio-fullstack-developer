from enum import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .base import db, BaseModel

class UserRole(Enum):
    """
    Enum for user roles.
    
    Values:
    - ADMIN: Full access to all features
    - AUDITOR: Can view invoices and export, but not modify settings
    - VIEWER: Read-only access, cannot export or access settings
    """
    ADMIN = "admin"
    AUDITOR = "auditor"
    VIEWER = "viewer"

class User(BaseModel, UserMixin):
    """
    User model for role-based access control.
    
    Features:
    - Flask-Login integration
    - Role-based permissions
    - Password hashing with Werkzeug
    - Session timeout support
    """
    __tablename__ = 'users'
    
    # User Information
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role and Permissions
    role = db.Column(db.Enum(UserRole, native_enum=False), default=UserRole.VIEWER, nullable=False)
    
    # Session Management
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Audit Fields
    created_by = db.Column(db.String(80))
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password: str):
        """
        Sets the user's password with secure hashing.
        
        Args:
            password: The plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Checks if the provided password matches the stored hash.
        
        Args:
            password: The plain text password to check
            
        Returns:
            Boolean indicating if password is correct
        """
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """
        Checks if the user has admin role.
        
        Returns:
            Boolean indicating if user is admin
        """
        return self.role == UserRole.ADMIN
    
    def is_auditor(self) -> bool:
        """
        Checks if the user has auditor role.
        
        Returns:
            Boolean indicating if user is auditor
        """
        return self.role == UserRole.AUDITOR
    
    def is_viewer(self) -> bool:
        """
        Checks if the user has viewer role.
        
        Returns:
            Boolean indicating if user is viewer
        """
        return self.role == UserRole.VIEWER
    
    def can_access_settings(self) -> bool:
        """
        Checks if the user can access settings.
        
        Returns:
            Boolean indicating if user can access settings
        """
        return self.is_admin()
    
    def can_export_invoices(self) -> bool:
        """
        Checks if the user can export invoices.
        
        Returns:
            Boolean indicating if user can export invoices
        """
        return self.is_admin() or self.is_auditor()
    
    def can_modify_simulation_config(self) -> bool:
        """
        Checks if the user can modify simulation configuration.
        
        Returns:
            Boolean indicating if user can modify simulation config
        """
        return self.is_admin()
    
    def can_upload_certificates(self) -> bool:
        """
        Checks if the user can upload digital certificates.
        
        Returns:
            Boolean indicating if user can upload certificates
        """
        return self.is_admin()
    
    def to_dict(self):
        """
        Converts the user to a dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the user
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'permissions': {
                'can_access_settings': self.can_access_settings(),
                'can_export_invoices': self.can_export_invoices(),
                'can_modify_simulation_config': self.can_modify_simulation_config(),
                'can_upload_certificates': self.can_upload_certificates()
            }
        }
    
    @classmethod
    def create_admin_user(cls, username: str, email: str, password: str) -> 'User':
        """
        Creates an admin user.
        
        Args:
            username: The username
            email: The email address
            password: The password
            
        Returns:
            The created user object
        """
        user = cls(
            username=username,
            email=email,
            role=UserRole.ADMIN
        )
        user.set_password(password)
        return user
    
    @classmethod
    def create_auditor_user(cls, username: str, email: str, password: str) -> 'User':
        """
        Creates an auditor user.
        
        Args:
            username: The username
            email: The email address
            password: The password
            
        Returns:
            The created user object
        """
        user = cls(
            username=username,
            email=email,
            role=UserRole.AUDITOR
        )
        user.set_password(password)
        return user
    
    @classmethod
    def create_viewer_user(cls, username: str, email: str, password: str) -> 'User':
        """
        Creates a viewer user.
        
        Args:
            username: The username
            email: The email address
            password: The password
            
        Returns:
            The created user object
        """
        user = cls(
            username=username,
            email=email,
            role=UserRole.VIEWER
        )
        user.set_password(password)
        return user 