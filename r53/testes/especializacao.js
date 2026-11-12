'use strict';
// Especialização (11/11/2026): as 34 contas de perícia e ofício dizem "Marque o treino" com a especialização marcada
// sem o treino, e os três contadores dizem quando falta o marco de Corpo. Ver
// r53/diagnostico-android/CORRECAO-ESPECIALIZACAO-2026-11-11.md.
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { ler, expandir } = require('./expansao_domada_modelo');
const p = require('../diagnostico-android/preparar_especializacao');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/especializacao_delta.json');

// O plano: 23 perícias, 11 ofícios e 3 contadores, todos na FICHA, cada um explicado pelo molde.
assert.equal(delta.length, 37);
assert.equal(delta.filter(d => p.CONTAS[d.r + ':' + d.c]).length, 34);
assert.deepEqual(delta.filter(d => p.CONTADORES[d.r + ':' + d.c]).map(d => d.r + ':' + d.c).sort(), ['105:37', '114:32', '89:37']);
for (const d of delta) {
  assert.equal(d.aba, 'FICHA');
  assert.equal(p.explicar(d.r + ':' + d.c, d.antes), d.depois, 'Fora do molde em ' + d.r + ',' + d.c);
}
for (const d of delta.filter(d => p.CONTAS[d.r + ':' + d.c])) {
  assert.ok(d.depois.endsWith(',' + d.antes.slice(1) + ')'), 'A conta antiga segue inteira');
  const [espec, treino] = p.CONTAS[d.r + ':' + d.c].map(c => c + d.r);
  assert.ok(d.depois.startsWith(`=IF(AND(DADOS_CONFIG!$C$`) && d.depois.includes(`,${espec}=TRUE,${treino}<>TRUE),"Marque o treino",`));
}
// O ofício avisa o treino por fora do aviso de atributo; a perícia não tem menu.
assert.ok(delta.find(d => d.r === 108 && d.c === 14).depois.includes('"Marque o treino",IF(AND(DADOS_CONFIG!$C$37<>1,NOT(OR(K108="FORÇA"'));
assert.ok(delta.find(d => d.r === 80 && d.c === 16).depois.includes('"Marque o treino",IF(DADOS_CONFIG!$E$14<>"",NA(),'));
// Os contadores: nível 10 primeiro, depois o Corpo, depois o "a mais" de sempre.
const curto = delta.find(d => d.r === 89 && d.c === 37).depois;
assert.ok(curto.indexOf('só no nível 10') < curto.indexOf('sem marco de Corpo') && curto.indexOf('sem marco de Corpo') < curto.indexOf('" a mais"'));
assert.ok(delta.find(d => d.r === 105 && d.c === 37).depois.includes('" sem marco de Corpo: escolha Corpo no Marco Escolhido ou tire a marcação"'));

// O modelo gerado bate com o depois; a camada se descasca de volta ao antes, atomicamente.
const abas = require('../diagnostico-android/preparar_texto_extra').reverterModelo(require('../diagnostico-android/preparar_corte_xp_missao').reverterModelo(ler('apps-script')));
const ficha = () => expandir(abas.find(a => a.nome === 'FICHA'));
for (const d of delta) assert.equal(ficha().get(d.r + ':' + d.c), d.depois, 'Modelo e plano divergem');
const errado = structuredClone(abas);
const ultima = delta[delta.length - 1];
errado.find(a => a.nome === 'FICHA').vals.find(v => v[0] === ultima.r && v[1] === ultima.c)[2] = '=99';
const copia = JSON.stringify(errado);
assert.throws(() => p.reverterModelo(errado), /Especialização divergente/);
assert.equal(JSON.stringify(errado), copia, 'Reversão parcial');
p.reverterModelo(abas);
for (const d of delta) assert.equal(ficha().get(d.r + ':' + d.c), d.antes);
assert.throws(() => p.reverterModelo(abas), /Especialização divergente/);

// O gerador Python desfaz o aviso exato (comparadores da configuração) e recusa um adulterado.
const py = `
import json, sys
sys.path.insert(0, 'ficha-v01')
import configuracao as c
delta = [d for d in json.load(open('r53/diagnostico-android/especializacao_delta.json')) if 'Marque o treino' in d['depois']]
assert len(delta) == 34
for d in delta:
    assert c.anterior(d['depois']) == c.anterior(d['antes']), (d['r'], d['c'])
p80 = [d for d in delta if d['r'] == 80 and d['c'] == 16][0]['depois']
o108 = [d for d in delta if d['r'] == 108 and d['c'] == 14][0]['depois']
for ruim in (p80.replace('E80=TRUE', 'E81=TRUE', 1), p80.replace('D80<>TRUE', 'D81<>TRUE', 1),
             p80.replace('$C$14<>1', '$C$15<>1', 1), o108.replace('E108=TRUE', 'R108=TRUE', 1)):
    assert ruim not in (p80, o108)
    try:
        c.anterior(ruim)
    except ValueError:
        pass
    else:
        raise SystemExit('aviso adulterado aceito')
print('ok')
`;
const python = require('node:fs').existsSync('.venv/bin/python') ? '.venv/bin/python' : 'python3';
assert.equal(execFileSync(python, ['-c', py], { encoding: 'utf8' }).trim(), 'ok');

// Instalação: aplicar e reverter nas duas localidades, recusando célula divergente.
for (const locale of ['pt_BR', 'en_US']) {
  const snap = fase => ({ locale, sheetIds: { FICHA: 1 }, cells: delta.map(d => ({ aba: d.aba, r: d.r, c: d.c, value: formulaLocal(d[fase], locale) })) });
  const aplicar = p.pedidos(delta, snap('antes'));
  const reverter = p.pedidos(delta, snap('depois'), true);
  assert.equal(aplicar.length, 37);
  for (const [i, d] of delta.entries()) {
    assert.deepEqual(aplicar[i].updateCells.start, { sheetId: 1, rowIndex: d.r - 1, columnIndex: d.c - 1 });
    assert.equal(aplicar[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.depois, locale));
    assert.equal(reverter[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.antes, locale));
  }
  const divergente = snap('antes');
  divergente.cells[5].value = '=99';
  assert.throws(() => p.pedidos(delta, divergente), /Célula divergente/);
}

// A regra: só especialização marcada sem treino avisa; texto colado não conta como marcado; valor fixo nunca avisa.
const avisa = (espec, treino, fixo) => !fixo && espec === true && treino !== true;
const casos = [[true, false, false, true], [true, '', false, true], [true, true, false, false], [false, false, false, false],
  ['x', false, false, false], [true, false, true, false]];
for (const [espec, treino, fixo, esperado] of casos) assert.equal(avisa(espec, treino, fixo), esperado, JSON.stringify([espec, treino, fixo]));
// O Corpo: avisa quando há mais especializações que marcos de Corpo, antes do "a mais".
const contador = (esp, corpo, nivel, aMais) => esp > 0 && nivel < 10 ? 'nível' : esp > corpo ? 'Corpo' : aMais > 0 ? 'a mais' : 'normal';
assert.equal(contador(1, 0, 10, 1), 'Corpo');
assert.equal(contador(1, 1, 10, 1), 'a mais');
assert.equal(contador(1, 0, 9, 1), 'nível');
assert.equal(contador(0, 0, 10, 0), 'normal');

console.log('Especialização: 34 avisos de treino, 3 contadores do Corpo, geração, reversão atômica, anterior do Python e pedidos em pt_BR e en_US.');
