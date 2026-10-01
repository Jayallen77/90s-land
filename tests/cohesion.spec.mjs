import fs from 'node:fs';
import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
const routes=['/events/?category=culture','/zones/fashion/','/zones/transparent-tech/','/webring/','/guestbook/','/credits/','/sitemap/','/surprise/','/404.html'];
for(const route of routes){
 test(`shared design and accessibility: ${route}`,async({page})=>{
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
  await page.goto(route);await page.evaluate(()=>document.fonts.ready);
  await expect(page.locator('html')).toHaveClass('js');
  await expect(page.locator('h1')).toHaveCount(1);
  await expect(page.locator('.ed-header,.ed-footer')).toHaveCount(2);
  await expect(page.locator('.window,.window-bar,.ed-preserved,.ed-reading-room')).toHaveCount(0);
  const result=await new AxeBuilder({page}).analyze();expect(result.violations).toEqual([]);
  expect(errors).toEqual([]);
 });
}
test('search pagination retains its place without losing the selected filter',async({page})=>{
 await page.goto('/search/?filter=objects');
 await expect(page.locator('.site-search-card:visible')).toHaveCount(18);
 await page.getByRole('button',{name:'Next →',exact:true}).click();
 await expect(page).toHaveURL(/filter=objects&page=2/);
 await expect(page.locator('.site-search-card:visible')).toHaveCount(Math.min(18,JSON.parse(fs.readFileSync(new URL('../data/artifacts.json',import.meta.url),'utf8')).length-18));
 await page.reload();await expect(page.locator('.site-search-card:visible')).toHaveCount(Math.min(18,JSON.parse(fs.readFileSync(new URL('../data/artifacts.json',import.meta.url),'utf8')).length-18));
 await page.goBack();await expect(page.locator('.site-search-card:visible')).toHaveCount(18);
});
