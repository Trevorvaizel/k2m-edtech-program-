import { test, expect } from '@playwright/test';

/**
 * Minimal debug test to isolate HTML loading issue
 * Tests if main.js executes and HTML is inserted into DOM
 */

test.describe('Debug: HTML Loading Issue', () => {

  test('should load index.html', async ({ page }) => {
    await page.goto('/');

    // Check if we're on the right page
    const title = await page.title();
    console.log('Page title:', title);
    expect(title).toBe('k2m-landing');
  });

  test('should have app container', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check if #app container exists
    const appContainer = page.locator('#app');
    await expect(appContainer).toHaveCount(1);
    console.log('✅ App container exists');
  });

  test('should load main.js module', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Check if main.js loaded by looking for side effects
    const hasLogs = await page.evaluate(() => {
      // Check if any sections were loaded
      const hero = document.querySelector('.hero-section');
      const mapFraming = document.querySelector('.map-framing');
      const territoryMap = document.querySelector('.territory-map');

      return {
        hero: !!hero,
        mapFraming: !!mapFraming,
        territoryMap: !!territoryMap,
        appHTML: document.getElementById('app')?.innerHTML.length || 0
      };
    });

    console.log('Main.js loaded sections:', hasLogs);
    console.log('App container HTML length:', hasLogs.appHTML);
  });

  test('should have content in app container', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const appContent = await page.evaluate(() => {
      const app = document.getElementById('app');
      if (!app) return { error: 'No app container' };

      return {
        innerHTMLLength: app.innerHTML.length,
        childElementCount: app.childElementCount,
        hasHero: !!app.querySelector('.hero-section'),
        hasMapFraming: !!app.querySelector('.map-framing'),
        hasTerritoryMap: !!app.querySelector('.territory-map'),
        firstChild: app.firstElementChild?.className || 'none'
      };
    });

    console.log('App container content:', JSON.stringify(appContent, null, 2));
  });

  test('should check for JavaScript errors', async ({ page }) => {
    const errors: string[] = [];

    page.on('pageerror', (error) => {
      errors.push(error.toString());
      console.log('JS Error:', error.message);
    });

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        console.log('Console error:', msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    console.log('Total JS errors:', errors.length);
    if (errors.length > 0) {
      console.log('Errors:', errors);
    }
  });

  test('should check if main.js executed', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const mainJsExecuted = await page.evaluate(() => {
      // Check for console logs that main.js should produce
      return {
        appContainerExists: !!document.getElementById('app'),
        windowHasGSAP: typeof window.gsap !== 'undefined',
        windowHasLenis: typeof window.lenis !== 'undefined',
        bodyChildren: document.body.childElementCount
      };
    });

    console.log('main.js execution check:', mainJsExecuted);
  });

  test('should manually trigger HTML insertion', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Try manually inserting HTML like main.js does
    const manualInsert = await page.evaluate(async () => {
      try {
        // Fetch the HTML files
        const heroResponse = await fetch('/src/components/Hero/Hero.html?raw');
        const heroHtml = await heroResponse.text();

        const mapFramingResponse = await fetch('/src/components/TerritoryMap/MapFraming.html?raw');
        const mapFramingHtml = await mapFramingResponse.text();

        const territoryMapResponse = await fetch('/src/components/TerritoryMap/TerritoryMap.html?raw');
        const territoryMapHtml = await territoryMapResponse.text();

        // Insert into app
        const app = document.getElementById('app');
        if (app) {
          app.innerHTML = heroHtml + mapFramingHtml + territoryMapHtml;
          return {
            success: true,
            heroLength: heroHtml.length,
            mapFramingLength: mapFramingHtml.length,
            territoryMapLength: territoryMapHtml.length,
            hasTerritoryMap: !!document.querySelector('.territory-map')
          };
        }

        return { success: false, error: 'No app container' };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });

    console.log('Manual HTML insertion result:', manualInsert);
  });
});
