// Frontend chat service to interact with the secured chat API
import axios from 'axios';
import { getCookie } from '../lib/cookies';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

const chatInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token to all chat API requests
chatInstance.interceptors.request.use(
  (config) => {
    const token = getCookie('authToken') || localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 and 403 responses
chatInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Clear stored tokens and redirect to login
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      document.cookie = 'authToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      document.cookie = 'userData=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface ChatMessage {
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp?: Date;
}

export interface ChatResponse {
  response: string;
  message_id: string;
  timestamp: Date;
  conversation_id: string;
}

export interface ChatHistoryRequest {
  limit?: number;
  offset?: number;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  total_count: number;
  has_more: boolean;
}

export const chatService = {
  /**
   * Send a chat message to the AI
   */
  sendMessage: async (userId: string, message: ChatMessage): Promise<ChatResponse> => {
    try {
      const response = await chatInstance.post<ChatResponse>(`/chat/${userId}`, message);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to send message');
    }
  },

  /**
   * Get chat history for a user
   */
  getChatHistory: async (
    userId: string,
    params: ChatHistoryRequest = {}
  ): Promise<ChatHistoryResponse> => {
    try {
      const response = await chatInstance.get<ChatHistoryResponse>(`/chat/${userId}/history`, {
        params,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get chat history');
    }
  },

  /**
   * Delete a conversation
   */
  deleteConversation: async (userId: string, conversationId: string): Promise<void> => {
    try {
      await chatInstance.delete(`/chat/${userId}/conversation/${conversationId}`);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to delete conversation');
    }
  },
};