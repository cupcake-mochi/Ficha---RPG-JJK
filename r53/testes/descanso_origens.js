'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib'),path=require('node:path');
const p=require('../diagnostico-android/preparar_descanso_origens');
const fonte=require('../diagnostico-android/preparar_origens_recursos').reverterFonte(fs.readFileSync('apps-script/Codigo.gs','utf8'));
const antigo=p.reverterFonte(fonte);
assert.notEqual(antigo,fonte);
const c=vm.createContext({code:antigo});vm.runInContext(p.runtime(),c);
assert.equal(c.code,fonte);
assert.throws(()=>vm.runInContext(p.runtime(),c),/já aplicada/);
const ruim=vm.createContext({code:p.mudancas.map(x=>x[0]).join('\n').replace(p.mudancas.at(-1)[0],'divergente')});
const antes=ruim.code;assert.throws(()=>vm.runInContext(p.runtime(),ruim),/divergente/);assert.equal(ruim.code,antes);
assert.equal(fs.readFileSync('r53/diagnostico-android/descanso_origens_runtime.gs','utf8'),p.runtime());
assert.throws(()=>p.prepararCodigo('outro projeto'),/incompatível/);
if(process.argv[2]) {
 const base=fs.readFileSync(process.argv[2],'utf8'),novo=p.prepararCodigo(base);new vm.Script(novo);
 assert.throws(()=>p.prepararCodigo(novo),/incompatível/);
}
if(process.argv[3]) {
 const parts=[];
 for(const nome of ['Ficha','Invocacoes','Analise','Configuracao','Origens']) {
  const m=fs.readFileSync(path.join(process.argv[3],'qa-era-'+nome+'.gs'),'utf8').match(/var R53_CODIGO_(\d+)_ = ("[^\n]*");/);
  assert(m);parts[+m[1]]=JSON.parse(m[2]);
 }
 const real=vm.createContext({code:zlib.gunzipSync(Buffer.from(parts.join(''),'base64')).toString('utf8')});
 for(const n of ['pilha_5156_runtime','recursos_fila_runtime','descanso_origens_runtime'])
  vm.runInContext(fs.readFileSync('r53/diagnostico-android/'+n+'.gs','utf8'),real);
 for(const [,depois] of p.mudancas)assert(real.code.includes(depois));
 new Function(real.code);
}
console.log(JSON.stringify({resultado:'OK',funcoes:p.mudancas.length,pacotePrivado:!!process.argv[3]}));
