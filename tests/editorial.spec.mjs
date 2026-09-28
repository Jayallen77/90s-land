import { test, expect } from '@playwright/test';
import catalog from '../content/editorial/catalog.json' with { type: 'json' };

test('dated highlights switch between grid and list', async ({ page }) => {
  await page.goto('/timeline/1996/?month=06');
  const grid = page.locator('[data-month-panel="6"] .ar-event-grid');
  await expect(grid.locator('.ar-event')).toHaveCount(catalog.events.filter(e=>e.date.startsWith('1996-06')).length);
  await page.locator('[data-archive-view="list"]').click();
  await expect(page.locator('[data-timeline]')).toHaveAttribute('data-view', 'list');
  await expect(page.locator('[data-archive-view="list"]')).toHaveAttribute('aria-pressed', 'true');
  await page.locator('[data-archive-view="grid"]').click();
  await expect(page.locator('[data-timeline]')).toHaveAttribute('data-view', 'grid');
});

test('old direct links open the preserved room and reveal the target', async ({ page }) => {
  for (const [route, hash] of [['/', 'artifact-family-pc'], ['/timeline/1996/', 'month-sep'], ['/zones/games/', 'artifact-genesis-controller']]) {
    await page.goto(`${route}#${hash}`);
    await expect(page.locator('.ed-reading-room')).toHaveAttribute('open', '');
    await expect(page.locator(`#${hash}`)).toBeVisible();
    await expect(page.locator(`#${hash}`)).toBeInViewport();
  }
});

test('hero artwork and fonts load without errors on all three compositions', async ({ page }) => {
  const failures = [];
  page.on('pageerror', error => failures.push(error.message));
  page.on('response', response => { if (response.status() >= 400) failures.push(`${response.status()} ${response.url()}`); });
  for (const route of ['/', '/timeline/1996/', '/zones/games/']) {
    await page.goto(route);
    const image = page.locator('.ed-hero > img');
    await image.evaluate(img => img.decode());
    expect(await image.evaluate(img => img.naturalWidth)).toBeGreaterThan(700);
    await page.evaluate(() => document.fonts.ready);
    expect(await page.evaluate(() => document.fonts.check('40px Jersey') && document.fonts.check('14px Barlow'))).toBe(true);
    await expect(page.locator('#siteNav [aria-current="page"]')).toHaveCount(1);
  }
  expect(failures).toEqual([]);
});

test('preserved reading rooms stay accessible without JavaScript', async ({ browser, baseURL }) => {
  const context = await browser.newContext({ baseURL, javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto('/zones/games/');
  await expect(page.locator('.ed-hero h1')).toBeVisible();
  await page.locator('.ed-reading-room > summary').click();
  await expect(page.locator('#artifact-genesis-controller')).toBeVisible();
  await context.close();
});
