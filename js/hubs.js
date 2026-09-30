import { createPagination } from './pagination.js';
/** DOM-backed collection filters. Full content remains available without JS. */
export function initializeHubs() {
  const root = document.querySelector('[data-hub]');
  if (!root) return;
  const eventGrid = root.querySelector('[data-event-library]');
  const paginate = eventGrid ? createPagination(eventGrid, page => {
    const next = new URL(location.href); next.searchParams.set('page', page);
    history.pushState({},'',next); render(); eventGrid.scrollIntoView({block:'start'});
  }) : null;
  const allowed = key => new Set(['all', ...Array.from(document.querySelectorAll(`[data-hub-filter="${key}"]`), a => a.dataset.value)]);
  const read = key => { const value = new URL(location.href).searchParams.get(key) || 'all'; return allowed(key).has(value) ? value : 'all'; };
  const render = () => {
    const values = Object.fromEntries(['topic','genre','platform','category'].map(key => [key, read(key)]));
    document.querySelectorAll('[data-hub-filter]').forEach(a => {
      a.setAttribute('aria-current', String(a.dataset.value === values[a.dataset.hubFilter]));
    });
    const filter = (selector, type, matches) => {
      const cards = [...root.querySelectorAll(selector)];
      if (!cards.length) return;
      cards.forEach(card => { card.hidden = !matches(card); });
      const visible = cards.filter(card => !card.hidden);
      const count = visible.length;
      if (type === 'events' && paginate) paginate(visible,new URL(location.href).searchParams.get('page'));
      const status = root.querySelector(`[data-hub-status="${type}"]`);
      if (status) status.textContent = `${count} of ${cards.length} ${type}`;
      const empty = root.querySelector(`[data-hub-empty="${type}"]`);
      if (empty) empty.hidden = count !== 0;
    };
    filter('[data-hub-story]', 'stories', card => (values.topic === 'all' || card.dataset.topics.split(' ').includes(values.topic)) && (values.category === 'all' || card.dataset.category === values.category));
    filter('[data-hub-event]', 'events', card => values.category === 'all' || card.dataset.category === values.category);
    filter('[data-hub-game]', 'games', card => (values.genre === 'all' || card.dataset.genre === values.genre) && (values.platform === 'all' || card.dataset.platform === values.platform));
  };
  document.querySelectorAll('[data-hub-filter], a[href*="?platform="]').forEach(a => {
    a.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
      event.preventDefault();
      const target = new URL(a.href), next = new URL(location.href);
      target.searchParams.forEach((value,key) => { if (value === 'all') next.searchParams.delete(key); else next.searchParams.set(key,value); });
      next.searchParams.delete('page');
      next.hash = target.hash;
      history.pushState({}, '', next);
      render();
      document.getElementById(next.hash.slice(1))?.scrollIntoView({block:'start'});
    });
  });
  addEventListener('popstate', render);
  render();
}
