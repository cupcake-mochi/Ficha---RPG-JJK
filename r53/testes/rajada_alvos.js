'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const zlib = require('node:zlib');
const p = require('../diagnostico-android/preparar_rajada_alvos');
const {formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');
const {norm} = require('../diagnostico-android/preparar_pratica_cotidiana');
const {formulas} = require('../rajada_alvos');
const rt = require('../pratica_cotidiana_runtime');

// 26/11/2026 (etapa 4 da versão rápida): nenhuma linha tem mais montagem (o personagem saiu na etapa 3, as invocações
// nesta). A rajada não tem alvo, e a restauração da prática cotidiana não escreve nada nem carrega o pacote.
const alvos = formulas();
assert.equal(alvos.length, 0);
assert.equal(formulas(undefined, rt.colunasMontagem).length, 0);
let loads = 0;
const ctx = vm.createContext({
  Utilities: {
    base64Decode: s => Buffer.from(s, 'base64'),
    newBlob: x => x,
    ungzip: x => {
      loads++;
      return {getDataAsString: () => zlib.gunzipSync(x).toString()};
    },
  },
  r53CargaFormulaNoIdioma_: formulaLocal,
});
vm.runInContext(rt.gerar(), ctx);
const writes = new Map();
function editar(aba, r, c, rr = r, cc = c) {
  writes.clear();
  return ctx.r53PraticaRestaurar_({range: {
    getRow: () => r,
    getLastRow: () => rr,
    getColumn: () => c,
    getLastColumn: () => cc,
    getSheet: () => ({
      getName: () => aba,
      getParent: () => ({getSpreadsheetLocale: () => 'pt_BR'}),
      getRange: (row, col) => ({
        setValues: values => values.forEach((line, y) => line.forEach((v, x) => writes.set((row + y) + ':' + (col + x), v))),
      }),
    }),
  }});
}
assert.equal(editar('FICHA', 2, 89), false);
assert.equal(editar('DADOS_R53', 2, 89, 253, 181), false);
assert.equal(writes.size, 0);
assert.equal(editar('DADOS_R53', 47, 104), false);
assert.equal(writes.size, 0);

assert.throws(() => p.prepararCodigo('outro projeto'), /PR75/);
if (process.argv[2]) {
  const dir = process.argv[2];
  const base = formulas(dir + '/base/apps-script');
  for (const locale of ['pt_BR', 'en_US']) {
    const snapshot = {locale, cells: base.map(d => ({
      ...d, sheetId: 40, value: formulaLocal(d.depois, locale),
    }))};
    const plano = p.prepararCelulas(snapshot);
    assert.equal(plano.pedidos.length, alvos.length);
    assert.equal(plano.reverter(plano.final).length, alvos.length);
    for (const [i, q] of plano.pedidos.entries()) {
      const d = alvos[i];
      assert.notEqual(snapshot.cells[i].value, formulaLocal(d.depois, locale));
      assert.equal(q.updateCells.fields, 'userEnteredValue');
      assert.equal(q.updateCells.start.rowIndex, d.r - 1);
      assert.equal(q.updateCells.start.columnIndex, d.c - 1);
      assert.equal(q.updateCells.rows[0].values[0].userEnteredValue.formulaValue,
        norm(formulaLocal(d.depois, locale)));
    }
    const alterado = structuredClone(snapshot);
    alterado.cells.at(-1).value = '=TRUE';
    assert.throws(() => p.prepararCelulas(alterado), /anteriores divergentes/);
    assert.throws(() => plano.reverter(alterado), /Célula divergente/);
  }
  for (const ficha of ['era', 'ciclo']) {
    const src = fs.readFileSync(dir + '/../correcao-tempo-feiticos/' + ficha + '-Codigo-relido.gs', 'utf8');
    new vm.Script(p.prepararCodigo(src));
  }
}
console.log(JSON.stringify({resultado:'OK', alvos:alvos.length, transportePrivado:!!process.argv[2]}));
