'use strict';
// Exercita o template proposto em VM, sem serviços Google e sem .gs gerados.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const template = fs.readFileSync(process.argv[2], 'utf8');
const spec = nome => ({nome, geracao:'ensaio', vals:[], fundos:[], merges:[], notas:[], bordas:[]});
const mapa = {
  'PersonagemFormas1.gs':'VALORES_PERSONAGEM_FORMAS_1_',
  'PersonagemPainel.gs':'VALORES_PERSONAGEM_PAINEL_',
  'PersonagemAnalise.gs':'CONTRATO_PERSONAGEM_'
};
const chunks = {
  main: 'var GERACAO_="ensaio";var COMPLEMENTOS_ESPERADOS_='+JSON.stringify(mapa)+';var ABAS='+
    JSON.stringify([spec('CONFIGURAÇÃO'),spec('ANALISE')])+';'+template,
};
for (const [key, nome, variavel] of [
  ['formas','DADOS_FORMAS','ABAS_PERSONAGEM_FORMAS'],
  ['aptidoes','DADOS_APTIDOES','ABAS_PERSONAGEM_APTIDOES'],
  ['talentos','DADOS_TALENTOS','ABAS_PERSONAGEM_TALENTOS']
]) chunks[key]='var '+variavel+'='+JSON.stringify([spec(nome)])+';if(typeof juntarAbas_==="function")juntarAbas_('+variavel+');';
for (const [key,nome,variavel] of [
  ['valores','DADOS_FORMAS','VALORES_PERSONAGEM_FORMAS_1_'],
  ['painel','CONFIGURAÇÃO','VALORES_PERSONAGEM_PAINEL_'],
  ['analise','ANALISE','CONTRATO_PERSONAGEM_']
]) chunks[key]='var '+variavel+'='+JSON.stringify([{nome,geracao:'ensaio',arquivo:key,vals:[[2,1,key]]}])+
  ';if(typeof juntarValores_==="function")juntarValores_('+variavel+');';
const keys=Object.keys(chunks);
const orders=[
  keys, [...keys].reverse(),
  ['formas','valores','aptidoes','painel','talentos','analise','main'],
  ['valores','main','painel','formas','analise','talentos','aptidoes'],
  ['main','valores','analise','formas','aptidoes','talentos','painel'],
  ['painel','analise','valores','talentos','aptidoes','main','formas']
];
let checks=0;
for(const order of orders) {
  const context=vm.createContext({});
  for(const key of order)vm.runInContext(chunks[key],context);
  const read=nome => JSON.parse(JSON.stringify(context.ABAS.find(a=>a.nome===nome)));
  assert.equal(context.ABAS.length,5,order.join(','));
  for(const [nome,esperado] of [['DADOS_FORMAS','valores'],['CONFIGURAÇÃO','painel'],['ANALISE','analise']]) {
    assert.deepEqual(read(nome).vals,[[2,1,esperado]],order.join(',')+' '+nome);
  }
  const antes=JSON.stringify(context.ABAS);
  context.juntarAbas_(context.ABAS_PERSONAGEM_FORMAS);
  context.juntarContratosPecas_();
  assert.equal(JSON.stringify(context.ABAS),antes,'junção repetida muda conteúdo');
  context.juntarValores_([{nome:'DADOS_FORMAS',geracao:'antiga',arquivo:'antigo',vals:[[4,1,'erro']]}]);
  assert(!read('DADOS_FORMAS').vals.some(v=>v[0]===4));
  assert(context.SOBRAS_.includes('antigo'));
  checks++;
}
process.stdout.write(JSON.stringify({ordens:checks,idempotencia:true,geracao_antiga_recusada:true})+'\n');
