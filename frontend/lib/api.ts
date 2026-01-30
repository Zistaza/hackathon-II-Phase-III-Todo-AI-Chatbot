// Centralized API service with JWT integration

import axios from 'axios';

const API_BASE_URL = `${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api`;

const apiInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Import the cookie helper functions
import { getCookie, removeCookie } from './cookies';

// Request interceptor to attach JWT token
apiInstance.interceptors.request.use(
  (config) => {
    const token = getCookie('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 unauthorized responses
apiInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stored tokens and redirect to login
      removeCookie('authToken');
      removeCookie('userData');
      // Also clear localStorage for consistency
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export { apiInstance, API_BASE_URL };