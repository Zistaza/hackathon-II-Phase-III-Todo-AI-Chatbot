'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '../../contexts/auth-context';
import { Header } from '../../components/navigation/header';
import { TodoProvider } from '../../contexts/todo-context';
import FloatingChatIcon from '../../components/FloatingChatIcon';
import { useTheme } from '../../contexts/theme-context'; // Import useTheme to ensure theme is applied

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { state } = useAuth();
  const { theme } = useTheme(); // Use theme to ensure it's applied

  // Show loading state while checking authentication
  // The middleware will handle redirecting unauthenticated users to login
  if (state.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // If user is not authenticated after loading, the middleware has already redirected
  // This shouldn't happen in practice since middleware handles it, but just in case
  if (!state.isAuthenticated) {
    // This case should not occur since middleware handles the redirect
    // Just render a message indicating redirection is happening
    typeof window !== 'undefined' && (window.location.href = '/login');
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <p>Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <TodoProvider>
      <div className={`min-h-screen bg-background text-foreground ${theme}`}>
        <Header />
        <main className="container mx-auto pt-20 sm:pt-24 px-4 sm:px-6 lg:px-8">
          {children}
        </main>
        <FloatingChatIcon />
      </div>
    </TodoProvider>
  );
}