'use strict';
// O ± recebe a variação final, não identifica a natureza do efeito.
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const c={};vm.createContext(c);
for(const [file,name] of [['apps-script/Codigo.gs','aplicaPasso_'],['r53/atalho_livre.gs','r53LivrePasso_']]){
 const text=fs.readFileSync(file,'utf8');const start=text.indexOf('function '+name+'(');const end=text.indexOf('\n}',start)+2;
 assert.ok(start>=0&&end>start);vm.runInContext(text.slice(start,end),c);
}
const cases=[
 [1,20,0,9,10,0], // bruto: não deve ganhar redução implícita
 [1,20,0,4,5,0], // cura de 9 já reduzida manualmente para 4
 [1,20,0,1,2,0], // mínimo positivo já calculado
 [19,20,0,4,20,0], // teto
 [5,20,3,-5,3,0], // dano usa temporária primeiro
 [5,20,3,4,9,3] // ajuste positivo não consome temporária
];
for(const [a,m,t,p,ea,et] of cases)for(const name of ['aplicaPasso_','r53LivrePasso_']){
 const v=c[name](a,m,t,p);assert.equal(v.atual,ea);assert.equal(v.temp,et);
}
console.log(JSON.stringify({resultado:'OK',casos:cases.length,rotas:2,escopo:'Ajuste final e paridade das duas rotas; não testa cura automática'}));
