'use strict';
// Gera o delta a partir de duas gerações locais. O preparador não acessa o Google.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { ler, expandir } = require('../testes/expansao_domada_modelo');
const { coordenadas, formulaLocal } = require('./preparar_pilha_5156');

const formulas = new Map();
for (let row = 2; row <= 13; row++) {
  formulas.set(row + ':203', 'GU' + row);
  formulas.set(row + ':228', 'HT' + row);
}
const nota = 'INVOCAÇÕES!L42';
const alvos = new Set([...formulas.values()].map(a1 => 'DADOS_INVOC!' + a1).concat(nota));

function normalizarFormula(formula) {
  // O Sheets relê um intervalo de uma célula como referência simples.
  return formula?.split(/("(?:[^"]|"")*")/).map((parte, i) =>
    i % 2 ? parte : parte.replace(/(\$[A-Z]+\d+):\1\b/g, '$1')
  ).join('');
}

function comparar(base, atual) {
  assert.deepEqual(atual.map(a => a.nome), base.map(a => a.nome), 'Abas divergentes');
  const delta = [];
  let posicoes = 0;
  for (const [i, antes] of base.entries()) {
    const depois = atual[i];
    const estrutura = ({ vals, abaixo, geracao, notas, ...resto }) => resto;
    assert.deepEqual(estrutura(depois), estrutura(antes), 'Estrutura ' + antes.nome);
    const origem = expandir(antes);
    const destino = expandir(depois);
    for (const pos of new Set([...origem.keys(), ...destino.keys()])) {
      posicoes++;
      if (origem.get(pos) === destino.get(pos)) continue;
      const a1 = formulas.get(pos);
      assert.ok(antes.nome === 'DADOS_INVOC' && a1, 'Mudança fora do alvo: ' + antes.nome + ' ' + pos);
      delta.push({ aba: antes.nome, a1, campo: 'formula', antes: origem.get(pos), depois: destino.get(pos) });
    }
    const notasAntes = new Map(antes.notas || []);
    const notasDepois = new Map(depois.notas || []);
    for (const a1 of new Set([...notasAntes.keys(), ...notasDepois.keys()])) {
      if (notasAntes.get(a1) === notasDepois.get(a1)) continue;
      assert.equal(antes.nome + '!' + a1, nota, 'Nota fora do alvo');
      delta.push({ aba: antes.nome, a1, campo: 'nota', antes: notasAntes.get(a1), depois: notasDepois.get(a1) });
    }
  }
  assert.deepEqual(new Set(delta.map(d => d.aba + '!' + d.a1)), alvos);
  return { abas: base.length, posicoes, delta };
}

function pedidos(delta, snapshot, reverter = false) {
  const { locale, sheetIds, cells } = snapshot;
  assert.ok(['pt_BR', 'en_US'].includes(locale), 'Localidade não ensaiada');
  assert.equal(delta.length, alvos.size, 'Quantidade de alterações divergente');
  assert.deepEqual(new Set(delta.map(d => d.aba + '!' + d.a1)), alvos, 'Alvos divergentes');
  const requests = [];
  for (const d of delta) {
    const key = d.aba + '!' + d.a1;
    const ehNota = key === nota;
    assert.equal(d.campo, ehNota ? 'nota' : 'formula');
    assert.ok(typeof d.antes === 'string' && typeof d.depois === 'string');
    assert.ok(cells[key], 'Snapshot ausente: ' + key);
    const localizar = v => ehNota ? v : formulaLocal(v, locale);
    const origem = localizar(reverter ? d.depois : d.antes);
    const destino = localizar(reverter ? d.antes : d.depois);
    const atual = ehNota ? cells[key].note : cells[key].userEnteredValue?.formulaValue;
    const igual = v => ehNota ? atual === v : normalizarFormula(atual) === normalizarFormula(v);
    assert.ok(igual(origem) || igual(destino), 'Estado divergente: ' + key);
    if (igual(destino)) continue;
    const sheetId = sheetIds[d.aba];
    assert.ok(Number.isInteger(sheetId), 'Aba sem ID: ' + d.aba);
    const { r, c } = coordenadas({ addr: d.a1 });
    requests.push({ updateCells: {
      start: { sheetId, rowIndex: r - 1, columnIndex: c - 1 },
      rows: [{ values: [ehNota ? { note: destino } : { userEnteredValue: { formulaValue: destino } }] }],
      fields: ehNota ? 'note' : 'userEnteredValue',
    } });
  }
  return requests;
}

if (require.main === module) {
  const [base, atual, saida] = process.argv.slice(2);
  if (!base || !atual || !saida) throw Error('Informe os dois diretórios de fontes GS e o arquivo de saída');
  const { delta, ...contagem } = comparar(ler(base), ler(atual));
  fs.writeFileSync(saida, JSON.stringify(delta, null, 2) + '\n');
  console.log(JSON.stringify({ ...contagem, formulas: delta.filter(d => d.campo === 'formula').length, notas: 1 }));
}

module.exports = { comparar, pedidos };
