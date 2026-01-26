'use client';

import React, { useState, useEffect } from 'react';
import { useChat } from 'ai/react';
import MessageRenderer from './MessageRenderer';
import InputValidator from './InputValidator';
import ErrorHandler from './ErrorHandler';
import ApiService from '../services/apiService';
import AuthService from '../services/authService';
import ValidationService from '../services/validationService';
import { generateId, getCurrentUserId } from '../lib/utils';

// Define types for our chat interface
interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  status?: 'sending' | 'delivered' | 'failed';
}

interface ChatInterfaceProps {
  userId?: string;
  sessionId?: string;
  onSessionChange?: (sessionId: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ userId: propUserId, sessionId: propSessionId, onSessionChange }) => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [userId, setUserId] = useState<string | null>(propUserId || null);
  const [sessionId, setSessionId] = useState<string | undefined>(propSessionId);

  const apiService = new ApiService();
  const authService = new AuthService();
  const validationService = new ValidationService();

  // Initialize user ID if not provided
  useEffect(() => {
    if (!propUserId && !userId) {
      const currentUserId = getCurrentUserId();
      if (currentUserId) {
        setUserId(currentUserId);
      }
    } else if (propUserId) {
      setUserId(propUserId);
    }
  }, [propUserId, userId]);

  // Initialize session ID if provided and restore conversation history
  useEffect(() => {
    if (propSessionId) {
      setSessionId(propSessionId);
    }

    // Restore conversation history on initial load
    const restoreHistory = async () => {
      if (userId && (propSessionId || sessionId)) {
        setIsLoading(true);
        try {
          const response = await apiService.restoreConversation(
            userId,
            propSessionId || sessionId
          );

          // Update session ID if new one was returned
          if (response.sessionId && response.sessionId !== sessionId) {
            setSessionId(response.sessionId);
            if (onSessionChange) {
              onSessionChange(response.sessionId);
            }
          }

          // Process the restored messages
          const restoredMessages: ChatMessage[] = response.conversationHistory.map(msg => ({
            id: msg.id,
            content: msg.content,
            role: msg.sender.toLowerCase() as 'user' | 'assistant',
            timestamp: msg.timestamp,
            status: 'delivered' as const,
          }));

          setMessages(restoredMessages);
        } catch (err) {
          console.error('Error restoring conversation:', err);
          setError('Failed to restore conversation history. Starting a new conversation.');
        } finally {
          setIsLoading(false);
        }
      }
    };

    restoreHistory();
  }, [userId, propSessionId, sessionId, onSessionChange]);

  // Handle sending a message
  const handleSendMessage = async (message: string) => {
    if (!userId) {
      setError('User ID is required to send messages');
      return;
    }

    // Validate the message
    const validationResult = validationService.validateMessage(message);
    if (!validationResult.isValid) {
      setError(validationResult.errors.join(', '));
      return;
    }

    // Add user message to UI immediately
    const userMessageId = generateId();
    const userMessage: ChatMessage = {
      id: userMessageId,
      content: message,
      role: 'user',
      timestamp: new Date().toISOString(),
      status: 'sending',
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setError(null);
    setIsLoading(true);

    try {
      // Prepare the request
      const chatRequest = {
        message: message,
        sessionId: sessionId,
        timestamp: new Date().toISOString(),
      };

      // Send message to backend
      const response = await apiService.sendMessage(userId, chatRequest);

      // Update session ID if new one was returned
      if (response.sessionId && response.sessionId !== sessionId) {
        setSessionId(response.sessionId);
        if (onSessionChange) {
          onSessionChange(response.sessionId);
        }
      }

      // Process the response messages
      const assistantMessages: ChatMessage[] = response.conversationHistory
        .filter(msg => msg.sender === 'ASSISTANT')
        .map(msg => ({
          id: msg.id,
          content: msg.content,
          role: 'assistant' as const,
          timestamp: msg.timestamp,
          status: 'delivered' as const,
        }));

      // Update the user message status to delivered
      setMessages(prev =>
        prev.map(msg =>
          msg.id === userMessageId
            ? { ...msg, status: 'delivered' }
            : msg
        )
      );

      // Add assistant messages to the chat
      setMessages(prev => {
        // Filter out any messages that are already in the state
        const newAssistantMessages = assistantMessages.filter(assMsg =>
          !prev.some(prevMsg => prevMsg.id === assMsg.id)
        );

        return [...prev, ...newAssistantMessages];
      });

    } catch (err: any) {
      console.error('Error sending message:', err);

      // Update the user message status to failed
      setMessages(prev =>
        prev.map(msg =>
          msg.id === userMessageId
            ? { ...msg, status: 'failed' }
            : msg
        )
      );

      setError(err.message || 'Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      handleSendMessage(input.trim());
    }
  };

  // Handle input change with validation
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInput(value);

    // Clear error if user starts typing after an error
    if (error) {
      setError(null);
    }
  };

  // Retry sending a failed message
  const handleRetryMessage = (messageId: string) => {
    const messageToRetry = messages.find(msg => msg.id === messageId && msg.role === 'user');
    if (messageToRetry) {
      handleSendMessage(messageToRetry.content);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto bg-background border border-border rounded-lg shadow-sm overflow-hidden">
      {/* Chat header */}
      <div className="bg-primary text-primary-foreground p-4">
        <h2 className="text-xl font-semibold">Todo AI Assistant</h2>
        <p className="text-sm opacity-80">Manage your todos with natural language</p>
      </div>

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/10">
        {messages.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <p>Start a conversation by typing a message below!</p>
            <p className="text-sm mt-2">Try: "Add a task to buy groceries" or "Show me my tasks"</p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageRenderer
              key={message.id}
              message={message}
              onRetry={message.role === 'user' && message.status === 'failed' ? () => handleRetryMessage(message.id) : undefined}
            />
          ))
        )}
        {isLoading && (
          <div className="flex items-center space-x-2 p-3 bg-secondary rounded-lg">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
            <span className="text-sm text-muted-foreground">AI is thinking...</span>
          </div>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/30 rounded-b-lg">
          <ErrorHandler errorMessage={error} />
        </div>
      )}

      {/* Input area */}
      <div className="border-t bg-background p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <InputValidator
            value={input}
            onChange={handleInputChange}
            onSubmit={handleSubmit}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </form>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          AI assistant can help you manage your todos using natural language
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;