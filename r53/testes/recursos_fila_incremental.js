'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),path=require('path'),zlib=require('zlib');
const p=require('../diagnostico-android/preparar_recursos_fila');
const runtime=fs.readFileSync('r53/diagnostico-android/recursos_fila_runtime.gs','utf8');
const source=fs.readFileSync('apps-script/Codigo.gs','utf8'),engine=fs.readFileSync('r53/recursos_delta.gs','utf8');
const fn=(s,n)=>{const a=s.indexOf('function '+n+'(');assert(a>=0);return s.slice(a,s.indexOf('\n}\n',a)+2);};
const changes=JSON.parse(runtime.match(/var mudancas = (.*);/)[1]);
let checks=0;const eq=(a,b)=>{assert.deepEqual(a,b);checks++;},throws=f=>{assert.throws(f);checks++;};
for(const [old,novo]of changes)eq(novo,fn(source,novo.match(/^function (\w+)/)[1]));
eq(require('../atalho_livre').DELTA_ATUAL,fn(source,'aplicarDelta_'));
const c={code:changes.map(x=>x[0]).join('\n')+'\n'};vm.createContext(c);vm.runInContext(runtime,c);
eq(c.code.includes(engine),true);new vm.Script(c.code);checks++;
throws(()=>vm.runInContext(runtime,c));
throws(()=>p.preparar('código desconhecido'));throws(()=>p.preparar(''));
// Divergência na segunda função recusa antes de substituir a primeira.
const ruim={code:changes[0][0]+'\n'+changes[1][0].replace('var ficha','var outra')},antes=ruim.code;vm.createContext(ruim);throws(()=>vm.runInContext(runtime,ruim));eq(ruim.code,antes);
if(process.argv[2]){
 const dir=process.argv[2],read=n=>fs.readFileSync(path.join(dir,n),'utf8');
 const original=read('qa-era-Codigo.gs'),novo=p.preparar(original);eq(original,read('qa-ciclo-Codigo.gs'));throws(()=>p.preparar(novo));
 // Reversão dos dois trechos deixa absolutamente todos os outros bytes iguais.
 const inicio=original.indexOf('// GERADO por r53/atalho_livre.js;'),fim=original.indexOf('\n}',original.indexOf('function r53LivreConferido_(',inicio))+3;
 let revertido=p.trocar(novo,fs.readFileSync('r53/atalho_livre.gs','utf8'),original.slice(inicio,fim));
 revertido=p.trocar(revertido,runtime+'\n','');eq(revertido,original);
 new vm.Script(novo);checks++;
 const chunks=[];for(const f of ['Ficha','Invocacoes','Analise','Configuracao','Origens']){const m=read('qa-era-'+f+'.gs').match(/var R53_CODIGO_(\d+)_ = ("[^\n]*");/);assert(m);chunks[+m[1]]=JSON.parse(m[2]);}
 const modulo=zlib.gunzipSync(Buffer.from(chunks.join(''),'base64')).toString('utf8');
 const box={code:modulo};vm.createContext(box);vm.runInContext(fs.readFileSync('r53/diagnostico-android/pilha_5156_runtime.gs','utf8'),box);const integrado=box.code;
 vm.runInContext(runtime,box);new vm.Script('(function(){'+box.code+'})()');checks++;
 for(const [,novo]of changes)eq(box.code.includes(novo),true);
 // O módulo otimizado conserva as demais funções e todos os catálogos.
 let volta=box.code;volta=volta.slice((engine+'\n').length);for(const [a,b]of changes)volta=p.trocar(volta,b,a);eq(volta,integrado);
 console.log(JSON.stringify({proposta:p.sha(novo),snapshot:p.sha(original),aplicado:false}));
}
console.log(JSON.stringify({resultado:'OK',verificacoes:checks,snapshotsPrivados:!!process.argv[2]}));
