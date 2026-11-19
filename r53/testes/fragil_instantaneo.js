'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const p = require('../diagnostico-android/preparar_fragil_instantaneo');
const {blocoMontagens} = require('../diagnostico-android/preparar_fragil_fica');
const {formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');
const {norm} = require('../diagnostico-android/preparar_pratica_cotidiana');

const alvos = p.formulas();
assert.equal(alvos.length, 753);
assert.deepEqual([...new Set(alvos.map(d => d.c))], [89, 94, 180]);
assert.throws(() => p.prepararCodigo('outro projeto'), /PR80/);

if (process.argv[2]) {
  const dir = process.argv[2];
  const antigas = p.formulas(dir + '/base/apps-script');
  for (const locale of ['pt_BR', 'en_US']) {
    const snapshot = {locale, cells: antigas.map(({aba, r, c, depois}) => ({
      aba, r, c, sheetId: 40, value: formulaLocal(depois, locale),
    }))};
    const plano = p.prepararCelulas(snapshot);
    const reversao = plano.reverter(plano.final);
    assert.equal(plano.pedidos.length, alvos.length);
    assert.equal(reversao.length, alvos.length);
    for (const [i, {r, c, depois}] of alvos.entries()) {
      const pedido = plano.pedidos[i].updateCells;
      assert.equal(pedido.fields, 'userEnteredValue');
      assert.deepEqual(pedido.start, {sheetId: 40, rowIndex: r - 1, columnIndex: c - 1});
      assert.equal(pedido.rows[0].values[0].userEnteredValue.formulaValue,
        norm(formulaLocal(depois, locale)));
      assert.equal(reversao[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue,
        snapshot.cells[i].value);
    }
    const alterado = structuredClone(snapshot);
    alterado.cells.at(-1).value = '=TRUE';
    assert.throws(() => p.prepararCelulas(alterado), /anteriores divergentes/);
    assert.throws(() => plano.reverter(alterado), /Célula divergente/);
  }
  const anterior = fs.readFileSync(dir + '/../instalacao-restricoes-agrupadas/Codigo-PR80.gs', 'utf8');
  const proposto = p.prepararCodigo(anterior);
  new vm.Script(proposto);
  assert.notEqual(blocoMontagens(proposto), blocoMontagens(anterior));
  assert.equal(proposto.replace(blocoMontagens(proposto), ''), anterior.replace(blocoMontagens(anterior), ''));
}
console.log(JSON.stringify({resultado: 'OK', alvos: alvos.length, transportePrivado: !!process.argv[2]}));
