'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../../contexts/auth-context';
import { useRouter } from 'next/navigation';
import { Button } from '../ui/button';
import ThemeToggle from '../ui/theme-toggle';

export const Header: React.FC = () => {
  const { state, logout } = useAuth();
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <header className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50 shadow-sm border-border/40 h-16 sm:h-20">
      <div className="container mx-auto px-4 sm:px-6 py-4 sm:py-5 h-full">
        <div className="flex justify-between items-center h-full">
          <Link
            href="/"
            className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-primary to-indigo-500 bg-clip-text text-transparent hover:opacity-90 transition-all duration-300 transform hover:scale-105"
            onClick={closeMenu}
          >
            Todo App
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-3 sm:space-x-4">
            <ThemeToggle />
            {state.isAuthenticated ? (
              <div className="flex items-center space-x-2 sm:space-x-3">
                <Link href="/dashboard">
                  <Button variant="ghost" size="md" className="hover:bg-primary/10 hover:text-primary transition-all duration-200 rounded-lg px-3 py-2">
                    Dashboard
                  </Button>
                </Link>
                <Link href="/tasks">
                  <Button variant="ghost" size="md" className="hover:bg-primary/10 hover:text-primary transition-all duration-200 rounded-lg px-3 py-2">
                    Tasks
                  </Button>
                </Link>
                <Button
                  onClick={() => {
                    logout();
                    router.push('/login');
                    router.refresh(); // Refresh to ensure state updates
                  }}
                  variant="outline"
                  size="md"
                  className="border-destructive/30 hover:bg-destructive/10 hover:border-destructive text-destructive hover:text-destructive transition-all duration-200 rounded-lg px-4 py-2"
                >
                  Logout
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 sm:space-x-3">
                <Link href="/login">
                  <Button variant="ghost" size="md" className="hover:bg-primary/10 hover:text-primary transition-all duration-200 rounded-lg px-3 py-2">
                    Login
                  </Button>
                </Link>
                <Link href="/register">
                  <Button variant="primary" size="md" className="bg-gradient-to-r from-primary to-indigo-500 hover:from-primary/90 hover:to-indigo-500/90 text-white transition-all duration-200 transform hover:scale-105 rounded-lg px-4 py-2 shadow-md hover:shadow-lg">
                    Register
                  </Button>
                </Link>
              </div>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center space-x-2">
            <ThemeToggle />
            <button
              onClick={toggleMenu}
              className="p-2 rounded-lg hover:bg-accent transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              aria-label="Toggle menu"
            >
              <svg
                className="w-6 h-6 text-foreground"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-2 pb-4 border-t border-border pt-4">
            <nav className="flex flex-col space-y-2">
              {state.isAuthenticated ? (
                <>
                  <Link
                    href="/dashboard"
                    className="px-4 py-3 rounded-lg hover:bg-accent transition-colors duration-200 text-foreground font-medium"
                    onClick={closeMenu}
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/tasks"
                    className="px-4 py-3 rounded-lg hover:bg-accent transition-colors duration-200 text-foreground font-medium"
                    onClick={closeMenu}
                  >
                    Tasks
                  </Link>
                  <button
                    onClick={() => {
                      logout();
                      router.push('/login');
                      router.refresh(); // Refresh to ensure state updates
                      closeMenu();
                    }}
                    className="px-4 py-3 rounded-lg hover:bg-destructive/10 hover:text-destructive text-destructive transition-colors duration-200 text-left font-medium"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="px-4 py-3 rounded-lg hover:bg-accent transition-colors duration-200 text-foreground font-medium"
                    onClick={closeMenu}
                  >
                    Login
                  </Link>
                  <Link
                    href="/register"
                    className="px-4 py-3 rounded-lg bg-gradient-to-r from-primary to-indigo-500 hover:from-primary/90 hover:to-indigo-500/90 text-white transition-all duration-200 font-medium text-center"
                    onClick={closeMenu}
                  >
                    Register
                  </Link>
                </>
              )}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};