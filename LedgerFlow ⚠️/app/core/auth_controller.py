from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta
import logging
from typing import Optional
from app.models.user import User, UserRole

class AuthController:
    """
    Handles user authentication and session management.
    
    Features:
    - Flask-Login integration
    - Role-based access control
    - Session timeout (30 minutes)
    - Password verification
    - User management
    """
    
    def __init__(self, app):
        """
        Initializes the authentication controller.
        
        Args:
            app: The Flask application
        """
        self.app = app
        self.login_manager = LoginManager(app)
        self.login_manager.login_view = "login"
        self.login_manager.session_protection = "strong"
        
        # Set session timeout to 30 minutes
        app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if not exists
        if not self.logger.handlers:
            import os
            os.makedirs('logs', exist_ok=True)
            handler = logging.FileHandler('logs/auth.log')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Set up user loader
        @self.login_manager.user_loader
        def load_user(user_id):
            return self._get_user_by_id(user_id)
        
        # Set up unauthorized handler
        @self.login_manager.unauthorized_handler
        def unauthorized():
            return redirect(url_for('login'))
    
    def login(self, username: str, password: str) -> bool:
        """
        Authenticates a user and creates a session.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            Boolean indicating if login was successful
        """
        try:
            user = self._authenticate(username, password)
            if user and user.is_active:
                login_user(user, remember=True)
                user.last_login = datetime.utcnow()
                
                # Save to database
                from app.models.base import db
                db.session.commit()
                
                self.logger.info(f"User {username} logged in successfully")
                return True
            else:
                self.logger.warning(f"Failed login attempt for username: {username}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def logout(self):
        """
        Logs out the current user.
        """
        if current_user.is_authenticated:
            self.logger.info(f"User {current_user.username} logged out")
            logout_user()
    
    def _authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticates a user with username and password.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                return user
            return None
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return None
    
    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Gets a user by ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            self.logger.error(f"Error getting user by ID: {e}")
            return None
    
    def create_initial_admin(self, username: str, email: str, password: str) -> bool:
        """
        Creates the initial admin user if no users exist.
        
        Args:
            username: The admin username
            email: The admin email
            password: The admin password
            
        Returns:
            Boolean indicating success
        """
        try:
            # Check if any users exist
            if User.query.first() is not None:
                self.logger.info("Users already exist, skipping initial admin creation")
                return False
            
            # Create admin user
            admin_user = User.create_admin_user(username, email, password)
            
            # Save to database
            from app.models.base import db
            db.session.add(admin_user)
            db.session.commit()
            
            self.logger.info(f"Initial admin user {username} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating initial admin: {e}")
            return False
    
    def create_user(self, username: str, email: str, password: str, role: UserRole, created_by: str = None) -> Optional[User]:
        """
        Creates a new user.
        
        Args:
            username: The username
            email: The email
            password: The password
            role: The user role
            created_by: The username of the user creating this account
            
        Returns:
            The created user object or None if failed
        """
        try:
            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                self.logger.error(f"Username {username} already exists")
                return None
            
            if User.query.filter_by(email=email).first():
                self.logger.error(f"Email {email} already exists")
                return None
            
            # Create user based on role
            if role == UserRole.ADMIN:
                user = User.create_admin_user(username, email, password)
            elif role == UserRole.AUDITOR:
                user = User.create_auditor_user(username, email, password)
            else:
                user = User.create_viewer_user(username, email, password)
            
            user.created_by = created_by
            
            # Save to database
            from app.models.base import db
            db.session.add(user)
            db.session.commit()
            
            self.logger.info(f"User {username} created successfully with role {role.value}")
            return user
            
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return None
    
    def update_user_role(self, user_id: int, new_role: UserRole, updated_by: str) -> bool:
        """
        Updates a user's role.
        
        Args:
            user_id: The user ID
            new_role: The new role
            updated_by: The username of the user making the change
            
        Returns:
            Boolean indicating success
        """
        try:
            user = User.query.get(user_id)
            if not user:
                self.logger.error(f"User with ID {user_id} not found")
                return False
            
            old_role = user.role
            user.role = new_role
            
            # Save to database
            from app.models.base import db
            db.session.commit()
            
            self.logger.info(f"User {user.username} role changed from {old_role.value} to {new_role.value} by {updated_by}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating user role: {e}")
            return False
    
    def deactivate_user(self, user_id: int, deactivated_by: str) -> bool:
        """
        Deactivates a user account.
        
        Args:
            user_id: The user ID
            deactivated_by: The username of the user making the change
            
        Returns:
            Boolean indicating success
        """
        try:
            user = User.query.get(user_id)
            if not user:
                self.logger.error(f"User with ID {user_id} not found")
                return False
            
            user.is_active = False
            
            # Save to database
            from app.models.base import db
            db.session.commit()
            
            self.logger.info(f"User {user.username} deactivated by {deactivated_by}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deactivating user: {e}")
            return False
    
    def get_all_users(self) -> list:
        """
        Gets all users.
        
        Returns:
            List of user dictionaries
        """
        try:
            users = User.query.all()
            return [user.to_dict() for user in users]
        except Exception as e:
            self.logger.error(f"Error getting users: {e}")
            return []
    
    def check_session_timeout(self) -> bool:
        """
        Checks if the current session has timed out.
        
        Returns:
            Boolean indicating if session has timed out
        """
        if not current_user.is_authenticated:
            return True
        
        # Check if session is permanent and has expired
        if session.get('_permanent', False):
            session_lifetime = self.app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(minutes=30))
            session_start = session.get('_session_start')
            
            if session_start:
                session_start = datetime.fromisoformat(session_start)
                if datetime.utcnow() - session_start > session_lifetime:
                    self.logger.info(f"Session timed out for user {current_user.username}")
                    return True
        
        return False 