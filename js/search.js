const VALID_FILTERS = new Set([
  "all",
  "highlights",
  "years",
  "zones",
  "objects",
  "tours",
  "community",
  "explore",
]);

export function initializeSearch() {
  const input = document.querySelector("#siteSearchInput");
  const cards = [...document.querySelectorAll(".site-search-card")];
  const buttons = [...document.querySelectorAll("[data-site-filter]")];
  const count = document.querySelector("#siteSearchCount");
  const empty = document.querySelector("#siteSearchNoResults");
  if (!input || !cards.length || !buttons.length) return;

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
    const query = input.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach((card) => {
      const matchesFilter =
        filter === "all" || card.dataset.searchCategory === filter;
      const haystack =
        `${card.dataset.title} ${card.dataset.tags} ${card.textContent}`.toLowerCase();
      const show = matchesFilter && (!query || haystack.includes(query));
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
