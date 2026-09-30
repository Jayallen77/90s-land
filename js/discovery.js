// Pure selections shared by the live week and discovery dialog.
const WEIGHTS = {story:3, object:3, event:2, year:1, collection:1, tour:1};

export function chooseMemory(items, recent = [], random = Math.random) {
  const available = items.filter(item => !recent.includes(item.id));
  const pool = available.length ? available : items;
  if (!pool.length) throw new Error('No published destinations');
  const kinds = Object.entries(WEIGHTS).filter(([kind]) => pool.some(item => item.kind===kind));
  if (!kinds.length) throw new Error('No supported destinations');
  let ticket = random()*kinds.reduce((sum,[,weight]) => sum+weight,0);
  const chosenKind = kinds.find(([,weight]) => (ticket-=weight)<0)?.[0] || kinds.at(-1)[0];
  const choices = pool.filter(item => item.kind===chosenKind);
  return choices[Math.min(choices.length-1, Math.floor(random()*choices.length))];
}

export function weekPicks(events, limit=4) {
  const ranked = [...events].sort((a,b) => Number(Boolean(b.defining))-Number(Boolean(a.defining)) || a.date.localeCompare(b.date) || a.id.localeCompare(b.id));
  const selected = [], themes = new Set();
  for (const event of ranked) {
    if (!themes.has(event.theme)) {selected.push(event); themes.add(event.theme);}
    if (selected.length===limit) break;
  }
  for (const event of ranked) {
    if (selected.length>=limit) break;
    if (!selected.includes(event) && (event.theme!=='movies' || selected.filter(e => e.theme==='movies').length<2)) selected.push(event);
  }
  return selected;
}
