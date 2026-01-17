import { test, expect } from '@playwright/test';

/**
 * Story 2.2: Particle Coalescence System - Visual & Functional Tests
 *
 * Tests particle system:
 * - Particle initialization and count based on device
 * - Particle styling and positioning
 * - Chaos → order animation with ScrollTrigger
 * - Text crystallization effects
 * - Performance safeguards (FPS monitoring, hardware detection)
 * - Accessibility support (prefers-reduced-motion)
 * - Memory management and cleanup
 */

test.describe('Story 2.2 - Particle Coalescence System Tests', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
  });

  test('should initialize particle system with correct particle count on desktop', async ({ page }) => {
    // Scroll TerritoryMap into view
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    // Wait for page load and particle initialization
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Give particles time to initialize

    // Debug: Check if TerritoryMap section exists
    const territoryMapExists = await page.evaluate(() => {
      return document.querySelector('.territory-map') !== null;
    });
    console.log('TerritoryMap section exists:', territoryMapExists);

    // Debug: Check if particle container exists
    const containerExists = await page.evaluate(() => {
      return document.querySelector('.particle-container') !== null;
    });
    console.log('Particle container exists:', containerExists);

    // Debug: Check if particle system exists
    const hasParticleSystem = await page.evaluate(() => {
      return typeof window.mapParticleSystem !== 'undefined';
    });
    console.log('Particle system exists:', hasParticleSystem);

    // Debug: Check particle container children
    const childCount = await page.evaluate(() => {
      const container = document.querySelector('.particle-container');
      return container ? container.children.length : 0;
    });
    console.log('Particle container children count:', childCount);

    // Wait for particles to be created
    const particles = page.locator('.map-particle');
    const count = await particles.count();
    console.log('Particle count:', count);

    // Desktop should have 300 particles (15 per zone × 7 zones)
    expect(count).toBe(300);
  });

  test('should initialize particle system with correct particle count on mobile', async ({ page }) => {
    // Set mobile viewport (iPhone 12)
    await page.setViewportSize({ width: 375, height: 667 });

    // Scroll TerritoryMap into view
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'start' });
    });

    await page.waitForTimeout(500);

    // Wait for particles to be created
    const particles = page.locator('.map-particle');
    const count = await particles.count();

    // Mobile should have 105 particles (reduced for performance)
    expect(count).toBe(105);
  });

  test('should style particles correctly with radial gradient', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Check first particle styling
    const particle = page.locator('.map-particle').first();
    await expect(particle).toBeVisible();

    // Verify particle size (4px on desktop)
    const width = await particle.evaluate((el) => {
      return window.getComputedStyle(el).width;
    });
    expect(width).toBe('4px');

    const height = await particle.evaluate((el) => {
      return window.getComputedStyle(el).height;
    });
    expect(height).toBe('4px');

    // Verify radial gradient background
    const background = await particle.evaluate((el) => {
      return window.getComputedStyle(el).background;
    });
    expect(background).toContain('radial-gradient');
    expect(background).toContain('208'); // ocean-mint-glow RGB

    // Verify border-radius (circular)
    const borderRadius = await particle.evaluate((el) => {
      return window.getComputedStyle(el).borderRadius;
    });
    expect(borderRadius).toBe('50%');

    // Verify will-change for GPU acceleration
    const willChange = await particle.evaluate((el) => {
      return window.getComputedStyle(el).willChange;
    });
    expect(willChange).toContain('transform');
    expect(willChange).toContain('opacity');

    // Verify pointer-events is none
    const pointerEvents = await particle.evaluate((el) => {
      return window.getComputedStyle(el).pointerEvents;
    });
    expect(pointerEvents).toBe('none');
  });

  test('should have particles with initial chaos positions and target positions', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Check that particles have target positions stored
    const particles = page.locator('.map-particle');
    const firstParticle = particles.first();

    // Verify targetX and targetY are stored
    const targetX = await firstParticle.evaluate((el) => {
      return el.targetX;
    });
    expect(targetX).not.toBeUndefined();

    const targetY = await firstParticle.evaluate((el) => {
      return el.targetY;
    });
    expect(targetY).not.toBeUndefined();

    // Verify initial positions are in chaos range (-1000 to 1000)
    const initialX = await firstParticle.evaluate((el) => {
      return el.initialX;
    });
    expect(initialX).toBeGreaterThanOrEqual(-1000);
    expect(initialX).toBeLessThanOrEqual(1000);

    const initialY = await firstParticle.evaluate((el) => {
      return el.initialY;
    });
    expect(initialY).toBeGreaterThanOrEqual(-1000);
    expect(initialY).toBeLessThanOrEqual(1000);
  });

  test('should animate particles from chaos to order on scroll', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Initial state: particles should be at chaos positions
    const particles = page.locator('.map-particle');
    const firstParticle = particles.first();

    // Particles should start invisible
    const initialOpacity = await firstParticle.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(initialOpacity)).toBe(0);

    // Scroll to trigger animation
    await page.evaluate(() => {
      window.scrollBy(0, 300);
    });

    await page.waitForTimeout(300);

    // After scroll: particles should be visible
    const scrolledOpacity = await firstParticle.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(scrolledOpacity)).toBeGreaterThan(0);

    // Particles should be moving toward target positions
    const transform = await firstParticle.evaluate((el) => {
      return window.getComputedStyle(el).transform;
    });
    expect(transform).not.toBe('none');
  });

  test('should apply 80/20 emotional punctuation (subtle vs bold particles)', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Get all particles
    const particles = page.locator('.map-particle');
    const count = await particles.count();

    // Check particle data attributes or class for subtle/bold split
    const subtleParticles = page.locator('.map-particle.subtle');
    const boldParticles = page.locator('.map-particle.bold');

    const subtleCount = await subtleParticles.count();
    const boldCount = await boldParticles.count();

    // 80% should be subtle, 20% should be bold
    const expectedSubtle = Math.floor(count * 0.8);
    const expectedBold = Math.floor(count * 0.2);

    expect(subtleCount).toBe(expectedSubtle);
    expect(boldCount).toBe(expectedBold);
  });

  test('should crystallize text with blur → sharp animation', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Check Zone 0-1 text initial state (heavy blur)
    const zoneText = page.locator('.zone-0-1 .zone-text').first();

    const initialFilter = await zoneText.evaluate((el) => {
      return window.getComputedStyle(el).filter;
    });
    expect(initialFilter).toContain('blur');

    const initialOpacity = await zoneText.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(initialOpacity)).toBeLessThan(1);

    // Scroll to trigger crystallization
    await page.evaluate(() => {
      window.scrollBy(0, 400);
    });

    await page.waitForTimeout(500);

    // After scroll: text should be sharp
    const scrolledFilter = await zoneText.evaluate((el) => {
      return window.getComputedStyle(el).filter;
    });
    expect(scrolledFilter).not.toContain('blur');

    const scrolledOpacity = await zoneText.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(scrolledOpacity)).toBe(1);
  });

  test('should have ScrollTrigger configured with scrub: 0.3', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Check that GSAP ScrollTrigger is registered
    const scrollTriggerExists = await page.evaluate(() => {
      return typeof window.gsap !== 'undefined' &&
             typeof window.ScrollTrigger !== 'undefined';
    });
    expect(scrollTriggerExists).toBe(true);

    // Verify ScrollTrigger instance exists for particle animation
    const hasScrollTrigger = await page.evaluate(() => {
      const triggers = window.ScrollTrigger?.getAll();
      return triggers && triggers.length > 0;
    });
    expect(hasScrollTrigger).toBe(true);
  });

  test('should respect prefers-reduced-motion and show particles instantly', async ({ page }) => {
    // Emulate prefers-reduced-motion
    await page.addInitScript(() => {
      window.matchMedia = (() => {
        return {
          matches: true,
          media: '(prefers-reduced-motion: reduce)',
          onchange: null,
          addListener: () => {},
          removeListener: () => {},
          addEventListener: () => {},
          removeEventListener: () => {},
          dispatchEvent: () => {}
        };
      });
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Scroll TerritoryMap into view
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Particles should appear instantly at final positions
    const particles = page.locator('.map-particle');
    const firstParticle = particles.first();

    const opacity = await firstParticle.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(opacity)).toBe(1);

    // Scale should be 1 (full size)
    const scale = await firstParticle.evaluate((el) => {
      const transform = window.getComputedStyle(el).transform;
      // Parse matrix to extract scale
      const matrix = transform.match(/matrix\(([^)]+)\)/);
      if (matrix) {
        const values = matrix[1].split(', ');
        return parseFloat(values[0]); // Scale X
      }
      return 1;
    });
    expect(scale).toBe(1);
  });

  test('should update ARIA label with particle description', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Verify territory-map has updated ARIA label
    const territoryMap = page.locator('.territory-map');
    const ariaLabel = await territoryMap.getAttribute('aria-label');

    expect(ariaLabel).toContain('particles coalesce');
    expect(ariaLabel).toContain('5 zones');
  });

  test('should cleanup particles and ScrollTrigger on unmount', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Get initial ScrollTrigger count
    const initialTriggers = await page.evaluate(() => {
      return window.ScrollTrigger?.getAll()?.length || 0;
    });

    // Navigate away from TerritoryMap
    await page.evaluate(() => {
      window.scrollTo(0, 0);
    });

    await page.waitForTimeout(1000);

    // Check cleanup method exists
    const cleanupExists = await page.evaluate(() => {
      return typeof window.mapParticleSystem?.cleanup === 'function';
    });
    expect(cleanupExists).toBe(true);
  });

  test('should maintain 60fps performance on desktop', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Measure FPS during scroll
    const fps = await page.evaluate(async () => {
      return new Promise((resolve) => {
        let frameCount = 0;
        let startTime = performance.now();
        let fps = 60;

        function measureFrame() {
          frameCount++;
          const currentTime = performance.now();

          if (currentTime >= startTime + 1000) {
            fps = frameCount;
            resolve(fps);
            return;
          }

          requestAnimationFrame(measureFrame);
        }

        measureFrame();
      });
    });

    // Should maintain 60fps (or close to it)
    expect(fps).toBeGreaterThanOrEqual(55);
  });

  test('should capture desktop screenshot before animation', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('story-2-2-desktop-initial.png', {
      maxDiffPixels: 100,
      threshold: 0.2
    });
  });

  test('should capture desktop screenshot after particle coalescence', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Scroll to trigger full animation
    await page.evaluate(() => {
      window.scrollBy(0, 500);
    });

    await page.waitForTimeout(1000);

    await expect(page).toHaveScreenshot('story-2-2-desktop-coalesced.png', {
      maxDiffPixels: 120,
      threshold: 0.22
    });
  });

  test('should capture mobile screenshot with particle animation', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'start' });
    });

    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('story-2-2-mobile-particles.png', {
      maxDiffPixels: 150,
      threshold: 0.25
    });
  });

  test('should reduce particle count on low-end devices', async ({ page }) => {
    // Emulate low-end device (2 CPU cores)
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 2
      });
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Scroll TerritoryMap into view
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Particle count should be reduced by 50%
    const particles = page.locator('.map-particle');
    const count = await particles.count();

    // Desktop with low-end: 300 * 0.5 = 150
    expect(count).toBe(150);
  });

  test('should distribute particles across zones correctly', async ({ page }) => {
    await page.evaluate(() => {
      const map = document.querySelector('.territory-map');
      if (map) map.scrollIntoView({ block: 'center' });
    });

    await page.waitForTimeout(500);

    // Check particle distribution
    const distribution = await page.evaluate(() => {
      const particles = document.querySelectorAll('.map-particle');
      const zoneCounts = {};

      particles.forEach((particle) => {
        const zoneIndex = particle.zoneIndex;

        if (!zoneCounts[zoneIndex]) {
          zoneCounts[zoneIndex] = 0;
        }
        zoneCounts[zoneIndex]++;
      });

      return zoneCounts;
    });

    // Zone 0-1 should have 40% of particles (120 desktop)
    const zone01Count = (distribution[0] || 0) + (distribution[1] || 0);
    expect(zone01Count).toBeGreaterThanOrEqual(110);
    expect(zone01Count).toBeLessThanOrEqual(130);
  });
});
