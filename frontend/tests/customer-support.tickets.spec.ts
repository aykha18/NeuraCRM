import { test, expect } from '@playwright/test';

const email = 'nodeit@node.com';
const password = 'NodeIT2024!';

test.describe('Customer Support - Tickets', () => {
  test('Create ticket via UI and verify it appears in list', async ({ page, request }) => {
    // Force API base before app scripts
    await page.addInitScript(({ api }) => { try { localStorage.setItem('API_BASE_URL', api); } catch {} }, { api: process.env.API_BASE_URL || 'http://127.0.0.1:8002' });
    await page.goto('/');

    // Go to Customer Support
    await page.getByRole('link', { name: /customer support/i }).click();
    await expect(page.getByRole('heading', { name: 'Support Tickets' })).toBeVisible();

    // Create ticket
    await page.getByTestId('cs-create-ticket').click();
    await expect(page.getByTestId('cs-ticket-modal')).toBeVisible();

    const title = `UI Test Ticket ${Date.now()}`;
    await page.getByTestId('cs-title').fill(title);
    await page.getByTestId('cs-description').fill('Ticket created by Playwright');
    await page.getByTestId('cs-priority').selectOption('high');
    await page.getByTestId('cs-category').selectOption('technical');
    await page.getByTestId('cs-customer-name').fill('UI Tester');
    await page.getByTestId('cs-customer-email').fill('uitester@example.com');

    const creation = page.waitForResponse(resp => resp.url().endsWith('/api/support/tickets') && ['POST','post'].includes(resp.request().method()));
    await page.getByTestId('cs-ticket-modal').getByRole('button', { name: /create ticket/i }).click();
    const resp = await creation;
    const status = resp.status();
    let bodyText = '';
    try { bodyText = await resp.text(); } catch {}
    expect(status, `POST /api/support/tickets failed: ${status} ${bodyText}`).toBeLessThan(300);

    // Success modal closes automatically; verify ticket is present
    await expect(page.getByTestId('cs-ticket-list')).toContainText(title, { timeout: 15_000 });

    // Quick API verification: fetch tickets and assert presence
    // Use frontend request context with current cookies for auth
    const apiBase = process.env.API_BASE_URL || 'http://127.0.0.1:8000';
    const ticketsResp = await request.get(`${apiBase}/api/support/tickets`);
    expect(ticketsResp.ok()).toBeTruthy();
    const data: any[] = await ticketsResp.json();
    expect(Array.isArray(data)).toBeTruthy();
    expect(data.some(t => t.title === title)).toBeTruthy();
  });
});


