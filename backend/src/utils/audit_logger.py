from datetime import datetime
import logging
from typing import Optional, Dict, Any
from ..models.user import CurrentUser


class AuditLogger:
    """
    Utility class for logging authentication events and activities
    """

    def __init__(self):
        self.logger = logging.getLogger("auth_audit")
        # Set up basic logging configuration if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_login_attempt(
        self,
        user_id: str,
        email: str,
        ip_address: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a user login attempt

        Args:
            user_id: ID of the user attempting to log in
            email: Email of the user attempting to log in
            ip_address: IP address of the login attempt
            success: Whether the login attempt was successful
            details: Additional details about the login attempt
        """
        log_data = {
            "event": "login_attempt",
            "user_id": user_id,
            "email": email,
            "ip_address": ip_address,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }

        if success:
            self.logger.info(f"LOGIN_SUCCESS: User {user_id} ({email}) logged in from {ip_address}", extra=log_data)
        else:
            self.logger.warning(f"LOGIN_FAILED: Failed login attempt for user {email} from {ip_address}", extra=log_data)

    def log_logout(
        self,
        user_id: str,
        email: str,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a user logout event

        Args:
            user_id: ID of the user logging out
            email: Email of the user logging out
            ip_address: IP address of the logout request
            details: Additional details about the logout
        """
        log_data = {
            "event": "logout",
            "user_id": user_id,
            "email": email,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }

        self.logger.info(f"LOGOUT: User {user_id} ({email}) logged out from {ip_address}", extra=log_data)

    def log_token_validation(
        self,
        token_subject: str,
        user_id: str,
        ip_address: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a JWT token validation event

        Args:
            token_subject: Subject of the token being validated
            user_id: ID of the user associated with the token
            ip_address: IP address of the validation request
            success: Whether the token validation was successful
            details: Additional details about the validation
        """
        log_data = {
            "event": "token_validation",
            "token_subject": token_subject,
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }

        if success:
            self.logger.info(f"TOKEN_VALID: Valid token for user {user_id} from {ip_address}", extra=log_data)
        else:
            self.logger.warning(f"TOKEN_INVALID: Invalid token for user {user_id} from {ip_address}", extra=log_data)

    def log_permission_denied(
        self,
        user_id: str,
        requested_resource: str,
        action: str,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a permission denied event

        Args:
            user_id: ID of the user denied permission
            requested_resource: Resource the user tried to access
            action: Action the user tried to perform
            ip_address: IP address of the request
            details: Additional details about the denied access
        """
        log_data = {
            "event": "permission_denied",
            "user_id": user_id,
            "requested_resource": requested_resource,
            "action": action,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }

        self.logger.warning(
            f"PERMISSION_DENIED: User {user_id} denied access to {requested_resource} for action {action} from {ip_address}",
            extra=log_data
        )

    def log_security_violation(
        self,
        violation_type: str,
        user_id: Optional[str],
        ip_address: Optional[str],
        details: Optional[Dict[str, Any]]
    ):
        """
        Log a security violation event

        Args:
            violation_type: Type of security violation
            user_id: ID of the user involved in the violation (if applicable)
            ip_address: IP address of the violation
            details: Additional details about the violation
        """
        log_data = {
            "event": "security_violation",
            "violation_type": violation_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }

        self.logger.critical(
            f"SECURITY_VIOLATION: {violation_type} detected from IP {ip_address} for user {user_id}",
            extra=log_data
        )

    def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        ip_address: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log data access events for audit trail

        Args:
            user_id: ID of the user accessing data
            resource_type: Type of resource being accessed
            resource_id: ID of the specific resource
            action: Action being performed (read, write, delete, etc.)
            ip_address: IP address of the access request
            success: Whether the access was successful
            details: Additional details about the access
        """
        log_data = {
            "event": "data_access",
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "ip_address": ip_address,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }

        if success:
            self.logger.info(
                f"DATA_ACCESS: User {user_id} performed {action} on {resource_type}/{resource_id} from {ip_address}",
                extra=log_data
            )
        else:
            self.logger.warning(
                f"DATA_ACCESS_FAILED: User {user_id} failed {action} on {resource_type}/{resource_id} from {ip_address}",
                extra=log_data
            )


# Global instance of audit logger
audit_logger = AuditLogger()