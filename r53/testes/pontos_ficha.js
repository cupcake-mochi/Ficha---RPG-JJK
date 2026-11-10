'use strict';
// Ponto fora de 0 a 6 na FICHA do jogador (10/11/2026): Z15 e AK14 acusam ponto negativo, fracionado ou acima
// do teto, sem reescrever a entrada. Ver r53/diagnostico-android/CORRECAO-PONTOS-FICHA-2026-11-10.md.
const assert = require('node:assert/strict');
const { ler, expandir } = require('./expansao_domada_modelo');
const p = require('../diagnostico-android/preparar_pontos_ficha');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/pontos_ficha_delta.json');

// O plano: só Z15 e AK14 da FICHA, cada um explicado pelo aviso.
assert.deepEqual(delta.map(d => d.aba + '!' + d.r + ',' + d.c).sort(), ['FICHA!14,37', 'FICHA!15,26']);
for (const d of delta) assert.equal(p.explicar(d.r + ':' + d.c, d.antes), d.depois, 'Fora do aviso em ' + d.r + ',' + d.c);
const z15 = delta.find(d => d.c === 26), ak14 = delta.find(d => d.c === 37);
assert.ok(z15.depois.includes('"Ponto fora de 0 a "&DADOS_CONFIG!$S$5'), 'Z15 segue o teto da campanha');
for (const c of p.PONTOS) assert.ok(z15.depois.includes(`$${c.replace(/\d+$/, '')}$21`), 'Z15 lê ' + c);
for (const c of p.CORPO) assert.ok(ak14.depois.includes(`$${c.replace(/\d+$/, '')}$15`), 'AK14 lê ' + c);
assert.ok(ak14.depois.includes('"Ponto fora de 0 a 6"'));

// O modelo gerado bate com o depois; a camada se descasca de volta ao antes, atomicamente.
const abas = ler('apps-script');
const ficha = () => expandir(abas.find(a => a.nome === 'FICHA'));
for (const d of delta) assert.equal(ficha().get(d.r + ':' + d.c), d.depois, 'Modelo e plano divergem');
const errado = structuredClone(abas);
const alvo = errado.find(a => a.nome === 'FICHA').vals.find(v => v[0] === ak14.r && v[1] === ak14.c);
alvo[2] = '=99';
const copia = JSON.stringify(errado);
assert.throws(() => p.reverterModelo(errado), /Pontos da ficha divergentes/);
assert.equal(JSON.stringify(errado), copia, 'Reversão parcial');
p.reverterModelo(abas);
for (const d of delta) assert.equal(ficha().get(d.r + ':' + d.c), d.antes);
assert.throws(() => p.reverterModelo(abas), /Pontos da ficha divergentes/);

// Instalação: aplicar e reverter nas duas localidades, recusando célula divergente.
for (const locale of ['pt_BR', 'en_US']) {
  const snap = fase => ({ locale, sheetIds: { FICHA: 1 }, cells: delta.map(d => ({ aba: d.aba, r: d.r, c: d.c, value: formulaLocal(d[fase], locale) })) });
  const aplicar = p.pedidos(delta, snap('antes'));
  const reverter = p.pedidos(delta, snap('depois'), true);
  assert.equal(aplicar.length, 2);
  for (const [i, d] of delta.entries()) {
    assert.deepEqual(aplicar[i].updateCells.start, { sheetId: 1, rowIndex: d.r - 1, columnIndex: d.c - 1 });
    assert.equal(aplicar[i].updateCells.fields, 'userEnteredValue');
    assert.equal(aplicar[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.depois, locale));
    assert.equal(reverter[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.antes, locale));
  }
  const divergente = snap('antes');
  divergente.cells[0].value = '=99';
  assert.throws(() => p.pedidos(delta, divergente), /Célula divergente/);
}

// A regra: o mesmo teste que a fórmula faz, caixa por caixa (o _N da ficha lê texto não numérico como 0).
const foraDe = (pontos, teto) => pontos.some(x => x < 0 || x > teto || x !== Math.floor(x));
const casos = [
  [[0, 0, 0, 0, 0], 6, false], [[3, 3, 3, 0, 0], 6, false], [[6, 6, 4, 0, 0], 6, false],
  [[-2, 4, 3, 3, 3], 6, true], [[2.5, 2.5, 2, 2, 2], 6, true], [[7, 3, 3, 0, 0], 6, true],
  [[46054, 0, 0, 0, 0], 6, true], // "1/2" digitado vira a data 01/02 e passava como "46052 a mais"
  [[7, 3, 3, 0, 0], 8, false], // campanha com teto 8
];
for (const [pontos, teto, esperado] of casos) assert.equal(foraDe(pontos, teto), esperado, JSON.stringify([pontos, teto]));

console.log('Pontos da ficha: Z15 e AK14, geração, reversão atômica e pedidos em pt_BR e en_US.');
