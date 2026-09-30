#!/usr/bin/env node
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import lighthouse from "lighthouse";
import desktopConfig from "lighthouse/core/config/desktop-config.js";
import * as chromeLauncher from "chrome-launcher";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDirectory = path.resolve(root, process.env.LIGHTHOUSE_OUTPUT || "reports/lighthouse");
const baseUrl = process.env.LIGHTHOUSE_BASE_URL || "http://127.0.0.1:4173";
const catalog = [
  ["home", "/"],
  ["timeline", "/timeline/"],
  ["year-1996", "/timeline/1996/?month=06"],
  ["games", "/zones/games/"],
  ["music", "/zones/music/"],
  ["movies", "/zones/tv-movies/"],
  ["tech", "/zones/tech-toys/"],
  ["culture", "/zones/culture/"],
  ["week", "/this-week/?date=1996-09-27"],
  ["story", "/stories/the-console-war-couch/"],
  ["object", "/archive/objects/n64-controller/"],
  ["year-1994", "/timeline/1994/"],
  ["internet-culture", "/zones/internet-culture/"],
  ["tour", "/tours/before-the-feed/"],
  ["search", "/search/?q=mosaic&filter=objects"]
];
const requested = process.env.LIGHTHOUSE_PAGES?.split(",");
if (requested?.some(name => !catalog.some(([key]) => key === name))) throw new Error("Unknown LIGHTHOUSE_PAGES entry");
const pages = requested ? catalog.filter(([key]) => requested.includes(key)) : catalog;
const modes = process.env.LIGHTHOUSE_MODES?.split(",") || ["mobile", "desktop"];
if (modes.some(mode => !["mobile", "desktop"].includes(mode))) throw new Error("Unknown LIGHTHOUSE_MODES entry");

await mkdir(outputDirectory, { recursive: true });
const chrome = await chromeLauncher.launch({
  chromeFlags: ["--headless=new", "--no-sandbox", "--disable-gpu"]
});
const summary = [];

try {
  for (const [name, pathname] of pages) {
    for (const mode of modes) {
      const desktop = mode === "desktop";
      const result = await lighthouse(`${baseUrl}${pathname}`, {
        port: chrome.port,
        output: "json",
        logLevel: "error",
        onlyCategories: [
          "performance",
          "accessibility",
          "best-practices",
          "seo"
        ]
      }, desktop ? desktopConfig : undefined);
      const scores = Object.fromEntries(
        Object.entries(result.lhr.categories).map(([key, category]) => [
          key,
          Math.round(category.score * 100)
        ])
      );
      const metrics = Object.fromEntries(["first-contentful-paint", "largest-contentful-paint", "total-blocking-time", "cumulative-layout-shift", "speed-index", "total-byte-weight"].map(key => [key, result.lhr.audits[key]?.numericValue ?? null]));
      // Search results deliberately use noindex. Preserve Lighthouse's raw score
      // while checking that policy and every other applicable SEO audit.
      const indexingExpected = name !== "search";
      const seoChecksPass = result.lhr.categories.seo.auditRefs.every(({id}) => {
        const audit = result.lhr.audits[id];
        if (id === "is-crawlable" && !indexingExpected) {
          return audit.score === 0 && audit.details?.items?.some(item => item.source?.snippet?.includes('noindex,follow'));
        }
        return audit.score === null || audit.score === 1;
      });
      const row = { page: name, path: pathname, mode, ...scores, metrics,
        indexingExpected, seoChecksPass,
        lighthouseVersion: result.lhr.lighthouseVersion, fetchedAt: result.lhr.fetchTime,
        warnings: result.lhr.runWarnings, error: result.lhr.runtimeError || null };
      summary.push(row);
      await writeFile(
        path.join(outputDirectory, `${name}-${mode}.json`),
        JSON.stringify(result.lhr, null, 2)
      );
      console.log(row);
    }
  }
} finally {
  await chrome.kill();
}

await writeFile(
  path.join(outputDirectory, "summary.json"),
  JSON.stringify(summary, null, 2) + "\n"
);

const failures = summary.filter(
  (row) =>
    row.error ||
    row.accessibility < 90 ||
    row["best-practices"] < 90 ||
    !row.seoChecksPass ||
    row.metrics["cumulative-layout-shift"] > 0.1 ||
    row.performance < (row.mode === "mobile" ? 85 : 90)
);
if (failures.length) {
  console.error("Lighthouse thresholds missed:", failures);
  process.exitCode = 1;
}
