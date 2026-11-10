'use strict';
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const { ler, expandir } = require('./expansao_domada_modelo');
const p = require('../diagnostico-android/preparar_buff_decimal');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/buff_decimal_delta.json');

// O plano: 206 fórmulas, só a troca do leitor, nas abas esperadas.
const porAba = {};
for (const d of delta) porAba[d.aba] = (porAba[d.aba] || 0) + 1;
assert.deepEqual(porAba, { FICHA: 11, DADOS_AM: 5, DADOS_INVOC: 168, DADOS_CONFIG: 22 });
assert.equal(new Set(delta.map(d => d.aba + '!' + d.r + ',' + d.c)).size, delta.length);
for (const d of delta) assert.equal(p.explicar(d.antes), d.depois, 'Fora do leitor em ' + d.aba + '!' + d.r + ',' + d.c);
// Entidades: as 12 linhas, 14 Buff/Debuff cada (5 atributos, 5 estatísticas, 4 TR).
const invoc = delta.filter(d => d.aba === 'DADOS_INVOC');
for (let r = 2; r <= 13; r++) assert.equal(invoc.filter(d => d.r === r).length, 14, 'Entidade da linha ' + r);
// Os 11 Buff/Debuff da FICHA aparecem todos.
const lidos = new Set();
for (const d of delta) for (const m of d.depois.matchAll(/ISTEXT\('?(?:FICHA'?!)?\$([A-Z]+)\$(\d+)\)/g)) if (d.aba !== 'DADOS_INVOC') lidos.add(m[1] + m[2]);
assert.deepEqual([...lidos].sort(), [...p.BUFFS_FICHA].sort());

// O gerador Python e o plano escrevem o mesmo leitor.
const py = execFileSync('python3', ['-c', 'import sys; sys.path.insert(0, sys.argv[1]); from leitura_buff import buff; print(buff("$X$9"))',
  path.join(__dirname, '../../ficha-v01')], { encoding: 'utf8' }).trim();
assert.equal(py, p.leitor('$X$9'));

// O modelo gerado bate com o depois; a camada se descasca de volta ao antes, atomicamente.
const abas = ler('apps-script');
for (const d of delta) assert.equal(expandir(abas.find(a => a.nome === d.aba)).get(d.r + ':' + d.c), d.depois);
const errado = structuredClone(abas);
// Estraga a última célula da FICHA: as outras abas já conferidas não podem ficar meio revertidas.
const ultima = delta.filter(d => d.aba === 'FICHA').at(-1);
const alvo = errado.find(a => a.nome === 'FICHA').vals.find(v => v[0] === ultima.r && v[1] === ultima.c);
assert.ok(alvo, 'Célula da FICHA fora dos valores explícitos');
alvo[2] = '=99';
const copia = JSON.stringify(errado);
assert.throws(() => p.reverterModelo(errado), /Buff decimal divergente/);
assert.equal(JSON.stringify(errado), copia, 'Reversão parcial');
p.reverterModelo(abas);
for (const d of delta) assert.equal(expandir(abas.find(a => a.nome === d.aba)).get(d.r + ':' + d.c), d.antes);
assert.throws(() => p.reverterModelo(abas), /Buff decimal divergente/);

// Instalação: aplicar e reverter nas duas localidades, recusando célula divergente.
const ids = { FICHA: 1, DADOS_AM: 2, DADOS_INVOC: 3, DADOS_CONFIG: 4 };
for (const locale of ['pt_BR', 'en_US']) {
  const snap = fase => ({ locale, sheetIds: ids, cells: delta.map(d => ({ aba: d.aba, r: d.r, c: d.c, value: formulaLocal(d[fase], locale) })) });
  const aplicar = p.pedidos(delta, snap('antes'));
  const reverter = p.pedidos(delta, snap('depois'), true);
  assert.equal(aplicar.length, 206);
  assert.equal(reverter.length, 206);
  for (const [i, d] of delta.entries()) {
    assert.deepEqual(aplicar[i].updateCells.start, { sheetId: ids[d.aba], rowIndex: d.r - 1, columnIndex: d.c - 1 });
    assert.equal(aplicar[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.depois, locale));
    assert.equal(reverter[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.antes, locale));
  }
  // A vírgula dentro do regex fica intacta no pt_BR.
  assert.ok(aplicar[0].updateCells.rows[0].values[0].userEnteredValue.formulaValue.includes('"[.,][0-9]*[1-9]"'));
  const divergente = snap('antes');
  divergente.cells[5].value = '=99';
  assert.throws(() => p.pedidos(delta, divergente), /Célula divergente/);
}

// A regra, como o leitor a calcula (espelho em JS; o Sheets foi ensaiado nas QAs).
function regra(v) {
  if (typeof v === 'string') {
    if (!new RegExp('^[+-]?[0-9]+([.,][0-9]+)?$').test(v)) return 0;
    const n = Number(/[0-9]+/.exec(v)[0]), q = /[.,][0-9]*[1-9]/.test(v) ? 1 : 0;
    return v[0] === '-' ? -n - q : Math.max(n, q);
  }
  const n = Number(v) || 0;
  return n > 0 ? Math.max(1, Math.floor(n)) : Math.floor(n);
}
for (const [v, esperado] of [[2, 2], [-3, -3], [0, 0], [1.5, 1], [0.5, 1], [-1.5, -2], [-0.5, -1], ['2', 2], ['+2', 2], ['-2', -2],
  ['1,5', 1], ['1.5', 1], ['0,5', 1], ['-1,5', -2], ['-0,5', -1], ['1,0', 1], ['1/2', 0], ['', 0], ['abc', 0], [' 2', 0], [null, 0]]) {
  assert.equal(regra(v), esperado, JSON.stringify(v));
}
console.log('Buff/Debuff decimal: 206 alvos (11 da FICHA, 168 das entidades), modelo, reversão e instalação em pt_BR e en_US.');
