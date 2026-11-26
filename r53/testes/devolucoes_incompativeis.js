'use strict';
// 26/11/2026 (etapa 4 da versão rápida): nenhuma linha tem mais montagem na DADOS_R53 (as invocações também saíram)
// 26/11/2026 (etapa 3 da versão rápida): só as linhas das invocações (47 a 250) têm montagem na DADOS_R53

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const zlib = require('node:zlib');
const p = require('../diagnostico-android/preparar_devolucoes_incompativeis');
const {blocoMontagens} = require('../diagnostico-android/preparar_fragil_fica');
const {formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');
const {gerar} = require('../pratica_cotidiana_runtime');

const alvos = p.formulas();
assert.equal(alvos.length, 0);
assert.deepEqual([...new Set(alvos.map(d => d.c))], []);
assert.ok(alvos.every(d => d.aba === 'DADOS_R53' && d.r !== 251));
assert.throws(() => p.prepararCodigo('outro projeto'), /PR78/);

// 26/11/2026 (etapa 4): sem montagem nenhuma, o código da Prática não leva mais a recuperação das montagens.
assert.throws(() => blocoMontagens(gerar()), /Recuperação de montagens ausente/);

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
  const src = fs.readFileSync(dir + '/../instalacao-sem-volta/era-Codigo-proposto.gs', 'utf8');
  const novo = p.prepararCodigo(src);
  new vm.Script(novo);
  assert.notEqual(novo, src);
  assert.equal(novo.replace(blocoMontagens(novo), ''), src.replace(blocoMontagens(src), ''));
}
console.log(JSON.stringify({resultado: 'OK', alvos: alvos.length, transportePrivado: !!process.argv[2]}));
