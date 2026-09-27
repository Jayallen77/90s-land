import test from 'node:test';
import assert from 'node:assert/strict';
import { parseDate, newYorkDate, historicalDate, changeYear, weekBounds, shiftDays, eventsInWeek, inDecade } from '../js/date-utils.js';

test('rejects normalized invalid dates and accepts the 1996 leap day', () => {
  for (const value of ['1995-02-29','1996-02-30','1996-13-01','96-02-29','1996-2-29','garbage',null]) assert.equal(parseDate(value),null);
  assert.ok(parseDate('1996-02-29'));
});
test('year changes clamp leap days', () => {
  assert.equal(changeYear('1996-02-29',1995),'1995-02-28');
  assert.equal(historicalDate(new Date('2024-02-29T20:00:00Z')),'1994-02-28');
});
test('New York date, rather than UTC date, controls the default', () => {
  assert.equal(newYorkDate(new Date('2026-09-28T02:00:00Z')),'2026-09-27');
  assert.equal(historicalDate(new Date('2026-09-28T02:00:00Z')),'1996-09-27');
  assert.equal(historicalDate(new Date('2026-09-28T05:00:00Z')),'1996-09-28');
});
test('civil week arithmetic remains stable through DST and year boundaries', () => {
  assert.deepEqual(weekBounds('1996-09-29'),{start:'1996-09-23',end:'1996-09-29'});
  assert.deepEqual(weekBounds('1997-01-01'),{start:'1996-12-30',end:'1997-01-05'});
  assert.deepEqual(weekBounds('1999-12-31'),{start:'1999-12-27',end:'2000-01-02'});
  assert.equal(shiftDays('1996-03-31',7),'1996-04-07');
  assert.equal(shiftDays('1996-10-27',-7),'1996-10-20');
});
test('both edges of a historical week are inclusive', () => {
  const events = ['1996-09-22','1996-09-23','1996-09-29','1996-09-30'].map(date => ({date}));
  assert.deepEqual(eventsInWeek(events,'1996-09-27').map(e=>e.date),['1996-09-23','1996-09-29']);
});
test('defaults and selectable dates stay within the archive', () => {
  assert.equal(historicalDate(new Date('2019-06-12T12:00:00Z')),'1990-01-01');
  assert.equal(historicalDate(new Date('2031-06-12T12:00:00Z')),'1999-12-31');
  assert.equal(inDecade('2000-01-01'),false);
  assert.equal(inDecade('1990-01-01'),true);
  assert.equal(inDecade('1999-12-31'),true);
});
