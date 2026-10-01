/** Screenshots and image/layout checks against a verified editorial release. */
import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
const origin=process.env.PLAYWRIGHT_BASE_URL||'http://127.0.0.1:4176';
const out='dist/editorial-expansion/screenshots';await fs.mkdir(out,{recursive:true});
const pages={home:'/',week:'/this-week/',timeline:'/timeline/',music:'/zones/music/',games:'/zones/games/',movies:'/zones/tv-movies/',tech:'/zones/tech-toys/',culture:'/zones/culture/',fashion:'/zones/fashion/',stories:'/stories/',objects:'/archive/objects/',resources:'/webring/',browser:'/stories/browser-wars-at-home/',bristol:'/stories/bristol-between-the-beats/',streetwear:'/stories/streetwear-the-logo-and-the-voice/',minidisc:'/archive/objects/minidisc/',memorycard:'/archive/objects/memory-card/',monthprecision:'/timeline/1995/?month=03&category=tech&view=calendar'};
for(let year=1990;year<=1999;year++)pages['year-'+year]=`/timeline/${year}/`;
const browser=await chromium.launch();const results=[];
for(const width of [390,1440]){
 const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const [name,route] of Object.entries(pages)){
  const response=await page.goto(origin+route);await page.evaluate(()=>document.fonts.ready);
  const broken=await page.locator('main img:visible').evaluateAll(async imgs=>{
   await Promise.all(imgs.map(img=>{img.loading='eager';return img.decode().catch(()=>{});}));
   return imgs.filter(img=>!img.naturalWidth).map(img=>img.src);
  });
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  results.push({name,route,width,status:response.status(),overflow,broken,errors:[...errors]});
  await page.screenshot({path:`${out}/${width}-${name}.png`,fullPage:true});
 }
 await page.close();
}
await browser.close();
await fs.writeFile('reports/editorial-expansion/visual-checks.json',JSON.stringify({views:results.length,results},null,2)+'\n');
const failures=results.filter(r=>r.status!==200||r.overflow||r.broken.length||r.errors.length);
console.log(JSON.stringify({views:results.length,failures},null,2));if(failures.length)process.exitCode=1;
