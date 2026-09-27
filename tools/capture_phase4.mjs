import {mkdir,writeFile} from 'node:fs/promises';
import {chromium} from '@playwright/test';
const output='reports/phase-4';await mkdir(output,{recursive:true});
const browser=await chromium.launch();const results=[];
try{
 for(const [name,route] of [['home','/'],['timeline','/timeline/'],['games','/zones/games/'],['music','/zones/music/'],['movies','/zones/tv-movies/'],['tech','/zones/tech-toys/'],['culture','/zones/culture/'],['week','/this-week/?date=1996-09-27']]){
  for(const [size,width,height] of [['desktop',1440,1000],['mobile',390,844]]){
   const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});const errors=[];
   page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:4173'+route);
   await page.evaluate(()=>document.fonts.ready);
   await page.evaluate(async()=>Promise.all([...document.querySelectorAll('main img')].filter(img=>img.getBoundingClientRect().height>0).map(img=>{img.loading='eager';return img.decode().catch(()=>{});})))
   await page.screenshot({path:`${output}/${name}-${size}.png`,fullPage:true});
   results.push({name,size,route,width,height,overflow:await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth),errors});await page.close();
  }
 }
}finally{await browser.close()}
await writeFile(`${output}/layout-metrics.json`,JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results));
if(results.some(r=>r.overflow>0||r.errors.length))process.exitCode=1;
