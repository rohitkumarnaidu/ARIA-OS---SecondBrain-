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
    sanitized = input_str
    patterns = [
        (r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        (r"<script", re.IGNORECASE),
        (r"javascript\s*:", re.IGNORECASE),
        (r"on\w+\s*=", re.IGNORECASE),
        (r"<iframe[^>]*>.*?</iframe>", re.IGNORECASE | re.DOTALL),
        (r"<iframe", re.IGNORECASE),
        (r"<embed[^>]*>", re.IGNORECASE),
        (r"<object[^>]*>", re.IGNORECASE),
        (r"data\s*:\s*text/html", re.IGNORECASE),
        (r"vbscript\s*:", re.IGNORECASE),
        (r"expression\s*\(.*\)", re.IGNORECASE),
        (r"document\.cookie", re.IGNORECASE),
        (r"document\.write", re.IGNORECASE),
        (r"alert\s*\(", re.IGNORECASE),
        (r"eval\s*\(", re.IGNORECASE),
    ]
    for pattern, flags in patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=flags)
    return sanitized.strip()


def sanitize_object(obj):
    if isinstance(obj, str):
        return sanitize_input(obj)
    if isinstance(obj, dict):
        return {k: sanitize_object(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_object(i) for i in obj]
    return obj


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
