import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import catalog from '../content/editorial/catalog.json' with { type: 'json' };
const juneCount = catalog.events.filter(e => e.date.startsWith('1996-06')).length;
const savedWeekCount = catalog.events.filter(e => '1996-09-23' <= e.date && e.date <= '1996-09-29').length;

test('calendar filters, view and month survive reload and browser history', async ({ page }) => {
  await page.goto('/timeline/1996/?month=06&view=calendar');
  const june = page.locator('[data-month-panel="6"]');
  await expect(june.locator('.ar-calendar [data-event]:visible')).toHaveCount(juneCount);
  await page.locator('[data-category-filter]').selectOption('games');
  await expect(june.locator('.ar-calendar [data-event]:visible')).toHaveCount(2);
  await page.locator('[data-region-filter]').selectOption('Japan');
  await expect(june.locator('.ar-calendar [data-event]:visible')).toHaveCount(1);
  await expect(june.locator('.ar-calendar [data-event]:visible')).toContainText('Nintendo');
  await page.reload();
  await expect(page.locator('[data-region-filter]')).toHaveValue('Japan');
  await page.locator('[data-month="7"]').click();
  await expect(page.locator('[data-month-panel="7"] [data-month-empty]')).toBeVisible();
  await page.goBack();
  await expect(june).toBeVisible();
  await expect(june.locator('.ar-calendar [data-event]:visible')).toHaveCount(1);
  await page.goForward();
  await expect(page.locator('[data-month-panel="7"]')).toBeVisible();
});

test('calendar displays actual leap days and month navigation crosses years safely', async ({ page }) => {
  await page.goto('/timeline/1996/?month=02&view=calendar');
  await expect(page.locator('[data-month-panel="2"] .ar-calendar time')).toHaveCount(29);
  await page.goto('/timeline/1995/?month=02&view=calendar');
  await expect(page.locator('[data-month-panel="2"] .ar-calendar time')).toHaveCount(28);
  await page.goto('/timeline/1996/?month=12&view=list&category=games');
  await page.locator('[data-next-month]').click();
  await expect(page).toHaveURL(/timeline\/1997\/\?month=01&view=list&category=games/);
  await page.goto('/timeline/1990/?month=01');
  await expect(page.locator('[data-prev-month]')).toBeHidden();
  await page.goto('/timeline/1999/?month=12');
  await expect(page.locator('[data-next-month]')).toBeHidden();
});

test('invalid calendar parameters fall back to usable controls', async ({ page }) => {
  await page.goto('/timeline/1996/?month=99&view=broken&category=invalid&region=bad&page=Infinity');
  await expect(page.locator('[data-timeline]')).toHaveAttribute('data-view','grid');
  await expect(page.locator('[data-category-filter]')).toHaveValue('all');
  await expect(page.locator('[data-month-panel]:visible')).toHaveCount(1);
  await page.locator('[data-month="6"]').click();
  await expect(page.locator('[data-month-panel="6"] .ar-event:visible')).toHaveCount(Math.min(12,juneCount));
});

test('a growing month paginates cards while calendar retains all its dates', async ({ page }) => {
  await page.route('**/timeline/1996/', async route => {
    const response = await route.fetch();
    let body = await response.text();
    const card = body.match(/<article class="ar-event"[^>]*data-date="1996-06-04"[\s\S]*?<\/article>/)[0];
    body = body.replace(/(<section class="ar-month"[^>]*data-month-panel="6"[\s\S]*?<div class="ar-event-grid">)[\s\S]*?(<\/div><table class="ar-calendar">)/, '$1' + card.repeat(17) + '$2');
    await route.fulfill({response,body});
  });
  await page.goto('/timeline/1996/');
  await page.locator('[data-month="6"]').click();
  await expect(page.locator('[data-month-panel="6"] .ar-event:visible')).toHaveCount(12);
  await page.locator('[data-event-next]').click();
  await expect(page.locator('[data-month-panel="6"] .ar-event:visible')).toHaveCount(5);
  await expect(page).toHaveURL(/page=2/);
  await page.locator('[data-archive-view="calendar"]').click();
  await expect(page.locator('[data-event-paging]')).toBeHidden();
  await expect(page.locator('[data-month-panel="6"] .ar-calendar [data-event]:visible')).toHaveCount(juneCount);
});

test('home and weekly defaults agree on the New York date and historical week', async ({ page }) => {
  await page.clock.setFixedTime(new Date('2026-09-28T02:00:00Z'));
  await page.goto('/');
  await expect(page.locator('#this-week .ed-date')).toHaveText('Sep 23, 1996 – Sep 29, 1996');
  await page.locator('#this-week .ed-cta').click();
  await expect(page).toHaveURL(/\/this-week\/$/);
  await expect(page.locator('[data-week-date]')).toHaveValue('1996-09-27');
  await expect(page.locator('[data-week-range]')).toHaveText('Sep 23, 1996 – Sep 29, 1996');
  await expect(page.locator('[data-week-days] .ar-day')).toHaveCount(7);
  await expect(page.locator('[data-week-days] .ar-week-event')).toHaveCount(savedWeekCount);
  await expect(page.locator('[data-week-days]')).toContainText('Nintendo 64');
});

test('week navigation, deep links, empty states and year changes stay coherent', async ({ page }) => {
  await page.goto('/this-week/?date=1996-12-29');
  await expect(page.locator('[data-week-range]')).toHaveText('Dec 23, 1996 – Dec 29, 1996');
  await page.locator('[data-week-next]').click();
  await expect(page.locator('[data-week-range]')).toHaveText('Dec 30, 1996 – Jan 5, 1997');
  await expect(page.locator('[data-week-select]')).toHaveValue('1997');
  await expect(page.locator('[data-week-empty]')).toBeHidden();
  await expect(page.locator('[data-week-days]')).toContainText('Sugar Bowl');
  await page.reload();
  await expect(page.locator('[data-week-date]')).toHaveValue('1997-01-05');
  await page.goBack();
  await expect(page.locator('[data-week-date]')).toHaveValue('1996-12-29');
  await page.goto('/this-week/?date=1996-02-29');
  await page.locator('[data-week-select]').selectOption('1995');
  await expect(page.locator('[data-week-date]')).toHaveValue('1995-02-28');
  await page.goto('/this-week/?date=1990-01-01');
  await expect(page.locator('[data-week-prev]')).toBeDisabled();
  await page.goto('/this-week/?date=1990-01-22');
  await expect(page.locator('[data-week-empty]')).toBeVisible();
  await expect(page.locator('[data-week-empty]')).toContainText('No sourced events');
  await expect(page.locator('[data-week-nearby]')).toContainText('Outside the selected week');
  await page.goto('/this-week/?date=1999-12-31');
  await expect(page.locator('[data-week-next]')).toBeDisabled();
});

test('archive fetch failure leaves an honest, readable static weekly page', async ({ page }) => {
  await page.route('**/data/editorial-index.json',route=>route.abort());
  await page.goto('/this-week/');
  await expect(page.locator('[data-week-explainer]')).toContainText('temporarily unavailable');
  await expect(page.locator('[data-weekly] .ar-controls')).toBeHidden();
  await expect(page.locator('[data-week-days] .ar-week-event')).toHaveCount(savedWeekCount);
});

test('search finds dates, regions, accents, stories and object detail records', async ({ page }) => {
  await page.goto('/search/?q=pokemon+1996&filter=events');
  const results = page.locator('.site-search-card:visible');
  await expect(results).toHaveCount(1);
  await expect(results).toHaveAttribute('href','/events/pokemon-red-green-japan/');
  await page.locator('#siteSearchInput').fill('1996 Japan');
  await expect(results).toHaveCount(5);
  await page.goto('/search/?q=symmetry&filter=stories');
  await expect(results).toHaveCount(1);
  await results.click();
  await expect(page.locator('h1')).toHaveText('A whole new dimension');
  await expect(page.locator('#sources a')).toHaveCount(4);
  await page.goto('/archive/objects/n64-controller/');
  await expect(page.locator('[data-artifact-inspect="n64-controller"]')).toBeVisible();
  await page.locator('[data-artifact-inspect="n64-controller"]').click();
  await expect(page.locator('[data-artifact-inspect="n64-controller"]')).toHaveText('Inspected ✓');
  await page.locator('[data-passport-trigger]').click();
  await expect(page.locator('[data-passport-artifacts]')).toHaveText('1');
});

test('new pages and real calendars remain readable without JavaScript', async ({ browser }) => {
  const context = await browser.newContext({javaScriptEnabled:false});
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:4173/timeline/1996/');
  await expect(page.locator('.ar-calendar:visible')).toHaveCount(12);
  await expect(page.locator('.ar-controls')).toBeHidden();
  await page.locator('[data-month-panel="6"] .ar-event').first().getByRole('link').click();
  await expect(page.locator('h1')).toContainText(catalog.events.filter(e=>e.date.startsWith('1996-06')).sort((a,b)=>a.date.localeCompare(b.date))[0].title);
  await expect(page.locator('#sources')).toBeVisible();
  await page.goto('http://127.0.0.1:4173/this-week/');
  await expect(page.getByText('Saved week for', {exact:false})).toBeVisible();
  await expect(page.locator('[data-week-days] .ar-day')).toHaveCount(7);
  await context.close();
});

for (const path of ['/this-week/','/timeline/1996/?month=06&view=calendar','/events/nintendo-64-us/','/stories/a-whole-new-dimension/','/archive/objects/geocities-homepage/']) {
  test(`new archive accessibility: ${path}`, async ({ page }) => {
    await page.goto(path);
    const results = await new AxeBuilder({page}).analyze();
    expect(results.violations).toEqual([]);
  });
}


test('mobile calendar pairs compact day labels with a readable filtered agenda', async ({ page }) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/timeline/1996/?month=06&view=calendar');
  const month = page.locator('[data-month-panel="6"]');
  await expect(month.locator('.ar-calendar')).toBeVisible();
  await expect(month.locator('.ar-event:visible')).toHaveCount(juneCount);
  await page.locator('[data-category-filter]').selectOption('games');
  await expect(month.locator('.ar-event:visible')).toHaveCount(2);
  await page.locator('[data-region-filter]').selectOption('Japan');
  await expect(month.locator('.ar-event:visible')).toHaveCount(1);
  await expect(month.locator('.ar-event:visible')).toContainText('Nintendo 64');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth)).toBe(0);
  const results = await new AxeBuilder({page}).analyze();
  expect(results.violations).toEqual([]);
});
