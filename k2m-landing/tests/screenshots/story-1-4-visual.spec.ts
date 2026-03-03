import { test, expect } from '@playwright/test';

test.describe('Story 1.4 - Hero Animations Visual Check', () => {
  test('should capture Hero section - initial state', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Let animations settle

    // Capture what we see NOW
    await page.screenshot({
      path: '_bmad-output/test-artifacts/screenshots/story-1-4-initial.png',
      fullPage: true,
    });

    console.log('✅ Screenshot saved: story-1-4-initial.png');
  });

  test('should capture Hero section - after scroll', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Scroll down to trigger animations
    await page.evaluate(() => window.scrollTo(0, 800));
    await page.waitForTimeout(1500); // Wait for scroll animations

    await page.screenshot({
      path: '_bmad-output/test-artifacts/screenshots/story-1-4-scrolled.png',
      fullPage: true,
    });

    console.log('✅ Screenshot saved: story-1-4-scrolled.png');
  });

  test('should check if Hero content exists', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check DOM elements
    const heroExists = await page.locator('.hero').count();
    const titleText = await page.locator('.hero-title').textContent();
    const glowTextCount = await page.locator('.glow-text').count();

    console.log(`Hero exists: ${heroExists > 0}`);
    console.log(`Title: ${titleText}`);
    console.log(`Glow text elements: ${glowTextCount}`);

    expect(heroExists).toBeGreaterThan(0);
  });
});
