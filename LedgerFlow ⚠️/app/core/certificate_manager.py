import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging
from typing import Optional, Tuple

class CertificateManager:
    """
    Manages digital certificates for PDF signing.
    
    Features:
    - Secure storage of PFX certificates outside web root
    - AES encryption for certificate and password
    - Certificate validation
    - Error handling and logging
    """
    
    def __init__(self):
        """
        Initializes the certificate manager.
        """
        # Store certificates in a secure location outside web root
        self.cert_storage_path = "instance/certificates"
        os.makedirs(self.cert_storage_path, exist_ok=True)
        
        # Initialize encryption key
        self._init_encryption_key()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if not exists
        if not self.logger.handlers:
            handler = logging.FileHandler('logs/certificate.log')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _init_encryption_key(self):
        """
        Initialize or load the encryption key.
        """
        key_file = os.path.join(self.cert_storage_path, "key.key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            # Generate new key
            self.key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher = Fernet(self.key)
    
    def store_certificate(self, pfx_file, password: str) -> bool:
        """
        Stores a PFX certificate and its password securely.
        
        Args:
            pfx_file: The uploaded PFX file
            password: The certificate password
            
        Returns:
            Boolean indicating success
        """
        try:
            # Validate certificate
            if not self._validate_certificate(pfx_file, password):
                self.logger.error("Certificate validation failed")
                return False
            
            # Read certificate data
            pfx_data = pfx_file.read()
            
            # Encrypt and store certificate and password
            encrypted_cert = self._encrypt_data(pfx_data)
            encrypted_password = self._encrypt_data(password.encode())
            
            # Save to secure storage outside web root
            cert_path = os.path.join(self.cert_storage_path, "certificate.pfx.enc")
            pwd_path = os.path.join(self.cert_storage_path, "certificate.pwd.enc")
            
            with open(cert_path, 'wb') as f:
                f.write(encrypted_cert)
            
            with open(pwd_path, 'wb') as f:
                f.write(encrypted_password)
            
            self.logger.info("Certificate stored successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing certificate: {e}")
            return False
    
    def get_certificate(self) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Retrieves the stored certificate and password.
        
        Returns:
            Tuple of (certificate_data, password) or (None, None) if not found
        """
        try:
            if not self._certificate_exists():
                return None, None
            
            cert_path = os.path.join(self.cert_storage_path, "certificate.pfx.enc")
            pwd_path = os.path.join(self.cert_storage_path, "certificate.pwd.enc")
            
            with open(cert_path, 'rb') as f:
                encrypted_cert = f.read()
            
            with open(pwd_path, 'rb') as f:
                encrypted_password = f.read()
            
            cert_data = self._decrypt_data(encrypted_cert)
            password = self._decrypt_data(encrypted_password).decode()
            
            return cert_data, password
            
        except Exception as e:
            self.logger.error(f"Error retrieving certificate: {e}")
            return None, None
    
    def _certificate_exists(self) -> bool:
        """
        Checks if a certificate is stored.
        
        Returns:
            Boolean indicating if certificate exists
        """
        cert_path = os.path.join(self.cert_storage_path, "certificate.pfx.enc")
        pwd_path = os.path.join(self.cert_storage_path, "certificate.pwd.enc")
        return os.path.exists(cert_path) and os.path.exists(pwd_path)
    
    def _validate_certificate(self, pfx_file, password: str) -> bool:
        """
        Validates a PFX certificate with the provided password.
        
        Args:
            pfx_file: The PFX file
            password: The certificate password
            
        Returns:
            Boolean indicating if certificate is valid
        """
        try:
            # Try to load the certificate to validate it
            from cryptography.hazmat.primitives.serialization import pkcs12
            
            pfx_data = pfx_file.read()
            pfx_file.seek(0)  # Reset file pointer
            
            # Attempt to load the certificate
            pkcs12.load_key_and_certificates(pfx_data, password.encode())
            return True
            
        except Exception as e:
            self.logger.error(f"Certificate validation error: {e}")
            return False
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """
        Encrypts data using Fernet (AES).
        
        Args:
            data: The data to encrypt
            
        Returns:
            Encrypted data
        """
        return self.cipher.encrypt(data)
    
    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """
        Decrypts data using Fernet (AES).
        
        Args:
            encrypted_data: The data to decrypt
            
        Returns:
            Decrypted data
        """
        return self.cipher.decrypt(encrypted_data)
    
    def remove_certificate(self) -> bool:
        """
        Removes the stored certificate.
        
        Returns:
            Boolean indicating success
        """
        try:
            cert_path = os.path.join(self.cert_storage_path, "certificate.pfx.enc")
            pwd_path = os.path.join(self.cert_storage_path, "certificate.pwd.enc")
            
            if os.path.exists(cert_path):
                os.remove(cert_path)
            
            if os.path.exists(pwd_path):
                os.remove(pwd_path)
            
            self.logger.info("Certificate removed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing certificate: {e}")
            return False
    
    def generate_dummy_certificate(self) -> bool:
        """
        Generates a dummy self-signed certificate for testing.
        
        Returns:
            Boolean indicating success
        """
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from datetime import datetime, timedelta
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Maharashtra"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Mumbai"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Company"),
                x509.NameAttribute(NameOID.COMMON_NAME, "test.example.com"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).sign(private_key, hashes.SHA256())
            
            # Create PKCS12 container
            from cryptography.hazmat.primitives.serialization import pkcs12
            
            pfx_data = pkcs12.serialize_key_and_certificates(
                name=b"test",
                key=private_key,
                cert=cert,
                cas=None,
                encryption_algorithm=serialization.BestAvailableEncryption(b"test123")
            )
            
            # Store the dummy certificate
            cert_data = pfx_data
            password = "test123"
            
            encrypted_cert = self._encrypt_data(cert_data)
            encrypted_password = self._encrypt_data(password.encode())
            
            cert_path = os.path.join(self.cert_storage_path, "certificate.pfx.enc")
            pwd_path = os.path.join(self.cert_storage_path, "certificate.pwd.enc")
            
            with open(cert_path, 'wb') as f:
                f.write(encrypted_cert)
            
            with open(pwd_path, 'wb') as f:
                f.write(encrypted_password)
            
            self.logger.info("Dummy certificate generated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating dummy certificate: {e}")
            return False 