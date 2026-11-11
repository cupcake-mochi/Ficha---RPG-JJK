'use strict';
const assert = require('node:assert/strict');
const { ler, expandir } = require('./expansao_domada_modelo');
const { valores, pedidos } = require('../diagnostico-android/preparar_buffs_entidades');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/buffs_entidades_delta.json');

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
  assert.equal(aplicar.length, 168);
  assert.equal(reverter.length, 168);
  for (const [i, d] of delta.entries()) {
    assert.deepEqual(aplicar[i].updateCells.start, { sheetId: 1, rowIndex: d.r - 1, columnIndex: d.c - 1 });
    assert.equal(aplicar[i].updateCells.fields, 'userEnteredValue');
    assert.deepEqual(aplicar[i].updateCells.rows[0].values[0], depois.cells[chave(d)]);
    assert.deepEqual(reverter[i].updateCells.rows[0].values[0], antes.cells[chave(d)]);
  }
  antes.cells['DADOS_INVOC!DQ2'].userEnteredValue.formulaValue = '=99';
  assert.throws(() => pedidos(delta, antes), /Célula divergente: DADOS_INVOC!2,121/);
}

// Antes: =N(ref). Depois: inteiro ASCII com sinal opcional em texto vale o número; o resto, como antes.
const molde = /^=IF\(ISTEXT\((.+?)\),IF\(REGEXMATCH\(\1,"\^\[\+-\]\?\[0-9\]\+\$"\),VALUE\(SUBSTITUTE\(\1,"\+",""\)\),0\),N\(\1\)\)$/;
for (const d of delta) {
  const m = d.depois.match(molde);
  assert.ok(m, 'Fórmula fora do molde: ' + chave(d));
  assert.equal(d.antes, '=N(' + m[1] + ')', 'Referência trocada em ' + chave(d));
  assert.match(m[1], /^'INVOCAÇÕES'!\$[A-Z]+\$\d+$/);
}
assert.equal(new Set(delta.map(d => d.depois.match(molde)[1])).size, 168, 'Entradas repetidas');

// Semântica da conversão, com a mesma regex (RE2 e JS concordam neste padrão).
const N = v => (typeof v === 'number' ? v : typeof v === 'boolean' ? Number(v) : 0);
const ajuste = v => (typeof v === 'string' ? (/^[+-]?[0-9]+$/.test(v) ? Number(v.replace('+', '')) : 0) : N(v));
const casos = [
  [null, 0], ['', 0], [0, 0], ['0', 0], [2, 2], [-2, -2], [1.5, 1.5], ['2', 2], ['+2', 2], ['-2', -2],
  ['-0', 0], ['+12', 12], [' 2', 0], ['2 ', 0], ['−2', 0], ['--2', 0], ['+-2', 0], ['1,5', 0], ['1.5', 0], ['abc', 0], ['+', 0],
];
for (const [v, esperado] of casos) assert.ok(Object.is(ajuste(v) + 0, esperado + 0), JSON.stringify(v));

// O leitor de 10/11 (buff decimal) é a camada seguinte: descascada antes de comparar com este plano.
const dados = require('../diagnostico-android/preparar_buff_decimal').reverterModelo(require('../diagnostico-android/preparar_aviso_atributo').reverterModelo(require('../diagnostico-android/preparar_menu_oficios').reverterModelo(require('../diagnostico-android/preparar_especializacao').reverterModelo(ler('apps-script'))))).find(a => a.nome === 'DADOS_INVOC');
const formulas = expandir(dados);
for (const d of delta) {
  assert.equal(formulas.get(d.r + ':' + d.c), d.depois, 'Modelo e plano divergem em ' + chave(d));
}
console.log('Buff/Debuff das entidades: 168 alvos, geração, aplicação e reversão em pt_BR e en_US.');
