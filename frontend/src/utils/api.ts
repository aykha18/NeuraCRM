// API utility functions for authenticated requests
import { API_BASE_URL } from '../config';

// Get the current auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

// Make an authenticated API request
export const authenticatedFetch = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  return response;
};

// Generic API request function
export const apiRequest = async <T>(
  endpoint: string,
  optionsOrMethod: RequestInit | string = 'GET',
  data?: any
): Promise<T> => {
  let options: RequestInit;

  if (typeof optionsOrMethod === 'string') {
    // New calling pattern: apiRequest(endpoint, method, data)
    options = {
      method: optionsOrMethod,
    };
    if (data && optionsOrMethod !== 'GET') {
      options.body = JSON.stringify(data);
    }
  } else {
    // Old calling pattern: apiRequest(endpoint, options)
    options = optionsOrMethod;
  }

  const response = await authenticatedFetch(endpoint, options);
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed: ${response.status} ${errorText}`);
  }
  
  return response.json();
};
