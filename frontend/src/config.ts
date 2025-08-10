// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://neuracrm-production.up.railway.app';

// Environment check
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;
