import { createPagination } from './pagination.js';
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

const normalize = value => value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim();

export function initializeSearch() {
  const input = document.querySelector("#siteSearchInput");
  const cards = [...document.querySelectorAll(".site-search-card")];
  const buttons = [...document.querySelectorAll("[data-site-filter]")];
  const count = document.querySelector("#siteSearchCount");
  const empty = document.querySelector("#siteSearchNoResults");
  if (!input || !cards.length || !buttons.length) return;
  const indexed = cards.map((card,index) => ({card,index,title:normalize(card.dataset.title),text:normalize(`${card.dataset.title} ${card.dataset.tags} ${card.textContent}`)}));

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

  let filter = "all", page = 1;
  const paginate = createPagination(document.querySelector('#siteSearchGrid'), next => {
    page = next; render({historyMode:'push'});
    document.querySelector('#siteSearchGrid').scrollIntoView({block:'start'});
  });

  function stateFromUrl() {
    const params = new URLSearchParams(window.location.search);
    input.value = params.get("q") || "";
    page = Number(params.get("page")) || 1;
    const requested = params.get("filter") || "all";
    filter = VALID_FILTERS.has(requested) ? requested : "all";
  }

  function updateUrl(mode = "replace") {
    const params = new URLSearchParams();
    if (input.value.trim()) params.set("q", input.value.trim());
    if (filter !== "all") params.set("filter", filter);
    if (page > 1) params.set("page",page);
    const query = params.toString();
    const url = query ? `?${query}` : window.location.pathname;
    if (mode === "push") window.history.pushState(null, "", url);
    else window.history.replaceState(null, "", url);
  }

  function render({ writeUrl = true, historyMode = "replace" } = {}) {
    const words = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    const queryMatches=indexed.filter(item => words.every(word => item.text.includes(word)));
    const queryTotals=queryMatches.reduce((result,{card})=>{const key=card.dataset.searchCategory;result[key]=(result[key]||0)+1;return result;},{});
    const query=words.join(' ');
    const rank=item=>!query ? 0 : item.title===query ? 3 : words.every(word=>item.title.includes(word)) ? 2 : 1;
    const matches=queryMatches.filter(({card})=>filter==='all'||card.dataset.searchCategory===filter).sort((a,b)=>rank(b)-rank(a)||a.index-b.index);
    const visible=matches.length;
    cards.forEach(card=>{card.hidden=true;});
    // Reuse the existing cards; relevance order and pagination share one list.
    const container=document.querySelector('#siteSearchGrid');
    matches.forEach(({card})=>{card.hidden=false;container.append(card);});
    buttons.forEach((button) => {
      const active = button.dataset.siteFilter === filter;
      button.setAttribute("aria-pressed", String(active));
      button.classList.toggle("active", active);
      button.querySelector('span').textContent=String(button.dataset.siteFilter==='all'?queryMatches.length:queryTotals[button.dataset.siteFilter]||0);
    });
    page = paginate(matches.map(item=>item.card), page);
    count.textContent = `Showing ${visible} ${visible === 1 ? "match" : "matches"}.`;
    empty.hidden = visible !== 0;
    if (writeUrl) updateUrl(historyMode);
  }

  input.addEventListener("input", () => {page=1;render();});
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      filter = button.dataset.siteFilter;
      page = 1;
      render({ historyMode: "push" });
    });
  });
  document.querySelector("[data-search-clear]")?.addEventListener("click", () => {
    input.value = "";
    filter = "all";
    page = 1;
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
