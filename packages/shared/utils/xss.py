import re
import html
from typing import Optional


XSS_PATTERNS = [
    (re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL), "script tags"),
    (re.compile(r"javascript:\s*", re.IGNORECASE), "javascript: URIs"),
    (re.compile(r"on\w+\s*=", re.IGNORECASE), "event handlers"),
    (re.compile(r"<iframe[^>]*>", re.IGNORECASE), "iframe tags"),
    (re.compile(r"<object[^>]*>", re.IGNORECASE), "object tags"),
    (re.compile(r"<embed[^>]*>", re.IGNORECASE), "embed tags"),
    (re.compile(r"<svg[^>]*onload\s*=", re.IGNORECASE), "svg onload"),
    (re.compile(r"document\.cookie", re.IGNORECASE), "cookie access"),
    (re.compile(r"eval\s*\(", re.IGNORECASE), "eval()"),
    (re.compile(r"<link[^>]*href\s*=", re.IGNORECASE), "link tags"),
    (re.compile(r"data:\s*text/html", re.IGNORECASE), "data URIs"),
]


def sanitize_html(value: str) -> str:
    """Strip known XSS vectors from HTML input."""
    if not isinstance(value, str):
        return str(value)

    sanitized = value
    for pattern, name in XSS_PATTERNS:
        sanitized = pattern.sub("", sanitized)
    return html.escape(sanitized, quote=True)


def strip_html(value: str) -> str:
    """Remove all HTML tags, leaving only text content."""
    if not isinstance(value, str):
        return str(value)

    text = re.sub(r"<[^>]*>", "", value)
    return html.unescape(text)


def sanitize_object(obj: object, max_depth: int = 10, _depth: int = 0) -> object:
    """Recursively sanitize all string fields in an object."""
    if _depth > max_depth:
        return obj

    if isinstance(obj, str):
        return sanitize_html(obj)

    if isinstance(obj, dict):
        return {k: sanitize_object(v, max_depth, _depth + 1) for k, v in obj.items()}

    if isinstance(obj, list):
        return [sanitize_object(item, max_depth, _depth + 1) for item in obj]

    return obj


def has_xss(value: str) -> Optional[str]:
    """Check if value contains XSS vectors. Returns the first matched pattern name or None."""
    for pattern, name in XSS_PATTERNS:
        if pattern.search(value):
            return name
    return None


def detect_xss_in_object(obj: object, max_depth: int = 10, _depth: int = 0) -> list:
    """Recursively find XSS vectors in an object. Returns list of (path, pattern) tuples."""
    findings = []

    if _depth > max_depth:
        return findings

    if isinstance(obj, str):
        match = has_xss(obj)
        if match:
            findings.append(("ROOT", match))
        return findings

    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                match = has_xss(v)
                if match:
                    findings.append((f"{k}", match))
            else:
                nested = detect_xss_in_object(v, max_depth, _depth + 1)
                for path, pattern in nested:
                    findings.append((f"{k}.{path}", pattern))

    if isinstance(obj, list):
        for i, item in enumerate(obj):
            nested = detect_xss_in_object(item, max_depth, _depth + 1)
            for path, pattern in nested:
                findings.append((f"[{i}].{path}", pattern))

    return findings
