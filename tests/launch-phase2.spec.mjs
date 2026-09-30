import {test, expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import curation from '../content/editorial/curation.json' with {type:'json'};
import catalog from '../content/editorial/catalog.json' with {type:'json'};

test('homepage exposes years, collections, search, objects and experiences', async ({page}) => {
  await page.goto('/');
  const years = page.getByRole('navigation', {name:'Browse a year'});
  await expect(years.getByRole('link')).toHaveCount(10);
  for (let year = 1990; year <= 1999; year++) {
    await expect(years.getByRole('link', {name:new RegExp(`^${year}`)})).toHaveAttribute('href', `/timeline/${year}/`);
  }
  await expect(page.locator('.artifact-shelf .artifact-ticket')).toHaveCount(4);
  await expect(page.locator('.ed-experiences a[href="/tours/before-the-feed/"]')).toBeVisible();
  await expect(page.locator('.ed-experiences a[href="/surprise/"]')).toBeVisible();
  const passport = page.locator('[data-home-passport]');
  await passport.click();
  await expect(page.locator('#passportDialog')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(passport).toBeFocused();
  await page.locator('.ed-home-search input').fill('Friends');
  await page.locator('.ed-home-search button').click();
  await expect(page).toHaveURL(/\/search\/\?q=Friends/);
  await expect(page.locator('.site-search-card:visible').first()).toHaveAttribute('href','/events/friends-premiere/');
});

for (const capsule of curation.years) {
  test(`${capsule.year} keeps defining moments visible while filtering the full calendar`, async ({page}) => {
    await page.goto(`/timeline/${capsule.year}/?month=01`);
    const moments = page.locator('[data-defining-event]');
    await expect(moments).toHaveCount(capsule.eventIds.length);
    expect(await moments.evaluateAll(items=>items.map(item=>item.dataset.definingEvent))).toEqual(capsule.eventIds);
    await expect(page.locator('#year-stories .ar-story-card')).toHaveCount(5);
    await expect(page.locator('#year-objects .artifact-ticket')).toHaveCount(4);
    await page.locator('[data-category-filter]').selectOption('news');
    await expect(moments).toHaveCount(capsule.eventIds.length);
    await expect(moments.first()).toBeVisible();
    for (const id of capsule.eventIds) {
      const event = catalog.events.find(event=>event.id===id);
      await expect(page.locator(`[data-defining-event="${id}"]`)).toHaveAttribute('href',`/events/${event.slug}/`);
    }
  });
}

test('search ranks titles, matches accents and punctuation, and counts each content type', async ({page}) => {
  await page.goto('/search/?q=a+whole+new+dimension');
  await expect(page.locator('.site-search-card:visible').first()).toHaveAttribute('href','/stories/a-whole-new-dimension/');
  await page.locator('#siteSearchInput').fill('Pokémon—1996');
  await page.locator('[data-site-filter="events"]').click();
  await expect(page.locator('.site-search-card:visible')).toHaveCount(1);
  await expect(page.locator('.site-search-card:visible')).toHaveAttribute('href','/events/pokemon-red-green-japan/');
  await expect(page.locator('[data-site-filter="events"] span')).toHaveText('1');
  await page.locator('#siteSearchInput').fill('n64');
  await expect(page.locator('[data-site-filter="objects"] span')).not.toHaveText('0');
  await expect(page.locator('[data-site-filter="stories"] span')).not.toHaveText('0');
  await page.locator('[data-site-filter="objects"]').click();
  await expect(page.locator('.site-search-card:visible[href="/archive/objects/n64-controller/"]')).toBeVisible();
  await page.goBack();
  await expect(page.locator('[data-site-filter="events"]')).toHaveAttribute('aria-pressed','true');
});

test('N64 and the PC tour offer relevant onward paths', async ({page}) => {
  await page.goto('/events/nintendo-64-us/');
  await expect(page.locator('.ed-context-path a[href="/zones/games/"]')).toBeVisible();
  await expect(page.locator('.ed-context-path a[href="/timeline/1996/#defining-moments"]')).toBeVisible();
  await expect(page.locator('.ar-related[href="/archive/objects/n64-controller/"]')).toBeVisible();
  await expect(page.locator('.ar-story-card[href="/stories/a-whole-new-dimension/"]')).toBeVisible();
  await page.goto('/tours/before-the-feed/');
  const stop = page.locator('[data-tour-stop]:visible');
  await expect(stop.locator('a[href="/stories/the-family-computer/"]')).toBeVisible();
  await expect(stop.locator('a[href="/events/windows-95-launch/"]')).toBeVisible();
});

test('object connections stay selective with access to the complete related dates', async ({page}) => {
  await page.goto('/archive/objects/vhs-tape/');
  await expect(page.locator('.ar-related[href^="/events/"]')).toHaveCount(3);
  await page.getByRole('link',{name:'More dates connected to this object →'}).click();
  await expect(page.locator('#siteSearchCount')).not.toHaveText('Showing 0 matches.');
  await expect(page.locator('.site-search-card:visible').first()).toHaveAttribute('data-search-category','events');
});

for (const width of [390, 1440]) {
  for (const [path, name] of [['/','home'], ['/timeline/1991/','year-1991'], ['/timeline/1992/','year-1992'], ['/timeline/1994/','year-1994'], ['/timeline/1996/','year-1996'], ['/search/?q=n64','search']]) {
    test(`${width}px: Phase 2 ${name} is readable and accessible`, async ({page}) => {
      await page.setViewportSize({width,height:900});
      await page.goto(path);
      await page.evaluate(()=>document.fonts.ready);
      expect(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth)).toBe(0);
      expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
      await page.screenshot({path:`${process.env.LAUNCH_QA_DIR || "reports/launch-phase2"}/${name}-${width}.png`,fullPage:true});
      await page.screenshot({path:`${process.env.LAUNCH_QA_DIR || "reports/launch-phase2"}/${name}-${width}-top.png`});
    });
  }
}
