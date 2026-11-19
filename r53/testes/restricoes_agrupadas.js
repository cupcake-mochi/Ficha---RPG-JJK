'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const zlib = require('node:zlib');
const p = require('../diagnostico-android/preparar_restricoes_agrupadas');
const {blocoRecuperacao} = p;
const {formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');
const {norm} = require('../diagnostico-android/preparar_pratica_cotidiana');
const {gerar} = require('../pratica_cotidiana_runtime');

const alvos = p.formulas();
assert.equal(alvos.length, 753);
assert.deepEqual([...new Set(alvos.map(d => d.c))], [89, 94, 104]);
assert.ok(alvos.every(d => d.aba === 'DADOS_R53' && d.r !== 251));
assert.throws(() => p.prepararCodigo('outro projeto'), /PR79/);

const runtime = blocoRecuperacao(gerar());
const base64 = /^function r53PraticaMontagem_.*base64Decode\("([^"]+)"\)/m.exec(runtime)[1];
const recuperadas = new Map();
for (const [coluna, molde, linhas] of JSON.parse(zlib.gunzipSync(Buffer.from(base64, 'base64')))) {
  for (const linha of linhas) recuperadas.set(linha + ':' + coluna, molde.replace(/\x01/g, String(linha)));
}
for (const {r, c, depois} of alvos) assert.equal(recuperadas.get(r + ':' + c), depois);

if (process.argv[2]) {
  const dir = process.argv[2];
  const antes = p.formulas(dir + '/base/apps-script');
  for (const locale of ['pt_BR', 'en_US']) {
    const snapshot = {locale, cells: antes.map(d => ({
      aba: d.aba, r: d.r, c: d.c, sheetId: 40, value: formulaLocal(d.depois, locale),
    }))};
    const plano = p.prepararCelulas(snapshot);
    const reversao = plano.reverter(plano.final);
    assert.equal(plano.pedidos.length, alvos.length);
    assert.equal(reversao.length, alvos.length);
    for (const [i, pedido] of plano.pedidos.entries()) {
      const {r, c} = alvos[i];
      const formula = pedido.updateCells.rows[0].values[0].userEnteredValue.formulaValue;
      assert.equal(formula, norm(formulaLocal(alvos[i].depois, locale)));
      assert.deepEqual(pedido.updateCells.start, {sheetId: 40, rowIndex: r - 1, columnIndex: c - 1});
      assert.equal(pedido.updateCells.fields, 'userEnteredValue');
      assert.notEqual(formula, snapshot.cells[i].value);
      assert.equal(reversao[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue,
        snapshot.cells[i].value);
    }
    const alterado = structuredClone(snapshot);
    alterado.cells.at(-1).value = '=TRUE';
    assert.throws(() => p.prepararCelulas(alterado), /anteriores divergentes/);
    assert.throws(() => plano.reverter(alterado), /Célula divergente/);
  }
  const src = fs.readFileSync(dir + '/../instalacao-devolucoes-incompativeis/Codigo-PR79.gs', 'utf8');
  const novo = p.prepararCodigo(src);
  new vm.Script(novo);
  assert.notEqual(novo, src);
  assert.equal(novo.replace(blocoRecuperacao(novo), ''), src.replace(blocoRecuperacao(src), ''));
}
console.log(JSON.stringify({resultado: 'OK', alvos: alvos.length, transportePrivado: !!process.argv[2]}));
