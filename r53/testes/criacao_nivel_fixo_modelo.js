'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),z=require('node:zlib');
const {ler,expandir}=require('./expansao_domada_modelo'),p=require('../diagnostico-android/preparar_criacao_nivel_fixo'),rt=require('../criacao_nivel_fixo_runtime');
function comparar(pasta){
 const antes=ler(pasta),depois=ler('apps-script'),allowed=new Map(p.plano().map(d=>[d.aba+'!'+d.r+':'+d.c,d])),seen=new Set();let posicoes=0,notas=0;
 assert.equal(antes.length,depois.length);
 for(const a of antes){const b=depois.find(b=>b.nome===a.nome);assert.ok(b);const meta=x=>Object.fromEntries(Object.entries(x).filter(([k])=>!['vals','abaixo','notas','geracao'].includes(k)));assert.deepEqual(meta(b),meta(a),'Metadados '+a.nome);
  const v=expandir(a),w=expandir(b);for(const k of new Set([...v.keys(),...w.keys()])){posicoes++;if(v.get(k)===w.get(k))continue;const d=allowed.get(a.nome+'!'+k);assert.ok(d,'Fora do delta '+a.nome+'!'+k);assert.equal(v.get(k),d.antes);assert.equal(w.get(k),d.depois);seen.add(a.nome+'!'+k);}
  for(const d of require('../diagnostico-android/criacao_nivel_fixo_suporte.json').filter(d=>d.aba===a.nome))assert.equal(v.get(d.r+':'+d.c),d.depois,'Molde vizinho inalterado');
  const na=new Map(a.notas||[]),nb=new Map(b.notas||[]);for(const k of new Set([...na.keys(),...nb.keys()])){const d=p.notas().find(d=>d.aba===a.nome&&d.a1===k);if(d){assert.equal(na.get(k),d.antes);assert.equal(nb.get(k),d.depois);notas++;}else assert.equal(nb.get(k),na.get(k),'Nota '+a.nome+'!'+k);}
 }
 assert.deepEqual(seen,new Set(allowed.keys()));assert.equal(notas,3);
 const patched=structuredClone(antes),c=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()})}});vm.runInContext(rt.gerar(),c);c.r53AjustarCriacao_(patched);c.r53AjustarCriacao_(patched);
 for(const a of patched){const b=depois.find(b=>b.nome===a.nome);assert.deepEqual([...expandir(a)].sort(),[...expandir(b)].sort(),a.nome+' incremental/integral');assert.deepEqual(JSON.parse(JSON.stringify([...(a.notas||[])].sort())),[...(b.notas||[])].sort(),a.nome+' notas');}
 const atual=structuredClone(depois),serializado=JSON.stringify(atual);c.r53AjustarCriacao_(atual);assert.equal(JSON.stringify(atual),serializado,'Bootstrap conserva a representação compacta da geração atual');
 return {resultado:'OK',abas:antes.length,posicoes,valores:seen.size,notas,retratoIncrementalComparado:true};
}
if(require.main===module){if(!process.argv[2])throw Error('Informe a base privada');console.log(JSON.stringify(comparar(process.argv[2])));}
module.exports={comparar};
