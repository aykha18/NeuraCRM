// API Configuration - Dynamic based on environment
// Check if we're running on Railway (production) - this takes priority over everything
const isRailway = typeof window !== 'undefined' && window.location.hostname === 'neuracrm.up.railway.app';

// Allow a runtime override via localStorage when running a built bundle served by the backend
// BUT NOT when running on Railway
const runtimeOverride = !isRailway && typeof window !== 'undefined' ? window.localStorage?.getItem('API_BASE_URL') : null;

// Default base URL: in dev use backend port 8000; in built/served bundles use current origin
const defaultBaseUrl = import.meta.env.DEV
  ? 'http://127.0.0.1:8000'
  : (typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8000');

export const API_BASE_URL = isRailway ? 'https://neuracrm.up.railway.app' :
  (runtimeOverride || import.meta.env.VITE_API_URL || defaultBaseUrl);

// Environment check
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;
