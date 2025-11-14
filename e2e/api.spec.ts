import { test, expect } from '@playwright/test';

test.describe('API Health Checks', () => {
  test('backend health endpoint should respond', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/health');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.status).toBe('ok');
  });

  test('database status endpoint should respond', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/db-status');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('status');
  });
});
