import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {chooseMemory, weekPicks} from '../js/discovery.js';
import {eventsInWeek, shiftDays} from '../js/date-utils.js';
const pool=JSON.parse(readFileSync(new URL('../assets/runtime/surprise.json',import.meta.url)));
const events=JSON.parse(readFileSync(new URL('../assets/runtime/week.json',import.meta.url))).events;

test('type weighting prevents a large event catalog from dominating',() => {
  const expected=['story','story','story','object','object','object','event','event','year','collection','tour'];
  expected.forEach((kind,index) => assert.equal(chooseMemory(pool,[],()=> (index+.5)/11).kind,kind));
});
test('recent choices stay excluded, including across legacy object IDs',() => {
  let recent=[];
  for(let i=0;i<100;i++) {
    const chosen=chooseMemory(pool,recent,()=>.3);
    assert(!recent.includes(chosen.id));recent=[chosen.id,...recent].slice(0,3);
  }
  assert.throws(()=>chooseMemory([]),/No published destinations/);
});
test('all 522 historical weeks keep honest, balanced picks from their actual dates',() => {
  for(let date='1990-01-01';date<'2000-01-01';date=shiftDays(date,7)) {
    const actual=eventsInWeek(events,date), picks=weekPicks(actual);
    assert(picks.length<=4);assert.equal(new Set(picks.map(e=>e.id)).size,picks.length);
    assert(picks.every(e=>actual.includes(e)));assert(picks.filter(e=>e.theme==='movies').length<=2);
    if(actual.some(e=>e.defining))assert(picks[0].defining);
    assert.equal(picks.length===0,actual.length===0);
  }
});
