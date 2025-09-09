"""
Role-Based Access Control (RBAC) System

Implements military-grade access control with role-based permissions,
session management, and security policy enforcement.
"""

import os
import json
import hashlib
import secrets
import sqlite3
import threading
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import bcrypt
import logging

from ..contracts import IAccessControl, SecurityContext, SecurityLevel


@dataclass
class User:
    """User account definition"""
    user_id: str
    username: str
    password_hash: str
    security_level: SecurityLevel
    roles: List[str]
    permissions: List[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    failed_attempts: int
    locked_until: Optional[datetime]


@dataclass
class Role:
    """Role definition with permissions"""
    role_id: str
    role_name: str
    description: str
    permissions: List[str]
    security_level_required: SecurityLevel
    is_active: bool


@dataclass
class Session:
    """User session"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    ip_address: Optional[str]
    is_active: bool


class RoleBasedAccessControl(IAccessControl):
    """
    Military-grade RBAC system with:
    - Multi-factor authentication support
    - Session management with timeout
    - Role-based permission system
    - Security policy enforcement
    - Audit logging integration
    """
    
    def __init__(self, db_path: str = "secure/rbac.db", 
                 session_timeout_minutes: int = 30,
                 max_failed_attempts: int = 3,
                 lockout_duration_minutes: int = 15):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration = timedelta(minutes=lockout_duration_minutes)
        self.lock = threading.Lock()
        
        # Initialize database
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._initialize_rbac_database()
        
        # Initialize default roles and admin user
        self._initialize_default_roles()
        self._initialize_admin_user()
        
        # Active sessions cache
        self.active_sessions: Dict[str, Session] = {}
        
        self.logger.info("RBAC system initialized")
    
    def _initialize_rbac_database(self):
        """Initialize RBAC database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Users table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        security_level TEXT NOT NULL,
                        roles TEXT NOT NULL,
                        permissions TEXT NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL,
                        last_login TEXT,
                        failed_attempts INTEGER DEFAULT 0,
                        locked_until TEXT
                    )
                """)
                
                # Roles table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS roles (
                        role_id TEXT PRIMARY KEY,
                        role_name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        permissions TEXT NOT NULL,
                        security_level_required TEXT NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT 1
                    )
                """)
                
                # Sessions table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_activity TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        ip_address TEXT,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # Access logs table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS access_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        resource TEXT NOT NULL,
                        action TEXT NOT NULL,
                        result TEXT NOT NULL,
                        ip_address TEXT,
                        details TEXT
                    )
                """)
                
                # Create indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp)")
                
                conn.commit()
                self.logger.info("RBAC database schema initialized")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize RBAC database: {e}")
            raise
    
    def _initialize_default_roles(self):
        """Initialize default system roles"""
        default_roles = [
            Role(
                role_id="admin",
                role_name="Administrator",
                description="Full system administration access",
                permissions=["READ", "WRITE", "ADMIN", "SECURITY", "USER_MANAGEMENT"],
                security_level_required=SecurityLevel.SECRET,
                is_active=True
            ),
            Role(
                role_id="operator",
                role_name="System Operator",
                description="Standard processing operations",
                permissions=["READ", "WRITE", "PROCESS"],
                security_level_required=SecurityLevel.CONFIDENTIAL,
                is_active=True
            ),
            Role(
                role_id="viewer",
                role_name="Viewer",
                description="Read-only access to system",
                permissions=["READ"],
                security_level_required=SecurityLevel.UNCLASSIFIED,
                is_active=True
            ),
            Role(
                role_id="security_officer",
                role_name="Security Officer",
                description="Security monitoring and audit access",
                permissions=["READ", "SECURITY", "AUDIT"],
                security_level_required=SecurityLevel.SECRET,
                is_active=True
            )
        ]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                for role in default_roles:
                    # Check if role exists
                    cursor = conn.execute("SELECT role_id FROM roles WHERE role_id = ?", (role.role_id,))
                    if not cursor.fetchone():
                        conn.execute("""
                            INSERT INTO roles 
                            (role_id, role_name, description, permissions, security_level_required, is_active)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            role.role_id,
                            role.role_name,
                            role.description,
                            json.dumps(role.permissions),
                            role.security_level_required.value,
                            role.is_active
                        ))
                        self.logger.info(f"Created default role: {role.role_name}")
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize default roles: {e}")
    
    def _initialize_admin_user(self):
        """Initialize default admin user"""
        admin_username = "admin"
        admin_password = "VeriDoc_Admin_2024!"  # Should be changed on first login
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if admin user exists
                cursor = conn.execute("SELECT user_id FROM users WHERE username = ?", (admin_username,))
                if not cursor.fetchone():
                    admin_user = User(
                        user_id="admin_user",
                        username=admin_username,
                        password_hash=self._hash_password(admin_password),
                        security_level=SecurityLevel.TOP_SECRET,
                        roles=["admin"],
                        permissions=["READ", "WRITE", "ADMIN", "SECURITY", "USER_MANAGEMENT"],
                        is_active=True,
                        created_at=datetime.now(),
                        last_login=None,
                        failed_attempts=0,
                        locked_until=None
                    )
                    
                    conn.execute("""
                        INSERT INTO users 
                        (user_id, username, password_hash, security_level, roles, permissions,
                         is_active, created_at, last_login, failed_attempts, locked_until)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        admin_user.user_id,
                        admin_user.username,
                        admin_user.password_hash,
                        admin_user.security_level.value,
                        json.dumps(admin_user.roles),
                        json.dumps(admin_user.permissions),
                        admin_user.is_active,
                        admin_user.created_at.isoformat(),
                        admin_user.last_login.isoformat() if admin_user.last_login else None,
                        admin_user.failed_attempts,
                        admin_user.locked_until.isoformat() if admin_user.locked_until else None
                    ))
                    
                    conn.commit()
                    self.logger.warning(f"Created default admin user with password: {admin_password}")
                    self.logger.warning("SECURITY: Change admin password immediately!")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize admin user: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def authenticate_user(self, user_id: str, credentials: Dict[str, any]) -> Optional[SecurityContext]:
        """Authenticate user and create security context"""
        try:
            username = credentials.get('username')
            password = credentials.get('password')
            ip_address = credentials.get('ip_address')
            
            if not username or not password:
                self._log_access_attempt(None, "authenticate", "FAILED", ip_address, 
                                        {"reason": "missing_credentials"})
                return None
            
            # Get user from database
            user = self._get_user_by_username(username)
            if not user:
                self._log_access_attempt(None, "authenticate", "FAILED", ip_address,
                                        {"reason": "user_not_found", "username": username})
                return None
            
            # Check if user is locked
            if user.locked_until and datetime.now() < user.locked_until:
                self._log_access_attempt(user.user_id, "authenticate", "BLOCKED", ip_address,
                                        {"reason": "account_locked"})
                return None
            
            # Check if user is active
            if not user.is_active:
                self._log_access_attempt(user.user_id, "authenticate", "BLOCKED", ip_address,
                                        {"reason": "account_disabled"})
                return None
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                self._handle_failed_login(user.user_id, ip_address)
                return None
            
            # Reset failed attempts on successful login
            self._reset_failed_attempts(user.user_id)
            
            # Update last login
            self._update_last_login(user.user_id)
            
            # Create security context
            context = SecurityContext(
                user_id=user.user_id,
                session_id="",  # Will be set when session is created
                security_level=user.security_level,
                permissions=user.permissions,
                timestamp=datetime.now(),
                source_ip=ip_address
            )
            
            self._log_access_attempt(user.user_id, "authenticate", "SUCCESS", ip_address,
                                   {"security_level": user.security_level.value})
            
            self.logger.info(f"User {username} authenticated successfully")
            return context
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return None
    
    def create_session(self, user_id: str) -> str:
        """Create secure session for authenticated user"""
        try:
            session_id = secrets.token_urlsafe(32)
            now = datetime.now()
            expires_at = now + self.session_timeout
            
            session = Session(
                session_id=session_id,
                user_id=user_id,
                created_at=now,
                last_activity=now,
                expires_at=expires_at,
                ip_address=None,  # Will be updated when known
                is_active=True
            )
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO sessions 
                    (session_id, user_id, created_at, last_activity, expires_at, ip_address, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.user_id,
                    session.created_at.isoformat(),
                    session.last_activity.isoformat(),
                    session.expires_at.isoformat(),
                    session.ip_address,
                    session.is_active
                ))
                conn.commit()
            
            # Cache session
            self.active_sessions[session_id] = session
            
            self.logger.info(f"Session created for user {user_id}: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    def validate_session(self, session_id: str) -> Optional[SecurityContext]:
        """Validate session and return security context"""
        try:
            # Check cached session first
            session = self.active_sessions.get(session_id)
            
            if not session:
                # Load from database
                session = self._get_session_from_db(session_id)
                if session:
                    self.active_sessions[session_id] = session
            
            if not session or not session.is_active:
                return None
            
            # Check if session is expired
            if datetime.now() > session.expires_at:
                self._expire_session(session_id)
                return None
            
            # Update last activity
            session.last_activity = datetime.now()
            self._update_session_activity(session_id)
            
            # Get user for context
            user = self._get_user_by_id(session.user_id)
            if not user or not user.is_active:
                self._expire_session(session_id)
                return None
            
            # Create security context
            context = SecurityContext(
                user_id=user.user_id,
                session_id=session_id,
                security_level=user.security_level,
                permissions=user.permissions,
                timestamp=datetime.now(),
                source_ip=session.ip_address
            )
            
            return context
            
        except Exception as e:
            self.logger.error(f"Session validation failed: {e}")
            return None
    
    def authorize_operation(self, context: SecurityContext, resource: str, action: str) -> bool:
        """Check if user is authorized for operation"""
        try:
            # Validate session first
            if not self.validate_session(context.session_id):
                self._log_access_attempt(context.user_id, f"authorize_{action}", "DENIED", 
                                       context.source_ip, {"reason": "invalid_session", "resource": resource})
                return False
            
            # Check if user has required permission
            required_permission = self._get_required_permission(action)
            if required_permission not in context.permissions:
                self._log_access_attempt(context.user_id, f"authorize_{action}", "DENIED",
                                       context.source_ip, {
                                           "reason": "insufficient_permissions",
                                           "resource": resource,
                                           "required": required_permission,
                                           "user_permissions": context.permissions
                                       })
                return False
            
            # Check security level requirements
            resource_security_level = self._get_resource_security_level(resource)
            if context.security_level.value < resource_security_level.value:
                self._log_access_attempt(context.user_id, f"authorize_{action}", "DENIED",
                                       context.source_ip, {
                                           "reason": "insufficient_security_level",
                                           "resource": resource,
                                           "required": resource_security_level.value,
                                           "user_level": context.security_level.value
                                       })
                return False
            
            # Log successful authorization
            self._log_access_attempt(context.user_id, f"authorize_{action}", "GRANTED",
                                   context.source_ip, {"resource": resource})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Authorization check failed: {e}")
            return False
    
    def _get_required_permission(self, action: str) -> str:
        """Get required permission for action"""
        action_permissions = {
            'read': 'READ',
            'view': 'READ',
            'write': 'WRITE',
            'create': 'WRITE',
            'update': 'WRITE',
            'delete': 'WRITE',
            'process': 'PROCESS',
            'admin': 'ADMIN',
            'security': 'SECURITY',
            'audit': 'AUDIT',
            'user_management': 'USER_MANAGEMENT'
        }
        
        return action_permissions.get(action.lower(), 'READ')
    
    def _get_resource_security_level(self, resource: str) -> SecurityLevel:
        """Get security level required for resource"""
        # Define resource security requirements
        if 'admin' in resource.lower():
            return SecurityLevel.SECRET
        elif 'security' in resource.lower() or 'audit' in resource.lower():
            return SecurityLevel.CONFIDENTIAL
        elif 'processing' in resource.lower():
            return SecurityLevel.CONFIDENTIAL
        else:
            return SecurityLevel.UNCLASSIFIED
    
    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT user_id, username, password_hash, security_level, roles, permissions,
                           is_active, created_at, last_login, failed_attempts, locked_until
                    FROM users WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return User(
                    user_id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    security_level=SecurityLevel(row[3]),
                    roles=json.loads(row[4]),
                    permissions=json.loads(row[5]),
                    is_active=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    last_login=datetime.fromisoformat(row[8]) if row[8] else None,
                    failed_attempts=row[9],
                    locked_until=datetime.fromisoformat(row[10]) if row[10] else None
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get user by username: {e}")
            return None
    
    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT user_id, username, password_hash, security_level, roles, permissions,
                           is_active, created_at, last_login, failed_attempts, locked_until
                    FROM users WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return User(
                    user_id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    security_level=SecurityLevel(row[3]),
                    roles=json.loads(row[4]),
                    permissions=json.loads(row[5]),
                    is_active=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    last_login=datetime.fromisoformat(row[8]) if row[8] else None,
                    failed_attempts=row[9],
                    locked_until=datetime.fromisoformat(row[10]) if row[10] else None
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get user by ID: {e}")
            return None
    
    def _get_session_from_db(self, session_id: str) -> Optional[Session]:
        """Load session from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT session_id, user_id, created_at, last_activity, expires_at, ip_address, is_active
                    FROM sessions WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return Session(
                    session_id=row[0],
                    user_id=row[1],
                    created_at=datetime.fromisoformat(row[2]),
                    last_activity=datetime.fromisoformat(row[3]),
                    expires_at=datetime.fromisoformat(row[4]),
                    ip_address=row[5],
                    is_active=bool(row[6])
                )
                
        except Exception as e:
            self.logger.error(f"Failed to load session from database: {e}")
            return None
    
    def _handle_failed_login(self, user_id: str, ip_address: Optional[str]):
        """Handle failed login attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Increment failed attempts
                conn.execute("""
                    UPDATE users SET failed_attempts = failed_attempts + 1 
                    WHERE user_id = ?
                """, (user_id,))
                
                # Check if should lock account
                cursor = conn.execute("SELECT failed_attempts FROM users WHERE user_id = ?", (user_id,))
                failed_attempts = cursor.fetchone()[0]
                
                if failed_attempts >= self.max_failed_attempts:
                    locked_until = datetime.now() + self.lockout_duration
                    conn.execute("""
                        UPDATE users SET locked_until = ? WHERE user_id = ?
                    """, (locked_until.isoformat(), user_id))
                    
                    self.logger.warning(f"Account locked due to failed attempts: {user_id}")
                
                conn.commit()
            
            self._log_access_attempt(user_id, "authenticate", "FAILED", ip_address,
                                   {"failed_attempts": failed_attempts})
            
        except Exception as e:
            self.logger.error(f"Failed to handle failed login: {e}")
    
    def _reset_failed_attempts(self, user_id: str):
        """Reset failed login attempts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE users SET failed_attempts = 0, locked_until = NULL 
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to reset failed attempts: {e}")
    
    def _update_last_login(self, user_id: str):
        """Update last login timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE users SET last_login = ? WHERE user_id = ?
                """, (datetime.now().isoformat(), user_id))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to update last login: {e}")
    
    def _update_session_activity(self, session_id: str):
        """Update session last activity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions SET last_activity = ? WHERE session_id = ?
                """, (datetime.now().isoformat(), session_id))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to update session activity: {e}")
    
    def _expire_session(self, session_id: str):
        """Expire session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions SET is_active = 0 WHERE session_id = ?
                """, (session_id,))
                conn.commit()
            
            # Remove from cache
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                
        except Exception as e:
            self.logger.error(f"Failed to expire session: {e}")
    
    def _log_access_attempt(self, user_id: Optional[str], action: str, result: str,
                          ip_address: Optional[str], details: Dict[str, any]):
        """Log access attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO access_logs 
                    (timestamp, user_id, session_id, resource, action, result, ip_address, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    user_id,
                    None,  # session_id not always available
                    "authentication",
                    action,
                    result,
                    ip_address,
                    json.dumps(details)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log access attempt: {e}")
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user and invalidate session"""
        try:
            self._expire_session(session_id)
            self.logger.info(f"User logged out: {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to logout user: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            cutoff_time = datetime.now()
            
            with sqlite3.connect(self.db_path) as conn:
                # Expire sessions in database
                cursor = conn.execute("""
                    UPDATE sessions SET is_active = 0 
                    WHERE expires_at < ? AND is_active = 1
                """, (cutoff_time.isoformat(),))
                
                expired_count = cursor.rowcount
                conn.commit()
            
            # Clean up cache
            expired_sessions = [
                sid for sid, session in self.active_sessions.items()
                if session.expires_at < cutoff_time
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
            
            if expired_count > 0:
                self.logger.info(f"Cleaned up {expired_count} expired sessions")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {e}")
