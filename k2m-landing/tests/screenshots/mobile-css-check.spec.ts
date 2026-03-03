import { test, expect } from '@playwright/test';

test.describe('Mobile CSS Debug', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test('should check mobile CSS is applied', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);

    const zone0 = page.locator('.constellation-zone[data-zone="0"]');
    await zone0.scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);

    // Check star positions
    const stars = zone0.locator('.thought-star');
    const count = await stars.count();

    console.log(`\n=== Mobile CSS Debug ===`);
    console.log(`Zone 0 has ${count} stars\n`);

    for (let i = 0; i < count; i++) {
      const star = stars.nth(i);

      // Get computed styles
      const position = await star.evaluate((el) => window.getComputedStyle(el).position);
      const top = await star.evaluate((el) => el.style.top);
      const left = await star.evaluate((el) => el.style.left);
      const display = await star.evaluate((el) => window.getComputedStyle(el).display);

      console.log(`Star ${i}:`);
      console.log(`  position: ${position}`);
      console.log(`  top: ${top}`);
      console.log(`  left: ${left}`);
      console.log(`  display: ${display}`);
    }

    // Check nebula
    const nebula = zone0.locator('.voice-nebula');
    const nebulaMaxWidth = await nebula.evaluate((el) => window.getComputedStyle(el).maxWidth);
    const nebulaPadding = await nebula.evaluate((el) => window.getComputedStyle(el).padding);

    console.log(`\nNebula:`);
    console.log(`  max-width: ${nebulaMaxWidth}`);
    console.log(`  padding: ${nebulaPadding}`);

    // Check if media query is active
    const isMobile = await page.evaluate(() => window.matchMedia('(max-width: 768px)').matches);
    console.log(`\nMedia query active: ${isMobile}`);
  });
});
