from typing import Optional
from ..models.user import CurrentUser
from ..utils.jwt import verify_token
from ..exceptions.auth import (
    MissingTokenException,
    InvalidTokenException,
    TokenExpiredException,
    InsufficientPermissionsException
)


def validate_mcp_tool_access(
    token: str,
    resource_owner_id: str,
    required_permissions: Optional[list] = None
) -> bool:
    """
    Validate MCP tool access by checking JWT token and resource ownership

    Args:
        token: JWT token to validate
        resource_owner_id: ID of the user who owns the resource
        required_permissions: Optional list of required permissions

    Returns:
        bool: True if access is granted, raises exception if not
    """
    # Verify the token
    token_data = verify_token(token)

    if token_data is None:
        # Determine the specific reason for token failure
        from ..utils.jwt import inspect_token
        inspection = inspect_token(token)

        if inspection is None:
            raise InvalidTokenException("Invalid token format")
        elif inspection.get("is_expired", True):
            raise TokenExpiredException("Token has expired")
        else:
            raise InvalidTokenException("Invalid token signature or claims")

    # Check if the token holder is the resource owner
    if token_data.user_id != resource_owner_id:
        raise InsufficientPermissionsException(
            f"Access denied: User {token_data.user_id} does not own resource "
            f"belonging to user {resource_owner_id}"
        )

    # If permissions are required, check if user has them (basic implementation)
    if required_permissions:
        # In a real implementation, you would check user permissions
        # For now, we'll just return True if user is the owner
        pass

    return True


def get_current_user_from_token(token: str) -> Optional[CurrentUser]:
    """
    Extract current user information from JWT token

    Args:
        token: JWT token to extract user information from

    Returns:
        CurrentUser if token is valid, None otherwise
    """
    token_data = verify_token(token)

    if token_data is None:
        return None

    return CurrentUser(
        user_id=token_data.user_id,
        email=token_data.email,
        is_authenticated=True
    )


def validate_resource_ownership(
    token: str,
    resource_owner_id: str,
    resource_id: str
) -> bool:
    """
    Validate that the user identified by the token owns the specified resource

    Args:
        token: JWT token to validate
        resource_owner_id: ID of the user who should own the resource
        resource_id: ID of the resource to validate ownership for

    Returns:
        bool: True if user owns the resource, raises exception if not
    """
    current_user = get_current_user_from_token(token)

    if not current_user:
        raise MissingTokenException("Valid token is required to access resources")

    if current_user.user_id != resource_owner_id:
        raise InsufficientPermissionsException(
            f"Resource {resource_id} does not belong to user {current_user.user_id}. "
            f"It belongs to user {resource_owner_id}."
        )

    return True


def check_user_permissions(
    token: str,
    required_permissions: list,
    user_permissions: Optional[list] = None
) -> bool:
    """
    Check if user has required permissions

    Args:
        token: JWT token to validate
        required_permissions: List of permissions required
        user_permissions: Optional list of user's permissions (would come from DB in real app)

    Returns:
        bool: True if user has all required permissions, raises exception if not
    """
    current_user = get_current_user_from_token(token)

    if not current_user:
        raise MissingTokenException("Valid token is required to check permissions")

    # In a real implementation, you would fetch user permissions from the database
    # For now, we'll assume all authenticated users have basic permissions
    if not required_permissions:
        return True

    # Placeholder for permission checking
    # In a real implementation, you would check against user's actual permissions
    return True