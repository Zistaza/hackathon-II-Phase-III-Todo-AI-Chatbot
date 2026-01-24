from fastapi import Request, HTTPException, status, Depends
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from ..utils.mcp_auth import validate_mcp_tool_access, get_current_user_from_token
from ..models.user import CurrentUser
from ..models.mcp_tool import MCPToolResource
from ..exceptions.auth import (
    MissingTokenException,
    InvalidTokenException,
    TokenExpiredException,
    InsufficientPermissionsException
)


class MCPTokenValidator:
    """
    Middleware class for validating MCP tool access using JWT tokens.
    Ensures that MCP tools are properly authenticated and authorized to access resources.
    """

    def __init__(self):
        self.security = HTTPBearer(auto_error=False)

    async def authenticate_mcp_request(
        self,
        request: Request,
        required_resources: Optional[List[MCPToolResource]] = None
    ) -> CurrentUser:
        """
        Authenticate an MCP tool request by validating the JWT token

        Args:
            request: The incoming FastAPI request
            required_resources: Optional list of resources that need access validation

        Returns:
            CurrentUser: The authenticated user information

        Raises:
            MissingTokenException: If no token is provided
            InvalidTokenException: If the token is invalid
            TokenExpiredException: If the token has expired
            InsufficientPermissionsException: If user lacks permissions for resources
        """
        # Extract authorization credentials from the request
        credentials: Optional[HTTPAuthorizationCredentials] = await self.security.__call__(request)

        if credentials is None:
            raise MissingTokenException("Authorization token is required for MCP tool access")

        token = credentials.credentials

        # Get current user from token
        current_user = get_current_user_from_token(token)

        if current_user is None:
            # Determine the specific reason for token failure
            from ..utils.jwt import inspect_token
            inspection = inspect_token(token)

            if inspection is None:
                raise InvalidTokenException("Invalid token format")
            elif inspection.get("is_expired", True):
                raise TokenExpiredException("Token has expired")
            else:
                raise InvalidTokenException("Invalid token signature or claims")

        # If required resources are specified, validate access to them
        if required_resources:
            for resource in required_resources:
                if current_user.user_id != resource.owner_id:
                    raise InsufficientPermissionsException(
                        f"Access denied: User {current_user.user_id} does not own "
                        f"resource {resource.resource_id} of type {resource.resource_type}"
                    )

        return current_user

    async def validate_user_owns_resource(
        self,
        request: Request,
        resource_owner_id: str,
        resource_id: str
    ) -> bool:
        """
        Validate that the authenticated user owns the specified resource

        Args:
            request: The incoming FastAPI request
            resource_owner_id: ID of the user who should own the resource
            resource_id: ID of the resource to validate ownership for

        Returns:
            bool: True if user owns the resource, raises exception if not
        """
        # Extract authorization credentials from the request
        credentials: Optional[HTTPAuthorizationCredentials] = await self.security.__call__(request)

        if credentials is None:
            raise MissingTokenException("Authorization token is required to access resources")

        token = credentials.credentials

        # Validate resource ownership
        from ..utils.mcp_auth import validate_resource_ownership
        return validate_resource_ownership(token, resource_owner_id, resource_id)

    def get_mcp_auth_dependency(
        self,
        required_resources: Optional[List[MCPToolResource]] = None
    ):
        """
        Create a FastAPI dependency for MCP tool authentication

        Args:
            required_resources: Optional list of resources that need access validation

        Returns:
            Dependency function for FastAPI
        """
        async def auth_dependency(
            request: Request
        ) -> CurrentUser:
            return await self.authenticate_mcp_request(request, required_resources)

        return auth_dependency


# Global instance of MCP auth middleware
mcp_auth_validator = MCPTokenValidator()


def get_current_mcp_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> CurrentUser:
    """
    FastAPI dependency to extract the current user from JWT token for MCP tools

    Args:
        request: The incoming FastAPI request
        credentials: HTTP authorization credentials from the Authorization header

    Returns:
        CurrentUser: Authenticated user information

    Raises:
        HTTPException: If token is invalid, expired, or missing required claims
    """
    token = credentials.credentials

    # Get current user from token
    current_user = get_current_user_from_token(token)

    if current_user is None:
        # Determine the specific reason for token failure
        from ..utils.jwt import inspect_token
        inspection = inspect_token(token)

        if inspection is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif inspection.get("is_expired", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return current_user