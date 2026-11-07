'use strict';
const assert=require('node:assert/strict');
const {ler,expandir}=require('./expansao_domada_modelo');
const plano=require('../diagnostico-android/repertorio_normal_plano.json');
function comparar(pasta){
 const antes=ler(pasta),depois=ler('apps-script'),allowed=new Map(plano.map(d=>[d.aba+'!'+d.r+':'+d.c,d])),seen=new Set();let posicoes=0;
 assert.equal(antes.length,depois.length);
 for(const a of antes){const b=depois.find(b=>b.nome===a.nome);assert.ok(b);const meta=x=>Object.fromEntries(Object.entries(x).filter(([k])=>!['vals','abaixo','geracao'].includes(k)));assert.deepEqual(meta(b),meta(a),'Metadados '+a.nome);
  const v=expandir(a),w=expandir(b);for(const k of new Set([...v.keys(),...w.keys()])){posicoes++;if(v.get(k)===w.get(k))continue;const key=a.nome+'!'+k,d=allowed.get(key);assert.ok(d,'Fora do delta '+key);assert.equal(v.get(k),d.antes);assert.equal(w.get(k),d.depois);seen.add(key);}
  if(a.nome==='DADOS_INVOC'){const suporte=require('../diagnostico-android/expansao_domada_suporte.json').filter(d=>d.aba===a.nome&&d.c===240);assert.equal(suporte.length,12);for(const d of suporte){assert.equal(v.get(d.r+':'+d.c),d.depois);assert.equal(w.get(d.r+':'+d.c),d.depois);}}
 }
 assert.deepEqual(seen,new Set(allowed.keys()));return {resultado:'OK',abas:antes.length,posicoes,alteracoes:24,metadadosPreservados:true};
}
if(require.main===module){if(!process.argv[2])throw Error('Informe as fontes privadas da PR87');console.log(JSON.stringify(comparar(process.argv[2])));}
module.exports={comparar};
