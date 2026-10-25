'use strict';
const assert=require('assert'),vm=require('vm'),fs=require('fs');
const {preparar,ajustarRitual}=require('../diagnostico-android/preparar_ritual_loader');
const old=row=>'=IF(AND(NOT(OR(FALSE)),$LI'+row+'="Ritual"),"Conferir Técnica Inata","")';
const fixture=()=>[{nome:'DADOS_AM',vals:[[2,346,old(2),1],[3,347,old(3),1],[4,1,'=42',8]],abaixo:[[3,343,13,347]]},{nome:'ANALISE',vals:[[1,1,"'literal",2]]}];
let a=fixture(),original=JSON.stringify(a);ajustarRitual(a);
assert(a[0].vals[0][2].includes('DADOS_AM!$A$2=1'));assert(a[0].vals[1][2].includes('$LI3'));
let patched=JSON.stringify(a);ajustarRitual(a);assert.strictEqual(JSON.stringify(a),patched);
assert.deepStrictEqual(a[1],JSON.parse(original)[1]);assert.deepStrictEqual(a[0].vals[2],JSON.parse(original)[0].vals[2]);
for(const mutate of [a=>a.splice(0,1),a=>a[0].vals.pop()&&a[0].vals.pop(),a=>a[0].vals.push(a[0].vals[0]),a=>a[0].vals[1][2]='=0',a=>a[0].abaixo=[]]){
 const broken=fixture();mutate(broken);const saved=JSON.stringify(broken);assert.throws(()=>ajustarRitual(broken));assert.strictEqual(JSON.stringify(broken),saved);
}
const anchor=" if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');";
let source='var R53_MODULO_; function r53Modulo_(){if(R53_MODULO_)return R53_MODULO_;R53_MODULO_=make();\n'+anchor+'\nreturn R53_MODULO_;}';
const result=preparar(source);assert.throws(()=>preparar(result));assert.throws(()=>preparar(''));
const ctx={make:()=>({__estado:()=>({abas:[],sobras:[]})})};vm.createContext(ctx);vm.runInContext(result,ctx);
assert.throws(()=>ctx.r53Modulo_());assert.strictEqual(ctx.R53_MODULO_,null);assert.throws(()=>ctx.r53Modulo_());
if(process.argv[2]){
 let state=JSON.parse(fs.readFileSync(process.argv[2])),copy=JSON.parse(JSON.stringify(state));ajustarRitual(state.abas);
 let changes=[];for(let i=0;i<copy.abas.length;i++)for(let j=0;j<copy.abas[i].vals.length;j++)if(JSON.stringify(copy.abas[i].vals[j])!==JSON.stringify(state.abas[i].vals[j]))changes.push([i,j]);
 assert.strictEqual(changes.length,2);for(let [i,j] of changes)copy.abas[i].vals[j][2]=state.abas[i].vals[j][2];assert.deepStrictEqual(copy,state);
}
console.log(JSON.stringify({resultado:'OK',cenarios:10,modulo_real:!!process.argv[2]}));
