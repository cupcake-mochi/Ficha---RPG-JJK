'use strict';
const fs=require('node:fs');
const {sha,trocar}=require('./preparar_recursos_fila');
const {formulaLocal}=require('./preparar_pilha_5156');
const {norm}=require('./preparar_pratica_cotidiana');
const rt=require('../criacao_nivel_fixo_runtime');
const base='36ca73efd1eca6809fd8ddfa1be324eebaad2f5aef0830d4c25c6aaeaaaff3bc';
const plano=()=>require('./criacao_nivel_fixo_plano.json');
const notas=()=>require('./criacao_nivel_fixo_notas.json');
const key=d=>JSON.stringify([d.aba,d.r,d.c]);
function prepararCodigo(src){
 if(sha(src)!==base)throw Error('Código exige a versão final ensaiada da PR88');
 let out=trocar(src,'function onEdit(e){if(e)e.r53Inicio_=Date.now();','function onEdit(e){if(e)e.r53Inicio_=Date.now();if(r53CriacaoRestaurar_(e))return r53ContinuarPaletaPendente_(e);');
 const anchor=" if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');";
 out=trocar(out,anchor," try { r53AjustarCriacao_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }\n"+anchor);
 return out+'\n'+rt.gerar();
}
function valor(v,locale){return typeof v==='string'&&v.startsWith('=')?norm(formulaLocal(v,locale)):v;}
function userValue(v){return typeof v==='number'?{numberValue:v}:typeof v==='string'&&v.startsWith('=')?{formulaValue:v}:{stringValue:v};}
function prepararCelulas(snapshot){
 const {locale,cells}=snapshot??{};
 if(!['pt_BR','en_US'].includes(locale)||!Array.isArray(cells)||cells.length!==plano().length)throw Error('Snapshot atual de valores obrigatório');
 const idx=new Map(cells.map(d=>[key(d),d]));if(idx.size!==cells.length)throw Error('Alvo duplicado');
 const deltas=plano().map(d=>{const x=idx.get(key(d));if(!x||!Number.isInteger(x.sheetId)||valor(x.value,locale)!==valor(d.antes,locale))throw Error('Célula anterior divergente: '+key(d));return {...x,antes:x.value,depois:valor(d.depois,locale)};});
 const pedidos=k=>deltas.map(d=>({updateCells:{start:{sheetId:d.sheetId,rowIndex:d.r-1,columnIndex:d.c-1},rows:[{values:[{userEnteredValue:userValue(d[k])}]}],fields:'userEnteredValue'}}));
 return {pedidos:pedidos('depois'),final:{locale,cells:deltas.map(d=>({aba:d.aba,r:d.r,c:d.c,sheetId:d.sheetId,value:d.depois}))},reverter(atual){if(atual?.locale!==locale||!Array.isArray(atual.cells)||atual.cells.length!==deltas.length)throw Error('Snapshot de reversão divergente');const by=new Map(atual.cells.map(d=>[key(d),d]));if(by.size!==deltas.length)throw Error('Alvo de reversão duplicado');for(const d of deltas){const x=by.get(key(d));if(!x||x.sheetId!==d.sheetId||valor(x.value,locale)!==d.depois)throw Error('Célula divergente na reversão');}return pedidos('antes');}};
}
function prepararNotas(cells){
 if(!Array.isArray(cells)||cells.length!==notas().length||new Set(cells.map(x=>x.aba+'!'+x.a1)).size!==cells.length)throw Error('Snapshot atual de notas obrigatório');
 return notas().map(d=>{const x=cells.find(x=>x.aba===d.aba&&x.a1===d.a1);if(!x||!Number.isInteger(x.sheetId)||x.note!==d.antes)throw Error('Nota anterior divergente');const m=/^([A-Z]+)(\d+)$/.exec(d.a1),c=[...m[1]].reduce((n,l)=>26*n+l.charCodeAt(0)-64,0);return {updateCells:{start:{sheetId:x.sheetId,rowIndex:+m[2]-1,columnIndex:c-1},rows:[{values:[{note:d.depois}]}],fields:'note'}};});
}
module.exports={base,plano,notas,prepararCodigo,prepararCelulas,prepararNotas};
if(require.main===module){const [input,output]=process.argv.slice(2);if(!input||!output)throw Error('Informe código atual e proposta privados');const src=fs.readFileSync(input,'utf8'),out=prepararCodigo(src);new Function(out);fs.writeFileSync(output,out);console.log(JSON.stringify({antes:sha(src),depois:sha(out),alvos:plano().length,notas:notas().length,aplicado:false}));}
