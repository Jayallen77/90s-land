/** Original reading examples. No storage, network requests or historical software emulation. */
export function mp3Budget(capacity, bitrate, minutes) {
  if (![capacity,bitrate,minutes].every(Number.isFinite) || capacity<1 || capacity>512 || !Number.isInteger(capacity) || ![64,96,128,192,256].includes(bitrate) || minutes<1 || minutes>12 || minutes*2%1!==0) return null;
  const seconds=capacity*8000/bitrate;
  const trackMB=minutes*60*bitrate/8000;
  return {seconds,trackMB,tracks:Math.floor(capacity/trackMB)};
}

export function keypadCounts(value) {
  const raw=String(value);
  if (!/^[A-Za-z]{1,24}$/.test(raw)) return null;
  const word=raw.toUpperCase();
  const groups=['ABC','DEF','GHI','JKL','MNO','PQRS','TUV','WXYZ'];
  const letters=[...word].map(letter=>{
    const index=groups.findIndex(group=>group.includes(letter));
    const key=String(index+2);
    return {key,taps:key.repeat(groups[index].indexOf(letter)+1)};
  });
  return {word,traditional:letters.map(l=>l.taps).join(' · '),presses:letters.reduce((sum,l)=>sum+l.taps.length,0),predictive:letters.map(l=>l.key).join(''),letterCount:word.length};
}

export function initializeReadingTools() {
  document.querySelectorAll('[data-reading-tool]').forEach(root=>{
    const form=root.querySelector('form');
    const result=root.querySelector('[data-reading-result]');
    function update() {
      if (root.dataset.readingTool==='mp3-budget') {
        const capacity=Number(form.elements.capacity.value),bitrate=Number(form.elements.bitrate.value),minutes=Number(form.elements.minutes.value);
        const budget=mp3Budget(capacity,bitrate,minutes);
        if (!budget) {result.textContent='Use 1–512 whole decimal MB and a track length from 1–12 minutes in half-minute steps.';return;}
        const duration=`${Math.floor(budget.seconds/60)}:${String(Math.floor(budget.seconds%60)).padStart(2,'0')}`;
        result.textContent=`At ${bitrate} kbps, ${capacity} MB holds at most ${duration} of audio payload: ${budget.tracks} whole ${minutes}-minute tracks. Each track needs ${budget.trackMB.toFixed(2)} MB.`;
      } else {
        const counts=keypadCounts(form.elements.word.value);
        result.textContent=counts?`${counts.word}: traditional ${counts.traditional} — ${counts.presses} letter presses. Predictive letter keys ${counts.predictive} — ${counts.letterCount} presses.`:'Enter one word using 1–24 letters A–Z. This comparison does not map punctuation or other alphabets.';
      }
    }
    form.addEventListener('submit',event=>event.preventDefault());
    form.addEventListener('input',update);
    form.addEventListener('change',update);
    root.querySelectorAll('input,select').forEach(control=>control.disabled=false);
    update();
  });
}
