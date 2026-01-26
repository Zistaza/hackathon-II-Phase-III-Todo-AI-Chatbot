import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from '../components/ChatInterface';
import ApiService from '../services/apiService';
import AuthService from '../services/authService';
import ValidationService from '../services/validationService';

// Mock the services
jest.mock('../services/apiService');
jest.mock('../services/authService');
jest.mock('../services/validationService');

const MockApiService = ApiService as jest.MockedClass<typeof ApiService>;
const MockAuthService = AuthService as jest.MockedClass<typeof AuthService>;
const MockValidationService = ValidationService as jest.MockedClass<typeof ValidationService>;

describe('End-to-End Chat Functionality', () => {
  const mockUserId = 'test-user-123';
  const mockSessionId = 'test-session-456';

  beforeEach(() => {
    jest.clearAllMocks();

    // Mock the AuthService methods
    MockAuthService.prototype.getToken = jest.fn().mockReturnValue('mock-token');
    MockAuthService.prototype.getUserId = jest.fn().mockReturnValue(mockUserId);
    MockAuthService.prototype.isAuthenticated = jest.fn().mockReturnValue(true);

    // Mock the ValidationService methods
    MockValidationService.prototype.validateMessage = jest.fn().mockReturnValue({
      isValid: true,
      errors: [],
      warnings: [],
      sanitizedValue: 'test message'
    });

    // Mock the ApiService methods
    MockApiService.prototype.restoreConversation = jest.fn().mockResolvedValue({
      response: '',
      toolCallResults: [],
      conversationHistory: [],
      sessionId: mockSessionId,
      timestamp: new Date().toISOString()
    });
  });

  it('should allow full chat flow: restore conversation, send message, receive response', async () => {
    // Mock the API service to return a response
    const mockSendMessage = jest.fn().mockResolvedValue({
      response: 'Sure, I can help with that!',
      toolCallResults: [
        {
          toolName: 'create_todo',
          result: { id: 'todo-123', title: 'Buy groceries', completed: false },
          status: 'success'
        }
      ],
      conversationHistory: [
        {
          id: 'msg-1',
          content: 'Add a task to buy groceries',
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

    render(<ChatInterface userId={mockUserId} sessionId={mockSessionId} />);

    // Wait for conversation restoration
    await waitFor(() => {
      expect(MockApiService.prototype.restoreConversation).toHaveBeenCalledWith(
        mockUserId,
        mockSessionId
      );
    });

    // Send a message
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: 'Send' });

    fireEvent.change(input, { target: { value: 'Add a task to buy groceries' } });
    fireEvent.click(sendButton);

    // Wait for message to be sent and response received
    await waitFor(() => {
      expect(screen.getByText('Add a task to buy groceries')).toBeInTheDocument();
      expect(screen.getByText('Sure, I can help with that!')).toBeInTheDocument();
    });

    // Verify API was called with correct parameters
    expect(MockApiService.prototype.sendMessage).toHaveBeenCalledWith(
      mockUserId,
      expect.objectContaining({
        message: 'Add a task to buy groceries',
        sessionId: mockSessionId
      })
    );

    // Verify validation was performed
    expect(MockValidationService.prototype.validateMessage).toHaveBeenCalledWith(
      'Add a task to buy groceries'
    );
  });

  it('should handle error in message flow gracefully', async () => {
    // Mock the API service to throw an error
    const mockSendMessage = jest.fn().mockRejectedValue(new Error('API error'));
    MockApiService.prototype.sendMessage = mockSendMessage;

    render(<ChatInterface userId={mockUserId} />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: 'Send' });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText('API error')).toBeInTheDocument();
    });

    // Verify error handling worked correctly
    expect(screen.getByText('API error')).toBeInTheDocument();
  });

  it('should validate input before sending', async () => {
    // Mock validation to fail
    MockValidationService.prototype.validateMessage = jest.fn().mockReturnValue({
      isValid: false,
      errors: ['Message is too short'],
      warnings: [],
      sanitizedValue: 'short'
    });

    render(<ChatInterface userId={mockUserId} />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: 'Send' });

    fireEvent.change(input, { target: { value: 'hi' } }); // Very short message
    fireEvent.click(sendButton);

    // Verify that sendMessage was not called because validation failed
    expect(MockApiService.prototype.sendMessage).not.toHaveBeenCalled();

    // Verify that error is displayed
    expect(screen.getByText('Message is too short')).toBeInTheDocument();
  });

  it('should maintain conversation state correctly', async () => {
    // Mock multiple responses
    let callCount = 0;
    const mockSendMessage = jest.fn().mockImplementation((userId: string, request: any) => {
      callCount++;
      return Promise.resolve({
        response: callCount === 1 ? 'Got it, first message!' : 'Understood, second message!',
        toolCallResults: [],
        conversationHistory: [
          {
            id: `msg-${callCount}`,
            content: request.message,
            sender: 'USER',
            timestamp: new Date().toISOString(),
            status: 'DELIVERED'
          },
          {
            id: `resp-${callCount}`,
            content: callCount === 1 ? 'Got it, first message!' : 'Understood, second message!',
            sender: 'ASSISTANT',
            timestamp: new Date().toISOString(),
            status: 'DELIVERED'
          }
        ],
        sessionId: mockSessionId,
        timestamp: new Date().toISOString()
      });
    });

    MockApiService.prototype.sendMessage = mockSendMessage;

    render(<ChatInterface userId={mockUserId} />);

    // Send first message
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: 'Send' });

    fireEvent.change(input, { target: { value: 'First message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('First message')).toBeInTheDocument();
      expect(screen.getByText('Got it, first message!')).toBeInTheDocument();
    });

    // Send second message
    fireEvent.change(input, { target: { value: 'Second message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Second message')).toBeInTheDocument();
      expect(screen.getByText('Understood, second message!')).toBeInTheDocument();
    });

    // Verify both conversations are visible
    expect(screen.getAllByText('First message')).toHaveLength(1);
    expect(screen.getAllByText('Got it, first message!')).toHaveLength(1);
    expect(screen.getAllByText('Second message')).toHaveLength(1);
    expect(screen.getAllByText('Understood, second message!')).toHaveLength(1);
  });
});