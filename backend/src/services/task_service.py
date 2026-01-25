"""
Service layer for handling task-related operations with multi-tenant isolation.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import select, Session
from src.models.task_model import Task
from src.database import get_session
from src.utils.multi_tenant_checker import MultiTenantChecker


class TaskService:
    def __init__(self):
        pass

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
            # Validate user exists and has access
            if not await MultiTenantChecker.verify_user_access(user_id):
                return None

            # Create new task instance
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                completed=False  # New tasks are not completed by default
            )

            # Save to database
            async with get_session() as session:
                session.add(task)
                await session.commit()
                await session.refresh(task)

            return task
        except Exception:
            return None

    async def get_tasks_by_user_id(
        self,
        user_id: str,
        filter_completed: Optional[bool] = False
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
            # Validate user exists and has access
            if not await MultiTenantChecker.verify_user_access(user_id):
                return []

            # Build query
            query = select(Task).where(Task.user_id == user_id)

            if filter_completed:
                query = query.where(Task.completed == False)

            # Execute query
            async with get_session() as session:
                result = await session.execute(query)
                tasks = result.scalars().all()

            return tasks
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
            # Validate user exists and has access
            if not await MultiTenantChecker.verify_user_access(user_id):
                return None

            # Validate UUID format
            uuid.UUID(task_id)

            # Build query
            query = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )

            # Execute query
            async with get_session() as session:
                result = await session.execute(query)
                task = result.scalar_one_or_none()

            return task
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
            # Validate user exists and has access
            if not await MultiTenantChecker.verify_user_access(user_id):
                return None

            # Get the task
            task = await self.get_task_by_id(task_id, user_id)
            if not task:
                return None

            # Update completion status
            task.completed = completed
            task.updated_at = datetime.now()

            # Save to database
            async with get_session() as session:
                session.add(task)
                await session.commit()
                await session.refresh(task)

            return task
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
            **kwargs: Properties to update (title, description, priority, completed)

        Returns:
            Updated Task object or None if failed
        """
        try:
            # Validate user exists and has access
            if not await MultiTenantChecker.verify_user_access(user_id):
                return None

            # Get the task
            task = await self.get_task_by_id(task_id, user_id)
            if not task:
                return None

            # Update allowed properties
            allowed_fields = {'title', 'description', 'priority', 'completed'}
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(task, field, value)

            # Update timestamp
            task.updated_at = datetime.now()

            # Save to database
            async with get_session() as session:
                session.add(task)
                await session.commit()
                await session.refresh(task)

            return task
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
            # Validate user exists and has access
            if not await MultiTenantChecker.verify_user_access(user_id):
                return False

            # Get the task
            task = await self.get_task_by_id(task_id, user_id)
            if not task:
                return False

            # Delete the task
            async with get_session() as session:
                await session.delete(task)
                await session.commit()

            return True
        except Exception:
            return False