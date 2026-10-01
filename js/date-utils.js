// Civil dates use UTC arithmetic; only the definition of "today" uses a timezone.
export const MIN_DATE = '1990-01-01';
export const MAX_DATE = '1999-12-31';
export function parseDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
  const date = new Date(`${value}T12:00:00Z`);
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value ? date : null;
}
export const isoDate = date => date.toISOString().slice(0, 10);
export function shiftDays(value, days) {
  const date = parseDate(value);
  if (!date) throw new RangeError('Invalid civil date');
  date.setUTCDate(date.getUTCDate() + days);
  return isoDate(date);
}
export function inDecade(value) { return !!parseDate(value) && value >= MIN_DATE && value <= MAX_DATE; }
export function clampDecade(value) { return value < MIN_DATE ? MIN_DATE : value > MAX_DATE ? MAX_DATE : value; }
export function changeYear(value, year) {
  const date = parseDate(value);
  if (!date || !Number.isInteger(year) || year < 1000 || year > 9999) throw new RangeError('Invalid year or date');
  const month = date.getUTCMonth();
  const maxDay = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
  return isoDate(new Date(Date.UTC(year, month, Math.min(date.getUTCDate(), maxDay), 12)));
}
export function newYorkDate(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-US', { timeZone:'America/New_York', year:'numeric', month:'2-digit', day:'2-digit' }).formatToParts(now);
  const values = Object.fromEntries(parts.map(p => [p.type, p.value]));
  return `${values.year}-${values.month}-${values.day}`;
}
export function editorialDate(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-US', {timeZone:'America/Denver',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
  const values = Object.fromEntries(parts.map(p => [p.type,p.value]));
  return `${values.year}-${values.month}-${values.day}`;
}
export function historicalDate(now = new Date()) {
  const today = editorialDate(now);
  return clampDecade(changeYear(today, Number(today.slice(0,4)) - 30));
}
export function weekBounds(value) {
  const date = parseDate(value);
  if (!date) throw new RangeError('Invalid week date');
  const start = shiftDays(value, -((date.getUTCDay() + 6) % 7));
  return { start, end:shiftDays(start, 6) };
}
export function eventsInWeek(events, value) {
  const { start, end } = weekBounds(value);
  return events.filter(event => parseDate(event.date) && event.date >= start && event.date <= end);
}
export function formatDate(value, options = {}) {
  return new Intl.DateTimeFormat('en-US', {timeZone:'UTC', month:'short', day:'numeric', year:'numeric', ...options}).format(parseDate(value));
}
