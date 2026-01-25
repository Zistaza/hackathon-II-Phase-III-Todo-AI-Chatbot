"""
JWT validation middleware for Todo AI Chatbot Agent
Validates JWT tokens and enforces user authentication
"""

from fastapi import HTTPException, Request
from typing import Dict, Any
import jwt
from ..utils.jwt_validator import JWTValidator  # Assuming this utility exists


class JWTValidationMiddleware:
    """
    Middleware to validate JWT tokens and enforce user authentication
    """

    def __init__(self, validator: JWTValidator = None):
        self.validator = validator or JWTValidator()

    async def __call__(self, request: Request):
        """
        Validate the JWT token in the request

        Args:
            request: The incoming request

        Raises:
            HTTPException: If the token is invalid or missing
        """
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid Authorization header"
            )

        token = auth_header[len("Bearer "):]

        try:
            # Validate the token
            payload = self.validator.validate_token(token)

            # Store user info in request state for later use
            request.state.user_id = payload.get("user_id")
            request.state.user_info = payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user

    Args:
        request: The incoming request

    Returns:
        Dictionary containing user information
    """
    if not hasattr(request.state, 'user_info'):
        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )

    return request.state.user_info