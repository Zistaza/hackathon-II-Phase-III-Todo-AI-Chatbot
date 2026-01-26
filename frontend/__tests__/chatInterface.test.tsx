import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from '../components/ChatInterface';
import ApiService from '../services/apiService';
import AuthService from '../services/authService';

// Mock the services
jest.mock('../services/apiService');
jest.mock('../services/authService');

const MockApiService = ApiService as jest.MockedClass<typeof ApiService>;
const MockAuthService = AuthService as jest.MockedClass<typeof AuthService>;

describe('ChatInterface Component', () => {
  const mockUserId = 'test-user-123';
  const mockSessionId = 'test-session-456';

  beforeEach(() => {
    jest.clearAllMocks();

    // Mock the AuthService methods
    MockAuthService.prototype.getToken = jest.fn().mockReturnValue('mock-token');
    MockAuthService.prototype.getUserId = jest.fn().mockReturnValue(mockUserId);
    MockAuthService.prototype.isAuthenticated = jest.fn().mockReturnValue(true);
  });

  it('renders the chat interface with header and input', () => {
    render(<ChatInterface userId={mockUserId} />);

    expect(screen.getByText('Todo AI Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send' })).toBeInTheDocument();
  });

  it('displays initial message when no messages exist', () => {
    render(<ChatInterface userId={mockUserId} />);

    expect(screen.getByText('Start a conversation by typing a message below!')).toBeInTheDocument();
  });

  it('allows user to type and send a message', async () => {
    // Mock the API service to return a response
    const mockSendMessage = jest.fn().mockResolvedValue({
      response: 'Sure, I can help with that!',
      toolCallResults: [],
      conversationHistory: [
        {
          id: 'msg-1',
          content: 'Test message',
          sender: 'USER',
          timestamp: new Date().toISOString(),
          status: 'DELIVERED'
        },
        {
          id: 'msg-2',
          content: 'Sure, I can help with that!',
          sender: 'ASSISTANT',
          timestamp: new Date().toISOString(),
          status: 'DELIVERED'
        }
      ],
      sessionId: mockSessionId,
      timestamp: new Date().toISOString()
    });

    MockApiService.prototype.sendMessage = mockSendMessage;
    MockApiService.prototype.restoreConversation = jest.fn().mockResolvedValue({
      response: '',
      toolCallResults: [],
      conversationHistory: [],
      sessionId: mockSessionId,
      timestamp: new Date().toISOString()
    });

    render(<ChatInterface userId={mockUserId} />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: 'Send' });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith(
        mockUserId,
        expect.objectContaining({
          message: 'Test message'
        })
      );
    });
  });

  it('shows error message when sending fails', async () => {
    const mockSendMessage = jest.fn().mockRejectedValue(new Error('Network error'));
    MockApiService.prototype.sendMessage = mockSendMessage;
    MockApiService.prototype.restoreConversation = jest.fn().mockResolvedValue({
      response: '',
      toolCallResults: [],
      conversationHistory: [],
      sessionId: mockSessionId,
      timestamp: new Date().toISOString()
    });

    render(<ChatInterface userId={mockUserId} />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: 'Send' });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('validates input before sending', async () => {
    const mockSendMessage = jest.fn();
    MockApiService.prototype.sendMessage = mockSendMessage;
    MockApiService.prototype.restoreConversation = jest.fn().mockResolvedValue({
      response: '',
      toolCallResults: [],
      conversationHistory: [],
      sessionId: mockSessionId,
      timestamp: new Date().toISOString()
    });

    render(<ChatInterface userId={mockUserId} />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: 'Send' });

    // Try to send an empty message
    fireEvent.click(sendButton);

    // The send function should not be called
    expect(mockSendMessage).not.toHaveBeenCalled();
  });

  it('restores conversation history on initial load', async () => {
    const mockRestoreConversation = jest.fn().mockResolvedValue({
      response: '',
      toolCallResults: [],
      conversationHistory: [
        {
          id: 'msg-1',
          content: 'Previous message',
          sender: 'USER',
          timestamp: new Date().toISOString(),
          status: 'DELIVERED'
        },
        {
          id: 'msg-2',
          content: 'Previous response',
          sender: 'ASSISTANT',
          timestamp: new Date().toISOString(),
          status: 'DELIVERED'
        }
      ],
      sessionId: mockSessionId,
      timestamp: new Date().toISOString()
    });

    MockApiService.prototype.restoreConversation = mockRestoreConversation;

    render(<ChatInterface userId={mockUserId} sessionId={mockSessionId} />);

    await waitFor(() => {
      expect(screen.getByText('Previous message')).toBeInTheDocument();
      expect(screen.getByText('Previous response')).toBeInTheDocument();
    });

    expect(mockRestoreConversation).toHaveBeenCalledWith(mockUserId, mockSessionId);
  });
});