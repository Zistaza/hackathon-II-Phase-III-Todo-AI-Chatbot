from fastapi import Request, HTTPException, status
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from ..utils.jwt import verify_token
from ..models.user import CurrentUser
from ..exceptions.auth import (
    MissingTokenException,
    InvalidTokenException,
    TokenExpiredException,
    InsufficientPermissionsException
)


class ChatAuthMiddleware:
    """
    Middleware class for validating JWT tokens specifically for chat endpoints.
    Ensures that the user is authenticated and authorized to access chat functionality.
    """

    def __init__(self):
        self.security = HTTPBearer(auto_error=False)

    async def authenticate_request(self, request: Request) -> CurrentUser:
        """
        Authenticate the incoming request by validating the JWT token

        Args:
            request: The incoming FastAPI request

        Returns:
            CurrentUser: The authenticated user information

        Raises:
            MissingTokenException: If no token is provided
            InvalidTokenException: If the token is invalid
            TokenExpiredException: If the token has expired
            InsufficientPermissionsException: If user lacks permissions
        """
        # Extract authorization credentials from the request
        credentials: Optional[HTTPAuthorizationCredentials] = await self.security.__call__(request)

        if credentials is None:
            raise MissingTokenException("Authorization token is required for chat access")

        token = credentials.credentials

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

        # Create and return current user object
        current_user = CurrentUser(
            user_id=token_data.user_id,
            email=token_data.email,
            is_authenticated=True
        )

        return current_user

    async def validate_user_access_to_chat(self, request: Request, user_id: str) -> bool:
        """
        Validate that the authenticated user has access to the specified user's chat

        Args:
            request: The incoming FastAPI request
            user_id: The user ID from the URL path parameter

        Returns:
            bool: True if user has access, raises exception if not
        """
        current_user = await self.authenticate_request(request)

        # Verify that the user ID in the path matches the user ID in the token
        if current_user.user_id != user_id:
            raise InsufficientPermissionsException(
                f"Access denied: Cannot access chat for user {user_id}. "
                f"You are authenticated as user {current_user.user_id}"
            )

        return True


# Global instance of chat auth middleware
chat_auth_middleware = ChatAuthMiddleware()