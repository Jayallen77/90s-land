const VALID_FILTERS = new Set([
  "all",
  "events",
  "stories",
  "highlights",
  "years",
  "zones",
  "objects",
  "tours",
  "community",
  "explore",
]);

const normalize = value => value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

export function initializeSearch() {
  const input = document.querySelector("#siteSearchInput");
  const cards = [...document.querySelectorAll(".site-search-card")];
  const buttons = [...document.querySelectorAll("[data-site-filter]")];
  const count = document.querySelector("#siteSearchCount");
  const empty = document.querySelector("#siteSearchNoResults");
  if (!input || !cards.length || !buttons.length) return;

  // Keep both count surfaces tied to the actual catalog, so new entries cannot
  // make the hero summary and filter badges disagree.
  const totals = cards.reduce((result, card) => {
    const category = card.dataset.searchCategory || "unknown";
    result[category] = (result[category] || 0) + 1;
    return result;
  }, {});
  buttons.forEach((button) => {
    const badge = button.querySelector("span");
    if (badge) badge.textContent = button.dataset.siteFilter === "all"
      ? String(cards.length)
      : String(totals[button.dataset.siteFilter] || 0);
  });
  const summaryIds = {
    years: "#searchSummaryYears",
    zones: "#searchSummaryZones",
    highlights: "#searchSummaryHighlights",
    objects: "#searchSummaryObjects",
  };
  Object.entries(summaryIds).forEach(([category, selector]) => {
    const summary = document.querySelector(selector);
    if (summary) summary.textContent = String(totals[category] || 0);
  });

  let filter = "all";

  function stateFromUrl() {
    const params = new URLSearchParams(window.location.search);
    input.value = params.get("q") || "";
    const requested = params.get("filter") || "all";
    filter = VALID_FILTERS.has(requested) ? requested : "all";
  }

  function updateUrl(mode = "replace") {
    const params = new URLSearchParams();
    if (input.value.trim()) params.set("q", input.value.trim());
    if (filter !== "all") params.set("filter", filter);
    const query = params.toString();
    const url = query ? `?${query}` : window.location.pathname;
    if (mode === "push") window.history.pushState(null, "", url);
    else window.history.replaceState(null, "", url);
  }

  function render({ writeUrl = true, historyMode = "replace" } = {}) {
    const words = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.forEach((card) => {
      const matchesFilter =
        filter === "all" || card.dataset.searchCategory === filter;
      const haystack =
        normalize(`${card.dataset.title} ${card.dataset.tags} ${card.textContent}`);
      const show = matchesFilter && words.every(word => haystack.includes(word));
      card.hidden = !show;
      if (show) visible += 1;
    });
    buttons.forEach((button) => {
      const active = button.dataset.siteFilter === filter;
      button.setAttribute("aria-pressed", String(active));
      button.classList.toggle("active", active);
    });
    count.textContent = `Showing ${visible} ${visible === 1 ? "match" : "matches"}.`;
    empty.hidden = visible !== 0;
    if (writeUrl) updateUrl(historyMode);
  }

  input.addEventListener("input", () => render());
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      filter = button.dataset.siteFilter;
      render({ historyMode: "push" });
    });
  });
  document.querySelector("[data-search-clear]")?.addEventListener("click", () => {
    input.value = "";
    filter = "all";
    render({ historyMode: "push" });
    input.focus();
  });
  window.addEventListener("popstate", () => {
    stateFromUrl();
    render({ writeUrl: false });
  });

  stateFromUrl();
  render({ writeUrl: false });
}
