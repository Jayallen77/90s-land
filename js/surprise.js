import { announce } from "./announce.js";
import { openDialog } from "./navigation.js?v=launch-phase1";
import { awardStamp } from "./passport.js?v=launch-phase1";
import {
  readJson,
  sessionStore,
  SURPRISE_KEY,
  writeJson,
} from "./storage.js";

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
let artifactsPromise;
let currentArtifact;

function loadArtifacts() {
  artifactsPromise ??= fetch("/assets/runtime/surprise.json").then((response) => {
    if (!response.ok) throw new Error("Artifact catalog unavailable");
    return response.json();
  });
  return artifactsPromise;
}

function chooseArtifact(items) {
  const recent = readJson(sessionStore, SURPRISE_KEY, []);
  const eligible = items.filter((item) => !recent.includes(item.id));
  const pool = eligible.length ? eligible : items;
  const chosen = pool[Math.floor(Math.random() * pool.length)];
  const nextRecent = [chosen.id, ...recent.filter((id) => id !== chosen.id)].slice(
    0,
    3,
  );
  writeJson(sessionStore, SURPRISE_KEY, nextRecent);
  return chosen;
}

function displayArtifact(dialog, artifact) {
  currentArtifact = artifact;
  dialog.querySelector("[data-surprise-title]").textContent = artifact.title;
  dialog.querySelector("[data-surprise-teaser]").textContent =
    artifact.teaser;
  dialog.querySelector("[data-surprise-meta]").textContent =
    `${artifact.dateLabel} · ${artifact.room.replaceAll("-", " ")}`;
  dialog.querySelector("[data-surprise-open]").href = artifact.target;
  dialog.querySelector("[data-surprise-loading]").hidden = true;
  dialog.querySelector("[data-surprise-ready]").hidden = false;
  announce(`Random memory loaded: ${artifact.title}.`);
}

async function reveal(dialog) {
  currentArtifact = undefined;
  dialog.querySelector("[data-surprise-loading]").hidden = false;
  dialog.querySelector("[data-surprise-ready]").hidden = true;
  dialog.querySelector("[data-surprise-error]").hidden = true;
  try {
    const [items] = await Promise.all([
      loadArtifacts(),
      reducedMotion.matches
        ? Promise.resolve()
        : new Promise((resolve) => window.setTimeout(resolve, 650)),
    ]);
    displayArtifact(dialog, chooseArtifact(items));
  } catch {
    artifactsPromise = undefined;
    dialog.querySelector("[data-surprise-loading]").hidden = true;
    dialog.querySelector("[data-surprise-error]").hidden = false;
  }
}

export function initializeSurprise() {
  const dialog = document.querySelector("#surpriseDialog");
  if (!dialog) return;

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest(
      "[data-surprise-trigger], [data-surprise-trigger-button]",
    );
    if (trigger) {
      event.preventDefault();
      openDialog(dialog, trigger);
      reveal(dialog);
      return;
    }
    if (event.target.closest("[data-surprise-again], [data-surprise-retry]")) reveal(dialog);
    if (event.target.closest("[data-surprise-open]") && currentArtifact) {
      awardStamp(
        "random-memory",
        "Passport stamp earned: Random Access Memory.",
      );
    }
  });
}
