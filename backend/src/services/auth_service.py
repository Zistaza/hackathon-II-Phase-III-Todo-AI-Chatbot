from typing import Optional
from ..utils.jwt import create_access_token, verify_token, JWTData
from ..models.user import CurrentUser


class AuthService:
    """
    Service class for handling authentication operations including token creation,
    validation, and user identity management.
    """

    @staticmethod
    def create_token(user_id: str, email: str) -> str:
        """
        Create a new JWT access token for the given user.

        Args:
            user_id: Unique identifier for the user
            email: User's email address

        Returns:
            JWT access token string
        """
        from ..utils.jwt import JWTData

        jwt_data = JWTData(
            user_id=user_id,
            email=email
        )

        return create_access_token(data=jwt_data)

    @staticmethod
    def validate_token(token: str) -> Optional[CurrentUser]:
        """
        Validate a JWT token and return the current user information.

        Args:
            token: JWT token string to validate

        Returns:
            CurrentUser object if token is valid, None otherwise
        """
        token_data = verify_token(token)

        if token_data is None:
            return None

        return CurrentUser(
            user_id=token_data.user_id,
            email=token_data.email,
            is_authenticated=True
        )

    @staticmethod
    def extract_user_from_token(token: str) -> Optional[JWTData]:
        """
        Extract raw JWT data from token without full validation.

        Args:
            token: JWT token string to extract data from

        Returns:
            JWTData object if token format is valid, None otherwise
        """
        return verify_token(token)


# Global instance of auth service
auth_service = AuthService()