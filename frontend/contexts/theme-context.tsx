'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  isSystemPreferred: boolean;
  setIsSystemPreferred: (isSystem: boolean) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>('light');
  const [isSystemPreferred, setIsSystemPreferred] = useState<boolean>(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Check for saved theme in localStorage
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    const savedSystemPreference = localStorage.getItem('isSystemPreferred') === 'true';

    // Check system preference
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
      // If user has explicitly set a theme, use that
      setTheme(savedTheme);
      setIsSystemPreferred(false);
    } else if (savedSystemPreference) {
      // If system preference is enabled, follow system
      setTheme(systemPrefersDark ? 'dark' : 'light');
      setIsSystemPreferred(true);
    } else {
      // Default to light theme
      setTheme('light');
      setIsSystemPreferred(true);
    }

    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    const body = document.body;

    // Remove old theme classes
    root.classList.remove('light', 'dark');
    body.classList.remove('light', 'dark');

    // Add new theme class to both html and body elements for better consistency
    root.classList.add(theme);
    body.classList.add(theme);

    // Apply smooth transition to both html and body
    root.style.setProperty('transition', 'all 0.3s ease');
    body.style.setProperty('transition', 'all 0.3s ease');

    // Save to localStorage
    localStorage.setItem('theme', theme);
    localStorage.setItem('isSystemPreferred', String(isSystemPreferred));

    // Clean up transition after animation
    const timer = setTimeout(() => {
      root.style.removeProperty('transition');
      body.style.removeProperty('transition');
    }, 300);

    return () => clearTimeout(timer);
  }, [theme, mounted, isSystemPreferred]);

  // Listen to system preference changes
  useEffect(() => {
    if (!mounted) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = () => {
      if (isSystemPreferred) {
        setTheme(mediaQuery.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleChange);

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [isSystemPreferred, mounted]);

  const value = {
    theme,
    setTheme,
    isSystemPreferred,
    setIsSystemPreferred
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};