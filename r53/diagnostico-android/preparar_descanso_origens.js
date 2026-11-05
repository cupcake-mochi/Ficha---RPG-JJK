'use strict';
const fs=require('node:fs'),path=require('node:path');
const {sha,trocar}=require('./preparar_recursos_fila');
const BASE='19ae4c19660ce322f6cf3df8041469f8a65a7cfa18a9260c7c32f2c760ec77ac';
const mudancas=require('./descanso_origens_patch.json');
function runtime(){
 return '(function(){\n var mudancas='+JSON.stringify(mudancas)+';\n'+
  ' if(code.indexOf("function regraDoDescanso_(")>=0)throw Error("Descanso/Origem: revisão já aplicada");\n'+
  ' mudancas.forEach(function(m){if(code.split(m[0]).length!==2)throw Error("Descanso/Origem: fonte divergente");});\n'+
  ' mudancas.forEach(function(m){code=code.replace(m[0],function(){return m[1];});});\n})();\n';
}
function prepararCodigo(codigo){
 if(sha(codigo)!==BASE)throw Error('Codigo.gs incompatível: exige a PR65 revisada');
 const ancora=' R53_MODULO_=(new Function(code))();';
 return trocar(codigo,ancora,runtime()+ancora);
}
// Somente para extratores históricos de funções alheias ao descanso.
function reverterFonte(src){
 if(!src.includes('function regraDoDescanso_('))return src;
 for(const m of mudancas)if(src.split(m[1]).length!==2)throw Error('Fonte de descanso divergente');
 for(const m of [...mudancas].reverse())src=src.replace(m[1],()=>m[0]);
 return src;
}
module.exports={BASE,mudancas,runtime,prepararCodigo,reverterFonte};
