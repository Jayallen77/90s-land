// Keep bookmarked section anchors stable after fonts and filters settle.
export function initializeEditorial() {
  const reveal = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;
    const hash = location.hash;
    document.fonts.ready.then(() => requestAnimationFrame(() => {
      if (location.hash === hash) target.scrollIntoView({block:'start',behavior:'instant'});
    }));
  };
  reveal();
  addEventListener('hashchange', reveal);
}
