import { test, expect } from '@playwright/test';

test.describe('Story 1.1 - Visual Verification', () => {
  test('should capture desktop screenshot', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Capture full page screenshot
    await page.screenshot({
      path: '_bmad-output/test-artifacts/screenshots/story-1-1-desktop.png',
      fullPage: true,
    });

    // Verify pure black background
    const backgroundColor = await page.evaluate(() => {
      return getComputedStyle(document.body).backgroundColor;
    });
    expect(backgroundColor).toBe('rgb(0, 0, 0)');
  });

  test('should capture mobile screenshot', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: '_bmad-output/test-artifacts/screenshots/story-1-1-mobile.png',
      fullPage: true,
    });
  });

  test('should verify design tokens are applied', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check if CSS variables are defined
    const pureBlack = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--pure-black');
    });

    const oceanMint = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--ocean-mint-primary');
    });

    expect(pureBlack.trim()).toBe('#000000');
    expect(oceanMint.trim()).toBe('#20B2AA');
  });

  test('should verify Google Fonts loaded', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check if Space Grotesk font is loaded
    const spaceGroteskLoaded = await page.evaluate(() => {
      return document.fonts.check('16px "Space Grotesk"');
    });

    const interLoaded = await page.evaluate(() => {
      return document.fonts.check('16px Inter');
    });

    expect(spaceGroteskLoaded).toBeTruthy();
    expect(interLoaded).toBeTruthy();
  });
});
