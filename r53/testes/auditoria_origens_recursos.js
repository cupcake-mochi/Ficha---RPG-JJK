'use strict';
// Diagnóstico contra o livro R66, não suíte de aprovação nem simulação da fila Google.
// Executa somente a conta real do descanso; leituras/seleções são cobertas no ensaio nativo.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('apps-script/Codigo.gs','utf8');
const inicio=source.indexOf('var DESCANSOS_ = '),fim=source.indexOf('function textoDoDescanso_(',inicio);
assert(inicio>=0&&fim>inicio);
const ctx=vm.createContext({});vm.runInContext(source.slice(inicio,fim),ctx);
const resultados=[];
for(const [modelo,maximo,classe] of [['Era',60,3],['Ciclo',20,1]]) {
 for(const [cenario,tipo,grau,atual,folego] of [
  ['propício com Fôlego','Curto · lugar propício',0,0,true],
  ['fora, grau 2 com Fôlego','Curto · fora',2,0,true],
  ['fora, grau 3 sem recuperação','Curto · fora',3,0,true],
  ['Fôlego próximo ao máximo','Curto · lugar propício',0,maximo-1,true],
  ['controle sem Fôlego','Curto · lugar propício',0,0,false]
 ]) {
  // Oráculo independente: regra normal primeiro, depois Classe, respeitando proibição/teto.
  const pct=tipo==='Curto · lugar propício'?25:[25,15,5,0][grau];
  const normal=pct>0?Math.max(1,Math.floor(maximo*pct/100)):0;
  const esperado=Math.min(maximo,atual+normal+(folego&&normal>0?classe:0));
  const obtido=ctx.contaDoDescanso_(tipo,{vida:6,vidaMax:30,pe:atual,peMax:maximo,
   integ:20,integMax:20,sequelas:0,exaustao:grau,folegoRecuperado:folego,classeDisponivel:classe}).pe;
  resultados.push({modelo,cenario,esperado,obtido,conforme:esperado===obtido});
 }
}
console.log(JSON.stringify({tipo:'diagnóstico local; não mede eventos nem latência',
 baseLivro:'JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d',
 total:resultados.length,conformes:resultados.filter(x=>x.conforme).length,
 divergentes:resultados.filter(x=>!x.conforme).length,resultados},null,2));
