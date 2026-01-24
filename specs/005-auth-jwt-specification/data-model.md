# Data Model: Phase III Authentication (Better Auth + JWT) for Todo AI Chatbot

## JWT Token Entity

### Fields
- **token**: String - The JWT token string
- **user_id**: String - Unique identifier for the authenticated user
- **email**: String - User's email address
- **exp**: Integer - Unix timestamp when the token expires
- **iat**: Integer - Unix timestamp when the token was issued
- **iss**: String - Token issuer (default: "better-auth")
- **aud**: String - Token audience (default: "todo-app")
- **sub**: String - Subject identifier (optional, user_id)

### Relationships
- Links to User entity via user_id

### Validation Rules
- Token must be properly formatted JWT
- Signature must be valid using BETTER_AUTH_SECRET
- Expiration time must be in the future
- Audience must equal "todo-app"
- Required claims: user_id, email

## User Identity Entity

### Fields
- **user_id**: String - Unique identifier for the user
- **email**: String - User's email address
- **name**: String - User's display name (optional)

### Relationships
- Associated with multiple JWT tokens (historical)
- Associated with multiple tasks (via foreign key)

### Validation Rules
- user_id must be unique
- email must be valid email format
- user_id in JWT must match user_id in API path

## Authenticated Request Entity

### Fields
- **request_id**: String - Unique identifier for the request
- **user_id**: String - User making the request
- **endpoint**: String - API endpoint accessed
- **timestamp**: DateTime - When the request was made
- **jwt_token**: String - The JWT token used for authentication
- **status**: Enum - Authentication status (SUCCESS, FAILURE)

### Relationships
- Belongs to User Identity
- Associated with specific API endpoint

### Validation Rules
- JWT token must be valid and unexpired
- user_id in JWT must match user_id in endpoint path
- Request must include Authorization header

## State Transition: JWT Token Lifecycle

### States
1. **ISSUED** - Token created and signed
2. **VALID** - Token is currently valid for use
3. **EXPIRED** - Token has exceeded its expiration time
4. **REVOKED** - Token has been invalidated (future feature)

### Transitions
- ISSUED → VALID (automatically upon creation)
- VALID → EXPIRED (upon reaching expiration time)
- VALID → REVOKED (upon explicit revocation - future feature)
- EXPIRED → INVALID (token becomes unusable)

## API Request Flow Data Model

### Fields
- **request_method**: String - HTTP method (GET, POST, PUT, DELETE, PATCH)
- **request_path**: String - API endpoint path with user_id parameter
- **auth_header**: String - Authorization header containing JWT
- **user_id_from_token**: String - Extracted from JWT
- **user_id_from_path**: String - Extracted from URL path
- **validation_result**: Boolean - Whether user_ids match
- **response_status**: Integer - HTTP status code returned

### Validation Rules
- user_id_from_token must equal user_id_from_path for successful authentication
- Invalid tokens return HTTP 401
- Mismatched user_ids return HTTP 403
- Valid requests return appropriate success status codes

## MCP Tool Access Entity

### Fields
- **tool_id**: String - Identifier for the MCP tool
- **user_id**: String - User requesting tool access
- **jwt_token**: String - Token used for authentication
- **resource_id**: String - ID of resource being accessed
- **resource_owner_id**: String - Owner of the accessed resource
- **access_granted**: Boolean - Whether access was permitted

### Validation Rules
- user_id must match resource_owner_id for access to be granted
- Invalid JWT tokens result in access denial
- Proper error responses must be returned for unauthorized access