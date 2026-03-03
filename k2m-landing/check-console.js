// Quick diagnostic - check browser console
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Capture all console messages
  const logs = [];
  page.on('console', msg => logs.push(`[${msg.type()}] ${msg.text()}`));

  // Capture errors
  page.on('pageerror', err => logs.push(`[ERROR] ${err.message}`));

  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Check DOM
  const appContent = await page.evaluate(() => {
    const app = document.getElementById('app');
    return {
      exists: !!app,
      innerHTML: app ? app.innerHTML.substring(0, 200) : null,
      isEmpty: app ? app.innerHTML.trim() === '' : true
    };
  });

  console.log('\n=== CONSOLE LOGS ===');
  logs.forEach(log => console.log(log));

  console.log('\n=== DOM STATE ===');
  console.log('App exists:', appContent.exists);
  console.log('App is empty:', appContent.isEmpty);
  console.log('First 200 chars:', appContent.innerHTML);

  await browser.close();
})();
