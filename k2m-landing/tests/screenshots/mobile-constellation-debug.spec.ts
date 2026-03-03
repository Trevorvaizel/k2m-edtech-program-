import { test, expect } from '@playwright/test';

test.describe('Mobile Constellation Zones Debug', () => {
  test.use({ viewport: { width: 375, height: 812 } }); // iPhone X

  test('should capture Zone 0 on mobile', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);

    const zone0 = page.locator('.constellation-zone[data-zone="0"]');
    await zone0.scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: 'test-results/mobile-zone-0-debug.png',
      fullPage: false
    });

    // Check where stars are positioned
    const stars = zone0.locator('.thought-star');
    const count = await stars.count();
    console.log(`Zone 0 has ${count} stars`);

    for (let i = 0; i < count; i++) {
      const star = stars.nth(i);
      const isVisible = await star.isVisible();
      console.log(`  Star ${i} visible: ${isVisible}`);
    }
  });

  test('should capture all zones on mobile', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);

    for (let i = 0; i <= 4; i++) {
      const zone = page.locator(`.constellation-zone[data-zone="${i}"]`);
      await zone.scrollIntoViewIfNeeded();
      await page.waitForTimeout(500);

      await page.screenshot({
        path: `test-results/mobile-zone-${i}-debug.png`,
        fullPage: false
      });

      const nebula = zone.locator('.voice-nebula');
      const stars = zone.locator('.thought-star');
      const starCount = await stars.count();

      console.log(`Zone ${i}: ${starCount} stars, nebula visible: ${await nebula.isVisible()}`);
    }
  });

  test('should check star positioning on mobile', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);

    const zone0 = page.locator('.constellation-zone[data-zone="0"]');
    await zone0.scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);

    // Get bounding boxes
    const zoneBox = await zone0.boundingBox();
    const nebula = zone0.locator('.voice-nebula');
    const nebulaBox = await nebula.boundingBox();

    console.log('Zone 0 bounding box:', zoneBox);
    console.log('Nebula bounding box:', nebulaBox);

    const stars = zone0.locator('.thought-star');
    const count = await stars.count();

    for (let i = 0; i < Math.min(count, 3); i++) {
      const star = stars.nth(i);
      const box = await star.boundingBox();
      console.log(`Star ${i} bounding box:`, box);

      // Check if star overlaps with nebula
      if (nebulaBox && box) {
        const overlap = !(
          box.x + box.width < nebulaBox.x ||
          box.x > nebulaBox.x + nebulaBox.width ||
          box.y + box.height < nebulaBox.y ||
          box.y > nebulaBox.y + nebulaBox.height
        );
        console.log(`  Overlaps with nebula: ${overlap}`);
      }
    }
  });
});
