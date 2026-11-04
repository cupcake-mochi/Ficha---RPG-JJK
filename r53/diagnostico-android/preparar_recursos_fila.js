'use strict';
// Preparação OFFLINE sobre snapshot da integração 51–56. Não acessa Google.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const raiz=path.resolve(__dirname,'../..');
const ANTES='8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0';
const ATALHO_ANTES='de090dfa36a22e25c40bbffc6f246ded4e068b98d3dbd08ac47fa76a4c90104b';
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const ler=p=>fs.readFileSync(path.join(raiz,p),'utf8');
function trocar(s,a,b){if(s.split(a).length!==2)throw Error('Âncora divergente ou duplicada');return s.replace(a,()=>b);}
function preparar(codigo){
 if(sha(codigo)!==ANTES)throw Error('Codigo incompatível: exige snapshot da integração 51–56; nada aplicado');
 const ini=codigo.indexOf('// GERADO por r53/atalho_livre.js;'),fim=codigo.indexOf('\n}',codigo.indexOf('function r53LivreConferido_(',ini))+3;
 const bloco=codigo.slice(ini,fim);
 if(sha(bloco)!==ATALHO_ANTES)throw Error('Atalho incompatível');
 let novo=trocar(codigo,bloco,ler('r53/atalho_livre.gs'));
 const anchor=' R53_MODULO_=(new Function(code))();';
 novo=trocar(novo,anchor,ler('r53/diagnostico-android/recursos_fila_runtime.gs')+'\n'+anchor);
 return novo;
}
if(require.main===module){
 const [entrada,saida]=process.argv.slice(2);
 if(!entrada||!saida)throw Error('Uso: node preparar_recursos_fila.js snapshot.gs proposta.gs (ambos privados)');
 const antes=fs.readFileSync(entrada,'utf8'),depois=preparar(antes);fs.writeFileSync(saida,depois);
 console.log(JSON.stringify({antes:sha(antes),depois:sha(depois),aplicado:false}));
}
module.exports={preparar,sha,ANTES,trocar};
