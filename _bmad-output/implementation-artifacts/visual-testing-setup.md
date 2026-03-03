# Visual Testing Setup Guide for K2M Landing Page

**Document Version:** 1.0
**Last Updated:** 2026-01-15
**Project:** K2M EdTech Awwwards-Level Landing Page
**Purpose:** Complete automated visual testing setup with Playwright for development-time visual feedback

---

## Table of Contents

1. [Installation & Configuration](#1-installation--configuration)
2. [Screenshot Tests for Hero Section](#2-screenshot-tests-for-hero-section)
3. [Screenshot Tests for All Sections](#3-screenshot-tests-for-all-sections)
4. [Animation Milestone Tests](#4-animation-milestone-tests)
5. [Video Recording for Smooth Scroll](#5-video-recording-for-smooth-scroll)
6. [Visual Regression Testing](#6-visual-regression-testing)
7. [Test Runner Scripts](#7-test-runner-scripts)
8. [Integration with Epic Workflow](#8-integration-with-epic-workflow)
9. [Multi-Viewport Testing](#9-multi-viewport-testing)
10. [Visual Testing Workflow Documentation](#10-visual-testing-workflow-documentation)

---

## 1. Installation & Configuration

### 1.1 Install Playwright and Dependencies

**Step 1: Install Playwright**
```bash
npm install -D @playwright/test
```

**What This Installs:**
- `@playwright/test` - Playwright test runner
- `@playwright/experimental-ct` - Component testing (optional, for future)
- TypeScript support (if using TypeScript)

**Step 2: Install Browsers**
```bash
npx playwright install chromium firefox webkit
```

**What This Installs:**
- **Chromium** (Chrome/Edge base) - ~170MB
- **Firefox** - ~80MB
- **WebKit** (Safari base) - ~70MB

**Optional: Install specific browsers only**
```bash
# Install Chromium only (smaller download, ~170MB)
npx playwright install chromium

# Install Chromium + Firefox (no WebKit)
npx playwright install chromium firefox
```

**Recommended:** Install all 3 browsers initially to ensure cross-browser compatibility from the start.

---

### 1.2 Create Playwright Configuration

**Create file:** `playwright.config.js` in project root

```javascript
import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for K2M Landing Page
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Test location
  testDir: './tests',

  // Test settings
  fullyParallel: true,
  forbidOnly: !!process.env.CI, // Fail if `test.only` is committed
  retries: process.env.CI ? 2 : 0, // Retry 2x in CI, 0x locally
  workers: process.env.CI ? 1 : undefined, // Run sequentially in CI, parallel locally

  // Reporter
  reporter: 'html', // Generates HTML report at the end

  // Global settings for all tests
  use: {
    // Base URL for tests (Vite dev server)
    baseURL: 'http://localhost:5173',

    // Collect trace when retrying (helps debug failures)
    trace: 'on-first-retry',

    // Screenshot settings
    screenshot: 'only-on-failure', // Capture screenshots only when tests fail

    // Video recording
    video: 'retain-on-failure', // Keep videos only when tests fail
  },

  // Projects (browser + viewport combinations)
  projects: [
    {
      name: 'chromium-desktop',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox-desktop',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit-desktop',
      use: { ...devices['Desktop Safari'] },
    },

    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Web Server (start Vite dev server automatically)
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI, // Don't start if already running (local dev)
    timeout: 120 * 1000, // 2 minutes to start
  },
});
```

**Key Settings Explained:**
- `testDir: './tests'` - All visual tests go in `tests/` directory
- `baseURL: 'http://localhost:5173'` - Vite dev server URL
- `webServer` - Auto-starts Vite before tests run
- `screenshot: 'only-on-failure'` - Captures screenshots when tests fail (we'll override for visual tests)
- `video: 'retain-on-failure'` - Keeps videos when tests fail
- `projects` - Runs tests on 5 configurations: 3 desktop browsers + 2 mobile

---

### 1.3 Create Directory Structure

**Run these commands to create directories:**
```bash
# Test directories
mkdir -p tests/hero
mkdir -p tests/map
mkdir -p tests/discord
mkdir -p tests/cta
mkdir -p tests/animations
mkdir -p tests/smooth-scroll

# Output directories
mkdir -p _bmad-output/test-artifacts/screenshots
mkdir -p _bmad-output/test-artifacts/animations
mkdir -p _bmad-output/test-artifacts/videos
mkdir -p _bmad-output/test-artifacts/baselines
```

**Directory Structure:**
```
k2m-edtech-program-/
├── playwright.config.js          ← Configuration file
├── package.json                  ← Add test scripts here
├── tests/                        ← All test files
│   ├── hero/
│   │   └── hero-visual.spec.ts
│   ├── map/
│   │   └── map-visual.spec.ts
│   ├── discord/
│   │   └── discord-visual.spec.ts
│   ├── cta/
│   │   └── cta-visual.spec.ts
│   ├── animations/
│   │   └── animation-timeline.spec.ts
│   └── smooth-scroll/
│       └── smooth-scroll.spec.ts
└── _bmad-output/
    └── test-artifacts/
        ├── screenshots/          ← Screenshots from tests
        ├── animations/           ← Animation milestone screenshots
        ├── videos/               ← Video recordings
        └── baselines/            ← Baseline images for regression testing
```

---

### 1.4 Add NPM Scripts

**Update `package.json` scripts section:**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",

    // Visual testing scripts
    "test:visual": "playwright test",
    "test:visual:headed": "playwright test --headed", // Show browser window
    "test:visual:debug": "playwright test --debug",    // Debug mode with inspector
    "test:visual:update": "playwright test --update-snapshots", // Update baselines
    "test:visual:report": "playwright show-report"     // View HTML report
  }
}
```

**Script Explanations:**
- `npm run test:visual` - Run all visual tests (headless)
- `npm run test:visual:headed` - Run tests with visible browser (debugging)
- `npm run test:visual:debug` - Run tests with Playwright Inspector (step-through debugging)
- `npm run test:visual:update` - Update baseline screenshots (after intentional changes)
- `npm run test:visual:report` - Open HTML test report in browser

---

### 1.5 Verify Installation

**Test Playwright is installed correctly:**
```bash
# Run Playwright's example tests (creates tests/example.spec.ts)
npx playwright test --reporter=line

# Expected output: Example tests pass
```

**Verify browsers are installed:**
```bash
npx playwright --version
# Expected output: Version x.x.x
```

**Check Vite server starts:**
```bash
npm run dev
# Expected output: Server running at http://localhost:5173
```

---

## 2. Screenshot Tests for Hero Section

### 2.1 Create Hero Visual Test

**Create file:** `tests/hero/hero-visual.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Hero Section - Visual Tests', () => {
  // Desktop viewport (1920x1080)
  test('should render Hero section correctly on desktop', async ({ page }) => {
    // Navigate to Hero section
    await page.goto('/#hero');
    await page.waitForLoadState('networkidle');

    // Wait for GSAP animations to complete (if any)
    await page.waitForTimeout(1500);

    // Capture Hero section screenshot
    await page.locator('#hero').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/hero/hero-desktop.png',
    });

    // Verify key elements are visible
    await expect(page.locator('text=You are not behind')).toBeVisible();
    await expect(page.locator('button >> text=Start Diagnostic')).toBeVisible();
  });

  // Tablet viewport (768x1024)
  test('should render Hero section correctly on tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/#hero');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Capture screenshot
    await page.locator('#hero').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/hero/hero-tablet.png',
    });

    // Verify text is readable
    await expect(page.locator('text=You are not behind')).toBeVisible();
  });

  // Mobile viewport (375x812 - iPhone X)
  test('should render Hero section correctly on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/#hero');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Capture screenshot
    await page.locator('#hero').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/hero/hero-mobile.png',
    });

    // Verify CTA button is above fold on mobile
    const heroSection = page.locator('#hero');
    const ctaButton = page.locator('button >> text=Start Diagnostic');

    // Check if button is visible within viewport
    await expect(heroSection).toBeVisible();
    await expect(ctaButton).toBeVisible();
  });

  // Full page screenshot (includes any overflow)
  test('should capture full Hero section without clipping', async ({ page }) => {
    await page.goto('/#hero');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Capture full page (scrolls if needed)
    await page.screenshot({
      path: '_bmad-output/test-artifacts/screenshots/hero/hero-full-page-desktop.png',
      fullPage: true,
    });
  });
});
```

---

### 2.2 Run Hero Visual Tests

**Execute Hero tests:**
```bash
# Run only Hero tests
npx playwright test tests/hero/

# Run with visible browser (for debugging)
npx playwright test tests/hero/ --headed

# Run in debug mode (step through tests)
npx playwright test tests/hero/ --debug
```

**Expected Output:**
```
Running 4 tests using 5 workers

  ✓ [chromium-desktop] › hero-visual.spec.ts:9:3 › should render Hero section correctly on desktop (2.5s)
  ✓ [firefox-desktop] › hero-visual.spec.ts:9:3 › should render Hero section correctly on desktop (2.3s)
  ✓ [webkit-desktop] › hero-visual.spec.ts:9:3 › should render Hero section correctly on desktop (2.7s)
  ✓ [mobile-chrome] › hero-visual.spec.ts:9:3 › should render Hero section correctly on desktop (2.1s)

  4 passed (12s)
```

**View Screenshots:**
```bash
# Open screenshots folder
ls _bmad-output/test-artifacts/screenshots/hero/

# Expected files:
# - hero-desktop.png
# - hero-tablet.png
# - hero-mobile.png
# - hero-full-page-desktop.png
```

---

### 2.3 Hero Test Checklist

**Verify these visual elements:**
- [ ] Headline text is readable and not clipped
- [ ] Subheadline text is readable
- [ ] CTA button is visible and above fold (especially mobile)
- [ ] Background/image loads correctly
- [ ] No horizontal scroll (overflow-x)
- [ ] Text contrast is sufficient (readable on background)
- [ ] Spacing/padding looks correct
- [ ] GSAP animations complete (text revealed, elements animated in)

**Common Issues to Catch:**
- ❌ Text cut off on mobile (overflow)
- ❌ CTA button below fold on mobile (poor UX)
- ❌ Image doesn't load (broken image icon)
- ❌ Text too small on mobile (readability)
- ❌ Horizontal scrollbar (layout too wide)

---

## 3. Screenshot Tests for All Sections

### 3.1 Territory Map Visual Test

**Create file:** `tests/map/map-visual.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Territory Map Section - Visual Tests', () => {
  test('should render Map section on desktop', async ({ page }) => {
    await page.goto('/#map');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500); // Wait for animations

    await page.locator('#map').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/map/map-desktop.png',
    });

    // Verify all 5 zones are visible
    for (let i = 0; i <= 4; i++) {
      await expect(page.locator(`.zone-${i}`)).toBeVisible();
    }
  });

  test('should render Map section on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/#map');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await page.locator('#map').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/map/map-mobile.png',
    });

    // Verify zones are stacked vertically on mobile
    const mapSection = page.locator('#map');
    await expect(mapSection).toBeVisible();
  });

  test('should capture all 5 zones individually', async ({ page }) => {
    await page.goto('/#map');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Screenshot each zone
    for (let i = 0; i <= 4; i++) {
      await page.locator(`.zone-${i}`).screenshot({
        path: `_bmad-output/test-artifacts/screenshots/map/zone-${i}-desktop.png`,
      });
    }
  });
});
```

---

### 3.2 Discord Section Visual Test

**Create file:** `tests/discord/discord-visual.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Discord Section - Visual Tests', () => {
  test('should render Discord section on desktop', async ({ page }) => {
    await page.goto('/#discord');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await page.locator('#discord').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/discord/discord-desktop.png',
    });

    // Verify chat bubbles are visible
    await expect(page.locator('.chat-bubble').first()).toBeVisible();
  });

  test('should render Discord section on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/#discord');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await page.locator('#discord').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/discord/discord-mobile.png',
    });

    // Verify community preview is visible
    await expect(page.locator('.discord-preview')).toBeVisible();
  });
});
```

---

### 3.3 CTA Section Visual Test

**Create file:** `tests/cta/cta-visual.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('CTA Section - Visual Tests', () => {
  test('should render CTA section on desktop', async ({ page }) => {
    await page.goto('/#cta');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await page.locator('#cta').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/cta/cta-desktop.png',
    });

    // Verify CTA button is prominent
    await expect(page.locator('button >> text=Start Diagnostic')).toBeVisible();
  });

  test('should render CTA section on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/#cta');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await page.locator('#cta').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/cta/cta-mobile.png',
    });

    // Verify form/button is easily tappable on mobile
    const ctaButton = page.locator('button >> text=Start Diagnostic');
    await expect(ctaButton).toBeVisible();

    // Check button size (min 44x44px for touch targets)
    const box = await ctaButton.boundingBox();
    expect(box?.height).toBeGreaterThanOrEqual(44);
    expect(box?.width).toBeGreaterThanOrEqual(44);
  });
});
```

---

### 3.4 Run All Section Tests

**Execute all section tests:**
```bash
# Run all visual tests
npm run test:visual

# Run specific sections
npx playwright test tests/hero/ tests/map/ tests/discord/ tests/cta/

# Expected output: ~15-20 tests (4 tests per section × 4 sections)
```

**Review all screenshots:**
```bash
# View all screenshots
ls _bmad-output/test-artifacts/screenshots/*/

# Expected structure:
# screenshots/
# ├── hero/
# │   ├── hero-desktop.png
# │   ├── hero-tablet.png
# │   └── hero-mobile.png
# ├── map/
# │   ├── map-desktop.png
# │   └── map-mobile.png
# ├── discord/
# │   ├── discord-desktop.png
# │   └── discord-mobile.png
# └── cta/
#     ├── cta-desktop.png
#     └── cta-mobile.png
```

---

## 4. Animation Milestone Tests

### 4.1 Capture Animation Frames

**Create file:** `tests/animations/animation-timeline.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Animation Timeline - Visual Tests', () => {
  test('should capture Hero text reveal animation', async ({ page }) => {
    await page.goto('/#hero');
    await page.waitForLoadState('networkidle');

    // Capture before animation (frame 0%)
    await page.screenshot({
      path: '_bmad-output/test-artifacts/animations/hero-reveal-0.png',
    });

    // Wait for animation to start (frame 50%)
    await page.waitForTimeout(750);
    await page.screenshot({
      path: '_bmad-output/test-artifacts/animations/hero-reveal-50.png',
    });

    // Wait for animation to complete (frame 100%)
    await page.waitForTimeout(750);
    await page.screenshot({
      path: '_bmad-output/test-artifacts/animations/hero-reveal-100.png',
    });

    // Verify final state
    await expect(page.locator('text=You are not behind')).toBeVisible();
  });

  test('should capture Territory Map particle coalescence', async ({ page }) => {
    await page.goto('/#map');
    await page.waitForLoadState('networkidle');

    // Before particles animate (0%)
    await page.screenshot({
      path: '_bmad-output/test-artifacts/animations/map-particles-0.png',
    });

    // Mid-animation (50%)
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: '_bmad-output/test-artifacts/animations/map-particles-50.png',
    });

    // After particles coalesce (100%)
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: '_bmad-output/test-artifacts/animations/map-particles-100.png',
    });
  });

  test('should capture Discord chat bubble animations', async ({ page }) => {
    await page.goto('/#discord');
    await page.waitForLoadState('networkidle');

    // Capture staggered chat bubble animations
    for (let i = 0; i <= 3; i++) {
      await page.waitForTimeout(500); // Wait for next bubble
      await page.screenshot({
        path: `_bmad-output/test-artifacts/animations/discord-bubble-${i}.png`,
      });
    }
  });

  test('should capture CTA hover animation', async ({ page }) => {
    await page.goto('/#cta');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Hover over CTA button
    const ctaButton = page.locator('button >> text=Start Diagnostic');
    await ctaButton.hover();

    // Wait for hover animation
    await page.waitForTimeout(300);

    // Capture hovered state
    await page.screenshot({
      path: '_bmad-output/test-artifacts/animations/cta-hover.png',
    });
  });
});
```

---

### 4.2 Run Animation Tests

**Execute animation tests:**
```bash
npx playwright test tests/animations/

# Expected output: 4 tests passed
```

**View animation frames:**
```bash
ls _bmad-output/test-artifacts/animations/

# Expected files:
# - hero-reveal-0.png (before animation)
# - hero-reveal-50.png (mid-animation)
# - hero-reveal-100.png (after animation)
# - map-particles-0.png, 50.png, 100.png
# - discord-bubble-0.png, 1.png, 2.png, 3.png
# - cta-hover.png
```

**What to Check:**
- [ ] Animations trigger correctly (elements visible before/after)
- [ ] Animation timing feels right (not too fast/slow)
- [ ] No janky transitions (smooth interpolation)
- [ ] Final state looks correct (elements in position)

---

## 5. Video Recording for Smooth Scroll

### 5.1 Configure Video Recording

**Video recording is already enabled in `playwright.config.js`:**
```javascript
use: {
  video: 'retain-on-failure', // Keeps videos on failure
},
```

**Enable video recording for all tests (add to config):**
```javascript
use: {
  video: 'on', // Record video for all tests
},
```

---

### 5.2 Create Smooth Scroll Video Test

**Create file:** `tests/smooth-scroll/smooth-scroll.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Smooth Scroll - Video Tests', () => {
  test('should record smooth scroll from Hero to Map', async ({ page }) => {
    await page.goto('/');

    // Start at Hero
    await page.locator('#hero').scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);

    // Smooth scroll to Map
    await page.evaluate(() => {
      window.scrollTo({ top: 1000, behavior: 'smooth' });
    });

    // Wait for scroll to complete
    await page.waitForTimeout(2000);

    // Video is automatically saved to:
    // _bmad-output/test-artifacts/videos/scroll-hero-to-map.webm
  });

  test('should record full page smooth scroll', async ({ page }) => {
    await page.goto('/');

    // Scroll through entire page
    await page.evaluate(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    await page.waitForTimeout(1000);

    await page.evaluate(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    });

    // Wait for full scroll
    await page.waitForTimeout(3000);

    // Video saved to: _bmad-output/test-artifacts/videos/full-page-scroll.webm
  });

  test('should verify 60fps on desktop', async ({ page }) => {
    await page.goto('/');

    // Measure FPS during scroll
    const fps = await page.evaluate(async () => {
      return new Promise((resolve) => {
        let frames = 0;
        let startTime = performance.now();

        function countFrames() {
          frames++;
          const elapsed = performance.now() - startTime;

          if (elapsed < 1000) {
            requestAnimationFrame(countFrames);
          } else {
            resolve(frames);
          }
        }

        requestAnimationFrame(countFrames);
      });
    });

    console.log(`Desktop FPS: ${fps}`);
    expect(fps).toBeGreaterThanOrEqual(55); // Allow 5fps margin (55-60fps)
  });

  test('should verify 45fps+ on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');

    // Measure FPS on mobile
    const fps = await page.evaluate(async () => {
      return new Promise((resolve) => {
        let frames = 0;
        let startTime = performance.now();

        function countFrames() {
          frames++;
          const elapsed = performance.now() - startTime;

          if (elapsed < 1000) {
            requestAnimationFrame(countFrames);
          } else {
            resolve(frames);
          }
        }

        requestAnimationFrame(countFrames);
      });
    });

    console.log(`Mobile FPS: ${fps}`);
    expect(fps).toBeGreaterThanOrEqual(40); // Allow 5fps margin (40-45fps+)
  });
});
```

---

### 5.3 Run Video Tests

**Execute video tests:**
```bash
npx playwright test tests/smooth-scroll/

# Expected output: 4 tests passed
```

**View videos:**
```bash
ls _bmad-output/test-artifacts/videos/

# Expected files:
# - scroll-hero-to-map.webm
# - full-page-scroll.webm
```

**Play videos:**
- Open `.webm` files in browser (Chrome, Firefox)
- Or use VLC media player

**What to Check:**
- [ ] Scroll feels smooth (no stuttering)
- [ ] FPS is at or above target (60fps desktop, 45fps mobile)
- [ ] No visible jank (dropped frames)
- [ ] Scroll timing feels natural (not too fast/slow)

---

## 6. Visual Regression Testing

### 6.1 Setup Visual Regression

**Install screenshot comparison (Playwright built-in):**
```bash
# No additional install needed - Playwright has built-in screenshot comparison
```

---

### 6.2 Create Baseline Screenshots

**First time: Create baseline screenshots**

**Run:** `npm run test:visual`

Playwright will automatically:
1. Take screenshots
2. Save them as baselines in `_bmad-output/test-artifacts/baselines/`

**Directory structure:**
```
_bmad-output/test-artifacts/
├── baselines/          ← Baseline images (reference)
│   ├── hero-desktop.png
│   ├── hero-mobile.png
│   └── ...
└── screenshots/        ← Current screenshots (compare to baselines)
    ├── hero-desktop.png
    ├── hero-mobile.png
    └── ...
```

---

### 6.3 Create Visual Regression Tests

**Create file:** `tests/visual-regression.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test('Hero section should match baseline', async ({ page }) => {
    await page.goto('/#hero');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Compare to baseline (fail if different)
    await expect(page).toHaveScreenshot('hero-desktop.png', {
      maxDiffPixels: 100,      // Allow 100 pixels to differ
      threshold: 0.05,         // Allow 5% difference (anti-aliasing)
    });
  });

  test('Map section should match baseline', async ({ page }) => {
    await page.goto('/#map');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await expect(page).toHaveScreenshot('map-desktop.png', {
      maxDiffPixels: 100,
      threshold: 0.05,
    });
  });

  test('Discord section should match baseline', async ({ page }) => {
    await page.goto('/#discord');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await expect(page).toHaveScreenshot('discord-desktop.png', {
      maxDiffPixels: 100,
      threshold: 0.05,
    });
  });

  test('CTA section should match baseline', async ({ page }) => {
    await page.goto('/#cta');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await expect(page).toHaveScreenshot('cta-desktop.png', {
      maxDiffPixels: 100,
      threshold: 0.05,
    });
  });
});
```

---

### 6.4 Run Visual Regression Tests

**First run (create baselines):**
```bash
npx playwright test tests/visual-regression.spec.ts

# Expected: Screenshots saved as baselines
```

**Subsequent runs (compare to baselines):**
```bash
npx playwright test tests/visual-regression.spec.ts

# Expected:
# - If no changes: All tests pass
# - If changes found: Tests fail, diff images generated
```

**When you make intentional changes:**
```bash
# Update baselines
npm run test:visual:update

# Or
npx playwright test tests/visual-regression.spec.ts --update-snapshots
```

---

### 6.5 View Visual Diffs

**When tests fail, Playwright generates diff images:**

**Diff image location:**
```
test-results/visual-regression-spec.ts/
├── hero-desktop-actual.png      ← Current screenshot
├── hero-desktop-expected.png    ← Baseline
└── hero-desktop-diff.png        ← Diff (red = differences)
```

**View diff:**
- Open `hero-desktop-diff.png` in image viewer
- Red areas = differences from baseline
- Decide: Is this intentional or a bug?

---

### 6.6 Visual Regression Thresholds

**Adjust thresholds in config:**

```javascript
// playwright.config.js
use: {
  // Screenshot comparison thresholds
  screenshot: 'only-on-failure',
},
expect: {
  // Visual regression settings
  toHaveScreenshot: {
    maxDiffPixels: 100,     // Max pixels allowed to differ
    threshold: 0.05,        // Max % difference allowed (5%)
  },
},
```

**Threshold guidelines:**
- `maxDiffPixels: 100` - Allow 100 pixels to differ (~1% of 1920x1080 screen)
- `threshold: 0.05` - Allow 5% difference (accounts for anti-aliasing, font rendering)
- Tighten for strict matching: `threshold: 0.02` (2%)
- Loosen for forgiving: `threshold: 0.1` (10%)

---

## 7. Test Runner Scripts

### 7.1 NPM Scripts

**Already defined in `package.json`:**
```json
{
  "scripts": {
    "test:visual": "playwright test",
    "test:visual:headed": "playwright test --headed",
    "test:visual:debug": "playwright test --debug",
    "test:visual:update": "playwright test --update-snapshots",
    "test:visual:report": "playwright show-report"
  }
}
```

---

### 7.2 Script Usage Examples

**Run all visual tests:**
```bash
npm run test:visual
```

**Run specific tests:**
```bash
# Only Hero tests
npx playwright test tests/hero/

# Only animation tests
npx playwright test tests/animations/

# Only regression tests
npx playwright test tests/visual-regression.spec.ts
```

**Run with visible browser (debugging):**
```bash
npm run test:visual:headed
```

**Debug mode (step through tests):**
```bash
npm run test:visual:debug

# Opens Playwright Inspector:
# - Step through code line-by-line
# - Inspect elements
# - View console logs
# - Execute arbitrary JavaScript
```

**Update baselines:**
```bash
npm run test:visual:update
```

**View HTML report:**
```bash
npm run test:visual:report

# Opens browser with:
# - Test results
# - Screenshots
# - Videos
# - Execution time
# - Error logs
```

---

### 7.3 Continuous Integration Scripts

**Add CI-specific scripts:**

```json
{
  "scripts": {
    "test:ci": "playwright test",
    "test:ci:report": "playwright show-report --host=localhost"
  }
}
```

**CI usage:**
```bash
# In CI environment (GitHub Actions, GitLab CI, etc.)
npm run test:ci

# Upload test report as artifact
# (GitHub Actions example)
- name: Upload Playwright Report
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

---

## 8. Integration with Epic Workflow

### 8.1 When to Run Visual Tests

**After each Epic story completion:**

| Story | When to Run Visual Tests | What to Check |
|-------|-------------------------|---------------|
| **1.1** (Design tokens) | After implementation | Colors, fonts, spacing applied correctly |
| **1.2** (GSAP + Lenis) | After implementation | Smooth scroll works, animations trigger |
| **1.3** (Hero structure) | After implementation | Hero layout, responsive design |
| **1.4** (Hero animations) | After implementation | Text reveal animations, timing |
| **1.5** (Hero optimization) | After implementation | Performance (60fps/45fps), no jank |

**After Epic 1 (Hero) complete:**
1. Run all visual tests: `npm run test:visual`
2. Review screenshots: `_bmad-output/test-artifacts/screenshots/`
3. Watch videos: `_bmad-output/test-artifacts/videos/`
4. Check for visual issues
5. Fix issues or update baselines
6. Mark Epic 1 "done"

**Repeat for Epic 2, 3, 4**

---

### 8.2 Visual Test Checklist

**Before marking story "done":**
- [ ] Visual tests pass (0 failures)
- [ ] Screenshots reviewed in image viewer
- [ ] Videos watched (smooth scroll, animations)
- [ ] No visual bugs (broken layout, unreadable text)
- [ ] Performance targets met (60fps desktop, 45fps mobile)
- [ ] Responsive design verified (mobile, tablet, desktop)
- [ ] Cross-browser verified (Chromium, Firefox, WebKit)

**If visual tests fail:**
1. Identify issue (screenshot, video, console log)
2. Fix issue in code
3. Re-run tests: `npm run test:visual`
4. Repeat until tests pass

**If tests fail but changes are intentional:**
1. Update baselines: `npm run test:visual:update`
2. Commit updated baselines to git
3. Mark story "done"

---

### 8.3 Prevent Visual Regressions

**Setup Git pre-commit hook (optional):**

**Create file:** `.husky/pre-commit`
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Run visual tests before commit
npm run test:visual

# If tests fail, block commit
if [ $? -ne 0 ]; then
  echo "❌ Visual tests failed. Fix issues or update baselines."
  exit 1
fi
```

**Install husky:**
```bash
npm install -D husky
npx husky install
```

**Now git commit will run visual tests automatically:**
```bash
git add .
git commit -m "feat: add Hero section"
# Visual tests run automatically
# If fail: commit blocked
# If pass: commit succeeds
```

---

## 9. Multi-Viewport Testing

### 9.1 Viewport Configuration

**Already configured in `playwright.config.js`:**

```javascript
projects: [
  {
    name: 'chromium-desktop',
    use: { ...devices['Desktop Chrome'] }, // 1920x1080
  },

  {
    name: 'mobile-chrome',
    use: { ...devices['Pixel 5'] }, // 393x851
  },

  {
    name: 'mobile-safari',
    use: { ...devices['iPhone 12'] }, // 390x844
  },
],
```

**Playwright device presets:**
- `Desktop Chrome` - 1920x1080
- `Desktop Firefox` - 1920x1080
- `Desktop Safari` - 1920x1080
- `Pixel 5` - 393x851 (Android mobile)
- `iPhone 12` - 390x844 (iOS mobile)
- `iPad Pro` - 1024x1366 (tablet)

---

### 9.2 Custom Viewport Tests

**Test custom viewport sizes:**

```typescript
import { test, expect } from '@playwright/test';

test.describe('Custom Viewport Tests', () => {
  test('should render correctly on 375x812 (iPhone X)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: '_bmad-output/test-artifacts/screenshots/iphone-x.png',
    });
  });

  test('should render correctly on 1920x1080 (Full HD)', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: '_bmad-output/test-artifacts/screenshots/full-hd.png',
    });
  });

  test('should render correctly on 2560x1440 (2K)', async ({ page }) => {
    await page.setViewportSize({ width: 2560, height: 1440 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: '_bmad-output/test-artifacts/screenshots/2k.png',
    });
  });
});
```

---

### 9.3 Responsive Design Testing

**Test responsive breakpoints:**

```typescript
import { test, expect } from '@playwright/test';

test.describe('Responsive Design Tests', () => {
  const viewports = [
    { width: 375, height: 812, name: 'mobile' },    // iPhone X
    { width: 768, height: 1024, name: 'tablet' },   // iPad
    { width: 1920, height: 1080, name: 'desktop' }, // Full HD
  ];

  for (const viewport of viewports) {
    test(`should render correctly on ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      await page.screenshot({
        path: `_bmad-output/test-artifacts/screenshots/responsive-${viewport.name}.png`,
        fullPage: true,
      });

      // Verify no horizontal scroll
      const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
      const clientWidth = await page.evaluate(() => document.body.clientWidth);
      expect(scrollWidth).toEqual(clientWidth);
    });
  }
});
```

**What to check:**
- [ ] No horizontal scroll (overflow-x)
- [ ] Text is readable (not too small)
- [ ] Touch targets are ≥44x44px (mobile)
- [ ] Layout stacks vertically (mobile)
- [ ] Images scale correctly

---

## 10. Visual Testing Workflow Documentation

### 10.1 Daily Development Workflow

**1. Make code changes**
```bash
# Edit code
vim src/components/Hero.js
```

**2. Run visual tests**
```bash
npm run test:visual
```

**3. Review results**
```bash
# Open screenshots
open _bmad-output/test-artifacts/screenshots/

# Watch videos (if any)
open _bmad-output/test-artifacts/videos/
```

**4. Fix issues or update baselines**
```bash
# If issues found: fix code
vim src/components/Hero.js

# If changes intentional: update baselines
npm run test:visual:update
```

**5. Commit**
```bash
git add .
git commit -m "feat: update Hero text color"
```

---

### 10.2 Epic Story Completion Workflow

**After completing Epic story (e.g., Story 1.3 - Build Hero):**

**Step 1: Run all visual tests**
```bash
npm run test:visual
```

**Step 2: Review screenshots**
- Open `_bmad-output/test-artifacts/screenshots/`
- Check Hero section on mobile, tablet, desktop
- Look for: broken layout, unreadable text, missing elements

**Step 3: Watch videos**
- Open `_bmad-output/test-artifacts/videos/`
- Verify smooth scroll works
- Check animations trigger correctly
- Confirm performance (60fps/45fps)

**Step 4: Check visual regression**
```bash
# Run regression tests
npx playwright test tests/visual-regression.spec.ts

# If tests fail:
# - Review diff images
# - Decide: bug or intentional change?
# - Bug: fix code
# - Intentional: update baselines
npm run test:visual:update
```

**Step 5: Mark story "done"**
- All visual tests pass ✅
- Screenshots reviewed ✅
- Videos watched ✅
- No visual bugs ✅
- Performance met ✅

---

### 10.3 Debugging Failed Tests

**Test fails? Debug step-by-step:**

**1. Run test in headed mode (see browser):**
```bash
npx playwright test tests/hero/ --headed
```

**2. Run test in debug mode (step through):**
```bash
npx playwright test tests/hero/ --debug

# Opens Playwright Inspector:
# - Step through code
# - Inspect DOM
# - View console logs
# - Execute JavaScript
```

**3. Check screenshots:**
```bash
# Failure screenshots saved to:
ls test-results/

# Open failure screenshot
open test-results/hero-desktop-failed.png
```

**4. Check videos:**
```bash
# Failure videos saved to:
ls test-results/

# Play video
open test-results/hero-desktop.webm
```

**5. Check console errors:**
```typescript
// Add to test
test('should capture console errors', async ({ page }) => {
  const errors = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  await page.goto('/#hero');

  // Assert no errors
  expect(errors).toHaveLength(0);
});
```

**6. Check network failures:**
```typescript
// Add to test
test('should capture network failures', async ({ page }) => {
  const failedRequests = [];

  page.on('requestfailed', request => {
    failedRequests.push(request.url());
  });

  await page.goto('/#hero');

  // Assert no failed requests
  expect(failedRequests).toHaveLength(0);
});
```

---

### 10.4 Common Visual Issues

**Issue 1: Screenshot doesn't match baseline**

**Cause:** Code changes, browser rendering, anti-aliasing

**Solutions:**
- If bug: Fix code
- If intentional: Update baseline (`npm run test:visual:update`)
- If anti-aliasing noise: Increase threshold (`threshold: 0.1`)

---

**Issue 2: Animation not captured in screenshot**

**Cause:** Screenshot taken before animation completes

**Solution:**
```typescript
// Add wait for animation
await page.waitForTimeout(1500); // Wait for GSAP to complete
await page.screenshot({ ... });
```

---

**Issue 3: Video not recorded**

**Cause:** Video not enabled in config

**Solution:**
```javascript
// playwright.config.js
use: {
  video: 'on', // Enable video recording
},
```

---

**Issue 4: Tests timeout**

**Cause:** Page loads too slowly, infinite loops

**Solution:**
```typescript
// Increase timeout
test.setTimeout(60000); // 60 seconds

// Or wait for specific element
await page.waitForSelector('#hero', { timeout: 10000 });
```

---

**Issue 5: Horizontal scroll on mobile**

**Cause:** Element too wide for viewport

**Solution:**
- Check CSS: `overflow-x: hidden`
- Check element widths: `max-width: 100%`
- Use `box-sizing: border-box`

---

### 10.5 Best Practices

**✅ DO:**
- Run visual tests after every story completion
- Review screenshots in image viewer (not just trust tests)
- Test on multiple viewports (mobile, tablet, desktop)
- Update baselines when changes are intentional
- Use version control for baselines (commit to git)
- Run tests in CI/CD pipeline
- Set appropriate thresholds (5% for most cases)

**❌ DON'T:**
- Commit code without running visual tests
- Ignore failing visual tests
- Set thresholds too high (>10% = meaningless)
- Update baselines without reviewing changes
- Test only on desktop (forget mobile)
- Skip visual regression tests

---

## Appendix

### A. Full Example Test File

**Complete Hero visual test:**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Hero Section - Complete Visual Test', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate before each test
    await page.goto('/#hero');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500); // Wait for animations
  });

  test('should render on desktop', async ({ page }) => {
    await page.locator('#hero').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/hero/hero-desktop.png',
    });

    await expect(page.locator('text=You are not behind')).toBeVisible();
    await expect(page.locator('button >> text=Start Diagnostic')).toBeVisible();
  });

  test('should render on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/#hero');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await page.locator('#hero').screenshot({
      path: '_bmad-output/test-artifacts/screenshots/hero/hero-mobile.png',
    });
  });

  test('should match baseline', async ({ page }) => {
    await expect(page).toHaveScreenshot('hero-baseline.png', {
      maxDiffPixels: 100,
      threshold: 0.05,
    });
  });

  test('should have no console errors', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });

    await page.reload();
    await page.waitForLoadState('networkidle');

    expect(errors).toHaveLength(0);
  });

  test('should have no failed network requests', async ({ page }) => {
    const failed = [];
    page.on('requestfailed', request => {
      failed.push(request.url());
    });

    await page.reload();
    await page.waitForLoadState('networkidle');

    expect(failed).toHaveLength(0);
  });
});
```

---

### B. Troubleshooting Guide

**Problem:** Tests fail locally but pass in CI

**Solution:** CI uses different browsers/versions. Lock versions:
```bash
npx playwright install --with-deps chromium
```

---

**Problem:** Screenshots look different on different machines

**Cause:** Font rendering, DPI, OS differences

**Solution:**
- Use consistent OS in CI (Docker with Xvfb)
- Or increase threshold to accommodate differences
- Test in same environment as production

---

**Problem:** Animations not captured correctly

**Solution:** Wait for GSAP timeline completion:
```typescript
await page.waitForFunction(() => {
  // Check if GSAP timeline is complete
  return window.gsapTimeline?.progress() === 1;
});
```

---

### C. Resources

- **Playwright Docs:** https://playwright.dev
- **Screenshots:** https://playwright.dev/docs/screenshots
- **Visual Regression:** https://playwright.dev/docs/test-snapshots
- **Video Recording:** https://playwright.dev/docs/videos
- **Best Practices:** https://playwright.dev/docs/best-practices

---

## Conclusion

**This visual testing setup provides:**

✅ **Automated screenshots** of all sections (Hero, Map, Discord, CTA)
✅ **Animation milestone captures** (0%, 50%, 100% frames)
✅ **Video recordings** of smooth scroll behavior
✅ **Visual regression testing** (catch accidental changes)
✅ **Multi-viewport testing** (mobile, tablet, desktop)
✅ **Performance validation** (60fps desktop, 45fps mobile)
✅ **Cross-browser testing** (Chrome, Firefox, Safari)
✅ **Integration workflow** (run after each Epic story)

**Next Steps:**
1. Install Playwright: `npm install -D @playwright/test`
2. Install browsers: `npx playwright install chromium firefox webkit`
3. Copy `playwright.config.js` to project root
4. Create test files in `tests/` directory
5. Run tests: `npm run test:visual`
6. Review screenshots/videos in `_bmad-output/test-artifacts/`

**Remember:**
- Run visual tests after each Epic story
- Review screenshots manually (don't just trust tests)
- Update baselines when changes are intentional
- Use visual tests to catch issues BEFORE human testing (Story 0.3)

**Document End**

**Last Updated:** 2026-01-15
**Version:** 1.0
**Status:** Ready for implementation
