import {test,expect} from './browser-fixtures.mjs';
import routes from '../data/routes.json' with {type:'json'};
import publication from '../content/editorial/publication.json' with {type:'json'};
import media from '../content/editorial/story-media.json' with {type:'json'};
import catalog from '../content/editorial/catalog.json' with {type:'json'};
import {eventHref} from './editorial-fixtures.mjs';

test('merged URLs work without scripts and retired filler is a real 404',async({browser,baseURL})=>{
 const context=await browser.newContext({baseURL,javaScriptEnabled:false});const page=await context.newPage();
 for(const path of ['/stories/the-toy-that-needed-you/','/stories/a-computer-in-your-pocket/','/events/nintendo-64-us/']){
  const target=publication.redirects[path];
  await page.goto(path);
  await expect(page).toHaveURL(new URL(target,baseURL).href);
  await expect(page.locator('h1')).toHaveCount(1);
 }
 for(const path of publication.retiredRoutes.slice(0,3))expect((await page.goto(path)).status()).toBe(404);
 await context.close();
});

test('deep timeline links reveal their entry despite conflicting filters and calendar view',async({page})=>{
 const event=catalog.events.find(e=>e.id==='pokemon-red-green-japan');
 await page.goto(eventHref(event).replace('#','&category=music&region=USA&view=calendar&page=99#'));
 await expect(page.locator(`[id="event-${event.id}"]`)).toBeVisible();
 await expect(page.locator('[data-category-filter]')).toHaveValue('all');
 await expect(page.locator('[data-region-filter]')).toHaveValue('all');
 await expect(page.locator('[data-timeline]')).toHaveAttribute('data-view','grid');
 await page.locator(`#event-${event.id} .ar-entry-notes > summary`).click();
 await expect(page.locator(`#event-${event.id} .ar-sources`)).toBeVisible();
 await page.reload();await expect(page.locator(`#event-${event.id}`)).toBeVisible();
});

test('a featured story appears once and consolidated sections are reachable from topics',async({page})=>{
 await page.goto('/zones/culture/');
 await expect(page.locator('#featured-story a[href="/stories/streetwear-the-logo-and-the-voice/"]')).toHaveCount(1);
 await expect(page.locator('.hub-story-grid a[href="/stories/streetwear-the-logo-and-the-voice/"]')).toHaveCount(0);
 await page.getByRole('link',{name:'Catalogs',exact:true}).click();
 await expect(page).toHaveURL(/topic=catalogs#section-stories$/);
 await expect(page.locator('.hub-story-grid a[href="/stories/meet-me-at-the-mall/"]')).toBeVisible();
 await page.getByRole('link',{name:'Sports',exact:true}).click();
 await expect(page).toHaveURL(/#sports-moments$/);
 await expect(page.locator('#sports-moments')).toContainText('WNBA');
});

test('every story shares its own lead image and object references do not repeat that photograph',async({page})=>{
 test.setTimeout(90_000);
 const srcs=new Set();
 for(const [id,record] of Object.entries(media)){
  expect(srcs.has(record.sourceIdentity),id).toBe(false);srcs.add(record.sourceIdentity);
  await page.goto(`/stories/${id}/`);
  await expect(page.locator('.story-figure img')).toHaveAttribute('alt',record.alt);
  await expect(page.locator('.story-figure figcaption')).toContainText(record.caption);
  await expect(page.locator('meta[property="og:image"]')).toHaveAttribute('content',/\/assets\/generated\/share\/story-/);
 }
 await page.goto('/archive/objects/n64-controller/');
 await expect(page.locator('.ar-object-art img')).toHaveCount(1);
 const src=await page.locator('.ar-object-art img').getAttribute('src');
 await expect(page.locator(`main img[src="${src}"]`)).toHaveCount(1);
});

for(const width of [390,1440])test(`${width}px: every collection, year, and utility page is readable`,async({page})=>{
 test.setTimeout(180_000);
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 const pages=routes.filter(r=>!['redirects','stories','objects'].includes(r.type));
 for(const route of pages){
  const response=await page.goto(route.path);
  expect(response.status(),route.path).toBe(route.path==='/404.html'?404:200);
  await page.setViewportSize({width,height:900});
  await expect(page.locator('h1')).toHaveCount(1);
  await page.locator('main img').evaluateAll(imgs=>Promise.all(imgs.map(img=>{img.loading='eager';return img.decode();})));
  expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),route.path).toBe(false);
  if(process.env.POLISH_QA_DIR)await page.screenshot({path:`${process.env.POLISH_QA_DIR}/${route.path.replaceAll('/','_')}-${width}.png`,fullPage:true});
 }
 expect(errors).toEqual([]);
});
