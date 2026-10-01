import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import routes from "../data/routes.json" with { type: "json" };
import artifacts from "../data/artifacts.json" with { type: "json" };
import resources from "../data/resources.json" with { type: "json" };

const viewports = [
  { name: "mobile", width: 390, height: 844 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "desktop", width: 1280, height: 800 },
  { name: "wide", width: 1440, height: 900 }
];

for (const viewport of viewports) {
 for(let batch=0;batch<routes.length;batch+=60){
  test(`${viewport.name}: routes ${batch+1}–${Math.min(batch+60,routes.length)} stay inside the viewport`, async ({ page }) => {
    test.setTimeout(180_000);
    await page.setViewportSize(viewport);
    for (const route of routes.slice(batch,batch+60)) {
      await page.goto(route.path);
      await expect(page.locator("#main-content")).toBeVisible();
      const layout = await page.evaluate(() => ({
        root: document.documentElement.scrollWidth - window.innerWidth,
        body: document.body.scrollWidth - window.innerWidth,
        clippedControls: [...document.querySelectorAll("a, button")].filter((element) => {
          const rect = element.getBoundingClientRect();
          return (
            rect.width > 0 &&
            rect.height > 0 &&
            (rect.right > window.innerWidth + 1 || rect.left < -1)
          );
        }).length
      }));
      expect(layout.root, route.path).toBeLessThanOrEqual(0);
      expect(layout.body, route.path).toBeLessThanOrEqual(0);
      expect(layout.clippedControls, route.path).toBe(0);
    }
  });
 }
}

test("editorial home keeps its headline, hero and primary action above the fold", async ({ page }) => {
  for (const viewport of [
    { width: 390, height: 844 },
    { width: 1280, height: 800 }
  ]) {
    await page.setViewportSize(viewport);
    await page.goto("/");
    await expect(page.locator(".ed-hero h1")).toBeInViewport();
    await expect(page.locator(".ed-hero > img")).toBeInViewport();
    await expect(page.getByRole("link", { name: "Explore the decade", exact: true }).first()).toBeInViewport();
    await expect(page.locator("#this-week")).toBeInViewport();
  }
});

test("mobile menu focuses the first link and restores focus", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const toggle = page.locator(".menu-toggle");
  await toggle.click();
  await expect(toggle).toHaveAttribute("aria-expanded", "true");
  await expect(page.locator("#museumDirectory a").first()).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(toggle).toHaveAttribute("aria-expanded", "false");
  await expect(toggle).toBeFocused();
});

test("Surprise Me excludes the three most recent choices", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Surprise me", exact: true }).first().click();
  await expect(page.locator("[data-surprise-ready]")).toBeVisible();
  const titles = [];
  for (let index = 0; index < 6; index += 1) {
    const title = await page.locator("[data-surprise-title]").textContent();
    expect(titles.slice(-3)).not.toContain(title);
    titles.push(title);
    if (index < 5) {
      await page.locator("[data-surprise-again]").click();
      await expect(page.locator("[data-surprise-ready]")).toBeVisible();
    }
  }
});

test("passport persists and resets through confirmation", async ({ page }) => {
  await page.goto("/");
  const objectId = await page.locator('[data-artifact-inspect]').first().getAttribute('data-artifact-inspect');
  await page.locator(`[data-artifact-inspect="${objectId}"]`).click();
  await page.reload();
  await expect(page.locator(`[data-artifact-inspect="${objectId}"]`)).toHaveText(
    "Inspected ✓"
  );
  await page.locator("[data-passport-trigger]").click();
  await expect(page.locator("[data-passport-artifacts]")).toHaveText("1");
  await expect(page.locator('[data-passport-stamp="first-touch"]')).toHaveClass(
    /is-earned/
  );
  await page.locator("[data-passport-reset-open]").click();
  await page.locator("[data-passport-reset-cancel]").click();
  await expect(page.locator("#passportDialog")).toBeVisible();
  await page.locator("[data-passport-reset-open]").click();
  await page.locator("[data-passport-reset-confirm]").click();
  await expect(page.locator("[data-passport-artifacts]")).toHaveText("0");
});

test("passport announces an in-memory fallback", async ({ browser, baseURL }) => {
  const context = await browser.newContext({ baseURL });
  await context.addInitScript(() => {
    Object.defineProperty(window, "localStorage", {
      get() {
        throw new DOMException("blocked", "SecurityError");
      }
    });
  });
  const page = await context.newPage();
  await page.goto("/");
  await page.locator("[data-passport-trigger]").click();
  await expect(page.locator("[data-storage-note]")).toContainText(
    "will not persist"
  );
  await context.close();
});

test("tour deep links, recreation, resume, and completion work", async ({ page }) => {
  await page.goto("/tours/before-the-feed/#mosaic-visual-web");
  const currentStop = page.locator("[data-tour-stop]:not([hidden])");
  await expect(currentStop).toHaveCount(1);
  await expect(currentStop).toHaveAttribute(
    "id",
    "mosaic-visual-web"
  );
  await page.locator("[data-tour-stop]:visible [data-tour-next]").click();
  await expect(page).toHaveURL(/#handmade-geocities$/);
  await page.locator('[data-homepage-toggle="stars"]').click();
  await expect(page.locator("[data-homepage-preview]")).toHaveClass(/has-stars/);
  await page.goto("/");
  await page.locator("[data-passport-trigger]").click();
  await expect(page.locator("[data-tour-resume]")).toBeVisible();
  await page.locator('[data-dialog-close="passportDialog"]').click();
  await page.goto("/tours/before-the-feed/#portals-and-precursors");
  await expect(currentStop).toHaveCount(1);
  await expect(currentStop).toHaveAttribute("id", "portals-and-precursors");
  await page.locator("[data-tour-stop]:visible [data-tour-next]").click();
  await expect(page.locator("[data-tour-progress-copy]")).toContainText(
    "Tour complete"
  );
  await page.locator("[data-passport-trigger]").click();
  await expect(page.locator('[data-passport-stamp="before-the-feed"]')).toHaveClass(
    /is-earned/
  );
});

test("search counts stay synchronized with the catalog", async ({ page }) => {
  await page.goto("/search/");
  const searchableRoutes = routes.filter(
    (route) => !["/", "/search/", "/sitemap/", "/credits/"].includes(route.path) && route.type !== "objects"
  );
  await expect(page.locator('[data-site-filter="objects"] span')).toHaveText(String(artifacts.length));
  await expect(page.locator('#searchSummaryObjects')).toBeEmpty();
  await expect(page.locator('[data-site-filter="all"] span')).toHaveText(
    String(searchableRoutes.length + artifacts.length + resources.length)
  );
});

test("search preserves URL state and gives recovery actions", async ({ page }) => {
  await page.goto("/search/?q=mosaic&filter=objects");
  await expect(page.locator("#siteSearchInput")).toHaveValue("mosaic");
  await expect(page.locator('[data-site-filter="objects"]')).toHaveAttribute(
    "aria-pressed",
    "true"
  );
  await expect(page.locator(".site-search-card:visible")).toHaveCount(1);
  await page.locator('[data-site-filter="zones"]').click();
  await expect(page).toHaveURL(/filter=zones/);
  await page.goBack();
  await expect(page.locator('[data-site-filter="objects"]')).toHaveAttribute(
    "aria-pressed",
    "true"
  );
  await page.locator("#siteSearchInput").fill("definitely-not-a-memory");
  await expect(page.locator("#siteSearchNoResults")).toBeVisible();
  await page.locator("[data-search-clear]").click();
  await expect(page).toHaveURL(/\/search\/$/);
});

test("guestbook sends and stores nothing", async ({ page }) => {
  await page.goto("/guestbook/");
  await expect(page.locator("form")).not.toHaveAttribute("action");
  await page.getByLabel("Your handle").fill("dialupkid");
  await page.getByLabel("Your message").fill("This museum rules.");
  await page
    .getByRole("button", { name: "Preview my entry — not saved" })
    .click();
  await expect(page.locator("[data-guestbook-preview]")).toContainText("dialupkid");
  await page.reload();
  await expect(page.locator("[data-guestbook-preview]")).toBeHidden();
});

test("core museum content and fallbacks work without JavaScript", async ({ browser, baseURL }) => {
  const context = await browser.newContext({ baseURL, javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("/");
  await expect(page.getByRole("link", { name: "Surprise me", exact: true }).first()).toHaveAttribute(
    "href",
    "/surprise/"
  );
  await expect(page.locator("[data-passport-trigger]")).toBeHidden();
  await page.goto("/tours/before-the-feed/#mosaic-visual-web");
  await expect(page.locator("[data-tour-stop]")).toHaveCount(6);
  await expect(page.locator("[data-tour-stop]:visible")).toHaveCount(6);
  await page.goto("/surprise/");
  await expect(page.locator(".mystery-envelope")).toHaveCount(
    11
  );
  await context.close();
});

test("timeline year-door artwork identifies its exhibit and editorial recreations", async ({ page }) => {
  await page.goto("/timeline/");
  await expect(page.locator(".timeline-card-artwork")).toHaveCount(10);
  await expect(page.locator('[data-timeline-room="timeline-1994"] .timeline-artwork-label')).toHaveText("EDITORIAL RECREATION · PERSONAL HOMEPAGE");
  await expect(page.locator('[data-timeline-room="timeline-1997"] .timeline-artwork-label')).toHaveText("EDITORIAL RECREATION · BUDDY LIST");
  await expect(page.locator('[data-timeline-room="timeline-1995"] .timeline-artwork-label')).toContainText("COLLECTION OBJECT");
});

test("year calendar uses real days and supports old month bookmarks", async ({ page }) => {
  await page.goto('/timeline/1996/?month=06&view=calendar');
  const calendar = page.locator('[data-month-panel="6"] .ar-calendar');
  await expect(calendar).toBeVisible();
  await expect(calendar.locator('time')).toHaveCount(30);
  await expect(calendar.locator('tbody tr').first().locator('td').nth(5).locator('time')).toHaveAttribute('datetime','1996-06-01');
  await page.locator('[data-month="7"]').click();
  await expect(page).toHaveURL(/month=07&view=calendar/);
  await expect(page.locator('[data-month-panel="7"] .ar-calendar')).toBeVisible();
  await page.goto('/timeline/1996/#month-jul');
  await expect(page.locator('[data-month-panel="7"]')).toBeVisible();
  await expect(page.locator('#month-jul')).toBeInViewport();
  await expect(page.locator('.ed-reading-room')).toHaveCount(0);
});

for (const path of [
  "/",
  "/timeline/",
  "/timeline/1994/",
  "/timeline/1996/",
  "/zones/games/",
  "/zones/internet-culture/",
  "/tours/before-the-feed/",
  "/search/"
]) {
  test(`axe: ${path}`, async ({ page }) => {
    await page.goto(path);
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
}
