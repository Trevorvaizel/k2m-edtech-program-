import { test, expect } from '@playwright/test';

test('Debug - Check what is actually rendering', async ({ page }) => {
  // Collect console messages
  const consoleLogs: string[] = [];
  page.on('console', msg => consoleLogs.push(`[${msg.type()}] ${msg.text()}`));

  await page.goto('/');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);

  // Check if CSS variables are defined
  const cssVars = await page.evaluate(() => {
    const root = getComputedStyle(document.documentElement);
    const body = getComputedStyle(document.body);
    return {
      pureBlack: root.getPropertyValue('--pure-black'),
      textPrimary: root.getPropertyValue('--text-primary'),
      oceanMintGlow: root.getPropertyValue('--ocean-mint-glow'),
      bodyBg: body.backgroundColor,
      bodyColor: body.color,
    };
  });

  // Check Hero elements
  const heroCheck = await page.evaluate(() => {
    const hero = document.querySelector('.hero');
    const title = document.querySelector('.hero-title');
    const titleStyle = title ? getComputedStyle(title) : null;

    return {
      heroExists: !!hero,
      titleExists: !!title,
      titleText: title?.textContent?.trim(),
      titleColor: titleStyle?.color,
      titleFontSize: titleStyle?.fontSize,
      appInnerHTML: document.getElementById('app')?.innerHTML?.substring(0, 300),
    };
  });

  console.log('\n=== CSS VARIABLES ===');
  console.log(JSON.stringify(cssVars, null, 2));

  console.log('\n=== HERO CHECK ===');
  console.log(JSON.stringify(heroCheck, null, 2));

  console.log('\n=== CONSOLE LOGS ===');
  consoleLogs.forEach(log => console.log(log));

  // Take screenshot
  await page.screenshot({
    path: '_bmad-output/test-artifacts/screenshots/debug-render.png',
    fullPage: true,
  });

  expect(heroCheck.heroExists).toBe(true);
});
