# API Contract: Todo AI Chatbot - Chat API

## Endpoint

```
POST /api/{user_id}/chat
```

## Authentication

- JWT Bearer token required in Authorization header
- User ID in path must match JWT subject
- Returns 401 for invalid/missing tokens
- Returns 403 if user ID doesn't match JWT subject

## Request

### Path Parameters

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| user_id   | string | Yes      | ID of the authenticated user |

### Headers

| Header          | Value                | Required | Description |
|-----------------|----------------------|----------|-------------|
| Authorization   | Bearer {jwt_token}   | Yes      | JWT authentication token |
| Content-Type    | application/json     | Yes      | Request body format |

### Body

| Field           | Type    | Required | Description |
|-----------------|---------|----------|-------------|
| message         | string  | Yes      | Natural language user input |
| conversation_id | integer | No       | Existing conversation reference |

## Response

### Success Response (200 OK)

```json
{
  "conversation_id": 123,
  "response": "Natural language response from AI assistant",
  "tool_calls": [
    {
      "tool_name": "string",
      "input": {},
      "output": {},
      "status": "success|error"
    }
  ]
}
```

### Error Responses

#### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing JWT token"
}
```

#### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "User ID does not match authenticated user"
}
```

#### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Conversation ID does not exist for user"
}
```

#### 422 Unprocessable Entity
```json
{
  "error": "Unprocessable Entity",
  "message": "Invalid request payload",
  "details": {}
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

## Behavior

### 12-Step Stateless Request Cycle

1. Authenticate request via JWT
2. Validate user_id matches JWT subject
3. Load conversation history from database (if conversation_id exists)
4. Append current user message to history
5. Persist user message before agent execution
6. Run OpenAI Agent with reconstructed message history and MCP tool definitions
7. Capture any MCP tool calls made by the agent
8. Persist tool calls and tool responses
9. Generate final assistant response
10. Persist assistant response
11. Return response payload to client
12. Discard all in-memory state

## Data Persistence

- All user messages stored in Message table
- All assistant responses stored in Message table
- All tool calls stored in ToolCall table
- Conversation metadata stored in Conversation table
- All data linked to authenticated user

## Validation

- JWT token validity checked on every request
- User ID in path validated against JWT subject
- Conversation ID validated against user ownership
- Request body validated for required fields
- Tool call results validated before persistence

## Performance Requirements

- 95% of requests complete within 5 seconds under normal load
- Stateless operation to support horizontal scaling
- No server-side caching or session storage