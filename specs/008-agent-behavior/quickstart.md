# Quickstart Guide: Todo AI Chatbot Agent

## Overview
This guide provides setup instructions and basic usage for the Todo AI Chatbot Agent that interprets natural language commands and interacts with MCP tools to manage user tasks.

## Prerequisites
- Python 3.11+
- OpenAI API key
- Running MCP tools server
- JWT authentication configured
- Neon Serverless PostgreSQL database

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hackathon-II-phase-III-todo-ai-chatbot
```

### 2. Install Dependencies
```bash
pip install openai fastapi uvicorn sqlmodel python-multipart better-auth
```

### 3. Configure Environment Variables
Create a `.env` file with the following:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql+asyncpg://username:password@localhost/dbname
BETTER_AUTH_SECRET=your_jwt_secret_here
MCP_SERVER_URL=http://localhost:8000  # URL to MCP tools server
```

## Basic Usage

### 1. Start the Agent Service
```bash
uvicorn backend.src.api.chat_router:app --reload --port 8001
```

### 2. Send a Chat Request
```bash
curl -X POST "http://localhost:8001/api/{user_id}/chat" \
  -H "Authorization: Bearer {valid_jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

## Key Features

### Intent Recognition
The agent recognizes these primary intents:
- **Task Creation**: "Add a task to...", "Create a task for...", "Remember to..."
- **Task Listing**: "Show my tasks", "List all tasks", "What do I need to do?"
- **Task Completion**: "Mark task as done", "Complete the meeting task", "Finish shopping"
- **Task Deletion**: "Delete the reminder", "Remove the appointment", "Cancel task"
- **Task Update**: "Change the deadline", "Update the description", "Rename the task"

### Multi-Step Reasoning
When faced with ambiguous requests, the agent performs safe discovery:
1. Detects ambiguity in user request
2. Lists relevant tasks using `list_tasks` MCP tool
3. Asks for clarification or presents options
4. Executes requested action on confirmed target

### Error Handling
- Invalid inputs trigger helpful error messages
- MCP tool errors are communicated clearly to users
- Failed operations suggest alternative approaches
- JWT authentication failures return 401 Unauthorized

## Configuration Options

### Agent Settings
Adjust agent behavior via configuration:
- `intent_confidence_threshold`: Minimum confidence for direct action (default: 0.8)
- `max_ambiguity_attempts`: Maximum attempts to resolve ambiguous requests (default: 3)
- `confirmation_required`: Require confirmation for destructive operations (default: true)

### Conversation Management
- Conversations are stateless between requests
- Full conversation history is reconstructed from database for each request
- User isolation is maintained through JWT authentication

## Complete Usage Examples

### Example 1: Adding a Task
```bash
curl -X POST "http://localhost:8001/api/user123/chat" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

### Example 2: Listing Tasks
```bash
curl -X POST "http://localhost:8001/api/user123/chat" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my tasks"
  }'
```

### Example 3: Completing a Task (with ambiguity resolution)
```bash
curl -X POST "http://localhost:8001/api/user123/chat" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Complete the meeting task"
  }'
```

### Example 4: Multi-step flow (discovery-first pattern)
```bash
curl -X POST "http://localhost:8001/api/user123/chat" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Delete that one"
  }'
```

## Error Handling Examples

### Example: Invalid Input
```json
{
  "error": "Invalid input",
  "message": "I couldn't understand your request. Try rephrasing your request in simpler terms.",
  "code": "INVALID_INPUT"
}
```

### Example: Task Not Found
```json
{
  "error": "Task not found",
  "message": "I couldn't find the task you're looking for. It may have been deleted or you might need to be more specific about which task you mean.",
  "code": "TASK_NOT_FOUND"
}
```