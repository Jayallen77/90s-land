import { announce } from "./announce.js";
import { awardStamp, getPassport, saveTourProgress } from "./passport.js";

const TOUR_ID = "before-the-feed";

export function initializeTour() {
  const main = document.querySelector(`[data-tour-id="${TOUR_ID}"]`);
  if (!main) return;

  const stops = [...main.querySelectorAll("[data-tour-stop]")];
  const progressBar = main.querySelector("[data-tour-progress-bar]");
  const progressMeter = progressBar.closest('[role="progressbar"]');
  const progressCopy = main.querySelector("[data-tour-progress-copy]");
  let activeIndex = 0;

  function validIndexFromHash() {
    const id = decodeURIComponent(window.location.hash.slice(1));
    return stops.findIndex((stop) => stop.id === id);
  }

  function render(index, options = {}) {
    activeIndex = Math.max(0, Math.min(index, stops.length - 1));
    stops.forEach((stop, stopIndex) => {
      stop.hidden = stopIndex !== activeIndex;
      stop.classList.toggle("is-current", stopIndex === activeIndex);
    });
    const current = stops[activeIndex];
    const number = activeIndex + 1;
    progressBar.style.width = `${(number / stops.length) * 100}%`;
    progressMeter.setAttribute("aria-valuenow", String(number));
    progressCopy.textContent = `Stop ${number} of ${stops.length}: ${current.querySelector("h2").textContent}`;
    saveTourProgress(TOUR_ID, {
      stopId: current.id,
      stopNumber: number,
      completed: false,
    });
    if (options.updateHash !== false) {
      window.history.pushState(null, "", `#${current.id}`);
    }
    if (options.focus) {
      const heading = current.querySelector("h2");
      heading.tabIndex = -1;
      heading.focus({ preventScroll: true });
    }
    current.scrollIntoView({
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "auto"
        : "smooth",
      block: "start",
    });
  }

  function complete() {
    const last = stops.at(-1);
    last.hidden = false;
    last.classList.add("is-complete");
    progressBar.style.width = "100%";
    progressMeter.setAttribute("aria-valuenow", String(stops.length));
    progressCopy.textContent =
      "Tour complete. Your Before the Feed stamp is ready.";
    saveTourProgress(TOUR_ID, {
      stopId: last.id,
      stopNumber: stops.length,
      completed: true,
    });
    awardStamp(
      "before-the-feed",
      "Passport stamp earned: Before the Feed.",
    );
    const next = last.querySelector("[data-tour-next]");
    next.disabled = true;
    next.textContent = "Tour complete ✓";
    announce("Before the Feed tour complete. You can keep exploring.");
  }

  main.addEventListener("click", (event) => {
    if (event.target.closest("[data-tour-back]")) {
      render(activeIndex - 1, { focus: true });
    }
    if (event.target.closest("[data-tour-next]")) {
      if (activeIndex === stops.length - 1) complete();
      else render(activeIndex + 1, { focus: true });
    }
  });

  window.addEventListener("popstate", () => {
    const hashIndex = validIndexFromHash();
    if (hashIndex >= 0) render(hashIndex, { updateHash: false });
  });

  const hashIndex = validIndexFromHash();
  const saved = getPassport().tourProgress[TOUR_ID];
  const savedIndex = saved?.stopId
    ? stops.findIndex((stop) => stop.id === saved.stopId)
    : -1;
  render(hashIndex >= 0 ? hashIndex : Math.max(savedIndex, 0), {
    updateHash: false,
  });
}

export function initializeHomepageBuilder() {
  document.querySelectorAll("[data-homepage-builder]").forEach((builder) => {
    const preview = builder.querySelector("[data-homepage-preview]");
    builder.addEventListener("click", (event) => {
      const toggle = event.target.closest("[data-homepage-toggle]");
      if (toggle) {
        const layer = toggle.dataset.homepageToggle;
        const pressed = toggle.getAttribute("aria-pressed") !== "true";
        toggle.setAttribute("aria-pressed", String(pressed));
        if (layer === "stars") preview.classList.toggle("has-stars", pressed);
        else {
          const target = preview.querySelector(`[data-builder-layer="${layer}"]`);
          if (target) target.hidden = !pressed;
        }
        announce(`${toggle.textContent}: ${pressed ? "on" : "off"}.`);
      }
      if (event.target.closest("[data-homepage-reset]")) {
        preview.classList.remove("has-stars");
        builder.querySelectorAll("[data-homepage-toggle]").forEach((button) => {
          button.setAttribute("aria-pressed", "false");
        });
        preview.querySelectorAll("[data-builder-layer]").forEach((layer) => {
          layer.hidden = true;
        });
        announce("Homepage recreation reset.");
      }
    });
  });
}
