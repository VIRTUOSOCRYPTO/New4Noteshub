import { test, expect } from '@playwright/test';

test.describe('Notes Features', () => {
  test('should load find notes page', async ({ page }) => {
    await page.goto('/find-notes');
    await expect(page).toHaveURL(/find-notes/);
  });

  test('should show notes filters', async ({ page }) => {
    await page.goto('/find-notes');
    await page.waitForLoadState('networkidle');
    const filters = page.locator('select, [role="combobox"], input[type="search"]');
    await expect(filters.first()).toBeVisible({ timeout: 10000 });
  });

  test('should display analytics page', async ({ page }) => {
    await page.goto('/analytics');
    await expect(page).toHaveURL(/analytics/);
  });
});
