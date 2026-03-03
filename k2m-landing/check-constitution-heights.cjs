const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const filePath = 'file:///mnt/c/Users/OMEN/Documents/K2M/k2m-edtech-program-/_bmad-output/ky4y/ky4y-cbo-constitution.html';

  await page.goto(filePath);
  await page.waitForLoadState('networkidle');

  const pageData = await page.evaluate(() => {
    const pages = document.querySelectorAll('.page');
    const data = [];

    pages.forEach((pageEl, i) => {
      const height = pageEl.scrollHeight;
      const heightMM = (height / 3.7795).toFixed(1);
      const A4_HEIGHT_PX = 1123;
      const isOverflow = height > A4_HEIGHT_PX;
      const overflowMM = isOverflow ? ((height - A4_HEIGHT_PX) / 3.7795).toFixed(1) : 0;

      const header = pageEl.querySelector('.rh-right, .cover-title')?.textContent?.trim().substring(0, 50) || '';

      data.push({
        page: i + 1,
        heightMM,
        overflowMM,
        isOverflow,
        header
      });
    });

    return data;
  });

  console.log('\n=== PAGE HEIGHT ANALYSIS ===\n');
  console.log('A4 Height: 297mm (1123px at 96 DPI)\n');

  let overflowCount = 0;
  pageData.forEach(p => {
    const status = p.isOverflow
      ? `✗ OVERFLOW by ${p.overflowMM}mm`
      : '✓ OK';
    const marker = p.isOverflow ? '❌' : '✅';
    console.log(`${marker} Page ${p.page.toString().padStart(2)}: ${p.heightMM.padStart(6, ' ')}mm ${status}`);
    if (p.isOverflow) overflowCount++;
  });

  console.log(`\n${overflowCount} page(s) overflow A4 size\n`);

  await browser.close();

  process.exit(overflowCount > 0 ? 1 : 0);
})();
