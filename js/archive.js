import { MIN_DATE, MAX_DATE, inDecade, clampDecade, shiftDays, changeYear, historicalDate, weekBounds, eventsInWeek, formatDate, parseDate } from './date-utils.js';

const CATEGORIES = {music:'Music', 'movies-tv':'Movies & TV', games:'Games', tech:'Tech', culture:'Culture', news:'World news'};
const PAGE_SIZE = 12;

export function initializeArchiveTimeline() {
  const root = document.querySelector('[data-timeline]');
  if (!root) return;
  const year = Number(root.dataset.year);
  const panels = [...root.querySelectorAll('[data-month-panel]')];
  const category = root.querySelector('[data-category-filter]');
  const region = root.querySelector('[data-region-filter]');
  const rail = [...document.querySelectorAll('[data-month]')];
  let state;
  const validOption = (select, value) => [...select.options].some(o => o.value === value) ? value : 'all';
  function read() {
    const params = new URLSearchParams(location.search);
    let month = Number(params.get('month'));
    const oldMonth = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'].indexOf(location.hash.replace('#month-',''));
    if (!month && oldMonth >= 0) month = oldMonth + 1;
    const anchor = location.hash.match(/^#events-\d{4}-(\d{2})$/);
    if (!month && anchor) month = Number(anchor[1]);
    if (!Number.isInteger(month) || month < 1 || month > 12) month = Number(historicalDate().slice(5,7));
    const view = ['grid','list','calendar'].includes(params.get('view')) ? params.get('view') : 'grid';
    state = {month, view, category:validOption(category, params.get('category')), region:validOption(region, params.get('region')), page:Math.max(1, Number(params.get('page')) || 1)};
  }
  function url(next = state, targetYear = year) {
    const params = new URLSearchParams({month:String(next.month).padStart(2,'0')});
    if (next.view !== 'grid') params.set('view', next.view);
    if (next.category !== 'all') params.set('category', next.category);
    if (next.region !== 'all') params.set('region', next.region);
    if (next.page > 1) params.set('page', next.page);
    return `/timeline/${targetYear}/?${params}#events-${targetYear}-${String(next.month).padStart(2,'0')}`;
  }
  function render(write = false) {
    root.dataset.ready = 'true';
    root.dataset.view = state.view;
    category.value = state.category; region.value = state.region;
    root.querySelectorAll('[data-archive-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.archiveView===state.view)));
    let total = 0, pages = 1;
    const matches = element => (state.category==='all' || element.dataset.category===state.category) && (state.region==='all' || element.dataset.region===state.region);
    panels.forEach(panel => {
      const active = Number(panel.dataset.monthPanel) === state.month;
      panel.hidden = !active;
      if (!active) return;
      const cards = [...panel.querySelectorAll('.ar-event')];
      const filtered = cards.filter(matches);
      total = filtered.length; pages = Math.max(1, Math.ceil(total/PAGE_SIZE));
      state.page = Math.min(pages, Math.floor(state.page));
      const pageItems = filtered.slice((state.page-1)*PAGE_SIZE, state.page*PAGE_SIZE);
      cards.forEach(card => { card.hidden = !(state.view === 'calendar' ? filtered : pageItems).includes(card); });
      panel.querySelectorAll('.ar-calendar [data-event]').forEach(link => { link.hidden = !matches(link); });
      panel.querySelector('[data-month-empty]').hidden = total > 0;
    });
    rail.forEach(link => {
      const month = Number(link.dataset.month);
      link.href = url({...state, month, page:1});
      if (month===state.month) link.setAttribute('aria-current','date'); else link.removeAttribute('aria-current');
    });
    for (const [selector, step] of [['[data-prev-month]',-1],['[data-next-month]',1]]) {
      const link = root.querySelector(selector);
      const shifted = new Date(Date.UTC(year, state.month-1+step, 1));
      const valid = shifted.getUTCFullYear() >= 1990 && shifted.getUTCFullYear() <= 1999;
      link.hidden = !valid;
      link.href = url({...state, month:shifted.getUTCMonth()+1, page:1}, shifted.getUTCFullYear());
    }
    root.querySelector('[data-timeline-status]').textContent = `${total} sourced ${total===1 ? 'event' : 'events'} · ${state.view} view`;
    root.querySelector('[data-event-paging]').hidden = pages <= 1 || state.view==='calendar';
    root.querySelector('[data-event-page]').textContent = `Page ${state.page} of ${pages}`;
    root.querySelector('[data-event-prev]').disabled = state.page <= 1;
    root.querySelector('[data-event-next]').disabled = state.page >= pages;
    if (write) history.pushState(null,'',url());
  }
  function update(change) { state = {...state,...change}; render(true); }
  document.querySelector('.ed-month-rail').addEventListener('click', event => {
    const link = event.target.closest('[data-month]');
    if (!link || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault(); update({month:Number(link.dataset.month),page:1});
  });
  category.addEventListener('change', () => update({category:category.value,page:1}));
  region.addEventListener('change', () => update({region:region.value,page:1}));
  root.querySelectorAll('[data-archive-view]').forEach(b => b.addEventListener('click', () => update({view:b.dataset.archiveView})));
  root.querySelector('[data-event-prev]').addEventListener('click', () => update({page:state.page-1}));
  root.querySelector('[data-event-next]').addEventListener('click', () => update({page:state.page+1}));
  window.addEventListener('popstate', () => { read(); render(); });
  window.addEventListener('hashchange', () => { read(); render(); });
  read(); render();
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function eventLink(event, withDate = false) {
  const link = element('a','ar-week-event'); link.href = event.url;
  link.append(element('span','ar-meta',`${withDate ? formatDate(event.date)+' · ' : ''}${CATEGORIES[event.category]} · ${event.region}`), element('h3','',event.title), element('p','',event.summary));
  return link;
}
function renderWeekDays(start, events) {
  const fragment = document.createDocumentFragment();
  for (let i=0; i<7; i++) {
    const date = shiftDays(start,i);
    const section = element('section','ar-day');
    const h = element('h2'); const time = element('time'); time.dateTime = date;
    time.append(element('span','',formatDate(date,{weekday:'short',month:undefined,day:undefined,year:undefined})), document.createTextNode(String(parseDate(date).getUTCDate())));
    h.append(time); section.append(h);
    const content = element('div');
    const items = events.filter(e => e.date===date);
    section.classList.toggle('ar-day-empty',items.length===0);
    if (items.length) content.append(...items.map(e => eventLink(e)));
    else content.append(element('p','ar-muted','No entries for this day.'));
    section.append(content); fragment.append(section);
  }
  return fragment;
}
function renderWeekLead(container, event) {
  container.replaceChildren();
  if (!event) return;
  const link = eventLink(event, true);
  link.querySelector('h3').replaceWith(element('h2','',event.title));
  if (event.image) {
    const image = element('img');
    Object.assign(image,event.image,{loading:'lazy',decoding:'async'});
    link.prepend(image);
  }
  container.append(link);
}
export async function initializeWeek() {
  const root = document.querySelector('[data-weekly]');
  const home = document.querySelector('#this-week');
  if (!root && !home) return;
  let catalog;
  try {
    const response = await fetch('/assets/runtime/week.json');
    if (!response.ok) throw new Error('Archive unavailable');
    catalog = await response.json();
  } catch {
    if (root) {
      root.querySelector('.ar-controls').hidden = true;
      root.querySelector('[data-week-explainer]').textContent = 'Showing the saved week. Live week browsing is temporarily unavailable; the complete timeline remains available.';
    }
    return;
  }
  const today = historicalDate();
  if (home) {
    const { start, end } = weekBounds(today);
    home.querySelector('h2 strong').textContent = today.slice(0,4);
    home.querySelector('.ed-date').textContent = `${formatDate(start)} – ${formatDate(end)}`;
    home.querySelector('.ed-cta').href = '/this-week/';
    const picks = eventsInWeek(catalog.events,today).filter(e => e.category !== 'news');
    const copy = home.querySelector('[data-home-week-copy]');
    const note = home.querySelector('.ed-week-note');
    if (copy) copy.textContent = picks[0]?.summary || 'Turn back the clock. Explore the week’s dates, the decade’s stories, and the objects you remember.';
    const art = home.querySelector('.ed-week-art');
    if (picks[0]?.image && art) {
      const image = element('img');
      Object.assign(image,picks[0].image,{loading:'eager',decoding:'async'});
      art.replaceChildren(image);
    }
    note.replaceChildren();
    const link = element('a','',picks[0]?.title || 'Open the historical week →');
    link.href = picks[0]?.url || '/this-week/'; note.append(link);
  }
  if (!root) return;
  const input = root.querySelector('[data-week-date]');
  const year = root.querySelector('[data-week-select]');
  let date, custom;
  function read() {
    const requested = new URLSearchParams(location.search).get('date');
    custom = inDecade(requested);
    date = custom ? requested : today;
  }
  function render(write = false) {
    const {start,end} = weekBounds(date);
    const events = eventsInWeek(catalog.events,date);
    root.querySelector('[data-week-year]').textContent = date.slice(0,4);
    root.querySelector('[data-week-range]').textContent = `${formatDate(start)} – ${formatDate(end)}`;
    input.value = date; year.value = date.slice(0,4);
    root.querySelector('[data-week-count]').textContent = `${events.length} sourced ${events.length===1 ? 'entry' : 'entries'}`;
    root.querySelector('[data-week-days]').replaceChildren(renderWeekDays(start,events));
    renderWeekLead(root.querySelector('[data-week-lead]'),events[0]);
    root.querySelector('[data-week-prev]').disabled = start <= MIN_DATE;
    root.querySelector('[data-week-next]').disabled = end >= MAX_DATE;
    root.querySelector('[data-week-empty]').hidden = events.length > 0;
    root.querySelector('[data-week-explainer]').textContent = custom ? 'Browsing a selected historical Monday–Sunday week. Choose “30 years ago” to return to today’s default.' : 'Monday–Sunday, containing the date 30 years before today in America/New_York. Dates beyond the archive are limited to 1990–1999.';
    const month = root.querySelector('[data-week-month]');
    month.href = `/timeline/${date.slice(0,4)}/?month=${date.slice(5,7)}#events-${date.slice(0,7)}`;
    const nearby = root.querySelector('[data-week-nearby]'); nearby.hidden = events.length > 0;
    if (!events.length) {
      const nearest = [...catalog.events].sort((a,b) => Math.abs(parseDate(a.date)-parseDate(date))-Math.abs(parseDate(b.date)-parseDate(date))).slice(0,3).sort((a,b) => a.date.localeCompare(b.date));
      root.querySelector('[data-nearby-events]').replaceChildren(...nearest.map(e => eventLink(e,true)));
    }
    if (write) history.pushState(null,'', custom ? `?date=${date}` : location.pathname);
  }
  function select(value) { if (inDecade(value)) { date=value; custom=true; render(true); } }
  input.addEventListener('change', () => { if (inDecade(input.value)) select(input.value); else input.value=date; });
  year.addEventListener('change', () => select(changeYear(date,Number(year.value))));
  root.querySelector('[data-week-prev]').addEventListener('click', () => select(clampDecade(shiftDays(date,-7))));
  root.querySelector('[data-week-next]').addEventListener('click', () => select(clampDecade(shiftDays(date,7))));
  root.querySelector('[data-week-today]').addEventListener('click', () => {date=today; custom=false; render(true);});
  window.addEventListener('popstate', () => {read(); render();});
  read(); render();
}
