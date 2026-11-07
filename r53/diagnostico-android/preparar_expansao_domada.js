'use strict';
// Planejamento offline. Não acessa Google nem instala o pacote integral.
const fs=require('node:fs');
const {sha,trocar}=require('./preparar_recursos_fila');
const {formulaLocal}=require('./preparar_pilha_5156');
const {norm}=require('./preparar_pratica_cotidiana');
const rt=require('../expansao_domada_runtime');
const base='7512bf622897eb1145f3849a55ccd80419a147e8cd540a3c2b6113d84c8cdfb7';
const plano=()=>require('./expansao_domada_plano.json');
function prepararCodigo(src){
 if(sha(src)!==base)throw Error('Código exige a versão ensaiada da PR85');
 const anchor=" if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');";
 let out=trocar(src,anchor," try { r53AjustarExpansao_(R53_MODULO_.__estado().abas,true); } catch(err) { R53_MODULO_=null; throw err; }\n"+anchor);
 out=trocar(out,'function onEdit(e){if(e)e.r53Inicio_=Date.now();',
  'function onEdit(e){if(e)e.r53Inicio_=Date.now();if(r53ExpansaoRestaurar_(e))return r53ContinuarPaletaPendente_(e);');
 return out+'\n'+rt.gerar();
}
const key=d=>JSON.stringify([d.aba,d.r,d.c]);
function prepararCelulas(snapshot){
 const {locale,cells}=snapshot??{};
 if(!['pt_BR','en_US'].includes(locale)||!Array.isArray(cells))throw Error('Snapshot atual obrigatório');
 const byKey=new Map(cells.map(d=>[key(d),d]));
 if(byKey.size!==48||cells.length!==48)throw Error('Cobertura do snapshot divergente');
 const deltas=plano().map(d=>{
  const x=byKey.get(key(d));
  if(!x||!Number.isInteger(x.sheetId)||norm(x.value)!==norm(formulaLocal(d.antes,locale)))throw Error('Célula anterior divergente: '+key(d));
  return {...x,antes:x.value,depois:norm(formulaLocal(d.depois,locale))};
 });
 function pedidos(data,campo){return data.map(d=>({updateCells:{start:{sheetId:d.sheetId,rowIndex:d.r-1,columnIndex:d.c-1},rows:[{values:[{userEnteredValue:d[campo].startsWith('=')?{formulaValue:d[campo]}:{stringValue:d[campo]}}]}],fields:'userEnteredValue'}}));}
 const final={locale,cells:deltas.map(d=>({aba:d.aba,r:d.r,c:d.c,sheetId:d.sheetId,value:d.depois}))};
 return {pedidos:pedidos(deltas,'depois'),final,reverter(atual){
  if(atual?.locale!==locale||!Array.isArray(atual.cells)||atual.cells.length!==48||new Set(atual.cells.map(key)).size!==48)throw Error('Snapshot de reversão divergente');
  const index=new Map(atual.cells.map(d=>[key(d),d]));
  for(const d of deltas){const x=index.get(key(d));if(!x||x.sheetId!==d.sheetId||norm(x.value)!==d.depois)throw Error('Célula divergente na reversão');}
  return pedidos(deltas,'antes');
 }};
}
function prepararNotas(cells){
 const deltas=require('./expansao_domada_notas.json');
 if(!Array.isArray(cells)||cells.length!==36||new Set(cells.map(x=>x.a1)).size!==36)throw Error('Snapshot de notas divergente');
 return deltas.map(d=>{const x=cells.find(x=>x.aba===d.aba&&x.a1===d.a1);if(!x||!Number.isInteger(x.sheetId)||(x.note??null)!==d.antes)throw Error('Nota anterior divergente: '+d.a1);const m=/^([A-Z]+)(\d+)$/.exec(d.a1),c=[...m[1]].reduce((s,v)=>26*s+v.charCodeAt(0)-64,0);return {updateCells:{start:{sheetId:x.sheetId,rowIndex:+m[2]-1,columnIndex:c-1},rows:[{values:[{note:d.depois}]}],fields:'note'}};});
}
module.exports={base,plano,prepararCodigo,prepararCelulas,prepararNotas};
if(require.main===module){const [input,output]=process.argv.slice(2);if(!input||!output)throw Error('Informe snapshot e proposta privados');const src=fs.readFileSync(input,'utf8'),out=prepararCodigo(src);new Function(out);fs.writeFileSync(output,out);console.log(JSON.stringify({antes:sha(src),depois:sha(out),alvos:plano().length,aplicado:false}));}
