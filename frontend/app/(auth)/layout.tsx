'use client';

import React from 'react';
import { useTheme } from '../../contexts/theme-context'; // Import useTheme to ensure theme is applied

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { theme } = useTheme(); // Use theme to ensure it's applied

  return (
    <div className={`min-h-screen flex items-center justify-center bg-background text-foreground ${theme} py-12 px-4 sm:px-6 lg:px-8`}>
      {children}
    </div>
  );
}