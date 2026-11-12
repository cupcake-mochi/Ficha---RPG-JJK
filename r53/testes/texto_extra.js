'use strict';
// Texto em caixa de número ou de marcar (11/11/2026): as 38 contas de perícia, ofício e TR avisam em vez de dar
// #VALUE!. Ver r53/diagnostico-android/CORRECAO-TEXTO-EXTRA-2026-11-11.md.
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { ler, expandir } = require('./expansao_domada_modelo');
const p = require('../diagnostico-android/preparar_texto_extra');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/texto_extra_delta.json');

// O plano: 23 perícias, 11 ofícios e 4 TRs, todos na FICHA, cada um explicado pelo molde.
assert.equal(delta.length, 38);
const col = c => delta.filter(d => d.c === c).length;
assert.deepEqual([col(16), col(32), col(14), col(27), col(42)], [11, 12, 6, 5, 4]);
for (const d of delta) {
  assert.equal(d.aba, 'FICHA');
  assert.equal(p.explicar(d.r + ':' + d.c, d.antes), d.depois, 'Fora do molde em ' + d.r + ',' + d.c);
  assert.ok(d.depois.endsWith(',' + d.antes.slice(1) + ')') || d.depois.endsWith(',' + d.antes.slice(1) + '))'), 'A conta antiga segue inteira');
  const [extra] = p.CONTAS[d.r + ':' + d.c].map(c => c + d.r);
  assert.ok(d.depois.startsWith(`=IF(AND(DADOS_CONFIG!$C$`) && d.depois.includes(`,ISERROR(${extra}+0)),"Extra só aceita número",`));
  // o aviso das caixas de marcar só existe onde há especialização (o TR não tem)
  assert.equal(d.depois.includes('"Apague o texto em Trein/Espec"'), d.c !== 42);
}
// A ordem: texto no Extra, texto em Trein/Espec, especialização sem treino, atributo, e a conta.
const o108 = delta.find(d => d.r === 108 && d.c === 14).depois;
const ordem = ['Extra só aceita número', 'Apague o texto em Trein/Espec', 'Marque o treino', 'Escolha o atributo', 'NA()'].map(t => o108.indexOf(t));
assert.ok(ordem.every((x, i) => x > 0 && (i === 0 || x > ordem[i - 1])), 'Ordem dos avisos: ' + ordem);
assert.ok(delta.find(d => d.r === 108 && d.c === 42).depois.includes('"Extra só aceita número",IF(AND(DADOS_CONFIG!$C$48<>1,NOT(OR(AK108="FORÇA"'));
assert.ok(delta.find(d => d.r === 109 && d.c === 42).depois.includes('ISERROR(AJ109+0)),"Extra só aceita número",IF(DADOS_CONFIG!$E$49<>"",NA(),'));

// O modelo gerado bate com o depois; a camada se descasca de volta ao antes, atomicamente.
const abas = ler('apps-script');
const ficha = () => expandir(abas.find(a => a.nome === 'FICHA'));
for (const d of delta) assert.equal(ficha().get(d.r + ':' + d.c), d.depois, 'Modelo e plano divergem');
const errado = structuredClone(abas);
const ultima = delta[delta.length - 1];
errado.find(a => a.nome === 'FICHA').vals.find(v => v[0] === ultima.r && v[1] === ultima.c)[2] = '=99';
const copia = JSON.stringify(errado);
assert.throws(() => p.reverterModelo(errado), /Texto no Extra divergente/);
assert.equal(JSON.stringify(errado), copia, 'Reversão parcial');
p.reverterModelo(abas);
for (const d of delta) assert.equal(ficha().get(d.r + ':' + d.c), d.antes);
assert.throws(() => p.reverterModelo(abas), /Texto no Extra divergente/);

// O gerador Python desfaz os avisos exatos (comparadores da configuração) e recusa um adulterado.
const py = `
import json, sys
sys.path.insert(0, 'ficha-v01')
import configuracao as c
delta = json.load(open('r53/diagnostico-android/texto_extra_delta.json'))
assert len(delta) == 38
for d in delta:
    assert c.anterior(d['depois']) == c.anterior(d['antes']), (d['r'], d['c'])
p80 = [d for d in delta if d['r'] == 80 and d['c'] == 16][0]['depois']
o108 = [d for d in delta if d['r'] == 108 and d['c'] == 14][0]['depois']
t109 = [d for d in delta if d['r'] == 109 and d['c'] == 42][0]['depois']
for ruim in (p80.replace('ISERROR(R80+0)', 'ISERROR(R81+0)', 1), p80.replace('$C$14<>1,ISERROR', '$C$15<>1,ISERROR', 1),
             p80.replace('IF(D80,0,0)', 'IF(D81,0,0)', 1), p80.replace('IF(E80,0,0)', 'IF(D80,0,0)', 1),
             o108.replace('ISERROR(O108+0)', 'ISERROR(K108+0)', 1), t109.replace('ISERROR(AJ109+0)', 'ISERROR(AJ110+0)', 1)):
    assert ruim not in (p80, o108, t109)
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
  assert.equal(aplicar.length, 38);
  for (const [i, d] of delta.entries()) {
    assert.deepEqual(aplicar[i].updateCells.start, { sheetId: 1, rowIndex: d.r - 1, columnIndex: d.c - 1 });
    assert.equal(aplicar[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.depois, locale));
    assert.equal(reverter[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, formulaLocal(d.antes, locale));
  }
  const divergente = snap('antes');
  divergente.cells[5].value = '=99';
  assert.throws(() => p.pedidos(delta, divergente), /Célula divergente/);
}

// A regra, com a mesma conversão do Sheets: vazio e número passam; "2" colado como texto soma; outro texto avisa.
const somaQuebra = v => v !== '' && typeof v === 'string' && !/^\s*-?\d+([.,]\d+)?\s*$/.test(v);
const ifQuebra = v => typeof v === 'string' && v !== '' && !/^(TRUE|FALSE)$/i.test(v);
const aviso = (extra, treino, espec, fixo) => fixo ? 'fixo' : somaQuebra(extra) ? 'Extra' : (ifQuebra(treino) || ifQuebra(espec)) ? 'Caixa' : 'conta';
const casos = [['', false, false, false, 'conta'], [2, true, false, false, 'conta'], ['2', false, false, false, 'conta'],
  ['dois', false, false, false, 'Extra'], ['', 'x', false, false, 'Caixa'], ['', false, 'x', false, 'Caixa'],
  ['dois', 'x', false, false, 'Extra'], ['dois', 'x', 'x', true, 'fixo']];
for (const [extra, treino, espec, fixo, esperado] of casos) assert.equal(aviso(extra, treino, espec, fixo), esperado, JSON.stringify([extra, treino, espec, fixo]));

console.log('Texto no Extra: 38 avisos de Extra, 34 de Trein/Espec, ordem, geração, reversão atômica, anterior do Python e pedidos em pt_BR e en_US.');
