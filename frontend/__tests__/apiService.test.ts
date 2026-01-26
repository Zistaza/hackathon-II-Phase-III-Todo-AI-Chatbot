import ApiService from '../services/apiService';
import axios from 'axios';

// Mock axios
jest.mock('axios');

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiService', () => {
  let apiService: ApiService;

  beforeEach(() => {
    apiService = new ApiService();
    // Set a mock base URL for testing
    Object.defineProperty(apiService, 'baseUrl', {
      value: 'http://localhost:8000',
      writable: true,
    });
    Object.defineProperty(apiService, 'jwtToken', {
      value: 'mock-jwt-token',
      writable: true,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('sendMessage', () => {
    it('should send a message to the backend and return response', async () => {
      const userId = 'user-123';
      const message = 'Hello, world!';
      const mockResponse = {
        response: 'Hi there!',
        toolCallResults: [],
        conversationHistory: [
          {
            id: 'msg-1',
            content: 'Hello, world!',
            sender: 'USER',
            timestamp: new Date().toISOString(),
            status: 'DELIVERED'
          },
          {
            id: 'msg-2',
            content: 'Hi there!',
            sender: 'ASSISTANT',
            timestamp: new Date().toISOString(),
            status: 'DELIVERED'
          }
        ],
        sessionId: 'session-456',
        timestamp: new Date().toISOString()
      };

      mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await apiService.sendMessage(userId, {
        message,
      });

      expect(mockedAxios.post).toHaveBeenCalledWith(
        `http://localhost:8000/api/${userId}/chat`,
        { message },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-jwt-token'
          }
        }
      );

      expect(result).toEqual(mockResponse);
    });

    it('should handle server error responses', async () => {
      const userId = 'user-123';
      const message = 'Hello, world!';

      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      });

      await expect(apiService.sendMessage(userId, { message }))
        .rejects
        .toThrow('Server error: 500 - Internal server error');
    });

    it('should handle network error responses', async () => {
      const userId = 'user-123';
      const message = 'Hello, world!';

      mockedAxios.post.mockRejectedValueOnce({
        request: {}
      });

      await expect(apiService.sendMessage(userId, { message }))
        .rejects
        .toThrow('Network error: Unable to reach server');
    });

    it('should handle request error responses', async () => {
      const userId = 'user-123';
      const message = 'Hello, world!';

      mockedAxios.post.mockRejectedValueOnce({
        message: 'Request failed'
      });

      await expect(apiService.sendMessage(userId, { message }))
        .rejects
        .toThrow('Request error: Request failed');
    });
  });

  describe('getConversationHistory', () => {
    it('should fetch conversation history', async () => {
      const userId = 'user-123';
      const sessionId = 'session-456';
      const mockResponse = {
        response: '',
        toolCallResults: [],
        conversationHistory: [],
        sessionId,
        timestamp: new Date().toISOString()
      };

      mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await apiService.getConversationHistory(userId, sessionId);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        `http://localhost:8000/api/${userId}/chat`,
        { message: '', sessionId },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-jwt-token'
          }
        }
      );

      expect(result).toEqual(mockResponse);
    });
  });

  describe('restoreConversation', () => {
    it('should restore conversation with a session ID', async () => {
      const userId = 'user-123';
      const sessionId = 'session-456';
      const mockResponse = {
        response: '',
        toolCallResults: [],
        conversationHistory: [
          {
            id: 'msg-1',
            content: 'Previous message',
            sender: 'USER',
            timestamp: new Date().toISOString(),
            status: 'DELIVERED'
          }
        ],
        sessionId,
        timestamp: new Date().toISOString()
      };

      mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await apiService.restoreConversation(userId, sessionId);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        `http://localhost:8000/api/${userId}/chat`,
        { message: '', sessionId },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-jwt-token'
          }
        }
      );

      expect(result).toEqual(mockResponse);
    });

    it('should return empty conversation if no session ID provided', async () => {
      const userId = 'user-123';

      const result = await apiService.restoreConversation(userId);

      expect(result).toEqual({
        response: '',
        toolCallResults: [],
        conversationHistory: [],
        sessionId: '',
        timestamp: expect.any(String)
      });
    });

    it('should return empty conversation on error', async () => {
      const userId = 'user-123';
      const sessionId = 'session-456';

      mockedAxios.post.mockRejectedValueOnce(new Error('Network error'));

      const result = await apiService.restoreConversation(userId, sessionId);

      expect(result).toEqual({
        response: '',
        toolCallResults: [],
        conversationHistory: [],
        sessionId: '',
        timestamp: expect.any(String)
      });
    });
  });

  describe('healthCheck', () => {
    it('should return true if API is healthy', async () => {
      mockedAxios.get.mockResolvedValueOnce({ status: 200 });

      const result = await apiService.healthCheck();

      expect(mockedAxios.get).toHaveBeenCalledWith('http://localhost:8000/health');
      expect(result).toBe(true);
    });

    it('should return false if API is not healthy', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

      const result = await apiService.healthCheck();

      expect(result).toBe(false);
    });
  });
});