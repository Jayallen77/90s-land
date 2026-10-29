import fs from 'node:fs';

const directory=new URL('../content/editorial/stories/',import.meta.url);
export const features=fs.readdirSync(directory).filter(name=>name.endsWith('.md')).sort().map(name=>{
 const text=fs.readFileSync(new URL(name,directory),'utf8');
 return JSON.parse(text.match(/<!-- story: (.*?) -->/)[1]);
});
export const eventHref=event=>`/timeline/${event.date.slice(0,4)}/${event.date.length>=7?`?month=${event.date.slice(5,7)}`:''}#event-${event.id}`;
