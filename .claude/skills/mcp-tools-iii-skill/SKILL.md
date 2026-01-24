---
name: mcp-tools-iii-skill
description: Implement and manage MCP tools securely for Phase-III Todo AI Chatbot, including task operations, user ownership validation, stateless persistence, and Official MCP SDK integration.
---

# MCP Tools Skill (Phase III)

## Instructions

1. **Tool implementation**
   - Implement the following MCP tools:
     - `add_task` — create a new task in the database
     - `list_tasks` — retrieve tasks with optional filters (all, pending, completed)
     - `complete_task` — mark a task as completed
     - `delete_task` — remove a task
     - `update_task` — modify task title or description
   - Ensure each tool follows the defined API contract and MCP schema

2. **Input validation**
   - Validate all required parameters for each tool
   - Handle missing, invalid, or malformed inputs gracefully
   - Return structured error responses for invalid operations

3. **User ownership verification**
   - Confirm that `user_id` in tool request matches the authenticated user
   - Prevent access or modification of other users’ data
   - Log violations or unauthorized access attempts for auditing

4. **Stateless persistence**
   - MCP tools must not store any server-side session state
   - Persist all task state in the database only
   - Support full conversation replay from database after server restart

5. **Error handling**
   - Gracefully handle errors such as task not found or invalid parameters
   - Return clear and consistent error messages
   - Avoid exposing internal database or server details

6. **Official MCP SDK integration**
   - Use MCP SDK to handle all tool execution and communication
   - Ensure compatibility with Phase-III AI agents and stateless server design
   - Do not include conversational logic in the MCP tools themselves

## Best Practices
- Enforce input validation and type checking for all tools
- Keep tools stateless and isolated from agent reasoning
- Maintain predictable and deterministic behavior for testing
- Log tool operations and results for audit and debugging
- Align tool contracts strictly with constitution.md and Phase-III specifications

## Example Structure
```python
from mcp_sdk import MCPTool
from database_skill import Task

class AddTaskTool(MCPTool):
    name = "add_task"

    def execute(self, user_id: str, title: str, description: str = ""):
        if not user_id or not title:
            return {"error": "Missing required parameters"}
        # Persist task in database
        task = Task(user_id=user_id, title=title, description=description)
        task.save()
        return {"task_id": task.id, "status": "created", "title": task.title}

class ListTasksTool(MCPTool):
    name = "list_tasks"

    def execute(self, user_id: str, status: str = "all"):
        tasks = Task.get_all(user_id=user_id, status=status)
        return [t.dict() for t in tasks]

# Similarly implement complete_task, delete_task, update_task tools
