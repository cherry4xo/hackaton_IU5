import bcrypt
from typing import Tuple
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)


def verify_and_update_password(plain_password: str, hashed_password: str) -> Tuple[bool, str]:
    """
    Verify a plain password against a hashed password and return whether it's valid
    and the updated hash if needed.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        Tuple of (is_valid, updated_hash) where is_valid indicates if the password
        matches and updated_hash is the potentially rehashed password
    """
    # Convert strings to bytes if needed
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    # Verify the password
    is_valid = bcrypt.checkpw(plain_password, hashed_password)
    
    # For bcrypt, we don't need to update the hash unless there's a specific reason
    # Just return the same hash
    return (is_valid, hashed_password.decode('utf-8') if isinstance(hashed_password, bytes) else hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password as a string
    """
    try:
        # Truncate password to 72 bytes to comply with bcrypt limitations
        if len(password.encode('utf-8')) > 72:
            # Find the right string slice that keeps us under 72 bytes
            truncated = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
            password_bytes = truncated.encode('utf-8')
        else:
            password_bytes = password.encode('utf-8')
        
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        # Log the error and re-raise it
        logger.error(f"Unexpected error during password hashing: {e}")
        raise


def generate_password() -> str:
    """
    Generate a random password.
    
    Returns:
        A randomly generated password string
    """
    import secrets
    import string
    
    # Generate a secure random password
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(16))
