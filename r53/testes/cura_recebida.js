'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const code=fs.readFileSync('apps-script/CuraRecebida.gs','utf8');let n=0;
function test(fn){fn();n++;}
const c={};vm.createContext(c);vm.runInContext(code,c);
const base={atual:1,maximo:20,corpo:'Corpo Exaurido',corporal:true};
for(const [v,ganho] of [[0,0],[1,1],[2,1],[3,1],[8,4],[9,4],[40,20]])test(()=>assert.equal(c.r53ContaCura_(base,v).ganho,ganho));
for(const corpo of ['Corpo Próprio','Corpo Quebradiço','Corpo Debilitado'])test(()=>assert.equal(c.r53ContaCura_({...base,corpo},9).depois,10));
test(()=>assert.equal(c.r53ContaCura_({...base,corporal:false},9).depois,10));
test(()=>assert.equal(c.r53ContaCura_({...base,atual:19},9).depois,20));
test(()=>assert.equal(c.r53ContaCura_({...base,atual:25},9).depois,25));
for(const bruto of [-1,1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1])test(()=>assert.throws(()=>c.r53ContaCura_(base,bruto)));
for(const patch of [{atual:''},{maximo:0},{maximo:'20'},{corporal:''},{atual:-1}])test(()=>assert.throws(()=>c.r53ContaCura_({...base,...patch},9)));
function scenario(options={}){
 let s={...base},writes=[],alerts=[],locked=0,released=0,toasts=0,reads=0;
 const sheet={getRange:a=>({getValues:()=>[[s.atual,0,0,0,0,0,s.maximo]],getValue:()=>a==='D52'?s.corpo:s.corporal,setValue:v=>{assert.equal(a,'D26');writes.push(v);s.atual=v;}})};
 const ui={Button:{OK:'OK',YES:'YES'},ButtonSet:{OK_CANCEL:'OC',YES_NO:'YN'},createMenu:()=>({addItem:()=>({addToUi(){}})}),prompt:()=>({getSelectedButton:()=>options.cancel?'CANCEL':'OK',getResponseText:()=>options.text??'9'}),alert:(...args)=>{alerts.push(args);if(args.length===3&&options.changed)s.atual=7;return options.no?'NO':'YES';}};
 const ctx={SpreadsheetApp:{getUi:()=>ui,getActive:()=>({getSheetByName:()=>sheet,toast(){toasts++;}}),flush(){}},LockService:{getDocumentLock:()=>({tryLock(){locked++;return !options.busy;},releaseLock(){released++;}})}};
 vm.createContext(ctx);vm.runInContext(code,ctx);ctx.aplicarCuraRecebida();return {s,writes,alerts,locked,released,toasts};
}
let x=scenario();test(()=>assert.deepEqual(x.writes,[5]));test(()=>assert.equal(x.released,1));test(()=>assert.equal(x.toasts,1));
for(const opt of [{cancel:true},{text:'9.5'},{text:'-9'},{text:''},{text:'0'},{no:true},{busy:true},{changed:true}])test(()=>assert.deepEqual(scenario(opt).writes,[]));
test(()=>assert.equal(scenario({changed:true}).released,1));
console.log(JSON.stringify({resultado:'OK',verificacoes:n}));
