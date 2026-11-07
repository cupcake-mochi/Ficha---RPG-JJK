'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),z=require('node:zlib'),fs=require('node:fs');
const p=require('../diagnostico-android/preparar_expansao_domada');
const rt=require('../expansao_domada_runtime');
const {formulaLocal}=require('../diagnostico-android/preparar_pilha_5156');
const {norm}=require('../diagnostico-android/preparar_pratica_cotidiana');
const plano=p.plano();
assert.equal(plano.length,48);
assert.equal(plano.filter(d=>d.aba==='DADOS_INVOC').length,36);
assert.equal(plano.filter(d=>d.aba==='ANALISE'&&d.c===4&&d.antes==='entrada'&&d.depois==='resultado').length,12);
assert.throws(()=>p.prepararCodigo('outra ficha'),/PR85/);
const notas=require('../diagnostico-android/expansao_domada_notas.json');
const notasSnapshot=notas.map(d=>({aba:d.aba,a1:d.a1,sheetId:3,note:d.antes}));
assert.equal(p.prepararNotas(notasSnapshot).length,36);
assert.ok(p.prepararNotas(notasSnapshot).every(r=>r.updateCells.fields==='note'));
assert.throws(()=>p.prepararNotas(notasSnapshot.slice(1)));
const notasAlteradas=structuredClone(notasSnapshot);notasAlteradas[0].note='Nota própria';assert.throws(()=>p.prepararNotas(notasAlteradas),/Nota anterior/);
for(const locale of ['pt_BR','en_US']){
 const snap={locale,cells:plano.map(d=>({aba:d.aba,r:d.r,c:d.c,sheetId:d.aba==='ANALISE'?2:1,value:norm(formulaLocal(d.antes,locale))}))};
 const pr=p.prepararCelulas(snap);
 assert.equal(pr.pedidos.length,48);assert.equal(pr.reverter(pr.final).length,48);
 pr.pedidos.forEach((request,i)=>{const d=plano[i],q=request.updateCells;assert.equal(q.fields,'userEnteredValue');assert.deepEqual(q.start,{sheetId:snap.cells[i].sheetId,rowIndex:d.r-1,columnIndex:d.c-1});assert.deepEqual(q.rows[0].values[0].userEnteredValue,d.depois.startsWith('=')?{formulaValue:norm(formulaLocal(d.depois,locale))}:{stringValue:'resultado'});});
 for(const mutate of [s=>s.cells.pop(),s=>s.cells.push(s.cells[0]),s=>{s.cells[0].value='=FALSE';},s=>{s.cells[0].aba='FICHA';}]){const x=structuredClone(snap);mutate(x);assert.throws(()=>p.prepararCelulas(x));}
 const dirty=structuredClone(pr.final);dirty.cells[0].value='=FALSE';assert.throws(()=>pr.reverter(dirty));
 let loads=0;const writes=[];
 const ctx=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>{loads++;return{getDataAsString:()=>z.gunzipSync(x).toString()};}},SpreadsheetApp:{newRichTextValue:()=>({setText(text){this.text=text;return this;},build(){return {rich:this.text};}})},r53CargaFormulaNoIdioma_:formulaLocal});
 vm.runInContext(rt.gerar(),ctx);
 function editar(name,r,c,rr=r,cc=c){writes.length=0;return ctx.r53ExpansaoRestaurar_({range:{getRow:()=>r,getLastRow:()=>rr,getColumn:()=>c,getLastColumn:()=>cc,getSheet:()=>({getName:()=>name,getParent:()=>({getSpreadsheetLocale:()=>locale}),getRange:(r,c)=>({setValues:rows=>rows.forEach((line,i)=>writes.push({r:r+i,c,value:line[0]})),setRichTextValues:rows=>rows.forEach((line,i)=>writes.push({r:r+i,c,value:line[0].rich.slice(1)}))})})}});}
 assert.equal(editar('INVOCAÇÕES',226,15),false);assert.equal(editar('DADOS_INVOC',2,240),false);assert.equal(editar('ANALISE',2947,3),false);assert.equal(loads,0);
 for(const d of plano){assert.equal(editar(d.aba,d.r,d.c),true);assert.deepEqual(writes,[{r:d.r,c:d.c,value:formulaLocal(d.depois,locale)}]);}
 assert.equal(editar('DADOS_INVOC',2,268,13,270),true);assert.equal(writes.length,36);assert.ok(writes.every(w=>[268,269,270].includes(w.c)));
 assert.equal(editar('ANALISE',2948,3,2948,4),true);assert.equal(writes.length,2);assert.equal(writes[0].value,"'INVOCAÇÕES'!Q226");
 assert.equal(editar('ANALISE',2948,1,2948,4),true);assert.equal(writes.length,4);assert.equal(writes[0].value,'invocacao.1.exp.acerto');
 assert.equal(loads,1);
 const abas=[{nome:'DADOS_INVOC',vals:plano.filter(d=>d.aba==='DADOS_INVOC'&&d.r===2).map(d=>[d.r,d.c,d.antes,2]),abaixo:[[2,239,13,268],[2,270,13,270]]},{nome:'ANALISE',vals:plano.filter(d=>d.aba==='ANALISE').map(d=>[d.r,d.c,d.antes,0])},{nome:'INVOCAÇÕES',vals:[],notas:[]}];
 const before=structuredClone(abas),broken=structuredClone(abas);broken[1].vals[4][2]='outro';assert.throws(()=>ctx.r53AjustarExpansao_(broken));assert.deepEqual(broken[0],before[0]);
 ctx.r53AjustarExpansao_(abas);
 for(const d of plano){const a=abas.find(a=>a.nome===d.aba);assert.equal(a.vals.find(v=>v[0]===d.r&&v[1]===d.c)[2],d.depois);}
 for(const d of notas)assert.equal(abas[2].notas.find(v=>v[0]===d.a1)[1],d.depois);
 assert.deepEqual(JSON.parse(JSON.stringify(abas[0].abaixo)),[[2,240,13,267]]);
 const after=JSON.stringify(abas);ctx.r53AjustarExpansao_(abas);assert.equal(JSON.stringify(abas),after);
 const semAnalise=structuredClone(before).filter(a=>a.nome!=='ANALISE');assert.throws(()=>ctx.r53AjustarExpansao_(semAnalise),/ANALISE/);ctx.r53AjustarExpansao_(semAnalise,true);assert.equal(semAnalise.length,2);assert.equal(semAnalise[0].vals.find(v=>v[0]===13&&v[1]===270)[2],plano.find(d=>d.aba==='DADOS_INVOC'&&d.r===13&&d.c===270).depois);
}
assert.equal(rt.gerar(),fs.readFileSync('apps-script/ExpansaoDomada.gs','utf8'));
if(process.argv[2]){const src=fs.readFileSync(process.argv[2],'utf8'),out=p.prepararCodigo(src);new vm.Script(out);assert.throws(()=>p.prepararCodigo(out),/PR85/);assert.equal(out.replace(rt.gerar(),'').replace('\n try { r53AjustarExpansao_(R53_MODULO_.__estado().abas,true); } catch(err) { R53_MODULO_=null; throw err; }','').replace('if(r53ExpansaoRestaurar_(e))return r53ContinuarPaletaPendente_(e);','').trimEnd(),src.trimEnd());}
console.log(JSON.stringify({resultado:'OK',alvos:48,locales:2,escopo:'planejamento, reversão, recuperação focal/mista, sobreposição idempotente e transporte'}));
