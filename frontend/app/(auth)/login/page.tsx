'use client';

import React from 'react';
import { LoginForm } from '../../../components/auth/login-form';

export default function LoginPage() {
  return (
    <div className="w-full max-w-lg mx-auto py-12 px-4">
      <div className="text-center mb-10">
        <h2 className="text-4xl font-bold text-foreground mb-4">
          Sign in to your account
        </h2>
        <p className="text-lg text-muted-foreground">
          Welcome back! Please enter your details to sign in.
        </p>
        <div className="mt-6">
          <a href="/" className="text-primary hover:text-primary/80 text-base font-medium inline-flex items-center gap-2">
            <span>←</span>
            <span>Back to Home</span>
          </a>
        </div>
      </div>
      <div className="bg-card border border-border rounded-2xl p-8 shadow-lg">
        <LoginForm />
      </div>
    </div>
  );
}