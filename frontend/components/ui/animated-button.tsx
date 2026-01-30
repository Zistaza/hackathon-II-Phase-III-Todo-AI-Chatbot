'use client';

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

interface AnimatedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost' | 'link';
  size?: 'sm' | 'md' | 'lg';
}

const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  ...props
}) => {
  // Define variant classes
  const variantClasses = {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90 active:bg-primary/80',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 active:bg-secondary/70',
    danger: 'bg-destructive text-destructive-foreground hover:bg-destructive/90 active:bg-destructive/80',
    outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground active:bg-accent/90',
    ghost: 'hover:bg-accent hover:text-accent-foreground active:bg-accent/90',
    link: 'underline-offset-4 hover:underline text-primary',
  };

  const baseClasses =
    'inline-flex items-center justify-center font-medium ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 whitespace-nowrap transition-all duration-200';

  const sizeClasses = {
    sm: 'h-9 min-h-9 px-3 py-2 text-sm rounded-md',
    md: 'h-10 min-h-10 px-4 py-2 text-base rounded-lg',
    lg: 'h-12 min-h-12 px-6 py-3 text-lg rounded-xl',
  };

  const buttonClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  const prefersReducedMotion =
    typeof window !== 'undefined'
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
      : false;

  return (
    <motion.button
      // Cast props to HTMLMotionProps<'button'> to fix TS type error
      {...(props as HTMLMotionProps<'button'>)}
      whileHover={!prefersReducedMotion ? { scale: 1.03 } : {}}
      whileTap={!prefersReducedMotion ? { scale: 0.98 } : {}}
      className={buttonClasses}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if ((e.key === 'Enter' || e.key === ' ') && props.onClick) {
          e.preventDefault();
          // @ts-ignore - onClick exists in props
          props.onClick(e);
        }
      }}
    >
      {children}
    </motion.button>
  );
};

export default AnimatedButton;
