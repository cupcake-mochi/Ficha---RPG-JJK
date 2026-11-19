'use strict';
// Menu de Origem inválida (PR54): CP3 e CQ3 da DADOS_CUSTOM seguem iguais às duas fórmulas ensaiadas no Google.
// A comparação integral contra a base da PR54 (93a109c) valeu só na entrega: desde então a geração mudou em outras
// abas, e o commit antigo nem tem todos os arquivos do carregador. A instalação e a reversão moram no
// menu_origem_molde.js, que está no smoke. Revisto em 11/11/2026.
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const loader=require('../../medidas/carregar-ficha');
const c={};vm.createContext(c);vm.runInContext(loader.fontes(),c);
const formulas=JSON.parse(fs.readFileSync('r53/testes/menu_origem_formulas.json','utf8'));
const normalize=s=>s.replace(/,/g,';').replace(/'(DADOS_CUSTOM|DADOS)'!/g,'$1!');
const now=c.ABAS.find(a=>a.nome==='DADOS_CUSTOM');
for(const [i,col] of [94,95].entries()){
 const b=now.vals.find(v=>v[0]===3&&v[1]===col);
 assert.ok(b,'Falta DADOS_CUSTOM!3,'+col);
 assert.equal(normalize(b[2]),formulas.next[i],'DADOS_CUSTOM!3,'+col+' fora da fórmula ensaiada');
 assert.notEqual(normalize(b[2]),formulas.old[i]);
}
console.log(JSON.stringify({resultado:'OK',celulas:2,escopo:'Paridade de CP3 e CQ3 com as fórmulas testadas nativamente'}));
