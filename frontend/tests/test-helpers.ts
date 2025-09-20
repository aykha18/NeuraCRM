/**
 * Test Helper Utilities for CRM UI Regression Tests
 * 
 * This file contains reusable helper functions and utilities
 * for consistent testing across all CRM modules.
 */

import { Page, expect, Locator } from '@playwright/test';

export class TestHelpers {
  
  /**
   * Wait for API response with timeout and error handling
   */
  static async waitForApiResponse(
    page: Page, 
    urlPattern: string | RegExp, 
    method: string = 'GET',
    timeout: number = 10000
  ) {
    return page.waitForResponse(
      response => {
        const url = response.url();
        const matchesUrl = typeof urlPattern === 'string' 
          ? url.includes(urlPattern)
          : urlPattern.test(url);
        return matchesUrl && response.request().method().toLowerCase() === method.toLowerCase();
      },
      { timeout }
    );
  }

  /**
   * Wait for element to be visible with retry logic
   */
  static async waitForElement(
    page: Page, 
    selector: string, 
    timeout: number = 10000
  ): Promise<Locator> {
    const element = page.locator(selector);
    await expect(element).toBeVisible({ timeout });
    return element;
  }

  /**
   * Fill form fields with validation
   */
  static async fillForm(page: Page, formData: Record<string, string>) {
    for (const [field, value] of Object.entries(formData)) {
      const input = page.getByLabel(new RegExp(field, 'i'));
      await expect(input).toBeVisible();
      await input.fill(value);
      
      // Verify the value was set
      if (await input.getAttribute('type') !== 'password') {
        await expect(input).toHaveValue(value);
      }
    }
  }

  /**
   * Select option from dropdown with validation
   */
  static async selectOption(page: Page, labelPattern: string | RegExp, value: string) {
    const select = page.getByLabel(labelPattern);
    await expect(select).toBeVisible();
    await select.selectOption(value);
    await expect(select).toHaveValue(value);
  }

  /**
   * Check if toast/notification message appears
   */
  static async expectToastMessage(page: Page, messagePattern: string | RegExp, timeout: number = 5000) {
    const toast = page.locator('[class*="toast"], [role="alert"], [class*="notification"]')
      .filter({ hasText: messagePattern });
    await expect(toast).toBeVisible({ timeout });
    return toast;
  }

  /**
   * Wait for loading state to complete
   */
  static async waitForLoadingComplete(page: Page, timeout: number = 10000) {
    // Wait for common loading indicators to disappear
    const loadingSelectors = [
      '[class*="loading"]',
      '[class*="spinner"]',
      'text=/loading/i',
      '[aria-label*="loading"]'
    ];

    for (const selector of loadingSelectors) {
      try {
        await page.waitForSelector(selector, { state: 'hidden', timeout: 2000 });
      } catch {
        // Ignore if selector doesn't exist
      }
    }

    // Wait for network to be idle
    await page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Take screenshot with timestamp for debugging
   */
  static async takeDebugScreenshot(page: Page, name: string) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await page.screenshot({ 
      path: `test-results/debug-${name}-${timestamp}.png`,
      fullPage: true 
    });
  }

  /**
   * Check table data integrity
   */
  static async validateTableData(page: Page, expectedColumns: string[]) {
    // Check table exists
    const table = page.locator('table');
    await expect(table).toBeVisible();

    // Check headers
    for (const column of expectedColumns) {
      await expect(page.getByRole('columnheader', { name: new RegExp(column, 'i') })).toBeVisible();
    }

    // Check if table has data rows
    const rows = page.locator('tbody tr');
    const rowCount = await rows.count();
    
    return {
      table,
      rows,
      rowCount,
      hasData: rowCount > 0
    };
  }

  /**
   * Validate form submission with API response
   */
  static async submitFormAndValidate(
    page: Page,
    submitButtonSelector: string,
    apiEndpoint: string,
    method: string = 'POST',
    expectedSuccessMessage?: string | RegExp
  ) {
    // Set up API response listener
    const responsePromise = this.waitForApiResponse(page, apiEndpoint, method);
    
    // Submit form
    await page.locator(submitButtonSelector).click();
    
    // Wait for API response
    const response = await responsePromise;
    expect(response.status()).toBeLessThan(300);
    
    // Check success message if provided
    if (expectedSuccessMessage) {
      await this.expectToastMessage(page, expectedSuccessMessage);
    }
    
    return response;
  }

  /**
   * Test responsive design at different viewport sizes
   */
  static async testResponsiveDesign(page: Page, testCallback: (viewport: string) => Promise<void>) {
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ];

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.waitForTimeout(500); // Allow layout to settle
      await testCallback(viewport.name);
    }
  }

  /**
   * Validate accessibility basics
   */
  static async checkBasicAccessibility(page: Page) {
    // Check for main heading
    const headings = page.locator('h1, h2, h3, [role="heading"]');
    expect(await headings.count()).toBeGreaterThan(0);

    // Check for proper button labels
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < Math.min(buttonCount, 10); i++) { // Check first 10 buttons
      const button = buttons.nth(i);
      const hasText = await button.textContent();
      const hasAriaLabel = await button.getAttribute('aria-label');
      const hasTitle = await button.getAttribute('title');
      
      expect(hasText || hasAriaLabel || hasTitle).toBeTruthy();
    }

    // Check for form labels
    const inputs = page.locator('input[type="text"], input[type="email"], input[type="password"], textarea, select');
    const inputCount = await inputs.count();
    
    for (let i = 0; i < Math.min(inputCount, 5); i++) { // Check first 5 inputs
      const input = inputs.nth(i);
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const placeholder = await input.getAttribute('placeholder');
      
      if (id) {
        const label = page.locator(`label[for="${id}"]`);
        const hasLabel = await label.count() > 0;
        expect(hasLabel || ariaLabel || placeholder).toBeTruthy();
      }
    }
  }

  /**
   * Generate test data with timestamp
   */
  static generateTestData(prefix: string = 'Test') {
    const timestamp = Date.now();
    return {
      title: `${prefix} Lead ${timestamp}`,
      company: `${prefix} Company ${timestamp}`,
      email: `test${timestamp}@example.com`,
      phone: `+1-555-${timestamp.toString().slice(-7)}`,
      description: `Test description created at ${new Date().toISOString()}`,
      timestamp
    };
  }

  /**
   * Clean up test data (for teardown)
   */
  static async cleanupTestData(page: Page, identifiers: string[]) {
    // This would typically make API calls to clean up test data
    // For now, just log what would be cleaned up
    console.log('Cleanup test data:', identifiers);
  }

  /**
   * Validate API error handling
   */
  static async testApiErrorHandling(
    page: Page, 
    apiEndpoint: string, 
    triggerAction: () => Promise<void>,
    expectedErrorMessage?: string | RegExp
  ) {
    // Intercept API and make it fail
    await page.route(`**${apiEndpoint}`, route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal Server Error' })
      });
    });

    // Trigger the action that should fail
    await triggerAction();

    // Check error message appears
    if (expectedErrorMessage) {
      const errorElement = page.locator('text=' + expectedErrorMessage.toString());
      await expect(errorElement).toBeVisible({ timeout: 5000 });
    }

    // Remove the route intercept
    await page.unroute(`**${apiEndpoint}`);
  }

  /**
   * Validate sorting functionality
   */
  static async testColumnSorting(
    page: Page, 
    columnName: string, 
    dataSelector: string = 'tbody tr'
  ) {
    const columnHeader = page.getByRole('columnheader', { name: new RegExp(columnName, 'i') });
    await expect(columnHeader).toBeVisible();

    // Get initial data
    const initialRows = await page.locator(dataSelector).count();
    if (initialRows < 2) return; // Need at least 2 rows to test sorting

    // Click to sort ascending
    await columnHeader.click();
    await page.waitForTimeout(500);

    // Verify sort indicator appears
    const sortIndicator = columnHeader.locator('svg, [class*="sort"], [class*="arrow"]');
    await expect(sortIndicator).toBeVisible();

    // Click again to sort descending
    await columnHeader.click();
    await page.waitForTimeout(500);

    // Sort indicator should still be visible
    await expect(sortIndicator).toBeVisible();
  }

  /**
   * Test pagination functionality
   */
  static async testPagination(page: Page) {
    const paginationContainer = page.locator('[class*="pagination"], [aria-label*="pagination"]');
    
    if (await paginationContainer.count() === 0) {
      console.log('No pagination found - likely not enough data');
      return;
    }

    await expect(paginationContainer).toBeVisible();

    // Test next page if available
    const nextButton = page.locator('button:has-text("Next"), button[aria-label*="next"]');
    if (await nextButton.count() > 0 && await nextButton.isEnabled()) {
      await nextButton.click();
      await this.waitForLoadingComplete(page);
    }

    // Test previous page if available
    const prevButton = page.locator('button:has-text("Previous"), button[aria-label*="previous"]');
    if (await prevButton.count() > 0 && await prevButton.isEnabled()) {
      await prevButton.click();
      await this.waitForLoadingComplete(page);
    }
  }
}

/**
 * Custom assertions for CRM-specific functionality
 */
export class CRMAssertions {
  
  static async expectLeadScore(page: Page, score: number, tolerance: number = 5) {
    const scoreElement = page.locator('[class*="score"], [data-testid*="score"]');
    await expect(scoreElement).toBeVisible();
    
    const scoreText = await scoreElement.textContent();
    const actualScore = parseInt(scoreText?.match(/\d+/)?.[0] || '0');
    
    expect(Math.abs(actualScore - score)).toBeLessThanOrEqual(tolerance);
  }

  static async expectStatusBadge(page: Page, status: string, colorClass?: string) {
    const statusBadge = page.locator(`[class*="rounded-full"]:has-text("${status}")`);
    await expect(statusBadge).toBeVisible();
    
    if (colorClass) {
      await expect(statusBadge).toHaveClass(new RegExp(colorClass));
    }
  }

  static async expectTableRowCount(page: Page, expectedCount: number, tolerance: number = 0) {
    const rows = page.locator('tbody tr');
    const actualCount = await rows.count();
    
    if (tolerance === 0) {
      expect(actualCount).toBe(expectedCount);
    } else {
      expect(Math.abs(actualCount - expectedCount)).toBeLessThanOrEqual(tolerance);
    }
  }

  static async expectFilteredResults(
    page: Page, 
    filterValue: string, 
    columnSelector: string
  ) {
    const rows = page.locator('tbody tr');
    const rowCount = await rows.count();
    
    if (rowCount === 0) return; // No results to check
    
    // Check first few rows contain the filter value
    for (let i = 0; i < Math.min(rowCount, 3); i++) {
      const cellText = await rows.nth(i).locator(columnSelector).textContent();
      expect(cellText?.toLowerCase()).toContain(filterValue.toLowerCase());
    }
  }
}

/**
 * Test data generators for different modules
 */
export class TestDataGenerator {
  
  static lead(overrides: Partial<any> = {}) {
    const timestamp = Date.now();
    return {
      title: `Test Lead ${timestamp}`,
      status: 'new',
      source: 'website',
      company: `Test Company ${timestamp}`,
      contact_name: `Test Contact ${timestamp}`,
      owner_id: 1,
      ...overrides
    };
  }

  static contact(overrides: Partial<any> = {}) {
    const timestamp = Date.now();
    return {
      name: `Test Contact ${timestamp}`,
      email: `test${timestamp}@example.com`,
      phone: `+1-555-${timestamp.toString().slice(-7)}`,
      company: `Test Company ${timestamp}`,
      ...overrides
    };
  }

  static deal(overrides: Partial<any> = {}) {
    const timestamp = Date.now();
    return {
      title: `Test Deal ${timestamp}`,
      value: 10000,
      stage: 'prospecting',
      description: `Test deal created at ${new Date().toISOString()}`,
      ...overrides
    };
  }
}

/**
 * Performance testing utilities
 */
export class PerformanceHelpers {
  
  static async measurePageLoad(page: Page, url: string) {
    const startTime = Date.now();
    
    await page.goto(url);
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    return {
      loadTime,
      isAcceptable: loadTime < 5000 // 5 second threshold
    };
  }

  static async measureApiResponse(page: Page, apiCall: () => Promise<any>) {
    const startTime = Date.now();
    
    const result = await apiCall();
    
    const responseTime = Date.now() - startTime;
    
    return {
      responseTime,
      result,
      isAcceptable: responseTime < 2000 // 2 second threshold
    };
  }
}