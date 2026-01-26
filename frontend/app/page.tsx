'use client';

import { useEffect, useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import { getCurrentUserId } from '../lib/utils';

export default function Home() {
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Get the current user ID
    const currentUserId = getCurrentUserId();
    setUserId(currentUserId);
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!userId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">User Authentication Required</h2>
          <p className="mb-4">Please log in to access the chat interface.</p>
          <button
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            onClick={() => window.location.href = '/auth/login'}
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8">
        <div className="h-[calc(100vh-4rem)]">
          <ChatInterface userId={userId} />
        </div>
      </div>
    </div>
  );
}
