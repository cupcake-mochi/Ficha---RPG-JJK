'use strict';
// Menu de atributo sem #N/A (10/11/2026): CD, Conjuração, Corpo a corpo e À distância dizem "Escolha o atributo"
// quando o menu está vazio ou fora dos cinco nomes. Ver r53/diagnostico-android/CORRECAO-AVISO-ATRIBUTO-2026-11-10.md.
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { ler, expandir } = require('./expansao_domada_modelo');
const p = require('../diagnostico-android/preparar_aviso_atributo');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/aviso_atributo_delta.json');

// O plano: as quatro caixas da linha 63, cada uma explicada pelo aviso do seu menu.
assert.deepEqual(delta.map(d => d.aba + '!' + d.r + ',' + d.c), ['FICHA!63,4', 'FICHA!63,15', 'FICHA!63,26', 'FICHA!63,37']);
for (const d of delta) assert.equal(p.explicar(d.r + ':' + d.c, d.antes), d.depois, 'Fora do aviso em ' + d.r + ',' + d.c);
for (const d of delta) {
  const [menu, linha] = p.ALVOS[d.r + ':' + d.c];
  assert.ok(d.depois.startsWith(`=IF(${p.invalido(menu, linha)},"Escolha o atributo",IF(DADOS_CONFIG!$E$${linha}<>"",NA(),`));
  assert.ok(d.depois.endsWith(',' + d.antes.slice(1) + ')'), 'A conta antiga segue inteira dentro do aviso');
}

// O modelo gerado bate com o depois; a camada se descasca de volta ao antes, atomicamente.
const abas = ler('apps-script');
const ficha = () => expandir(abas.find(a => a.nome === 'FICHA'));
for (const d of delta) assert.equal(ficha().get(d.r + ':' + d.c), d.depois, 'Modelo e plano divergem');
const errado = structuredClone(abas);
const ultima = delta[delta.length - 1];
const alvo = errado.find(a => a.nome === 'FICHA').vals.find(v => v[0] === ultima.r && v[1] === ultima.c);
alvo[2] = '=99';
const copia = JSON.stringify(errado);
assert.throws(() => p.reverterModelo(errado), /Aviso de atributo divergentes/);
assert.equal(JSON.stringify(errado), copia, 'Reversão parcial');
p.reverterModelo(abas);
for (const d of delta) assert.equal(ficha().get(d.r + ':' + d.c), d.antes);
assert.throws(() => p.reverterModelo(abas), /Aviso de atributo divergentes/);

// O gerador Python desfaz o aviso exato (comparadores da configuração) e recusa um adulterado.
const py = `
import json, sys
sys.path.insert(0, 'ficha-v01')
import configuracao as c
delta = json.load(open('r53/diagnostico-android/aviso_atributo_delta.json'))
for d in delta:
    assert c.anterior(d['depois']) == c.anterior(d['antes']), (d['r'], d['c'])
ruim = delta[0]['depois'].replace('"ESSÊNCIA"', '"SABEDORIA"')
try:
    c.anterior(ruim)
except ValueError:
    pass
else:
    raise SystemExit('aviso adulterado aceito')
print('ok')
`;
assert.equal(execFileSync('python3', ['-c', py], { encoding: 'utf8' }).trim(), 'ok');

// Instalação: aplicar e reverter nas duas localidades, recusando célula divergente.
for (const locale of ['pt_BR', 'en_US']) {
  const snap = fase => ({ locale, sheetIds: { FICHA: 1 }, cells: delta.map(d => ({ aba: d.aba, r: d.r, c: d.c, value: formulaLocal(d[fase], locale) })) });
  const aplicar = p.pedidos(delta, snap('antes'));
  const reverter = p.pedidos(delta, snap('depois'), true);
  assert.equal(aplicar.length, 4);
  for (const [i, d] of delta.entries()) {
    assert.deepEqual(aplicar[i].updateCells.start, { sheetId: 1, rowIndex: d.r - 1, columnIndex: d.c - 1 });
    assert.equal(aplicar[i].updateCells.fields, 'userEnteredValue');
    assert.equal(aplicar[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.depois, locale));
    assert.equal(reverter[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.antes, locale));
  }
  const divergente = snap('antes');
  divergente.cells[2].value = '=99';
  assert.throws(() => p.pedidos(delta, divergente), /Célula divergente/);
}

// A regra: o Sheets compara texto sem caixa, então só nome fora da lista (ou vazio) avisa; valor fixo nunca avisa.
const avisa = (menu, fixo) => !fixo && !p.ATRIBUTOS.some(a => a.toLowerCase() === String(menu).toLowerCase());
const casos = [['FORÇA', false, false], ['força', false, false], ['ESSÊNCIA', false, false], ['', false, true],
  ['FORCA', false, true], ['Sabedoria', false, true], ['', true, false]];
for (const [menu, fixo, esperado] of casos) assert.equal(avisa(menu, fixo), esperado, JSON.stringify([menu, fixo]));

console.log('Aviso de atributo: quatro caixas, geração, reversão atômica, anterior do Python e pedidos em pt_BR e en_US.');
