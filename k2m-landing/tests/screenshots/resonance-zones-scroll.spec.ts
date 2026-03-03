import { test, expect } from '@playwright/test';

/**
 * Visual Regression Test - Resonance Zones Scroll Behavior
 *
 * Tests zone activation, card visibility, and progress dot tracking
 * through actual scrolling on both desktop and mobile viewports.
 */

test.describe('Resonance Zones - Scroll Behavior', () => {
  test('desktop: scroll through all zones and capture states', async ({ page }) => {
    await page.goto('/');

    // Wait for page load
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000); // Allow animations to settle

    // Desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Screenshot: Hero section
    await page.screenshot({
      path: 'test-results/screenshots/resonance/01-hero.png',
      fullPage: false
    });

    // Scroll to Zone 0 (Confusion)
    await page.evaluate(() => {
      document.querySelector('.resonance-zone[data-zone="0"]')?.scrollIntoView({
        behavior: 'instant',
        block: 'center'
      });
    });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: 'test-results/screenshots/resonance/02-zone-0-confusion.png',
      fullPage: false
    });

    // Scroll to Zone 1 (Curiosity)
    await page.evaluate(() => {
      document.querySelector('.resonance-zone[data-zone="1"]')?.scrollIntoView({
        behavior: 'instant',
        block: 'center'
      });
    });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: 'test-results/screenshots/resonance/03-zone-1-curiosity.png',
      fullPage: false
    });

    // Scroll to Zone 2 (Trial & Error)
    await page.evaluate(() => {
      document.querySelector('.resonance-zone[data-zone="2"]')?.scrollIntoView({
        behavior: 'instant',
        block: 'center'
      });
    });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: 'test-results/screenshots/resonance/04-zone-2-trial-error.png',
      fullPage: false
    });

    // Scroll to Zone 3 (Collaboration)
    await page.evaluate(() => {
      document.querySelector('.resonance-zone[data-zone="3"]')?.scrollIntoView({
        behavior: 'instant',
        block: 'center'
      });
    });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: 'test-results/screenshots/resonance/05-zone-3-collaboration.png',
      fullPage: false
    });

    // Scroll to Zone 4 (Confidence)
    await page.evaluate(() => {
      document.querySelector('.resonance-zone[data-zone="4"]')?.scrollIntoView({
        behavior: 'instant',
        block: 'center'
      });
    });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: 'test-results/screenshots/resonance/06-zone-4-confidence.png',
      fullPage: false
    });

    // SCROLL BACK UP - Test reactivation
    // Back to Zone 2
    await page.evaluate(() => {
      document.querySelector('.resonance-zone[data-zone="2"]')?.scrollIntoView({
        behavior: 'instant',
        block: 'center'
      });
    });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: 'test-results/screenshots/resonance/07-back-to-zone-2.png',
      fullPage: false
    });

    // Back to Zone 0
    await page.evaluate(() => {
      document.querySelector('.resonance-zone[data-zone="0"]')?.scrollIntoView({
        behavior: 'instant',
        block: 'center'
      });
    });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: 'test-results/screenshots/resonance/08-back-to-zone-0.png',
      fullPage: false
    });
  });

  test('mobile: scroll through all zones and capture states', async ({ page }) => {
    await page.goto('/');

    // Wait for page load
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });

    // Screenshot: Hero mobile
    await page.screenshot({
      path: 'test-results/screenshots/resonance/mobile-01-hero.png',
      fullPage: false
    });

    // Scroll through zones on mobile
    for (let i = 0; i <= 4; i++) {
      await page.evaluate((zoneIndex) => {
        document.querySelector(`.resonance-zone[data-zone="${zoneIndex}"]`)?.scrollIntoView({
          behavior: 'instant',
          block: 'center'
        });
      }, i);
      await page.waitForTimeout(800);
      await page.screenshot({
        path: `test-results/screenshots/resonance/mobile-02-zone-${i}.png`,
        fullPage: false
      });
    }

    // Scroll back to Zone 1 on mobile
    await page.evaluate(() => {
      document.querySelector('.resonance-zone[data-zone="1"]')?.scrollIntoView({
        behavior: 'instant',
        block: 'center'
      });
    });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: 'test-results/screenshots/resonance/mobile-03-back-to-zone-1.png',
      fullPage: false
    });
  });

  test('slow scroll: simulate user scrolling behavior', async ({ page }) => {
    await page.goto('/');

    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Slow scroll through first 3 zones
    await page.evaluate(async () => {
      const zones = document.querySelectorAll('.resonance-zone');
      for (let i = 0; i < Math.min(3, zones.length); i++) {
        zones[i].scrollIntoView({ behavior: 'smooth', block: 'center' });
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
    });

    await page.waitForTimeout(500);
    await page.screenshot({
      path: 'test-results/screenshots/resonance/09-slow-scroll-zone-2.png',
      fullPage: false
    });
  });
});
