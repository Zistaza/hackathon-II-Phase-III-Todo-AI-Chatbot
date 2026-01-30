'use client';

import React from 'react';
import { RegisterForm } from '../../../components/auth/register-form';

export default function RegisterPage() {
  return (
    <div className="w-full max-w-lg mx-auto py-12 px-4">
      <div className="text-center mb-10">
        <h2 className="text-4xl font-bold text-foreground mb-4">
          Create a new account
        </h2>
        <p className="text-lg text-muted-foreground">
          Join us today! Please enter your details to create an account.
        </p>
        <div className="mt-6">
          <a href="/" className="text-primary hover:text-primary/80 text-base font-medium inline-flex items-center gap-2">
            <span>←</span>
            <span>Back to Home</span>
          </a>
        </div>
      </div>
      <div className="bg-card border border-border rounded-2xl p-8 shadow-lg">
        <RegisterForm />
      </div>
    </div>
  );
}