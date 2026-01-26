import React from 'react';
import { formatTimestamp } from '../lib/utils';

// Define types for our message renderer
interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  status?: 'sending' | 'delivered' | 'failed';
}

interface MessageRendererProps {
  message: ChatMessage;
  onRetry?: () => void;
}

const MessageRenderer: React.FC<MessageRendererProps> = ({ message, onRetry }) => {
  const isUser = message.role === 'user';
  const isFailed = message.status === 'failed';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-primary text-primary-foreground rounded-br-none'
            : 'bg-secondary text-secondary-foreground rounded-bl-none'
        } ${isFailed ? 'bg-destructive/20 border border-destructive/30' : ''}`}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>

        <div className="flex items-center justify-between mt-2 text-xs opacity-70">
          <span>{formatTimestamp(message.timestamp)}</span>

          {message.role === 'user' && (
            <div className="flex items-center space-x-1">
              {message.status === 'sending' && (
                <span className="text-xs">Sending...</span>
              )}
              {message.status === 'delivered' && (
                <span className="text-xs">✓ Delivered</span>
              )}
              {message.status === 'failed' && (
                <button
                  onClick={onRetry}
                  className="text-xs text-destructive hover:underline cursor-pointer"
                >
                  Failed - Retry
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageRenderer;