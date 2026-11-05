import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeSearch,matchesWords,searchRank} from '../js/search-matching.js';

test('reader aliases preserve the intended subject',()=>{
 for(const pair of [['R&B','rnb'],['R and B','rnb'],['Nintendo 64','N64'],['PS1','PlayStation'],['PSX','PlayStation 1'],['Super NES','SNES'],['Pokémon','Pokemon']])assert.equal(normalizeSearch(pair[0]),normalizeSearch(pair[1]));
});
test('short queries do not match arbitrary substrings',()=>{
 assert.equal(matchesWords(normalizeSearch('Try a classic guestbook preview'),normalizeSearch('R&B').split(' ')),false);
 assert.equal(matchesWords(normalizeSearch('A better record'),['r','b']),false);
 assert.equal(matchesWords(normalizeSearch('1996 Japan Nintendo 64'),['1996','japan','n64']),true);
 assert.equal(matchesWords(normalizeSearch('Nintendo'),['ninten']),true);
});
test('the subject in a title outranks incidental prose',()=>{
 const q=[normalizeSearch('R&B')];
 assert.ok(searchRank(normalizeSearch('90s R&B had many voices'),q)>searchRank(normalizeSearch('Calling a friend'),q));
});
