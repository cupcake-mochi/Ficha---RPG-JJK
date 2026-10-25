'use strict';
const assert=require('assert'),fs=require('fs'),vm=require('vm');
const {ajustarCarga,preparar}=require('../diagnostico-android/preparar_carga_invocacoes');
const formula=(col,i,step)=>{const p=[33,35,37,42].map(r=>"'INVOCAÇÕES'!$"+col+'$'+(r+step*i));return '=SUM('+p[0]+':'+p[1]+','+p[2]+':'+p[3]+')';};
const fixture=()=>[{nome:'DADOS_INVOC',vals:Array.from({length:12},(_,i)=>[i+2,139,formula(i<6?'Y':'AR',i%6,198),7]),abaixo:[]},{nome:'ANALISE',vals:[[1,1,"'literal",4]]}];
let data=fixture(),before=structuredClone(data);ajustarCarga(data);
for(let i=0;i<12;i++)assert.strictEqual(data[0].vals[i][2],formula(i<6?'Y':'AR',i%6,231));
assert.deepStrictEqual(data[1],before[1]);const patched=structuredClone(data);ajustarCarga(data);assert.deepStrictEqual(data,patched);
for(const corrupt of [a=>a.shift(),a=>a[0].vals.pop(),a=>a[0].vals.push(a[0].vals[1]),a=>a[0].vals[11][2]='=0',a=>a[0].abaixo.push([3,139,13,139])]){
 let a=fixture();corrupt(a);let saved=structuredClone(a);assert.throws(()=>ajustarCarga(a));assert.deepStrictEqual(a,saved);
}
const anchor=' try { r53AjustarRitual_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }';
let source='var R53_MODULO_; function r53Modulo_(){if(R53_MODULO_)return R53_MODULO_;R53_MODULO_=make();\n'+anchor+'\nreturn R53_MODULO_;}';
let result=preparar(source);assert.throws(()=>preparar(result));assert.throws(()=>preparar(''));
let ctx={make:()=>({__estado:()=>({abas:[]})}),r53AjustarRitual_:()=>{}};vm.createContext(ctx);vm.runInContext(result,ctx);assert.throws(()=>ctx.r53Modulo_());assert.strictEqual(ctx.R53_MODULO_,null);
if(process.argv[2]){
 let state=JSON.parse(fs.readFileSync(process.argv[2])),saved=structuredClone(state);ajustarCarga(state.abas);let changes=[];
 for(let i=0;i<state.abas.length;i++)for(let j=0;j<state.abas[i].vals.length;j++)if(JSON.stringify(saved.abas[i].vals[j])!==JSON.stringify(state.abas[i].vals[j])){changes.push([i,j]);saved.abas[i].vals[j][2]=state.abas[i].vals[j][2];}
 assert.strictEqual(changes.length,10);assert.deepStrictEqual(saved,state);
}
console.log(JSON.stringify({resultado:'OK',moldes_corrigidos:10,idempotencia:true,recusa_atomica:true,modulo_real:!!process.argv[2]}));
