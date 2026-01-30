// Task service for handling todo API calls

import { apiInstance, API_BASE_URL } from '../lib/api';
import { Task, TaskCreate, TaskUpdate } from '../types';
import axios from 'axios';
import { getCookie, removeCookie } from '../lib/cookies';

// Get the current user ID from cookies
const getCurrentUserId = (): string | null => {
  const userDataStr = getCookie('userData');
  if (userDataStr) {
    try {
      // Try parsing directly first
      let user;
      try {
        user = JSON.parse(userDataStr);
      } catch {
        // If direct parsing fails, try decoding first
        user = JSON.parse(decodeURIComponent(userDataStr));
      }

      // Validate that the user object has an id property
      if (!user || !user.id || typeof user.id !== 'string' || user.id.trim() === '') {
        console.error('Invalid user data in cookie - missing or invalid id:', user);
        return null;
      }

      console.log('Retrieved user ID:', user.id); // Debug log
      return user.id.trim();
    } catch (error) {
      console.error('Failed to parse user data from cookie:', error);
      return null;
    }
  }
  console.log('No userData cookie found'); // Debug log
  return null;
};

export const todoService = {
  // Get all tasks for the authenticated user
  getTasks: async (): Promise<Task[]> => {
    const userId = getCurrentUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    try {
      // Validate user ID format (should be a UUID-like string and URL-safe)
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      // Log for debugging
      console.log('Fetching tasks for userId:', userId);

      // Construct the full URL for debugging - apiInstance already includes /api prefix
      const url = `/${userId}/tasks`;
      console.log('Making request to URL:', url);

      // Make sure the URL starts with a slash for relative path
      const normalizedUrl = url.startsWith('/') ? url : `/${url}`;
      const response = await apiInstance.get<Task[]>(normalizedUrl);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching tasks:', error);
      console.error('Full error response:', error.response);
      console.error('Error code:', error.code);
      console.error('Request URL:', error.config?.url);
      console.error('Request method:', error.config?.method);

      // Check if it's a 401 error specifically
      if (error.response?.status === 401) {
        // Clear auth cookies and localStorage
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }

      // Check if it's a 404 error
      if (error.response?.status === 404) {
        console.error('404 error - User ID may be invalid or user does not exist:', userId);
        // This might indicate that the user account was deleted or the ID is incorrect
        // For safety, clear auth data and redirect to login
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('User account not found. Please log in again.');
      }

      // Provide more detailed error information for debugging
      const errorMessage = error.response?.data?.message || error.message || 'Failed to fetch tasks';
      const errorDetails = {
        message: errorMessage,
        code: error.code,
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        response_data: error.response?.data
      };

      console.error('Detailed error information:', errorDetails);
      throw new Error(errorMessage);
    }
  },

  // Create a new task
  createTask: async (taskData: TaskCreate): Promise<Task> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for task creation:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      const response = await apiInstance.post<Task>(`/${userId}/tasks`, taskData);
      return response.data;
    } catch (error: any) {
      console.error('Error creating task:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.message || error.message || 'Failed to create task');
    }
  },

  // Get a specific task by ID
  getTaskById: async (taskId: string): Promise<Task> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for getting task:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      const response = await apiInstance.get<Task>(`/${userId}/tasks/${taskId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching task by ID:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.message || error.message || 'Failed to fetch task');
    }
  },

  // Update a task
  updateTask: async (taskId: string, taskData: TaskUpdate): Promise<Task> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for updating task:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      const response = await apiInstance.put<Task>(`/${userId}/tasks/${taskId}`, taskData);
      return response.data;
    } catch (error: any) {
      console.error('Error updating task:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.message || error.message || 'Failed to update task');
    }
  },

  // Delete a task
  deleteTask: async (taskId: string): Promise<void> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for deleting task:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      await apiInstance.delete(`/${userId}/tasks/${taskId}`);
    } catch (error: any) {
      console.error('Delete task error:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.detail || error.response?.data?.message || 'Failed to delete task');
    }
  },

  // Toggle task completion status
  toggleTaskCompletion: async (taskId: string): Promise<{ id: string; completed: boolean; message: string }> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for toggling task completion:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      const response = await apiInstance.patch(`/${userId}/tasks/${taskId}/complete`);
      return response.data;
    } catch (error: any) {
      console.error('Error toggling task completion:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.message || error.message || 'Failed to toggle task completion');
    }
  },
};