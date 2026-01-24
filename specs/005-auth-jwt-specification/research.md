# Research Findings: Phase III Authentication (Better Auth + JWT) for Todo AI Chatbot

## Decision: JWT Claim Design and Payload Structure

### Rationale
Based on the current implementation in `/backend/src/utils/jwt.py`, the JWT payload structure follows security best practices with minimal user information. The current design includes standard claims (`exp`, `iat`, `iss`, `aud`) and custom claims (`user_id`, `email`). This approach balances functionality with security by minimizing token size and information exposure.

### Current Implementation
```python
class JWTData(BaseModel):
    user_id: str
    email: str
    exp: Optional[int] = None
    iat: Optional[int] = None
    iss: Optional[str] = "better-auth"
    aud: Optional[str] = "todo-app"
```

### Alternatives Considered
1. **Extended Claims**: Adding more user information like `name`, `role`, `permissions` - rejected due to increased token size and security risks
2. **Minimal Claims**: Only `user_id` - rejected as email provides useful secondary identification
3. **Standard `sub` Claim**: Adding `sub` as standard subject identifier - considered but not implemented in current version

## Decision: Error Handling Approaches (HTTP 401 vs 403)

### Rationale
The system correctly differentiates between authentication failures (401) and authorization failures (403). This follows REST API best practices and provides clear feedback to clients about the nature of the error.

### Current Implementation
- **HTTP 401 Unauthorized**: Used for invalid/missing/expired tokens
- **HTTP 403 Forbidden**: Used when user is authenticated but lacks permission (cross-user access attempts)

### Alternatives Considered
1. **Unified 401 Response**: Using 401 for all authentication/authorization failures - rejected as it obscures the specific issue
2. **More Granular Codes**: Different codes for different error types - rejected as it overcomplicated the API contract

## Decision: Multi-Tenant Query Filtering Methods

### Rationale
The system implements robust multi-tenant isolation through database WHERE clauses that filter by `user_id`. This ensures users can only access their own data and prevents cross-user data access.

### Current Implementation
- **Database Queries**: All queries include `WHERE Task.user_id == current_user.user_id`
- **URL Parameter Validation**: Verifies URL `user_id` matches JWT `user_id`
- **Dual Verification**: Both API path and database query validate user ownership

### Alternatives Considered
1. **Application-Level Filtering**: Filtering after database retrieval - rejected as it's less efficient and potentially insecure
2. **Row-Level Security**: Database-level security policies - considered overkill for current scale
3. **ORM Hooks**: Automatic filtering through ORM middleware - rejected as it obscures query logic

## Decision: Stateless Session Management Strategy

### Rationale
The system implements a pure JWT-only approach, which aligns with the statelessness requirement in the constitution. This provides scalability and simplifies infrastructure while maintaining security.

### Current Implementation
- **Pure JWT**: No server-side session storage
- **Signature Validation**: Each request validates JWT signature and claims
- **Expiration Enforcement**: Automatic token expiry after 24 hours

### Alternatives Considered
1. **JWT + Redis Cache**: Caching active sessions for revocation - rejected as it violates statelessness principle
2. **Refresh Tokens**: Separate refresh token system - considered but deferred for simplicity
3. **Hybrid Approach**: Selective caching for security features only - considered for future enhancement

## Decision: Integration Points Between Chat API, AI Agents, and MCP Tools

### Rationale
The integration architecture extends the existing authentication system to new components while maintaining security and multi-tenant isolation. Each component must validate JWT tokens and enforce user data boundaries.

### Current Implementation
- **Authentication Middleware**: Applied to all protected endpoints
- **User Context Propagation**: Current user context passed to all services
- **Consistent Validation**: Same validation rules across all components

### Alternatives Considered
1. **Separate Authentication Systems**: Different auth for each component - rejected as it creates inconsistency
2. **Shared Session Tokens**: Passing session tokens between components - rejected as it complicates state management
3. **Service-to-Service Authentication**: Additional authentication layer between services - considered but deferred for initial implementation