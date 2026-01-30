"""
Service layer for handling task-related operations with multi-tenant isolation.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import select, Session
from ..models.task_model import Task
from ..models.user_model import User
from ..database import engine
from ..utils.multi_tenant_checker import MultiTenantChecker


from ..models.user_model import User

class TaskService:
    def __init__(self):
        pass

    def _ensure_user_exists_sync(self, user_id: str) -> bool:
        """
        Ensure that a user exists in the local database.
        If the user doesn't exist, create a minimal user record.

        Args:
            user_id: The ID of the user to ensure exists

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate user_id format first
            if not user_id or len(user_id) < 10:
                print(f"DEBUG: Invalid user_id format: {user_id}")
                return False

            # Check if user already exists - using synchronous session with engine
            with Session(engine) as session:
                statement = select(User).where(User.id == user_id)
                result = session.execute(statement)
                user = result.first()

                if user is None:
                    print(f"DEBUG: Creating user record for user_id: {user_id}")
                    # Create a minimal user record
                    # Since we don't have email/name from the JWT, we'll use placeholder values
                    # In a real application, you'd want to sync with the auth provider
                    new_user = User(
                        id=user_id,
                        email=f"user_{user_id}@placeholder.com",  # Placeholder email
                        name=f"User {user_id[:8]}",  # Use first 8 chars of user_id
                        password="$2b$12$placeholder_hash"  # Placeholder bcrypt hash
                    )

                    session.add(new_user)
                    session.commit()
                    print(f"DEBUG: Successfully created user record for user_id: {user_id}")

            return True
        except Exception as e:
            print(f"DEBUG: Error in _ensure_user_exists: {str(e)}")
            import traceback
            traceback.print_exc()
            # If we can't create the user, return False
            return False

    async def _ensure_user_exists(self, user_id: str) -> bool:
        """
        Async wrapper for _ensure_user_exists_sync to maintain API compatibility
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._ensure_user_exists_sync, user_id)

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: Optional[int] = None
    ) -> Optional[Task]:
        """
        Create a new task for a user.

        Args:
            user_id: The ID of the user creating the task
            title: The title of the task
            description: Optional description of the task
            priority: Optional priority level (1-5)

        Returns:
            Created Task object or None if failed
        """
        try:
            # Ensure the user exists in the local database
            user_ensure_success = await self._ensure_user_exists(user_id)
            if not user_ensure_success:
                print(f"DEBUG: Failed to ensure user exists: {user_id}")
                return None

            # Create new task instance - set default priority if not provided
            final_priority = priority if priority is not None else 1

            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=final_priority,
                completed=False  # New tasks are not completed by default
            )

            # Save to database - using engine directly
            def _create_task_sync():
                with Session(engine) as session:
                    session.add(task)
                    session.commit()
                    session.refresh(task)
                    return task

            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _create_task_sync)
            return result
        except Exception as e:
            print(f"DEBUG: Error in create_task: {str(e)}")
            # Log the exception for debugging but still return None to maintain API contract
            import traceback
            traceback.print_exc()
            return None

    async def get_tasks_by_user_id(
        self,
        user_id: str,
        filter_completed: Optional[bool] = None
    ) -> List[Task]:
        """
        Get all tasks for a specific user.

        Args:
            user_id: The ID of the user whose tasks to retrieve
            filter_completed: Whether to filter out completed tasks

        Returns:
            List of Task objects
        """
        try:
            # Ensure the user exists in the local database
            await self._ensure_user_exists(user_id)

            # Execute query using engine directly
            def _get_tasks_sync():
                with Session(engine) as session:
                    # Build query
                    query = select(Task).where(Task.user_id == user_id)

                    if filter_completed is not None:
                        query = query.where(Task.completed == filter_completed)

                    # Execute query
                    result = session.execute(query)
                    tasks = result.scalars().all()
                    return tasks

            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _get_tasks_sync)
        except Exception:
            return []

    async def get_task_by_id(
        self,
        task_id: str,
        user_id: str
    ) -> Optional[Task]:
        """
        Get a specific task by its ID and user ID.

        Args:
            task_id: The ID of the task to retrieve
            user_id: The ID of the user requesting the task

        Returns:
            Task object or None if not found
        """
        try:
            # Ensure the user exists in the local database
            await self._ensure_user_exists(user_id)

            # Validate UUID format
            uuid.UUID(task_id)

            # Execute query using engine directly
            def _get_task_sync():
                with Session(engine) as session:
                    # Build query
                    query = select(Task).where(
                        Task.id == task_id,
                        Task.user_id == user_id
                    )

                    # Execute query
                    result = session.execute(query)
                    task = result.scalar_one_or_none()
                    return task

            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _get_task_sync)
        except Exception:
            return None

    async def update_task_completion(
        self,
        task_id: str,
        user_id: str,
        completed: bool
    ) -> Optional[Task]:
        """
        Update the completion status of a task.

        Args:
            task_id: The ID of the task to update
            user_id: The ID of the user requesting the update
            completed: Whether the task is completed

        Returns:
            Updated Task object or None if failed
        """
        try:
            # Ensure the user exists in the local database
            await self._ensure_user_exists(user_id)

            # Get the task
            task = await self.get_task_by_id(task_id, user_id)
            if not task:
                return None

            # Update completion status and save
            def _update_task_completion_sync():
                with Session(engine) as session:
                    # Refresh the task from the database to avoid detached instance issues
                    refreshed_task = session.get(Task, task.id)
                    if not refreshed_task:
                        return None

                    refreshed_task.completed = completed
                    refreshed_task.updated_at = datetime.now()

                    session.add(refreshed_task)
                    session.commit()
                    session.refresh(refreshed_task)
                    return refreshed_task

            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _update_task_completion_sync)
        except Exception:
            return None

    async def update_task(
        self,
        task_id: str,
        user_id: str,
        **kwargs
    ) -> Optional[Task]:
        """
        Update properties of a task.

        Args:
            task_id: The ID of the task to update
            user_id: The ID of the user requesting the update
            **kwargs: Properties to update (title, description, completed)

        Returns:
            Updated Task object or None if failed
        """
        try:
            # Ensure the user exists in the local database
            await self._ensure_user_exists(user_id)

            # Update task in the database
            def _update_task_sync():
                with Session(engine) as session:
                    # Get the task from the database to avoid detached instance issues
                    task = session.get(Task, task_id)

                    # Verify the user owns this task
                    if not task or task.user_id != user_id:
                        return None

                    # Update allowed properties
                    allowed_fields = {'title', 'description', 'priority', 'completed'}
                    for field, value in kwargs.items():
                        if field in allowed_fields:
                            setattr(task, field, value)

                    # Update timestamp
                    task.updated_at = datetime.now()

                    # Save to database
                    session.add(task)
                    session.commit()
                    session.refresh(task)
                    return task

            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _update_task_sync)
        except Exception:
            return None

    async def delete_task(
        self,
        task_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a task.

        Args:
            task_id: The ID of the task to delete
            user_id: The ID of the user requesting the deletion

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure the user exists in the local database
            await self._ensure_user_exists(user_id)

            # Delete the task from database
            def _delete_task_sync():
                with Session(engine) as session:
                    # Get the task from the database to avoid detached instance issues
                    task = session.get(Task, task_id)

                    # Verify the user owns this task
                    if not task or task.user_id != user_id:
                        return False

                    # Delete the task
                    session.delete(task)
                    session.commit()
                    return True

            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _delete_task_sync)
        except Exception:
            return False