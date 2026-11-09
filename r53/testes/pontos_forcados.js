'use strict';
const assert = require('node:assert/strict');
const { ler, expandir } = require('./expansao_domada_modelo');
const { valores, pedidos } = require('../diagnostico-android/preparar_pontos_forcados');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/pontos_forcados_delta.json');

const chave = d => d.aba + '!' + valores.get(d.r + ':' + d.c);
function snapshot(locale, fase) {
  const cells = Object.fromEntries(delta.map(d => [
    chave(d), { userEnteredValue: { formulaValue: formulaLocal(d[fase], locale) } },
  ]));
  return { locale, sheetIds: { DADOS_INVOC: 1 }, cells };
}

for (const locale of ['pt_BR', 'en_US']) {
  const antes = snapshot(locale, 'antes');
  const depois = snapshot(locale, 'depois');
  const aplicar = pedidos(delta, antes);
  const reverter = pedidos(delta, depois, true);
  assert.equal(aplicar.length, 12);
  assert.equal(reverter.length, 12);
  for (const [i, d] of delta.entries()) {
    assert.deepEqual(aplicar[i].updateCells.start, { sheetId: 1, rowIndex: d.r - 1, columnIndex: d.c - 1 });
    assert.equal(aplicar[i].updateCells.fields, 'userEnteredValue');
    assert.deepEqual(aplicar[i].updateCells.rows[0].values[0], depois.cells[chave(d)]);
    assert.deepEqual(reverter[i].updateCells.rows[0].values[0], antes.cells[chave(d)]);
  }
  antes.cells['DADOS_INVOC!HL2'].userEnteredValue.formulaValue = '=99';
  assert.throws(() => pedidos(delta, antes), /Célula divergente: DADOS_INVOC!2,220/);
}

// Depois = antes + a condição "fora" no OR do erro + o sufixo. Pontos em DJ:DN da mesma linha.
for (const d of delta) {
  assert.equal(d.c, 220);
  const r = d.r;
  const fora = 'OR(' + ['DJ', 'DK', 'DL', 'DM', 'DN']
    .map(c => `$${c}${r}<0,$${c}${r}>6,$${c}${r}<>INT($${c}${r})`).join(',') + ')';
  const erro = `=IF(OR($FW${r}>$FX${r},$FZ${r}>$FY${r})`;
  assert.ok(d.antes.startsWith(erro + ',"⚠ "'), 'Antes fora do molde em ' + chave(d));
  assert.ok(d.antes.endsWith('" · ACIMA DE 3 SÓ COM MARCO","")'), 'Antes sem o sufixo de Marco em ' + chave(d));
  const esperado = erro.slice(0, -1) + ',' + fora + ')' + d.antes.slice(erro.length) +
    `&IF(${fora}," · PONTO FORA DE 0 A 6","")`;
  assert.equal(d.depois, esperado, 'Depois fora do molde em ' + chave(d));
}

// Semântica da condição nova.
const fora = p => p.some(x => x < 0 || x > 6 || x !== Math.floor(x));
const casos = [
  [[0, 0, 0, 0, 0], false], [[3, 3, 3, 0, 0], false], [[6, 6, 4, 0, 0], false],
  [[4, 4, 3, 1, -1], true], [[3.5, 3.5, 3, 1, 0], true], [[7, 3, 3, 0, 0], true], [[0, 0, 0, 0, 6.0001], true],
];
for (const [p, esperado] of casos) assert.equal(fora(p), esperado, JSON.stringify(p));

const dados = ler('apps-script').find(a => a.nome === 'DADOS_INVOC');
const formulas = expandir(dados);
for (const d of delta) {
  assert.equal(formulas.get(d.r + ':' + d.c), d.depois, 'Modelo e plano divergem em ' + chave(d));
}
console.log('Pontos forçados das entidades: 12 alvos, geração, aplicação e reversão em pt_BR e en_US.');
