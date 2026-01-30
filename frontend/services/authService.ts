// Define types for authentication
interface AuthResponse {
  token: string;
  userId: string;
  expiresAt: string;
}

interface UserProfile {
  id: string;
  email: string;
  name?: string;
}

class AuthService {
  private tokenKey = 'jwtToken';
  private userKey = 'userProfile';

  // Store JWT token
  setToken(token: string): void {
    if (typeof window !== 'undefined') {
      // Set in both localStorage and cookie for consistency
      localStorage.setItem(this.tokenKey, token);
      // Also set in cookie for server-side access
      this.setCookie('authToken', token, 7); // 7 days expiry
    }
  }

  // Get stored JWT token - check both cookie and localStorage
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      // First check cookie (for server-side consistency)
      const cookieToken = this.getCookie('authToken');
      if (cookieToken) {
        return cookieToken;
      }
      // Fallback to localStorage
      return localStorage.getItem(this.tokenKey);
    }
    return null;
  }

  // Remove token (logout) - remove from both cookie and localStorage
  removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.tokenKey);
      this.removeCookie('authToken');
    }
  }

  // Store user profile
  setUserProfile(profile: UserProfile): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.userKey, JSON.stringify(profile));
      // Also set in cookie for server-side access
      this.setCookie('userData', JSON.stringify(profile), 7); // 7 days expiry
    }
  }

  // Get stored user profile - check both cookie and localStorage
  getUserProfile(): UserProfile | null {
    if (typeof window !== 'undefined') {
      // First check cookie
      const cookieUserData = this.getCookie('userData');
      if (cookieUserData) {
        try {
          return JSON.parse(cookieUserData);
        } catch (e) {
          console.error('Error parsing cookie user data:', e);
        }
      }
      // Fallback to localStorage
      const profileStr = localStorage.getItem(this.userKey);
      return profileStr ? JSON.parse(profileStr) : null;
    }
    return null;
  }

  // Remove user profile - remove from both cookie and localStorage
  removeUserProfile(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.userKey);
      this.removeCookie('userData');
    }
  }

  // Helper method to set cookie
  private setCookie(name: string, value: string, days?: number) {
    let expires = '';
    if (days) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = `; expires=${date.toUTCString()}`;
    }
    document.cookie = `${name}=${value}${expires}; path=/; SameSite=Lax`;
  }

  // Helper method to get cookie
  private getCookie(name: string): string | null {
    const nameEQ = `${name}=`;
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  // Helper method to remove cookie
  private removeCookie(name: string) {
    document.cookie = `${name}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) {
      return false;
    }

    // Check if token is expired
    try {
      const payload = this.decodeToken(token);
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp > currentTime;
    } catch (error) {
      return false;
    }
  }

  // Decode JWT token to get payload
  private decodeToken(token: string): { exp: number; [key: string]: any } {
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid token');
    }

    const payload = parts[1];
    // Add padding if needed
    const paddedPayload = payload + '='.repeat((4 - (payload.length % 4)) % 4);
    const decodedPayload = atob(paddedPayload);
    return JSON.parse(decodedPayload);
  }

  // Get user ID from token
  getUserId(): string | null {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    try {
      const payload = this.decodeToken(token);
      return payload.userId || payload.sub || null;
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }

  // Refresh token (if refresh tokens are implemented)
  async refreshToken(): Promise<string | null> {
    // In a real implementation, you would make an API call to refresh the token
    // This is a simplified version that just returns the existing token if valid
    const token = this.getToken();
    if (token && this.isAuthenticated()) {
      return token;
    }

    // If token is expired, return null to trigger re-authentication
    return null;
  }

  // Logout function
  logout(): void {
    this.removeToken();
    this.removeUserProfile();
  }

  // Validate token format (basic check)
  isValidToken(token: string): boolean {
    const parts = token.split('.');
    return parts.length === 3;
  }
}

export default AuthService;