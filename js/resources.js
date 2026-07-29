export function initializeResources() {
  const input = document.querySelector("#resourceSearch");
  const cards = [...document.querySelectorAll("#resourceGrid .resource-card")];
  const buttons = [...document.querySelectorAll("[data-resource-filter]")];
  const count = document.querySelector("#resourceCount");
  const empty = document.querySelector("#resourceNoResults");
  if (!cards.length || !count) return;

  let filter = "all";

  function render() {
    const query = input?.value.trim().toLowerCase() || "";
    let visible = 0;
    cards.forEach((card) => {
      const matchesFilter =
        filter === "all" || card.dataset.category === filter;
      const matchesText = !query || card.textContent.toLowerCase().includes(query);
      const show = matchesFilter && matchesText;
      card.hidden = !show;
      if (show) visible += 1;
    });
    buttons.forEach((button) => {
      const active = button.dataset.resourceFilter === filter;
      button.setAttribute("aria-pressed", String(active));
      button.classList.toggle("active", active);
    });
    count.textContent = `Showing ${visible} external ${visible === 1 ? "destination" : "destinations"}.`;
    if (empty) empty.hidden = visible !== 0;
  }

  input?.addEventListener("input", render);
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      filter = button.dataset.resourceFilter;
      render();
    });
  });
  render();
}
