import axios, { AxiosResponse } from 'axios';

// Define types for our API interactions
interface ChatRequest {
  message: string;
  sessionId?: string;
  timestamp?: string;
}

interface ToolCallResult {
  toolName: string;
  result: any;
  status: string;
}

interface ChatMessage {
  id: string;
  content: string;
  sender: 'USER' | 'ASSISTANT';
  timestamp: string;
  status: 'SENT' | 'DELIVERED' | 'FAILED' | 'PROCESSING';
}

interface ChatResponse {
  response: string;
  message_id: string;
  timestamp: string;
  conversation_id: string;
  // For compatibility with ChatInterface, we'll add the expected fields
  toolCallResults?: ToolCallResult[];
  conversationHistory?: ChatMessage[];
  sessionId?: string;
}

class ApiService {
  private baseUrl: string;
  private jwtToken: string | null;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '';
    this.jwtToken = this.getToken();
  }

  // Get token from both localStorage and cookies
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      // Check localStorage first
      const token = localStorage.getItem('authToken');
      if (token) {
        return token;
      }

      // Check cookies as fallback
      const cookies = document.cookie.split(';');
      for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'authToken') {
          return value;
        }
      }
    }
    return null;
  }

  // Set JWT token for authentication
  setAuthToken(token: string | null): void {
    this.jwtToken = token;
    if (typeof window !== 'undefined' && token) {
      localStorage.setItem('authToken', token);
      // Also set in cookies for consistency
      const date = new Date();
      date.setTime(date.getTime() + (7 * 24 * 60 * 60 * 1000)); // 7 days
      document.cookie = `authToken=${token}; expires=${date.toUTCString()}; path=/; SameSite=Lax`;
    } else if (typeof window !== 'undefined') {
      localStorage.removeItem('authToken');
      document.cookie = 'authToken=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/;';
    }
  }

  // Get auth headers
  private getAuthHeaders(): { [key: string]: string } {
    // Refresh token in case it was updated elsewhere
    this.jwtToken = this.getToken();

    const headers: { [key: string]: string } = {
      'Content-Type': 'application/json',
    };

    if (this.jwtToken) {
      headers['Authorization'] = `Bearer ${this.jwtToken}`;
    }

    return headers;
  }

  // Send a message to the chat endpoint
  async sendMessage(userId: string, request: ChatRequest): Promise<ChatResponse> {
    try {
      // Transform the request to match the backend's ChatMessage format
      const chatMessage = {
        content: request.message,
        role: "user", // Backend expects role as a string
        timestamp: request.timestamp || new Date().toISOString()
      };

      const response: AxiosResponse<ChatResponse> = await axios.post(
        `${this.baseUrl}/api/chat/${userId}`,
        chatMessage,
        {
          headers: this.getAuthHeaders(),
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Error sending message:', error);

      // Handle different types of errors
      if (error.response) {
        // Server responded with error status
        throw new Error(`Server error: ${error.response.status} - ${error.response.data?.message || 'Unknown error'}`);
      } else if (error.request) {
        // Request was made but no response received
        throw new Error('Network error: Unable to reach server');
      } else {
        // Something else happened
        throw new Error(`Request error: ${error.message}`);
      }
    }
  }

  // Fetch conversation history (if needed for restoration)
  async getConversationHistory(userId: string, sessionId?: string): Promise<ChatResponse> {
    try {
      // Currently, we'll return an empty conversation history since the backend
      // doesn't have a specific endpoint for fetching full conversation history
      // This is a simplified approach for now
      return {
        response: '',
        message_id: '',
        timestamp: new Date().toISOString(),
        conversation_id: sessionId || '',
        toolCallResults: [],
        conversationHistory: [],
        sessionId: sessionId,
      };
    } catch (error: any) {
      console.error('Error fetching conversation history:', error);
      throw error;
    }
  }

  // Restore conversation from backend on initial load
  async restoreConversation(userId: string, sessionId?: string): Promise<ChatResponse> {
    try {
      // If we have a session ID, try to restore that session
      if (sessionId) {
        // Currently, we'll return an empty conversation history since the backend
        // doesn't have a specific endpoint for fetching full conversation history
        // This is a simplified approach for now
        return {
          response: '',
          message_id: '',
          timestamp: new Date().toISOString(),
          conversation_id: sessionId,
          toolCallResults: [],
          conversationHistory: [],
          sessionId: sessionId,
        };
      }

      // If no session ID, return empty response
      return {
        response: '',
        message_id: '',
        timestamp: new Date().toISOString(),
        conversation_id: '',
        toolCallResults: [],
        conversationHistory: [],
        sessionId: '',
      };
    } catch (error: any) {
      console.error('Error restoring conversation:', error);
      // Return empty conversation on error
      return {
        response: '',
        message_id: '',
        timestamp: new Date().toISOString(),
        conversation_id: '',
        toolCallResults: [],
        conversationHistory: [],
        sessionId: '',
      };
    }
  }

  // Validate conversation history structure
  private validateConversationHistory(history: any[] | undefined): boolean {
    if (!history || !Array.isArray(history)) {
      return false;
    }

    for (const item of history) {
      if (
        typeof item !== 'object' ||
        !item.id ||
        !item.content ||
        !item.sender ||
        !item.timestamp ||
        !['USER', 'ASSISTANT'].includes(item.sender)
      ) {
        return false;
      }
    }

    return true;
  }

  // Health check for the API
  async healthCheck(): Promise<boolean> {
    try {
      await axios.get(`${this.baseUrl}/health`);
      return true;
    } catch (error) {
      console.error('API health check failed:', error);
      return false;
    }
  }
}

export default ApiService;