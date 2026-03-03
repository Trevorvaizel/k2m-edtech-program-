import { test, expect } from '@playwright/test';

test('debug: check CSS cascade and specificity', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1500);

  // Scroll to Zone 1
  await page.evaluate(() => {
    document.querySelector('.resonance-zone[data-zone="1"]')?.scrollIntoView({
      behavior: 'instant',
      block: 'center'
    });
  });

  await page.waitForTimeout(1000);

  // Check detailed CSS state
  const cssDebug = await page.evaluate(() => {
    const zone = document.querySelector('.resonance-zone[data-zone="1"]');
    const voiceStage = zone?.querySelector('.voice-stage');

    // Get all computed styles
    const stageStyles = window.getComputedStyle(voiceStage);
    const zoneStyles = window.getComputedStyle(zone);

    // Check if CSS files loaded
    const stylesheets = Array.from(document.styleSheets).map(sheet => {
      try {
        return sheet.href || sheet.ownerNode?.textContent?.substring(0, 50);
      } catch(e) {
        return 'error';
      }
    });

    return {
      zoneClass: zone?.className,
      zoneInFocus: zone?.classList.contains('in-focus'),
      zoneDisplay: zoneStyles.display,
      zonePosition: zoneStyles.position,

      voiceStageClass: voiceStage?.className,
      voiceStageDisplay: stageStyles.display,
      voiceStagePosition: stageStyles.position,
      voiceStageZIndex: stageStyles.zIndex,
      voiceStageOpacity: stageStyles.opacity,
      voiceStageTransform: stageStyles.transform,
      voiceStageTransition: stageStyles.transition,
      voiceStageVisibility: stageStyles.visibility,
      voiceStageBackgroundColor: stageStyles.backgroundColor,
      voiceStageBorder: stageStyles.border,

      // Check parent elements
      voiceStageParent: voiceStage?.parentElement?.className,
      voiceStageParentDisplay: window.getComputedStyle(voiceStage?.parentElement || null).display,

      stylesheetsLoaded: stylesheets.length,
      firstStylesheet: stylesheets[0]
    };
  });

  console.log('CSS Debug Info:', JSON.stringify(cssDebug, null, 2));

  await page.screenshot({
    path: 'test-results/screenshots/debug/css-cascade-debug.png'
  });
});
