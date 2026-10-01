import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import catalog from '../content/editorial/catalog.json' with {type:'json'};
import fs from 'node:fs';
const features=[...fs.readFileSync(new URL('../content/editorial/features.md',import.meta.url),'utf8').matchAll(/<!-- story: (.*?) -->/g)].map(m=>JSON.parse(m[1]));
const storyCount=category=>[...catalog.stories,...features].filter(s=>!category||s.category===category).length;
const hubCategory=path=>({'/zones/games/':'games','/zones/music/':'music','/zones/tv-movies/':'movies-tv','/zones/tech-toys/':'tech','/zones/culture/':'culture'}[path]);
const hubs=['/zones/games/','/zones/music/','/zones/tv-movies/','/zones/tech-toys/','/zones/culture/'];
for(const path of hubs){
 test(`complete hub, every advertised topic has content: ${path}`,async({page})=>{
  await page.goto(path);
  await expect(page.locator('h1')).toHaveCount(1);
  await expect(page.locator('[data-hub-story]')).toHaveCount(storyCount(hubCategory(path)));
  await page.locator('.ed-hero>img').evaluate(img=>img.decode());
  const links=await page.locator('[data-hub-filter="topic"], [data-hub-filter="genre"]').evaluateAll(as=>as.map(a=>a.getAttribute('href')));
  for(const href of links){
   await page.goto(path+href);
   const cards=page.locator(path.includes('games')?'[data-hub-game]:visible':'[data-hub-story]:visible');
   await expect.poll(()=>cards.count(),{message:href}).toBeGreaterThan(0);
  }
  await page.goto(path);
  const result=await new AxeBuilder({page}).analyze();
  expect(result.violations).toEqual([]);
 });
}
test('game genre and platform filters combine, recover and survive history',async({page})=>{
 await page.goto('/zones/games/?genre=rpg&platform=handhelds#game-archive');
 const games=page.locator('[data-hub-game]:visible');
 await expect(games).toHaveCount(1);await expect(games).toContainText('Pokémon');
 await page.locator('[data-hub-filter="platform"][data-value="consoles"]').click();
 await expect(games).toHaveCount(2);
 await page.reload();await expect(games).toHaveCount(2);
 await page.goBack();await expect(games).toHaveCount(1);
 await page.goto('/zones/games/?genre=shooters&platform=handhelds#game-archive');
 await expect(page.locator('[data-hub-empty="games"]')).toBeVisible();
 await page.getByRole('link',{name:'Reset game filters'}).click();
 await expect(games).toHaveCount(12);
 await page.goto('/zones/games/?genre=invalid&platform=unknown');await expect(games).toHaveCount(12);
});
test('hub content and the game shelf are available without scripts',async({browser,baseURL})=>{
 const context=await browser.newContext({baseURL, javaScriptEnabled:false});const page=await context.newPage();
 await page.goto('/zones/games/');
 await expect(page.locator('[data-hub-game]:visible')).toHaveCount(12);
 await page.locator('[data-hub-story]').first().getByRole('link').click();
 await expect(page.locator('#sources')).toBeVisible();await context.close();
});
test('Culture is a real hub with the original specialist collections intact',async({page})=>{
 await page.goto('/');await page.locator('#siteNav').getByRole('link',{name:'Culture',exact:true}).click();
 await expect(page).toHaveURL(/\/zones\/culture\//);
 for(const href of ['/zones/fashion/','/zones/internet-culture/','/zones/transparent-tech/'])await expect(page.locator(`main a[href="${href}"]`)).toBeVisible();
});

test('story library categories survive reload and recover from invalid values',async({page})=>{
 await page.goto('/stories/');
 const stories=page.locator('[data-hub-story]:visible');
 await expect(stories).toHaveCount(storyCount());
 for(const category of ['music','movies-tv','games','tech','culture']){
  await page.locator(`[data-hub-filter="category"][data-value="${category}"]`).click();
  await expect(stories).toHaveCount(storyCount(category));
  await expect(stories.first()).toHaveAttribute('data-category',category);
 }
 await page.reload();await expect(stories).toHaveCount(storyCount('culture'));
 await page.goto('/stories/?category=unknown');await expect(stories).toHaveCount(storyCount());
 const result=await new AxeBuilder({page}).analyze();expect(result.violations).toEqual([]);
});

test('category view-all links open matching stories and dated events',async({page})=>{
 await page.goto('/zones/music/');
 await page.locator('#section-stories').getByRole('link',{name:'VIEW ALL'}).click();
 await expect(page).toHaveURL(/stories\/\?category=music/);
 await expect(page.locator('[data-hub-story]:visible')).toHaveCount(storyCount('music'));
 await page.goto('/events/?category=games');
 await expect(page.locator('[data-hub-event]:visible')).toHaveCount(Math.min(18,catalog.events.filter(event=>event.category==='games').length));
 for(const card of await page.locator('[data-hub-event]:visible').all()) await expect(card).toHaveAttribute('data-category','games');
 await page.getByRole('link',{name:'All events',exact:true}).click();
 await page.getByRole('button',{name:'Next →',exact:true}).click();
 await expect(page).toHaveURL(/page=2/);
 await page.reload(); await expect(page.getByRole('status').last()).toContainText('Page 2');
 await page.goBack(); await expect(page.getByRole('status').last()).toContainText('Page 1');
});

test('resources retain a selected category and query through reload and history',async({page})=>{
 await page.goto('/webring/?filter=software-archives#directory');
 const cards=page.locator('#resourceGrid .resource-card:visible');
 await expect(cards).toHaveCount(11);
 await page.locator('[data-resource-filter="games-emulation"]').click();
 await expect(cards).toHaveCount(18);
 await page.reload(); await expect(page).toHaveURL(/filter=games-emulation/);
 await page.getByRole('button',{name:'Next →',exact:true}).click();
 await expect(cards).toHaveCount(3);
 await page.goBack(); await expect(cards).toHaveCount(18);
 await page.locator('#resourceSearch').fill('zzzz-no-resource');
 await expect(page.locator('#resourceNoResults')).toBeVisible();
});
