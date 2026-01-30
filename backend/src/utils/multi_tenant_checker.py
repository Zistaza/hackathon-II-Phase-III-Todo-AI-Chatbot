"""
Utility for checking multi-tenant access and user permissions.
"""
from typing import Optional
from ..models.user_model import User
from ..database import engine
from sqlmodel import select


class MultiTenantChecker:
    @staticmethod
    async def verify_user_access(user_id: str) -> bool:
        """
        Verify that a user exists and has access to the system.

        Args:
            user_id: The user ID to verify

        Returns:
            True if user exists and has access, False otherwise
        """
        if not user_id:
            return False

        try:
            # Execute query using engine directly
            def _verify_user_sync():
                with Session(engine) as session:
                    # Query for user by ID
                    statement = select(User).where(User.id == user_id)
                    result = session.execute(statement)
                    user = result.first()

                    # Return True if user exists
                    return user is not None

            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _verify_user_sync)
        except Exception:
            # If there's an error querying the database, return False
            return False

    @staticmethod
    async def verify_user_owns_resource(user_id: str, resource_user_id: str) -> bool:
        """
        Verify that a user owns a specific resource.

        Args:
            user_id: The ID of the user making the request
            resource_user_id: The ID of the user who owns the resource

        Returns:
            True if user owns the resource, False otherwise
        """
        if not user_id or not resource_user_id:
            return False

        return user_id == resource_user_id

    @staticmethod
    async def check_cross_tenant_access(request_user_id: str, resource_user_id: str) -> bool:
        """
        Check if a user is attempting cross-tenant access.

        Args:
            request_user_id: The ID of the user making the request
            resource_user_id: The ID of the user who owns the resource

        Returns:
            True if cross-tenant access is detected, False if access is valid
        """
        if not request_user_id or not resource_user_id:
            return True  # Consider it cross-tenant if either ID is missing

        return request_user_id != resource_user_id