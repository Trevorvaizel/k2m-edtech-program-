import { test, expect } from '@playwright/test';

test('debug: check zone activation states', async ({ page }) => {
  await page.goto('/');

  // Wait for load
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1500);

  // Check initial state
  const zone0Active = await page.evaluate(() => {
    const zone = document.querySelector('.resonance-zone[data-zone="0"]');
    return {
      inFocus: zone?.classList.contains('in-focus'),
      voiceStageOpacity: window.getComputedStyle(zone?.querySelector('.voice-stage') || null).opacity,
      voiceStageTransform: window.getComputedStyle(zone?.querySelector('.voice-stage') || null).transform
    };
  });

  console.log('Zone 0 initial:', zone0Active);

  // Scroll to Zone 1
  await page.evaluate(() => {
    document.querySelector('.resonance-zone[data-zone="1"]')?.scrollIntoView({
      behavior: 'instant',
      block: 'center'
    });
  });

  await page.waitForTimeout(1000);

  // Check Zone 1 state after scrolling
  const zone1State = await page.evaluate(() => {
    const zone = document.querySelector('.resonance-zone[data-zone="1"]');
    const voiceStage = zone?.querySelector('.voice-stage');
    return {
      zoneInFocus: zone?.classList.contains('in-focus'),
      voiceStageExists: !!voiceStage,
      voiceStageOpacity: voiceStage ? window.getComputedStyle(voiceStage).opacity : null,
      voiceStageTransform: voiceStage ? window.getComputedStyle(voiceStage).transform : null,
      voiceStageDisplay: voiceStage ? window.getComputedStyle(voiceStage).display : null,
      voiceStageVisibility: voiceStage ? window.getComputedStyle(voiceStage).visibility : null
    };
  });

  console.log('Zone 1 after scroll:', zone1State);
  expect(zone1State.zoneInFocus).toBe(true);

  // Check ALL zones' in-focus status
  const allZones = await page.evaluate(() => {
    const zones = document.querySelectorAll('.resonance-zone');
    return Array.from(zones).map(zone => ({
      zone: zone.dataset.zone,
      inFocus: zone.classList.contains('in-focus')
    }));
  });

  console.log('All zones status:', allZones);

  // Screenshot
  await page.screenshot({
    path: 'test-results/screenshots/debug/zone-1-debug.png'
  });
});
