/** Responsive visual review, retained under ignored dist/redesign. */
import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
const pages={home:'/',timeline:'/timeline/',year:'/timeline/1990/',month:'/timeline/1996/?month=06&view=calendar',music:'/zones/music/',movies:'/zones/tv-movies/',games:'/zones/games/',tech:'/zones/tech-toys/',culture:'/zones/culture/',fashion:'/zones/fashion/',internet:'/zones/internet-culture/',transparent:'/zones/transparent-tech/',stories:'/stories/',story:'/stories/the-internet-came-in-the-mail/',events:'/events/?category=tech',event:'/events/tamagotchi-japan/',objects:'/archive/objects/',object:'/archive/objects/n64-controller/',search:'/search/?q=mosaic',resources:'/webring/',tour:'/tours/before-the-feed/',surprise:'/surprise/',passport:'/',guestbook:'/guestbook/',sitemap:'/sitemap/',credits:'/credits/',missing:'/404.html',week:'/this-week/'};
const out='dist/redesign/screenshots';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch();const results=[];
for(const width of [390,768,1280,1440]){
 const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
 for(const [name,route] of Object.entries(pages)){
  const response=await page.goto((process.env.PLAYWRIGHT_BASE_URL||'http://127.0.0.1:4173')+route);
  await page.evaluate(()=>document.fonts.ready);
  if(name==='passport')await page.locator('[data-passport-trigger]').click();
  await page.locator('img:visible').evaluateAll(imgs=>Promise.all(imgs.map(img=>{img.loading='eager';return img.decode().catch(()=>{});})));
  const layout=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth-innerWidth,legacy:document.querySelectorAll('.window,.window-bar,.ed-reading-room,.ed-preserved').length}));
  results.push({name,route,width,status:response.status(),...layout});
  await page.screenshot({path:`${out}/${width}-${name}.png`,fullPage:name!=='passport'});
  if(layout.overflow||layout.legacy||response.status()!==200)console.log('CHECK',results.at(-1));
 }
 await page.close();
}
await browser.close();await fs.writeFile('dist/redesign/visual-results.json',JSON.stringify(results,null,2));console.log(`Captured ${results.length} responsive views.`);
