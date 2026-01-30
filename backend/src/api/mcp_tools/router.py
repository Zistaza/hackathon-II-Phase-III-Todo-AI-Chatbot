"""
MCP Tools router for the Todo AI Chatbot application.
Exposes MCP tools as FastAPI endpoints.
"""
from fastapi import APIRouter
from .add_task import add_task
from .complete_task import complete_task
from .delete_task import delete_task
from .list_tasks import list_tasks
from .update_task import update_task

router = APIRouter(prefix="/mcp-tools", tags=["mcp-tools"])

# Add routes for each MCP tool
@router.post("/add-task")
async def api_add_task(
    title: str,
    description: str = None,
    priority: int = None,
    token: str = None
):
    return await add_task(title=title, description=description, priority=priority, token=token)


@router.post("/complete-task")
async def api_complete_task(
    task_id: str,
    token: str = None
):
    return await complete_task(task_id=task_id, token=token)


@router.post("/delete-task")
async def api_delete_task(
    task_id: str,
    token: str = None
):
    return await delete_task(task_id=task_id, token=token)


@router.post("/list-tasks")
async def api_list_tasks(
    token: str = None
):
    return await list_tasks(token=token)


@router.post("/update-task")
async def api_update_task(
    task_id: str,
    title: str = None,
    description: str = None,
    priority: int = None,
    completed: bool = None,
    token: str = None
):
    return await update_task(
        task_id=task_id,
        title=title,
        description=description,
        priority=priority,
        completed=completed,
        token=token
    )