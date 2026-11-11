'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const p=require('../diagnostico-android/preparar_origens_recursos');
const fonte=require('../reserva_bolsa_restaurar').reverterFonte(require('../pratica_cotidiana_runtime').reverterFonte(require('../repertorio_trilha_runtime').reverterFonte(fs.readFileSync('apps-script/Codigo.gs','utf8')))),base=p.reverterFonte(fonte);
const c=vm.createContext({code:base});vm.runInContext(p.runtime(),c);
for(const [,depois]of p.mudancas.slice(0,2))assert(c.code.includes(depois));
assert.throws(()=>vm.runInContext(p.runtime(),c),/divergente/);
const ruim=vm.createContext({code:base.replace(p.mudancas[1][0],'divergente')}),antes=ruim.code;
assert.throws(()=>vm.runInContext(p.runtime(),ruim),/divergente/);assert.equal(ruim.code,antes);
assert.equal(p.runtime(),fs.readFileSync('r53/diagnostico-android/origens_recursos_runtime.gs','utf8'));
assert.throws(()=>p.prepararCodigo('base errada'),/divergente/);
const model=vm.createContext({});vm.runInContext(require('../../medidas/carregar-ficha').fontes(),model);
require('../diagnostico-android/preparar_aviso_atributo').reverterModelo(require('../diagnostico-android/preparar_menu_oficios').reverterModelo(require('../diagnostico-android/preparar_especializacao').reverterModelo(model.ABAS)));require('../diagnostico-android/preparar_buff_decimal').reverterModelo(model.ABAS);require('../diagnostico-android/preparar_reserva_bolsa').reverterModelo(model.ABAS);
assert.equal(model.SOBRAS_.length,0);
for(const d of p.plano)assert.equal(model.ABAS.find(a=>a.nome===d.aba).vals.find(v=>v[0]===d.r&&v[1]===d.c)?.[2],d.depois);
const alterado=JSON.parse(JSON.stringify(model.ABAS)),d=p.plano.at(-1);
alterado.find(a=>a.nome===d.aba).vals.find(v=>v[0]===d.r&&v[1]===d.c)[2]='outra fórmula';
const antesModelo=JSON.stringify(alterado);assert.throws(()=>p.reverterModelo(alterado),/divergente/);assert.equal(JSON.stringify(alterado),antesModelo);
p.reverterModelo(model.ABAS);vm.runInContext(p.molde(),model);model.r53AjustarOrigensRecursos_(model.ABAS);
for(const d of p.plano)assert.equal(model.ABAS.find(a=>a.nome===d.aba).vals.find(v=>v[0]===d.r&&v[1]===d.c)?.[2],d.depois);
const depoisModelo=JSON.stringify(model.ABAS);model.r53AjustarOrigensRecursos_(model.ABAS);assert.equal(JSON.stringify(model.ABAS),depoisModelo);
const l=require('../descanso_leve').gerar();assert.equal(l.output,fs.readFileSync('apps-script/Descanso.gs','utf8'));
let edited=0,locked=0,flushed=0,released=0;
const ctx=vm.createContext({LockService:{getDocumentLock:()=>({tryLock:()=>{locked++;return true;},releaseLock:()=>released++})},SpreadsheetApp:{flush:()=>flushed++,getActive:()=>({toast:()=>{}})}});
vm.runInContext(l.output,ctx);ctx.r53DescansoLeve_=()=>({editar:()=>edited++});
function event(row=45,col=4,nr=1,nc=1,name='FICHA',value='Curto · fora'){return {value,range:{getSheet:()=>({getName:()=>name}),getRow:()=>row,getColumn:()=>col,getNumRows:()=>nr,getNumColumns:()=>nc}};}
for(const e of [null,event(44),event(45,3),event(45,4,2),event(45,4,1,11),event(45,4,1,1,'FICHA PESSOAL')])assert.equal(ctx.r53DescansoEdit_(e),false);
assert.equal(edited,0);assert.equal(locked,0);
assert.equal(ctx.r53DescansoEdit_(event(45,4,1,10)),true);assert.equal(edited,1);assert.equal(flushed,1);assert.equal(released,1);
assert.equal(ctx.r53DescansoEdit_(event(45,4,1,1,'FICHA','Escolha o descanso')),true);assert.equal(locked,1);
ctx.r53DescansoLeve_=()=>({editar:()=>{throw Error('falha simulada');}});
assert.throws(()=>ctx.r53DescansoEdit_(event()),/falha simulada/);assert.equal(flushed,2);assert.equal(released,2);
let avisos=0;
ctx.LockService.getDocumentLock=()=>({tryLock:()=>false,releaseLock:()=>{throw Error('não adquiriu a trava');}});
ctx.SpreadsheetApp.getActive=()=>({toast:()=>avisos++});
assert.equal(ctx.r53DescansoEdit_(event()),true);assert.equal(avisos,1);assert.equal(flushed,2);assert.equal(released,2);
if(process.argv[2]){
 const s=fs.readFileSync(process.argv[2],'utf8'),out=p.prepararCodigo(s);new vm.Script(out);assert.throws(()=>p.prepararCodigo(out),/divergente/);assert(!out.includes('QA67 entrada'));
 // Reproduz o carregamento do modelo antigo instalado, com todos os remendos.
 const zlib=require('node:zlib'),path=require('node:path'),dir=process.argv[3];
 assert(dir,'Informe o diretório privado dos cinco fragmentos antigos');
 const fragments=[];
 for(const file of ['Ficha','Invocacoes','Analise','Configuracao','Origens']){const m=/var R53_CODIGO_(\d+)_ = ("[^\n]*");/.exec(fs.readFileSync(path.join(dir,'qa-era-'+file+'.gs'),'utf8'));assert(m);fragments[+m[1]]=JSON.parse(m[2]);}
 const old=zlib.gunzipSync(Buffer.from(fragments.join(''),'base64')).toString('utf8');
 const legacy=JSON.parse(JSON.stringify(vm.runInNewContext('(function(){'+old+'})()').__estado().abas));
 const patches=[['preparar_pilha_5156','r53AjustarPilha516_'],['preparar_integridade_movimento','r53AjustarIntegridadeMovimento_'],['preparar_equipamento','r53AjustarEquipamento_'],['preparar_bencaos_imunidades','r53AjustarBencaosImunidades_'],['preparar_origens_recursos','r53AjustarOrigensRecursos_']];
 const patchCtx=vm.createContext({});
 for(const [file,name] of patches){const patch=require('../diagnostico-android/'+file);const code=patch.molde?patch.molde():'var R53_PILHA_516_='+JSON.stringify(patch.plano)+';\n'+fs.readFileSync('r53/diagnostico-android/pilha_5156_molde.gs','utf8');vm.runInContext(code,patchCtx);patchCtx[name](legacy);}
 for(const d of p.plano)assert.equal(legacy.find(a=>a.nome===d.aba).vals.find(v=>v[0]===d.r&&v[1]===d.c)?.[2],d.depois);
}
console.log(JSON.stringify({resultado:'OK',alvos:p.plano.length,rotinaLeve:l.nomes.length,escopo:'transporte, mesma rotina, colagens e liberação da trava; sem Google'}));
