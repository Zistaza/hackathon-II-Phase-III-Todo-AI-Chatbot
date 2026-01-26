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
      localStorage.setItem(this.tokenKey, token);
    }
  }

  // Get stored JWT token
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(this.tokenKey);
    }
    return null;
  }

  // Remove token (logout)
  removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.tokenKey);
    }
  }

  // Store user profile
  setUserProfile(profile: UserProfile): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.userKey, JSON.stringify(profile));
    }
  }

  // Get stored user profile
  getUserProfile(): UserProfile | null {
    if (typeof window !== 'undefined') {
      const profileStr = localStorage.getItem(this.userKey);
      return profileStr ? JSON.parse(profileStr) : null;
    }
    return null;
  }

  // Remove user profile
  removeUserProfile(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.userKey);
    }
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