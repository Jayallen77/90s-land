import { test as base } from '@playwright/test';
import publication from '../content/editorial/publication.json' with {type:'json'};
export { expect } from '@playwright/test';

// The document load event precedes app.js's dynamic enhancement imports.
// Wait for existing UI readiness signals before interacting or navigating away.
// Static/failure-mode tests must still be able to inspect the no-JS fallback.
async function waitForEnhancements(page) {
  await page.waitForFunction(() => {
    if (document.documentElement.classList.contains('no-js')) return true;
    const passport = document.querySelector('[data-passport-trigger]');
    if (passport?.hidden) return false;
    const timeline = document.querySelector('[data-timeline]');
    if (timeline && timeline.dataset.ready !== 'true') return false;
    const hub = document.querySelector('[data-hub]');
    if (hub && [...hub.querySelectorAll('[data-hub-status]')].some(node => !node.textContent.trim())) return false;
    const search = document.querySelector('#siteSearchGrid');
    if (search && !search.hasAttribute('data-search-ready')) return false;
    return true;
  }, undefined, { timeout: 15_000 });
}

export const test = base.extend({
  page: async ({ page }, use) => {
    for (const method of ['goto', 'reload', 'goBack', 'goForward']) {
      const navigate = page[method].bind(page);
      page[method] = async (...args) => {
        const response = await navigate(...args);
        const target=method==='goto' && publication.redirects[new URL(args[0],'http://localhost').pathname];
        if(target){const destination=new URL(target,'http://localhost');await page.waitForURL(url=>url.pathname===destination.pathname && url.hash===destination.hash,{waitUntil:'load'});}
        await waitForEnhancements(page);
        return response;
      };
    }
    await use(page);
  },
});
