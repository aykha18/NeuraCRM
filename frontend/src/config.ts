// API Configuration - Dynamic based on environment
// Allow a runtime override via localStorage when running a built bundle served by the backend
const runtimeOverride = typeof window !== 'undefined' ? window.localStorage?.getItem('API_BASE_URL') : null;

// Check if we're running on Railway (production)
const isRailway = typeof window !== 'undefined' && window.location.hostname === 'neuracrm.up.railway.app';

export const API_BASE_URL = runtimeOverride || import.meta.env.VITE_API_URL || 
  (isRailway ? 'https://neuracrm.up.railway.app' : 'http://127.0.0.1:8000');

// Environment check
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;
