import {test,expect} from './browser-fixtures.mjs';
import AxeBuilder from '@axe-core/playwright';

for(const width of [390,1440])test(`${width}px: reading tools explain storage and shared letter keys`,async({page})=>{
 await page.setViewportSize({width,height:900});
 await page.goto('/stories/thirty-two-megabytes/');
 const storage=page.locator('[data-reading-tool="mp3-budget"]');
 await expect(storage.locator('[data-reading-result]')).toContainText('33:20');
 await page.getByLabel('Constant bitrate').selectOption('64');
 await expect(storage.locator('[data-reading-result]')).toContainText('66:40');
 await page.getByLabel('Storage (decimal MB)').fill('1');
 await page.getByLabel('Track length (minutes)').fill('12');
 await expect(storage.locator('[data-reading-result]')).toContainText('0 whole 12-minute tracks');
 await page.getByLabel('Storage (decimal MB)').fill('');
 await expect(storage.locator('[data-reading-result]')).toContainText('Use 1–512');
 await expect(storage.locator('[data-reading-result]')).not.toContainText('NaN');
 expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
 await page.goto('/stories/texting-on-twelve-keys/');
 const result=page.locator('[data-reading-result]');
 await expect(result).toContainText('13 letter presses');
 await page.getByLabel('Word to compare (A–Z)').fill('HOME');
 await expect(result).toContainText('4663');
 await page.getByLabel('Word to compare (A–Z)').focus();
 await page.keyboard.press('ControlOrMeta+A');await page.keyboard.type('GOOD');await page.keyboard.press('Enter');
 await expect(result).toContainText('4663');
 await page.getByLabel('Word to compare (A–Z)').fill('<script>');
 await expect(result).toContainText('Enter one word');
 expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
});

test('new reading controls wait until their module is ready',async({page})=>{
 let release,seen;
 const ready=new Promise(resolve=>{release=resolve;});const requested=new Promise(resolve=>{seen=resolve;});
 await page.route('**/js/reading-tools.js*',async route=>{seen();await ready;await route.continue();});
 try{
  await page.goto('/stories/thirty-two-megabytes/',{waitUntil:'domcontentloaded'});await requested;
  await expect(page.getByLabel('Constant bitrate')).toBeDisabled();
  await expect(page.locator('[data-reading-result]')).toContainText('33:20');
  release();await expect(page.getByLabel('Constant bitrate')).toBeEnabled();
  await page.getByLabel('Constant bitrate').selectOption('64');await expect(page.locator('[data-reading-result]')).toContainText('66:40');
 }finally{release();}
});

test('SMS finds the specific keypad story and survives search history',async({page})=>{
 await page.goto('/search/?q=SMS');
 await expect(page.locator('.site-search-card:visible').first()).toHaveAttribute('href','/stories/texting-on-twelve-keys/');
 await page.locator('[data-site-filter="stories"]').click();
 await page.locator('#siteSearchInput').fill('TR-909');
 await page.goBack();await expect(page.locator('#siteSearchInput')).toHaveValue('SMS');
 await page.locator('#siteSearchInput').fill('TR-909');
 await expect(page.locator('.site-search-card[href="/archive/objects/tr-909/"]')).toBeVisible();
});

test('new object collection persists alongside the existing Passport',async({page})=>{
 await page.goto('/archive/objects/game-link-cable/');
 await page.locator('[data-artifact-inspect="game-link-cable"]').click();
 await page.reload();
 await expect(page.locator('[data-artifact-inspect="game-link-cable"]')).toHaveText('Collected ✓');
 await page.locator('[data-passport-trigger]').click();
 await expect(page.locator('#passportDialog')).toContainText('1 objects inspected');
 await expect(page.locator('#passportDialog')).toContainText('Object Handler');
});

test.describe('static reading examples',()=>{
 test.use({javaScriptEnabled:false});
 for(const [slug,example] of [['thirty-two-megabytes','33:20'],['texting-on-twelve-keys','13 letter presses']])test(`${slug} remains readable without scripts`,async({page})=>{
  await page.goto('/stories/'+slug+'/');
  await expect(page.locator('[data-reading-result]')).toContainText(example);
  await expect(page.locator('[data-reading-tool] noscript')).toBeVisible();
  for(const control of await page.locator('[data-reading-tool] input,[data-reading-tool] select').all())await expect(control).toBeDisabled();
  await expect(page.getByRole('heading',{name:'Sources',exact:true})).toBeVisible();
 });
});
