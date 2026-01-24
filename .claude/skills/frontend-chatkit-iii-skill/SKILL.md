---
name: frontend-chatkit-iii-skill
description: Build and manage the frontend chat interface using OpenAI ChatKit for Phase-III Todo AI Chatbot, integrating with backend chat API, MCP tools, and JWT authentication securely.
---

# Frontend ChatKit Skill (Phase III)

## Instructions

1. **ChatKit interface**
   - Use ChatKit components to build a responsive, user-friendly chat UI
   - Render user messages and AI assistant responses clearly
   - Display message timestamps and conversation context
   - Ensure accessibility standards (ARIA roles, keyboard navigation)

2. **Backend communication**
   - Send user messages to backend POST /api/{user_id}/chat endpoint
   - Include JWT token for authentication
   - Handle API responses, including AI response text and MCP tool outputs
   - Display tool outputs in the UI in a readable format

3. **Conversation replay**
   - Fetch and render previous messages on page load
   - Support stateless conversation: all state reconstructed from backend database
   - Enable smooth scrolling and message ordering

4. **JWT authentication**
   - Store JWT securely (e.g., in memory or secure storage)
   - Attach token to all requests to backend
   - Handle token expiration gracefully with user feedback

5. **MCP tool display**
   - Show results of MCP tool calls returned by backend
   - Format tool call outputs in a readable, user-friendly way
   - Handle errors or failed tool calls with clear messages

6. **Performance and responsive design**
   - Ensure the interface works on mobile, tablet, and desktop
   - Lazy-load messages if conversation history is large
   - Optimize component rendering to prevent lag

7. **Integration with AI agents**
   - Maintain correct message flow to OpenAI Agents SDK via backend
   - Do not allow frontend to perform task operations directly
   - Preserve cloud-native, stateless principles

## Best Practices
- Keep frontend stateless; rely on backend for all persistent data
- Validate and sanitize user input before sending to backend
- Maintain consistent styling and UX patterns
- Ensure proper error handling and fallback messages
- Test across multiple devices and screen sizes

## Example Structure
```javascript
import { ChatKit, MessageList, MessageInput } from "openai-chatkit";
import { sendMessageToBackend } from "./api";
import { useState, useEffect } from "react";

export default function ChatInterface({ userId, jwtToken }) {
  const [messages, setMessages] = useState([]);

  // Load conversation history
  useEffect(() => {
    async function loadHistory() {
      const history = await fetchConversationHistory(userId, jwtToken);
      setMessages(history);
    }
    loadHistory();
  }, [userId, jwtToken]);

  // Handle sending message
  async function handleSend(messageContent) {
    const response = await sendMessageToBackend(userId, messageContent, jwtToken);
    setMessages(prev => [...prev, { role: "user", content: messageContent }, { role: "assistant", content: response.response }]);
    // Optionally render MCP tool outputs
    if (response.tool_calls?.length) {
      response.tool_calls.forEach(tool => setMessages(prev => [...prev, { role: "system", content: JSON.stringify(tool) }]));
    }
  }

  return (
    <ChatKit>
      <MessageList messages={messages} />
      <MessageInput onSend={handleSend} />
    </ChatKit>
  );
}
