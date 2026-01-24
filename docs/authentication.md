# Authentication System Documentation

## Overview
This document describes the JWT-based authentication and authorization system implemented for the Todo AI Chatbot application. The system ensures every request is properly authenticated, enforces strict multi-tenant data isolation, and maintains stateless operation across all components.

## Architecture

### Components
1. **JWT Utilities** (`backend/src/utils/jwt.py`): Handles token creation, validation, and inspection
2. **Authentication Configuration** (`backend/src/config/auth.py`): Defines authentication settings
3. **Authentication Dependencies** (`backend/src/dependencies/auth.py`): FastAPI dependencies for extracting current user
4. **Authentication Services** (`backend/src/services/auth_service.py`): Business logic for authentication operations
5. **Authentication Exceptions** (`backend/src/exceptions/auth.py`): Custom authentication-related exceptions
6. **Middleware** (`backend/src/middleware/chat_auth.py`, `backend/src/middleware/mcp_auth.py`): Specialized authentication middleware

## JWT Token Structure

The system uses JWT tokens with the following claims:
- `user_id`: Unique identifier for the authenticated user
- `email`: User's email address
- `exp`: Expiration timestamp
- `iat`: Issue timestamp
- `iss`: Token issuer ("better-auth")
- `aud`: Token audience ("todo-app")

## Multi-Tenant Data Isolation

The system enforces strict multi-tenant data isolation by:
1. Including `user_id` as a foreign key in all data models
2. Validating that the `user_id` in the JWT token matches the `user_id` in the URL path parameter
3. Filtering all database queries by the authenticated user's `user_id`

### Example Validation Pattern
```python
# In all API endpoints
if current_user.user_id != user_id_from_path:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: Cannot access another user's data"
    )
```

## Error Handling

The system differentiates between authentication and authorization errors:
- **HTTP 401 Unauthorized**: Used for invalid/missing/expired tokens
- **HTTP 403 Forbidden**: Used when user is authenticated but lacks permission (cross-user access attempts)
- **HTTP 404 Not Found**: Used for non-existent resources (even if user tries to access other users' data)

## Chat API Authentication

The Chat API endpoints follow the same authentication pattern:
- `POST /api/{user_id}/chat`: Send a chat message
- `GET /api/{user_id}/chat/history`: Get chat history
- `DELETE /api/{user_id}/chat/conversation/{conversation_id}`: Delete a conversation

## MCP Tool Authentication

MCP tools must validate user ownership of resources and enforce authentication:
- Tools are registered per user
- Resource access is validated against ownership
- All operations require valid authentication

## Frontend Integration

The frontend includes:
- Authentication context (`frontend/contexts/auth-context.tsx`) for managing user state
- Authentication service (`frontend/services/auth-service.ts`) for API calls
- Chat service (`frontend/services/chat-service.ts`) for secured chat API interaction
- Chat component (`frontend/components/chat-component.tsx`) with authentication context

## Security Features

1. **Stateless Authentication**: Pure JWT approach with no server-side session storage
2. **Token Expiration**: Automatic token expiry after 24 hours (configurable)
3. **Signature Validation**: Each request validates JWT signature and claims
4. **Rate Limiting**: Protection against authentication endpoint abuse
5. **Audit Logging**: Logging of authentication events and security violations

## Environment Variables

Required environment variables:
```bash
# Authentication
BETTER_AUTH_SECRET="your-secure-jwt-secret-here-minimum-32-chars"
BETTER_AUTH_URL="http://localhost:8000"  # Your backend URL
```

## Testing

The system includes comprehensive tests:
- Unit tests for authentication components
- Integration tests for multi-tenant isolation
- Contract tests for API endpoint validation
- Security-focused tests for access control

## Best Practices

1. Use strong, randomly generated JWT secrets (minimum 32 characters)
2. Always validate user_id in URL matches JWT token
3. Filter all database queries by user_id
4. Use consistent error messages
5. Log security events without exposing sensitive information
6. Don't reveal whether resources exist when access is denied