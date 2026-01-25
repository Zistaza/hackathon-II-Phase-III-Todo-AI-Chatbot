# Quickstart Guide: Todo AI Chatbot - Chat API

## Prerequisites

- Python 3.11+
- pip package manager
- Access to Neon Serverless PostgreSQL
- Better Auth configured with JWT support
- OpenAI API key
- MCP server with todo tools configured

## Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd hackathon-II-phase-III-todo-ai-chatbot
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration:
# DATABASE_URL=your_neon_postgres_url
# BETTER_AUTH_SECRET=your_jwt_secret
# OPENAI_API_KEY=your_openai_api_key
# MCP_SERVER_URL=your_mcp_server_url
```

## Database Setup

1. Initialize the database:
```bash
# Run migrations to create required tables
python -m src.database.migrate
```

## Running the Service

1. Start the backend service:
```bash
python -m src.main
```

2. The chat API will be available at:
```
POST http://localhost:8000/api/{user_id}/chat
```

## API Usage Example

### Send a message to the AI assistant:
```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a todo: Buy groceries",
    "conversation_id": 1
  }'
```

### Response format:
```json
{
  "conversation_id": 1,
  "response": "I've created the todo 'Buy groceries' for you.",
  "tool_calls": [
    {
      "tool_name": "create_todo",
      "input": {"title": "Buy groceries"},
      "result": {"id": 456, "title": "Buy groceries", "completed": false}
    }
  ]
}
```

## Testing

1. Run unit tests:
```bash
pytest tests/unit/
```

2. Run integration tests:
```bash
pytest tests/integration/
```

3. Run contract tests:
```bash
pytest tests/contract/
```

## Configuration

### JWT Settings
- Token validation happens on every request
- User ID in URL path must match JWT subject
- Invalid tokens return 401 Unauthorized

### MCP Integration
- MCP tools are registered at startup
- Tool calls are logged and persisted
- Error handling for failed tool executions

### State Management
- Conversation history reconstructed from database on each request
- No server-side session storage
- All state persisted to database before response