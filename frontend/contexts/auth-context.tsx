'use client';

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { User, AuthResponse } from '../types';
import { getCookie, setCookie, removeCookie } from '../lib/cookies';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthAction {
  type: string;
  payload?: any;
}

interface AuthContextType {
  state: AuthState;
  login: (authData: AuthResponse) => void;
  logout: () => void;
  register: (userData: User) => void;
  refreshToken: () => Promise<boolean>;
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Action types
const SET_USER = 'SET_USER';
const SET_TOKEN = 'SET_TOKEN';
const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
const LOGOUT = 'LOGOUT';
const SET_LOADING = 'SET_LOADING';

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case SET_USER:
      return {
        ...state,
        user: action.payload,
      };
    case SET_TOKEN:
      return {
        ...state,
        token: action.payload,
      };
    case LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    case LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
      };
    case SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      };
    default:
      return state;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing token on initial load
  useEffect(() => {
    // First check cookies (for server-side consistency)
    let token = getCookie('authToken');
    let userDataStr = getCookie('userData');

    // If not in cookies, fallback to localStorage
    if (!token) {
      token = localStorage.getItem('authToken');
    }
    if (!userDataStr) {
      userDataStr = localStorage.getItem('userData');
    }

    if (token && userDataStr) {
      try {
        const parsedUser = JSON.parse(userDataStr);
        dispatch({
          type: LOGIN_SUCCESS,
          payload: { token, user: parsedUser },
        });
      } catch (error) {
        console.error('Failed to parse stored user data:', error);
        // Clear both cookies and localStorage if there's an error
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        dispatch({ type: SET_LOADING, payload: false });
      }
    } else {
      dispatch({ type: SET_LOADING, payload: false });
    }
  }, []);

  const login = (authData: AuthResponse) => {
    const { token, user } = authData;

    setCookie('authToken', token, 7); // Store for 7 days
    setCookie('userData', JSON.stringify(user), 7); // Store for 7 days
    // Also store in localStorage for client-side access consistency
    localStorage.setItem('authToken', token);
    localStorage.setItem('userData', JSON.stringify(user));

    dispatch({
      type: LOGIN_SUCCESS,
      payload: { token, user },
    });
  };

  const logout = () => {
    removeCookie('authToken');
    removeCookie('userData');
    // Clear localStorage as well to ensure no user data remains
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');

    dispatch({ type: LOGOUT });
  };

  const register = (userData: User) => {
    // Registration will typically redirect to login, but we can set user if needed
    dispatch({
      type: SET_USER,
      payload: userData,
    });
  };

  const refreshToken = async (): Promise<boolean> => {
    // In a real implementation, you'd call your refresh token endpoint
    // For now, returning true to indicate success
    return true;
  };

  const value = {
    state,
    login,
    logout,
    register,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};