'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),z=require('node:zlib'),crypto=require('node:crypto'),path=require('node:path');
const p=require('../diagnostico-android/preparar_criacao_nivel_fixo'),rt=require('../criacao_nivel_fixo_runtime'),{formulaLocal}=require('../diagnostico-android/preparar_pilha_5156');
assert.equal(p.plano().length,13);assert.equal(p.notas().length,3);assert.throws(()=>p.prepararCodigo('outra base'),/PR88/);
assert.equal(rt.gerar(),fs.readFileSync('apps-script/CriacaoNivelFixo.gs','utf8'),'Runtime gerado corresponde à fonte atual');
for(const locale of ['pt_BR','en_US']){
 const local=v=>typeof v==='string'&&v.startsWith('=')?formulaLocal(v,locale):v;
 const snap={locale,cells:p.plano().map(d=>({...d,sheetId:9,value:local(d.antes)}))},prepared=p.prepararCelulas(snap);assert.equal(prepared.pedidos.length,13);assert.equal(prepared.reverter(prepared.final).length,13);
 for(const mutate of [s=>s.cells.pop(),s=>s.cells[0]=s.cells[1],s=>s.cells[0].value='não substituir',s=>s.locale='xx',s=>s.cells[0].sheetId=null]){const bad=structuredClone(snap);mutate(bad);assert.throws(()=>p.prepararCelulas(bad));}
 const bad=structuredClone(prepared.final);bad.cells[0].value='edição posterior';assert.throws(()=>prepared.reverter(bad));
 const notes=p.notas().map(d=>({...d,sheetId:8,note:d.antes}));assert.equal(p.prepararNotas(notes).length,3);notes[0].note='edição posterior';assert.throws(()=>p.prepararNotas(notes));
 const writes=[],c=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()})},r53CargaFormulaNoIdioma_:formulaLocal});vm.runInContext(rt.gerar(),c);
 const event=(r,rr,col,cc,name='DADOS_INVOC')=>({range:{getRow:()=>r,getLastRow:()=>rr,getColumn:()=>col,getLastColumn:()=>cc,getSheet:()=>({getName:()=>name,getParent:()=>({getSpreadsheetLocale:()=>locale}),getRange:(r,c)=>({setValues:rows=>rows.forEach((row,i)=>writes.push([r+i,c,row[0]]))})})}});
 for(const [r,rr,col,cc,n]of [[2,13,171,171,12],[2,3,170,172,6],[12,13,170,172,6],[5,5,68,69,2],[2,3,169,173,10]]){writes.length=0;assert.equal(c.r53CriacaoRestaurar_(event(r,rr,col,cc)),true);assert.equal(writes.length,n);for(const d of p.plano().filter(d=>d.r>=r&&d.r<=rr&&d.c>=col&&d.c<=cc))assert.ok(writes.some(x=>x[0]===d.r&&x[1]===d.c&&x[2]===local(d.depois)));}
 writes.length=0;assert.equal(c.r53CriacaoRestaurar_(event(2,2,169,174)),false);assert.equal(writes.length,5,'Bloco maior continua no editor histórico');assert.equal(c.r53CriacaoRestaurar_(event(2,13,171,171,'FICHA')),false);
 // Retrato compacto, idempotência e recusa atômica de notas/valores divergentes.
 const fixture=()=>[{nome:'DADOS_INVOC',vals:p.plano().filter(d=>d.r===2||d.c!==171).map(d=>[d.r,d.c,d.antes,7]),abaixo:[[2,170,13,172]]},{nome:'INVOCAÇÕES',vals:[],notas:p.notas().map(d=>[d.a1,d.antes])}];
 const tabs=fixture();c.r53AjustarCriacao_(tabs);for(const d of p.plano())assert.equal(tabs[0].vals.find(v=>v[0]===d.r&&v[1]===d.c)[2],d.depois);assert.deepEqual(JSON.parse(JSON.stringify(tabs[0].abaixo)),[[2,170,13,170],[2,172,13,172]]);const once=JSON.stringify(tabs);c.r53AjustarCriacao_(tabs);assert.equal(JSON.stringify(tabs),once);
 for(const mutate of [a=>a[1].notas[2][1]='nota divergente',a=>a[0].vals[0][2]='valor divergente',a=>a[0].abaixo[0][2]=12,a=>a[0].vals.push(a[0].vals[0])]){const bad=fixture();mutate(bad);const before=JSON.stringify(bad);assert.throws(()=>c.r53AjustarCriacao_(bad));assert.equal(JSON.stringify(bad),before);}
}
if(process.argv[2]){
 const src=fs.readFileSync(process.argv[2],'utf8'),out=p.prepararCodigo(src);new Function(out);assert.throws(()=>p.prepararCodigo(out),/PR88/);
 const utilities={base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()}),computeDigest:(_,s)=>Array.from(crypto.createHash('sha256').update(s).digest()),DigestAlgorithm:{SHA_256:1},Charset:{UTF_8:1}};
 const c=vm.createContext({Utilities:utilities});vm.runInContext(out,c);
 if(process.argv[3]){for(const n of ['Ficha','Invocacoes','Analise','Configuracao','Origens'])vm.runInContext(fs.readFileSync(path.join(process.argv[3],'qa-era-'+n+'.gs'),'utf8'),c);const s=c.r53Modulo_().__estado();assert.equal(s.sobras.length,0);for(const d of p.plano()){const a=s.abas.find(a=>a.nome===d.aba);assert.equal(a.vals.find(v=>v[0]===d.r&&v[1]===d.c)[2],d.depois);}for(const d of p.notas()){const a=s.abas.find(a=>a.nome===d.aba);assert.equal(a.notas.find(v=>v[0]===d.a1)[1],d.depois);}}
}
console.log(JSON.stringify({resultado:'OK',valores:13,notas:3,locales:2,escopo:'snapshot, reversão, recuperação focal/mista, retrato e recusa atômica'}));
