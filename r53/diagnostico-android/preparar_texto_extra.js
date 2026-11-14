'use strict';
// Texto em caixa de número ou de marcar na FICHA do jogador (11/11/2026). Um "dois" no Extra, ou um "x" colado em
// Trein ou Espec, dava #VALUE! no total das 23 perícias, dos 11 ofícios e dos 4 TRs. A caixa avisa (decisão do
// Mizuki: aviso na caixa), por fora dos outros avisos:
// - "Extra só aceita número", nas 38 contas;
// - "Apague o texto em Trein/Espec", nas 34 de perícia e ofício (o treino dos TRs usa "=TRUE" e não quebra).
// Com valor fixo da campanha não avisa. O ISERROR repete a operação da conta: "2" colado como texto soma e não avisa.
// Gerador: ficha-v01/configuracao.py (avisa_texto).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { ler, expandir } = require('../testes/expansao_domada_modelo');
const { planejarCelulas } = require('./preparar_pilha_5156');

const CAMINHO = __dirname + '/texto_extra_delta.json';
const AVISO_EXTRA = 'Extra só aceita número';
const AVISO_CAIXA = 'Apague o texto em Trein/Espec';
// coluna da conta → [Extra, especialização, treino]; o TR não tem caixa de especialização
const CAIXAS = { 16: ['R', 'E', 'D'], 32: ['AH', 'U', 'T'], 14: ['O', 'E', 'D'], 27: ['AB', 'R', 'Q'], 42: ['AJ'] };
const CONTAS = {};
for (let r = 80; r <= 90; r++) CONTAS[r + ':16'] = CAIXAS[16];
for (let r = 79; r <= 90; r++) CONTAS[r + ':32'] = CAIXAS[32];
for (let r = 108; r <= 113; r++) CONTAS[r + ':14'] = CAIXAS[14];
for (let r = 108; r <= 112; r++) CONTAS[r + ':27'] = CAIXAS[27];
for (let r = 108; r <= 111; r++) CONTAS[r + ':42'] = CAIXAS[42];
const textoNoExtra = (extra, linha) => `AND(DADOS_CONFIG!$C$${linha}<>1,ISERROR(${extra}+0))`;
const textoNaCaixa = (espec, treino, linha) =>
  `AND(DADOS_CONFIG!$C$${linha}<>1,OR(ISERROR(IF(${treino},0,0)),ISERROR(IF(${espec},0,0))))`;

// Depois = antes com os avisos por fora; nada mais muda.
function explicar(pos, antes) {
  if (typeof antes !== 'string') return null;
  const caixas = CONTAS[pos];
  if (!caixas) return null;
  const r = pos.split(':')[0];
  const [extra, espec, treino] = caixas.map(c => c + r);
  const linhas = new Set([...antes.matchAll(/DADOS_CONFIG!\$[A-E]\$(\d+)/g)].map(m => m[1]));
  if (linhas.size !== 1) return null;
  const linha = [...linhas][0];
  if (!new RegExp(`\\+ ?${extra}(?![\\d(])`).test(antes)) return null;
  let f = antes;
  if (espec) {
    if (!antes.includes(`IF(${espec}, $D$67 + INT($D$67 / 2), IF(${treino}, $D$67, 0))`)) return null;
    f = `=IF(${textoNaCaixa(espec, treino, linha)},"${AVISO_CAIXA}",${f.slice(1)})`;
  }
  return `=IF(${textoNoExtra(extra, linha)},"${AVISO_EXTRA}",${f.slice(1)})`;
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
      assert.ok(CONTAS[pos], 'Mudança fora das contas: ' + pos);
      assert.equal(explicar(pos, o.get(pos)), d.get(pos), 'Mudança fora do molde em ' + pos);
      const [r, c] = pos.split(':').map(Number);
      delta.push({ aba: a.nome, r, c, antes: o.get(pos), depois: d.get(pos) });
    }
  }
  assert.equal(delta.length, 38, 'Esperadas 23 perícias, 11 ofícios e 4 TRs');
  return { delta, abas: base.length, posicoes };
}

// Comparadores históricos: devolve as 38 células ao estado anterior. Atômico: confere tudo antes de gravar.
function reverterModelo(abas, delta = require(CAMINHO)) {
  const aba = abas.find(a => a.nome === 'FICHA');
  if (!aba) throw Error('Texto no Extra: aba FICHA ausente');
  const antes = expandir(aba);
  for (const d of delta) if (antes.get(d.r + ':' + d.c) !== d.depois) throw Error('Texto no Extra divergente: FICHA!' + d.r + ',' + d.c);
  const copia = structuredClone(aba);
  for (const v of copia.vals) {
    const d = delta.find(d => d.r === v[0] && d.c === v[1]);
    if (d) v[2] = d.antes;
  }
  const depois = expandir(copia);
  const alvo = new Map(delta.map(d => [d.r + ':' + d.c, d.antes]));
  for (const pos of new Set([...antes.keys(), ...depois.keys()])) {
    const esperado = alvo.has(pos) ? alvo.get(pos) : antes.get(pos);
    if (depois.get(pos) !== esperado) throw Error('Texto no Extra: reversão fora do molde em FICHA!' + pos);
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

module.exports = { explicar, comparar, reverterModelo, pedidos, textoNoExtra, textoNaCaixa, CONTAS, AVISO_EXTRA, AVISO_CAIXA };
