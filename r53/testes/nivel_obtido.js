'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),z=require('node:zlib'),crypto=require('node:crypto'),path=require('node:path');
const p=require('../diagnostico-android/preparar_nivel_obtido'),rt=require('../nivel_obtido_runtime'),{formulaLocal}=require('../diagnostico-android/preparar_pilha_5156');
assert.equal(p.plano().length,36);assert.equal(p.notas().length,2);assert.equal(p.validacoes().length,12);
assert.equal(rt.gerar(),fs.readFileSync('apps-script/NivelObtido.gs','utf8'));
assert.throws(()=>p.prepararCodigo('outra base'),/PR89/);
const utilities={base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()}),computeDigest:(_,s)=>Array.from(crypto.createHash('sha256').update(s).digest()),DigestAlgorithm:{SHA_256:1},Charset:{UTF_8:1}};
for(const locale of ['pt_BR','en_US']){
 const local=v=>typeof v==='string'&&v.startsWith('=')?formulaLocal(v,locale):v;
 const support={locale,cells:p.suporte().map(d=>({...d,sheetId:9,value:local(d.depois)}))};assert.equal(p.conferirSuporte(support),60);
 for(const mutate of [s=>s.cells.pop(),s=>s.cells[0]=s.cells[1],s=>s.cells[0].value='outra correção',s=>s.locale='xx']){const bad=structuredClone(support);mutate(bad);assert.throws(()=>p.conferirSuporte(bad));}
 const snap={locale,cells:p.plano().map(d=>({...d,sheetId:9,value:local(d.antes)}))},prepared=p.prepararCelulas(snap);
 assert.equal(prepared.pedidos.length,36);assert.equal(prepared.reverter(prepared.final).length,36);
 for(const mutate of [s=>s.cells.pop(),s=>s.cells[0]=s.cells[1],s=>s.cells[0].value='edição posterior',s=>s.locale='xx',s=>s.cells[0].sheetId=null]){const bad=structuredClone(snap);mutate(bad);assert.throws(()=>p.prepararCelulas(bad));}
 const bad=structuredClone(prepared.final);bad.cells[0].value='edição posterior';assert.throws(()=>prepared.reverter(bad));
 const notes=p.notas().map(d=>({...d,sheetId:8,note:d.antes}));assert.equal(p.prepararNotas(notes).length,2);notes[0].note='outra nota';assert.throws(()=>p.prepararNotas(notes));
 const validations=p.validacoes().map(d=>({...d,sheetId:8,dataValidation:null}));assert.equal(p.prepararValidacoes(validations).length,12);validations[0].dataValidation={condition:{type:'BOOLEAN'}};assert.throws(()=>p.prepararValidacoes(validations));
 const writes=[],c=vm.createContext({Utilities:utilities,r53CargaFormulaNoIdioma_:formulaLocal});vm.runInContext(rt.gerar(),c);
 const event=(r,rr,col,cc,name='DADOS_INVOC')=>({range:{getRow:()=>r,getLastRow:()=>rr,getColumn:()=>col,getLastColumn:()=>cc,getSheet:()=>({getName:()=>name,getParent:()=>({getSpreadsheetLocale:()=>locale}),getRange:(r,c)=>({setValues:rows=>rows.forEach((row,i)=>writes.push([r+i,c,row[0]]))})})}});
 for(const [r,rr,col,cc,n]of [[2,13,112,112,12],[2,3,111,113,6],[12,13,111,113,6],[2,3,214,216,6],[12,13,270,271,4],[2,13,215,215,12],[2,13,271,271,12]]){
  writes.length=0;assert.equal(c.r53NivelRestaurar_(event(r,rr,col,cc)),true);assert.equal(writes.length,n);
  for(const d of p.plano().filter(d=>d.r>=r&&d.r<=rr&&d.c>=col&&d.c<=cc))assert.ok(writes.some(x=>x[0]===d.r&&x[1]===d.c&&x[2]===local(d.depois)));
 }
 writes.length=0;assert.equal(c.r53NivelRestaurar_(event(2,3,110,113)),false);assert.equal(writes.length,6);
 writes.length=0;assert.equal(c.r53NivelRestaurar_(event(2,13,112,112,'INVOCAÇÕES')),false);assert.equal(writes.length,0);
 writes.length=0;assert.equal(c.r53NivelRestaurar_(event(2,13,171,171)),false);assert.equal(writes.length,0,'FO permanece no controlador da PR89');
 const fixture=()=>[{nome:'DADOS_INVOC',vals:p.plano().map(d=>[d.r,d.c,d.antes,7])},{nome:'INVOCAÇÕES',vals:[],dv:[],notas:p.notas().map(d=>[d.a1,d.antes])}];
 const tabs=fixture();c.r53AjustarNivel_(tabs);for(const d of p.plano())assert.equal(tabs[0].vals.find(v=>v[0]===d.r&&v[1]===d.c)[2],d.depois);
 assert.equal(tabs[1].dv.length,12);const once=JSON.stringify(tabs);c.r53AjustarNivel_(tabs);assert.equal(JSON.stringify(tabs),once);
 for(const mutate of [a=>a[0].vals[0][2]='divergente',a=>a[0].vals.push(a[0].vals[0]),a=>a[1].notas[1][1]='divergente',a=>a[1].dv.push([p.validacoes()[11].a1,'"outro menu"'])]){
  const bad=fixture();mutate(bad);const before=JSON.stringify(bad);assert.throws(()=>c.r53AjustarNivel_(bad));assert.equal(JSON.stringify(bad),before,'Recusa atômica');
 }
}
if(process.argv[2]){
 const src=fs.readFileSync(process.argv[2],'utf8'),out=p.prepararCodigo(src);new Function(out);assert.throws(()=>p.prepararCodigo(out),/PR89/);
 const c=vm.createContext({Utilities:utilities});vm.runInContext(out,c);
 if(process.argv[3]){
  for(const n of ['Ficha','Invocacoes','Analise','Configuracao','Origens'])vm.runInContext(fs.readFileSync(path.join(process.argv[3],'qa-era-'+n+'.gs'),'utf8'),c);
  const s=c.r53Modulo_().__estado();assert.equal(s.sobras.length,0);
  for(const d of p.plano()){const a=s.abas.find(a=>a.nome===d.aba);assert.equal(a.vals.find(v=>v[0]===d.r&&v[1]===d.c)[2],d.depois);}
  for(const d of p.notas())assert.equal(s.abas.find(a=>a.nome===d.aba).notas.find(x=>x[0]===d.a1)[1],d.depois);
  assert.equal(s.abas.find(a=>a.nome==='INVOCAÇÕES').dv.filter(x=>p.validacoes().some(d=>d.a1===x[0])).length,12);
 }
}
console.log(JSON.stringify({resultado:'OK',valores:36,notas:2,validacoes:12,suporte:60,locales:2,escopo:'snapshots, reversão, recuperação e atomicidade; transporte opcional'}));
