import {test,expect} from './browser-fixtures.mjs';
import AxeBuilder from '@axe-core/playwright';
test.use({hasTouch:true});
async function accessible(page){expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);}

test('R&B is a subject, not two letters scattered through the catalog',async({page})=>{
 await page.goto('/search/?q=R%26B');
 const cards=page.locator('.site-search-card:visible');
 await expect(cards.first()).toHaveAttribute('href','/stories/rnb-had-many-voices/');
 await expect(cards.filter({hasText:'Guestbook preview'})).toHaveCount(0);
 expect(await cards.count()).toBeLessThan(100);
 for(const [query,path] of [['Nintendo 64','/archive/objects/n64-controller/'],['PS1','/archive/objects/playstation-hardware/']]){
  await page.locator('#siteSearchInput').fill(query);
  await expect(page.locator(`.site-search-card[href="${path}"]`)).toBeVisible();
 }
});

for(const width of [390,1440])test(`${width}px: all six original exhibits work without sending data`,async({page})=>{
 await page.setViewportSize({width,height:900});
 await page.goto('/archive/objects/geocities-homepage/');
 await expect(page.getByText('WELCOME TO THE MIX TAPE PLANET')).toBeVisible();
 await page.getByRole('button',{name:'Add tiled stars',exact:true}).tap();
 await expect(page.locator('[data-homepage-preview]')).toHaveClass(/has-stars/);
 await accessible(page);
 await page.goto('/archive/objects/visitor-counter/');
 await page.getByRole('button',{name:'Preview another visit'}).tap();
 await expect(page.locator('[data-demo-count]')).toHaveText('000248');
 await page.getByRole('button',{name:'Preview another visit'}).focus();await page.keyboard.press('Enter');
 await expect(page.locator('[data-demo-count]')).toHaveText('000249');
 await page.reload();await expect(page.locator('[data-demo-count]')).toHaveText('000247');
 await accessible(page);
 await page.goto('/archive/objects/guestbook/');
 await page.getByLabel('Your handle').fill('test_reader');await page.getByLabel('Your message').fill('<b>Local text, not HTML</b>');
 await page.getByRole('button',{name:'Preview my entry',exact:true}).tap();
 await expect(page.locator('[data-guestbook-preview]')).toContainText('<b>Local text, not HTML</b>');
 await expect(page.locator('[data-guestbook-preview] b')).toHaveCount(0);
 await accessible(page);
 await page.goto('/archive/objects/webring-bar/');
 await page.getByRole('button',{name:'Next page →',exact:true}).tap();
 await expect(page.locator('[data-ring-title]')).toHaveText('Pixel Pilot’s Game Notes');
 await page.getByRole('button',{name:'← Previous page',exact:true}).tap();
 await expect(page.locator('[data-ring-title]')).toHaveText('Tape Deck Planet');
 await accessible(page);
 await page.goto('/archive/objects/aim-away-message/');
 await page.getByLabel('Your away message').fill('At the record shop. Back soon.');
 await page.getByRole('button',{name:'Preview away message',exact:true}).tap();
 await expect(page.locator('[data-away-preview]')).toHaveText('At the record shop. Back soon.');
 await accessible(page);
 await page.goto('/archive/objects/yahoo-directory/');
 await page.locator('.web-category').filter({hasText:'Music'}).locator('summary').tap();
 await expect(page.locator('.web-category a[href="/stories/from-mixtape-to-file/"]')).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 await accessible(page);
});


test('homepage controls wait for their delayed module before accepting input',async({page})=>{
 let release;
 const moduleReady=new Promise(resolve=>{release=resolve;});
 let intercepted;
 const requestSeen=new Promise(resolve=>{intercepted=resolve;});
 await page.route('**/js/tour.js*',async route=>{intercepted();await moduleReady;await route.continue();});
 await page.setViewportSize({width:1440,height:900});
 try{
  await page.goto('/archive/objects/geocities-homepage/',{waitUntil:'domcontentloaded'});
  await requestSeen;
  const stars=page.getByRole('button',{name:'Add tiled stars',exact:true});
  await expect(stars).toBeDisabled();
  release();
  await expect(stars).toBeEnabled();
  await stars.tap();
  await expect(page.locator('[data-homepage-preview]')).toHaveClass(/has-stars/);
 }finally{release();}
});

test('sparse-week reading is labeled separately and empty days can be revealed',async({page})=>{
 await page.goto('/this-week/?date=1996-11-05');
 await expect(page.locator('[data-week-count]')).toHaveText('0 sourced entries');
 await expect(page.locator('[data-week-reading]')).toBeVisible();
 await expect(page.locator('[data-reading-title]')).toHaveText('From the 1996 collection');
 await expect(page.locator('[data-reading-links] a')).toHaveCount(4);
 await expect(page.locator('.ar-day-empty:visible')).toHaveCount(0);
 await page.locator('[data-show-empty-days]').check();
 await expect(page.locator('.ar-day-empty:visible')).toHaveCount(7);
 await page.locator('[data-week-select]').selectOption('1994');
 await expect(page.locator('[data-reading-title]')).toHaveText('From the 1994 collection');
});
