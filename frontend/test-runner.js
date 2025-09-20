#!/usr/bin/env node

/**
 * CRM UI Test Runner
 * 
 * Convenient script to run different types of UI regression tests
 * with proper configuration and reporting.
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// ANSI color codes for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

// Test configurations
const testConfigs = {
  regression: {
    name: 'Full Regression Suite',
    config: 'tests/regression.config.ts',
    description: 'Complete UI regression tests for all modules'
  },
  smoke: {
    name: 'Smoke Tests',
    config: 'tests/regression.config.ts',
    grep: '@smoke',
    description: 'Critical functionality tests only'
  },
  leads: {
    name: 'Lead Management Tests',
    config: 'tests/regression.config.ts',
    testMatch: 'tests/leads-management.spec.ts',
    description: 'Lead management module tests'
  },
  mobile: {
    name: 'Mobile Responsive Tests',
    config: 'tests/regression.config.ts',
    project: 'mobile-chrome',
    description: 'Mobile device compatibility tests'
  },
  crossbrowser: {
    name: 'Cross-Browser Tests',
    config: 'tests/regression.config.ts',
    project: 'chromium-desktop,firefox-desktop,webkit-desktop',
    description: 'Multi-browser compatibility tests'
  },
  visual: {
    name: 'Visual Regression Tests',
    config: 'tests/regression.config.ts',
    testMatch: 'tests/visual/**/*.spec.ts',
    description: 'Screenshot comparison tests'
  },
  performance: {
    name: 'Performance Tests',
    config: 'tests/regression.config.ts',
    testMatch: 'tests/performance/**/*.spec.ts',
    description: 'Load time and performance tests'
  }
};

// Utility functions
function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logHeader(message) {
  log('\n' + '='.repeat(60), 'cyan');
  log(`  ${message}`, 'bright');
  log('='.repeat(60), 'cyan');
}

function logSuccess(message) {
  log(`✅ ${message}`, 'green');
}

function logError(message) {
  log(`❌ ${message}`, 'red');
}

function logWarning(message) {
  log(`⚠️  ${message}`, 'yellow');
}

function logInfo(message) {
  log(`ℹ️  ${message}`, 'blue');
}

// Check if required files exist
function checkPrerequisites() {
  const requiredFiles = [
    'package.json',
    'tests/global.setup.ts',
    'tests/regression.config.ts'
  ];

  const missingFiles = requiredFiles.filter(file => !fs.existsSync(file));
  
  if (missingFiles.length > 0) {
    logError('Missing required files:');
    missingFiles.forEach(file => log(`  - ${file}`, 'red'));
    return false;
  }
  
  return true;
}

// Check if application is running
async function checkApplicationStatus() {
  logInfo('Checking application status...');
  
  const frontendUrl = process.env.BASE_URL || 'http://localhost:5173';
  const backendUrl = process.env.API_BASE_URL || 'http://localhost:8000';
  
  try {
    // Simple check - in a real implementation, you'd make HTTP requests
    logSuccess(`Frontend expected at: ${frontendUrl}`);
    logSuccess(`Backend expected at: ${backendUrl}`);
    logWarning('Make sure both frontend and backend are running before starting tests');
    return true;
  } catch (error) {
    logError('Application health check failed');
    return false;
  }
}

// Run Playwright command
function runPlaywright(args) {
  return new Promise((resolve, reject) => {
    const playwrightCmd = process.platform === 'win32' ? 'npx.cmd' : 'npx';
    const fullArgs = ['playwright', 'test', ...args];
    
    log(`\nExecuting: ${playwrightCmd} ${fullArgs.join(' ')}`, 'cyan');
    
    const child = spawn(playwrightCmd, fullArgs, {
      stdio: 'inherit',
      shell: true
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        resolve(code);
      } else {
        reject(new Error(`Playwright exited with code ${code}`));
      }
    });
    
    child.on('error', (error) => {
      reject(error);
    });
  });
}

// Build Playwright arguments based on configuration
function buildPlaywrightArgs(config, options = {}) {
  const args = [];
  
  // Configuration file
  if (config.config) {
    args.push('--config', config.config);
  }
  
  // Test pattern matching
  if (config.testMatch) {
    args.push(config.testMatch);
  }
  
  // Grep pattern
  if (config.grep || options.grep) {
    args.push('--grep', config.grep || options.grep);
  }
  
  // Project selection
  if (config.project || options.project) {
    const projects = (config.project || options.project).split(',');
    projects.forEach(project => {
      args.push('--project', project.trim());
    });
  }
  
  // Additional options
  if (options.headed) args.push('--headed');
  if (options.debug) args.push('--debug');
  if (options.ui) args.push('--ui');
  if (options.reporter) args.push('--reporter', options.reporter);
  if (options.workers) args.push('--workers', options.workers);
  if (options.retries) args.push('--retries', options.retries);
  if (options.timeout) args.push('--timeout', options.timeout);
  
  return args;
}

// Generate test report
async function generateReport() {
  logInfo('Generating test report...');
  
  try {
    await runPlaywright(['show-report', '--host', '0.0.0.0']);
  } catch (error) {
    logWarning('Could not open report automatically');
    logInfo('View report manually: npx playwright show-report');
  }
}

// Main test execution function
async function runTests(testType, options = {}) {
  const config = testConfigs[testType];
  
  if (!config) {
    logError(`Unknown test type: ${testType}`);
    logInfo('Available test types:');
    Object.keys(testConfigs).forEach(key => {
      log(`  ${key}: ${testConfigs[key].description}`, 'yellow');
    });
    return false;
  }
  
  logHeader(`Running ${config.name}`);
  log(config.description, 'blue');
  
  // Check prerequisites
  if (!checkPrerequisites()) {
    return false;
  }
  
  // Check application status
  await checkApplicationStatus();
  
  try {
    // Build and execute Playwright command
    const args = buildPlaywrightArgs(config, options);
    await runPlaywright(args);
    
    logSuccess(`${config.name} completed successfully!`);
    
    // Generate report if requested
    if (options.report) {
      await generateReport();
    }
    
    return true;
    
  } catch (error) {
    logError(`${config.name} failed: ${error.message}`);
    return false;
  }
}

// CLI interface
function showHelp() {
  logHeader('CRM UI Test Runner');
  
  log('\nUsage:', 'bright');
  log('  node test-runner.js <test-type> [options]');
  
  log('\nTest Types:', 'bright');
  Object.entries(testConfigs).forEach(([key, config]) => {
    log(`  ${key.padEnd(15)} ${config.description}`, 'yellow');
  });
  
  log('\nOptions:', 'bright');
  log('  --headed         Run tests in headed mode (show browser)');
  log('  --debug          Run tests in debug mode');
  log('  --ui             Run tests with Playwright UI');
  log('  --report         Open test report after completion');
  log('  --project <name> Run tests on specific project/browser');
  log('  --grep <pattern> Run tests matching pattern');
  log('  --workers <num>  Number of parallel workers');
  log('  --retries <num>  Number of retries for failed tests');
  log('  --timeout <ms>   Test timeout in milliseconds');
  log('  --reporter <type> Reporter type (html, json, junit)');
  
  log('\nExamples:', 'bright');
  log('  node test-runner.js regression --headed --report');
  log('  node test-runner.js leads --debug');
  log('  node test-runner.js smoke --project chromium-desktop');
  log('  node test-runner.js crossbrowser --workers 1');
  
  log('\nEnvironment Variables:', 'bright');
  log('  BASE_URL         Frontend application URL (default: http://localhost:5173)');
  log('  API_BASE_URL     Backend API URL (default: http://localhost:8000)');
  log('  CI               Enable CI mode (default: false)');
  log('  HEADLESS         Run in headless mode (default: true in CI)');
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    showHelp();
    return null;
  }
  
  const testType = args[0];
  const options = {};
  
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    
    if (arg.startsWith('--')) {
      const key = arg.substring(2);
      
      // Boolean flags
      if (['headed', 'debug', 'ui', 'report'].includes(key)) {
        options[key] = true;
      }
      // Value flags
      else if (['project', 'grep', 'workers', 'retries', 'timeout', 'reporter'].includes(key)) {
        options[key] = args[++i];
      }
    }
  }
  
  return { testType, options };
}

// Main execution
async function main() {
  const parsed = parseArgs();
  
  if (!parsed) {
    process.exit(0);
  }
  
  const { testType, options } = parsed;
  
  // Set environment variables if not already set
  if (!process.env.BASE_URL) {
    process.env.BASE_URL = 'http://localhost:5173';
  }
  if (!process.env.API_BASE_URL) {
    process.env.API_BASE_URL = 'http://localhost:8000';
  }
  
  const success = await runTests(testType, options);
  
  if (success) {
    logSuccess('\n🎉 All tests completed successfully!');
    process.exit(0);
  } else {
    logError('\n💥 Tests failed or encountered errors');
    process.exit(1);
  }
}

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  logError(`Uncaught exception: ${error.message}`);
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  logError(`Unhandled rejection: ${reason}`);
  process.exit(1);
});

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    logError(`Fatal error: ${error.message}`);
    process.exit(1);
  });
}

module.exports = {
  runTests,
  testConfigs,
  checkPrerequisites,
  checkApplicationStatus
};