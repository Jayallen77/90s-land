// Reproducible final visual-review artifacts from the packaged preview.
import {mkdir,writeFile} from 'node:fs/promises';
import {chromium} from '@playwright/test';
const base=process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:4185';
const output='reports/launch-phase3/screenshots';
const pages=[['home','/'],...Array.from({length:10},(_,i)=>[`year-${1990+i}`,`/timeline/${1990+i}/?month=06`]),
  ['music','/zones/music/'],['movies','/zones/tv-movies/'],['games','/zones/games/'],['tech','/zones/tech-toys/'],['culture','/zones/culture/'],['fashion','/zones/fashion/'],['internet','/zones/internet-culture/'],['transparent','/zones/transparent-tech/'],
  ['week','/this-week/?date=1996-09-29'],['search','/search/?q=mosaic&filter=objects'],['objects','/archive/objects/'],['stories','/stories/'],['surprise','/surprise/'],['tour','/tours/before-the-feed/'],['credits','/credits/'],['resources','/webring/'],['sitemap','/sitemap/'],['video-store','/stories/friday-at-the-video-store/'],['aim','/archive/objects/aim-away-message/']];
await mkdir(output,{recursive:true});const browser=await chromium.launch();const rows=[];
try {
  for(const [name,url] of pages)for(const width of [390,1440]) {
    const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});const errors=[];
    page.on('pageerror',error=>errors.push(error.message));await page.goto(base+url);await page.evaluate(()=>document.fonts.ready);
    if(name==='search')await page.locator('#siteSearchGrid[data-search-ready]').waitFor();
    await page.evaluate(async()=>Promise.all([...document.querySelectorAll('main img')].filter(img=>img.getBoundingClientRect().height>0).map(img=>{img.loading='eager';return img.decode().catch(()=>{});})));
    const file=`${name}-${width}.jpg`;await page.screenshot({path:`${output}/${file}`,fullPage:true,quality:82});
    if(name==='tour') {
      await page.locator('[data-tour-stop][hidden]').first().waitFor({state:'attached'});
      for(let i=0;i<6;i++)await page.locator('[data-tour-stop]:visible [data-tour-next]').click();
      await page.locator('[data-tour-finish] [data-tour-passport]').click();
      await page.screenshot({path:`${output}/passport-${width}.jpg`,quality:88});
    }
    rows.push({name,url,width,file,overflow:await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth),errors});await page.close();
  }
} finally {await browser.close();}
await writeFile(`${output}/inventory.json`,JSON.stringify(rows,null,2)+'\n');
console.log(JSON.stringify({captures:rows.length+2,failures:rows.filter(row=>row.overflow>0 || row.errors.length)}));
if(rows.some(row=>row.overflow>0 || row.errors.length))process.exitCode=1;
