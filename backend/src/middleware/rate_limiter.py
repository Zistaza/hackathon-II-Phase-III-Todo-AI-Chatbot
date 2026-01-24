from fastapi import Request, HTTPException, status
from typing import Dict, Optional
from datetime import datetime, timedelta
import time
import threading
from collections import defaultdict


class RateLimiter:
    """
    Rate limiting middleware for authentication endpoints to prevent abuse
    """

    def __init__(self):
        self.requests = defaultdict(list)  # key: identifier, value: list of timestamps
        self.lock = threading.Lock()

    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if a request from the given identifier is allowed

        Args:
            identifier: Unique identifier for the requester (IP address, user ID, etc.)
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed: bool, remaining_requests: int)
        """
        with self.lock:
            now = time.time()
            window_start = now - window_seconds

            # Clean up old requests outside the window
            self.requests[identifier] = [
                timestamp for timestamp in self.requests[identifier]
                if timestamp > window_start
            ]

            current_requests = len(self.requests[identifier])

            if current_requests >= max_requests:
                # Calculate remaining time until the oldest request expires
                oldest_request = min(self.requests[identifier]) if self.requests[identifier] else now
                retry_after = int(oldest_request + window_seconds - now)
                return False, retry_after

            # Add current request
            self.requests[identifier].append(now)

            remaining = max_requests - current_requests - 1
            return True, remaining

    def check_auth_endpoint_limits(self, request: Request) -> tuple[bool, int]:
        """
        Apply specific rate limits to authentication endpoints

        Args:
            request: The incoming request

        Returns:
            Tuple of (is_allowed: bool, retry_after_seconds: int)
        """
        # Get identifier - prioritize user ID if authenticated, otherwise use IP
        user_id = getattr(request.state, 'current_user_id', None) if hasattr(request.state, 'current_user_id') else None
        client_ip = request.client.host if request.client else "unknown"

        identifier = user_id if user_id else client_ip

        # Different rate limits for different auth endpoints
        url_path = request.url.path.lower()

        if '/auth/login' in url_path or '/auth/register' in url_path:
            # Lower rate limit for login/register endpoints to prevent brute force
            return self.is_allowed(identifier, max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
        elif '/auth/token' in url_path:
            # Higher rate limit for token refresh/verification
            return self.is_allowed(identifier, max_requests=30, window_seconds=60)  # 30 attempts per minute
        else:
            # Default rate limit for other auth-related endpoints
            return self.is_allowed(identifier, max_requests=100, window_seconds=60)  # 100 attempts per minute

    def cleanup_old_requests(self, max_age_seconds: int = 3600):
        """
        Clean up old request records to prevent memory leaks

        Args:
            max_age_seconds: Maximum age of request records to keep (default: 1 hour)
        """
        with self.lock:
            now = time.time()
            for identifier in list(self.requests.keys()):
                self.requests[identifier] = [
                    timestamp for timestamp in self.requests[identifier]
                    if timestamp > (now - max_age_seconds)
                ]
                # Remove empty lists
                if not self.requests[identifier]:
                    del self.requests[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter()


async def apply_rate_limit(request: Request) -> bool:
    """
    Apply rate limiting to a request

    Args:
        request: The incoming request

    Returns:
        True if request is allowed, raises HTTPException if rate limited
    """
    is_allowed, retry_after = rate_limiter.check_auth_endpoint_limits(request)

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )

    return True


class RateLimitMiddleware:
    """
    FastAPI middleware class for rate limiting
    """

    def __init__(self):
        self.rate_limiter = rate_limiter

    async def __call__(self, request: Request, call_next):
        # Apply rate limiting to authentication endpoints
        if '/auth' in request.url.path.lower() or '/api/' in request.url.path.lower():
            try:
                await apply_rate_limit(request)
            except HTTPException as e:
                return e

        response = await call_next(request)
        return response


# Function to manually check rate limits for specific endpoints
def check_rate_limit(
    identifier: str,
    max_requests: int = 10,
    window_seconds: int = 60
) -> tuple[bool, int]:
    """
    Manually check rate limits for a specific identifier

    Args:
        identifier: Unique identifier for the requester
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds

    Returns:
        Tuple of (is_allowed: bool, retry_after_seconds: int)
    """
    return rate_limiter.is_allowed(identifier, max_requests, window_seconds)