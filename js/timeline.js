const monthKeys = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];

export function initializeTimelineViews() {
  document.querySelectorAll(".month-timeline").forEach((section) => {
    const grid = section.querySelector(".capsule-month-grid");
    const controls = section.querySelector(".timeline-controls");
    if (!grid || !controls) return;

    const cards = [...grid.querySelectorAll(".month-card")];
    cards.forEach((card, index) => {
      if (!card.id && monthKeys[index]) card.id = `month-${monthKeys[index]}`;
    });
    grid.dataset.view = "grid";

    const buttons = [...controls.querySelectorAll("[data-month-view]")];
    const status = controls.querySelector("[data-month-view-status]");
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const view = button.dataset.monthView;
        if (!["grid", "list", "calendar"].includes(view)) return;
        grid.dataset.view = view;
        buttons.forEach((option) => {
          option.setAttribute("aria-pressed", String(option === button));
        });
        if (status) status.textContent = `${view[0].toUpperCase()}${view.slice(1)} view`;
      });
    });

    const year = Number(location.pathname.match(/\/timeline\/(\d{4})\//)?.[1]);
    if (year !== new Date().getFullYear() - 30) return;
    const currentMonth = monthKeys[new Date().getMonth()];
    controls.querySelector(`[href="#month-${currentMonth}"]`)?.setAttribute("aria-current", "date");
  });
}
