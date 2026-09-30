/** One compact paginator for DOM-backed search and resource collections. */
export function createPagination(container, onChange, pageSize = 18) {
  const nav = document.createElement('nav');
  nav.className = 'list-paging ar-js-only';
  nav.setAttribute('aria-label', 'Result pages');
  const previous = document.createElement('button');
  previous.type = 'button'; previous.className = 'button'; previous.textContent = '← Previous';
  const label = document.createElement('span'); label.setAttribute('role','status');
  const next = document.createElement('button');
  next.type = 'button'; next.className = 'button'; next.textContent = 'Next →';
  let current = 1;
  previous.addEventListener('click', () => onChange(current - 1));
  next.addEventListener('click', () => onChange(current + 1));
  nav.append(previous,label,next); container.after(nav);
  return (matches, requested = 1) => {
    const pages = Math.max(1, Math.ceil(matches.length / pageSize));
    current = Math.min(pages, Math.max(1, Math.floor(Number(requested) || 1)));
    matches.forEach((card,index) => { card.hidden = index < (current-1)*pageSize || index >= current*pageSize; });
    nav.hidden = pages <= 1;
    label.textContent = `Page ${current} of ${pages}`;
    previous.disabled = current === 1; next.disabled = current === pages;
    return current;
  };
}
