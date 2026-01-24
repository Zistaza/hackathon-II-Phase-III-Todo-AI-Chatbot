from typing import Optional, Dict, Any, List
from datetime import datetime
import jwt
import re

from ..utils.jwt import verify_token, inspect_token, JWTData
from ..models.user import CurrentUser
from ..exceptions.auth import (
    InvalidTokenException,
    TokenExpiredException,
    MissingTokenException,
    InsufficientPermissionsException
)


class AuthValidator:
    """
    Comprehensive authentication validation utilities with enhanced error handling
    """

    @staticmethod
    def validate_token_comprehensive(token: str, expected_audience: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive validation of a JWT token

        Args:
            token: JWT token to validate
            expected_audience: Optional expected audience for the token

        Returns:
            Dictionary with validation results and token data
        """
        result = {
            "valid": False,
            "token_data": None,
            "errors": [],
            "warnings": []
        }

        if not token:
            result["errors"].append("Token is required")
            return result

        # Inspect the token structure first
        inspection = inspect_token(token)
        if not inspection:
            result["errors"].append("Token has invalid format")
            return result

        # Check if token is expired
        if inspection.get("is_expired", False):
            result["errors"].append("Token has expired")
            return result

        # Check audience if specified
        if expected_audience and inspection.get("payload", {}).get("aud") != expected_audience:
            result["errors"].append(f"Token audience mismatch. Expected: {expected_audience}")
            return result

        # Verify the token signature and claims
        token_data = verify_token(token)
        if not token_data:
            result["errors"].append("Token signature verification failed")
            return result

        # Validate required claims
        if not token_data.user_id:
            result["errors"].append("Token missing required user_id claim")
            return result

        if not token_data.email:
            result["errors"].append("Token missing required email claim")
            return result

        # Check if token has reasonable expiration time (not too far in the future)
        if hasattr(token_data, 'exp') and token_data.exp:
            current_time = int(datetime.utcnow().timestamp())
            time_diff = token_data.exp - current_time
            # Warn if token expires more than 30 days from now
            if time_diff > 30 * 24 * 60 * 60:
                result["warnings"].append("Token has unusually long expiration time")

        result["valid"] = True
        result["token_data"] = token_data
        return result

    @staticmethod
    def validate_user_permissions(
        current_user: CurrentUser,
        required_permissions: List[str],
        user_permissions: Optional[List[str]] = None
    ) -> bool:
        """
        Validate that a user has the required permissions

        Args:
            current_user: The authenticated user
            required_permissions: List of permissions required for access
            user_permissions: Optional list of user's actual permissions

        Returns:
            bool: True if user has all required permissions
        """
        if not required_permissions:
            return True

        if not user_permissions:
            # In a real implementation, this would come from database
            # For now, we'll return True for authenticated users
            return True

        # Check if user has all required permissions
        for perm in required_permissions:
            if perm not in user_permissions:
                raise InsufficientPermissionsException(
                    f"User {current_user.user_id} lacks required permission: {perm}"
                )

        return True

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format using regex

        Args:
            email: Email address to validate

        Returns:
            bool: True if email format is valid
        """
        if not email:
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password strength and return validation results

        Args:
            password: Password to validate

        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": True,
            "strength_score": 0,
            "requirements_met": [],
            "requirements_missing": [],
            "feedback": []
        }

        score = 0
        min_length = len(password) >= 8
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        if min_length:
            score += 1
            result["requirements_met"].append("minimum_length")
        else:
            result["requirements_missing"].append("minimum_length")
            result["feedback"].append("Password must be at least 8 characters long")

        if has_uppercase:
            score += 1
            result["requirements_met"].append("uppercase_letter")
        else:
            result["requirements_missing"].append("uppercase_letter")
            result["feedback"].append("Password must contain at least one uppercase letter")

        if has_lowercase:
            score += 1
            result["requirements_met"].append("lowercase_letter")
        else:
            result["requirements_missing"].append("lowercase_letter")
            result["feedback"].append("Password must contain at least one lowercase letter")

        if has_digit:
            score += 1
            result["requirements_met"].append("digit")
        else:
            result["requirements_missing"].append("digit")
            result["feedback"].append("Password must contain at least one digit")

        if has_special:
            score += 1
            result["requirements_met"].append("special_character")
        else:
            result["requirements_missing"].append("special_character")
            result["feedback"].append("Password must contain at least one special character")

        result["strength_score"] = score
        result["valid"] = score >= 4  # At least 4 out of 5 requirements met

        if result["valid"]:
            result["feedback"].append("Password meets strength requirements")

        return result

    @staticmethod
    def validate_user_id_format(user_id: str) -> bool:
        """
        Validate user ID format

        Args:
            user_id: User ID to validate

        Returns:
            bool: True if user ID format is valid
        """
        if not user_id or len(user_id) < 1:
            return False

        # Allow alphanumeric, hyphens, and underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        return re.match(pattern, user_id) is not None

    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent injection attacks

        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not input_str:
            return ""

        # Truncate to max length
        input_str = input_str[:max_length]

        # Remove potentially dangerous characters/sequences
        # This is a basic sanitization - in production, use a dedicated library
        sanitized = input_str.replace('<script', '').replace('javascript:', '') \
                            .replace('vbscript:', '').replace('onload', '') \
                            .replace('onerror', '')

        return sanitized


class AuditLogger:
    """
    Utility class for logging authentication events
    """

    @staticmethod
    def log_auth_event(
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an authentication-related event

        Args:
            event_type: Type of authentication event (login, logout, token_validation, etc.)
            user_id: ID of the user involved in the event
            ip_address: IP address of the request
            success: Whether the event was successful
            details: Additional details about the event
        """
        import logging
        logger = logging.getLogger(__name__)

        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }

        log_msg = f"AUTH_EVENT: {event_type} - User: {user_id}, Success: {success}"
        if success:
            logger.info(log_msg, extra=log_data)
        else:
            logger.warning(log_msg, extra=log_data)

    @staticmethod
    def log_security_event(
        event_type: str,
        user_id: Optional[str],
        ip_address: Optional[str],
        details: Optional[Dict[str, Any]]
    ):
        """
        Log a security-related event

        Args:
            event_type: Type of security event
            user_id: ID of the user involved
            ip_address: IP address of the request
            details: Additional details about the event
        """
        import logging
        logger = logging.getLogger(__name__)

        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }

        log_msg = f"SECURITY_EVENT: {event_type} - User: {user_id}"
        logger.warning(log_msg, extra=log_data)


# Global instances
auth_validator = AuthValidator()
audit_logger = AuditLogger()