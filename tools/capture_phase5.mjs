import {mkdir,writeFile} from 'node:fs/promises';
import {chromium} from '@playwright/test';
const output=process.env.CAPTURE_OUTPUT || 'reports/phase-5/screenshots';
await mkdir(output,{recursive:true});
const browser=await chromium.launch();const results=[];
const pages=[['home','/'],['timeline','/timeline/'],['year-1996','/timeline/1996/?month=06'],['games','/zones/games/'],['music','/zones/music/'],['movies','/zones/tv-movies/'],['tech','/zones/tech-toys/'],['culture','/zones/culture/'],['week','/this-week/?date=1996-09-27']];
try{
 for(const [name,route] of pages){
  for(const [size,width,height] of [['small',320,812],['mobile',390,844],['desktop',name==='games'?1182:1086,name==='games'?665:724]]){
   const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});const errors=[];
   page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:4173'+route);
   await page.evaluate(()=>document.fonts.ready);
   await page.evaluate(async()=>Promise.all([...document.querySelectorAll('main img')].filter(img=>img.getBoundingClientRect().height>0).map(img=>{img.loading='eager';return img.decode().catch(()=>{});})))
   await page.screenshot({path:`${output}/${name}-${size}.png`,fullPage:size!=='desktop'});
   const metrics=await page.evaluate(()=>{
    const heading=document.querySelector('h1'),range=document.createRange();range.selectNodeContents(heading);
    const rect=range.getBoundingClientRect();const hero=heading.closest('.ed-hero')?.getBoundingClientRect();
    return {overflow:document.documentElement.scrollWidth-innerWidth,headingClipped:Boolean(rect.right>innerWidth+1||rect.left<0||(hero&&rect.bottom>hero.bottom+1)),headingWidth:rect.width};
   });
   results.push({name,size,route,width,height,...metrics,errors});await page.close();
  }
 }
}finally{await browser.close()}
await writeFile(`${output}/layout-metrics.json`,JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify(results));
if(results.some(r=>r.overflow>0||r.headingClipped||r.errors.length))process.exitCode=1;
