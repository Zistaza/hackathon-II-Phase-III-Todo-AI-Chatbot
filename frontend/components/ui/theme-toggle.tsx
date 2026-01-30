'use client';

import React from 'react';
import { useTheme } from '@/contexts/theme-context';
import { FiSun, FiMoon } from 'react-icons/fi';

const ThemeToggle: React.FC = () => {
  const { theme, setTheme, isSystemPreferred, setIsSystemPreferred } = useTheme();

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    setIsSystemPreferred(false);
  };

  const toggleSystemPreference = () => {
    setIsSystemPreferred(!isSystemPreferred);
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={toggleTheme}
        aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        className="relative rounded-full p-2 btn-enhanced hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        role="switch"
        aria-checked={theme === 'dark'}
      >
        {theme === 'light' ? (
          <FiMoon className="h-5 w-5 text-foreground" aria-hidden="true" />
        ) : (
          <FiSun className="h-5 w-5 text-foreground" aria-hidden="true" />
        )}
      </button>
      <button
        onClick={toggleSystemPreference}
        aria-label={`Turn ${isSystemPreferred ? 'off' : 'on'} system preference`}
        className="text-xs px-2 py-1 rounded bg-accent text-accent-foreground hover:bg-accent/80 transition-colors"
      >
        {isSystemPreferred ? 'System' : 'Manual'}
      </button>
    </div>
  );
};

export default ThemeToggle;