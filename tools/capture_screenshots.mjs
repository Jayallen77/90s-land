#!/usr/bin/env node
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const output = path.join(root, "reports", "screenshots");
const base = process.env.PREVIEW_BASE_URL || "http://127.0.0.1:4173";
await mkdir(output, { recursive: true });

const browser = await chromium.launch({ headless: true });
try {
  for (const viewport of [
    { width: 390, height: 844 },
    { width: 768, height: 1024 },
    { width: 1280, height: 800 },
    { width: 1440, height: 900 }
  ]) {
    const page = await browser.newPage({
      viewport,
      colorScheme: "dark",
      reducedMotion: "reduce"
    });
    await page.goto(`${base}/`);
    await page.screenshot({
      path: path.join(output, `lobby-${viewport.width}x${viewport.height}.png`)
    });
    await page.close();
  }

  for (const viewport of [
    { label: "mobile", width: 390, height: 844 },
    { label: "desktop", width: 1280, height: 800 }
  ]) {
    const page = await browser.newPage({
      viewport,
      colorScheme: "dark",
      reducedMotion: "reduce"
    });
    await page.goto(`${base}/`);
    await page.getByRole("link", { name: "Surprise me", exact: true }).first().click();
    await page.locator("[data-surprise-ready]").waitFor({ state: "visible" });
    await page.screenshot({
      path: path.join(output, `surprise-${viewport.label}.png`)
    });
    await page.locator('[data-dialog-close="surpriseDialog"]').first().click();
    await page.locator('[data-artifact-inspect="family-pc"]').click();
    if (await page.locator(".menu-toggle").isVisible()) {
      await page.locator(".menu-toggle").click();
    }
    await page.locator("[data-passport-trigger]").click();
    await page.screenshot({
      path: path.join(output, `passport-${viewport.label}.png`)
    });
    await page.close();

    const tour = await browser.newPage({
      viewport,
      colorScheme: "dark",
      reducedMotion: "reduce"
    });
    await tour.goto(`${base}/tours/before-the-feed/#handmade-geocities`);
    await tour.waitForFunction(
      () =>
        [...document.querySelectorAll("[data-tour-stop]")].filter(
          (stop) => !stop.hidden
        ).length === 1
    );
    await tour.locator("#handmade-geocities").evaluate((element) => {
      window.scrollTo({
        top: element.getBoundingClientRect().top + window.scrollY - 76,
        behavior: "instant"
      });
    });
    await tour.screenshot({
      path: path.join(output, `tour-${viewport.label}.png`)
    });
    await tour.close();
  }
} finally {
  await browser.close();
}

console.log(`Saved screenshots to ${output}`);
