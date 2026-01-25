# API Contract: Todo AI Chatbot Agent

## Overview
This contract defines the API endpoints and interactions for the Todo AI Chatbot Agent that processes natural language requests and orchestrates MCP tools.

## Base URL
`POST /api/{user_id}/chat`

## Authentication
- JWT Bearer token required in Authorization header
- User ID in URL path must match user ID in JWT token (multi-tenant isolation)
- Returns 401 Unauthorized for invalid/missing tokens

## Request Format

### Headers
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

### Body Schema
```json
{
  "message": "string",
  "conversation_id": "string (optional)",
  "timestamp": "ISO 8601 datetime (optional)"
}
```

#### Field Definitions
- `message`: (Required) The natural language message from the user
- `conversation_id`: (Optional) Identifier for continuing an existing conversation; if omitted, starts a new conversation
- `timestamp`: (Optional) Client-provided timestamp; if omitted, server timestamp is used

## Response Format

### Success Response (200 OK)
```json
{
  "conversation_id": "string",
  "response": "string",
  "tool_calls": [
    {
      "id": "string",
      "name": "string",
      "arguments": {},
      "status": "string",
      "result": {}
    }
  ],
  "next_action": "string",
  "timestamp": "ISO 8601 datetime"
}
```

#### Success Response Field Definitions
- `conversation_id`: Unique identifier for the conversation thread
- `response`: Natural language response to the user
- `tool_calls`: Array of MCP tool calls made during processing
  - `id`: Unique identifier for the tool call
  - `name`: Name of the MCP tool (add_task, list_tasks, complete_task, delete_task, update_task)
  - `arguments`: Arguments passed to the tool
  - `status`: Status of the tool call (success, error)
  - `result`: Result returned by the tool
- `next_action`: Indicates if further user input is required (continue, await_confirmation, completed)
- `timestamp`: Server timestamp of response generation

### Error Responses

#### 400 Bad Request
```json
{
  "error": "string",
  "message": "string",
  "code": "INVALID_INPUT"
}
```

#### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing authentication token",
  "code": "AUTH_REQUIRED"
}
```

#### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "User ID in token does not match user ID in URL",
  "code": "FORBIDDEN_ACCESS"
}
```

#### 422 Unprocessable Entity
```json
{
  "error": "Validation Error",
  "message": "string",
  "code": "VALIDATION_ERROR",
  "details": []
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred",
  "code": "INTERNAL_ERROR"
}
```

## MCP Tool Contracts

The agent orchestrates these MCP tools:

### add_task
- **Intent**: Create a new task
- **Triggered by**: "add", "create", "remember", "write down"
- **Arguments**:
  ```json
  {
    "title": "string (required)",
    "description": "string (optional)",
    "due_date": "ISO 8601 datetime (optional)"
  }
  ```
- **Expected Result**:
  ```json
  {
    "task_id": "string",
    "title": "string",
    "status": "pending"
  }
  ```

### list_tasks
- **Intent**: Retrieve existing tasks
- **Triggered by**: "see", "show", "list", "check", "view"
- **Arguments**:
  ```json
  {
    "status_filter": "string (optional: all, pending, completed)",
    "sort_order": "string (optional: asc, desc)",
    "limit": "integer (optional)"
  }
  ```
- **Expected Result**:
  ```json
  {
    "tasks": [
      {
        "id": "string",
        "title": "string",
        "description": "string",
        "status": "string",
        "created_at": "ISO 8601 datetime",
        "updated_at": "ISO 8601 datetime"
      }
    ]
  }
  ```

### complete_task
- **Intent**: Mark a task as completed
- **Triggered by**: "done", "complete", "finish"
- **Arguments**:
  ```json
  {
    "task_id": "string (required)"
  }
  ```
- **Expected Result**:
  ```json
  {
    "task_id": "string",
    "status": "completed",
    "completed_at": "ISO 8601 datetime"
  }
  ```

### delete_task
- **Intent**: Remove a task
- **Triggered by**: "delete", "remove", "cancel"
- **Arguments**:
  ```json
  {
    "task_id": "string (required)"
  }
  ```
- **Expected Result**:
  ```json
  {
    "task_id": "string",
    "deleted": true
  }
  ```

### update_task
- **Intent**: Modify an existing task
- **Triggered by**: "change", "update", "rename", "edit"
- **Arguments**:
  ```json
  {
    "task_id": "string (required)",
    "title": "string (optional)",
    "description": "string (optional)",
    "due_date": "ISO 8601 datetime (optional)",
    "status": "string (optional)"
  }
  ```
- **Expected Result**:
  ```json
  {
    "task_id": "string",
    "title": "string",
    "description": "string",
    "status": "string",
    "updated_at": "ISO 8601 datetime"
  }
  ```

## Business Rules

### Multi-Tenant Isolation
- All MCP tools must filter data by the authenticated user's ID
- User ID in JWT must match user ID in URL path
- Users cannot access or modify other users' tasks

### Stateless Operation
- Each request must contain full conversation context
- Agent maintains no in-memory state between requests
- Conversation history is reconstructed from database for each request

### Safety Constraints
- Destructive operations (delete, update) require confirmation when ambiguity exists
- Agent must validate user intent before executing operations
- Error responses must be informative but not expose system details

## Error Handling

### Client Errors (4xx)
- 400: Malformed request or invalid message content
- 401: Missing or invalid authentication token
- 403: User ID mismatch between token and URL
- 422: Request validation failed

### Server Errors (5xx)
- 500: Unexpected internal error during processing
- 502: Error communicating with MCP tools
- 503: MCP tools temporarily unavailable

## Rate Limiting
- Requests limited to prevent abuse
- Per-user rate limits applied
- Excessive requests result in 429 Too Many Requests response