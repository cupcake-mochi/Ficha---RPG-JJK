'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),crypto=require('crypto');
const {preparar,ancora}=require('../diagnostico-android/preparar_vida_bloquear_loader');
const h=fs.readFileSync('r53/diagnostico-android/vida_bloquear_molde.gs','utf8'),c={};vm.createContext(c);vm.runInContext(h,c);
const cp=x=>JSON.parse(JSON.stringify(x)),p=c.R53_VIDA_BLOQUEAR_,run=c.r53AjustarVidaBloquear_;
const original=[{nome:'FICHA',vals:p.map(x=>[x.r,x.c,x.antes,22]).concat([[67,15,'preservar',13]])},{nome:'ANALISE',vals:[[1,1,'preservar']]}];
let n=0;function test(fn){fn();n++;}
let a=cp(original),expected=cp(original);p.forEach((x,i)=>expected[0].vals[i][2]=x.depois);
test(()=>assert.equal(run(a),2));test(()=>assert.deepEqual(a,expected));test(()=>assert.equal(run(a),0));
for(let i=0;i<2;i++){
 let b=cp(original);b[0].vals[i][2]='=999';let before=cp(b);test(()=>assert.throws(()=>run(b)));test(()=>assert.deepEqual(b,before));
}
for(let b of [[],[original[0],original[0]],[{nome:'FICHA',vals:[]}],[{nome:'FICHA',vals:original[0].vals.concat([original[0].vals[0]])}]])test(()=>assert.throws(()=>run(cp(b))));
const g={};vm.createContext(g);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),g);require('../diagnostico-android/preparar_aviso_atributo').reverterModelo(g.ABAS);require('../diagnostico-android/preparar_buff_decimal').reverterModelo(g.ABAS);require('../diagnostico-android/preparar_reserva_bolsa').reverterModelo(g.ABAS);require('../diagnostico-android/preparar_origens_recursos').reverterModelo(g.ABAS);for(let x of p){const posterior=require('../diagnostico-android/bencaos_imunidades_plano.json').find(d=>d.aba===x.aba&&d.r===x.r&&d.c===x.c);if(posterior)test(()=>assert.equal(posterior.antes,x.depois));test(()=>assert.equal(g.ABAS.find(a=>a.nome==='FICHA').vals.find(v=>v[0]===x.r&&v[1]===x.c)[2],posterior?posterior.depois:x.depois));}
const sha=s=>crypto.createHash('sha256').update(s).digest('hex'),s='// outro incremento\n'+ancora+'\n// fim';let out=preparar(s,sha(s));test(()=>assert.ok(out.startsWith('// outro incremento\n')));test(()=>assert.ok(out.includes(ancora+'\n// fim')));
test(()=>assert.throws(()=>preparar(s,'errado')));test(()=>assert.throws(()=>preparar(out,sha(out))));for(let b of ['sem ancora',s+ancora])test(()=>assert.throws(()=>preparar(b,sha(b))));
console.log(JSON.stringify({resultado:'OK',verificacoes:n}));
