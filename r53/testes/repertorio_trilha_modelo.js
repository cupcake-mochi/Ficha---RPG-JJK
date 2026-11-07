'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),z=require('node:zlib');
const {ler,expandir}=require('./expansao_domada_modelo');
const rt=require('../repertorio_trilha_runtime'),deltas=require('../diagnostico-android/repertorio_trilha_plano.json'),notas=require('../diagnostico-android/repertorio_trilha_notas.json');
function comparar(pasta){
 const antes=ler(pasta),depois=ler('apps-script');
 const allowed=new Map(deltas.map(d=>[d.aba+'!'+d.r+':'+d.c,d])),seen=new Set();let positions=0;
 const norm=v=>v===''||v===undefined?null:v;
 for(const a of antes){const b=depois.find(b=>b.nome===a.nome);assert.ok(b);const v=expandir(a),w=expandir(b);
  for(const k of new Set([...v.keys(),...w.keys()])){positions++;if(norm(v.get(k))===norm(w.get(k)))continue;const key=a.nome+'!'+k,d=allowed.get(key);assert.ok(d,'Fora do delta '+key);assert.equal(norm(v.get(k)),d.antes);assert.equal(w.get(k),d.depois);seen.add(key);}
  const na=new Map(a.notas||[]),nb=new Map(b.notas||[]);for(const k of new Set([...na.keys(),...nb.keys()])){const d=notas.find(d=>d.aba===a.nome&&d.a1===k);if(d){assert.equal(na.get(k)??null,d.antes);assert.equal(nb.get(k),d.depois);}else assert.equal(nb.get(k),na.get(k),a.nome+' nota '+k);}
  const exclude=new Set(['vals','abaixo','geracao','notas']);if(a.nome==='INVOCAÇÕES')for(const k of ['estilos','fundos','bordas','merges','dv','alturas'])exclude.add(k);
  const metadata=s=>Object.fromEntries(Object.entries(s).filter(([k])=>!exclude.has(k)));assert.deepEqual(metadata(b),metadata(a),a.nome+' metadados');
  if(a.nome==='INVOCAÇÕES'){
   const extra=b.merges.filter(x=>!a.merges.some(y=>JSON.stringify(x)===JSON.stringify(y)));assert.deepEqual(extra.sort(),[[34,4,34,6],[35,4,36,6],[37,4,39,6]].sort());assert.equal(b.merges.length,a.merges.length+3);
   assert.deepEqual(b.dv.filter(x=>x[0]!=='D35'),a.dv);assert.deepEqual(b.dv.find(x=>x[0]==='D35'),['D35','DADOS_INVOC!$CY$2:$CY$3']);
   const oldStyles=new Map(a.vals.filter(x=>x.length>3).map(x=>[x[0]+':'+x[1],a.estilos[x[3]]]));for(const x of b.vals){if(x[0]>=34&&x[0]<=39&&x[1]>=4&&x[1]<=6)continue;if(x.length>3)assert.deepEqual(b.estilos[x[3]],oldStyles.get(x[0]+':'+x[1]),'estilo fora do seletor');}
  }
 }
 assert.deepEqual(seen,new Set(allowed.keys()));
 const patched=structuredClone(antes),c=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()})}});vm.runInContext(rt.gerar(),c);c.r53AjustarRepertorio_(patched);c.r53AjustarRepertorio_(patched);
 for(const a of patched){const b=depois.find(b=>b.nome===a.nome),v=expandir(a),w=expandir(b);for(const k of new Set([...v.keys(),...w.keys()]))assert.equal(norm(v.get(k)),norm(w.get(k)),a.nome+' retrato '+k);assert.deepEqual(JSON.parse(JSON.stringify([...(a.notas||[])].sort())),[...(b.notas||[])].sort());}
 const bad=structuredClone(antes),target=bad.find(a=>a.nome==='INVOCAÇÕES').vals.find(x=>x[0]===170&&x[1]===9);target[2]='entrada divergente';const copy=JSON.stringify(bad);assert.throws(()=>c.r53AjustarRepertorio_(bad));assert.equal(JSON.stringify(bad),copy,'pré-condições devem anteceder mutações');
 return {resultado:'OK',abas:antes.length,posicoes:positions,valoresAlterados:102,notasAlteradas:14,seletorNovo:true,retratoIncrementalComparado:true};
}
if(require.main===module){if(!process.argv[2])throw Error('Informe a pasta privada de fontes anteriores');console.log(JSON.stringify(comparar(process.argv[2])));}
module.exports={comparar};
