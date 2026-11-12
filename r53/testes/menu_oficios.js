'use strict';
// Ofícios e TR Físico (11/11/2026): as doze contas dizem "Escolha o atributo" com o menu vazio ou fora das opções, e os
// menus dos ofícios nascem no atributo padrão do livro. Ver r53/diagnostico-android/CORRECAO-OFICIOS-TR-2026-11-11.md.
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { ler, expandir } = require('./expansao_domada_modelo');
const p = require('../diagnostico-android/preparar_menu_oficios');
const { formulaLocal } = require('../diagnostico-android/preparar_pilha_5156');
const delta = require('../diagnostico-android/menu_oficios_delta.json');
const livro = require('node:fs').readFileSync('manual.txt', 'utf8');

// O plano: doze contas (onze ofícios e o TR Físico) e oito menus, todos na FICHA, cada um explicado pelo molde.
assert.equal(delta.length, 20);
assert.equal(delta.filter(d => p.CONTAS[d.r + ':' + d.c]).length, 12);
assert.equal(delta.filter(d => p.VALORES[d.r + ':' + d.c]).length, 8);
for (const d of delta) {
  assert.equal(d.aba, 'FICHA');
  assert.equal(p.explicar(d.r + ':' + d.c, d.antes), d.depois, 'Fora do molde em ' + d.r + ',' + d.c);
}
const fisico = delta.find(d => d.r === 108 && d.c === 42);
assert.ok(fisico.depois.startsWith('=IF(AND(DADOS_CONFIG!$C$48<>1,NOT(OR(AK108="FORÇA",AK108="DESTREZA"))),"Escolha o atributo",'));
for (const d of delta.filter(d => p.CONTAS[d.r + ':' + d.c])) assert.ok(d.depois.endsWith(',' + d.antes.slice(1) + ')'), 'A conta antiga segue inteira');

// O padrão vem da tabela de Ofícios do manual.txt (o mesmo texto do R66).
const tabela = livro.slice(livro.indexOf('Ofício | Atributo padrão | Aplicações'));
const padrao = Object.fromEntries(tabela.split('\n').slice(1, 12).map(l => l.split(' | ')).map(([o, a]) => [o, a.toUpperCase()]));
assert.equal(Object.keys(padrao).length, 11);
const abas = require('../diagnostico-android/preparar_especializacao').reverterModelo(require('../diagnostico-android/preparar_texto_extra').reverterModelo(ler('apps-script'))); // a camada da especialização vem depois
const ficha = () => expandir(abas.find(a => a.nome === 'FICHA'));
const f = ficha();
for (const [nome, atr] of Object.entries(padrao)) {
  const pos = [...f.entries()].find(([, v]) => typeof v === 'string' && v.trim() === nome)[0];
  const [r, c] = pos.split(':').map(Number);
  const menu = c === 6 ? r + ':11' : r + ':24';
  assert.equal(f.get(menu), atr, nome + ' nasce em ' + atr);
}

// O modelo gerado bate com o depois; a camada se descasca de volta ao antes, atomicamente.
for (const d of delta) assert.equal(f.get(d.r + ':' + d.c), d.depois, 'Modelo e plano divergem');
const errado = structuredClone(abas);
const ultima = delta[delta.length - 1];
errado.find(a => a.nome === 'FICHA').vals.find(v => v[0] === ultima.r && v[1] === ultima.c)[2] = '=99';
const copia = JSON.stringify(errado);
assert.throws(() => p.reverterModelo(errado), /Menu dos ofícios divergente/);
assert.equal(JSON.stringify(errado), copia, 'Reversão parcial');
p.reverterModelo(abas);
for (const d of delta) assert.equal(ficha().get(d.r + ':' + d.c), d.antes);
assert.throws(() => p.reverterModelo(abas), /Menu dos ofícios divergente/);

// O gerador Python desfaz o aviso exato (comparadores da configuração), com dois ou cinco nomes, e recusa um adulterado.
const py = `
import json, sys
sys.path.insert(0, 'ficha-v01')
import configuracao as c
delta = [d for d in json.load(open('r53/diagnostico-android/menu_oficios_delta.json')) if d['antes'].startswith('=')]
for d in delta:
    assert c.anterior(d['depois']) == c.anterior(d['antes']), (d['r'], d['c'])
for ruim in (delta[0]['depois'].replace('"ESSÊNCIA"))', '"FORÇA"))', 1),
             [d for d in delta if d['c'] == 42][0]['depois'].replace('AK108="DESTREZA"))', 'AK108="ESSÊNCIA"))', 1)):
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

// Instalação: aplicar e reverter nas duas localidades, recusando célula divergente e menu já trocado pelo jogador.
for (const locale of ['pt_BR', 'en_US']) {
  const snap = fase => ({ locale, sheetIds: { FICHA: 1 }, cells: delta.map(d => ({ aba: d.aba, r: d.r, c: d.c, value: formulaLocal(d[fase], locale) })) });
  const aplicar = p.pedidos(delta, snap('antes'));
  const reverter = p.pedidos(delta, snap('depois'), true);
  assert.equal(aplicar.length, 20);
  for (const [i, d] of delta.entries()) {
    assert.deepEqual(aplicar[i].updateCells.start, { sheetId: 1, rowIndex: d.r - 1, columnIndex: d.c - 1 });
    assert.equal(aplicar[i].updateCells.fields, 'userEnteredValue');
    const ent = aplicar[i].updateCells.rows[0].values[0].userEnteredValue;
    assert.equal(ent.formulaValue ?? ent.stringValue, formulaLocal(d.depois, locale));
  }
  const divergente = snap('antes');
  divergente.cells[0].value = '=99';
  assert.throws(() => p.pedidos(delta, divergente), /Célula divergente/);
  const trocado = snap('antes');
  const i = delta.findIndex(d => p.VALORES[d.r + ':' + d.c]);
  trocado.cells[i].value = 'FORÇA';
  assert.throws(() => p.pedidos(delta, trocado), /Célula divergente/);
}

// A regra: o Sheets compara texto sem caixa, então só nome fora das opções (ou vazio) avisa; valor fixo nunca avisa.
const avisa = (menu, fixo, nomes) => !fixo && !nomes.some(a => a.toLowerCase() === String(menu).toLowerCase());
const casos = [['DESTREZA', false, p.ATRIBUTOS, false], ['', false, p.ATRIBUTOS, true], ['FORCA', false, p.ATRIBUTOS, true],
  ['ESSÊNCIA', false, ['FORÇA', 'DESTREZA'], true], ['destreza', false, ['FORÇA', 'DESTREZA'], false], ['', true, p.ATRIBUTOS, false]];
for (const [menu, fixo, nomes, esperado] of casos) assert.equal(avisa(menu, fixo, nomes), esperado, JSON.stringify([menu, fixo]));

console.log('Ofícios e TR Físico: doze avisos, oito padrões do livro, geração, reversão atômica, anterior do Python e pedidos em pt_BR e en_US.');
