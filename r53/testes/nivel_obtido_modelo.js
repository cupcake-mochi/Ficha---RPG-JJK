'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),z=require('node:zlib');
const {ler,expandir}=require('./expansao_domada_modelo'),p=require('../diagnostico-android/preparar_nivel_obtido'),rt=require('../nivel_obtido_runtime');
function comparar(pasta){
 const antes=ler(pasta),depois=ler('apps-script'),allowed=new Map(p.plano().map(d=>[d.aba+'!'+d.r+':'+d.c,d])),seen=new Set();let posicoes=0,notas=0,validacoes=0;
 for(const a of antes){
  const b=depois.find(b=>b.nome===a.nome);assert.ok(b);
  const meta=x=>Object.fromEntries(Object.entries(x).filter(([k])=>!['vals','abaixo','notas','dv','geracao','menus_estritos'].includes(k)));assert.deepEqual(meta(b),meta(a),'Metadados '+a.nome);
  const targets=p.validacoes().filter(d=>d.aba===a.nome).map(d=>d.a1);assert.deepEqual([...(b.menus_estritos||[])].sort(),[...(a.menus_estritos||[]),...targets].sort(),'Menus estritos '+a.nome);
  const v=expandir(a),w=expandir(b);for(const k of new Set([...v.keys(),...w.keys()])){posicoes++;if(v.get(k)===w.get(k))continue;const d=allowed.get(a.nome+'!'+k);assert.ok(d,'Fora do delta '+a.nome+'!'+k);assert.equal(v.get(k),d.antes);assert.equal(w.get(k),d.depois);seen.add(a.nome+'!'+k);}
  for(const d of require('../diagnostico-android/nivel_obtido_suporte.json').filter(d=>d.aba===a.nome))assert.equal(v.get(d.r+':'+d.c),d.depois);
  const na=new Map(a.notas||[]),nb=new Map(b.notas||[]);for(const k of new Set([...na.keys(),...nb.keys()])){const d=p.notas().find(d=>d.aba===a.nome&&d.a1===k);if(d){assert.equal(na.get(k),d.antes);assert.equal(nb.get(k),d.depois);notas++;}else assert.equal(nb.get(k),na.get(k),'Nota '+a.nome+'!'+k);}
  const da=new Map(a.dv||[]),db=new Map(b.dv||[]);for(const k of new Set([...da.keys(),...db.keys()])){const d=p.validacoes().find(d=>d.aba===a.nome&&d.a1===k);if(d){assert.equal(da.get(k),undefined);assert.equal(db.get(k),'"'+d.depois.condition.values.map(x=>x.userEnteredValue).join(',')+'"');validacoes++;}else assert.equal(db.get(k),da.get(k),'Validação '+a.nome+'!'+k);}
 }
 assert.deepEqual(seen,new Set(allowed.keys()));assert.equal(notas,2);assert.equal(validacoes,12);
 const patched=structuredClone(antes),c=vm.createContext({Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>z.gunzipSync(x).toString()})}});vm.runInContext(rt.gerar(),c);c.r53AjustarNivel_(patched);c.r53AjustarNivel_(patched);
 for(const a of patched){const b=depois.find(b=>b.nome===a.nome);assert.deepEqual([...expandir(a)].sort(),[...expandir(b)].sort(),a.nome+' incremental/integral');assert.deepEqual([...(a.menus_estritos||[])].sort(),[...(b.menus_estritos||[])].sort(),a.nome+' menus estritos');for(const key of ['notas','dv'])assert.deepEqual(JSON.parse(JSON.stringify([...(a[key]||[])].sort())),[...(b[key]||[])].sort(),a.nome+' '+key);}
 const atual=structuredClone(depois),s=JSON.stringify(atual);c.r53AjustarNivel_(atual);assert.equal(JSON.stringify(atual),s,'Bootstrap conserva geração atual');
 return {resultado:'OK',abas:antes.length,posicoes,valores:seen.size,notas,validacoes,retratoIncrementalComparado:true};
}
if(require.main===module)console.log(JSON.stringify(comparar(process.argv[2])));
module.exports={comparar};

