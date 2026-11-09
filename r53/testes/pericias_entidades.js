'use strict';
const assert = require('node:assert/strict');
const { ler, expandir } = require('./expansao_domada_modelo');
const { pedidos } = require('../diagnostico-android/preparar_pericias_entidades');
const { coordenadas, formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/pericias_entidades_delta.json');

const sheetIds = { DADOS_INVOC: 1, 'INVOCAÇÕES': 2 };
const chave = d => d.aba + '!' + d.a1;
function snapshot(locale, fase) {
  const cells = Object.fromEntries(delta.map(d => [chave(d),
    d.campo === 'nota' ? { note: d[fase] } : { userEnteredValue: { formulaValue: formulaLocal(d[fase], locale) } },
  ]));
  return { locale, sheetIds, cells };
}

for (const locale of ['pt_BR', 'en_US']) {
  const antes = snapshot(locale, 'antes');
  const depois = snapshot(locale, 'depois');
  const instalar = pedidos(delta, antes);
  const reverter = pedidos(delta, depois, true);
  assert.equal(instalar.length, 25);
  assert.equal(reverter.length, 25);
  assert.equal(pedidos(delta, depois).length, 0);
  assert.equal(pedidos(delta, antes, true).length, 0);
  const relido = structuredClone(depois);
  const formula = relido.cells['DADOS_INVOC!GU2'].userEnteredValue;
  formula.formulaValue = formula.formulaValue.replace('$EQ2:$EQ2', '$EQ2').replace('$HU2:$HU2', '$HU2');
  assert.notEqual(formula.formulaValue, depois.cells['DADOS_INVOC!GU2'].userEnteredValue.formulaValue);
  assert.equal(pedidos(delta, relido).length, 0);
  for (const [i, d] of delta.entries()) {
    const campo = d.campo === 'nota' ? 'note' : 'userEnteredValue';
    assert.equal(instalar[i].updateCells.fields, campo);
    assert.deepEqual(instalar[i].updateCells.rows[0].values[0], depois.cells[chave(d)]);
    assert.deepEqual(reverter[i].updateCells.rows[0].values[0], antes.cells[chave(d)]);
  }
  antes.cells['DADOS_INVOC!GU2'].userEnteredValue.formulaValue = '=99';
  assert.throws(() => pedidos(delta, antes), /Estado divergente: DADOS_INVOC!GU2/);
}

const modelo = ler('apps-script');
const invocacoes = expandir(modelo.find(a => a.nome === 'DADOS_INVOC'));
const notas = new Map(modelo.find(a => a.nome === 'INVOCAÇÕES').notas);
for (const d of delta) {
  const { r, c } = coordenadas({ addr: d.a1 });
  const atual = d.campo === 'nota' ? notas.get(d.a1) : invocacoes.get(r + ':' + c);
  assert.equal(atual, d.depois, 'Geração e plano divergem em ' + chave(d));
}
console.log('Perícias das entidades: 25 alvos, instalação e reversão em dois idiomas, recusa de divergência.');
