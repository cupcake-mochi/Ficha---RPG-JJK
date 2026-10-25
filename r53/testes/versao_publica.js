'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const {preparar,anchor}=require('../diagnostico-android/preparar_versao_publica');
const ctx={};vm.createContext(ctx);vm.runInContext(fs.readFileSync('r53/diagnostico-android/versao_publica.gs','utf8'),ctx);
const plan=JSON.parse(JSON.stringify(ctx.R53_VERSAO_PUBLICA_));
function fixture(){return plan.map(p=>({nome:p.aba,vals:[[p.linha,p.coluna,p.antes],[20,20,'entrada preservada']]}));}
const a=fixture();assert.strictEqual(ctx.r53AjustarVersaoPublica_(a),2);assert.strictEqual(ctx.r53AjustarVersaoPublica_(a),0);
for(const p of plan){const sh=a.find(a=>a.nome===p.aba);assert.strictEqual(sh.vals[0][2],p.depois);assert.strictEqual(sh.vals[1][2],'entrada preservada');assert(!/R53|\$[BD]\$1|em dia/.test(sh.vals[0][2]));}
const bad=fixture();bad[1].vals[0][2]='fórmula desconhecida';const before=JSON.stringify(bad);assert.throws(()=>ctx.r53AjustarVersaoPublica_(bad),/divergente/);assert.strictEqual(JSON.stringify(bad),before);
const source='function loader(){\n'+anchor+'\n}\nfunction r53OnEditOriginal_(e){if(e)e.r53Inicio_=Date.now();return 1;}';const patched=preparar(source);assert(patched.includes('r53AjustarVersaoPublica_(R53_MODULO_.__estado().abas)'));
assert.throws(()=>preparar(patched),/já instalada/);assert.throws(()=>preparar('function vazio(){}'),/divergente/);
let written='';ctx.r53Formula_=f=>f;const sh={getName:()=> 'FICHA',getRange:()=>({setFormula:f=>{written=f;}})};
const range={getSheet:()=>sh,getRow:()=>4,getColumn:()=>8,getNumRows:()=>1,getNumColumns:()=>19};
assert.strictEqual(ctx.r53RestaurarVersaoPublica_({source:{},range}),true);assert.strictEqual(written,plan.find(p=>p.aba==='FICHA').depois);
range.getNumRows=()=>2;assert.strictEqual(ctx.r53RestaurarVersaoPublica_({source:{},range}),false);
range.getNumRows=()=>1;range.getRow=()=>2;range.getColumn=()=>34;range.getNumColumns=()=>13;sh.getName=()=> 'CARTEIRA';assert.strictEqual(ctx.r53RestaurarVersaoPublica_({source:{},range}),true);assert.strictEqual(written,plan.find(p=>p.aba==='CARTEIRA').depois);
console.log(JSON.stringify({resultado:'OK',escopo:'dois moldes, idempotência, recusa atômica e preparador estrito'}));
