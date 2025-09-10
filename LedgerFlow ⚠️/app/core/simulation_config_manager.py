import hashlib
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.user import User

class SimulationConfigManager:
    """
    Manages simulation configuration locking and unlocking.
    
    Features:
    - Config hash generation and storage
    - Admin-only unlocking mechanism
    - Password verification for unlocking
    - Hash display for auditors
    """
    
    def __init__(self):
        """
        Initializes the simulation config manager.
        """
        self.config_hash = None
        self.is_locked = False
        self.locked_at = None
        self.locked_by = None
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if not exists
        if not self.logger.handlers:
            import os
            os.makedirs('logs', exist_ok=True)
            handler = logging.FileHandler('logs/simulation_config.log')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def lock_config(self, config: Dict[str, Any], locked_by: str) -> str:
        """
        Locks the simulation config by storing its hash.
        
        Args:
            config: The simulation config object
            locked_by: The username of the user locking the config
            
        Returns:
            The hash of the config
        """
        try:
            # Convert config to JSON and sort keys for consistent hashing
            config_json = json.dumps(config, sort_keys=True, default=str)
            self.config_hash = hashlib.sha256(config_json.encode()).hexdigest()
            
            self.is_locked = True
            self.locked_at = datetime.utcnow()
            self.locked_by = locked_by
            
            self.logger.info(f"Config locked by {locked_by} with hash: {self.config_hash}")
            return self.config_hash
            
        except Exception as e:
            self.logger.error(f"Error locking config: {e}")
            return None
    
    def get_config_hash(self) -> Optional[str]:
        """
        Gets the hash of the locked config.
        
        Returns:
            The hash of the config or None if not locked
        """
        return self.config_hash if self.is_locked else None
    
    def unlock_config(self, admin_password: str, unlocked_by: str) -> bool:
        """
        Unlocks the simulation config if the admin password is correct.
        
        Args:
            admin_password: The admin password
            unlocked_by: The username of the user attempting to unlock
            
        Returns:
            Boolean indicating if unlock was successful
        """
        try:
            if not self.is_locked:
                self.logger.warning(f"Config is not locked, unlock attempted by {unlocked_by}")
                return False
            
            # Verify admin password
            if self._verify_admin_password(admin_password):
                self.is_locked = False
                self.locked_at = None
                self.locked_by = None
                self.config_hash = None
                
                self.logger.info(f"Config unlocked by {unlocked_by}")
                return True
            else:
                self.logger.warning(f"Invalid admin password provided by {unlocked_by}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error unlocking config: {e}")
            return False
    
    def is_config_locked(self) -> bool:
        """
        Checks if the simulation config is locked.
        
        Returns:
            Boolean indicating if config is locked
        """
        return self.is_locked
    
    def get_lock_info(self) -> Dict[str, Any]:
        """
        Gets information about the current lock status.
        
        Returns:
            Dictionary with lock information
        """
        return {
            'is_locked': self.is_locked,
            'config_hash': self.config_hash,
            'locked_at': self.locked_at.isoformat() if self.locked_at else None,
            'locked_by': self.locked_by
        }
    
    def verify_config_integrity(self, config: Dict[str, Any]) -> bool:
        """
        Verifies that the current config matches the stored hash.
        
        Args:
            config: The current config to verify
            
        Returns:
            Boolean indicating if config integrity is maintained
        """
        try:
            if not self.is_locked or not self.config_hash:
                return True  # No lock to verify against
            
            # Generate hash of current config
            config_json = json.dumps(config, sort_keys=True, default=str)
            current_hash = hashlib.sha256(config_json.encode()).hexdigest()
            
            # Compare with stored hash
            integrity_maintained = current_hash == self.config_hash
            
            if not integrity_maintained:
                self.logger.warning(f"Config integrity check failed. Expected: {self.config_hash}, Got: {current_hash}")
            
            return integrity_maintained
            
        except Exception as e:
            self.logger.error(f"Error verifying config integrity: {e}")
            return False
    
    def _verify_admin_password(self, password: str) -> bool:
        """
        Verifies the admin password.
        
        Args:
            password: The password to verify
            
        Returns:
            Boolean indicating if password is correct
        """
        try:
            # Get admin user
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                self.logger.error("No admin user found")
                return False
            
            # Check password
            return admin_user.check_password(password)
            
        except Exception as e:
            self.logger.error(f"Error verifying admin password: {e}")
            return False
    
    def get_auditor_display_info(self) -> Dict[str, Any]:
        """
        Gets information to display to auditors about the locked config.
        
        Returns:
            Dictionary with display information
        """
        if not self.is_locked:
            return {
                'status': 'unlocked',
                'message': 'Configuration is not locked'
            }
        
        return {
            'status': 'locked',
            'config_hash': self.config_hash,
            'locked_at': self.locked_at.isoformat() if self.locked_at else None,
            'locked_by': self.locked_by,
            'message': f'Configuration locked by {self.locked_by} at {self.locked_at.strftime("%Y-%m-%d %H:%M:%S") if self.locked_at else "Unknown"}'
        }
    
    def export_lock_history(self) -> Dict[str, Any]:
        """
        Exports the lock history for audit purposes.
        
        Returns:
            Dictionary with lock history
        """
        return {
            'current_status': {
                'is_locked': self.is_locked,
                'config_hash': self.config_hash,
                'locked_at': self.locked_at.isoformat() if self.locked_at else None,
                'locked_by': self.locked_by
            },
            'exported_at': datetime.utcnow().isoformat(),
            'exported_by': 'system'
        }
    
    def reset_lock(self, reset_by: str) -> bool:
        """
        Resets the lock state (admin only).
        
        Args:
            reset_by: The username of the user resetting the lock
            
        Returns:
            Boolean indicating success
        """
        try:
            self.is_locked = False
            self.locked_at = None
            self.locked_by = None
            self.config_hash = None
            
            self.logger.info(f"Config lock reset by {reset_by}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting lock: {e}")
            return False 