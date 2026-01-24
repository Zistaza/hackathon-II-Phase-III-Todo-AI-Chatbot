# Quickstart Guide: Phase III Authentication (Better Auth + JWT) for Todo AI Chatbot

## Overview
This guide explains how to implement and use the JWT-based authentication system with Better Auth for the Todo AI Chatbot application. The system ensures secure, stateless authentication with strict multi-tenant data isolation.

## Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Better Auth configured with JWT plugin
- Neon Serverless PostgreSQL database
- Environment variables configured for authentication

## Environment Setup

### Backend Configuration
```bash
# Required environment variables for JWT authentication
export BETTER_AUTH_SECRET="your-secure-jwt-secret-here-minimum-32-chars"
export BETTER_AUTH_URL="http://localhost:8000"  # Your backend URL
export DATABASE_URL="postgresql://..."  # Neon PostgreSQL connection string
```

### JWT Configuration
The system uses the following JWT settings:
- Algorithm: HS256
- Expiration: 24 hours (configurable)
- Audience: "todo-app"
- Issuer: "better-auth"

## Implementation Steps

### 1. JWT Token Generation
Better Auth automatically generates JWT tokens upon successful authentication. The tokens contain:
- `user_id`: Unique identifier for the authenticated user
- `email`: User's email address
- Standard claims: `exp`, `iat`, `iss`, `aud`

### 2. Protecting API Endpoints
All endpoints must validate JWT tokens using the authentication dependency:

```python
from backend.src.dependencies.auth import get_current_user
from backend.src.models.auth import CurrentUser

@app.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    # Verify user_id in URL matches JWT token
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Process authenticated request
    return {"message": "Authenticated successfully"}
```

### 3. Database Query Filtering
Always filter database queries by the authenticated user's ID:

```python
from sqlmodel import select
from backend.src.models.task import Task

# Secure query - only returns user's own tasks
statement = select(Task).where(Task.user_id == current_user.user_id)
user_tasks = session.exec(statement).all()
```

### 4. Error Handling
Implement proper error responses:

- **HTTP 401 Unauthorized**: For invalid/missing/expired tokens
- **HTTP 403 Forbidden**: For cross-user access attempts
- **HTTP 404 Not Found**: For non-existent resources (even if user tries to access other users' data)

## Testing Authentication

### Valid Token Test
```bash
curl -X GET \
  http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer YOUR_VALID_JWT_TOKEN"
```

### Invalid Token Test
```bash
curl -X GET \
  http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer INVALID_TOKEN"
# Expected: HTTP 401 Unauthorized
```

### Cross-User Access Test
```bash
curl -X GET \
  http://localhost:8000/api/user456/tasks \
  -H "Authorization: Bearer TOKEN_FOR_user123"
# Expected: HTTP 403 Forbidden
```

## Integration with AI Chatbot

### Chat API Authentication
The chat API endpoint follows the same authentication pattern:

```python
@app.post("/api/{user_id}/chat")
async def send_chat_message(
    user_id: str,
    message: ChatMessage,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify user identity
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Process message with AI agent using authenticated context
    ai_response = await process_with_ai_agent(
        current_user.user_id,
        message.content
    )

    return {"response": ai_response}
```

### MCP Tool Integration
MCP tools must validate JWT tokens before executing operations:

```python
def validate_mcp_access(jwt_token: str, resource_owner_id: str) -> bool:
    current_user = verify_token(jwt_token)
    if not current_user:
        return False

    # Ensure user owns the resource
    return current_user.user_id == resource_owner_id
```

## Security Best Practices

### 1. Token Security
- Use strong, randomly generated JWT secrets (minimum 32 characters)
- Rotate secrets periodically
- Never log JWT tokens
- Use HTTPS in production

### 2. Multi-Tenant Isolation
- Always validate user_id in URL matches JWT token
- Filter all database queries by user_id
- Never return data from other users

### 3. Error Handling
- Don't reveal whether resources exist when access is denied
- Use consistent error messages
- Log security events without exposing sensitive information

## Troubleshooting

### Common Issues
1. **401 Errors**: Check JWT token format and expiration
2. **403 Errors**: Verify user_id in URL matches JWT token
3. **Database Access**: Ensure all queries filter by current_user.user_id

### Debugging Authentication
Enable debug logging to trace authentication flow:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps
1. Implement refresh token functionality (optional)
2. Add rate limiting to authentication endpoints
3. Set up monitoring for authentication failures
4. Configure production security headers