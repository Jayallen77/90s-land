import { mkdir, writeFile } from 'node:fs/promises';
import { chromium } from '@playwright/test';

const output = 'reports/phase-3';
await mkdir(output, { recursive:true });
const browser = await chromium.launch();
const results = [];
try {
  for (const [name, route, width, height] of [
    ['calendar-desktop','/timeline/1996/?month=06&view=calendar',1440,1000],
    ['week-desktop','/this-week/?date=1996-09-27',1440,1000],
    ['story-desktop','/stories/a-whole-new-dimension/',1440,1000],
    ['calendar-mobile','/timeline/1996/?month=06&view=calendar',390,844],
    ['week-mobile','/this-week/?date=1996-09-27',390,844],
    ['object-mobile','/archive/objects/n64-controller/',390,844],
  ]) {
    const page = await browser.newPage({viewport:{width,height}, reducedMotion:'reduce'});
    const errors = [];
    page.on('pageerror', error=>errors.push(error.message));
    await page.goto(`http://127.0.0.1:4173${route}`);
    if (route.startsWith('/this-week/')) await page.locator('[data-week-lead] .ar-week-event').waitFor();
    await page.evaluate(()=>document.fonts.ready);
    await page.evaluate(async()=>Promise.all([...document.querySelectorAll('main img')].filter(img=>img.getBoundingClientRect().height>0).map(img=>{img.loading='eager'; return img.decode().catch(()=>{});})));
    await page.screenshot({path:`${output}/${name}.png`,fullPage:true});
    const overflow = await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
    results.push({name,route,width,height,overflow,errors});
    await page.close();
  }
} finally { await browser.close(); }
await writeFile(`${output}/layout-metrics.json`,JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify(results,null,2));
if (results.some(result=>result.overflow>0 || result.errors.length)) process.exitCode=1;
