import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should display home page', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/NotesHub/i);
  });

  test('should show registration form elements', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[name="usn"], input[placeholder*="USN" i]').first()).toBeVisible({ timeout: 10000 });
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/');
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    await page.waitForTimeout(1000);
  });

  test('should navigate to find notes', async ({ page }) => {
    await page.goto('/');
    await page.goto('/find-notes');
    await expect(page).toHaveURL(/find-notes/);
  });
});
