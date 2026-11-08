'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),z=require('node:zlib'),crypto=require('node:crypto'),path=require('node:path');
const p=require('../diagnostico-android/preparar_contagem_especiais'),rt=require('../expansao_domada_runtime');
const {formulaLocal}=require('../diagnostico-android/preparar_pilha_5156');
const plano=p.plano();assert.equal(plano.length,24);
for(const d of plano){assert.equal(d.aba,'DADOS_INVOC');assert.ok([239,270].includes(d.c));assert.ok(d.r>=2&&d.r<=13);const old=`COUNTIFS(DADOS_R53!$A$2:$A$253,"entidade."&$DD${d.r}&".esp.*",DADOS_R53!$B$2:$B$253,"?*")`,value=`SUMPRODUCT(N(LEN(FILTER(DADOS_R53!$B$2:$B$253,REGEXMATCH(DADOS_R53!$A$2:$A$253,"^entidade[.]"&$DD${d.r}&"[.]esp[.]"))&"")>0))`;assert.equal(d.antes.replace(old,value),d.depois);}
assert.throws(()=>p.prepararCodigo('base desconhecida'),/PR87/);
for(const locale of ['pt_BR','en_US']){
 const snap={locale,cells:plano.map(d=>({...d,sheetId:12,value:formulaLocal(d.antes,locale)}))};const pr=p.prepararCelulas(snap);
 assert.equal(pr.pedidos.length,24);assert.equal(pr.reverter(pr.final).length,24);assert.ok(pr.pedidos.every(q=>q.updateCells.fields==='userEnteredValue'));
 for(const mutate of [s=>s.cells.pop(),s=>s.cells.push(s.cells[0]),s=>s.cells[0]=s.cells[1],s=>s.locale='xx',s=>s.cells[0].sheetId=null,s=>s.cells[0].value='=FALSE']){const bad=structuredClone(snap);mutate(bad);assert.throws(()=>p.prepararCelulas(bad));}
 const bad=structuredClone(pr.final);bad.cells[0].value='edição posterior';assert.throws(()=>pr.reverter(bad));
 const writes=[],c=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()})},r53CargaFormulaNoIdioma_:formulaLocal});vm.runInContext(rt.gerar(),c);
 const event=(r,rr,col,cc)=>({range:{getRow:()=>r,getLastRow:()=>rr,getColumn:()=>col,getLastColumn:()=>cc,getSheet:()=>({getName:()=> 'DADOS_INVOC',getParent:()=>({getSpreadsheetLocale:()=>locale}),getRange:(r,c)=>({setValues:rows=>rows.forEach((row,i)=>writes.push([r+i,c,row[0]]))})})}});
 assert.equal(c.r53ExpansaoRestaurar_(event(2,13,239,239)),true);assert.equal(writes.length,12);
 assert.deepEqual(writes,plano.filter(d=>d.c===239).map(d=>[d.r,d.c,formulaLocal(d.depois,locale)]));
 writes.length=0;assert.equal(c.r53ExpansaoRestaurar_(event(2,13,268,270)),true);assert.equal(writes.length,36);
 for(const d of plano.filter(d=>d.c===270))assert.ok(writes.some(x=>x[0]===d.r&&x[1]===d.c&&x[2]===formulaLocal(d.depois,locale)));
 writes.length=0;assert.equal(c.r53ExpansaoRestaurar_(event(2,3,239,240)),true);assert.equal(writes.length,4);
 const suporte=require('../diagnostico-android/expansao_domada_suporte.json');for(const row of [2,3])assert.ok(writes.some(x=>x[0]===row&&x[1]===240&&x[2]===formulaLocal(suporte.find(d=>d.aba==='DADOS_INVOC'&&d.r===row&&d.c===240).depois,locale)));
}
if(process.argv[2]){
 const src=fs.readFileSync(process.argv[2],'utf8'),out=p.prepararCodigo(src);new Function(out);
 assert.equal(src.replace(p.runtimeAnterior(),''),out.replace(rt.gerar(),''),'Todo código fora da recuperação deve permanecer igual');
 assert.throws(()=>p.prepararCodigo(out),/PR87/);
 const utilities={base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()}),computeDigest:(_,s)=>Array.from(crypto.createHash('sha256').update(s).digest()),DigestAlgorithm:{SHA_256:1},Charset:{UTF_8:1}};
 const contexts=[src,out].map(code=>{const c=vm.createContext({Utilities:utilities});vm.runInContext(code,c);return c;});
 assert.equal(JSON.stringify(contexts[0].r53PraticaMontagem_()),JSON.stringify(contexts[1].r53PraticaMontagem_()));
 const oldSupport=JSON.parse(JSON.stringify(contexts[0].r53ExpansaoCarga_().suporte)),newSupport=JSON.parse(JSON.stringify(contexts[1].r53ExpansaoCarga_().suporte));assert.equal(oldSupport.length,48);assert.equal(newSupport.length,60);assert.deepEqual(newSupport.filter(d=>!(d.aba==='DADOS_INVOC'&&d.c===240)),oldSupport);
 const previous=JSON.parse(JSON.stringify(contexts[0].r53ExpansaoDados_())),current=JSON.parse(JSON.stringify(contexts[1].r53ExpansaoDados_()));const wanted=new Map(plano.map(d=>[d.r+':'+d.c,d]));
 assert.equal(previous.length,current.length);for(let n=0;n<previous.length;n++){const a=previous[n],b=current[n],d=wanted.get(a.r+':'+a.c);if(d&&a.aba==='DADOS_INVOC'){assert.equal(a.depois,d.antes);assert.equal(b.depois,d.depois);assert.deepEqual({...a,depois:b.depois},b);}else assert.deepEqual(a,b);}
 if(process.argv[3]){const c=contexts[1];for(const n of ['Ficha','Invocacoes','Analise','Configuracao','Origens'])vm.runInContext(fs.readFileSync(path.join(process.argv[3],'qa-era-'+n+'.gs'),'utf8'),c);const estado=c.r53Modulo_().__estado();assert.equal(estado.sobras.length,0);assert.equal(estado.abas.some(a=>['DADOS_R53','ANALISE'].includes(a.nome)),false);const a=estado.abas.find(a=>a.nome==='DADOS_INVOC');for(const d of plano)assert.equal(a.vals.find(v=>v[0]===d.r&&v[1]===d.c)[2],d.depois);}
}
console.log(JSON.stringify({resultado:'OK',alvos:24,locales:2,escopo:'snapshot, reversão, recuperação focal/mista e módulo Android legado'}));
