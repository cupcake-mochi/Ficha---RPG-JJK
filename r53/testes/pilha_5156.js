'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),zlib=require('zlib'),path=require('path');
const p=require('../diagnostico-android/preparar_pilha_5156');
let checks=0;const t=f=>{f();checks++;};const clone=x=>JSON.parse(JSON.stringify(x));
const helper=fs.readFileSync('r53/diagnostico-android/pilha_5156_molde.gs','utf8');
const c={R53_PILHA_516_:clone(p.plano)};vm.createContext(c);vm.runInContext(helper,c);
const abas=[];
for(const d of p.plano){let a=abas.find(x=>x.nome===d.aba);if(!a){a={nome:d.aba,vals:[],notas:[]};abas.push(a);}if(d.antes!==null)(d.addr?a.notas:a.vals).push(d.addr?[d.addr,d.antes]:[d.r,d.c,d.antes,73]);}
const antes=clone(abas);c.r53AjustarPilha516_(abas);
const depois=clone(abas);c.r53AjustarPilha516_(abas);t(()=>assert.deepEqual(clone(abas),depois));
for(const d of p.plano){const a=abas.find(x=>x.nome===d.aba);t(()=>assert.equal(d.addr?a.notas.find(x=>x[0]===d.addr)[1]:a.vals.find(x=>x[0]===d.r&&x[1]===d.c)[2],d.depois));}
// Uma divergência tardia não pode deixar os primeiros alvos parcialmente alterados.
const ruins=clone(antes);ruins.at(-1).notas.at(-1)[1]='divergente';const copia=clone(ruins);
t(()=>assert.throws(()=>c.r53AjustarPilha516_(ruins),/divergente/));t(()=>assert.deepEqual(ruins,copia));
// Paridade dos 14 alvos com as fontes geradas, incluindo estilos existentes preservados.
const fontes={};vm.createContext(fontes);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),fontes);
require('../diagnostico-android/preparar_aviso_atributo').reverterModelo(require('../diagnostico-android/preparar_menu_oficios').reverterModelo(require('../diagnostico-android/preparar_especializacao').reverterModelo(fontes.ABAS)));require('../diagnostico-android/preparar_buff_decimal').reverterModelo(fontes.ABAS);require('../diagnostico-android/preparar_reserva_bolsa').reverterModelo(fontes.ABAS);
require('../diagnostico-android/preparar_origens_recursos').reverterModelo(fontes.ABAS);
const revisoes = require('../diagnostico-android/integridade_movimento_plano.json');
const conjuracao = require('../diagnostico-android/conjuracao_integridade_plano.json');
for (const d of p.plano) {
 const a = fontes.ABAS.find(x => x.nome === d.aba);
 const atual = d.addr ? a.notas.find(x => x[0] === d.addr)[1] :
   a.vals.find(x => x[0] === d.r && x[1] === d.c)[2];
 const revisao = revisoes.find(x => x.aba === d.aba && (d.addr ? x.addr === d.addr : x.r === d.r && x.c === d.c));
 if (revisao) t(() => assert.equal(revisao.antes, d.depois));
 const posterior = require('../diagnostico-android/bencaos_imunidades_plano.json').find(x => x.aba === d.aba && (d.addr ? x.addr === d.addr : x.r === d.r && x.c === d.c));
 if (posterior) t(() => assert.equal(posterior.antes, revisao ? revisao.depois : d.depois));
 const antesConjuracao = posterior ? posterior.depois : revisao ? revisao.depois : d.depois;
 const ultima = !d.addr && conjuracao.find(x => x.aba === d.aba && x.r === d.r && x.c === d.c);
 if (ultima) t(() => assert.equal(ultima.antes, antesConjuracao));
 t(() => assert.equal(atual, ultima ? ultima.depois : antesConjuracao));
}
for(const locale of ['pt_BR','en_US']){
 const snapshot={locale,cells:p.plano.map(d=>({...d,sheetId:['FICHA','DADOS_CUSTOM','DADOS','FICHA AMALDIÇOADA'].indexOf(d.aba),[d.addr?'note':'value']:p.formulaLocal(d.antes,locale)}))};
 const copy=clone(snapshot),out=p.planejarCelulas(snapshot);t(()=>assert.equal(out.requests.length,14));t(()=>assert.deepEqual(snapshot,copy));
 t(()=>assert.equal(out.requests.filter(x=>x.updateCells.fields==='note').length,3));
 const final=clone(snapshot);final.cells.forEach((x,i)=>{x[x.addr?'note':'value']=p.formulaLocal(p.plano[i].depois,locale);});
 t(()=>assert.equal(p.planejarCelulas(final,true).requests.length,14));t(()=>assert.throws(()=>p.planejarCelulas(final),/divergente/));
 const ruim=clone(snapshot);ruim.cells.at(-1).note='alterado';t(()=>assert.throws(()=>p.planejarCelulas(ruim),/divergente/));
 const duplicado=clone(snapshot);duplicado.cells.push(duplicado.cells[0]);t(()=>assert.throws(()=>p.planejarCelulas(duplicado),/duplicado/));
}
t(()=>assert.equal(p.formulaLocal('=IF(A1=4.5,"a,b;4.5 e ""oi""",0)','pt_BR'),'=IF(A1=4,5;"a,b;4.5 e ""oi""";0)'));
t(()=>assert.throws(()=>p.formulaLocal('=SUM({1,2})','pt_BR'),/Matriz/));
t(()=>assert.throws(()=>p.preparar('outro código'),/incompatível/));
// Opcional: snapshots privados recuperados das cópias. Nunca incluí-los no Git.
if(process.argv[2]){
 const dir=process.argv[2],read=n=>fs.readFileSync(path.join(dir,n),'utf8');
 const antigo=read('Codigo-antes-reconstituido.gs'),novo=p.preparar(antigo);
 t(()=>assert.equal(novo,read('qa-era-Codigo.gs')));t(()=>assert.equal(novo,read('qa-ciclo-Codigo.gs')));
 t(()=>assert.throws(()=>p.preparar(novo),/incompatível/));
 const fragmentos=[];
 for(const f of ['Ficha','Invocacoes','Analise','Configuracao','Origens']){const text=read('qa-era-'+f+'.gs'),m=/var R53_CODIGO_(\d+)_ = ("[^\n]*");/.exec(text);assert(m);fragmentos[+m[1]]=JSON.parse(m[2]);}
 const modulo=zlib.gunzipSync(Buffer.from(fragmentos.join(''),'base64')).toString('utf8');t(()=>assert.equal(p.sha(modulo),p.MODULO));
 const ctx={code:modulo};vm.createContext(ctx);vm.runInContext(fs.readFileSync('r53/diagnostico-android/pilha_5156_runtime.gs','utf8'),ctx);
 // A fonte integral agora inclui a revisão posterior do descanso por Origem.
 vm.runInContext(require('../diagnostico-android/preparar_descanso_origens').runtime(),ctx);
 vm.runInContext(require('../diagnostico-android/preparar_origens_recursos').runtime(),ctx);
 const anterior=vm.runInNewContext('(function(){'+modulo+'})()'),mod=vm.runInNewContext('(function(){'+ctx.code+'})()');
 t(()=>assert.equal(typeof mod.r53DescansarComQueda,'function'));
 const model=JSON.parse(JSON.stringify(mod.__estado().abas));c.r53AjustarPilha516_(model);t(()=>assert.equal(model.length,anterior.__estado().abas.length));
 t(()=>assert.equal(mod.__estado().sobras.length,0));
 // O bloco de descanso resultante reproduz as funções da fonte atual integral.
 const codigo=fs.readFileSync('apps-script/Codigo.gs','utf8');
 for(const nome of ['contaDoDescanso_','r53DescansarComQueda','descansar_']){
  const extrair=s=>{const start=s.indexOf('function '+nome+'(');assert(start>=0);const end=s.indexOf('\nfunction ',start+1);return s.slice(start,end<0?undefined:end).replace(/\/\*\*[\s\S]*?\*\/\s*$/,'').trim();};
  t(()=>assert.equal(extrair(ctx.code),extrair(codigo)));
 }
}
console.log(JSON.stringify({resultado:'OK',verificacoes:checks,snapshotsPrivados:!!process.argv[2]}));
