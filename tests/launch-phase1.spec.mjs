import {test, expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import catalog from '../content/editorial/catalog.json' with {type:'json'};
import routes from '../data/routes.json' with {type:'json'};
import {weekBounds, shiftDays, eventsInWeek} from '../js/date-utils.js';

// Exercise the real controls and rendered visibility against the source catalog.
// History is covered by archive.spec.mjs; suppress pushState only in the large
// matrix so Chromium's navigation rate limit cannot skip filter combinations.
for (const width of [390, 1440]) {
  for (let year = 1990; year <= 1999; year++) {
    test(`${width}px: ${year}, all months, categories, regions and views agree on empty states`, async ({page}) => {
      test.setTimeout(120_000);
      await page.setViewportSize({width, height:900});
      await page.goto(`/timeline/${year}/?month=01`);
      await expect(page.locator('[data-timeline]')).toHaveAttribute('data-ready', 'true');
      const failures = await page.evaluate(({events, year, width}) => {
        const category = document.querySelector('[data-category-filter]');
        const region = document.querySelector('[data-region-filter]');
        const root = document.querySelector('[data-timeline]');
        const failures = [];
        const push = history.pushState;
        history.pushState = () => {};
        try {
          for (let month = 1; month <= 12; month++) {
            document.querySelector(`[data-month="${month}"]`).click();
            const panel = root.querySelector(`[data-month-panel="${month}"]`);
            for (const cat of [...category.options].map(option => option.value)) {
              category.value = cat;
              category.dispatchEvent(new Event('change'));
              for (const reg of [...region.options].map(option => option.value)) {
                region.value = reg;
                region.dispatchEvent(new Event('change'));
                const expected = events.filter(event => event.date.startsWith(`${year}-${String(month).padStart(2, '0')}`) && (cat === 'all' || event.category === cat) && (reg === 'all' || event.region === reg)).length;
                for (const view of ['grid', 'list', 'calendar']) {
                  root.querySelector(`[data-archive-view="${view}"]`).click();
                  const empty = panel.querySelector('[data-month-empty]');
                  const calendarLinks = [...panel.querySelectorAll('.ar-calendar [data-event]')].filter(link => !link.hidden).length;
                  const cards = [...panel.querySelectorAll('.ar-event')].filter(card => !card.hidden).length;
                  const status = root.querySelector('[data-timeline-status]').textContent;
                  if (empty.hidden !== (expected > 0) || (getComputedStyle(empty).display === 'none') !== (expected > 0) || !status.startsWith(`${expected} sourced `) || calendarLinks !== expected || cards !== (view === 'calendar' ? expected : Math.min(expected, 12))) {
                    failures.push({year, month, cat, reg, view, width, expected, cards, calendarLinks, emptyHidden:empty.hidden, status});
                  }
                }
              }
            }
          }
        } finally { history.pushState = push; }
        return failures;
      }, {events:catalog.events, year, width});
      expect(failures).toEqual([]);
    });
  }
  test(`${width}px: every historical week keeps its count, events and empty state together`, async ({page}) => {
    test.setTimeout(120_000);
    await page.setViewportSize({width, height:900});
    await page.goto('/this-week/?date=1990-01-01');
    await expect(page.locator('[data-week-date]')).toHaveValue('1990-01-01');
    const weeks = [];
    for (let date = '1990-01-01'; date < '2000-01-01'; date = shiftDays(date, 7)) {
      weeks.push({date, count:eventsInWeek(catalog.events, date).length, ...weekBounds(date)});
    }
    const failures = await page.evaluate(weeks => {
      const failures = [], input = document.querySelector('[data-week-date]');
      const push = history.pushState;
      history.pushState = () => {};
      try {
        for (const week of weeks) {
          input.value = week.date;
          input.dispatchEvent(new Event('change'));
          const empty = document.querySelector('[data-week-empty]');
          const links = [...document.querySelectorAll('[data-week-days] .ar-week-event')];
          const status = document.querySelector('[data-week-count]').textContent;
          if (links.length !== week.count || empty.hidden !== (week.count > 0) || (getComputedStyle(empty).display === 'none') !== (week.count > 0) || !status.startsWith(`${week.count} sourced `)) failures.push({week, links:links.length, emptyHidden:empty.hidden, status});
          for (const day of document.querySelectorAll('[data-week-days] .ar-day')) {
            if (day.querySelector('.ar-week-event') && day.classList.contains('ar-day-empty')) failures.push({week, day:'populated day marked empty'});
          }
        }
      } finally { history.pushState = push; }
      return failures;
    }, weeks);
    expect(failures).toEqual([]);
  });
}

for (const width of [320, 390, 768, 1280, 1440]) {
  test(`${width}px: full museum directory is accessible and opens Passport`, async ({page}) => {
    await page.setViewportSize({width, height:900});
    await page.goto('/zones/culture/');
    await page.locator('#menuToggle').click();
    const directory = page.locator('#museumDirectory');
    await expect(directory).toBeVisible();
    await expect(directory.getByRole('link', {name:'Home', exact:true})).toBeFocused();
    for (const name of ['Explore', 'Collections', 'Play / Experience', 'More']) await expect(directory.getByRole('heading', {name, exact:true})).toBeVisible();
    for (const name of ['Fashion', 'Internet Culture', 'Objects', 'Search', 'Sources & Credits']) await expect(directory.getByRole('link', {name, exact:true})).toBeVisible();
    const results = await new AxeBuilder({page}).analyze();
    expect(results.violations).toEqual([]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth)).toBe(0);
    if ([390, 1440].includes(width)) await page.screenshot({path:`${process.env.LAUNCH_QA_DIR || "reports/launch-phase1"}/directory-${width}.png`});
    await directory.getByRole('button', {name:/^Passport/}).click();
    await expect(directory).toBeHidden();
    await expect(page.locator('#passportDialog')).toBeVisible();
    await expect(page.locator('[data-passport-rooms]')).toHaveText('1');
    await page.locator('[data-passport-reset-open]').click();
    await page.locator('[data-passport-reset-cancel]').click();
    await page.keyboard.press('Escape');
    await expect(page.locator('#menuToggle')).toBeFocused();
    await expect(page.locator('#menuToggle')).toHaveAttribute('aria-expanded', 'false');
    await page.locator('#menuToggle').click();
    await directory.getByRole('button', {name:'Close museum directory'}).click();
    await expect(page.locator('#menuToggle')).toBeFocused();
  });
}

test('Culture visits persist and count toward Room Hopper', async ({page}) => {
  for (const path of ['/zones/culture/', '/zones/music/', '/zones/games/']) await page.goto(path);
  await page.locator('[data-passport-trigger]').click();
  await expect(page.locator('[data-passport-rooms]')).toHaveText('3');
  await expect(page.locator('[data-passport-stamp="room-hopper"]')).toHaveClass(/is-earned/);
  await page.reload();
  await page.locator('[data-passport-trigger]').click();
  await expect(page.locator('[data-passport-rooms]')).toHaveText('3');
});

test('all tour stops work, completion survives reload and revisits, malformed anchors recover', async ({page}) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/tours/before-the-feed/#%E0%A4%A');
  const current = page.locator('[data-tour-stop]:visible');
  await expect(current).toHaveAttribute('data-tour-number', '1');
  for (let stop = 1; stop <= 6; stop++) {
    await expect(current).toHaveCount(1);
    await expect(current).toHaveAttribute('data-tour-number', String(stop));
    if (stop > 1) {
      await current.locator('[data-tour-back]').click();
      await expect(current).toHaveAttribute('data-tour-number', String(stop - 1));
      await current.locator('[data-tour-next]').click();
    }
    await current.locator('[data-tour-next]').click();
  }
  await expect(page.locator('[data-tour-progress-copy]')).toContainText('Tour complete');
  await page.reload();
  await expect(page.locator('[data-tour-progress-copy]')).toContainText('Tour complete');
  await current.locator('[data-tour-back]').click();
  await current.locator('[data-tour-next]').click();
  await expect(current.locator('[data-tour-next]')).toHaveText('Tour complete ✓');
  await page.goto('/');
  await page.locator('[data-passport-trigger]').click();
  await expect(page.locator('[data-tour-resume]')).toBeHidden();
  await expect(page.locator('[data-passport-stamp="before-the-feed"]')).toHaveClass(/is-earned/);
  expect(errors).toEqual([]);
});

test('Surprise Me fetch failure offers recovery and retries successfully', async ({page}) => {
  let requests = 0;
  await page.route('**/assets/runtime/surprise.json', route => ++requests === 1 ? route.abort() : route.continue());
  await page.goto('/');
  await page.locator('[data-surprise-trigger]').click();
  await expect(page.locator('[data-surprise-error]')).toBeVisible();
  await expect(page.locator('[data-surprise-loading]')).toBeHidden();
  expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
  await page.locator('[data-surprise-error] [data-surprise-retry]').click();
  await expect(page.locator('[data-surprise-ready]')).toBeVisible();
  await expect(page.locator('[data-surprise-error]')).toBeHidden();
  await page.locator('[data-surprise-open]').click();
  await expect(page.locator('main')).toBeVisible();
  await expect(page.locator('h1')).toHaveCount(1);
});

test('resetting Passport also clears the completed tour controls', async ({page}) => {
  await page.goto('/tours/before-the-feed/#portals-and-precursors');
  // Static fallback shows all stops until progressive enhancement selects one.
  await expect(page.locator('[data-tour-stop]:visible')).toHaveCount(1);
  await expect(page.locator('[data-tour-stop]:visible')).toHaveAttribute('id','portals-and-precursors');
  await page.locator('[data-tour-stop]:visible [data-tour-next]').click();
  await page.locator('[data-passport-trigger]').click();
  await page.locator('[data-passport-reset-open]').click();
  await page.locator('[data-passport-reset-confirm]').click();
  await expect(page.locator('[data-passport-stamps]')).toHaveText('0');
  await page.keyboard.press('Escape');
  await expect(page.locator('[data-tour-stop]:visible [data-tour-next]')).toBeEnabled();
  await expect(page.locator('[data-tour-stop]:visible [data-tour-next]')).toHaveText('Complete tour');
});

test('directory and primary routes remain available without JavaScript', async ({browser, baseURL}) => {
  const context = await browser.newContext({baseURL, javaScriptEnabled:false, viewport:{width:320, height:900}});
  const page = await context.newPage();
  await page.goto('/');
  await expect(page.locator('.directory-fallback')).toBeVisible();
  await expect(page.locator('#siteNav')).toBeVisible();
  await page.locator('.directory-fallback').click();
  await expect(page.locator('h1')).toHaveText('Site map');
  await context.close();
});

for (let batch = 0; batch < routes.length; batch += 60) {
  test(`public runtime and image QA: routes ${batch + 1}–${Math.min(batch + 60, routes.length)}`, async ({page}) => {
    test.setTimeout(180_000);
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
    page.on('response', response => {if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`);});
    for (const route of routes.slice(batch, batch + 60)) {
      await page.goto(route.path);
      await expect(page.locator('h1')).toHaveCount(1);
      const failedImages = await page.evaluate(async () => {
        const images = [...document.querySelectorAll('img')];
        return (await Promise.all(images.map(async image => {
          image.loading = 'eager';
          try {await image.decode(); return null;} catch {return image.currentSrc || image.src;}
        }))).filter(Boolean);
      });
      expect(failedImages, route.path).toEqual([]);
    }
    expect(errors).toEqual([]);
  });
}
