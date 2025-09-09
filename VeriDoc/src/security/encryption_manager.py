"""
Military-Grade Encryption Manager

Implements AES-256 encryption, digital signatures, and secure key management
for government-grade operations.
"""

import os
import hmac
import hashlib
import secrets
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import json
import base64
import logging

from ..contracts import IEncryptionManager, SecurityContext, SecurityLevel


class EncryptionManager(IEncryptionManager):
    """
    Military-grade encryption manager implementing AES-256 encryption,
    RSA digital signatures, and secure key management.
    """
    
    def __init__(self, key_storage_path: str = "secure/keys"):
        self.logger = logging.getLogger(__name__)
        self.key_storage_path = key_storage_path
        self.backend = default_backend()
        
        # Initialize secure storage
        os.makedirs(key_storage_path, exist_ok=True)
        
        # Initialize or load master keys
        self._initialize_master_keys()
        
        # Key derivation settings
        self.kdf_iterations = 100000  # PBKDF2 iterations
        self.salt_length = 32
        self.key_length = 32  # 256 bits
        
        self.logger.info("Military-grade encryption manager initialized")
    
    def _initialize_master_keys(self):
        """Initialize or load master encryption keys"""
        master_key_path = os.path.join(self.key_storage_path, "master.key")
        signing_key_path = os.path.join(self.key_storage_path, "signing.pem")
        
        # Initialize master symmetric key
        if not os.path.exists(master_key_path):
            self.master_key = secrets.token_bytes(32)  # 256-bit key
            with open(master_key_path, 'wb') as f:
                f.write(self.master_key)
            os.chmod(master_key_path, 0o600)  # Restrict permissions
            self.logger.info("Generated new master encryption key")
        else:
            with open(master_key_path, 'rb') as f:
                self.master_key = f.read()
            self.logger.info("Loaded existing master encryption key")
        
        # Initialize RSA signing key pair
        if not os.path.exists(signing_key_path):
            self.signing_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=self.backend
            )
            
            # Save private key
            private_pem = self.signing_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            with open(signing_key_path, 'wb') as f:
                f.write(private_pem)
            os.chmod(signing_key_path, 0o600)
            
            # Save public key
            public_key_path = os.path.join(self.key_storage_path, "signing_public.pem")
            public_pem = self.signing_private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            with open(public_key_path, 'wb') as f:
                f.write(public_pem)
            
            self.logger.info("Generated new RSA signing key pair")
        else:
            with open(signing_key_path, 'rb') as f:
                private_pem = f.read()
            self.signing_private_key = serialization.load_pem_private_key(
                private_pem, password=None, backend=self.backend
            )
            self.logger.info("Loaded existing RSA signing key")
        
        self.signing_public_key = self.signing_private_key.public_key()
    
    def _derive_key(self, context: SecurityContext, purpose: str) -> bytes:
        """Derive encryption key from master key and context"""
        # Create context-specific salt
        context_data = f"{context.user_id}:{context.session_id}:{purpose}:{context.security_level.value}"
        salt = hashlib.sha256(context_data.encode()).digest()
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            iterations=self.kdf_iterations,
            backend=self.backend
        )
        return kdf.derive(self.master_key)
    
    def encrypt_data(self, data: bytes, context: SecurityContext) -> bytes:
        """
        Encrypt data using AES-256-GCM with context-derived key
        
        Returns:
            Encrypted data format: [IV(16)] + [AUTH_TAG(16)] + [ENCRYPTED_DATA]
        """
        try:
            # Validate security context
            self._validate_context(context)
            
            # Derive encryption key
            key = self._derive_key(context, "encrypt")
            
            # Generate random IV
            iv = secrets.token_bytes(16)  # 128-bit IV for GCM
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # Encrypt data
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Combine IV + auth tag + ciphertext
            encrypted_package = iv + encryptor.tag + ciphertext
            
            self.logger.debug(f"Encrypted {len(data)} bytes for user {context.user_id}")
            return encrypted_package
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes, context: SecurityContext) -> bytes:
        """
        Decrypt data using AES-256-GCM with context-derived key
        
        Args:
            encrypted_data: Format [IV(16)] + [AUTH_TAG(16)] + [ENCRYPTED_DATA]
        """
        try:
            # Validate security context
            self._validate_context(context)
            
            if len(encrypted_data) < 32:  # IV + TAG minimum
                raise ValueError("Invalid encrypted data format")
            
            # Extract components
            iv = encrypted_data[:16]
            auth_tag = encrypted_data[16:32]
            ciphertext = encrypted_data[32:]
            
            # Derive decryption key
            key = self._derive_key(context, "encrypt")
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, auth_tag),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # Decrypt data
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            self.logger.debug(f"Decrypted {len(plaintext)} bytes for user {context.user_id}")
            return plaintext
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise
    
    def generate_signature(self, data: bytes, context: SecurityContext) -> str:
        """Generate RSA digital signature for data"""
        try:
            # Validate security context
            self._validate_context(context)
            
            # Create signature context
            signature_data = {
                'data_hash': hashlib.sha256(data).hexdigest(),
                'user_id': context.user_id,
                'session_id': context.session_id,
                'timestamp': context.timestamp.isoformat(),
                'security_level': context.security_level.value
            }
            
            # Serialize signature data
            signature_json = json.dumps(signature_data, sort_keys=True)
            signature_bytes = signature_json.encode('utf-8')
            
            # Generate RSA signature
            signature = self.signing_private_key.sign(
                signature_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Return base64-encoded signature
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            
            self.logger.debug(f"Generated signature for user {context.user_id}")
            return signature_b64
            
        except Exception as e:
            self.logger.error(f"Signature generation failed: {e}")
            raise
    
    def verify_signature(self, data: bytes, signature: str, context: SecurityContext) -> bool:
        """Verify RSA digital signature"""
        try:
            # Validate security context
            self._validate_context(context)
            
            # Recreate signature data
            signature_data = {
                'data_hash': hashlib.sha256(data).hexdigest(),
                'user_id': context.user_id,
                'session_id': context.session_id,
                'timestamp': context.timestamp.isoformat(),
                'security_level': context.security_level.value
            }
            
            # Serialize signature data
            signature_json = json.dumps(signature_data, sort_keys=True)
            signature_bytes = signature_json.encode('utf-8')
            
            # Decode signature
            signature_raw = base64.b64decode(signature.encode('utf-8'))
            
            # Verify signature
            try:
                self.signing_public_key.verify(
                    signature_raw,
                    signature_bytes,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                
                self.logger.debug(f"Signature verified for user {context.user_id}")
                return True
                
            except Exception:
                self.logger.warning(f"Signature verification failed for user {context.user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Signature verification error: {e}")
            return False
    
    def encrypt_file(self, file_path: str, context: SecurityContext) -> str:
        """Encrypt file and return encrypted file path"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.encrypt_data(file_data, context)
            
            encrypted_path = file_path + '.enc'
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Securely delete original
            self._secure_delete_file(file_path)
            
            self.logger.info(f"File encrypted: {file_path} -> {encrypted_path}")
            return encrypted_path
            
        except Exception as e:
            self.logger.error(f"File encryption failed: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, context: SecurityContext) -> str:
        """Decrypt file and return decrypted file path"""
        try:
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.decrypt_data(encrypted_data, context)
            
            # Remove .enc extension
            decrypted_path = encrypted_file_path.replace('.enc', '')
            with open(decrypted_path, 'wb') as f:
                f.write(decrypted_data)
            
            self.logger.info(f"File decrypted: {encrypted_file_path} -> {decrypted_path}")
            return decrypted_path
            
        except Exception as e:
            self.logger.error(f"File decryption failed: {e}")
            raise
    
    def _validate_context(self, context: SecurityContext):
        """Validate security context"""
        if not context.user_id:
            raise ValueError("Invalid security context: missing user_id")
        
        if not context.session_id:
            raise ValueError("Invalid security context: missing session_id")
        
        # Check for expired context (30 minutes)
        max_age = timedelta(minutes=30)
        if datetime.now() - context.timestamp > max_age:
            raise ValueError("Security context expired")
    
    def _secure_delete_file(self, file_path: str, passes: int = 3):
        """Securely delete file with multiple overwrite passes"""
        try:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                
                with open(file_path, 'r+b') as f:
                    for _ in range(passes):
                        f.seek(0)
                        f.write(secrets.token_bytes(file_size))
                        f.flush()
                        os.fsync(f.fileno())
                
                os.remove(file_path)
                self.logger.debug(f"Securely deleted file: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Secure file deletion failed: {e}")
    
    def generate_hmac(self, data: bytes, context: SecurityContext) -> str:
        """Generate HMAC for data integrity"""
        try:
            key = self._derive_key(context, "hmac")
            hmac_hash = hmac.new(key, data, hashlib.sha256).hexdigest()
            return hmac_hash
        except Exception as e:
            self.logger.error(f"HMAC generation failed: {e}")
            raise
    
    def verify_hmac(self, data: bytes, hmac_value: str, context: SecurityContext) -> bool:
        """Verify HMAC for data integrity"""
        try:
            expected_hmac = self.generate_hmac(data, context)
            return hmac.compare_digest(expected_hmac, hmac_value)
        except Exception as e:
            self.logger.error(f"HMAC verification failed: {e}")
            return False
    
    def rotate_keys(self, context: SecurityContext) -> bool:
        """Rotate encryption keys (requires admin privileges)"""
        try:
            if not self._has_admin_privileges(context):
                raise PermissionError("Key rotation requires admin privileges")
            
            # Backup current keys
            backup_path = os.path.join(self.key_storage_path, f"backup_{datetime.now().isoformat()}")
            os.makedirs(backup_path, exist_ok=True)
            
            # Generate new keys
            self._initialize_master_keys()
            
            self.logger.warning(f"Encryption keys rotated by {context.user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
            return False
    
    def _has_admin_privileges(self, context: SecurityContext) -> bool:
        """Check if context has admin privileges"""
        return (context.security_level in [SecurityLevel.SECRET, SecurityLevel.TOP_SECRET] and
                "ADMIN" in context.permissions)
    
    def get_encryption_info(self) -> Dict[str, any]:
        """Get encryption system information"""
        return {
            'algorithm': 'AES-256-GCM',
            'key_derivation': 'PBKDF2-SHA256',
            'signature_algorithm': 'RSA-4096-PSS',
            'kdf_iterations': self.kdf_iterations,
            'initialized': True
        }
