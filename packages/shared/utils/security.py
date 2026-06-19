"""Security utilities for API protection"""

import hashlib
import secrets
import re


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def hash_password(password: str) -> str:
    """Hash password using SHA-256 (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent injection"""
    # Remove potentially dangerous characters
    dangerous_patterns = [
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onclick=",
        r"onload=",
    ]

    sanitized = input_str
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

    return sanitized.strip()


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$"
    return re.match(pattern, url) is not None


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data, showing only last few characters"""
    if len(data) <= visible_chars:
        return "*" * len(data)
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


def generate_api_key(prefix: str = "sk") -> str:
    """Generate an API key with prefix"""
    return f"{prefix}_{generate_secure_token(48)}"
