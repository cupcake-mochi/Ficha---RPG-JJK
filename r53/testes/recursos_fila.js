'use strict';
// Eventos entregues simulados. Não substitui o ensaio de gatilhos no Google.
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const {criaSheets}=require('../../medidas/sheets-de-mentira'),{fontes}=require('../../medidas/carregar-ficha');
const logs=[],{ctx,ss}=criaSheets(fontes(),fs.readFileSync('apps-script/Codigo.gs','utf8'),{console:{log:s=>logs.push(s)}});
for(const s of ctx.ABAS){const a=ss.insertSheet(s.nome);if(s.cols>26)a.insertColumnsAfter(26,s.cols-26);if(s.rows>1000)a.insertRowsAfter(1000,s.rows-1000);}
for(const n of ['MONTAGENS','DADOS_R53'])if(!ss.getSheetByName(n))ss.insertSheet(n);
vm.runInContext(fs.readFileSync('r53/atalho_livre.gs','utf8'),ctx);
ctx.r53LivreValido_=()=>true;
let checks=0;const eq=(a,b)=>{assert.deepEqual(a,b);checks++;};
const ficha=ss.getSheetByName('FICHA'),inv=ss.getSheetByName('INVOCAÇÕES');
const caixas=ctx.ABAS.find(s=>s.nome==='INVOCAÇÕES').redutores;
const put=(s,vals)=>Object.entries(vals).forEach(([a,v])=>s.getRange(a).setValue(v));
const casos=[];
for(const linha of [26,30,34])for(const modo of ['onEdit','atalho'])casos.push({s:ficha,d:'AM'+linha,a:'D'+linha,m:'J'+linha,t:'AF'+linha,modo});
for(const [d,a,t,m]of caixas)casos.push({s:inv,d,a,m,t,modo:'onEdit'});
for(const x of casos){
 const {s,d,a,m,t,modo}=x;
 const evento=(value,oldValue)=>({source:ss,range:s.getRange(d),value,oldValue});
 const run=e=>modo==='atalho'?ctx.r53EdicaoLivre_(e):ctx.onEdit(e);
 const reset=(temp=0,current=20)=>put(s,{[a]:current,[m]:20,[t]:temp,[d]:''});
 reset();s.getRange(d).setValue(-3);run(evento('-5'));eq(s.getRange(a).getValue(),15);eq(s.getRange(d).getValue(),-3);
 run(evento('-3','-5'));eq(s.getRange(a).getValue(),12);eq(s.getRange(d).getValue(),'');
 reset();s.getRange(d).setValue(-5);run(evento('-5'));run(evento('-5','-5'));eq(s.getRange(a).getValue(),10);
 reset(6);s.getRange(d).setValue(-3);run(evento('-5'));run(evento('-3','-5'));eq(s.getRange(a).getValue(),18);eq(s.getRange(t).getValue(),0);
 reset();s.getRange(d).setValue(-3);run(evento(undefined,'-5'));eq(s.getRange(a).getValue(),20);eq(s.getRange(d).getValue(),-3);
 for(const valor of ['0','x','Infinity']){run(evento(valor));eq(s.getRange(a).getValue(),20);eq(s.getRange(d).getValue(),-3);}
 reset(0,10);s.getRange(d).setValue(50);run(evento('50'));eq(s.getRange(a).getValue(),20);
 reset(3,10);s.getRange(d).setValue(-50);run(evento('-50'));eq(s.getRange(a).getValue(),0);eq(s.getRange(t).getValue(),0);
 reset(0,10);s.getRange(d).setValue(-0.5);run(evento('-0.5'));eq(s.getRange(a).getValue(),9.5);
 if(s===inv){
  reset(0,'');s.getRange(d).setValue(-5);run(evento('-5'));eq(s.getRange(a).getValue(),15);
  const neighbor=(d.startsWith('X')?'Y':'AR')+d.match(/\d+/)[0];
  reset(3,10);put(s,{[d]:-5,[neighbor]:7});run({source:ss,range:s.getRange(d+':'+neighbor)});
  eq(s.getRange(a).getValue(),8);eq(s.getRange(t).getValue(),0);eq(s.getRange(d).getValue(),'');eq(s.getRange(neighbor).getValue(),7);
 }
}
eq(logs,[]);
// Falha de trava: nenhum saldo consumido, campo preservado, aviso e sem fallback.
const originalLock=ctx.LockService,originalFlush=ctx.SpreadsheetApp.flush;let trace=[],toasts=[];
ss.toast=(...args)=>toasts.push(args);ctx.LockService={getDocumentLock:()=>({tryLock:()=>false,releaseLock:()=>trace.push('release')})};
put(ficha,{D26:20,J26:20,AF26:0,AM26:-5});
eq(ctx.r53EdicaoLivre_({source:ss,range:ficha.getRange('AM26'),value:'-5'}),true);
eq(ficha.getRange('D26').getValue(),20);eq(ficha.getRange('AM26').getValue(),-5);eq(toasts.length,1);eq(trace,[]);
ctx.LockService={getDocumentLock:()=>({tryLock:()=>{trace.push('lock');return true;},releaseLock:()=>trace.push('release')})};
ctx.SpreadsheetApp.flush=()=>trace.push('flush');logs.length=0;
eq(ctx.r53EdicaoLivre_({source:ss,range:ficha.getRange('AM26'),value:'-5'}),true);eq(trace,['lock','flush','release']);eq(ficha.getRange('D26').getValue(),15);
// Falha após a escrita: nenhum fallback nem segunda aplicação. Trava liberada.
trace=[];let writes=0;const get=ficha.getRange.bind(ficha);
ficha.getRange=function(...args){const r=get(...args);if(args[0]==='D26'){const set=r.setValue.bind(r);r.setValue=v=>{writes++;set(v);throw Error('falha simulada após gravar');};}return r;};
put(ficha,{AM26:-5});eq(ctx.r53EdicaoLivre_({source:ss,range:get('AM26'),value:'-5'}),true);
eq(writes,1);eq(get('D26').getValue(),10);eq(get('AM26').getValue(),-5);eq(trace,['lock','flush','release']);eq(toasts.length,2);
ficha.getRange=get;ctx.LockService=originalLock;ctx.SpreadsheetApp.flush=originalFlush;
// Um comando recusado pode sumir da caixa quando o evento seguinte termina.
let tentativas=0;
ctx.LockService={getDocumentLock:()=>({tryLock:()=>++tentativas>1,releaseLock:()=>{}})};
toasts=[];logs.length=0;
put(ficha,{D26:20,J26:20,AF26:0,AM26:-3});
const caixaVida=ficha.getRange('AM26');
ctx.r53EdicaoLivre_({source:ss,range:caixaVida,value:'-5'});
ctx.r53EdicaoLivre_({source:ss,range:caixaVida,value:'-3',oldValue:'-5'});
eq(ficha.getRange('D26').getValue(),17);
eq(caixaVida.getValue(),'');
eq(toasts.length,1);
eq(toasts[0][0],'Ajuste -5 em FICHA!AM26 não aplicado. Confira os saldos e repita esse ajuste se necessário.');
ctx.LockService=originalLock;
// A aritmética não muda nesta correção (inclusive A08 ainda pendente).
for(const a of [0,5,20,''])for(const m of [0,20])for(const t of [0,3])for(const d of [-30,-3,0,3,30]){
 const antes=ctx.aplicaPasso_(a,m,t,d),depois=ctx.r53LivrePasso_(a,m,t,d);eq(JSON.stringify(antes),JSON.stringify(depois));
}
const engine=fs.readFileSync('r53/recursos_delta.gs','utf8'),codigo=fs.readFileSync('apps-script/Codigo.gs','utf8');
eq(codigo.split(engine).length,2);
const gs=fs.readFileSync('r53/atalho_livre.gs','utf8');eq(gs.split(engine.replace('function r53DeltaExecutar_(', 'function r53LivreDeltaExecutar_(')).length,2);
const g=require('../atalho_livre'),pega=n=>JSON.parse(gs.match(new RegExp('^var '+n+'=(.*);$','m'))[1]);
eq(g.fonte(pega('R53_LIVRE_'),...pega('R53_LIVRE_HASHES_'),pega('R53_LIVRE_GATILHOS_'),pega('R53_LIVRE_MARCAS_'),{caixas:pega('R53_LIVRE_DELTA_'),passo:gs.match(/function r53LivrePasso_\([\s\S]*?\n}/)[0]}),gs);
console.log(JSON.stringify({resultado:'OK',verificacoes:checks,rotas:casos.length,escopo:'onEdit completo e dispatcher rápido simulados; não nativo'}));
