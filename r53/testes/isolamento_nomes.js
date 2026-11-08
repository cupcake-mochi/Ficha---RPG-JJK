'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),z=require('node:zlib'),crypto=require('node:crypto'),path=require('node:path');
const p=require('../diagnostico-android/preparar_isolamento_nomes'),rt=require('../expansao_domada_runtime'),{formulaLocal}=require('../diagnostico-android/preparar_pilha_5156');
assert.equal(p.plano().length,24);assert.throws(()=>p.prepararCodigo('outra base'),/PR88/);
assert.equal(Buffer.from(rt.gerar().match(/base64Decode\("([^"]+)"\)/)[1],'base64')[9],3,'Cabeçalho gzip igual no Windows e Linux');
for(const d of p.plano()){assert.equal(d.aba,'DADOS_INVOC');assert.ok([239,270].includes(d.c));assert.ok(d.r>=2&&d.r<=13);const old=`SUMPRODUCT(N(REGEXMATCH(DADOS_R53!$A$2:$A$253,"^entidade[.]"&$DD${d.r}&"[.]esp[.]")),N(LEN(DADOS_R53!$B$2:$B$253&"")>0))`,fixed=`SUMPRODUCT(N(LEN(FILTER(DADOS_R53!$B$2:$B$253,REGEXMATCH(DADOS_R53!$A$2:$A$253,"^entidade[.]"&$DD${d.r}&"[.]esp[.]"))&"")>0))`;assert.equal(d.antes.replace(old,fixed),d.depois);}
for(const locale of ['pt_BR','en_US']){
 const snap={locale,cells:p.plano().map(d=>({...d,sheetId:9,value:formulaLocal(d.antes,locale)}))},pr=p.prepararCelulas(snap);assert.equal(pr.pedidos.length,24);assert.equal(pr.reverter(pr.final).length,24);
 for(const mutate of [s=>s.cells.pop(),s=>s.cells[0]=s.cells[1],s=>s.cells[0].value='não substituir',s=>s.locale='xx',s=>s.cells[0].sheetId=null]){const bad=structuredClone(snap);mutate(bad);assert.throws(()=>p.prepararCelulas(bad));}
 const bad=structuredClone(pr.final);bad.cells[0].value='edição posterior';assert.throws(()=>pr.reverter(bad));
 const writes=[],c=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()})},r53CargaFormulaNoIdioma_:formulaLocal});vm.runInContext(rt.gerar(),c);
 const event=(r,rr,col,cc)=>({range:{getRow:()=>r,getLastRow:()=>rr,getColumn:()=>col,getLastColumn:()=>cc,getSheet:()=>({getName:()=> 'DADOS_INVOC',getParent:()=>({getSpreadsheetLocale:()=>locale}),getRange:(r,c)=>({setValues:rows=>rows.forEach((row,i)=>writes.push([r+i,c,row[0]]))})})}});
 assert.equal(c.r53ExpansaoRestaurar_(event(2,13,239,239)),true);assert.equal(writes.length,12);for(const d of p.plano().filter(d=>d.c===239))assert.ok(writes.some(x=>x[0]===d.r&&x[1]===d.c&&x[2]===formulaLocal(d.depois,locale)));
 writes.length=0;assert.equal(c.r53ExpansaoRestaurar_(event(2,3,239,240)),true);assert.equal(writes.length,4);assert.ok(writes.filter(x=>x[1]===239).every(x=>x[2].includes('LEN(FILTER(')));
 writes.length=0;assert.equal(c.r53ExpansaoRestaurar_(event(2,13,268,270)),true);assert.equal(writes.length,36);
}
if(process.argv[2]){
 const src=fs.readFileSync(process.argv[2],'utf8'),out=p.prepararCodigo(src);new Function(out);assert.equal(src.replace(p.runtimeAnterior(),''),out.replace(rt.gerar(),''));assert.throws(()=>p.prepararCodigo(out),/PR88/);
 const utilities={base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()}),computeDigest:(_,s)=>Array.from(crypto.createHash('sha256').update(s).digest()),DigestAlgorithm:{SHA_256:1},Charset:{UTF_8:1}};
 const contexts=[src,out].map(code=>{const c=vm.createContext({Utilities:utilities});vm.runInContext(code,c);return c;});
 for(const key of ['suporte','notas'])assert.equal(JSON.stringify(contexts[0].r53ExpansaoCarga_()[key]),JSON.stringify(contexts[1].r53ExpansaoCarga_()[key]));assert.equal(JSON.stringify(contexts[0].r53PraticaMontagem_()),JSON.stringify(contexts[1].r53PraticaMontagem_()));
 if(process.argv[3]){const c=contexts[1];for(const n of ['Ficha','Invocacoes','Analise','Configuracao','Origens'])vm.runInContext(fs.readFileSync(path.join(process.argv[3],'qa-era-'+n+'.gs'),'utf8'),c);const estado=c.r53Modulo_().__estado();assert.equal(estado.sobras.length,0);const a=estado.abas.find(a=>a.nome==='DADOS_INVOC');for(const d of p.plano())assert.equal(a.vals.find(v=>v[0]===d.r&&v[1]===d.c)[2],d.depois);}
 if(process.argv[4])assert.equal(out,require('../diagnostico-android/preparar_contagem_especiais').prepararCodigo(fs.readFileSync(process.argv[4],'utf8')),'As duas bases devem produzir o mesmo código final');
}
console.log(JSON.stringify({resultado:'OK',alvos:24,locales:2,escopo:'transporte exato, snapshots, reversão, recuperação e módulo antigo'}));
