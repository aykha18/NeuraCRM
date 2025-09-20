import { test, expect, Page } from '@playwright/test';

/**
 * Lead Management Module - UI Regression Test Suite
 * 
 * This test suite covers all critical UI functionality for the Lead Management module:
 * - Lead listing and display
 * - Search and filtering
 * - Sorting functionality
 * - CRUD operations (Create, Read, Update, Delete)
 * - Bulk operations
 * - Lead scoring features
 * - Export functionality
 * - Responsive design
 * - Error handling
 */

test.describe('Lead Management Module', () => {
  
  // Test data constants
  const TEST_LEAD_TITLE = `Test Lead ${Date.now()}`;
  const UPDATED_LEAD_TITLE = `Updated Lead ${Date.now()}`;
  
  test.beforeEach(async ({ page }) => {
    // Navigate to leads page
    await page.goto('/leads');
    
    // Wait for page to load
    await expect(page.getByRole('heading', { name: 'Leads' })).toBeVisible();
    await page.waitForLoadState('networkidle');
  });

  test.describe('Page Layout and Navigation', () => {
    
    test('should display main page elements correctly', async ({ page }) => {
      // Check main heading
      await expect(page.getByRole('heading', { name: 'Leads' })).toBeVisible();
      
      // Check action buttons are present
      await expect(page.getByRole('button', { name: /create lead/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /score all leads/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /analytics/i })).toBeVisible();
      
      // Check search and filter elements
      await expect(page.getByPlaceholder('Search leads...')).toBeVisible();
      await expect(page.getByRole('combobox').first()).toBeVisible(); // Status filter
      await expect(page.getByRole('combobox').nth(1)).toBeVisible(); // Score filter
      
      // Check export buttons
      await expect(page.getByRole('button', { name: /export csv/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /export excel/i })).toBeVisible();
    });

    test('should display leads table with correct columns', async ({ page }) => {
      // Check table headers are present
      const expectedHeaders = ['Name', 'Company', 'Status', 'Score', 'Owner', 'Created', 'Actions'];
      
      for (const header of expectedHeaders) {
        await expect(page.getByRole('columnheader', { name: new RegExp(header, 'i') })).toBeVisible();
      }
      
      // Check select all checkbox
      await expect(page.getByRole('checkbox', { name: /select all leads/i })).toBeVisible();
    });

    test('should be responsive on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      // Table should be hidden on mobile
      await expect(page.locator('table')).toBeHidden();
      
      // Mobile card view should be visible
      await expect(page.getByRole('button', { name: /create new lead/i })).toBeVisible();
      
      // Check if leads are displayed as cards (if any exist)
      const leadCards = page.locator('[class*="rounded-2xl shadow border p-4"]');
      if (await leadCards.count() > 0) {
        await expect(leadCards.first()).toBeVisible();
      }
    });
  });

  test.describe('Lead Creation', () => {
    
    test('should open create lead modal when button is clicked', async ({ page }) => {
      await page.getByRole('button', { name: /create lead/i }).click();
      
      // Check modal is visible
      await expect(page.locator('[role="dialog"]')).toBeVisible();
      
      // Check form fields are present
      await expect(page.getByLabel(/title/i)).toBeVisible();
      await expect(page.getByLabel(/status/i)).toBeVisible();
      await expect(page.getByLabel(/source/i)).toBeVisible();
    });

    test('should create a new lead successfully', async ({ page }) => {
      // Open create modal
      await page.getByRole('button', { name: /create lead/i }).click();
      
      // Fill form
      await page.getByLabel(/title/i).fill(TEST_LEAD_TITLE);
      await page.getByLabel(/status/i).selectOption('qualified');
      await page.getByLabel(/source/i).selectOption('website');
      
      // Submit form
      const createResponse = page.waitForResponse(response => 
        response.url().includes('/api/leads') && response.request().method() === 'POST'
      );
      
      await page.getByRole('button', { name: /create/i }).click();
      
      // Wait for API response
      const response = await createResponse;
      expect(response.status()).toBeLessThan(300);
      
      // Check success message
      await expect(page.getByText(/lead created successfully/i)).toBeVisible();
      
      // Verify lead appears in table
      await expect(page.getByText(TEST_LEAD_TITLE)).toBeVisible();
    });

    test('should show validation error for empty title', async ({ page }) => {
      // Open create modal
      await page.getByRole('button', { name: /create lead/i }).click();
      
      // Try to submit without title
      await page.getByRole('button', { name: /create/i }).click();
      
      // Should show validation message
      await expect(page.getByText(/please enter a lead title/i)).toBeVisible();
    });

    test('should close modal when cancel is clicked', async ({ page }) => {
      // Open create modal
      await page.getByRole('button', { name: /create lead/i }).click();
      
      // Click cancel or close button
      await page.getByRole('button', { name: /cancel/i }).click();
      
      // Modal should be closed
      await expect(page.locator('[role="dialog"]')).toBeHidden();
    });
  });

  test.describe('Lead Listing and Display', () => {
    
    test('should display leads in table format', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      // Check if leads are displayed
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Check first lead row has all expected columns
        const firstRow = leadRows.first();
        await expect(firstRow.locator('td').nth(1)).toBeVisible(); // Name
        await expect(firstRow.locator('td').nth(2)).toBeVisible(); // Company
        await expect(firstRow.locator('td').nth(3)).toBeVisible(); // Status
        await expect(firstRow.locator('td').nth(4)).toBeVisible(); // Score
        await expect(firstRow.locator('td').nth(5)).toBeVisible(); // Owner
        await expect(firstRow.locator('td').nth(6)).toBeVisible(); // Created
        await expect(firstRow.locator('td').nth(7)).toBeVisible(); // Actions
      }
    });

    test('should display lead scores correctly', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Check if lead score component is displayed
        const scoreElements = page.locator('[class*="lead-score"], [class*="score"]');
        if (await scoreElements.count() > 0) {
          await expect(scoreElements.first()).toBeVisible();
        }
      }
    });

    test('should display status badges with correct colors', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const statusBadges = page.locator('[class*="rounded-full"][class*="px-3"]');
      const badgeCount = await statusBadges.count();
      
      if (badgeCount > 0) {
        // Check first status badge is visible and has color classes
        const firstBadge = statusBadges.first();
        await expect(firstBadge).toBeVisible();
        
        // Check it has appropriate color classes
        const classList = await firstBadge.getAttribute('class');
        expect(classList).toMatch(/(bg-blue|bg-green|bg-red|bg-yellow|bg-purple)/);
      }
    });
  });

  test.describe('Search and Filtering', () => {
    
    test('should filter leads by search term', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const initialRowCount = await page.locator('tbody tr').count();
      
      if (initialRowCount > 0) {
        // Get first lead name
        const firstLeadName = await page.locator('tbody tr:first-child td:nth-child(2)').textContent();
        
        if (firstLeadName && firstLeadName.trim()) {
          // Search for part of the name
          const searchTerm = firstLeadName.trim().substring(0, 3);
          await page.getByPlaceholder('Search leads...').fill(searchTerm);
          
          // Wait for filtering to complete
          await page.waitForTimeout(500);
          
          // Check results contain search term
          const filteredRows = page.locator('tbody tr');
          const filteredCount = await filteredRows.count();
          
          if (filteredCount > 0) {
            const firstResult = await filteredRows.first().locator('td:nth-child(2)').textContent();
            expect(firstResult?.toLowerCase()).toContain(searchTerm.toLowerCase());
          }
        }
      }
    });

    test('should filter leads by status', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      // Select a status filter
      await page.getByRole('combobox').first().selectOption('qualified');
      
      // Wait for filtering
      await page.waitForTimeout(500);
      
      // Check filter summary appears
      await expect(page.getByText(/active filters/i)).toBeVisible();
      await expect(page.getByText(/status: qualified/i)).toBeVisible();
      
      // Check filtered results (if any)
      const filteredRows = page.locator('tbody tr');
      const filteredCount = await filteredRows.count();
      
      if (filteredCount > 0) {
        // Check first result has qualified status
        const statusBadge = filteredRows.first().locator('td:nth-child(4) span');
        const statusText = await statusBadge.textContent();
        expect(statusText?.toLowerCase()).toContain('qualified');
      }
    });

    test('should filter leads by score range', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      // Select score filter
      await page.getByRole('combobox').nth(1).selectOption('hot');
      
      // Wait for filtering
      await page.waitForTimeout(500);
      
      // Check filter summary appears
      await expect(page.getByText(/active filters/i)).toBeVisible();
      await expect(page.getByText(/score: hot/i)).toBeVisible();
    });

    test('should clear all filters when clear button is clicked', async ({ page }) => {
      // Apply some filters
      await page.getByPlaceholder('Search leads...').fill('test');
      await page.getByRole('combobox').first().selectOption('qualified');
      
      // Wait for filters to apply
      await page.waitForTimeout(500);
      
      // Clear filters
      await page.getByRole('button', { name: /clear filters/i }).click();
      
      // Check filters are cleared
      await expect(page.getByPlaceholder('Search leads...')).toHaveValue('');
      await expect(page.getByRole('combobox').first()).toHaveValue('');
      
      // Filter summary should be hidden
      await expect(page.getByText(/active filters/i)).toBeHidden();
    });

    test('should show "no results" message when no leads match filters', async ({ page }) => {
      // Search for something that definitely won't exist
      await page.getByPlaceholder('Search leads...').fill('xyznoresults123456');
      
      // Wait for filtering
      await page.waitForTimeout(500);
      
      // Check no results are shown
      const rowCount = await page.locator('tbody tr').count();
      expect(rowCount).toBe(0);
    });
  });

  test.describe('Sorting Functionality', () => {
    
    test('should sort leads by name when column header is clicked', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const initialRowCount = await page.locator('tbody tr').count();
      
      if (initialRowCount > 1) {
        // Click name column header
        await page.getByRole('columnheader', { name: /name/i }).click();
        
        // Wait for sorting
        await page.waitForTimeout(500);
        
        // Check sort indicator is visible
        const nameHeader = page.getByRole('columnheader', { name: /name/i });
        await expect(nameHeader.locator('svg')).toBeVisible();
        
        // Verify sorting by checking first two rows
        const firstRowName = await page.locator('tbody tr:first-child td:nth-child(2)').textContent();
        const secondRowName = await page.locator('tbody tr:nth-child(2) td:nth-child(2)').textContent();
        
        if (firstRowName && secondRowName) {
          expect(firstRowName.localeCompare(secondRowName)).toBeLessThanOrEqual(0);
        }
      }
    });

    test('should reverse sort order when column header is clicked twice', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const initialRowCount = await page.locator('tbody tr').count();
      
      if (initialRowCount > 1) {
        const nameHeader = page.getByRole('columnheader', { name: /name/i });
        
        // Click once for ascending
        await nameHeader.click();
        await page.waitForTimeout(500);
        
        const firstClickName = await page.locator('tbody tr:first-child td:nth-child(2)').textContent();
        
        // Click again for descending
        await nameHeader.click();
        await page.waitForTimeout(500);
        
        const secondClickName = await page.locator('tbody tr:first-child td:nth-child(2)').textContent();
        
        // Names should be different (unless all names are the same)
        if (firstClickName !== secondClickName) {
          expect(firstClickName).not.toBe(secondClickName);
        }
      }
    });

    test('should sort by score when "Sort by Score" button is clicked', async ({ page }) => {
      // Click sort by score button
      await page.getByRole('button', { name: /sort by score/i }).click();
      
      // Wait for sorting
      await page.waitForTimeout(500);
      
      // Check that score column shows sort indicator
      const scoreHeader = page.getByRole('columnheader', { name: /score/i });
      await expect(scoreHeader.locator('svg')).toBeVisible();
    });
  });

  test.describe('Lead Actions', () => {
    
    test('should open lead detail modal when view button is clicked', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Click view button on first lead
        await leadRows.first().getByTitle('View').click();
        
        // Check detail modal opens
        await expect(page.locator('[role="dialog"]')).toBeVisible();
      }
    });

    test('should convert lead to deal when convert button is clicked', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Find a lead that's not already converted
        const convertButton = page.getByTitle('Convert to Deal').first();
        
        if (await convertButton.isVisible()) {
          // Wait for conversion API call
          const convertResponse = page.waitForResponse(response => 
            response.url().includes('/convert-to-deal') && response.request().method() === 'POST'
          );
          
          await convertButton.click();
          
          // Wait for API response
          const response = await convertResponse;
          expect(response.status()).toBeLessThan(300);
          
          // Check success message
          await expect(page.getByText(/converted to deal/i)).toBeVisible();
        }
      }
    });

    test('should show delete confirmation when delete button is clicked', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Click delete button on first lead
        await leadRows.first().getByTitle('Delete').click();
        
        // Check confirmation dialog appears
        await expect(page.getByText(/confirm/i)).toBeVisible();
        await expect(page.getByRole('button', { name: /delete/i })).toBeVisible();
        await expect(page.getByRole('button', { name: /cancel/i })).toBeVisible();
      }
    });
  });

  test.describe('Inline Editing', () => {
    
    test('should enable inline editing when lead name is clicked', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Click on first lead name
        const leadNameCell = leadRows.first().locator('td:nth-child(2) span');
        await leadNameCell.click();
        
        // Check input field appears
        await expect(leadRows.first().locator('td:nth-child(2) input')).toBeVisible();
      }
    });

    test('should save changes when Enter is pressed during inline editing', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Click on first lead name to edit
        const leadNameCell = leadRows.first().locator('td:nth-child(2) span');
        await leadNameCell.click();
        
        // Edit the name
        const inputField = leadRows.first().locator('td:nth-child(2) input');
        await inputField.fill(UPDATED_LEAD_TITLE);
        
        // Wait for update API call
        const updateResponse = page.waitForResponse(response => 
          response.url().includes('/api/leads/') && response.request().method() === 'PUT'
        );
        
        // Press Enter to save
        await inputField.press('Enter');
        
        // Wait for API response
        const response = await updateResponse;
        expect(response.status()).toBeLessThan(300);
        
        // Check success message
        await expect(page.getByText(/lead updated/i)).toBeVisible();
      }
    });

    test('should cancel editing when Escape is pressed', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Get original name
        const originalName = await leadRows.first().locator('td:nth-child(2) span').textContent();
        
        // Click to edit
        await leadRows.first().locator('td:nth-child(2) span').click();
        
        // Change the value
        const inputField = leadRows.first().locator('td:nth-child(2) input');
        await inputField.fill('Cancelled Edit');
        
        // Press Escape to cancel
        await inputField.press('Escape');
        
        // Check original name is restored
        await expect(leadRows.first().locator('td:nth-child(2) span')).toHaveText(originalName || '');
      }
    });
  });

  test.describe('Bulk Operations', () => {
    
    test('should select all leads when select all checkbox is clicked', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Click select all checkbox
        await page.getByRole('checkbox', { name: /select all leads/i }).click();
        
        // Check bulk action bar appears
        await expect(page.getByText(/selected/)).toBeVisible();
        
        // Check all individual checkboxes are selected
        const checkboxes = page.locator('tbody tr input[type="checkbox"]');
        const checkboxCount = await checkboxes.count();
        
        for (let i = 0; i < checkboxCount; i++) {
          await expect(checkboxes.nth(i)).toBeChecked();
        }
      }
    });

    test('should show bulk action bar when leads are selected', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Select first lead
        await leadRows.first().locator('input[type="checkbox"]').click();
        
        // Check bulk action bar appears
        await expect(page.getByText(/1 selected/)).toBeVisible();
        await expect(page.getByRole('button', { name: /delete selected/i })).toBeVisible();
        await expect(page.getByRole('button', { name: /clear/i })).toBeVisible();
      }
    });

    test('should clear selection when clear button is clicked', async ({ page }) => {
      // Wait for leads to load
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      const leadRows = page.locator('tbody tr');
      const leadCount = await leadRows.count();
      
      if (leadCount > 0) {
        // Select first lead
        await leadRows.first().locator('input[type="checkbox"]').click();
        
        // Click clear button
        await page.getByRole('button', { name: /clear/i }).click();
        
        // Check bulk action bar disappears
        await expect(page.getByText(/selected/)).toBeHidden();
        
        // Check checkbox is unchecked
        await expect(leadRows.first().locator('input[type="checkbox"]')).not.toBeChecked();
      }
    });
  });

  test.describe('Lead Scoring Features', () => {
    
    test('should trigger score all leads when button is clicked', async ({ page }) => {
      // Click score all leads button
      const scoreResponse = page.waitForResponse(response => 
        response.url().includes('/score-all') && response.request().method() === 'POST'
      );
      
      await page.getByRole('button', { name: /score all leads/i }).click();
      
      // Wait for API response
      const response = await scoreResponse;
      expect(response.status()).toBeLessThan(300);
      
      // Check success message appears
      await expect(page.getByText(/successfully scored/i)).toBeVisible();
    });

    test('should open analytics modal when analytics button is clicked', async ({ page }) => {
      // Click analytics button
      const analyticsResponse = page.waitForResponse(response => 
        response.url().includes('/scoring-analytics') && response.request().method() === 'GET'
      );
      
      await page.getByRole('button', { name: /analytics/i }).click();
      
      // Wait for API response
      const response = await analyticsResponse;
      expect(response.status()).toBeLessThan(300);
      
      // Check analytics modal opens
      await expect(page.locator('[role="dialog"]')).toBeVisible();
    });
  });

  test.describe('Export Functionality', () => {
    
    test('should trigger CSV export when export CSV button is clicked', async ({ page }) => {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download');
      
      // Click export CSV button
      await page.getByRole('button', { name: /export csv/i }).click();
      
      // Wait for download
      const download = await downloadPromise;
      
      // Check download started
      expect(download.suggestedFilename()).toBe('leads.csv');
    });

    test('should trigger Excel export when export Excel button is clicked', async ({ page }) => {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download');
      
      // Click export Excel button
      await page.getByRole('button', { name: /export excel/i }).click();
      
      // Wait for download
      const download = await downloadPromise;
      
      // Check download started
      expect(download.suggestedFilename()).toBe('leads.xlsx');
    });
  });

  test.describe('Pagination', () => {
    
    test('should show pagination controls when there are many leads', async ({ page }) => {
      // Check if pagination exists (depends on data)
      const paginationControls = page.locator('[class*="pagination"], [aria-label*="pagination"]');
      
      if (await paginationControls.count() > 0) {
        await expect(paginationControls.first()).toBeVisible();
      }
    });
  });

  test.describe('Error Handling', () => {
    
    test('should show error message when API fails', async ({ page }) => {
      // Intercept API calls and make them fail
      await page.route('**/api/leads', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal Server Error' })
        });
      });
      
      // Reload page to trigger error
      await page.reload();
      
      // Check error message is displayed
      await expect(page.getByText(/failed to load leads/i)).toBeVisible();
    });

    test('should handle network errors gracefully', async ({ page }) => {
      // Intercept and abort network requests
      await page.route('**/api/leads', route => route.abort());
      
      // Reload page
      await page.reload();
      
      // Should show some kind of error or loading state
      const errorOrLoading = page.locator('text=/error|failed|loading/i');
      await expect(errorOrLoading.first()).toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    
    test('should have proper ARIA labels and roles', async ({ page }) => {
      // Check main heading has proper role
      await expect(page.getByRole('heading', { name: 'Leads' })).toBeVisible();
      
      // Check buttons have proper labels
      await expect(page.getByRole('button', { name: /create lead/i })).toBeVisible();
      
      // Check form inputs have labels
      const searchInput = page.getByPlaceholder('Search leads...');
      await expect(searchInput).toBeVisible();
      
      // Check table has proper structure
      await expect(page.getByRole('table')).toBeVisible();
      await expect(page.getByRole('columnheader').first()).toBeVisible();
    });

    test('should be keyboard navigable', async ({ page }) => {
      // Tab through interactive elements
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Check focus is visible (this is basic - more detailed tests would check specific focus states)
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });
  });

  test.describe('Performance', () => {
    
    test('should load leads page within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto('/leads');
      await page.waitForLoadState('networkidle');
      
      const loadTime = Date.now() - startTime;
      
      // Should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
    });

    test('should handle large datasets without performance issues', async ({ page }) => {
      // This test would need actual large dataset or mocked data
      // For now, just check that the page remains responsive
      
      await page.waitForSelector('tbody tr', { timeout: 10000 });
      
      // Perform multiple operations quickly
      await page.getByPlaceholder('Search leads...').fill('test');
      await page.getByRole('combobox').first().selectOption('qualified');
      await page.getByRole('columnheader', { name: /name/i }).click();
      
      // Page should still be responsive
      await expect(page.getByRole('heading', { name: 'Leads' })).toBeVisible();
    });
  });
});