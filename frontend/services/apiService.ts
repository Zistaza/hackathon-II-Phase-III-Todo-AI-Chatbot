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
  toolCallResults: ToolCallResult[];
  conversationHistory: ChatMessage[];
  sessionId: string;
  timestamp: string;
}

class ApiService {
  private baseUrl: string;
  private jwtToken: string | null;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '';
    this.jwtToken = typeof window !== 'undefined' ? localStorage.getItem('jwtToken') : null;
  }

  // Set JWT token for authentication
  setAuthToken(token: string | null): void {
    this.jwtToken = token;
    if (typeof window !== 'undefined' && token) {
      localStorage.setItem('jwtToken', token);
    } else if (typeof window !== 'undefined') {
      localStorage.removeItem('jwtToken');
    }
  }

  // Get auth headers
  private getAuthHeaders(): { [key: string]: string } {
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
      const response: AxiosResponse<ChatResponse> = await axios.post(
        `${this.baseUrl}/api/${userId}/chat`,
        request,
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
      // We'll simulate getting conversation history by sending an empty message
      // In a real implementation, you might have a dedicated endpoint for this
      const request: ChatRequest = {
        message: '',
        sessionId,
      };

      return await this.sendMessage(userId, request);
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
        const request: ChatRequest = {
          message: '',
          sessionId,
        };

        const response = await this.sendMessage(userId, request);

        // Verify the response has valid conversation history
        if (this.validateConversationHistory(response.conversationHistory)) {
          return response;
        }
      }

      // If no session ID or restoration failed, return empty response
      return {
        response: '',
        toolCallResults: [],
        conversationHistory: [],
        sessionId: '',
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      console.error('Error restoring conversation:', error);
      // Return empty conversation on error
      return {
        response: '',
        toolCallResults: [],
        conversationHistory: [],
        sessionId: '',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Validate conversation history structure
  private validateConversationHistory(history: any[]): boolean {
    if (!Array.isArray(history)) {
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