// Diagnostic script to check Hero section
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🔍 Navigating to http://localhost:5173/...');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });

  // Wait a bit for any dynamic content
  await page.waitForTimeout(2000);

  // Take screenshot
  await page.screenshot({ path: 'diagnostic-screenshot.png', fullPage: true });
  console.log('📸 Screenshot saved: diagnostic-screenshot.png');

  // Check if Hero section exists
  const heroExists = await page.locator('.hero').count();
  console.log(`\n✅ Hero section exists: ${heroExists > 0 ? 'YES' : 'NO'} (${heroExists} found)`);

  // Check for specific text elements
  const glowText = await page.locator('.glow-text').count();
  console.log(`✅ Glow text elements: ${glowText} found`);

  // Get all glow text content
  const glowTextContent = await page.locator('.glow-text').allTextContents();
  console.log(`   Content: ${JSON.stringify(glowTextContent)}`);

  // Check for hero title
  const heroTitle = await page.locator('.hero-title').textContent();
  console.log(`✅ Hero title: "${heroTitle}"`);

  // Check for hero subtitle
  const heroSubtitle = await page.locator('.hero-subtitle').textContent();
  console.log(`✅ Hero subtitle: "${heroSubtitle}"`);

  // Check if GSAP is loaded
  const gsapLoaded = await page.evaluate(() => typeof window.gsap !== 'undefined');
  console.log(`✅ GSAP loaded: ${gsapLoaded ? 'YES' : 'NO'}`);

  // Check if ScrollTrigger is loaded
  const scrollTriggerLoaded = await page.evaluate(() => typeof window.ScrollTrigger !== 'undefined');
  console.log(`✅ ScrollTrigger loaded: ${scrollTriggerLoaded ? 'YES' : 'NO'}`);

  // Check if Lenis is initialized
  const lenisLoaded = await page.evaluate(() => typeof window.lenis !== 'undefined');
  console.log(`✅ Lenis smooth scroll: ${lenisLoaded ? 'YES' : 'NO'}`);

  // Check console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`❌ Console Error: ${msg.text()}`);
    }
  });

  // Check for animation elements
  const animatedElements = await page.evaluate(() => {
    return {
      titleAnimated: document.querySelector('.hero-title')?.style.willChange,
      subtitleAnimated: document.querySelector('.hero-subtitle')?.style.willChange,
      glowAnimated: document.querySelector('.glow-text')?.style.textShadow,
    };
  });
  console.log(`\n🎬 Animation states:`, animatedElements);

  // Scroll down to trigger animations
  console.log(`\n📜 Scrolling down to trigger animations...`);
  await page.evaluate(() => window.scrollBy(0, 500));
  await page.waitForTimeout(1000);

  await page.screenshot({ path: 'diagnostic-screenshot-scrolled.png', fullPage: true });
  console.log('📸 Scrolled screenshot saved: diagnostic-screenshot-scrolled.png');

  console.log('\n✅ Diagnostic complete! Check screenshots.');

  // Keep browser open for 30 seconds to inspect
  await page.waitForTimeout(30000);

  await browser.close();
})();
