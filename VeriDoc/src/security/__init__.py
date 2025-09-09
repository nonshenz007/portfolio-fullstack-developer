"""
Government-Grade Security Framework

This package implements military-grade security features including:
- AES-256 encryption at rest
- Digital signatures for tamper-proof operations
- Role-Based Access Control (RBAC)
- Tamper-proof audit logging
- Secure memory management
"""

from .encryption_manager import EncryptionManager
from .audit_logger import TamperProofAuditLogger
from .access_control import RoleBasedAccessControl
from .security_manager import GovernmentSecurityManager

__all__ = [
    'EncryptionManager',
    'TamperProofAuditLogger', 
    'RoleBasedAccessControl',
    'GovernmentSecurityManager'
]
