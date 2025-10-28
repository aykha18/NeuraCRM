import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import App from './App.tsx'
import { captureUtmAttribution } from './utils/utm'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Capture UTM on first load
if (captureUtmAttribution) {
  try {
    captureUtmAttribution(window.location.href, document.referrer || '');
  } catch (error) {
    console.error('UTM capture failed:', error);
  }
}

// Add error boundary for React rendering
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

const rootElement = document.getElementById('root');
if (!rootElement) {
  console.error('Root element not found!');
  // Create a fallback element to show something
  const fallback = document.createElement('div');
  fallback.innerHTML = '<h1>NeuraCRM Loading...</h1><p>If this persists, please refresh the page.</p>';
  fallback.style.cssText = 'text-align: center; padding: 50px; font-family: Arial, sans-serif;';
  document.body.appendChild(fallback);
} else {
  try {
    console.log('Starting React app...');
    createRoot(rootElement).render(
      <StrictMode>
        <QueryClientProvider client={queryClient}>
          <App />
        </QueryClientProvider>
      </StrictMode>,
    );
    console.log('React app rendered successfully');
  } catch (error) {
    console.error('Failed to render React app:', error);
    rootElement.innerHTML = '<h1>Application Error</h1><p>Please refresh the page or contact support.</p>';
  }
}
