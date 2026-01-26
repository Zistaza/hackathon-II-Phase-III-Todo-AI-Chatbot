# Data Model: Todo AI Chatbot Frontend - ChatKit Interface

## Core Entities

### Chat Message
**Description**: Represents a communication unit between user and AI assistant
- **id**: Unique identifier for the message
- **content**: Text content of the message
- **sender**: Enum (USER | ASSISTANT)
- **timestamp**: ISO datetime of message creation
- **status**: Enum (SENT | DELIVERED | FAILED | PROCESSING)
- **metadata**: Optional additional data (tool call results, error details)

**Validation Rules**:
- content: Required, maximum 2000 characters
- sender: Required, must be either USER or ASSISTANT
- timestamp: Required, must be valid ISO date
- status: Required, default to SENT

### Conversation Session
**Description**: Represents a single interaction thread between user and AI
- **sessionId**: Unique identifier for the session
- **userId**: Associated user identifier
- **messages**: Array of ChatMessage objects
- **createdAt**: Timestamp when session started
- **updatedAt**: Timestamp of last activity
- **isActive**: Boolean indicating if session is currently active

**Validation Rules**:
- sessionId: Required, unique
- userId: Required, must match authenticated user
- messages: Required, minimum 0 items
- createdAt: Required, must be valid ISO date
- updatedAt: Required, must be valid ISO date

### Todo Action
**Description**: Represents a user intent to perform a todo management operation
- **actionType**: Enum (CREATE | UPDATE | DELETE | LIST | COMPLETE)
- **parameters**: Object containing action-specific parameters
- **result**: Result of the action execution
- **timestamp**: When the action was processed

**Validation Rules**:
- actionType: Required, must be valid enum value
- parameters: Required, object format varies by actionType
- result: Optional, depends on action execution

## UI State Models

### Input Validation State
**Description**: Tracks validation status of user input
- **isValid**: Boolean indicating if input passes validation
- **errors**: Array of validation error messages
- **warnings**: Array of warning messages
- **sanitizedValue**: Cleaned version of user input

### Error State
**Description**: Manages error display and recovery
- **hasError**: Boolean indicating if an error occurred
- **errorMessage**: User-friendly error message
- **errorType**: Enum (NETWORK | VALIDATION | SERVER | AUTHENTICATION)
- **canRetry**: Boolean indicating if retry is possible
- **retryAction**: Function to execute for retry

## API Communication Models

### Chat Request
**Description**: Structure for sending messages to the backend
- **message**: String content of the user's message
- **userId**: Identifier of the sending user
- **sessionId**: Current session identifier
- **timestamp**: When the request was created

**Validation Rules**:
- message: Required, non-empty, maximum 2000 characters
- userId: Required, must match authenticated user
- sessionId: Required, must be valid session

### Chat Response
**Description**: Structure for responses from the backend
- **response**: String content of the AI's response
- **toolCallResults**: Array of results from executed tools
- **conversationHistory**: Updated conversation history
- **sessionId**: Session identifier
- **timestamp**: When the response was generated

**Validation Rules**:
- response: Required, non-empty
- toolCallResults: Optional, array of tool results
- conversationHistory: Required, array of messages
- sessionId: Required, must match original session