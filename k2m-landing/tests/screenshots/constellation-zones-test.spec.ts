import { test, expect } from '@playwright/test';

test.describe('Constellation Zones Integration Test', () => {
  test('should verify constellation zones are loaded', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Wait for page to load
    await page.waitForTimeout(2000);

    // Check if starfield exists
    const starfield = page.locator('#starfield');
    await expect(starfield).toBeAttached();

    // Check if all 5 constellation zones exist
    for (let i = 0; i <= 4; i++) {
      const zone = page.locator(`.constellation-zone[data-zone="${i}"]`);
      await expect(zone).toBeAttached();
      console.log(`✅ Zone ${i} found`);

      // Check if zone has voice nebula
      const nebula = zone.locator('.voice-nebula');
      await expect(nebula).toBeAttached();

      // Check if zone has thought stars
      const stars = zone.locator('.thought-star');
      const starCount = await stars.count();
      console.log(`  Zone ${i} has ${starCount} thought stars`);
      expect(starCount).toBeGreaterThan(0);
    }

    // Check if constellation canvases exist
    for (let i = 0; i <= 4; i++) {
      const canvas = page.locator(`#canvas${i}.constellation-canvas`);
      await expect(canvas).toBeAttached();
    }

    console.log('✅ All constellation zones loaded successfully');
  });

  test('should capture screenshot of Zone 0', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Wait for page load
    await page.waitForTimeout(2000);

    // Scroll to Zone 0
    const zone0 = page.locator('.constellation-zone[data-zone="0"]');
    await zone0.scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);

    // Capture screenshot
    await page.screenshot({
      path: 'test-results/constellation-zone-0.png',
      fullPage: false
    });

    console.log('✅ Screenshot saved: constellation-zone-0.png');
  });
});
