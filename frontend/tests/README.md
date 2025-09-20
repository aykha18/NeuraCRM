# CRM UI Regression Test Suite

This directory contains comprehensive UI regression tests for the NeuraCRM application. The test suite is built using Playwright and covers all major CRM modules with extensive test scenarios.

## 📁 Test Structure

```
tests/
├── README.md                     # This file
├── global.setup.ts              # Global test setup and authentication
├── regression.config.ts         # Playwright configuration for regression tests
├── test-helpers.ts              # Reusable test utilities and helpers
├── leads-management.spec.ts     # Lead Management module tests
├── contacts-management.spec.ts  # Contact Management module tests (to be created)
├── deals-pipeline.spec.ts       # Deal Pipeline module tests (to be created)
├── dashboard.spec.ts            # Dashboard module tests (to be created)
├── chat-messaging.spec.ts       # Chat/Messaging module tests (to be created)
├── customer-support.spec.ts     # Customer Support module tests (existing)
├── visual/                      # Visual regression tests
├── performance/                 # Performance tests
├── smoke/                       # Smoke tests for critical paths
└── .storage/                    # Authentication storage
```

## 🎯 Test Coverage

### Lead Management Module ✅ COMPLETE
- **Page Layout & Navigation**: Header, buttons, responsive design
- **Lead Creation**: Modal forms, validation, API integration
- **Lead Listing**: Table display, data integrity, pagination
- **Search & Filtering**: Text search, status filters, score filters
- **Sorting**: Column sorting, sort indicators, data ordering
- **Lead Actions**: View, edit, delete, convert to deal
- **Inline Editing**: Click-to-edit, save/cancel, validation
- **Bulk Operations**: Select all, bulk delete, selection management
- **Lead Scoring**: Score calculation, analytics modal
- **Export Functions**: CSV and Excel export
- **Error Handling**: API failures, network errors
- **Accessibility**: ARIA labels, keyboard navigation
- **Performance**: Load times, responsiveness

### Modules To Be Implemented
- **Contact Management**: CRUD operations, company associations
- **Deal Pipeline**: Kanban board, stage management, deal progression
- **Dashboard**: Analytics widgets, real-time updates, KPIs
- **Chat/Messaging**: Real-time chat, room management, message history
- **Customer Support**: Ticket management, knowledge base
- **Email Automation**: Campaign management, template editing
- **Financial Management**: Invoicing, payments, revenue tracking
- **User Management**: Roles, permissions, organization settings

## 🚀 Running Tests

### Prerequisites
```bash
# Install dependencies
npm install

# Ensure the application is running
npm run dev  # Frontend on http://localhost:5173
python main.py  # Backend on http://localhost:8000
```

### Basic Test Execution
```bash
# Run all regression tests
npx playwright test --config=tests/regression.config.ts

# Run specific module tests
npx playwright test tests/leads-management.spec.ts

# Run tests in headed mode (see browser)
npx playwright test --headed

# Run tests in specific browser
npx playwright test --project=chromium-desktop

# Run tests with debug mode
npx playwright test --debug
```

### Test Categories
```bash
# Smoke tests (critical functionality only)
npx playwright test --config=tests/regression.config.ts --grep="@smoke"

# Visual regression tests
npx playwright test tests/visual/ --config=tests/regression.config.ts

# Performance tests
npx playwright test tests/performance/ --config=tests/regression.config.ts

# Mobile responsive tests
npx playwright test --project=mobile-chrome

# Cross-browser tests
npx playwright test --project=chromium-desktop --project=firefox-desktop --project=webkit-desktop
```

### Continuous Integration
```bash
# CI-optimized test run
CI=true npx playwright test --config=tests/regression.config.ts

# Generate test report
npx playwright show-report test-results/html-report
```

## 📊 Test Reports

After running tests, reports are generated in multiple formats:

- **HTML Report**: `test-results/html-report/index.html` - Interactive report with screenshots
- **JSON Report**: `test-results/results.json` - Machine-readable results
- **JUnit Report**: `test-results/junit.xml` - For CI/CD integration

```bash
# View HTML report
npx playwright show-report

# Open specific report
open test-results/html-report/index.html
```

## 🔧 Test Configuration

### Environment Variables
```bash
# Application URLs
BASE_URL=http://localhost:5173          # Frontend URL
API_BASE_URL=http://localhost:8000      # Backend API URL

# Test execution
CI=true                                 # Enable CI mode
HEADLESS=true                          # Run in headless mode
WORKERS=2                              # Number of parallel workers

# Authentication
TEST_EMAIL=nodeit@node.com             # Test user email
TEST_PASSWORD=NodeIT2024!              # Test user password
```

### Browser Configuration
The test suite runs on multiple browsers and devices:
- **Desktop**: Chrome, Firefox, Safari (WebKit)
- **Mobile**: Chrome on Android, Safari on iOS
- **Tablet**: iPad Pro
- **Screen Sizes**: 1366x768, 1920x1080, 2560x1440
- **Special Modes**: Dark mode, slow network simulation

## 🧪 Writing New Tests

### Test Structure Template
```typescript
import { test, expect } from '@playwright/test';
import { TestHelpers, CRMAssertions } from './test-helpers';

test.describe('Module Name', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/module-path');
    await TestHelpers.waitForLoadingComplete(page);
  });

  test.describe('Feature Group', () => {
    
    test('should perform specific action', async ({ page }) => {
      // Arrange
      const testData = TestHelpers.generateTestData('Test');
      
      // Act
      await page.getByRole('button', { name: /action/i }).click();
      
      // Assert
      await expect(page.getByText(/expected result/i)).toBeVisible();
    });
  });
});
```

### Best Practices

1. **Use Page Object Model** for complex pages
2. **Wait for API responses** before assertions
3. **Use semantic selectors** (roles, labels) over CSS selectors
4. **Test error scenarios** and edge cases
5. **Include accessibility checks** in all tests
6. **Test responsive behavior** on different screen sizes
7. **Use test data generators** for consistent test data
8. **Clean up test data** after tests complete

### Helper Functions
```typescript
// Wait for API response
await TestHelpers.waitForApiResponse(page, '/api/leads', 'POST');

// Fill form with validation
await TestHelpers.fillForm(page, {
  'Title': 'Test Lead',
  'Status': 'qualified'
});

// Check toast message
await TestHelpers.expectToastMessage(page, /success/i);

// Test responsive design
await TestHelpers.testResponsiveDesign(page, async (viewport) => {
  // Test logic for each viewport
});

// Custom CRM assertions
await CRMAssertions.expectLeadScore(page, 85);
await CRMAssertions.expectStatusBadge(page, 'qualified', 'bg-green');
```

## 🐛 Debugging Tests

### Debug Mode
```bash
# Run single test in debug mode
npx playwright test tests/leads-management.spec.ts --debug

# Debug specific test
npx playwright test --debug --grep="should create a new lead"
```

### Screenshots and Videos
- **Screenshots**: Automatically captured on failure
- **Videos**: Recorded for failed tests
- **Traces**: Full interaction traces for debugging

### Common Issues

1. **Timing Issues**: Use `waitFor` methods instead of `setTimeout`
2. **Element Not Found**: Check if element is in viewport or loaded
3. **API Failures**: Verify backend is running and accessible
4. **Authentication**: Ensure global setup completed successfully
5. **Flaky Tests**: Add proper waits and retry logic

## 📈 Performance Testing

### Metrics Tracked
- **Page Load Time**: < 5 seconds
- **API Response Time**: < 2 seconds
- **Time to Interactive**: < 3 seconds
- **Memory Usage**: Monitor for leaks
- **Network Requests**: Optimize bundle size

### Performance Tests
```typescript
test('should load page within acceptable time', async ({ page }) => {
  const { loadTime, isAcceptable } = await PerformanceHelpers.measurePageLoad(page, '/leads');
  expect(isAcceptable).toBeTruthy();
  expect(loadTime).toBeLessThan(5000);
});
```

## 🔒 Security Testing

### Areas Covered
- **Authentication**: Login/logout flows
- **Authorization**: Role-based access control
- **Data Validation**: Input sanitization
- **XSS Prevention**: Script injection attempts
- **CSRF Protection**: Cross-site request forgery

## 📱 Mobile Testing

### Responsive Breakpoints
- **Mobile**: 375px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px+

### Mobile-Specific Tests
- Touch interactions
- Swipe gestures
- Orientation changes
- Mobile navigation patterns

## 🎨 Visual Regression Testing

### Screenshot Comparison
```typescript
test('should match visual baseline', async ({ page }) => {
  await page.goto('/leads');
  await expect(page).toHaveScreenshot('leads-page.png');
});
```

### Visual Test Guidelines
- Use consistent viewport sizes
- Wait for animations to complete
- Hide dynamic content (timestamps, etc.)
- Test both light and dark themes

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: UI Regression Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install
      - run: npm run test:regression
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

## 📋 Test Checklist

Before deploying, ensure all tests pass:

- [ ] **Smoke Tests**: Critical user journeys work
- [ ] **Regression Tests**: No existing functionality broken
- [ ] **Cross-Browser**: Works in Chrome, Firefox, Safari
- [ ] **Mobile**: Responsive design functions correctly
- [ ] **Performance**: Load times within acceptable limits
- [ ] **Accessibility**: WCAG compliance maintained
- [ ] **Visual**: No unintended UI changes

## 🤝 Contributing

### Adding New Tests
1. Create test file following naming convention: `module-name.spec.ts`
2. Use existing helpers and patterns
3. Include comprehensive test scenarios
4. Add documentation for complex test logic
5. Ensure tests are deterministic and not flaky

### Test Review Criteria
- **Coverage**: All major user flows tested
- **Reliability**: Tests pass consistently
- **Maintainability**: Clear, readable test code
- **Performance**: Tests run efficiently
- **Documentation**: Well-documented test scenarios

## 📞 Support

For questions about the test suite:
1. Check this documentation
2. Review existing test examples
3. Check Playwright documentation
4. Contact the development team

---

**Last Updated**: January 2024  
**Test Suite Version**: 1.0.0  
**Playwright Version**: Latest