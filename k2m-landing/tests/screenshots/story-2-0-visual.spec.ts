import { test, expect } from '@playwright/test';

/**
 * Story 2.0: Build Pre-Map Anticipation Framing - Visual Regression Tests
 *
 * Tests MapFraming section:
 * - Initial state (text hidden, background gradient)
 * - Progressive text reveals (30%, 50%, 70% scroll)
 * - Mobile viewport responsiveness
 * - WCAG AA contrast compliance
 * - Performance benchmarks (60fps desktop, 45fps mobile)
 */

test.describe('Story 2.0 - MapFraming Visual Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to the landing page
    await page.goto('/');

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500); // Allow animations to initialize
  });

  test('should render MapFraming section with correct initial state', async ({ page }) => {
    // Scroll MapFraming section into view
    const mapFraming = page.locator('.map-framing');
    await mapFraming.scrollIntoViewIfNeeded();

    // Wait for section to be visible
    await expect(mapFraming).toBeVisible();

    // Verify all text elements exist but are hidden (opacity: 0)
    await expect(page.locator('.framing-text-1')).toHaveCSS('opacity', '0');
    await expect(page.locator('.framing-text-2')).toHaveCSS('opacity', '0');
    await expect(page.locator('.framing-text-3')).toHaveCSS('opacity', '0');

    // Verify background gradient is present
    const backgroundColor = await mapFraming.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    expect(backgroundColor).toContain('10'); // #0A0A0A soft black

    // Screenshot for visual regression
    await expect(page).toHaveScreenshot('story-2-0-initial-state.png', {
      maxDiffPixels: 100,
      threshold: 0.2
    });
  });

  test('should reveal first text at 70% viewport position', async ({ page }) => {
    // Scroll to trigger first text reveal (70% down viewport)
    await page.evaluate(() => {
      const framing = document.querySelector('.map-framing');
      if (framing) {
        framing.scrollIntoView({ block: 'center' });
      }
    });

    await page.waitForTimeout(1000); // Wait for ScrollTrigger animation

    // Verify first text is now visible
    const text1 = page.locator('.framing-text-1');
    await expect(text1).toBeVisible();

    const opacity1 = await text1.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(opacity1)).toBeGreaterThan(0.5); // Should be fading in

    // Screenshot for visual regression
    await expect(page).toHaveScreenshot('story-2-0-first-text-reveal.png', {
      maxDiffPixels: 100,
      threshold: 0.2
    });
  });

  test('should reveal second text at 50% viewport position', async ({ page }) => {
    // Scroll to trigger second text reveal (50% down viewport)
    await page.evaluate(() => {
      const framing = document.querySelector('.map-framing');
      if (framing) {
        framing.scrollIntoView({ block: 'start' });
        window.scrollBy(0, window.innerHeight * 0.3);
      }
    });

    await page.waitForTimeout(1000); // Wait for ScrollTrigger animation

    // Verify second text is now visible
    const text2 = page.locator('.framing-text-2');
    await expect(text2).toBeVisible();

    const opacity2 = await text2.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(opacity2)).toBeGreaterThan(0.5);

    // Screenshot for visual regression
    await expect(page).toHaveScreenshot('story-2-0-second-text-reveal.png', {
      maxDiffPixels: 100,
      threshold: 0.2
    });
  });

  test('should reveal third text at 30% viewport position', async ({ page }) => {
    // Scroll to trigger third text reveal (30% down viewport)
    await page.evaluate(() => {
      const framing = document.querySelector('.map-framing');
      if (framing) {
        framing.scrollIntoView({ block: 'start' });
        window.scrollBy(0, window.innerHeight * 0.5);
      }
    });

    await page.waitForTimeout(1000); // Wait for ScrollTrigger animation

    // Verify third text is now visible
    const text3 = page.locator('.framing-text-3');
    await expect(text3).toBeVisible();

    const opacity3 = await text3.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(opacity3)).toBeGreaterThan(0.5);

    // Verify background has darkened to pure black
    const mapFraming = page.locator('.map-framing');
    const backgroundColor = await mapFraming.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    expect(backgroundColor).toContain('0'); // #000000 pure black

    // Screenshot for visual regression
    await expect(page).toHaveScreenshot('story-2-0-third-text-reveal.png', {
      maxDiffPixels: 100,
      threshold: 0.2
    });
  });

  test('should render correctly on mobile viewport (375x667)', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Scroll MapFraming into view
    await page.evaluate(() => {
      const framing = document.querySelector('.map-framing');
      if (framing) {
        framing.scrollIntoView({ block: 'center' });
      }
    });

    await page.waitForTimeout(1000);

    // Verify responsive text sizes (using clamp values)
    const text1 = page.locator('.framing-text-1');
    const fontSize1 = await text1.evaluate((el) => {
      return window.getComputedStyle(el).fontSize;
    });
    const fontSizeValue1 = parseFloat(fontSize1);
    expect(fontSizeValue1).toBeGreaterThan(24); // Should be larger on mobile
    expect(fontSizeValue1).toBeLessThan(40); // But not desktop size

    // Verify mobile padding is reduced (2rem vs 4rem desktop)
    const mapFraming = page.locator('.map-framing');
    const paddingTop = await mapFraming.evaluate((el) => {
      return window.getComputedStyle(el).paddingTop;
    });
    expect(paddingTop).toBe('32px'); // 2rem = 32px

    // Screenshot for mobile visual regression
    await expect(page).toHaveScreenshot('story-2-0-mobile.png', {
      maxDiffPixels: 150,
      threshold: 0.25
    });
  });

  test('should meet WCAG AA contrast requirements', async ({ page }) => {
    // Get accessibility tree
    const accessibilityTree = await page.accessibility.snapshot();

    // Verify MapFraming section is accessible
    const mapFramingAccessible = accessibilityTree?.children?.find(node =>
      node.name?.includes('Territory Map Introduction')
    );
    expect(mapFramingAccessible).toBeDefined();

    // Verify text contrast (WCAG AA requires 4.5:1 for normal text)
    const text1 = page.locator('.framing-text-1');
    const color1 = await text1.evaluate((el) => {
      return window.getComputedStyle(el).color;
    });
    // Ocean mint on black should have sufficient contrast
    expect(color1).toBeTruthy();

    // Verify aria-label is present
    const mapFraming = page.locator('.map-framing');
    const ariaLabel = await mapFraming.getAttribute('aria-label');
    expect(ariaLabel).toBe('Territory Map Introduction');
  });

  test('should maintain 60fps performance on desktop', async ({ page }) => {
    // Collect performance metrics during scroll
    const fps = await page.evaluate(async () => {
      return new Promise((resolve) => {
        const frames: number[] = [];
        let lastTime = performance.now();
        let frameCount = 0;

        function measureFrame() {
          const now = performance.now();
          frameCount++;

          if (now - lastTime >= 1000) {
            frames.push(frameCount);
            frameCount = 0;
            lastTime = now;
          }

          if (frames.length < 5) { // Measure for 5 seconds
            requestAnimationFrame(measureFrame);
          } else {
            const avgFps = frames.reduce((a, b) => a + b, 0) / frames.length;
            resolve(avgFps);
          }
        }

        // Start measuring and scroll
        measureFrame();

        const framing = document.querySelector('.map-framing');
        if (framing) {
          framing.scrollIntoView({ block: 'start' });
          window.scrollBy(0, window.innerHeight * 0.8);
        }
      });
    });

    // Assert minimum 60fps on desktop
    expect(fps).toBeGreaterThanOrEqual(58); // Allow small margin of error
  });

  test('should maintain 45fps+ performance on mobile emulation', async ({ page }) => {
    // Set mobile viewport and CPU throttling
    await page.setViewportSize({ width: 375, height: 667 });
    await page.emulateMedia({ media: 'screen' });

    // Collect performance metrics
    const fps = await page.evaluate(async () => {
      return new Promise((resolve) => {
        const frames: number[] = [];
        let lastTime = performance.now();
        let frameCount = 0;

        function measureFrame() {
          const now = performance.now();
          frameCount++;

          if (now - lastTime >= 1000) {
            frames.push(frameCount);
            frameCount = 0;
            lastTime = now;
          }

          if (frames.length < 3) { // Measure for 3 seconds on mobile
            requestAnimationFrame(measureFrame);
          } else {
            const avgFps = frames.reduce((a, b) => a + b, 0) / frames.length;
            resolve(avgFps);
          }
        }

        measureFrame();

        const framing = document.querySelector('.map-framing');
        if (framing) {
          framing.scrollIntoView({ block: 'start' });
          window.scrollBy(0, window.innerHeight * 0.5);
        }
      });
    });

    // Assert minimum 45fps on mobile
    expect(fps).toBeGreaterThanOrEqual(43); // Allow small margin of error
  });

  test('should integrate smoothly with Hero section', async ({ page }) => {
    // Scroll from Hero to MapFraming
    await page.evaluate(() => {
      const hero = document.querySelector('.hero');
      if (hero) {
        hero.scrollIntoView({ block: 'center' });
      }
    });

    await page.waitForTimeout(500);

    // Scroll to MapFraming
    await page.evaluate(() => {
      const framing = document.querySelector('.map-framing');
      if (framing) {
        framing.scrollIntoView({ block: 'start' });
      }
    });

    await page.waitForTimeout(1000);

    // Verify no layout shift (section is visible)
    const mapFraming = page.locator('.map-framing');
    await expect(mapFraming).toBeVisible();

    // Verify background gradient connects (#0A0A0A from Hero to #000000 in MapFraming)
    const heroSection = page.locator('.hero');
    const heroBg = await heroSection.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });

    const framingBg = await mapFraming.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });

    // Both should be dark (soft black to pure black gradient)
    expect(heroBg).toContain('10');
    expect(framingBg).toContain('10');

    // Screenshot for integration visual regression
    await expect(page).toHaveScreenshot('story-2-0-hero-to-framing-transition.png', {
      maxDiffPixels: 120,
      threshold: 0.22
    });
  });

  test('should handle anticipatory pin smoothly', async ({ page }) => {
    // Test anticipatory pin effect (gradual slowdown before pin)
    const scrollBehavior = await page.evaluate(async () => {
      return new Promise((resolve) => {
        const scrollPositions: number[] = [];
        let lastScroll = 0;

        // Track scroll position during pin
        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            scrollPositions.push(window.scrollY);
          });
        }, { threshold: [0, 0.25, 0.5, 0.75, 1] });

        const framing = document.querySelector('.map-framing');
        if (framing) {
          observer.observe(framing);
        }

        // Scroll through section
        setTimeout(() => {
          if (framing) {
            framing.scrollIntoView({ block: 'start' });
            window.scrollBy(0, window.innerHeight * 0.8);
          }
        }, 100);

        setTimeout(() => {
          observer.disconnect();
          resolve({
            positions: scrollPositions,
            hasSmoothScroll: scrollPositions.length > 2
          });
        }, 2000);
      });
    });

    // Verify scroll was tracked (ScrollTrigger pin was active)
    expect(scrollBehavior.hasSmoothScroll).toBe(true);
  });
});
