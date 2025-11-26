# core/auth.py
import os
import hashlib
import secrets
from typing import Tuple, Optional, Dict
from core.database import create_user_row, get_user_row_by_username

# constants
PBKDF2_ITERATIONS = 100_000
HASH_NAME = "sha256"
SALT_SIZE = 16  # bytes

# Return raw bytes of PBKDF2-HMAC hash.
def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(HASH_NAME, password.encode("utf-8"), salt, PBKDF2_ITERATIONS)

# Create salt + hash (hex). Returns (salt_hex, hash_hex).
def make_password_hash(password: str) -> Tuple[str, str]:
    salt = os.urandom(SALT_SIZE)
    hashed = _hash_password(password, salt)
    return salt.hex(), hashed.hex()

def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    computed = _hash_password(password, salt)
    return secrets.compare_digest(computed, expected)

#Create a new user. Returns (ok, error_message).
def register_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
    username = username.strip()
    if not username or not password:
        return False, "Username and password are required."

    existing = get_user_row_by_username(username)
    if existing:
        return False, "Username already exists."

    salt_hex, hash_hex = make_password_hash(password)
    try:
        create_user_row(username, hash_hex, salt_hex)
        return True, None
    except Exception as e:
        return False, str(e)

# If credentials valid, return user dict (id, username). Otherwise, None.
def authenticate_user(username: str, password: str) -> Optional[Dict]:
    row = get_user_row_by_username(username.strip())
    if not row:
        return None

    salt_hex = row["salt"]
    hash_hex = row["password_hash"]
    if verify_password(password, salt_hex, hash_hex):
        return {"id": row["id"], "username": row["username"]}

    return None
