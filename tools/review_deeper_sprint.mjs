/** Review the complete active collection in the actual public-only release. */
import {chromium} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
const base=process.env.PLAYWRIGHT_BASE_URL||'http://127.0.0.1:4175';
const output=process.env.REVIEW_OUTPUT||'/private/tmp/90s-land-sprint-qa-20261105';
const reportPath=process.env.REVIEW_REPORT||'reports/deeper-sprint/page-qa.json';
const selectedPaths=new Set((process.env.REVIEW_PATHS||'').split(',').filter(Boolean));
const routes=JSON.parse(await readFile('data/routes.json','utf8')).filter(r=>r.type!=='redirects'&&(!selectedPaths.size||selectedPaths.has(r.path)));
const browser=await chromium.launch();const results=[];
await Promise.all([390,1440].flatMap(width=>[0,1].map(async worker=>{
 const context=await browser.newContext({viewport:{width,height:1000},hasTouch:width===390,reducedMotion:'reduce',timezoneId:'America/Denver'});
 const page=await context.newPage();const dir=path.join(output,String(width));await mkdir(dir,{recursive:true});
 for(let index=worker;index<routes.length;index+=2){
  const route=routes[index];const errors=[];const onError=e=>errors.push(e.message);page.on('pageerror',onError);
  try{
   const response=await page.goto(base+route.path,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
   const height=await page.evaluate(()=>document.documentElement.scrollHeight);
   for(let y=0;y<height;y+=900){await page.evaluate(y=>scrollTo(0,y),y);await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));}
   await page.evaluate(()=>scrollTo(0,0));
   await page.evaluate(()=>Promise.all([...document.images].filter(i=>i.getBoundingClientRect().height>0).map(i=>i.decode().catch(()=>{}))));
   const state=await page.evaluate(()=>({title:document.title,h1:document.querySelectorAll('h1').length,overflow:document.documentElement.scrollWidth>innerWidth,brokenImages:[...document.images].filter(i=>i.getBoundingClientRect().height>0&&(!i.complete||!i.naturalWidth)).map(i=>i.currentSrc||i.src),unrenderedFigure:/\{\{(?:figure|tool):/.test(document.querySelector('main')?.innerText||'')}));
   const violations=(await new AxeBuilder({page}).analyze()).violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}));
   const name=(route.path==='/'?'home':route.path.replace(/^\//,'').replace(/\/$/,'').replaceAll('/','--'))+'.jpg';
   await page.screenshot({path:path.join(dir,name),fullPage:true,type:'jpeg',quality:65,animations:'disabled'});
   const issues=[...(response.status()!==200?['HTTP '+response.status()]:[]),...(state.h1!==1?['h1 count '+state.h1]:[]),...(state.overflow?['horizontal overflow']:[]),...state.brokenImages.map(i=>'broken image '+i),...(state.unrenderedFigure?['unrendered figure marker']:[]),...errors,...violations.map(v=>'axe '+v.id)];
   results.push({path:route.path,width,status:response.status(),title:state.title,screenshot:width+'/'+name,height,issues,violations});
  }catch(error){results.push({path:route.path,width,issues:[String(error)]});}
  page.off('pageerror',onError);
  if(results.length%16===0)console.log(`Reviewed ${results.length}/${routes.length*2} renders; ${results.filter(r=>r.issues.length).length} with issues`);
 }
 await context.close();
})));
await browser.close();results.sort((a,b)=>a.path.localeCompare(b.path)||a.width-b.width);
const report={base,activePages:routes.length,viewports:[390,1440],renders:results.length,issuePages:results.filter(r=>r.issues.length).length,results};
await writeFile(path.join(output,'page-qa.json'),JSON.stringify(report,null,2)+'\n');
await writeFile(reportPath,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({activePages:routes.length,renders:results.length,issuePages:report.issuePages,output}));
process.exitCode=report.issuePages?1:0;
