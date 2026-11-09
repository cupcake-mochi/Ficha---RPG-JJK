'use strict';
const assert = require('node:assert/strict');
const { ler, expandir } = require('./expansao_domada_modelo');
const { valores, pedidos } = require('../diagnostico-android/preparar_tr_treinado');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/tr_treinado_delta.json');

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
  antes.cells['DADOS_INVOC!HG2'].userEnteredValue.formulaValue = '=99';
  assert.throws(() => pedidos(delta, antes), /Célula divergente: DADOS_INVOC!2,215/);
}

const dados = ler('apps-script').find(a => a.nome === 'DADOS_INVOC');
const formulas = expandir(dados);
const TESTES = ['Físico', 'Vigor', 'Intelecto', 'Espírito'];
const colunasTr = new Set();
for (const d of delta) {
  assert.equal(d.c, 215);
  const r = d.r;
  // Depois = antes + o pedido de revisão logo antes do nível; a caixa é a mesma que dá a maestria aos quatro TR.
  const m = d.depois.match(new RegExp(`IF\\(OR\\(\\$([A-Z]+)${r}="Físico"`));
  assert.ok(m, 'Sem a conferência do TR em ' + chave(d));
  const T = '$' + m[1] + r;
  colunasTr.add(m[1]);
  const revisao = `&IF(OR(${TESTES.map(t => `${T}="${t}"`).join(',')}),""," · REVISAR: escolha o TR treinado")`;
  const marca = '&" · nível "';
  assert.equal(d.antes.split(marca).length, 2, 'Marca do nível ausente ou repetida em ' + chave(d));
  assert.equal(d.depois, d.antes.replace(marca, revisao + marca), 'Depois fora do molde em ' + chave(d));
  const daLinha = [...formulas].filter(([k]) => k.startsWith(r + ':')).map(([, f]) => f).filter(f => typeof f === "string");
  for (const t of TESTES) {
    assert.ok(daLinha.some(f => f.includes(`IF(${T}="${t}",`)), `A caixa ${T} não dá a maestria ao TR ${t}`);
  }
  assert.equal(formulas.get(r + ':' + d.c), d.depois, 'Modelo e plano divergem em ' + chave(d));
}
assert.equal(colunasTr.size, 1, 'TR treinado em colunas diferentes');

// Semântica, como o "=" do Sheets compara texto: sem diferenciar maiúsculas, com acento e espaço contando.
const valido = v => typeof v === 'string' && TESTES.some(t => t.toLowerCase() === v.toLowerCase());
for (const [v, esperado] of [['Físico', true], ['Espírito', true], ['físico', true], ['', false], [null, false],
  ['Fisico', false], [' Vigor', false], [3, false]]) {
  assert.equal(valido(v), esperado, JSON.stringify(v));
}
console.log('TR treinado das entidades: 12 alvos, geração, aplicação e reversão em pt_BR e en_US.');
