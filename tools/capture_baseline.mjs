#!/usr/bin/env node
// Capture only the unchanged Phase 1 site. Never refresh the frozen baseline.
import { createHash } from "node:crypto";
import { createServer } from "node:http";
import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const directory = path.join(root, "reports/baseline/phase-1");
const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");
const manifest = JSON.parse(await readFile(path.join(directory, "manifest.json"), "utf8"));
const exists = async (file) => Boolean(await stat(file).catch(() => null));
const evidencePath = path.join(directory, "screenshots.json");

if (process.argv.includes("--check")) {
  const evidence = JSON.parse(await readFile(evidencePath, "utf8"));
  if (evidence.revision !== manifest.revision || evidence.captures.length !== 6) {
    throw new Error("Visual baseline revision/capture set differs");
  }
  for (const capture of evidence.captures) {
    if (sha(await readFile(path.join(root, capture.file))) !== capture.sha256) {
      throw new Error(`Visual baseline changed: ${capture.file}`);
    }
  }
  console.log("Visual baseline: six frozen captures verified");
  process.exit(0);
}
if (await exists(evidencePath)) {
  throw new Error("Visual baseline already exists. Refusing to overwrite it.");
}
for (const [file, expected] of Object.entries(manifest.servedFileHashes)) {
  if (sha(await readFile(path.join(root, file))) !== expected) {
    throw new Error(`Cannot capture a changed public baseline: ${file}`);
  }
}
const mime = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".webp": "image/webp", ".avif": "image/avif", ".jpg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".svg": "image/svg+xml", ".woff2": "font/woff2" };
const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
    let file = path.resolve(root, `.${pathname}`);
    if (file !== root && !file.startsWith(root + path.sep)) {
      response.writeHead(403).end();
      return;
    }
    if ((await stat(file)).isDirectory()) file = path.join(file, "index.html");
    response.writeHead(200, { "Content-Type": mime[path.extname(file)] || "application/octet-stream" });
    response.end(await readFile(file));
  } catch {
    response.writeHead(404).end();
  }
});
await new Promise((resolve, reject) => {
  server.once("error", reject);
  server.listen(0, "127.0.0.1", resolve);
});
let browser;
try {
  browser = await chromium.launch({ headless: true });
  const captures = [];
  await mkdir(path.join(directory, "screenshots"), { recursive: true });
  for (const [name, route, width, height] of [
    ["home", "/", 1086, 724],
    ["timeline", "/timeline/1996/", 1086, 724],
    ["games", "/zones/games/", 1182, 665],
    ["home", "/", 390, 844],
    ["timeline", "/timeline/1996/", 390, 844],
    ["games", "/zones/games/", 390, 844],
  ]) {
    const file = `reports/baseline/phase-1/screenshots/${name}-${width}x${height}.png`;
    if (await exists(path.join(root, file))) throw new Error(`Refusing to overwrite ${file}`);
    const page = await browser.newPage({ viewport: { width, height }, reducedMotion: "reduce", colorScheme: "dark" });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(`http://127.0.0.1:${server.address().port}${route}`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    const layout = await page.evaluate(() => ({
      documentHeight: document.documentElement.scrollHeight,
      documentWidth: document.documentElement.scrollWidth,
      heading: document.querySelector("h1")?.textContent.trim(),
      mainTop: document.querySelector("main").getBoundingClientRect().top,
    }));
    if (errors.length || layout.documentWidth > width) throw new Error(`Invalid baseline capture ${name}: ${errors.join(", ")}`);
    const bytes = await page.screenshot({ path: path.join(root, file), animations: "disabled" });
    captures.push({ name, route, viewport: { width, height }, file, sha256: sha(bytes), layout });
    await page.close();
  }
  await writeFile(evidencePath, JSON.stringify({ schemaVersion: 1, revision: manifest.revision, capturedAt: new Date().toISOString(), browser: browser.version(), reducedMotion: true, captures }, null, 2) + "\n");
  console.log(`Captured ${captures.length} desktop/mobile baselines without changing the public site`);
} finally {
  await browser?.close();
  await new Promise((resolve) => server.close(resolve));
}
