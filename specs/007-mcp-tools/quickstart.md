# Quickstart Guide: Todo AI Chatbot MCP Tools

## Overview
This guide provides a quick setup and usage guide for the MCP (Model Context Protocol) tools in the Todo AI Chatbot. These tools enable AI agents to manage user tasks through standardized tool calls.

## Prerequisites
- Python 3.11+
- Poetry (dependency manager)
- PostgreSQL-compatible database (Neon Serverless PostgreSQL recommended)
- JWT authentication configured with shared secret

## Setup

### 1. Clone and Install Dependencies
```bash
# Clone the repository
git clone <repository-url>
cd hackathon-II-phase-III-todo-ai-chatbot

# Navigate to backend directory
cd backend

# Install dependencies
poetry install
```

### 2. Environment Configuration
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
JWT_SECRET=your-super-secret-jwt-key-here
BETTER_AUTH_SECRET=your-better-auth-secret
```

### 3. Database Setup
```bash
# Run database migrations
poetry run python -m src.database.migrate

# Initialize database
poetry run python -m src.database.init
```

### 4. Start the Server
```bash
# Start development server
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Available MCP Tools

### add_task
Creates a new task in the user's todo list.

**Schema:**
```json
{
  "name": "add_task",
  "description": "Add a new task to the user's todo list",
  "input_schema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Title of the task (required)"
      },
      "description": {
        "type": "string",
        "description": "Detailed description of the task (optional)"
      },
      "priority": {
        "type": "integer",
        "description": "Priority level (1-5, optional)",
        "minimum": 1,
        "maximum": 5
      }
    },
    "required": ["title"]
  }
}
```

**Example Call:**
```json
{
  "name": "add_task",
  "arguments": {
    "title": "Buy groceries",
    "description": "Milk, bread, eggs, fruits",
    "priority": 3
  }
}
```

### list_tasks
Retrieves all tasks for the authenticated user.

**Schema:**
```json
{
  "name": "list_tasks",
  "description": "Retrieve all tasks for the authenticated user",
  "input_schema": {
    "type": "object",
    "properties": {
      "filter_completed": {
        "type": "boolean",
        "description": "Whether to filter out completed tasks (optional, default: false)"
      }
    }
  }
}
```

**Example Call:**
```json
{
  "name": "list_tasks",
  "arguments": {
    "filter_completed": false
  }
}
```

### complete_task
Marks a specific task as completed.

**Schema:**
```json
{
  "name": "complete_task",
  "description": "Mark a specific task as completed",
  "input_schema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "ID of the task to complete (required)"
      },
      "completed": {
        "type": "boolean",
        "description": "Whether the task is completed (default: true)"
      }
    },
    "required": ["task_id"]
  }
}
```

**Example Call:**
```json
{
  "name": "complete_task",
  "arguments": {
    "task_id": "task-uuid-here",
    "completed": true
  }
}
```

### delete_task
Removes a task from the user's todo list.

**Schema:**
```json
{
  "name": "delete_task",
  "description": "Remove a task from the user's todo list",
  "input_schema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "ID of the task to delete (required)"
      }
    },
    "required": ["task_id"]
  }
}
```

**Example Call:**
```json
{
  "name": "delete_task",
  "arguments": {
    "task_id": "task-uuid-here"
  }
}
```

### update_task
Modifies an existing task's properties.

**Schema:**
```json
{
  "name": "update_task",
  "description": "Modify an existing task's properties",
  "input_schema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "ID of the task to update (required)"
      },
      "title": {
        "type": "string",
        "description": "New title for the task (optional)"
      },
      "description": {
        "type": "string",
        "description": "New description for the task (optional)"
      },
      "priority": {
        "type": "integer",
        "description": "New priority level (1-5, optional)",
        "minimum": 1,
        "maximum": 5
      },
      "completed": {
        "type": "boolean",
        "description": "Whether the task is completed (optional)"
      }
    },
    "required": ["task_id"]
  }
}
```

**Example Call:**
```json
{
  "name": "update_task",
  "arguments": {
    "task_id": "task-uuid-here",
    "title": "Updated task title",
    "priority": 5
  }
}
```

## Integration with Chat Endpoint

The MCP tools are accessible through the main chat endpoint:

```
POST /api/{user_id}/chat
```

The endpoint expects a JSON payload containing the user's message and potentially MCP tool calls. The system will process the request and return both the chat response and results from any MCP tools that were invoked.

## Authentication

All MCP tool calls require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt-token-here>
```

The JWT must contain the user_id claim that matches the user attempting to access the tools.

## Error Handling

All MCP tools return standardized error responses:

```json
{
  "success": false,
  "error": {
    "type": "error_type",
    "message": "Human-readable error message",
    "code": "error_code"
  }
}
```

Common error types:
- `AuthenticationError`: Invalid or expired JWT token
- `AuthorizationError`: Attempting to access another user's data
- `ValidationError`: Invalid input parameters
- `NotFoundError`: Requested task doesn't exist
- `InternalError`: Server-side processing error