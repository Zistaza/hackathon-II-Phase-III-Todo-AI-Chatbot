'use client';

import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}

interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {}

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Card: React.FC<CardProps> = ({ className = '', ...props }) => (
  <div
    className={`rounded-2xl border bg-card text-card-foreground shadow-lg ${className}`}
    {...props}
  />
);

export const CardHeader: React.FC<CardHeaderProps> = ({ className = '', ...props }) => (
  <div className={`flex flex-col space-y-2 p-8 pb-6 ${className}`} {...props} />
);

export const CardTitle: React.FC<CardTitleProps> = ({ className = '', ...props }) => (
  <h3 className={`font-bold leading-tight tracking-tight text-xl sm:text-2xl ${className}`} {...props} />
);

export const CardDescription: React.FC<CardDescriptionProps> = ({ className = '', ...props }) => (
  <p className={`text-base text-muted-foreground ${className}`} {...props} />
);

export const CardContent: React.FC<CardContentProps> = ({ className = '', ...props }) => (
  <div className={`p-8 pt-2 ${className}`} {...props} />
);

export const CardFooter: React.FC<CardFooterProps> = ({ className = '', ...props }) => (
  <div className={`flex items-center p-8 pt-2 ${className}`} {...props} />
);