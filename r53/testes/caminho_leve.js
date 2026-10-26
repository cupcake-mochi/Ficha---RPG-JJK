'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const {gerar,corpo,NOMES}=require('../caminho_leve');const d=gerar();
assert.strictEqual(fs.readFileSync('apps-script/Caminho.gs','utf8'),d.output);
const src=fs.readFileSync('apps-script/Codigo.gs','utf8');
for(const n of NOMES){let body=corpo(src,n);for(const[a,b]of d.ioPatches)body=body.replace(a,b);body=body.replace(/ss.getSheetByName\('DADOS_PROGRESSAO'\)/g,'r53ProgCaminho_(ss)').replace(/SpreadsheetApp.getActive\(\).getSheetByName\('DADOS_PROGRESSAO'\)/g,'r53ProgCaminho_(SpreadsheetApp.getActive())').replace(/SpreadsheetApp.getActive\(\)/g,'R53_CAMINHO_SS_');assert(d.code.includes(body),n);}
assert(!/R53_CODIGO_|R53_EDITOR_|r53Modulo_/.test(d.code));
const box={};vm.createContext(box);vm.runInContext(d.output,box);
let got,calls=0;box.r53CaminhoLeve_=()=>({editar:e=>{calls++;got=e;}});
function range(sheet,row,col,nr=1,nc=1){let r={getSheet:()=>({getName:()=>sheet}),getRow:()=>row,getLastRow:()=>row+nr-1,getColumn:()=>col,getLastColumn:()=>col+nc-1,getNumRows:()=>nr,getNumColumns:()=>nc,getValue:()=>"Caminho com ' e = literal",getCell:()=>r};return r;}
for(const [col,nc] of [[4,1],[4,9],[14,1],[14,9]]){
 const e={range:range('FICHA',11,col,1,nc),oldValue:'Vanguarda',value:'Bastião',source:{},authMode:'LIMITED'};
 assert.strictEqual(box.r53EditarCaminho_(e),true);assert.notStrictEqual(got,e);assert.strictEqual(got.oldValue,e.oldValue);assert.strictEqual(got.source,e.source);assert.strictEqual(got.value,e.value);assert.strictEqual(e.r53EditorVerificado_,undefined);
}
const before=calls;for(const r of [range('FICHA',10,4),range('FICHA',11,5),range('FICHA',11,4,2),range('FICHA',11,4,1,10),range('CARTEIRA',11,4)])assert.strictEqual(box.r53EditarCaminho_({range:r}),false);
assert.strictEqual(calls,before);assert.strictEqual(box.r53EditarCaminho_({range:range('FICHA',11,4)}),true);assert.strictEqual(got.value,"Caminho com ' e = literal");
// O módulo conserva a sequência de efeitos do caminho antigo, sem o editor de combate.
const traceBox={SpreadsheetApp:{getActive(){return traceBox.ss;}}};traceBox.ss={getSheetByName:n=>n==='R53_EVENTOS'?null:({getDataRange:()=>({getValues:()=>[]})})};vm.createContext(traceBox);
const entry=d.code.replace('return {editar:function(e){','var resultado={editar:function(e){').replace(/\}\};$/,'}};');vm.runInContext(entry,traceBox);
const order=[];traceBox.indiceDosDados_=()=>({});for(const n of ['marcarPericiasDoCaminho_','trilhaDoCaminho_','habilidadesDaFicha_','grupoDeArmaDaTrilha_','trocaArmaDoCaminho_','fichaMexeNaPessoal_'])traceBox[n]=()=>order.push(n);
traceBox.resultado.editar({source:traceBox.ss,range:range('FICHA',11,4)});assert.deepStrictEqual(order,['marcarPericiasDoCaminho_','trilhaDoCaminho_','habilidadesDaFicha_','grupoDeArmaDaTrilha_','trocaArmaDoCaminho_','fichaMexeNaPessoal_']);
console.log('Caminho leve: 29 regras preservadas com leituras limitadas, seleção/mesclagem, evento, colagens e sequência aprovados.');
