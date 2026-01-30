'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '../../contexts/auth-context';
import { useRouter } from 'next/navigation';
import { Button } from '../ui/button';
import ThemeToggle from '../ui/theme-toggle';

export const Header: React.FC = () => {
  const { state, logout } = useAuth();
  const router = useRouter();

  return (
    <header className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-6 py-5 flex justify-between items-center">
        <Link href="/" className="text-3xl font-bold bg-gradient-to-r from-primary to-indigo-500 bg-clip-text text-transparent hover:opacity-90 transition-opacity">
          Todo App
        </Link>

        <nav className="flex items-center space-x-6">
          <ThemeToggle />
          {state.isAuthenticated ? (
            <>
              <Link href="/dashboard">
                <Button variant="primary" size="md" className="hover-lift">Dashboard</Button>
              </Link>
              <Link href="/tasks">
                <Button variant="primary" size="md" className="hover-lift">Tasks</Button>
              </Link>
              <Link href="/showcase">
                <Button variant="secondary" size="md" className="hover-lift">Styles Showcase</Button>
              </Link>
              <Button
                onClick={() => {
                  logout();
                  router.push('/login');
                  router.refresh(); // Refresh to ensure state updates
                }}
                variant="primary"
                size="md"
                className="hover-lift"
              >
                Logout
              </Button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-base font-medium hover:underline hover:text-primary transition-colors py-2">
                Login
              </Link>
              <Link href="/register" className="text-base font-medium hover:underline hover:text-primary transition-colors py-2">
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};