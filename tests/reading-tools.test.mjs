import test from 'node:test';
import assert from 'node:assert/strict';
import {mp3Budget,keypadCounts} from '../js/reading-tools.js';
test('storage budgets preserve units and the whole-track boundary',()=>{
 assert.deepEqual(mp3Budget(32,128,4),{seconds:2000,trackMB:3.84,tracks:8});
 assert.equal(mp3Budget(32,64,4).seconds,4000);
 assert.equal(mp3Budget(1,256,12).tracks,0);
 for(const args of [[NaN,128,4],[0,128,4],[513,128,4],[32,127,4],[32,128,-1],[1.5,128,4],[32,128,2.1]])assert.equal(mp3Budget(...args),null);
});
test('key mapping explains repeated keys and ambiguous predictions',()=>{
 const hello=keypadCounts('hello');
 assert.equal(hello.presses,13);assert.equal(hello.predictive,'43556');assert.equal(hello.letterCount,5);
 for(const word of ['GOOD','HOME','HOOD','GONE'])assert.equal(keypadCounts(word).predictive,'4663');
 assert.equal(keypadCounts('Z').traditional,'9999');
 for(const word of ['', 'hello there','café','ß','<script>','A'.repeat(25)])assert.equal(keypadCounts(word),null);
});
