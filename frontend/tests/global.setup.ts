import type { FullConfig, request as APIRequest } from '@playwright/test';
import { request, chromium } from '@playwright/test';

const EMAIL = 'nodeit@node.com';
const PASSWORD = 'NodeIT2024!';
const API_BASE = process.env.API_BASE_URL || 'http://127.0.0.1:8002';
const APP_BASE = process.env.BASE_URL || 'http://localhost:5173';

export default async function globalSetup(_config: FullConfig) {
  // Create an authenticated storage state for the app domain
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  // Ensure app points to correct API
  await page.goto(APP_BASE);
  await page.addInitScript(({ api }) => {
    try { localStorage.setItem('API_BASE_URL', api); } catch {}
  }, { api: API_BASE });
  await page.reload();

  // Perform login through UI to get proper cookies/localStorage
  await page.goto(`${APP_BASE}/signin`);
  await page.getByLabel('Email').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  
  // Wait for successful login by checking for dashboard or any protected route
  await page.waitForURL(/dashboard|customer-support|kanban|leads/i, { timeout: 15000 });

  // Save storage for reuse
  await context.storageState({ path: './tests/.storage/state.json' });
  await browser.close();

  // Sanity: ping tickets
  const ctx = await request.newContext({ baseURL: API_BASE });
  await ctx.get('/api/support/tickets');
  await ctx.dispose();
}


