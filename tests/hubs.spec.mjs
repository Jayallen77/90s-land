import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
const hubs=['/zones/games/','/zones/music/','/zones/tv-movies/','/zones/tech-toys/','/zones/culture/'];
for(const path of hubs){
 test(`complete hub, every advertised topic has content: ${path}`,async({page})=>{
  await page.goto(path);
  await expect(page.locator('h1')).toHaveCount(1);
  await expect(page.locator('[data-hub-story]')).toHaveCount(6);
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
 await expect(stories).toHaveCount(30);
 for(const category of ['music','movies-tv','games','tech','culture']){
  await page.locator(`[data-hub-filter="category"][data-value="${category}"]`).click();
  await expect(stories).toHaveCount(6);
  await expect(stories.first()).toHaveAttribute('data-category',category);
 }
 await page.reload();await expect(stories).toHaveCount(6);
 await page.goto('/stories/?category=unknown');await expect(stories).toHaveCount(30);
 const result=await new AxeBuilder({page}).analyze();expect(result.violations).toEqual([]);
});
