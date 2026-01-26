# API Contract: Chat Interface for Todo AI Chatbot

## Overview
This document defines the API contract between the ChatKit frontend and the backend chat endpoint for todo management functionality.

## Endpoint: POST /api/{user_id}/chat

### Description
Endpoint for sending user messages to the AI assistant for processing and todo management operations.

### Request Parameters
- **Path Parameter**:
  - `user_id` (string, required): The unique identifier of the authenticated user

### Request Headers
- `Authorization` (string, required): Bearer token for authentication (format: "Bearer {jwt_token}")
- `Content-Type` (string, required): "application/json"

### Request Body
```json
{
  "message": "string (required)",
  "sessionId": "string (optional)",
  "timestamp": "ISO 8601 datetime string (optional)"
}
```

#### Request Body Fields
- `message`: The user's input message for the AI assistant (max 2000 characters)
- `sessionId`: Optional session identifier for maintaining conversation context
- `timestamp`: Optional timestamp for the message (defaults to current time if not provided)

### Response Format
**Success Response (200 OK)**:
```json
{
  "response": "string",
  "toolCallResults": [
    {
      "toolName": "string",
      "result": "object",
      "status": "string"
    }
  ],
  "conversationHistory": [
    {
      "id": "string",
      "content": "string",
      "sender": "USER|ASSISTANT",
      "timestamp": "ISO 8601 datetime string",
      "status": "SENT|DELIVERED|FAILED|PROCESSING"
    }
  ],
  "sessionId": "string",
  "timestamp": "ISO 8601 datetime string"
}
```

**Error Responses**:
- **400 Bad Request**: Invalid request body or parameters
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: User attempting to access another user's data
- **429 Too Many Requests**: Rate limiting exceeded
- **500 Internal Server Error**: Server-side error occurred

### Response Fields
- `response`: The AI assistant's response to the user's message
- `toolCallResults`: Array of results from any tools called by the AI
- `conversationHistory`: Updated conversation history including the new messages
- `sessionId`: The session identifier for maintaining context
- `timestamp`: When the response was generated

## Validation Rules
- Message length must not exceed 2000 characters
- User ID in URL must match the authenticated user ID in the JWT
- Session ID (if provided) must be valid for the user
- All requests must include a valid JWT token

## Authentication
All requests must include a valid JWT token in the Authorization header. The token must correspond to the user ID in the URL path to satisfy the multi-tenant isolation requirement.

## Rate Limiting
Requests may be rate-limited to prevent abuse. Clients should implement exponential backoff for retry logic when receiving 429 responses.

## Error Handling
In case of server errors, clients should implement retry logic with exponential backoff. For client errors (4xx), the client should not retry automatically but should inform the user of the issue.