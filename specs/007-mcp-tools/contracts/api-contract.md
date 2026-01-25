# API Contract: Todo AI Chatbot MCP Tools

## Overview
This document defines the API contracts for the MCP (Model Context Protocol) tools in the Todo AI Chatbot. These contracts specify the exact input/output schemas, validation rules, and behavior for each tool.

## Common Headers
All endpoints require the following headers:

```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

## Authentication & Authorization
- All MCP tools require a valid JWT token in the Authorization header
- The user_id in the JWT must match the authenticated user context
- Unauthorized requests return HTTP 401
- Cross-tenant access attempts return HTTP 403

## MCP Tool Contracts

### add_task

#### Endpoint
This tool is accessible via the chat endpoint when an AI agent calls the add_task function.

#### Request Schema
```json
{
  "name": "add_task",
  "arguments": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "Title of the task (required)"
      },
      "description": {
        "type": "string",
        "maxLength": 1000,
        "description": "Detailed description of the task (optional)"
      },
      "priority": {
        "type": "integer",
        "minimum": 1,
        "maximum": 5,
        "description": "Priority level (1-5, optional)"
      }
    },
    "required": ["title"]
  }
}
```

#### Response Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
        "task_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "completed": {"type": "boolean"},
        "priority": {"type": "integer"},
        "created_at": {"type": "string", "format": "date-time"}
      },
      "required": ["task_id", "title", "completed", "created_at"]
    },
    "error": {
      "type": "object",
      "properties": {
        "type": {"type": "string"},
        "message": {"type": "string"},
        "code": {"type": "string"}
      },
      "required": ["type", "message", "code"]
    }
  },
  "oneOf": [
    {"required": ["success", "data"]},
    {"required": ["success", "error"]}
  ]
}
```

#### Success Response (HTTP 200)
```json
{
  "success": true,
  "data": {
    "task_id": "uuid-string-here",
    "title": "Buy groceries",
    "description": "Milk, bread, eggs, fruits",
    "completed": false,
    "priority": 3,
    "created_at": "2026-01-25T10:30:00Z"
  }
}
```

#### Error Responses
- `ValidationError` (HTTP 400): Invalid input parameters
- `AuthenticationError` (HTTP 401): Invalid or expired JWT
- `AuthorizationError` (HTTP 403): Attempting to act on behalf of another user

---

### list_tasks

#### Request Schema
```json
{
  "name": "list_tasks",
  "arguments": {
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

#### Response Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
        "tasks": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {"type": "string"},
              "title": {"type": "string"},
              "description": {"type": "string"},
              "completed": {"type": "boolean"},
              "priority": {"type": "integer"},
              "created_at": {"type": "string", "format": "date-time"},
              "updated_at": {"type": "string", "format": "date-time"}
            },
            "required": ["id", "title", "completed", "created_at", "updated_at"]
          }
        }
      },
      "required": ["tasks"]
    },
    "error": {
      "type": "object",
      "properties": {
        "type": {"type": "string"},
        "message": {"type": "string"},
        "code": {"type": "string"}
      },
      "required": ["type", "message", "code"]
    }
  },
  "oneOf": [
    {"required": ["success", "data"]},
    {"required": ["success", "error"]}
  ]
}
```

#### Success Response (HTTP 200)
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "task-uuid-1",
        "title": "Buy groceries",
        "description": "Milk, bread, eggs, fruits",
        "completed": false,
        "priority": 3,
        "created_at": "2026-01-25T10:00:00Z",
        "updated_at": "2026-01-25T10:00:00Z"
      },
      {
        "id": "task-uuid-2",
        "title": "Walk the dog",
        "completed": true,
        "priority": 2,
        "created_at": "2026-01-25T09:00:00Z",
        "updated_at": "2026-01-25T09:30:00Z"
      }
    ]
  }
}
```

#### Error Responses
- `AuthenticationError` (HTTP 401): Invalid or expired JWT
- `AuthorizationError` (HTTP 403): Attempting to access another user's tasks

---

### complete_task

#### Request Schema
```json
{
  "name": "complete_task",
  "arguments": {
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

#### Response Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
        "task_id": {"type": "string"},
        "completed": {"type": "boolean"},
        "updated_at": {"type": "string", "format": "date-time"}
      },
      "required": ["task_id", "completed", "updated_at"]
    },
    "error": {
      "type": "object",
      "properties": {
        "type": {"type": "string"},
        "message": {"type": "string"},
        "code": {"type": "string"}
      },
      "required": ["type", "message", "code"]
    }
  },
  "oneOf": [
    {"required": ["success", "data"]},
    {"required": ["success", "error"]}
  ]
}
```

#### Success Response (HTTP 200)
```json
{
  "success": true,
  "data": {
    "task_id": "task-uuid-here",
    "completed": true,
    "updated_at": "2026-01-25T11:00:00Z"
  }
}
```

#### Error Responses
- `ValidationError` (HTTP 400): Invalid task_id format
- `NotFoundError` (HTTP 404): Task does not exist
- `AuthenticationError` (HTTP 401): Invalid or expired JWT
- `AuthorizationError` (HTTP 403): Attempting to complete another user's task

---

### delete_task

#### Request Schema
```json
{
  "name": "delete_task",
  "arguments": {
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

#### Response Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
        "deleted": {"type": "boolean"},
        "task_id": {"type": "string"}
      },
      "required": ["deleted", "task_id"]
    },
    "error": {
      "type": "object",
      "properties": {
        "type": {"type": "string"},
        "message": {"type": "string"},
        "code": {"type": "string"}
      },
      "required": ["type", "message", "code"]
    }
  },
  "oneOf": [
    {"required": ["success", "data"]},
    {"required": ["success", "error"]}
  ]
}
```

#### Success Response (HTTP 200)
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "task_id": "task-uuid-here"
  }
}
```

#### Error Responses
- `ValidationError` (HTTP 400): Invalid task_id format
- `NotFoundError` (HTTP 404): Task does not exist
- `AuthenticationError` (HTTP 401): Invalid or expired JWT
- `AuthorizationError` (HTTP 403): Attempting to delete another user's task

---

### update_task

#### Request Schema
```json
{
  "name": "update_task",
  "arguments": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "ID of the task to update (required)"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "New title for the task (optional)"
      },
      "description": {
        "type": "string",
        "maxLength": 1000,
        "description": "New description for the task (optional)"
      },
      "priority": {
        "type": "integer",
        "minimum": 1,
        "maximum": 5,
        "description": "New priority level (1-5, optional)"
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

#### Response Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
        "task_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "completed": {"type": "boolean"},
        "priority": {"type": "integer"},
        "updated_at": {"type": "string", "format": "date-time"}
      },
      "required": ["task_id", "title", "completed", "updated_at"]
    },
    "error": {
      "type": "object",
      "properties": {
        "type": {"type": "string"},
        "message": {"type": "string"},
        "code": {"type": "string"}
      },
      "required": ["type", "message", "code"]
    }
  },
  "oneOf": [
    {"required": ["success", "data"]},
    {"required": ["success", "error"]}
  ]
}
```

#### Success Response (HTTP 200)
```json
{
  "success": true,
  "data": {
    "task_id": "task-uuid-here",
    "title": "Updated task title",
    "description": "Updated description",
    "completed": false,
    "priority": 4,
    "updated_at": "2026-01-25T11:30:00Z"
  }
}
```

#### Error Responses
- `ValidationError` (HTTP 400): Invalid input parameters
- `NotFoundError` (HTTP 404): Task does not exist
- `AuthenticationError` (HTTP 401): Invalid or expired JWT
- `AuthorizationError` (HTTP 403): Attempting to update another user's task

## Common Error Codes

| Error Type | HTTP Code | Description |
|------------|-----------|-------------|
| `AuthenticationError` | 401 | Invalid or expired JWT token |
| `AuthorizationError` | 403 | Attempting to access another user's data |
| `ValidationError` | 400 | Invalid input parameters |
| `NotFoundError` | 404 | Requested resource doesn't exist |
| `InternalError` | 500 | Server-side processing error |

## Performance Requirements
- All MCP tools must respond within 2 seconds under normal load conditions
- The system should maintain 99% availability for tool requests
- Database operations should complete within 500ms for optimal performance