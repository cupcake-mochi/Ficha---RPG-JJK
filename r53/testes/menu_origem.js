'use strict';
// Compara a geração integral com a base da PR54 e com as duas fórmulas ensaiadas no Google.
const fs=require('fs'),vm=require('vm'),cp=require('child_process'),assert=require('assert/strict');
const loader=require('../../medidas/carregar-ficha');
const baseline='93a109ce3477845618da3beff941af7326f17db7';
function load(source){const c={};vm.createContext(c);vm.runInContext(source,c);return JSON.parse(JSON.stringify(c.ABAS));}
const before=load(loader.arquivos().map(n=>cp.execFileSync('git',['show',baseline+':apps-script/'+n],{encoding:'utf8',maxBuffer:64*1024*1024})).join('\n'));
const after=load(loader.fontes());
const formulas=JSON.parse(fs.readFileSync('r53/testes/menu_origem_formulas.json','utf8'));
const normalize=s=>s.replace(/,/g,';').replace(/'(DADOS_CUSTOM|DADOS)'!/g,'$1!');
const old=before.find(a=>a.nome==='DADOS_CUSTOM'),now=after.find(a=>a.nome==='DADOS_CUSTOM');
for(const [i,col] of [94,95].entries()){
 const a=old.vals.find(v=>v[0]===3&&v[1]===col),b=now.vals.find(v=>v[0]===3&&v[1]===col);
 assert.equal(normalize(a[2]),formulas.old[i]);assert.equal(normalize(b[2]),formulas.next[i]);
 a[2]=b[2];
}
for(const a of before)delete a.geracao;
for(const a of after)delete a.geracao;
assert.deepEqual(after,before,'Só CP3 e CQ3 podem mudar; demais abas, fórmulas, notas e contratos preservados');
console.log(JSON.stringify({resultado:'OK',celulas_alteradas:2,abas:after.length,escopo:'Paridade com fórmulas testadas nativamente e comparação integral das abas contra PR54'}));
