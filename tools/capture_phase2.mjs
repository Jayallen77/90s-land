import { mkdir, writeFile } from 'node:fs/promises';
import { chromium } from '@playwright/test';

const output = 'reports/phase-2/screenshots';
await mkdir(output, { recursive: true });
const browser = await chromium.launch();
const results = [];
try {
  for (const [name, route, width, height] of [
    ['home', '/', 1086, 724], ['timeline', '/timeline/1996/', 1086, 724],
    ['games', '/zones/games/', 1182, 665], ['home-mobile', '/', 390, 844],
    ['timeline-mobile', '/timeline/1996/', 390, 844], ['games-mobile', '/zones/games/', 390, 844],
  ]) {
    const page = await browser.newPage({ viewport: { width, height }, reducedMotion: 'reduce' });
    await page.goto(`http://127.0.0.1:4173${route}`);
    await page.evaluate(() => document.fonts.ready);
    await page.locator('.ed-hero > img').evaluate(image => image.decode());
    await page.locator('.ed-main').evaluate(async main => {
      await Promise.all([...main.querySelectorAll('img')].filter(img => img.getBoundingClientRect().top < innerHeight && img.getBoundingClientRect().height > 0).map(img => img.decode().catch(() => {})));
    });
    await page.screenshot({ path: `${output}/${name}.png` });
    const metrics = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth - innerWidth,
      heroHeight: document.querySelector('.ed-hero').clientHeight,
      firstModuleTop: document.querySelector('.ed-home-grid,.ed-topic-rail,.ed-month-rail').getBoundingClientRect().top,
      objectCollectionTop: document.querySelector('.artifact-shelf').getBoundingClientRect().top,
    }));
    results.push({ name, route, width, height, ...metrics });
    await page.close();
  }
} finally { await browser.close(); }
await writeFile('reports/phase-2/layout-metrics.json', JSON.stringify(results, null, 2)+'\n');
console.log(results);
