'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const p=require('../diagnostico-android/preparar_bencaos_imunidades');
const {formulaLocal}=require('../diagnostico-android/preparar_pilha_5156');
const ctx=vm.createContext({});
vm.runInContext(require('../../medidas/carregar-ficha').fontes(),ctx);
assert.equal(ctx.SOBRAS_.length,0);
vm.runInContext(p.molde(),ctx);
const key=d=>d.aba+'!'+(d.addr||d.r+','+d.c);
assert.equal(new Set(p.plano.map(key)).size,p.plano.length);
const val=(abas,d)=>{let a=abas.find(a=>a.nome===d.aba);return d.addr?a.notas.find(v=>v[0]===d.addr)?.[1]:a.vals.find(v=>v[0]===d.r&&v[1]===d.c)?.[2];};
for(const d of p.plano)assert.equal(val(ctx.ABAS,d),d.depois,key(d));
const abas=[...new Set(p.plano.map(d=>d.aba))].map(nome=>({nome,vals:[],notas:[]}));
for(const d of p.plano){let a=abas.find(a=>a.nome===d.aba);(d.addr?a.notas:a.vals).push(d.addr?[d.addr,d.antes]:[d.r,d.c,d.antes,0]);}
const ruim=JSON.parse(JSON.stringify(abas)),d=p.plano.at(-1),a=ruim.find(a=>a.nome===d.aba);
(d.addr?a.notas.find(v=>v[0]===d.addr):a.vals.find(v=>v[0]===d.r&&v[1]===d.c))[d.addr?1:2]='divergente';
const antes=JSON.stringify(ruim);assert.throws(()=>ctx.r53AjustarBencaosImunidades_(ruim),/divergente/);assert.equal(JSON.stringify(ruim),antes);
ctx.r53AjustarBencaosImunidades_(abas);const depois=JSON.stringify(abas);ctx.r53AjustarBencaosImunidades_(abas);assert.equal(JSON.stringify(abas),depois);
for(const locale of ['pt_BR','en_US']){const cells=p.plano.map(d=>({...d,sheetId:abas.findIndex(a=>a.nome===d.aba),[d.addr?'note':'value']:formulaLocal(d.antes,locale)}));assert.equal(p.planejar({locale,cells}).requests.length,p.plano.length);for(const c of cells)c[c.addr?'note':'value']=formulaLocal(c.depois,locale);assert.equal(p.planejar({locale,cells},true).requests.length,p.plano.length);assert.throws(()=>p.planejar({locale,cells}),/divergente/);}
assert.throws(()=>p.prepararCodigo('outro projeto'),/incompatível/);
if(process.argv[2]){const s=fs.readFileSync(process.argv[2],'utf8'),novo=p.prepararCodigo(s);new vm.Script(novo);assert.throws(()=>p.prepararCodigo(novo),/incompatível/);}
console.log(JSON.stringify({resultado:'OK',alvos:p.plano.length,basePrivada:!!process.argv[2]}));
