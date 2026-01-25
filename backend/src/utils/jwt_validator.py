"""
Utility for validating JWT tokens and extracting user information.
"""
import os
import jwt
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "fallback_secret_key_for_development")
ALGORITHM = "HS256"


class JWTValidator:
    @staticmethod
    def validate_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a JWT token and extract user information.

        Args:
            token: JWT token string

        Returns:
            Dictionary with user information if valid, None otherwise
        """
        if not token:
            return None

        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            # Decode the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check if token has expired
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                return None

            # Return user data from token
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "exp": exp
            }
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Invalid token
            return None
        except Exception:
            # Other error occurred
            return None

    @staticmethod
    def decode_token_without_validation(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode a JWT token without validation (for debugging purposes only).

        Args:
            token: JWT token string

        Returns:
            Dictionary with token contents if decodable, None otherwise
        """
        if not token:
            return None

        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            # Decode the token without validation
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception:
            return None