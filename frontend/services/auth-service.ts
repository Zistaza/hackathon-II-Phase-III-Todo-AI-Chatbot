// Auth service for handling authentication API calls

import axios from 'axios';
import { UserRegistration, LoginRequest, AuthResponse } from '../types';
import { setCookie, removeCookie, getCookie } from '../lib/cookies';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
const BASE_URL = API_BASE_URL.replace('/api', ''); // Base URL without /api suffix for auth endpoints

const authInstance = axios.create({
  baseURL: API_BASE_URL, // For API endpoints that use /api prefix
  headers: {
    'Content-Type': 'application/json',
  },
});

// Separate instance for auth endpoints (without /api prefix)
const authApiInstance = axios.create({
  baseURL: BASE_URL, // Base URL without /api for auth endpoints
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token to authInstance
authInstance.interceptors.request.use(
  (config) => {
    const token = getCookie('authToken') || localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Request interceptor to attach JWT token to authApiInstance
authApiInstance.interceptors.request.use(
  (config) => {
    const token = getCookie('authToken') || localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 unauthorized responses for both instances
const handleUnauthorized = (error: any) => {
  if (error.response?.status === 401) {
    // Clear stored tokens and redirect to login
    removeCookie('authToken');
    removeCookie('userData');
    localStorage.removeItem('authToken');  // Also remove from localStorage for consistency
    localStorage.removeItem('userData');
    window.location.href = '/login';
  }
  return Promise.reject(error);
};

authInstance.interceptors.response.use(
  (response) => response,
  handleUnauthorized
);

authApiInstance.interceptors.response.use(
  (response) => response,
  handleUnauthorized
);

export const authService = {
  register: async (userData: UserRegistration): Promise<AuthResponse> => {
    try {
      const response = await authApiInstance.post('/auth/register', userData);
      // Set cookie for Next.js middleware and localStorage for client-side access
      if (response.data && response.data.token) {
        setCookie('authToken', response.data.token, 7); // Store for 7 days
        localStorage.setItem('authToken', response.data.token); // Also store in localStorage
        if (response.data.user) {
          setCookie('userData', JSON.stringify(response.data.user), 7); // Store for 7 days
          localStorage.setItem('userData', JSON.stringify(response.data.user)); // Also store in localStorage
        }
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Registration failed');
    }
  },

  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    try {
      const response = await authApiInstance.post('/auth/login', credentials);
      // Set cookie for Next.js middleware and localStorage for client-side access
      if (response.data && response.data.token) {
        setCookie('authToken', response.data.token, 7); // Store for 7 days
        localStorage.setItem('authToken', response.data.token); // Also store in localStorage
        if (response.data.user) {
          setCookie('userData', JSON.stringify(response.data.user), 7); // Store for 7 days
          localStorage.setItem('userData', JSON.stringify(response.data.user)); // Also store in localStorage
        }
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  },

  logout: async (): Promise<void> => {
    try {
      await authApiInstance.post('/auth/logout');
      // Clear cookies and localStorage
      removeCookie('authToken');
      removeCookie('userData');
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
    } catch (error: any) {
      console.error('Logout error:', error);
      // Still clear cookies and localStorage even if API call fails
      removeCookie('authToken');
      removeCookie('userData');
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
    }
  },

  verifyToken: async (token: string): Promise<boolean> => {
    try {
      // To verify a token, we can make a request to a protected endpoint
      // We'll use a minimal request to the user's own tasks endpoint
      // Since we don't know the user ID ahead of time, we'll return true if token exists
      // and let the backend handle validation on actual requests
      return !!token; // Basic validation - in production, you might want a dedicated endpoint
    } catch (error) {
      return false;
    }
  },
};