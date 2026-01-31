import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// Utility function to merge class names with tailwind classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Generate a unique ID
export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

// Format date as ISO string
export function formatDate(date: Date): string {
  return date.toISOString();
}

// Format timestamp for display
export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleString();
}

// Debounce function to limit how often a function is called
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return function debounced(this: any, ...args: Parameters<T>): void {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Deep clone an object
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== "object") return obj;
  if (obj instanceof Date) return new Date(obj.getTime()) as any;
  if (obj instanceof Array) return obj.map((item) => deepClone(item)) as any;
  const cloned: any = {};
  Object.keys(obj).forEach((key) => {
    cloned[key] = deepClone((obj as any)[key]);
  });
  return cloned;
}

// Check if running in browser
export function isBrowser(): boolean {
  return typeof window !== 'undefined';
}

// Get current user ID from various sources
export function getCurrentUserId(): string | null {
  if (!isBrowser()) return null;

  // Try to get from localStorage first
  const storedUserId = localStorage.getItem('userId');
  if (storedUserId) {
    return storedUserId;
  }

  // Try to get from JWT token
  const token = localStorage.getItem('jwtToken');
  if (token) {
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = parts[1];
        const paddedPayload = payload + '='.repeat((4 - (payload.length % 4)) % 4);
        const decodedPayload = atob(paddedPayload);
        const parsedPayload = JSON.parse(decodedPayload);
        return parsedPayload.userId || parsedPayload.sub || null;
      }
    } catch (error) {
      console.error('Error parsing JWT token:', error);
    }
  }

  // Return null if no user ID found
  return null;
}

// Sleep function for async delays
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Check if value is empty
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string' && value.trim() === '') return true;
  if (Array.isArray(value) && value.length === 0) return true;
  if (typeof value === 'object' && Object.keys(value).length === 0) return true;
  return false;
}

// Format bytes to human-readable format
export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Capitalize first letter of a string
export function capitalize(str: string): string {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Generate a random string of specified length
export function randomString(length: number): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// Check if a string is a valid URL
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch (error) {
    return false;
  }
}