'use strict';
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const cells = new Map(); let writes = 0;
// Contraprova nativa de 23/10: RichText também consome o apóstrofo de escape.
const literalGoogle = text => text.startsWith("'") ? text.slice(1) : text;
function cell(r,c) { const key=r+','+c; if(!cells.has(key))cells.set(key,{value:'',formula:''});return cells.get(key); }
const sheet = {getName:()=> 'ANALISE',getLastRow:()=> 605,
  getRange(r,c,nr=1,nc=1) { return {getRow:()=>r,getLastRow:()=>r+nr-1,getColumn:()=>c,getLastColumn:()=>c+nc-1,getSheet:()=>sheet,
    getValue:()=>cell(r,c).value,getFormula:()=>cell(r,c).formula,
    getValues:()=>Array.from({length:nr},(_,i)=>Array.from({length:nc},(_,j)=>cell(r+i,c+j).value)),
    getFormulas:()=>Array.from({length:nr},(_,i)=>Array.from({length:nc},(_,j)=>cell(r+i,c+j).formula)),
    setRichTextValues(rows) { rows.forEach((row,i)=>row.forEach((v,j)=>{cell(r+i,c+j).value=literalGoogle(v.text);cell(r+i,c+j).formula='';writes++;})); },
    setRichTextValue(v) { cell(r,c).value=literalGoogle(v.text);cell(r,c).formula='';writes++; },
    setFormula(f) {cell(r,c).formula=f;},getDisplayValue:()=>cell(r,c).value}; }};
const ss={getSheetByName:()=>sheet,toast(){},getSpreadsheetLocale:()=> 'pt_BR'};
const context={console,ABAS:[],ABA_AMALDICOADA_:'FICHA AMALDIÇOADA',REFERENCIA_PURA_: /^='?[^']+'?!/,livresDaAba_:()=>({}),
 a1_:(r,c)=>'cel'+r+','+c,formulaNoIdioma_:x=>x,SpreadsheetApp:{getActive:()=>ss,newRichTextValue:()=>({setText(text){this.text=text;return this;},build(){return {text:this.text};}})}};
vm.createContext(context);
vm.runInContext(fs.readFileSync('apps-script/Android.gs','utf8'),context);
const source=fs.readFileSync('apps-script/Codigo.gs','utf8');
const start=source.indexOf('function devolverConta_('),end=source.indexOf('\n}',start)+2;
vm.runInContext(source.slice(start,end),context);
const texts=["'FICHA PESSOAL'!$A$1",'=texto','FALSE','001', 'Aspas " internas',"'",''];
const formula=t=>'="'+t.replaceAll('"','""')+'"';
for(let r=2;r<=605;r++){const t=texts[(r-2)%texts.length];Object.assign(cell(r,3),{formula:formula(t),value:t});cell(r,2).value='preservar';}
// Uma fórmula realmente dinâmica não pode ser congelada.
Object.assign(cell(10,3),{formula:'=A10',value:'dinâmica'});
const expected=604-1;
assert.strictEqual(context.otimizarAnaliseAndroid().convertidas,expected);
assert.strictEqual(writes,expected);
assert.strictEqual(context.otimizarAnaliseAndroid().convertidas,0);
for(let r=2;r<=605;r++){assert.strictEqual(cell(r,2).value,'preservar');if(r!==10){assert.strictEqual(cell(r,3).formula,'');assert.strictEqual(cell(r,3).value,texts[(r-2)%texts.length]);}}
assert.strictEqual(cell(10,3).formula,'=A10');
context.ABAS=[{nome:'ANALISE',vals:texts.map((t,i)=>[2+i,3,formula(t)])}];
texts.forEach((t,i)=>{cell(i+2,3).value='apagado';cell(i+2,3).formula='';});
assert.strictEqual(context.devolverConta_({range:sheet.getRange(2,3,texts.length)},'ANALISE'),texts.length);
texts.forEach((t,i)=>{assert.strictEqual(cell(i+2,3).value,t);assert.strictEqual(cell(i+2,3).formula,'');});
// Sem escrita redundante quando os literais já estão corretos.
const previous=writes;
assert.strictEqual(context.devolverConta_({range:sheet.getRange(2,3,texts.length)},'ANALISE'),0);
assert.strictEqual(writes,previous);
assert.strictEqual(context.r53LiteralAnalise_('=A1'),null);
assert.strictEqual(context.r53LiteralAnalise_('="incompleta'),null);
console.log(JSON.stringify({resultado:'OK',constantes:expected,restauracoes:texts.length,idempotente:true,limite:'Mock local; exige validação nativa de RichText/restauração antes da publicação.'}));
