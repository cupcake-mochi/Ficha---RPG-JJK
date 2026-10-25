'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const {preparar,antigo,novo}=require('../diagnostico-android/preparar_missoes');
let checks=0;
function eq(a,b){assert.deepStrictEqual(a,b);checks++;}
const source=fs.readFileSync('apps-script/Salarios.gs','utf8');
function fixture(mode){
 const trace=[],ctx={};vm.createContext(ctx);vm.runInContext(source,ctx);ctx.salarioMissaoDireta_=()=>false;
 const e={range:{getSheet:()=>({getName:()=> 'FICHA PESSOAL'}),getRow:()=>15,getLastRow:()=>15,getColumn:()=>49,getLastColumn:()=>50},value:'missão'};
 ctx.salarioEditar_=ev=>{eq(ev,e);ev.salarioProcessado_=true;trace.push('read');if(mode!=='instalavel'){ev.salarioAntesGravar_();trace.push('write');}trace.push('flush');};
 function original(ev){eq(ev,e);eq(ctx.salarioIntegrarMissao_(ev,original),false);trace.push('original');if(mode==='erro')throw Error('erro original');}
 return {ctx,e,trace,original};
}
for(const mode of ['simples','instalavel']){
 const f=fixture(mode);eq(f.ctx.salarioIntegrarMissao_(f.e,f.original),true);
 eq(f.trace,mode==='simples'?['read','original','write','flush']:['read','flush','original']);
 eq(f.e.salarioAntesGravar_,undefined);eq(f.e.salarioIntegrada_,undefined);
}
const f=fixture('erro');assert.throws(()=>f.ctx.salarioIntegrarMissao_(f.e,f.original),/erro original/);checks++;
eq(f.trace,['read','original']);eq(f.e.salarioAntesGravar_,undefined);eq(f.e.salarioIntegrada_,undefined);
const base=require('../diagnostico-android/preparar_salario_extrato').preparar({files:[{name:'Codigo',source:fs.readFileSync('r53/testes/salarios-com-formula.gs','utf8')}]}).files[0].source;
const s='function r53OnEditOriginal_(e){if(e)e.r53Inicio_=Date.now();return 1;}\n'+base;
const out=preparar(s);eq(out.includes(novo),true);eq(out.includes('salarioIntegrarMissao_(e,function(ev){return r53Modulo_().onEdit(ev);})'),true);
assert.throws(()=>preparar(out),/já presente/);checks++;
assert.throws(()=>preparar(s.replace(antigo,'return;')),/divergente/);checks++;
assert.throws(()=>preparar(s+s),/divergente/);checks++;
let calls=0;const matrix=Array.from({length:73},()=>Array(24).fill('')),notes=matrix.map(r=>r.map(()=>''));
for(const [off,type] of [[0,'Curta'],[6,'Longa'],[12,'Solo simples'],[18,'Final de arco']]){matrix[0][off]='Missão '+off;matrix[0][off+1]=type;}
const sheet={getRange:(r,c,n,cols)=>({getNotes:()=>{calls++;return notes;},getValues:()=>{calls++;return matrix.map(row=>row.slice(c-49,c-49+cols));}})};
const ctx={};vm.createContext(ctx);vm.runInContext(source,ctx);const ss={getSheetByName:()=>sheet};
const separate=ctx.salarioMissoesAtuais_(ss,false);eq(calls,5);calls=0;
const grouped=ctx.salarioMissoesAtuais_(ss,true);eq(calls,2);eq(JSON.stringify(grouped),JSON.stringify(separate));eq(grouped.length,4);
const original=fs.readFileSync('apps-script/Codigo.gs','utf8'),oracle={};vm.createContext(oracle);
for(const name of ['nivelDoXp_','nivelQueSobe_']){const i=original.indexOf('function '+name+'('),j=original.indexOf('\n}',i)+2;vm.runInContext(original.slice(i,j),oracle);}
for(const scale of [0,10,50,150])for(const current of [0,2,10,20,21,30])for(const cap of [0,10,20])for(let xp=0;xp<=5000;xp+=137){
 const curve=Array.from({length:30},(_,i)=>({nivel:i+1,xp:i*scale}));eq(ctx.salarioNivelQueSobe_(curve,xp,current,cap),oracle.nivelQueSobe_(curve,xp,current,cap));
}
// The bounded fast path preserves source formulas and honors dynamic indexes.
let level=1,total=500,restored=0;const data=Array.from({length:35},()=>Array(120).fill(''));
data[0][42]='nível';data[0][43]='xp acumulado';data[0][100]='limiar do feito';data[1][100]=20;
for(let i=1;i<=30;i++){data[i][42]=i;data[i][43]=(i-1)*100;}
data[0][52]='nivel';data[0][53]='AH11';data[0][118]='xp total';data[0][119]='AZ11';
const personal={getName:()=> 'FICHA PESSOAL',getRange:(a,b)=>b?{setFormula:f=>{assert(f.startsWith('='));restored++;}}:{getValue:()=>total}};
const directSS={getSheetByName:n=>n==='DADOS'?{getRange:a=>{eq(a,'AQ4:DP100');return {getValues:()=>data.map(row=>row.slice(42,120))};}}:n==='FICHA'?{getRange:()=>({getValue:()=>level,setValue:v=>{level=v;}})}:personal};
ctx.r53Formula_=f=>f;const event={source:directSS,range:{getSheet:()=>personal,getRow:()=>15,getLastRow:()=>15,getColumn:()=>49,getLastColumn:()=>50}};
let bounds=0;for(const method of ['getRow','getLastRow','getColumn','getLastColumn']){const read=event.range[method];event.range[method]=()=>{bounds++;return read();};}
eq(ctx.salarioMissaoDireta_(event),true);eq(level,6);eq(restored,0);eq(bounds,4);
total=0;ctx.salarioMissaoDireta_(event);eq(level,6);
total=99999;ctx.salarioMissaoDireta_(event);eq(level,20);level=21;ctx.salarioMissaoDireta_(event);eq(level,30);
event.range.getColumn=()=>53;event.range.getLastColumn=()=>53;ctx.salarioMissaoDireta_(event);eq(restored,1);
event.range.getRow=()=>14;eq(ctx.salarioMissaoDireta_(event),false);
const generated=JSON.parse(fs.readFileSync('salarios/missoes_moldes.json'));eq(generated.length,292);
console.log(JSON.stringify({checks,resultado:'OK',escopo:'Ordem leitura/XP/gravação, evento único, rotina instalável, erros, delta estrito'}));
