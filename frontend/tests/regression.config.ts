import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for UI Regression Testing
 * 
 * This configuration is specifically optimized for comprehensive
 * UI regression testing of the CRM application.
 */

export default defineConfig({
  testDir: './tests',
  
  // Test execution settings
  timeout: 90_000, // Increased timeout for complex UI operations
  expect: { 
    timeout: 15_000, // Longer expect timeout for slow operations
    toHaveScreenshot: { threshold: 0.2 } // Allow slight visual differences
  },
  
  // Parallel execution
  fullyParallel: true,
  forbidOnly: !!process.env.CI, // Prevent .only in CI
  retries: process.env.CI ? 2 : 1, // Retry failed tests in CI
  workers: process.env.CI ? 2 : undefined, // Limit workers in CI
  
  // Reporting
  reporter: [
    ['html', { outputFolder: 'test-results/html-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list'] // Console output
  ],
  
  // Global setup
  globalSetup: './tests/global.setup.ts',
  
  // Default test settings
  use: {
    // Base URL
    baseURL: process.env.BASE_URL || 'http://localhost:8000',
    
    // Browser settings
    headless: process.env.CI ? true : false,
    viewport: { width: 1280, height: 720 },
    
    // Test artifacts
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Authentication
    storageState: './tests/.storage/state.json',
    
    // Network settings
    ignoreHTTPSErrors: true,
    
    // Timeouts
    actionTimeout: 10_000,
    navigationTimeout: 30_000,
    
    // Locale and timezone
    locale: 'en-US',
    timezoneId: 'America/New_York',
  },

  // Test projects for different browsers and scenarios
  projects: [
    // Desktop browsers
    {
      name: 'chromium-desktop',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
    },
    {
      name: 'firefox-desktop',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1920, height: 1080 }
      },
    },
    {
      name: 'webkit-desktop',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1920, height: 1080 }
      },
    },
    
    // Mobile browsers
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
    
    // Tablet
    {
      name: 'tablet',
      use: { ...devices['iPad Pro'] },
    },
    
    // Different screen sizes for responsive testing
    {
      name: 'small-desktop',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1366, height: 768 }
      },
    },
    {
      name: 'large-desktop',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 2560, height: 1440 }
      },
    },
    
    // Dark mode testing
    {
      name: 'dark-mode',
      use: {
        ...devices['Desktop Chrome'],
        colorScheme: 'dark',
      },
    },
    
    // Slow network simulation
    {
      name: 'slow-network',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--simulate-slow-network']
        }
      },
    }
  ],

  // Development server (if needed)
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },

  // Output directories
  outputDir: 'test-results/artifacts',
  
  // Global test patterns
  testMatch: [
    '**/*.spec.ts',
    '**/*.test.ts',
    '**/regression/**/*.ts'
  ],
  
  // Files to ignore
  testIgnore: [
    '**/node_modules/**',
    '**/dist/**',
    '**/build/**'
  ],
  
  // Metadata
  metadata: {
    'test-suite': 'CRM UI Regression Tests',
    'version': '1.0.0',
    'environment': process.env.NODE_ENV || 'development'
  }
});

// Export specific configurations for different test types
export const smokeTestConfig = defineConfig({
  testMatch: ['**/smoke/**/*.spec.ts'],
  timeout: 30_000,
  retries: 0,
  projects: [
    {
      name: 'smoke-chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ]
});

export const visualRegressionConfig = defineConfig({
  testMatch: ['**/visual/**/*.spec.ts'],
  expect: {
    toHaveScreenshot: { 
      threshold: 0.1,
      mode: 'strict'
    }
  },
  use: {
    screenshot: 'only-on-failure'
  }
});

export const performanceTestConfig = defineConfig({
  testMatch: ['**/performance/**/*.spec.ts'],
  timeout: 120_000,
  workers: 1, // Run performance tests sequentially
  projects: [
    {
      name: 'performance-chromium',
      use: { 
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--enable-precise-memory-info']
        }
      }
    }
  ]
});