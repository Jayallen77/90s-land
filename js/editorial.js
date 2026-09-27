// Keep the original rooms and their deep links available behind compact summaries.
function revealHashTarget() {
  if (!location.hash) return;
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = document.getElementById(id);
  if (!target) return;
  let parent = target.parentElement;
  let opened = false;
  while (parent) {
    if (parent instanceof HTMLDetailsElement && !parent.open) {
      parent.open = true;
      opened = true;
    }
    parent = parent.parentElement;
  }
  if (opened) requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
}

export function initializeEditorial() {
  revealHashTarget();
  window.addEventListener('hashchange', revealHashTarget);
  // Clicking an already-current hash also needs to reopen a manually closed room.
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#"]');
    if (anchor && anchor.hash === location.hash) revealHashTarget();
  });
  const grid = document.querySelector('[data-editorial-grid]');
  if (grid) {
    document.querySelectorAll('[data-editorial-view]').forEach(button => {
      button.addEventListener('click', () => {
        grid.dataset.view = button.dataset.editorialView;
        document.querySelectorAll('[data-editorial-view]').forEach(item => {
          item.setAttribute('aria-pressed', String(item === button));
        });
      });
    });
  }
}
