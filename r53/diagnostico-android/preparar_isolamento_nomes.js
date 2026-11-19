'use strict';
// Incremental sobre a primeira entrega da PR88; mantém erros na origem.
const fs=require('node:fs');
const {sha,trocar}=require('./preparar_recursos_fila');
const {formulaLocal}=require('./preparar_pilha_5156');
const {norm}=require('./preparar_pratica_cotidiana');
const rt=require('../expansao_domada_runtime');
const base='8935211c6e87cd4515b0df860bd0d71524f316d08e42013f86cc9fa6b1d53bea';
const plano=()=>require('./isolamento_nomes_plano.json');
const key=d=>JSON.stringify([d.aba,d.r,d.c]);
function planoAnterior(){const index=new Map(plano().map(d=>[key(d),d]));return require('./expansao_domada_plano.json').map(d=>{const x=index.get(key(d));if(x&&x.depois!==d.depois)throw Error('Plano de isolamento divergente');return x?{...d,depois:x.antes}:d;});}
function runtimeAnterior(){return rt.gerar(planoAnterior());}
function prepararCodigo(src){if(sha(src)!==base)throw Error('Código exige a primeira versão ensaiada da PR88');return trocar(src,runtimeAnterior(),rt.gerar());}
function prepararCelulas(snapshot){
 const {locale,cells}=snapshot??{};
 if(!['pt_BR','en_US'].includes(locale)||!Array.isArray(cells)||cells.length!==24)throw Error('Snapshot atual de 24 fórmulas obrigatório');
 const index=new Map(cells.map(d=>[key(d),d]));if(index.size!==24)throw Error('Alvo duplicado');
 const deltas=plano().map(d=>{const x=index.get(key(d));if(!x||!Number.isInteger(x.sheetId)||norm(x.value)!==norm(formulaLocal(d.antes,locale)))throw Error('Célula anterior divergente: '+key(d));return {...x,antes:x.value,depois:norm(formulaLocal(d.depois,locale))};});
 const pedidos=(k)=>deltas.map(d=>({updateCells:{start:{sheetId:d.sheetId,rowIndex:d.r-1,columnIndex:d.c-1},rows:[{values:[{userEnteredValue:{formulaValue:d[k]}}]}],fields:'userEnteredValue'}}));
 return {pedidos:pedidos('depois'),final:{locale,cells:deltas.map(d=>({aba:d.aba,r:d.r,c:d.c,sheetId:d.sheetId,value:d.depois}))},reverter(atual){
  if(atual?.locale!==locale||!Array.isArray(atual.cells)||atual.cells.length!==24)throw Error('Snapshot de reversão divergente');const idx=new Map(atual.cells.map(d=>[key(d),d]));if(idx.size!==24)throw Error('Alvo de reversão duplicado');
  for(const d of deltas){const x=idx.get(key(d));if(!x||x.sheetId!==d.sheetId||norm(x.value)!==d.depois)throw Error('Célula divergente na reversão');}return pedidos('antes');
 }};
}
module.exports={base,plano,planoAnterior,runtimeAnterior,prepararCodigo,prepararCelulas};
if(require.main===module){const [input,output]=process.argv.slice(2);if(!input||!output)throw Error('Informe código atual e proposta privados');const src=fs.readFileSync(input,'utf8'),out=prepararCodigo(src);new Function(out);fs.writeFileSync(output,out);console.log(JSON.stringify({antes:sha(src),depois:sha(out),alvos:24,aplicado:false}));}
