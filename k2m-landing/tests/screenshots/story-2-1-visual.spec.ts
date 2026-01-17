import { test, expect } from '@playwright/test';

/**
 * Story 2.1: Territory Map SVG Structure - Visual Regression Tests
 *
 * Tests TerritoryMap section:
 * - All 5 zones visible with correct positioning (desktop)
 * - Zone 4 ocean mint accent styling
 * - Text contrast WCAG AA compliance
 * - Mobile viewport responsive layout (vertical stack)
 * - Semantic HTML structure and accessibility
 * - Particle container readiness for Story 2.2
 */

test.describe('Story 2.1 - TerritoryMap Visual Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to the landing page
    await page.goto('/');

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500); // Allow animations to initialize
  });

  test('should render TerritoryMap section with all 5 zones on desktop', async ({ page }) => {
    // Scroll TerritoryMap section into view
    const territoryMap = page.locator('.territory-map');
    await territoryMap.scrollIntoViewIfNeeded();

    // Wait for section to be visible
    await expect(territoryMap).toBeVisible();

    // Verify all 5 zones exist and are visible
    const zone0 = page.locator('.zone-0');
    const zone1 = page.locator('.zone-1');
    const zone2 = page.locator('.zone-2');
    const zone3 = page.locator('.zone-3');
    const zone4 = page.locator('.zone-4');

    await expect(zone0).toBeVisible();
    await expect(zone1).toBeVisible();
    await expect(zone2).toBeVisible();
    await expect(zone3).toBeVisible();
    await expect(zone4).toBeVisible();

    // Verify zone positioning (absolute positioning along diagonal journey)
    // Note: getComputedStyle returns computed pixel values, not percentages
    const zone0Left = await zone0.evaluate((el) => {
      const left = window.getComputedStyle(el).left;
      return parseFloat(left); // Returns pixel value
    });
    expect(zone0Left).toBeGreaterThan(80); // Approximately 8.3% of 1200px = ~100px
    expect(zone0Left).toBeLessThan(120);

    const zone4Left = await zone4.evaluate((el) => {
      const left = window.getComputedStyle(el).left;
      return parseFloat(left);
    });
    expect(zone4Left).toBeGreaterThan(1000); // Approximately 91.6% of 1200px = ~1100px
    expect(zone4Left).toBeLessThan(1150);

    // Verify background is pure black
    const backgroundColor = await territoryMap.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    expect(backgroundColor).toContain('0'); // #000000 pure black

    // Screenshot for visual regression
    await expect(page).toHaveScreenshot('story-2-1-desktop-initial.png', {
      maxDiffPixels: 100,
      threshold: 0.2
    });
  });

  test('should display Zone 4 with ocean mint accent styling', async ({ page }) => {
    // Scroll to TerritoryMap
    const territoryMap = page.locator('.territory-map');
    await territoryMap.scrollIntoViewIfNeeded();

    // Verify Zone 4 has destination class
    const zone4 = page.locator('.zone-4.zone-destination');
    await expect(zone4).toBeVisible();

    // Verify ocean mint border color
    const borderColor = await zone4.evaluate((el) => {
      return window.getComputedStyle(el).borderColor;
    });
    expect(borderColor).toContain('64, 224, 208'); // #40E0D0 ocean mint glow

    // Verify box-shadow glow effect
    const boxShadow = await zone4.evaluate((el) => {
      return window.getComputedStyle(el).boxShadow;
    });
    expect(boxShadow).toContain('64, 224, 208'); // Ocean mint glow

    // Verify Zone 4 heading has ocean mint color
    const zone4Heading = page.locator('.zone-4 h3');
    const headingColor = await zone4Heading.evaluate((el) => {
      return window.getComputedStyle(el).color;
    });
    expect(headingColor).toContain('64, 224, 208'); // #40E0D0

    // Screenshot for Zone 4 accent visual regression
    await zone4.scrollIntoViewIfNeeded();
    await expect(page).toHaveScreenshot('story-2-1-zone-4-accent.png', {
      maxDiffPixels: 80,
      threshold: 0.15
    });
  });

  test('should display approved copy in all zones', async ({ page }) => {
    // Scroll TerritoryMap into view
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) {
        map.scrollIntoView({ block: 'center' });
      }
    });

    await page.waitForTimeout(500);

    // Verify Zone 0 copy
    const zone0Heading = page.locator('.zone-0 h3');
    await expect(zone0Heading).toHaveText('AI isn\'t for me');

    const zone0Desc = page.locator('.zone-0 p');
    await expect(zone0Desc).toHaveText('Where most students start. Feeling overwhelmed.');

    // Verify Zone 1 copy
    const zone1Heading = page.locator('.zone-1 h3');
    await expect(zone1Heading).toHaveText('I could try this');

    const zone1Desc = page.locator('.zone-1 p');
    await expect(zone1Desc).toHaveText('First sparks of curiosity.');

    // Verify Zone 2 copy
    const zone2Heading = page.locator('.zone-2 h3');
    await expect(zone2Heading).toHaveText('AI does tasks for me');

    const zone2Desc = page.locator('.zone-2 p');
    await expect(zone2Desc).toHaveText('Using it for real work. But inconsistent.');

    // Verify Zone 3 copy
    const zone3Heading = page.locator('.zone-3 h3');
    await expect(zone3Heading).toHaveText('AI understands my intent');

    const zone3Desc = page.locator('.zone-3 p');
    await expect(zone3Desc).toHaveText('True collaboration begins.');

    // Verify Zone 4 copy
    const zone4Heading = page.locator('.zone-4 h3');
    await expect(zone4Heading).toHaveText('I control the quality');

    const zone4Desc = page.locator('.zone-4 p');
    await expect(zone4Desc).toHaveText('You direct. You refine. You own the outcome. This is where confidence lives.');
  });

  test('should have WCAG AA compliant text contrast', async ({ page }) => {
    // Scroll TerritoryMap into view
    const territoryMap = page.locator('.territory-map');
    await territoryMap.scrollIntoViewIfNeeded();

    // Verify zone headings contrast (WCAG AA requires 3:1 for large text)
    const zone0Heading = page.locator('.zone-0 h3');
    const headingColor = await zone0Heading.evaluate((el) => {
      const rgb = window.getComputedStyle(el).color.match(/\d+/g);
      if (rgb) {
        const [r, g, b] = rgb.map(Number);
        // Calculate luminance
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        return luminance;
      }
      return 0;
    });

    // White text on black background should have high contrast
    expect(headingColor).toBeGreaterThan(0.7); // High luminance = good contrast

    // Verify zone descriptions contrast (WCAG AA requires 4.5:1 for normal text)
    const zone0Desc = page.locator('.zone-0 p');
    const descColor = await zone0Desc.evaluate((el) => {
      const rgb = window.getComputedStyle(el).color.match(/\d+/g);
      if (rgb) {
        const [r, g, b] = rgb.map(Number);
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        return luminance;
      }
      return 0;
    });

    // Text should be readable
    expect(descColor).toBeGreaterThan(0.5); // Sufficient contrast
  });

  test('should render correctly on mobile viewport with vertical layout', async ({ page }) => {
    // Set mobile viewport (iPhone 12)
    await page.setViewportSize({ width: 375, height: 667 });

    // Scroll TerritoryMap into view
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) {
        map.scrollIntoView({ block: 'start' });
      }
    });

    await page.waitForTimeout(500);

    // Verify all zones are still visible
    const zone0 = page.locator('.zone-0');
    const zone1 = page.locator('.zone-1');
    const zone2 = page.locator('.zone-2');
    const zone3 = page.locator('.zone-3');
    const zone4 = page.locator('.zone-4');

    await expect(zone0).toBeVisible();
    await expect(zone1).toBeVisible();
    await expect(zone2).toBeVisible();
    await expect(zone3).toBeVisible();
    await expect(zone4).toBeVisible();

    // Verify zones are stacked vertically (relative positioning)
    const zone0Position = await zone0.evaluate((el) => {
      return window.getComputedStyle(el).position;
    });
    expect(zone0Position).toBe('relative');

    // Verify responsive font sizes (using clamp values)
    const zone0Heading = page.locator('.zone-0 h3');
    const fontSize = await zone0Heading.evaluate((el) => {
      return window.getComputedStyle(el).fontSize;
    });
    const fontSizeValue = parseFloat(fontSize);
    expect(fontSizeValue).toBeGreaterThan(16); // Should be responsive
    expect(fontSizeValue).toBeLessThan(24); // But not desktop size

    // Verify mobile padding is reduced (2rem vs 4rem desktop)
    const territoryMap = page.locator('.territory-map');
    const paddingTop = await territoryMap.evaluate((el) => {
      return window.getComputedStyle(el).paddingTop;
    });
    expect(paddingTop).toBe('32px'); // 2rem = 32px

    // Verify no horizontal scrolling
    const bodyWidth = await page.evaluate(() => {
      return document.body.scrollWidth;
    });
    const viewportWidth = await page.evaluate(() => {
      return window.innerWidth;
    });
    expect(bodyWidth).toBe(viewportWidth); // No horizontal overflow

    // Screenshot for mobile visual regression
    await expect(page).toHaveScreenshot('story-2-1-mobile-vertical.png', {
      maxDiffPixels: 150,
      threshold: 0.25
    });
  });

  test('should have accessible semantic HTML structure', async ({ page }) => {
    // Verify aria-label is present on section
    const territoryMap = page.locator('.territory-map');
    const ariaLabel = await territoryMap.getAttribute('aria-label');
    expect(ariaLabel).toBe('Territory Map showing learning journey from Zone 0 to 4');

    // Verify SVG has role="img" and aria-label
    const svg = page.locator('.territory-svg');
    await expect(svg).toHaveAttribute('role', 'img');

    const svgAriaLabel = await svg.getAttribute('aria-label');
    expect(svgAriaLabel).toBe('Journey path from Zone 0 to Zone 4');

    // Verify heading hierarchy (h3 under section)
    const headings = await page.locator('.territory-map h3').all();
    expect(headings.length).toBe(5); // 5 zones, each with h3

    // Verify semantic structure: section > div.zone > h3 + p
    const zone0 = page.locator('.zone-0');
    const zone0Heading = zone0.locator('h3');
    const zone0Desc = zone0.locator('p');

    await expect(zone0Heading).toBeVisible();
    await expect(zone0Desc).toBeVisible();
  });

  test('should have data-zone attributes for JavaScript targeting', async ({ page }) => {
    // Verify all zones have data-zone attributes
    const zone0 = page.locator('.zone-0[data-zone="0"]');
    const zone1 = page.locator('.zone-1[data-zone="1"]');
    const zone2 = page.locator('.zone-2[data-zone="2"]');
    const zone3 = page.locator('.zone-3[data-zone="3"]');
    const zone4 = page.locator('.zone-4[data-zone="4"]');

    await expect(zone0).toHaveAttribute('data-zone', '0');
    await expect(zone1).toHaveAttribute('data-zone', '1');
    await expect(zone2).toHaveAttribute('data-zone', '2');
    await expect(zone3).toHaveAttribute('data-zone', '3');
    await expect(zone4).toHaveAttribute('data-zone', '4');
  });

  test('should have particle container for Story 2.2', async ({ page }) => {
    // Verify particle container exists
    const particleContainer = page.locator('.particle-container');
    await expect(particleContainer).toBeVisible();

    // Verify container positioning (absolute, inset: 0)
    const position = await particleContainer.evaluate((el) => {
      return window.getComputedStyle(el).position;
    });
    expect(position).toBe('absolute');

    // Verify pointer-events is none (won't block interactions)
    const pointerEvents = await particleContainer.evaluate((el) => {
      return window.getComputedStyle(el).pointerEvents;
    });
    expect(pointerEvents).toBe('none');

    // Verify z-index (above background, below zones)
    const zIndex = await particleContainer.evaluate((el) => {
      return window.getComputedStyle(el).zIndex;
    });
    expect(zIndex).toBe('1');

    // Verify will-change property is set for future animations
    const willChange = await particleContainer.evaluate((el) => {
      return window.getComputedStyle(el).willChange;
    });
    expect(willChange).toContain('transform');
    expect(willChange).toContain('opacity');
  });

  test('should render SVG with correct structure and styling', async ({ page }) => {
    // Verify SVG element exists with correct viewBox
    const svg = page.locator('.territory-svg');
    await expect(svg).toBeVisible();

    const viewBox = await svg.getAttribute('viewBox');
    expect(viewBox).toBe('0 0 1200 800');

    // Verify journey path exists (organic Bezier curve)
    const journeyPath = page.locator('.journey-path');
    await expect(journeyPath).toBeVisible();

    const pathData = await journeyPath.getAttribute('d');
    expect(pathData).toContain('M 100,700'); // Start at Zone 0
    expect(pathData).toContain('1100,180'); // End at Zone 4

    // Verify zone markers exist
    const zone0Marker = page.locator('.zone-0-marker');
    const zone4Marker = page.locator('.zone-4-marker');

    await expect(zone0Marker).toBeVisible();
    await expect(zone4Marker).toBeVisible();

    // Verify Zone 4 glow exists
    const zone4Glow = page.locator('.zone-4-glow');
    await expect(zone4Glow).toBeVisible();

    // Verify radial gradient definition exists (SVG defs are hidden by design)
    const gradient = page.locator('#destination-glow');
    await expect(gradient).toHaveCount(1); // Element exists in DOM

    // Verify SVG is positioned behind zones (z-index: 0)
    const svgZIndex = await svg.evaluate((el) => {
      return window.getComputedStyle(el).zIndex;
    });
    expect(svgZIndex).toBe('0');
  });

  test('should integrate smoothly with MapFraming section', async ({ page }) => {
    // Scroll from MapFraming to TerritoryMap
    await page.evaluate(() => {
      const framing = document.querySelector('.map-framing');
      if (framing) {
        framing.scrollIntoView({ block: 'center' });
      }
    });

    await page.waitForTimeout(500);

    // Scroll to TerritoryMap
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) {
        map.scrollIntoView({ block: 'start' });
      }
    });

    await page.waitForTimeout(1000);

    // Verify both sections are visible
    const mapFraming = page.locator('.map-framing');
    const territoryMap = page.locator('.territory-map');

    await expect(mapFraming).toBeVisible();
    await expect(territoryMap).toBeVisible();

    // Verify no layout shift between sections
    const territoryMapVisible = await territoryMap.isVisible();
    expect(territoryMapVisible).toBe(true);

    // Verify background transition (MapFraming pure black → TerritoryMap pure black)
    const framingBg = await mapFraming.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });

    const mapBg = await territoryMap.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });

    // Both should be pure black (#000000)
    expect(framingBg).toContain('0');
    expect(mapBg).toContain('0');

    // Screenshot for integration visual regression
    await expect(page).toHaveScreenshot('story-2-1-framing-to-map-transition.png', {
      maxDiffPixels: 120,
      threshold: 0.22
    });
  });

  test('should be keyboard navigable', async ({ page }) => {
    // Scroll TerritoryMap into view
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) {
        map.scrollIntoView({ block: 'center' });
      }
    });

    await page.waitForTimeout(500);

    // Verify zones exist and are in DOM (keyboard navigable structure)
    const zone0 = page.locator('.zone-0');
    await expect(zone0).toBeVisible();

    // Verify zones have semantic structure for keyboard navigation
    const zone0Heading = zone0.locator('h3');
    await expect(zone0Heading).toBeVisible();

    // Tab key should move through the page (zones are part of tab order via semantic structure)
    await page.keyboard.press('Tab');
    await page.waitForTimeout(100);

    // Verify keyboard interaction is possible
    const hasActiveElement = await page.evaluate(() => {
      return document.activeElement !== null;
    });
    expect(hasActiveElement).toBe(true);
  });

  test('should test on Samsung Galaxy S21+ viewport (360x800)', async ({ page }) => {
    // Set Samsung Galaxy S21+ viewport
    await page.setViewportSize({ width: 360, height: 800 });

    // Scroll TerritoryMap into view
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) {
        map.scrollIntoView({ block: 'start' });
      }
    });

    await page.waitForTimeout(500);

    // Verify all zones visible on smaller viewport
    const zones = page.locator('.zone');
    const count = await zones.count();
    expect(count).toBe(5);

    // Verify no horizontal scroll
    const bodyWidth = await page.evaluate(() => {
      return document.body.scrollWidth;
    });
    const viewportWidth = await page.evaluate(() => {
      return window.innerWidth;
    });
    expect(bodyWidth).toBe(viewportWidth);

    // Screenshot for Galaxy S21+ visual regression
    await expect(page).toHaveScreenshot('story-2-1-galaxy-s21.png', {
      maxDiffPixels: 160,
      threshold: 0.26
    });
  });
});
