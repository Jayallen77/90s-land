/** Search language used by titles, metadata and reader queries. */
export function normalizeSearch(value) {
  return String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase()
    .replace(/\br\s*(?:&|and|[- ]?n[- ]?)\s*b\b/g,'rnb')
    .replace(/\brhythm\s+(?:and|&)\s+blues\b/g,'rnb')
    .replace(/\bnintendo\s*64\b/g,'n64')
    .replace(/\b(?:ps1|psx|playstation\s*1)\b/g,'playstation')
    .replace(/\b(?:super\s+nintendo|super\s+nes)\b/g,'snes')
    .replace(/\bhip[ -]+hop\b/g,'hiphop')
    .replace(/\bcd[ -]+r\b/g,'cdr')
    .replace(/\b(?:sms|text messages?|text messaging)\b/g,'texting')
    .replace(/\btr[ -]?909\b/g,'tr909')
    .replace(/[^\p{L}\p{N}]+/gu,' ').trim();
}

export function matchesWords(text, words) {
  const tokens=text.split(/\s+/);
  // Short inputs are words, never letters anywhere inside hundreds of pages.
  return words.every(word=>tokens.some(token=>token===word || (word.length>=3 && token.startsWith(word))));
}

export function searchRank(title, words) {
  if (!words.length) return 0;
  if(title===words.join(' '))return 3;
  return matchesWords(title,words)?2:1;
}
