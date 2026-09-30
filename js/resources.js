import { createPagination } from './pagination.js';
export function initializeResources() {
  const input = document.querySelector('#resourceSearch');
  const grid = document.querySelector('#resourceGrid');
  const cards = [...grid.querySelectorAll('.resource-card')];
  const buttons = [...document.querySelectorAll('[data-resource-filter]')];
  const count = document.querySelector('#resourceCount');
  const empty = document.querySelector('#resourceNoResults');
  const allowed = new Set(buttons.map(button => button.dataset.resourceFilter));
  let filter = 'all', page = 1;
  const paginate = createPagination(grid, next => {page=next;render(true);grid.scrollIntoView({block:'start'});});
  function read() {
    const params = new URL(location.href).searchParams;
    input.value = params.get('q') || '';
    filter = allowed.has(params.get('filter')) ? params.get('filter') : 'all';
    page = Number(params.get('page')) || 1;
  }
  function render(push = false, write = true) {
    const query = input.value.trim().toLowerCase();
    cards.forEach(card => {card.hidden = !((filter==='all'||card.dataset.category===filter)&&(!query||card.textContent.toLowerCase().includes(query)));});
    const matches = cards.filter(card=>!card.hidden);
    page = paginate(matches,page);
    buttons.forEach(button => button.setAttribute('aria-pressed',String(button.dataset.resourceFilter===filter)));
    count.textContent = `${matches.length} external ${matches.length===1?'destination':'destinations'}`;
    empty.hidden = matches.length !== 0;
    if (write) {
      const url = new URL(location.href); url.search = '';
      if (query) url.searchParams.set('q',input.value.trim());
      if (filter!=='all') url.searchParams.set('filter',filter);
      if (page>1) url.searchParams.set('page',page);
      history[push?'pushState':'replaceState']({},'',url);
    }
  }
  input.addEventListener('input',()=>{page=1;render();});
  buttons.forEach(button=>button.addEventListener('click',()=>{filter=button.dataset.resourceFilter;page=1;render(true);}));
  addEventListener('popstate',()=>{read();render(false,false);});
  read(); render(false,false);
}
