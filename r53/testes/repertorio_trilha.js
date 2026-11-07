'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),z=require('node:zlib');
const crypto=require('node:crypto'),path=require('node:path');
const p=require('../diagnostico-android/preparar_repertorio_trilha'),rt=require('../repertorio_trilha_runtime');
const {formulaLocal}=require('../diagnostico-android/preparar_pilha_5156');
const clone=x=>structuredClone(x);
for(const locale of ['pt_BR','en_US']){
 const snapshot={locale,cells:p.plano().map(d=>({...d,sheetId:7,value:formulaLocal(d.antes,locale)}))};
 const prepared=p.prepararCelulas(snapshot);assert.equal(prepared.pedidos.length,102);assert.equal(prepared.reverter(prepared.final).length,102);
 for(const mutate of [s=>s.cells.pop(),s=>s.cells.push(s.cells[0]),s=>s.cells[0]=s.cells[1],s=>s.cells[0].value='não sobrescrever',s=>s.locale='xx',s=>s.cells[0].sheetId=null]){const bad=clone(snapshot);mutate(bad);assert.throws(()=>p.prepararCelulas(bad));}
 const bad=clone(prepared.final);bad.cells.at(-1).value='edição posterior';assert.throws(()=>prepared.reverter(bad));
 const writes=[],c={Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()})},r53CargaFormulaNoIdioma_:formulaLocal};vm.createContext(c);vm.runInContext(rt.gerar(),c);
 function event(aba,r,rr,col,cc){const sh={getName:()=>aba,getParent:()=>({getSpreadsheetLocale:()=>locale}),getRange:(r,c,n,w)=>({setValues:rows=>{assert.equal(rows.length,n);assert.equal(w,1);rows.forEach((row,i)=>writes.push([r+i,c,row[0]]));}})};return {range:{getSheet:()=>sh,getRow:()=>r,getLastRow:()=>rr,getColumn:()=>col,getLastColumn:()=>cc}};}
 assert.equal(c.r53RepertorioRestaurar_(event('DADOS_INVOC',16,28,105,108)),true);assert.equal(writes.length,52);
 for(const d of p.plano().filter(d=>d.aba==='DADOS_INVOC'))assert.ok(writes.some(([r,col,v])=>r===d.r&&col===d.c&&v===formulaLocal(d.depois,locale)));
 writes.length=0;assert.equal(c.r53RepertorioRestaurar_(event('DADOS_R53',57,57,183,183)),true);assert.equal(writes.length,1);
 writes.length=0;assert.equal(c.r53RepertorioRestaurar_(event('INVOCAÇÕES',170,170,9,25)),true);assert.equal(writes.length,1);
 writes.length=0;assert.equal(c.r53RepertorioRestaurar_(event('INVOCAÇÕES',34,39,4,6)),true);assert.deepEqual(writes.map(x=>x.slice(0,2)),[[34,4],[37,4]]);
 writes.length=0;assert.equal(c.r53RepertorioRestaurar_(event('INVOCAÇÕES',34,34,4,6)),true);assert.deepEqual(writes.map(x=>x.slice(0,2)),[[34,4],[37,4]]);
 writes.length=0;assert.equal(c.r53RepertorioRestaurar_(event('DADOS_R53',57,59,181,183)),true);assert.equal(writes.length,9);
 assert.equal(c.r53RepertorioEntrada_(event('INVOCAÇÕES',35,36,4,6)),true);assert.equal(c.r53RepertorioEntrada_(event('INVOCAÇÕES',34,39,4,6)),false);
}
assert.throws(()=>p.prepararCodigo('base desconhecida'));
const ns=p.notas().map(d=>({...d,sheetId:7,note:d.antes}));assert.equal(p.prepararNotas(ns).length,14);const badNotes=clone(ns);badNotes[0].note='nota própria';assert.throws(()=>p.prepararNotas(badNotes));
const ui={sheetId:7,cells:Array.from({length:6},(_,i)=>['D','E','F'].map(c=>({a1:c+(34+i),cell:{}}))).flat(),labelFormat:{textFormat:{fontSize:8}},valueFormat:{textFormat:{fontSize:10}}};
assert.equal(p.prepararUI(ui).length,7);for(const key of ['userEnteredValue','dataValidation','note']){const bad=clone(ui);bad.cells[4].cell[key]=key==='note'?'nota':{};assert.throws(()=>p.prepararUI(bad));}
assert.equal(rt.reverterFonte('antes\n'+rt.GUARDA+'depois'),'antes\ndepois');assert.throws(()=>rt.reverterFonte(rt.GUARDA+rt.GUARDA));
if(process.argv[2]){
 const src=fs.readFileSync(process.argv[2],'utf8'),out=p.prepararCodigo(src);new Function(out);assert.ok(out.includes('r53AjustarRepertorio_(R53_MODULO_.__estado().abas,true)'));assert.ok(out.includes('r53AjustarExpansao_'));
 const maps=[src,out].map(code=>{const c=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()})}});vm.runInContext(code,c);const m=new Map();for(const [col,formula,rows]of c.r53PraticaMontagem_())for(const row of rows){const key=row+':'+col;assert.equal(m.has(key),false);m.set(key,formula.replace(/\x01/g,String(row)));}return m;});
 const targets=new Map(p.plano().filter(d=>d.aba==='DADOS_R53').map(d=>[d.r+':'+d.c,d.depois]));
 for(const [k,v]of maps[0])assert.equal(maps[1].get(k),targets.get(k)??v,'Molde legado '+k);
 for(const [k,v]of targets)assert.equal(maps[1].get(k),v);
 for(const k of maps[1].keys())assert.ok(maps[0].has(k)||targets.has(k),'Molde não previsto');
}
if(process.argv[3]){
 const c=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()}),computeDigest:(_,s)=>Array.from(crypto.createHash('sha256').update(s).digest()),DigestAlgorithm:{SHA_256:1},Charset:{UTF_8:1}}});
 for(const n of ['Ficha','Invocacoes','Analise','Configuracao','Origens'])vm.runInContext(fs.readFileSync(path.join(process.argv[3],'qa-era-'+n+'.gs'),'utf8'),c);
 vm.runInContext(p.prepararCodigo(fs.readFileSync(process.argv[2],'utf8')),c);
 const estado=c.r53Modulo_().__estado();assert.equal(estado.sobras.length,0);assert.equal(estado.abas.some(a=>a.nome==='ANALISE'),false);
 assert.equal(estado.abas.some(a=>a.nome==='DADOS_R53'),false);
 const moldes=c.r53PraticaMontagem_();
 for(const d of p.plano()){if(d.aba==='DADOS_R53'){const g=moldes.find(g=>g[0]===d.c&&g[2].includes(d.r));assert.ok(g);assert.equal(g[1].replace(/\x01/g,String(d.r)),d.depois);}else{const a=estado.abas.find(a=>a.nome===d.aba);assert.equal(a.vals.find(v=>v[0]===d.r&&v[1]===d.c)[2],d.depois);}}
}
console.log(JSON.stringify({resultado:'OK',alvos:102,notas:14,locales:2,escopo:'Pré-condições, reversão, seletor e recuperação focal/mista'}));
