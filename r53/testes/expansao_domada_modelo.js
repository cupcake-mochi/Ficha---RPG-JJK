'use strict';
// Comparação integral opcional contra artefatos públicos anteriores, fora do Git.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const {deslocaFormula}=require('../../medidas/sheets-de-mentira');
const rt=require('../expansao_domada_runtime');
const deltas=require('../diagnostico-android/expansao_domada_plano.json');
const notas=require('../diagnostico-android/expansao_domada_notas.json');
function ler(pasta){
 const c=vm.createContext({});
 const skip=new Set(['Ficha.gs','Codigo.gs','Habilidades.gs','Salarios.gs','PaletaAndroid.gs','Caminho.gs','CuraRecebida.gs','Socorro.gs','Descanso.gs','ReservaBolsa.gs','PraticaCotidiana.gs','ExpansaoDomada.gs']);
 const names=['Ficha.gs',...fs.readdirSync(pasta).filter(n=>n.endsWith('.gs')&&!skip.has(n)).sort(),'Habilidades.gs','Codigo.gs'];
 vm.runInContext(names.map(n=>fs.readFileSync(path.join(pasta,n),'utf8')).join('\n'),c);
 assert.deepEqual(Array.from(c.SOBRAS_),[]);
 return JSON.parse(JSON.stringify(c.ABAS));
}
function expandir(a){const m=new Map(a.vals.map(([r,c,v])=>[r+':'+c,v]));for(const [r,c,rr,cc]of a.abaixo||[])for(let col=c;col<=cc;col++){const v=m.get(r+':'+col);if(typeof v!=='string'||!v.startsWith('='))continue;for(let row=r+1;row<=rr;row++)if(!m.has(row+':'+col))m.set(row+':'+col,deslocaFormula(v,row-r,0));}return m;}
function comparar(antes,depois){
 const allowed=new Map(deltas.map(d=>[d.aba+'!'+d.r+':'+d.c,d])),seen=new Set();let count=0;
 assert.equal(antes.length,depois.length);
 for(let i=0;i<antes.length;i++){
  const a=antes[i],b=depois[i];const {vals:av,abaixo:aa,geracao:ag,notas:an,...ma}=a,{vals:bv,abaixo:ba,geracao:bg,notas:bn,...mb}=b;
  assert.deepEqual(mb,ma,'Metadados '+a.nome);
  const na=new Map(an||[]),nb=new Map(bn||[]),keys=new Set([...na.keys(),...nb.keys()]);
  for(const k of keys){const n=notas.find(d=>d.aba===a.nome&&d.a1===k);if(n){assert.equal(na.get(k)??null,n.antes);assert.equal(nb.get(k),n.depois);}else assert.equal(nb.get(k),na.get(k),'Nota '+a.nome+'!'+k);}
  const v=expandir(a),w=expandir(b);for(const k of new Set([...v.keys(),...w.keys()])){count++;if(JSON.stringify(v.get(k))===JSON.stringify(w.get(k)))continue;const key=a.nome+'!'+k,d=allowed.get(key);assert.ok(d,'Fora do delta '+key);assert.equal(v.get(k),d.antes);assert.equal(w.get(k),d.depois);seen.add(key);}
 }
 assert.deepEqual(seen,new Set(allowed.keys()));return count;
}
if(require.main===module){
 if(!process.argv[2])throw Error('Informe a pasta privada de fontes públicas anteriores');
 const antes=ler(process.argv[2]),depois=ler('apps-script'),positions=comparar(antes,depois);
 // Exercita o mesmo retrato incrementado que será consultado pelo editor antigo.
 const patched=structuredClone(antes);const z=require('node:zlib');const c=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()})}});vm.runInContext(rt.gerar(),c);c.r53AjustarExpansao_(patched);
 for(const a of patched){const b=depois.find(b=>b.nome===a.nome);assert.deepEqual([...expandir(a)].sort(),[...expandir(b)].sort(),a.nome);assert.deepEqual(JSON.parse(JSON.stringify([...(a.notas||[])].sort())),[...(b.notas||[])].sort(),'Notas '+a.nome);}
 console.log(JSON.stringify({resultado:'OK',abas:antes.length,posicoes:positions,valoresAlterados:48,notasAlteradas:36,instalacaoIntegralComparada:true,retratoIncrementalComparado:true}));
}
module.exports={ler,expandir,comparar};
