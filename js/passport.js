import { announce } from "./announce.js";
import { closeDialog, openDialog } from "./navigation.js";
import {
  localStore,
  PASSPORT_KEY,
  readJson,
  writeJson,
} from "./storage.js";

const VERSION = 1;
const TRACKABLE_ROOMS = new Set([
  "fashion",
  "games",
  "internet-culture",
  "music",
  "tech-toys",
  "transparent-tech",
  "tv-movies",
]);

function emptyPassport() {
  return {
    version: VERSION,
    visitedRooms: [],
    inspectedArtifacts: [],
    stamps: [],
    tourProgress: {},
  };
}

function normalize(candidate) {
  if (!candidate || candidate.version !== VERSION) return emptyPassport();
  return {
    version: VERSION,
    visitedRooms: Array.isArray(candidate.visitedRooms)
      ? [...new Set(candidate.visitedRooms)]
      : [],
    inspectedArtifacts: Array.isArray(candidate.inspectedArtifacts)
      ? [...new Set(candidate.inspectedArtifacts)]
      : [],
    stamps: Array.isArray(candidate.stamps) ? [...new Set(candidate.stamps)] : [],
    tourProgress:
      candidate.tourProgress && typeof candidate.tourProgress === "object"
        ? candidate.tourProgress
        : {},
  };
}

let state = normalize(readJson(localStore, PASSPORT_KEY, emptyPassport()));

function persist() {
  if (!writeJson(localStore, PASSPORT_KEY, state)) {
    announce("Passport progress will last only until this page is closed.");
  }
  render();
  window.dispatchEvent(
    new CustomEvent("passport:changed", { detail: structuredClone(state) }),
  );
}

function earn(stampId, message) {
  if (state.stamps.includes(stampId)) return false;
  state.stamps.push(stampId);
  if (message) announce(message);
  return true;
}

function applyMilestones() {
  if (state.inspectedArtifacts.length >= 1) {
    earn("first-touch", "Passport stamp earned: Object Handler.");
  }
  if (state.visitedRooms.length >= 3) {
    earn("room-hopper", "Passport stamp earned: Room Hopper.");
  }
  if (state.inspectedArtifacts.length >= 5) {
    earn("object-collector", "Passport stamp earned: Pocket Curator.");
  }
}

function render() {
  document.querySelectorAll("[data-passport-count]").forEach((node) => {
    node.textContent = String(state.stamps.length);
  });
  document.querySelectorAll("[data-passport-rooms]").forEach((node) => {
    node.textContent = String(state.visitedRooms.length);
  });
  document.querySelectorAll("[data-passport-artifacts]").forEach((node) => {
    node.textContent = String(state.inspectedArtifacts.length);
  });
  document.querySelectorAll("[data-passport-stamps]").forEach((node) => {
    node.textContent = String(state.stamps.length);
  });
  document.querySelectorAll("[data-passport-stamp]").forEach((node) => {
    const earned = state.stamps.includes(node.dataset.passportStamp);
    node.classList.toggle("is-locked", !earned);
    node.classList.toggle("is-earned", earned);
  });
  document.querySelectorAll("[data-timeline-room]").forEach((door) => {
    const visited = state.visitedRooms.includes(door.dataset.timelineRoom);
    door.classList.toggle("is-visited", visited);
    const label = door.querySelector("[data-visited-door-label]");
    if (label) label.textContent = visited ? "Visited ✓" : "Not visited";
  });
  document.querySelectorAll("[data-artifact-inspect]").forEach((button) => {
    const inspected = state.inspectedArtifacts.includes(
      button.dataset.artifactInspect,
    );
    button.classList.toggle("is-inspected", inspected);
    button.textContent = inspected ? "Inspected ✓" : "Inspect + stamp";
  });

  const progress = state.tourProgress["before-the-feed"];
  document.querySelectorAll("[data-tour-resume]").forEach((panel) => {
    const resumable = progress && !progress.completed && progress.stopId;
    panel.hidden = !resumable;
    if (!resumable) return;
    panel.querySelector("[data-tour-resume-label]").textContent =
      `stop ${progress.stopNumber} of 6`;
    panel.querySelector("[data-tour-resume-link]").href =
      `/tours/before-the-feed/#${progress.stopId}`;
  });
}

export function getPassport() {
  return structuredClone(state);
}

export function recordArtifact(artifactId) {
  if (!artifactId || state.inspectedArtifacts.includes(artifactId)) return;
  state.inspectedArtifacts.push(artifactId);
  applyMilestones();
  persist();
  announce(`Object inspected. ${state.inspectedArtifacts.length} in your passport.`);
}

export function awardStamp(stampId, message) {
  if (earn(stampId, message)) persist();
}

export function saveTourProgress(tourId, progress) {
  state.tourProgress[tourId] = { ...progress };
  persist();
}

function recordCurrentRoom() {
  const room = document.body.dataset.room;
  const trackable = TRACKABLE_ROOMS.has(room) || room.startsWith("timeline-");
  if (!trackable || state.visitedRooms.includes(room)) return;
  state.visitedRooms.push(room);
  applyMilestones();
  persist();
}

function resetPassport() {
  state = emptyPassport();
  localStore.remove(PASSPORT_KEY);
  persist();
  announce("Museum Passport reset.");
}

export function initializePassport() {
  const trigger = document.querySelector("[data-passport-trigger]");
  const dialog = document.querySelector("#passportDialog");
  const resetDialog = document.querySelector("#passportResetDialog");
  if (!trigger || !dialog || !resetDialog) return;

  trigger.hidden = false;
  document.querySelectorAll("[data-storage-note]").forEach((note) => {
    if (!localStore.persistent) {
      note.textContent =
        "Browser storage is unavailable. Progress will not persist after this page closes.";
      note.classList.add("is-warning");
    }
  });

  trigger.addEventListener("click", () => openDialog(dialog, trigger));
  document.addEventListener("click", (event) => {
    const inspect = event.target.closest("[data-artifact-inspect]");
    if (inspect) recordArtifact(inspect.dataset.artifactInspect);

    if (event.target.closest("[data-passport-reset-open]")) {
      closeDialog(dialog);
      openDialog(resetDialog, trigger);
    }
    if (event.target.closest("[data-passport-reset-cancel]")) {
      closeDialog(resetDialog);
      openDialog(dialog, trigger);
    }
    if (event.target.closest("[data-passport-reset-confirm]")) {
      resetPassport();
      closeDialog(resetDialog);
      openDialog(dialog, trigger);
    }
  });

  recordCurrentRoom();
  render();
}
