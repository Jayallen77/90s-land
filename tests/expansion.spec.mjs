import {test,expect} from '@playwright/test';
import fs from 'node:fs';
import {historicalDate,weekBounds,formatDate,eventsInWeek} from '../js/date-utils.js';
import catalog from '../content/editorial/catalog.json' with {type:'json'};
const features=[...fs.readFileSync(new URL('../content/editorial/features.md',import.meta.url),'utf8').matchAll(/<!-- story: (.*?) -->/g)].map(m=>JSON.parse(m[1]));
const objects=JSON.parse(fs.readFileSync(new URL('../data/artifacts.json',import.meta.url),'utf8')).filter(a=>a.media.reviewedAt==='2026-10-01');

test('month-level events remain discoverable in calendar view without inventing a day',async({page})=>{
  await page.goto('/timeline/1995/?month=03&view=calendar&category=tech');
  await expect(page.locator('[data-timeline]')).toHaveAttribute('data-ready','true');
  const month=page.locator('[data-month-panel="3"]');
  await expect(month.locator('.ar-event[data-date="1995-03"]')).toBeVisible();
  await expect(month.locator('.ar-calendar a[href="/events/casio-qv10/"]')).toHaveCount(0);
  await expect(month.locator('[data-month-empty]')).toHaveText('');
  await page.locator('[data-category-filter]').selectOption('music');
  await expect(page.locator('[data-year-context] [data-event]:visible').first()).toHaveAttribute('data-category','music');
});

test('every new feature and object renders readable content, valid images and internal paths',async({page})=>{
  test.setTimeout(120_000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const width of [390,1440]){
   await page.setViewportSize({width,height:900});
   for(const path of [...features.map(s=>`/stories/${s.id}/`),...objects.map(a=>`/archive/objects/${a.slug}/`)]){
    const response=await page.goto(path);expect(response.status(),path).toBe(200);
    await expect(page.locator('h1')).toHaveCount(1);
    await expect(page.locator('#sources')).toBeVisible();
    await page.locator('main img').evaluateAll(imgs=>Promise.all(imgs.map(img=>{img.loading='eager';return img.decode();})));
    expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),`${width}: ${path}`).toBe(false);
   }
  }
  expect(errors).toEqual([]);
});

test('saved HTML contains the current build week and new library without JavaScript',async({browser,baseURL})=>{
 const context=await browser.newContext({baseURL,javaScriptEnabled:false});const page=await context.newPage();
 const manifest=new URL('../dist/release/release-manifest.json',import.meta.url);
 const asOf=process.env.PLAYWRIGHT_BASE_URL&&fs.existsSync(manifest)?JSON.parse(fs.readFileSync(manifest,'utf8')).editorialAsOf:catalog.buildAsOf;
 const day=historicalDate(new Date(`${asOf}T12:00:00-06:00`));const selected=eventsInWeek(catalog.events,day);
 await page.goto('/this-week/');await expect(page.locator('[data-week-range]')).toContainText(formatDate(weekBounds(day).start));
 if(selected.length){await expect(page.locator('[data-week-days]')).toContainText(selected[0].title);await expect(page.locator('[data-week-empty]')).toHaveText('');}
 await page.goto('/stories/');await expect(page.locator('[data-hub-story]')).toHaveCount(catalog.stories.length+features.length);
 await context.close();
});

test('every new album record has a complete visible title on mobile and desktop',async({page})=>{
 test.setTimeout(120_000);
 const albums=catalog.events.filter(e=>e.id.startsWith('album-')&&e.publishedAt==='2026-10-01');
 for(const width of [390,1440]){
  await page.setViewportSize({width,height:900});
  for(const album of albums){
   const response=await page.goto(`/events/${album.slug}/`);expect(response.status()).toBe(200);
   await expect(page.locator('h1')).toHaveText(album.title);
   expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),`${width}: ${album.id}`).toBe(false);
  }
 }
});
