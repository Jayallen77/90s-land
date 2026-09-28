import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const surfaces=['/','/timeline/','/timeline/1996/?month=06&view=calendar','/zones/games/','/zones/music/','/zones/tv-movies/','/zones/tech-toys/','/zones/culture/','/this-week/','/stories/','/stories/the-console-war-couch/','/archive/objects/n64-controller/','/search/?q=1996','/tours/before-the-feed/','/zones/fashion/','/zones/internet-culture/','/zones/transparent-tech/'];

test('320px reflow keeps primary headings and interactive controls readable',async({page})=>{
 await page.setViewportSize({width:320,height:812});
 for(const route of surfaces){
  await page.goto(route);await page.evaluate(()=>document.fonts.ready);
  await expect(page.locator('h1')).toBeVisible();
  const layout=await page.evaluate(()=>{
   const h=document.querySelector('h1'),range=document.createRange();range.selectNodeContents(h);const rect=range.getBoundingClientRect();
   return {overflow:document.documentElement.scrollWidth-innerWidth,clippedHeading:rect.left<0||rect.right>innerWidth+1};
  });
  expect(layout,route).toEqual({overflow:0,clippedHeading:false});
 }
});

test('mobile game links have comfortable hit areas and accessible labels',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/zones/games/');
 for(const control of await page.locator('.hub-rail a,.hub-game-copy>div>a').all()){
  expect((await control.boundingBox()).height).toBeGreaterThanOrEqual(44);
 }
 const result=await new AxeBuilder({page}).withRules(['target-size','label-content-name-mismatch']).analyze();expect(result.violations).toEqual([]);
});

test('keyboard navigation opens the menu, filters games and returns from Passport',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/zones/games/');
 await page.locator('#menuToggle').focus();await page.keyboard.press('Enter');
 await expect(page.locator('#siteNav a').first()).toBeFocused();
 await page.keyboard.press('Escape');await expect(page.locator('#menuToggle')).toBeFocused();
 await page.locator('[data-hub-filter="genre"][data-value="racing"]').focus();await page.keyboard.press('Enter');
 await expect(page.locator('[data-hub-game]:visible')).toHaveCount(2);
 const trigger=page.locator('[data-passport-trigger]').first();await trigger.focus();await page.keyboard.press('Enter');
 await expect(page.locator('#passportDialog')).toBeVisible();await page.keyboard.press('Escape');await expect(trigger).toBeFocused();
});

test('failed enhancement import restores the navigable static archive',async({page})=>{
 await page.route('**/js/archive.js*',r=>r.abort());await page.goto('/timeline/1996/');
 await expect(page.locator('html')).toHaveClass('no-js');
 await expect(page.locator('[data-month-panel]:visible')).toHaveCount(12);
 await expect(page.locator('#siteNav')).toBeVisible();
});

test('runtime requests use optimized fonts and responsive object images',async({page})=>{
 const requests=[];page.on('request',request=>requests.push(request.url()));
 await page.goto('/');await page.evaluate(()=>document.fonts.ready);
 await page.locator('.ed-six-up').scrollIntoViewIfNeeded();
 await page.locator('.ed-six-up img').first().evaluate(img=>img.decode());
 expect(requests.filter(url=>url.includes('/assets/fonts/')&&url.endsWith('.ttf'))).toEqual([]);
 expect(await page.locator('.ed-six-up img').first().evaluate(img=>img.currentSrc)).toContain('/assets/generated/editorial/');
});
