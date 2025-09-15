import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { API_BASE_URL } from '../config';

interface User {
  id: number;
  name: string;
  email: string;
  role?: string;
  organization_id?: number;
  created_at?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (name: string, email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!token;

  // Check for existing token on app load
  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
      // Verify token is not expired (basic check)
      try {
        const payload = JSON.parse(atob(storedToken.split('.')[1]));
        const currentTime = Date.now() / 1000;
        if (payload.exp && payload.exp < currentTime) {
          // Token is expired, remove it
          localStorage.removeItem('access_token');
          setIsLoading(false);
          return;
        }
      } catch (error) {
        // Invalid token format, remove it
        localStorage.removeItem('access_token');
        setIsLoading(false);
        return;
      }
      
      setToken(storedToken);
      // Verify token and get user info
      fetchUserInfo(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserInfo = async (authToken: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token is invalid, remove it
        localStorage.removeItem('access_token');
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      // Silent fail: reset auth state
      localStorage.removeItem('access_token');
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const { access_token } = data;
        
        localStorage.setItem('access_token', access_token);
        setToken(access_token);
        
        // Fetch user info
        await fetchUserInfo(access_token);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      if (response.ok) {
        // Registration successful, now login
        await login(email, password);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
    register,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
