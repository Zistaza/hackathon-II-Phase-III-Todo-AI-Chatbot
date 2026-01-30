from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class TaskBase(SQLModel):
    """
    Base model for task with common fields
    """
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    priority: int = Field(default=1)  # Default priority level (1-5 scale)


class Task(TaskBase, table=True):
    """
    Task model for database storage

    Fields:
    - id: Unique task identifier
    - title: Task title (required)
    - description: Task description (optional)
    - completed: Completion status (default: False)
    - user_id: Reference to the user who owns this task
    - created_at: Task creation timestamp
    - updated_at: Last update timestamp
    """
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    priority: int = Field(default=1)  # Default priority level (1-5 scale)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """
    Model for creating a new task
    """
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: int = 1  # Default priority level


class TaskUpdate(SQLModel):
    """
    Model for updating task information
    """
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None


class TaskPublic(TaskBase):
    """
    Public model for task data (includes ID and timestamps)
    """
    id: str
    user_id: str
    priority: int
    created_at: datetime
    updated_at: datetime