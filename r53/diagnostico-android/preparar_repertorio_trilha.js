'use strict';
// Preparação offline para a base ensaiada; nunca constrói uma ficha preenchida.
const fs=require('node:fs');
const {sha,trocar}=require('./preparar_recursos_fila');
const {formulaLocal}=require('./preparar_pilha_5156');
const {norm}=require('./preparar_pratica_cotidiana');
const rt=require('../repertorio_trilha_runtime');
const pratica=require('../pratica_cotidiana_runtime');
const {blocoMontagens}=require('./preparar_fragil_fica');
const base='5b7bb420739efeeb28e036b8da79f38bcc0e19b20d4d14f229f0effaac74e7ef';
const plano=()=>require('./repertorio_trilha_plano.json');
const notas=()=>require('./repertorio_trilha_notas.json');
const key=d=>JSON.stringify([d.aba,d.r,d.c]);
function prepararCodigo(src){
 if(sha(src)!==base)throw Error('Código exige a versão ensaiada da PR86');
 const anchor=" if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');";
 let out=trocar(src,anchor," try { r53AjustarRepertorio_(R53_MODULO_.__estado().abas,true); } catch(err) { R53_MODULO_=null; throw err; }\n"+anchor);
 out=trocar(out,blocoMontagens(out),blocoMontagens(pratica.gerar()));
 out=trocar(out,'function onEdit(e){if(e)e.r53Inicio_=Date.now();','function onEdit(e){if(e)e.r53Inicio_=Date.now();if(r53RepertorioRestaurar_(e)||r53RepertorioEntrada_(e))return r53ContinuarPaletaPendente_(e);');
 return out+'\n'+rt.gerar();
}
function prepararCelulas(snapshot){
 const {locale,cells}=snapshot??{};
 if(!['pt_BR','en_US'].includes(locale)||!Array.isArray(cells)||cells.length!==plano().length)throw Error('Snapshot atual obrigatório');
 const byKey=new Map(cells.map(d=>[key(d),d]));if(byKey.size!==cells.length)throw Error('Alvo duplicado');
 const deltas=plano().map(d=>{const x=byKey.get(key(d)),expected=d.antes===null?null:norm(formulaLocal(d.antes,locale));if(!x||!Number.isInteger(x.sheetId)||(x.value??null)!==null&&typeof x.value!=='string'||norm(x?.value??null)!==expected)throw Error('Célula anterior divergente: '+key(d));return {...x,antes:x.value??null,depois:norm(formulaLocal(d.depois,locale))};});
 const pedidos=(items,k)=>items.map(d=>({updateCells:{start:{sheetId:d.sheetId,rowIndex:d.r-1,columnIndex:d.c-1},rows:[{values:[d[k]===null?{}:{userEnteredValue:d[k].startsWith('=')?{formulaValue:d[k]}:{stringValue:d[k]}}]}],fields:'userEnteredValue'}}));
 return {pedidos:pedidos(deltas,'depois'),final:{locale,cells:deltas.map(d=>({aba:d.aba,r:d.r,c:d.c,sheetId:d.sheetId,value:d.depois}))},reverter(atual){if(atual?.locale!==locale||!Array.isArray(atual.cells)||atual.cells.length!==deltas.length)throw Error('Snapshot de reversão divergente');const index=new Map(atual.cells.map(d=>[key(d),d]));if(index.size!==deltas.length)throw Error('Alvo de reversão duplicado');for(const d of deltas){const x=index.get(key(d));if(!x||x.sheetId!==d.sheetId||norm(x.value)!==d.depois)throw Error('Célula divergente na reversão');}return pedidos(deltas,'antes');}};
}
function prepararNotas(cells){
 if(!Array.isArray(cells)||cells.length!==notas().length||new Set(cells.map(x=>x.a1)).size!==cells.length)throw Error('Snapshot de notas divergente');
 return notas().map(d=>{const x=cells.find(x=>x.aba===d.aba&&x.a1===d.a1);if(!x||!Number.isInteger(x.sheetId)||(x.note??null)!==d.antes)throw Error('Nota anterior divergente');const m=/^([A-Z]+)(\d+)$/.exec(d.a1),c=[...m[1]].reduce((s,v)=>26*s+v.charCodeAt(0)-64,0);return {updateCells:{start:{sheetId:x.sheetId,rowIndex:+m[2]-1,columnIndex:c-1},rows:[{values:[{note:d.depois}]}],fields:'note'}};});
}
function prepararUI(s){
 if(!Number.isInteger(s?.sheetId)||!Array.isArray(s.cells)||s.cells.length!==18||!s.labelFormat||!s.valueFormat)throw Error('Snapshot da área do seletor obrigatório');
 const expected=new Set(Array.from({length:6},(_,i)=>['D','E','F'].map(c=>c+(34+i))).flat());
 for(const x of s.cells){if(!expected.delete(x.a1)||x.cell?.userEnteredValue||x.cell?.dataValidation||x.cell?.note)throw Error('Área do seletor ocupada ou divergente');}
 if(expected.size)throw Error('Área do seletor incompleta');
 const range=(r,rr)=>({sheetId:s.sheetId,startRowIndex:r-1,endRowIndex:rr,startColumnIndex:3,endColumnIndex:6});
 const hint=structuredClone(s.valueFormat);hint.textFormat={...hint.textFormat,fontSize:9};hint.horizontalAlignment='LEFT';hint.wrapStrategy='WRAP';
 const requests=[{repeatCell:{range:range(34,34),cell:{userEnteredFormat:s.labelFormat},fields:'userEnteredFormat'}},{repeatCell:{range:range(35,36),cell:{userEnteredFormat:s.valueFormat},fields:'userEnteredFormat'}},{repeatCell:{range:range(37,39),cell:{userEnteredFormat:hint},fields:'userEnteredFormat'}}];
 for(const [r,rr]of [[34,34],[35,36],[37,39]])requests.push({mergeCells:{range:range(r,rr),mergeType:'MERGE_ALL'}});
 requests.push({setDataValidation:{range:{sheetId:s.sheetId,startRowIndex:34,endRowIndex:35,startColumnIndex:3,endColumnIndex:4},rule:{condition:{type:'ONE_OF_RANGE',values:[{userEnteredValue:"='DADOS_INVOC'!$CY$2:$CY$3"}]},strict:true,showCustomUi:true}}});
 return requests;
}
module.exports={base,plano,notas,prepararCodigo,prepararCelulas,prepararNotas,prepararUI};
if(require.main===module){const [input,output]=process.argv.slice(2);if(!input||!output)throw Error('Informe código atual e proposta privados');const src=fs.readFileSync(input,'utf8'),out=prepararCodigo(src);new Function(out);fs.writeFileSync(output,out);console.log(JSON.stringify({antes:sha(src),depois:sha(out),alvos:plano().length,aplicado:false}));}
