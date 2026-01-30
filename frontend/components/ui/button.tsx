'use client';

import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  className = '',
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-lg font-semibold btn-enhanced focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background shadow-sm whitespace-nowrap';

  const variantClasses = {
    primary: 'bg-gradient-to-r from-primary to-indigo-500 text-primary-foreground hover:from-primary/90 hover:to-indigo-600 active:from-primary/80 active:to-indigo-700',
    secondary: 'bg-gradient-to-r from-secondary to-gray-400 text-secondary-foreground hover:from-secondary/90 hover:to-gray-500 active:from-secondary/80 active:to-gray-600',
    danger: 'bg-gradient-to-r from-destructive to-rose-600 text-destructive-foreground hover:from-destructive/90 hover:to-rose-700 active:from-destructive/80 active:to-rose-800',
  };

  const sizeClasses = {
    sm: 'h-10 min-h-10 px-4 text-sm',
    md: 'h-12 min-h-12 px-6 text-base',
    lg: 'h-14 min-h-14 px-8 text-lg',
  };

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  return (
    <button
      className={classes}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </>
      ) : children}
    </button>
  );
};