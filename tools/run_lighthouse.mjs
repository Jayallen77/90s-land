#!/usr/bin/env node
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import lighthouse from "lighthouse";
import desktopConfig from "lighthouse/core/config/desktop-config.js";
import * as chromeLauncher from "chrome-launcher";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDirectory = path.join(root, "reports", "lighthouse");
const baseUrl = process.env.LIGHTHOUSE_BASE_URL || "http://127.0.0.1:4173";
const pages = [
  ["home", "/"],
  ["timeline", "/timeline/"],
  ["year-1994", "/timeline/1994/"],
  ["internet-culture", "/zones/internet-culture/"],
  ["tour", "/tours/before-the-feed/"],
  ["search", "/search/?q=mosaic&filter=objects"]
];

await mkdir(outputDirectory, { recursive: true });
const chrome = await chromeLauncher.launch({
  chromeFlags: ["--headless=new", "--no-sandbox", "--disable-gpu"]
});
const summary = [];

try {
  for (const [name, pathname] of pages) {
    for (const mode of ["mobile", "desktop"]) {
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
      const row = { page: name, path: pathname, mode, ...scores };
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
    row.accessibility < 90 ||
    row["best-practices"] < 90 ||
    row.seo < 90 ||
    row.performance < (row.mode === "mobile" ? 85 : 90)
);
if (failures.length) {
  console.error("Lighthouse thresholds missed:", failures);
  process.exitCode = 1;
}
