"""
Security Middleware

Adds security headers, rate limiting, and basic protection.
"""

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# In-memory store for rate limiting (use Redis in production)
request_counts = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60     # seconds


class SecurityMiddleware(BaseHTTPMiddleware):
    """Add security headers and rate limiting."""

    async def dispatch(self, request: Request, call_next):
        # Add security headers
        response: Response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Rate limiting (basic implementation)
        if request.url.path.startswith("/api/"):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()

            # Clean old requests
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if now - req_time < RATE_LIMIT_WINDOW
            ]

            # Check rate limit
            if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again later."}
                )

            # Add current request
            request_counts[client_ip].append(now)

        return response


def setup_security_middleware(app):
    """Setup security middleware for the app."""
    app.add_middleware(SecurityMiddleware)