# Research Summary: Todo AI Chatbot MCP Tools

## MCP SDK Standards Research

### Key Findings
- MCP (Model Context Protocol) tools follow a standardized schema format with clear input/output definitions
- Tools must include name, description, parameters (with types and validation), and return values
- Official MCP SDK requires tools to be stateless and follow REST-like patterns
- Tools should return structured responses with success/error indicators

### Best Practices Identified
- Use JSON Schema for parameter validation
- Include comprehensive error handling with specific error codes
- Provide clear examples for each tool's input/output
- Follow naming conventions consistent with existing tools

## JWT-based Multi-tenant Patterns Research

### Key Findings
- JWT tokens should contain user_id as a claim for multi-tenant isolation
- Middleware should validate JWT and extract user context before business logic
- All database queries must be filtered by user_id to prevent cross-tenant access
- Token expiration should be handled gracefully with clear error messages

### Security Guidelines
- Validate JWT signature using shared secret
- Verify token hasn't expired
- Confirm user_id in token matches expected context
- Use short-lived tokens (15-30 minutes) for enhanced security

## Stateless Backend Constraints Research

### Key Findings
- Statelessness achieved by storing all necessary data in database or client
- Conversation state maintained in database rather than server memory
- Each request contains all necessary context (via JWT) to process independently
- Caching strategies should be used carefully to maintain stateless nature

### Persistence Patterns
- Use database transactions for consistency
- Store conversation context with each message
- Implement proper cleanup for old conversations
- Cache frequently accessed data at CDN level when possible

## SQLModel + Neon DB Interactions Research

### Key Findings
- SQLModel provides excellent integration with FastAPI for type safety
- Neon Serverless PostgreSQL offers automatic scaling and connection pooling
- Use async database operations to improve performance
- Implement proper connection management to optimize Neon's serverless benefits

### Best Practices
- Define models with proper relationships and constraints
- Use foreign keys to enforce referential integrity
- Implement proper indexing for frequently queried fields
- Handle database errors gracefully with retry logic

## Agent Behavior Mapping Research

### Key Findings
- Natural language commands should be mapped to tools using pattern matching
- Confidence scoring helps determine best tool match
- Fallback mechanisms needed for unrecognized commands
- Command history can improve accuracy of future mappings

### Mapping Guidelines
- Define clear keywords for each tool type
- Use context from conversation history to improve accuracy
- Implement fuzzy matching for variations in user language
- Provide feedback loops to improve mapping over time

## Tool Schema Definitions

### Standard MCP Tool Schema
```json
{
  "name": "tool_name",
  "description": "Clear description of what the tool does",
  "input_schema": {
    "type": "object",
    "properties": {
      // Define input parameters here
    },
    "required": ["required_parameters"]
  }
}
```

### Example for add_task Tool
```json
{
  "name": "add_task",
  "description": "Add a new task to the user's todo list",
  "input_schema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Title of the task"
      },
      "description": {
        "type": "string",
        "description": "Detailed description of the task"
      }
    },
    "required": ["title"]
  }
}
```

## Error Handling Standards

### Common Error Types
- AuthenticationError: Invalid or expired JWT
- AuthorizationError: User attempting to access another user's data
- ValidationError: Invalid input parameters
- NotFoundError: Requested resource doesn't exist
- InternalError: Server-side processing errors

### Response Format
```json
{
  "success": boolean,
  "data": {...}, // Present on success
  "error": {     // Present on error
    "type": "error_type",
    "message": "Human-readable error message",
    "code": "error_code"
  }
}
```