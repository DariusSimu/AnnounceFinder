from cryptography.fernet import Fernet
import os

def get_fernet():
    key = os.environ.get('ENCRYPTION_KEY', '')
    if not key:
        # fallback to config.py for local development
        try:
            from config import ENCRYPTION_KEY
            key = ENCRYPTION_KEY
        except ImportError:
            return None
    if not key:
        return None
    return Fernet(key.encode())

def encrypt(value: str) -> str:
    f = get_fernet()
    if not f: return value
    return f.encrypt(value.encode()).decode()

def decrypt(value: str) -> str:
    f = get_fernet()
    if not f: return value
    return f.decrypt(value.encode()).decode()