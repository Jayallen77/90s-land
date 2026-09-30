import { announce } from "./announce.js";
import { openDialog } from "./navigation.js?v=launch-phase3";
import { awardStamp } from "./passport.js?v=launch-phase3";
import { chooseMemory } from './discovery.js?v=launch-phase3';
import {
  readJson,
  sessionStore,
  SURPRISE_KEY,
  writeJson,
} from "./storage.js";

let artifactsPromise;
let currentArtifact;
let revealNumber = 0;

function loadArtifacts() {
  artifactsPromise ??= fetch("/assets/runtime/surprise.json").then((response) => {
    if (!response.ok) throw new Error("Artifact catalog unavailable");
    return response.json();
  });
  return artifactsPromise;
}

function chooseArtifact(items) {
  const recent = readJson(sessionStore, SURPRISE_KEY, []);
  const chosen = chooseMemory(items, recent);
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
    `${artifact.dateLabel} · ${artifact.room}`;
  dialog.querySelector("[data-surprise-open]").href = artifact.target;
  dialog.querySelector("[data-surprise-loading]").hidden = true;
  dialog.querySelector("[data-surprise-ready]").hidden = false;
  announce(`Random memory loaded: ${artifact.title}.`);
}

async function reveal(dialog) {
  const number = ++revealNumber;
  currentArtifact = undefined;
  dialog.querySelector("[data-surprise-loading]").hidden = false;
  dialog.querySelector("[data-surprise-ready]").hidden = true;
  dialog.querySelector("[data-surprise-error]").hidden = true;
  try {
    const items = await loadArtifacts();
    if (number !== revealNumber) return;
    displayArtifact(dialog, chooseArtifact(items));
  } catch {
    if (number !== revealNumber) return;
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
