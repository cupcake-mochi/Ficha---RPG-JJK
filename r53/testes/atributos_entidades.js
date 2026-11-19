'use strict';
const assert = require('node:assert/strict');
const { ler, expandir } = require('./expansao_domada_modelo');
const { valores, pedidos } = require('../diagnostico-android/preparar_atributos_entidades');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/atributos_entidades_delta.json');

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
  assert.equal(aplicar.length, 60);
  assert.equal(reverter.length, 60);
  for (const [i, d] of delta.entries()) {
    assert.deepEqual(aplicar[i].updateCells.start, { sheetId: 1, rowIndex: d.r - 1, columnIndex: d.c - 1 });
    assert.equal(aplicar[i].updateCells.fields, 'userEnteredValue');
    assert.deepEqual(aplicar[i].updateCells.rows[0].values[0], depois.cells[chave(d)]);
    assert.deepEqual(reverter[i].updateCells.rows[0].values[0], antes.cells[chave(d)]);
  }
  antes.cells['DADOS_INVOC!DL2'].userEnteredValue.formulaValue = '=99';
  assert.throws(() => pedidos(delta, antes), /Célula divergente: DADOS_INVOC!2,116/);
}

const dados = ler('apps-script').find(a => a.nome === 'DADOS_INVOC');
const formulas = expandir(dados);
for (const d of delta) {
  assert.equal(formulas.get(d.r + ':' + d.c), d.depois, 'Modelo e plano divergem em ' + chave(d));
}
console.log('Atributos das entidades: 60 alvos, geração, aplicação e reversão em pt_BR e en_US.');
