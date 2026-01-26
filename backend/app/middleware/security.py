"""
Security middleware for FastAPI application
Implements security headers and rate limiting
"""

import time
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses

    Headers implemented:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: max-age=31536000
    - Content-Security-Policy: restrictive policy
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: restricted permissions
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filter in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Force HTTPS (31536000 seconds = 1 year)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Content Security Policy (incluir frontend y API)
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Ajustar si frontend endurece CSP
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' https://preciosregulados-api.onrender.com https://cuantocuestauruguay.com https://www.cuantocuestauruguay.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (disable unnecessary features)
        permissions = ["geolocation=()", "microphone=()", "camera=()", "payment=()", "usb=()", "magnetometer=()"]
        response.headers["Permissions-Policy"] = ", ".join(permissions)

        # Remove server header (MutableHeaders doesn't support .pop())
        if "Server" in response.headers:
            del response.headers["Server"]

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting in-memory (per-IP) with separate limits for ETL endpoints"""

    def __init__(self, app, requests_per_minute: int = 60, requests_per_minute_etl: int = 5):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_minute_etl = requests_per_minute_etl
        self.request_counts = {}
        self.window_size = 60  # seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP (consider X-Forwarded-For if behind proxy)
        client_ip = request.client.host
        current_time = time.time()

        # Clean old entries
        self.request_counts = {
            ip: [(timestamp, count) for timestamp, count in requests if current_time - timestamp < self.window_size]
            for ip, requests in self.request_counts.items()
        }

        # Get requests for this IP in current window
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []

        ip_requests = self.request_counts[client_ip]
        request_count = sum(count for _, count in ip_requests)

        # Seleccionar límite según path (endpoints ETL más estrictos)
        limit = self.requests_per_minute_etl if request.url.path.startswith("/api/v1/etl") else self.requests_per_minute

        # Check rate limit
        if request_count >= limit:
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=429,
                headers={
                    "Retry-After": str(self.window_size),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + self.window_size)),
                },
            )

        # Add this request
        self.request_counts[client_ip].append((current_time, 1))

        response = await call_next(request)

        # Add rate limit headers
        remaining = limit - request_count - 1
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_size))

        return response


def setup_security_middleware(app):
    """
    Configure all security middleware for the FastAPI app

    Usage in main.py:
        from app.middleware.security import setup_security_middleware
        setup_security_middleware(app)
    """
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Add rate limiting (límites configurables desde settings)
    from app.core.config import settings

    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_GENERAL,
        requests_per_minute_etl=settings.RATE_LIMIT_ETL,
    )

    return app
