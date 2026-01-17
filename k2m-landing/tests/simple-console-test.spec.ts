import { test, expect } from '@playwright/test';

test('simple console log test', async ({ page }) => {
  const logs: string[] = [];
  const errors: string[] = [];

  page.on('console', msg => {
    const text = msg.text();
    logs.push(text);
    console.log('Browser console:', text);
  });

  page.on('pageerror', error => {
    const text = error.toString();
    errors.push(text);
    console.error('Browser error:', text);
  });

  await page.goto('/');

  console.log('All logs:', JSON.stringify(logs, null, 2));
  console.log('All errors:', JSON.stringify(errors, null, 2));
});
