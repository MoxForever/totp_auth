from base64 import b64decode, b64encode
import hashlib
import time


def generate_csrf_token(secret_key: str) -> str:
    current = time.time()
    hashed = hashlib.sha256(f"{current}:{secret_key}".encode()).hexdigest()
    return b64encode(f"{current}:{hashed}".encode()).decode()


def check_csrf_token(secret_key: str, token: str) -> bool:
    try:
        decoded = b64decode(token).decode()
        current, hashed = decoded.split(":", 1)
        expected = hashlib.sha256(f"{current}:{secret_key}".encode()).hexdigest()
        return hashed == expected
    except Exception:
        return False
