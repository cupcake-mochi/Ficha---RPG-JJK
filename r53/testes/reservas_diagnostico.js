'use strict';
// Diagnóstico mecânico: preserva resultados divergentes; não altera as expectativas para produzir verde.
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('apps-script/Codigo.gs','utf8');
function extrair(nome){const start=source.indexOf('function '+nome+'('),end=source.indexOf('\nfunction ',start+1);assert(start>=0);return source.slice(start,end);}
const c={};vm.createContext(c);vm.runInContext(extrair('aplicaPasso_')+'\n'+extrair('tetoTemp_'),c);
const a={};vm.createContext(a);vm.runInContext(fs.readFileSync('r53/atalho_livre.gs','utf8'),a);
const resultados=[];
for(const max of [0,1,2,3,8,23])for(const recebido of [-2,0,1,6,15]){
 const esperado=Math.min(Math.max(0,recebido),max>0?Math.max(1,Math.floor(max/2)):0),obtido=c.tetoTemp_(recebido,max);
 resultados.push({tipo:'teto',max,recebido,esperado,obtido,conforme:esperado===obtido});
}
const casos=[
 ['absorção parcial',[10,23,11,-12],{atual:9,temp:0}],
 ['só temporária',[10,23,11,-5],{atual:10,temp:6}],
 ['gasto de PE',[2,8,4,-5],{atual:1,temp:0}],
 ['limite inferior',[3,23,2,-50],{atual:0,temp:0}],
 ['ganho não repõe temporária',[10,23,3,4],{atual:14,temp:3}],
 ['ganho limitado ao máximo',[22,23,3,8],{atual:23,temp:3}],
 ['temporária protege vida zero',[0,23,3,-2],{atual:0,temp:1}],
 ['ajuste nulo',[10,23,3,0],{atual:10,temp:3}]
];
for(const [nome,entrada,esperado] of casos)for(const [caminho,fn] of [['modulo',c.aplicaPasso_],['atalho',a.r53LivrePasso_]]){
 const obtido=JSON.parse(JSON.stringify(fn(...entrada)));resultados.push({tipo:'delta',nome,caminho,entrada,esperado,obtido,conforme:JSON.stringify(esperado)===JSON.stringify(obtido)});
}
console.log(JSON.stringify({escopo:'Funções reais do módulo e atalho; não simula onEdit nativo',casos:resultados.length,aprovados:resultados.filter(x=>x.conforme).length,divergencias:resultados.filter(x=>!x.conforme),resultados},null,2));
