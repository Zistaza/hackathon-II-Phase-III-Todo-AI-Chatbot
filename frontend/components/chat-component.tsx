'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/auth-context';
import { chatService, ChatMessage } from '../services/chat-service';

interface ChatProps {
  userId: string;
}

const ChatComponent: React.FC<ChatProps> = ({ userId }) => {
  const { state: authState } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !authState.isAuthenticated || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
    };

    // Add user message to the chat
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send message to the backend
      const response = await chatService.sendMessage(userId, userMessage);

      // Add AI response to the chat
      setMessages((prev) => [
        ...prev,
        {
          content: response.response,
          role: 'assistant',
          timestamp: new Date(response.timestamp),
        },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          content: 'Sorry, there was an error processing your message.',
          role: 'system',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!authState.isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-full">
        <p>Please log in to access the chat feature.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-card border rounded-lg p-4">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4 max-h-[400px]">
        {messages.length === 0 ? (
          <div className="text-center text-muted-foreground mt-8">
            <p>Start a conversation with the AI assistant!</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : msg.role === 'assistant'
                    ? 'bg-secondary text-secondary-foreground'
                    : 'bg-destructive text-destructive-foreground'
                }`}
              >
                <p>{msg.content}</p>
                {msg.timestamp && (
                  <p className="text-xs opacity-70 mt-1">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type your message..."
          className="flex-1 border border-input rounded-lg p-2 resize-none min-h-[60px] max-h-[120px]"
          disabled={isLoading}
        />
        <button
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isLoading}
          className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default ChatComponent;