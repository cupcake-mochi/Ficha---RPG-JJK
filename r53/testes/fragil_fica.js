'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const p = require('../diagnostico-android/preparar_fragil_fica');
const {formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');
const {norm} = require('../diagnostico-android/preparar_pratica_cotidiana');

const alvos = p.formulas();
assert.equal(alvos.length, 753);
assert.deepEqual([...new Set(alvos.map(d => d.c))], [89, 94, 180]);
assert.ok(alvos.every(d => d.aba === 'DADOS_R53' && d.r !== 251));
assert.throws(() => p.prepararCodigo('outro projeto'), /PR76/);

if (process.argv[2]) {
  const dir = process.argv[2];
  const antes = p.formulas(dir + '/base/apps-script');
  for (const locale of ['pt_BR', 'en_US']) {
    const snapshot = {locale, cells: antes.map(d => ({
      aba: d.aba, r: d.r, c: d.c, sheetId: 40, value: formulaLocal(d.depois, locale),
    }))};
    const plano = p.prepararCelulas(snapshot);
    const reversao = plano.reverter(plano.final);
    assert.equal(plano.pedidos.length, 753);
    assert.equal(reversao.length, 753);
    for (const [i, pedido] of plano.pedidos.entries()) {
      const d = alvos[i];
      const q = pedido.updateCells;
      assert.deepEqual(q.start, {sheetId: 40, rowIndex: d.r - 1, columnIndex: d.c - 1});
      assert.equal(q.fields, 'userEnteredValue');
      const depois = norm(formulaLocal(d.depois, locale));
      assert.notEqual(norm(snapshot.cells[i].value), depois);
      assert.equal(q.rows[0].values[0].userEnteredValue.formulaValue, depois);
      assert.equal(reversao[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue,
        snapshot.cells[i].value);
    }
    const alterado = structuredClone(snapshot);
    alterado.cells.at(-1).value = '=TRUE';
    assert.throws(() => p.prepararCelulas(alterado), /anteriores divergentes/);
    assert.throws(() => plano.reverter(alterado), /Célula divergente/);
  }
  const bloco = /^function r53PraticaMontagem_\(\)\{[^\n]+\}$/m;
  for (const ficha of ['era', 'ciclo']) {
    const src = fs.readFileSync(dir + '/../instalacao-rajada-alvos/' + ficha + '-Codigo-proposto.gs', 'utf8');
    const novo = p.prepararCodigo(src);
    new vm.Script(novo);
    assert.notEqual(novo, src);
    assert.equal(novo.replace(bloco, ''), src.replace(bloco, ''));
  }
}
console.log(JSON.stringify({resultado: 'OK', alvos: alvos.length, transportePrivado: !!process.argv[2]}));
