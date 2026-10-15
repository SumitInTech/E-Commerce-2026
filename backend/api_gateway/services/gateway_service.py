"""
API Gateway Security & Traffic Management Services.
Includes Sliding-Window Rate Limiting, Threat Sanitization, and Distributed Tracing.
"""
import time
import re
from typing import Dict, Tuple, List
from collections import defaultdict
from backend.config import settings


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter tracking request timestamps per client IP."""
    def __init__(self, requests_per_minute: int = 120):
        self.rate_limit = requests_per_minute
        self.window_seconds = 60
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        now = time.time()
        cutoff = now - self.window_seconds

        # Evict old requests outside window
        self.requests[client_ip] = [ts for ts in self.requests[client_ip] if ts > cutoff]

        current_count = len(self.requests[client_ip])
        if current_count >= self.rate_limit:
            remaining = 0
            return False, remaining

        self.requests[client_ip].append(now)
        remaining = self.rate_limit - len(self.requests[client_ip])
        return True, remaining


class SecuritySanitizer:
    """Inspects query parameters and request payloads for common attack vectors (SQLi, XSS)."""
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(UNION(\s+ALL)?|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC(\s+IMMEDIATE)?)\b|--|\/\*|\*\/|;\s*$)",
        re.IGNORECASE
    )
    XSS_PATTERN = re.compile(
        r"(<script.*?>.*?<\/script>|javascript:|onerror=|onload=|eval\(|alert\()",
        re.IGNORECASE
    )

    @classmethod
    def inspect(cls, raw_payload: str) -> Tuple[bool, str]:
        if cls.SQL_INJECTION_PATTERN.search(raw_payload):
            return False, "Potential SQL Injection pattern detected"
        if cls.XSS_PATTERN.search(raw_payload):
            return False, "Potential Cross-Site Scripting (XSS) payload detected"
        return True, "Safe"


rate_limiter = SlidingWindowRateLimiter(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
security_sanitizer = SecuritySanitizer()
