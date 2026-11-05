import {announce} from './announce.js';

const ring=[
 {title:'Tape Deck Planet',copy:'Handwritten track lists and one more song for side B.',href:'/stories/from-mixtape-to-file/'},
 {title:'Pixel Pilot’s Game Notes',copy:'A place for save files, secret passages, and the next demo disc.',href:'/stories/the-demo-disc-evening/'},
 {title:'The Homepage Garage',copy:'Tiled backgrounds, favorite links, and a page that keeps changing.',href:'/stories/a-web-you-could-make/'}
];
export function initializeExhibits(){
 document.querySelectorAll('[data-web-exhibit]').forEach(root=>{
  let visits=247,index=0;
  root.querySelector('[data-demo-visit]')?.addEventListener('click',()=>{visits=(visits+1)%1000000;root.querySelector('[data-demo-count]').textContent=String(visits).padStart(6,'0');});
  root.querySelector('[data-demo-reset]')?.addEventListener('click',()=>{visits=247;root.querySelector('[data-demo-count]').textContent='000247';});
  const renderRing=()=>{const page=ring[index];root.querySelector('[data-ring-title]').textContent=page.title;root.querySelector('[data-ring-copy]').textContent=page.copy;root.querySelector('[data-ring-open]').href=page.href;announce(`Ring example: ${page.title}`);};
  root.querySelectorAll('[data-ring-step]').forEach(button=>button.addEventListener('click',()=>{index=(index+Number(button.dataset.ringStep)+ring.length)%ring.length;renderRing();}));
  root.querySelector('[data-ring-random]')?.addEventListener('click',()=>{index=(index+1+Math.floor(Math.random()*(ring.length-1)))%ring.length;renderRing();});
  root.querySelector('[data-away-form]')?.addEventListener('submit',event=>{event.preventDefault();const value=new FormData(event.currentTarget).get('away');root.querySelector('[data-away-preview]').textContent=String(value).trim();root.querySelector('[data-away-status]').textContent='Preview updated. No message was sent.';});
  if(['visitor-counter','webring-bar','aim-away-message'].includes(root.dataset.webExhibit)){
   root.querySelectorAll('[data-exhibit-control]').forEach(button=>{button.disabled=false;});
  }
 });
}
