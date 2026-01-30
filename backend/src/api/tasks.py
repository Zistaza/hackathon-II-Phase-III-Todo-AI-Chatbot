from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from ..models.user import CurrentUser
from ..middleware.auth import get_current_user
from ..models.user_model import User
from ..database import get_session
from ..models.task_model import Task, TaskCreate, TaskUpdate, TaskPublic
from datetime import datetime

router = APIRouter()


@router.get("/{user_id}/tasks", response_model=List[Task])
async def get_tasks(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for the authenticated user

    Args:
        user_id: User ID from URL path
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        List of tasks belonging to the user
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    # This ensures multi-tenant data isolation
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in get tasks - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's tasks"
        )

    # Query the database for tasks belonging to the current user
    statement = select(Task).where(Task.user_id == current_user.user_id)
    results = session.exec(statement)
    tasks = results.all()

    return tasks


@router.post("/{user_id}/tasks", response_model=Task)
async def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user

    Args:
        user_id: User ID from URL path
        task: Task data to create
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Created task
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in task creation - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot create tasks for another user"
        )

    # Create a new task record in the database
    db_task = Task(
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=current_user.user_id
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


@router.get("/{user_id}/tasks/{id}", response_model=Task)
async def get_task(
    user_id: str,
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task for the authenticated user

    Args:
        user_id: User ID from URL path
        id: Task ID to retrieve
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Specific task if it belongs to the user
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in get task by ID - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's task"
        )

    # Query for the specific task in the database
    statement = select(Task).where(Task.id == id, Task.user_id == current_user.user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return db_task


@router.put("/{user_id}/tasks/{id}", response_model=Task)
async def update_task(
    user_id: str,
    id: str,
    task_update: TaskUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task for the authenticated user

    Args:
        user_id: User ID from URL path
        id: Task ID to update
        task_update: Updated task data
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Updated task
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in update task - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot update another user's task"
        )

    # Query for the specific task in the database
    statement = select(Task).where(Task.id == id, Task.user_id == current_user.user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update the task with provided fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


@router.delete("/{user_id}/tasks/{id}")
async def delete_task(
    user_id: str,
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task for the authenticated user

    Args:
        user_id: User ID from URL path
        id: Task ID to delete
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Success message
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in delete task - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot delete another user's task"
        )

    # Query for the specific task in the database
    statement = select(Task).where(Task.id == id, Task.user_id == current_user.user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Delete the task from the database
    session.delete(db_task)
    session.commit()

    return {"message": f"Task {id} deleted successfully"}


@router.patch("/{user_id}/tasks/{id}/complete")
async def toggle_task_completion(
    user_id: str,
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle completion status of a specific task for the authenticated user

    Args:
        user_id: User ID from URL path
        id: Task ID to toggle
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Updated completion status
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in toggle task completion - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot modify another user's task"
        )

    # Query for the specific task in the database
    statement = select(Task).where(Task.id == id, Task.user_id == current_user.user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle the completion status
    db_task.completed = not db_task.completed
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return {"id": db_task.id, "completed": db_task.completed, "message": f"Task {id} completion status updated"}