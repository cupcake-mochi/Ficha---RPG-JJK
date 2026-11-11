'use strict';
// Especialização na FICHA do jogador (11/11/2026). Dois avisos da mesma regra do livro (R66):
// 1. "Se você tiver especialização numa perícia ou ofício treinado...": com a caixa de especialização marcada e a de
//    treino não, as 23 perícias e os 11 ofícios somavam maestria e meia sem gastar treino. A caixa diz "Marque o
//    treino" (decisão do Mizuki: aviso na caixa). Com valor fixo da campanha não avisa.
// 2. Cada especialização gasta uma escolha de Corpo no marco. Sem o Corpo marcado, os contadores diziam só "1 a mais"
//    (achado do Mizuki). Agora dizem "Especialização sem marco de Corpo", e o resumo diz o que fazer.
// Geradores: ficha-v01/configuracao.py (avisa_treino) e ficha-v01/ficha_automatica.py (contadores).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { ler, expandir } = require('../testes/expansao_domada_modelo');
const { planejarCelulas } = require('./preparar_pilha_5156');

const CAMINHO = __dirname + '/especializacao_delta.json';
const AVISO = 'Marque o treino';
// coluna da conta → [especialização, treino]
const CAIXAS = { 16: ['E', 'D'], 32: ['U', 'T'], 14: ['E', 'D'], 27: ['R', 'Q'] };
const CONTAS = {};
for (let r = 80; r <= 90; r++) CONTAS[r + ':16'] = CAIXAS[16];
for (let r = 79; r <= 90; r++) CONTAS[r + ':32'] = CAIXAS[32];
for (let r = 108; r <= 113; r++) CONTAS[r + ':14'] = CAIXAS[14];
for (let r = 108; r <= 112; r++) CONTAS[r + ':27'] = CAIXAS[27];
const SEM_CORPO = 'DADOS!$AK$15>DADOS!$AK$10';
const FALTA = '(DADOS!$AK$15-DADOS!$AK$10)';
const CURTO = `IF(${SEM_CORPO},"Especialização sem marco de Corpo",`;
const LONGO = `IF(${SEM_CORPO},"Marcou "&${FALTA}&IF(${FALTA}=1," especialização"," especializações")` +
  '&" sem marco de Corpo: escolha Corpo no Marco Escolhido ou tire a marcação",';
// contador → [trecho antes do qual o aviso entra, aviso]
const CONTADORES = {
  '89:37': ['IF(DADOS!$AK$24>0,DADOS!$AK$24&" a mais",', CURTO],
  '114:32': ['IF(DADOS!$AK$24>0,DADOS!$AK$24&" a mais",', CURTO],
  '105:37': ['IF(DADOS!$AK$24>0,"Marcou "&DADOS!$AK$24&" a mais: tire uma perícia, um ofício ou uma especialização",', LONGO],
};
const semTreino = (espec, treino, linha) => `AND(DADOS_CONFIG!$C$${linha}<>1,${espec}=TRUE,${treino}<>TRUE)`;

// Depois = antes com o aviso por fora (contas) ou o aviso do Corpo antes do "a mais" (contadores); nada mais muda.
function explicar(pos, antes) {
  if (typeof antes !== 'string') return null;
  const contador = CONTADORES[pos];
  if (contador) {
    const [trecho, aviso] = contador;
    if (!antes.startsWith('=IF(AND(DADOS!$AK$15>0,$AH$11<10),"Especialização só no nível 10') || antes.split(trecho).length !== 2) return null;
    return antes.replace(trecho, aviso + trecho) + ')';
  }
  const caixas = CONTAS[pos];
  if (!caixas) return null;
  const r = pos.split(':')[0];
  const [espec, treino] = caixas.map(c => c + r);
  const linhas = new Set([...antes.matchAll(/DADOS_CONFIG!\$[A-E]\$(\d+)/g)].map(m => m[1]));
  if (linhas.size !== 1) return null;
  if (!antes.includes(`IF(${espec}, $D$67 + INT($D$67 / 2), IF(${treino}, $D$67, 0))`)) return null;
  return `=IF(${semTreino(espec, treino, [...linhas][0])},"${AVISO}",${antes.slice(1)})`;
}

function comparar(base, atual) {
  assert.deepEqual(atual.map(a => a.nome), base.map(a => a.nome), 'Abas divergentes');
  const delta = [];
  let posicoes = 0;
  for (const [i, a] of base.entries()) {
    const b = atual[i];
    const estrutura = ({ vals, abaixo, geracao, notas, ...resto }) => resto;
    assert.deepEqual(estrutura(b), estrutura(a), 'Estrutura ' + a.nome);
    assert.deepEqual(b.notas || [], a.notas || [], 'Notas ' + a.nome);
    const o = expandir(a), d = expandir(b);
    for (const pos of new Set([...o.keys(), ...d.keys()])) {
      posicoes++;
      if (o.get(pos) === d.get(pos)) continue;
      assert.equal(a.nome, 'FICHA', 'Mudança fora da FICHA: ' + a.nome + ' ' + pos);
      assert.ok(CONTAS[pos] || CONTADORES[pos], 'Mudança fora das contas e dos contadores: ' + pos);
      assert.equal(explicar(pos, o.get(pos)), d.get(pos), 'Mudança fora do molde em ' + pos);
      const [r, c] = pos.split(':').map(Number);
      delta.push({ aba: a.nome, r, c, antes: o.get(pos), depois: d.get(pos) });
    }
  }
  assert.equal(delta.length, 37, 'Esperadas 34 contas e 3 contadores');
  return { delta, abas: base.length, posicoes };
}

// Comparadores históricos: devolve as 37 células ao estado anterior. Atômico: confere tudo antes de gravar.
function reverterModelo(abas, delta = require(CAMINHO)) {
  const aba = abas.find(a => a.nome === 'FICHA');
  if (!aba) throw Error('Especialização: aba FICHA ausente');
  const antes = expandir(aba);
  for (const d of delta) if (antes.get(d.r + ':' + d.c) !== d.depois) throw Error('Especialização divergente: FICHA!' + d.r + ',' + d.c);
  const copia = structuredClone(aba);
  for (const v of copia.vals) {
    const d = delta.find(d => d.r === v[0] && d.c === v[1]);
    if (d) v[2] = d.antes;
  }
  const depois = expandir(copia);
  const alvo = new Map(delta.map(d => [d.r + ':' + d.c, d.antes]));
  for (const pos of new Set([...antes.keys(), ...depois.keys()])) {
    const esperado = alvo.has(pos) ? alvo.get(pos) : antes.get(pos);
    if (depois.get(pos) !== esperado) throw Error('Especialização: reversão fora do molde em FICHA!' + pos);
  }
  aba.vals = copia.vals;
  return abas;
}

// Instalação nas QAs: snapshot = { locale, sheetIds: {FICHA: id}, cells: [{aba, r, c, value}] } na ordem do delta.
function pedidos(delta, snapshot, reverter = false) {
  assert.ok(['pt_BR', 'en_US'].includes(snapshot.locale), 'Localidade não ensaiada');
  assert.equal(snapshot.cells.length, delta.length, 'Quantidade de alterações divergente');
  const cells = snapshot.cells.map(c => ({ ...c, sheetId: snapshot.sheetIds[c.aba] }));
  return planejarCelulas({ locale: snapshot.locale, cells }, reverter, delta).requests;
}

if (require.main === module) {
  const [base, atual] = process.argv.slice(2);
  if (!base || !atual) throw Error('Informe os dois diretórios de fontes GS');
  const r = comparar(ler(base), ler(atual));
  fs.writeFileSync(CAMINHO, JSON.stringify(r.delta, null, 2) + '\n');
  console.log(JSON.stringify({ abas: r.abas, posicoes: r.posicoes, alteracoes: r.delta.length }));
}

module.exports = { explicar, comparar, reverterModelo, pedidos, semTreino, CONTAS, CONTADORES, AVISO };
