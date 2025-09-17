// API Configuration - Dynamic based on environment
// Allow a runtime override via localStorage when running a built bundle served by the backend
const runtimeOverride = typeof window !== 'undefined' ? window.localStorage?.getItem('API_BASE_URL') : null;
export const API_BASE_URL = runtimeOverride || import.meta.env.VITE_API_URL || 
  (import.meta.env.DEV ? 'http://127.0.0.1:8000' : 'https://neuracrm.up.railway.app');

// Environment check
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;
