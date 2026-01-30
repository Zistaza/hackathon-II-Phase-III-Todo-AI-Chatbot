---
name: authentication-iii
description: Handle secure authentication and authorization for Phase-III Todo AI Chatbot, including JWT generation/validation, multi-tenant isolation, and Better Auth integration.
---

# Auth Skill (Phase III)

## Instructions

1. **JWT authentication**
   - Generate JWT tokens with user_id and expiry claims
   - Validate tokens for all protected API routes
   - Return structured payload including token and metadata
   - Reject requests without valid tokens (HTTP 401)

2. **User identity verification**
   - Verify that user_id in request matches authenticated JWT
   - Enforce multi-tenant isolation so users can only access their own data
   - Handle invalid or mismatched user identity gracefully

3. **Stateless authentication**
   - Do not store session state on the server
   - Persist authentication state entirely via tokens
   - Ensure compatibility with stateless MCP server design

4. **Better Auth integration**
   - Use BETTER_AUTH_SECRET environment variable for secure API calls
   - Integrate with Better Auth API for external authentication
   - Handle signup/signin and verification responses cleanly

5. **Secure API endpoint protection**
   - Wrap endpoints with authentication middleware
   - Ensure all requests are verified before calling MCP tools
   - Log unauthorized access attempts for auditing

## Best Practices
- Never store plain-text passwords
- Validate JWT tokens for every request
- Ensure multi-tenant data isolation
- Keep authentication logic stateless
- Use environment variables for secrets and API keys
- Handle errors gracefully and return consistent responses

## Example Structure
```python
class AuthSkill:
    def generate_jwt(self, user_id: str) -> str:
        # Create JWT token with user_id and expiry
        pass

    def validate_jwt(self, token: str) -> dict:
        # Validate JWT and return decoded payload
        pass

    def verify_user_identity(self, user_id: str, token_payload: dict) -> bool:
        # Ensure user_id matches JWT payload
        pass

    def better_auth_signup(self, email: str):
        # Integrate with Better Auth API signup
        pass

    def better_auth_signin(self, email: str):
        # Integrate with Better Auth API signin
        pass

    def auth_middleware(self, request):
        # Middleware to enforce authentication and multi-tenant isolation
        pass
