// Keep the original rooms and their deep links available behind compact summaries.
function revealHashTarget() {
  if (!location.hash) return;
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = document.getElementById(id);
  if (!target) return;
  let parent = target.parentElement;
  let inReadingRoom = false;
  while (parent) {
    if (parent instanceof HTMLDetailsElement) {
      inReadingRoom = true;
      parent.open = true;
    }
    parent = parent.parentElement;
  }
  if (!inReadingRoom) return;
  const hash = location.hash;
  const scroll = () => {
    if (location.hash === hash && target.closest('details')?.open) target.scrollIntoView({ block:'start', behavior:'instant' });
  };
  requestAnimationFrame(scroll);
  // Opening a closed room can start additional font loads. Re-anchor after those
  // metrics settle so a long reading room cannot carry the target off screen.
  requestAnimationFrame(() => document.fonts.ready.then(() => requestAnimationFrame(scroll)));
}

export function initializeEditorial() {
  revealHashTarget();
  window.addEventListener('hashchange', revealHashTarget);
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#"]');
    if (anchor && anchor.hash === location.hash) revealHashTarget();
  });
}
