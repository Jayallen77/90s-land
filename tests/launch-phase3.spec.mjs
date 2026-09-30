import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import pool from '../assets/runtime/surprise.json' with {type:'json'};
import {weekPicks} from '../js/discovery.js';
import catalog from '../assets/runtime/week.json' with {type:'json'};
import {eventsInWeek} from '../js/date-utils.js';

test('default week rolls over in New York while a selected week stays put',async({page})=>{
  await page.clock.install({time:new Date('2026-09-30T03:59:30Z')});
  await page.goto('/this-week/');
  await expect(page.locator('[data-week-date]')).toHaveValue('1996-09-29');
  await page.clock.runFor(60000);
  await expect(page.locator('[data-week-date]')).toHaveValue('1996-09-30');
  await page.locator('[data-week-date]').fill('1998-08-15');
  await page.locator('[data-week-date]').dispatchEvent('change');
  await page.clock.setSystemTime(new Date('2026-10-08T04:01:00Z'));
  await page.clock.runFor(60000);
  await expect(page.locator('[data-week-date]')).toHaveValue('1998-08-15');
  await page.locator('[data-week-today]').click();
  await expect(page.locator('[data-week-date]')).toHaveValue('1996-10-08');
});

test('weekly picks and related year links update without dropping any calendar entry',async({page})=>{
  await page.goto('/this-week/?date=1996-09-29');
  await expect(page.locator('[data-week-date]')).toHaveValue('1996-09-29');
  for(const date of ['1996-09-29','1998-05-06','1990-01-22','1999-12-31']) {
    await page.locator('[data-week-date]').fill(date);
    await page.locator('[data-week-date]').dispatchEvent('change');
    const actual=eventsInWeek(catalog.events,date), picks=weekPicks(actual);
    const selected=page.locator('[data-week-highlights] a');
    await expect(selected).toHaveCount(picks.length);
    expect(await selected.evaluateAll(links=>links.map(link=>new URL(link.href).pathname))).toEqual(picks.map(e=>e.url));
    await expect(page.locator('[data-week-days] .ar-week-event')).toHaveCount(actual.length);
    await expect(page.locator('[data-week-connections] a').first()).toHaveAttribute('href',`/timeline/${date.slice(0,4)}/`);
  }
});

test('all six shuffle kinds can be opened and quick repeated clicks keep one current pick',async({page})=>{
  for(const kind of ['story','object','event','year','collection','tour']) {
    await page.route('**/assets/runtime/surprise.json',route=>route.fulfill({json:pool.filter(item=>item.kind===kind)}));
    await page.goto('/surprise/');
    await page.locator('[data-surprise-trigger-button]').click();
    await expect(page.locator('[data-surprise-ready]')).toBeVisible();
    await page.evaluate(()=>{for(let i=0;i<6;i++)document.querySelector('[data-surprise-again]').click();});
    await expect(page.locator('[data-surprise-ready]')).toBeVisible();
    const href=await page.locator('[data-surprise-open]').getAttribute('href');
    expect(pool.some(item=>item.kind===kind && item.target===href)).toBe(true);
    await page.locator('[data-surprise-open]').click();
    await expect(page).toHaveURL(new RegExp(href));
    await page.locator('[data-passport-trigger]').first().click();
    await expect(page.locator('[data-passport-stamp="random-memory"] [data-passport-stamp-state]')).toHaveText('Earned ✓');
    await page.unroute('**/assets/runtime/surprise.json');
  }
});

for(const width of [390,1440]) {
  test(`${width}px: tour completion has accessible next steps and clear Passport states`,async({page})=>{
    await page.setViewportSize({width,height:900});
    await page.goto('/tours/before-the-feed/');
    await expect(page.locator('[data-tour-stop]:visible')).toHaveCount(1);
    for(let i=0;i<6;i++)await page.locator('[data-tour-stop]:visible [data-tour-next]').click();
    await expect(page.locator('[data-tour-finish]')).toBeVisible();
    await page.locator('[data-tour-finish] [data-tour-passport]').click();
    await expect(page.locator('[data-passport-stamp="before-the-feed"] [data-passport-stamp-state]')).toHaveText('Earned ✓');
    await expect(page.locator('.passport-stats')).toContainText('places explored');
    expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
    await page.locator('[data-passport-reset-open]').click();
    await page.locator('[data-passport-reset-confirm]').click();
    await expect(page.locator('[data-passport-stamp="before-the-feed"] [data-passport-stamp-state]')).toHaveText('Not yet earned');
    await page.locator('[data-dialog-close="passportDialog"]').click();
    await expect(page.locator('[data-tour-finish]')).toBeHidden();
    await expect(page.locator('[data-tour-stop]:visible [data-tour-next]')).toBeEnabled();
  });
}

test('search filter count updates leave their widths stable',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto('/search/');
  const badges=page.locator('.site-filter-row .resource-filter span');
  await expect(badges.first()).not.toHaveText('0');
  const before=await badges.evaluateAll(nodes=>nodes.map(n=>n.getBoundingClientRect().width));
  await page.locator('#siteSearchInput').fill('mosaic');
  await expect(page).toHaveURL(/q=mosaic/);
  expect(await badges.evaluateAll(nodes=>nodes.map(n=>n.getBoundingClientRect().width))).toEqual(before);
});
