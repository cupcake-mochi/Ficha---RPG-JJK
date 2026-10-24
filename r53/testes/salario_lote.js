'use strict';
// VM com serviços simulados: o fechamento em lote lê DADOS_SALARIOS uma vez, credita os períodos vencidos pela regra
// do salarioApurar_, não repete período pago e não lê nada quando ainda não venceu. Não fala com o Sheets.
const vm = require('vm'), assert = require('assert'), fs = require('fs'), path = require('path');
const {preparar, NOVO, ANCORA} = require('../diagnostico-android/preparar_salario_lote.js');
const p = preparar({files: [{name: 'Codigo', type: 'SERVER_JS', source: ANCORA + 'return 1;}'}]});
assert(p.files[0].source.startsWith(NOVO));
const ctx = {console: {log: m => process.env.DEPURAR && console.error(m)}};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname, '../../apps-script/Salarios.gs'), 'utf8'), ctx);
vm.runInContext(p.files.find(f => f.name === 'SalarioLote').source, ctx);
const dia = s => vm.runInContext('salarioDiaISO_("' + s + '")', ctx);
const HOJE = dia('2026-12-25'), EMISSAO = dia('2026-10-20');
ctx.Utilities = {formatDate: d => Math.abs(d - Date.now()) < 864e5 ? '2026-12-25' : d.toISOString().slice(0, 10)};
const VDate = vm.runInContext('Date', ctx), data = d => new VDate((d - 25569) * 86400000 + 12 * 3600000);
let leituras = 0, livro = [], props = {}, grav = {};
function grade() {
  const g = Array.from({length: 1000}, () => Array(14).fill(''));
  g[1][0] = 'm1'; g[1][2] = 'Curta'; g[1][3] = EMISSAO + 3; g[1][4] = true;      // 1º ciclo: 1 participação
  g[2][0] = 'm2'; g[2][2] = 'Longa'; g[2][3] = EMISSAO + 35; g[2][4] = true;     // 2º ciclo: 2
  g[3][0] = 'm3'; g[3][2] = 'Longa'; g[3][3] = EMISSAO + 40; g[3][4] = false;    // removida: não conta
  g[1][11] = JSON.stringify({versao: 1, inicio: EMISSAO, graus: [[EMISSAO, 'Grau 4']]});
  const N = [data(EMISSAO), true, 30, 3, 0.25, true, data(EMISSAO + 30), 150000, 300000, 600000, 1200000, 2400000,
    1, 1, 2, 3, 1, 1, 'Grau 4', 'Kaori', livro.length, 1000, livro.length ? livro[livro.length - 1][2] : '',
    livro.map(l => l[0]).join('|')];
  N.forEach((x, i) => { g[i + 1][13] = x; });
  return g;
}
const faixa = (k) => ({setValue: v => { grav[k] = v; }, setValues: v => { grav[k] = v; if (k.startsWith('livro')) livro = livro.concat(v); }});
const abas = {
  DADOS_SALARIOS: {getRange: (a, b) => typeof a === 'number' ? {getValues: () => (leituras++, grade())} : faixa('dados ' + a)},
  'SALÁRIOS': {getRange: (l) => faixa('livro ' + l), insertRowsAfter() {}},
  'CONFIGURAÇÃO': {getRange: a => faixa('cfg ' + a)}
};
const ss = {getSheetByName: n => abas[n]};
ctx.SpreadsheetApp = {getActive: () => ss, flush() {}};
ctx.LockService = {getDocumentLock: () => ({tryLock: () => true, releaseLock() {}})};
ctx.ScriptApp = {getScriptId: () => 'copia'};
ctx.PropertiesService = {getScriptProperties: () => ({getProperty: () => 'original'}),
  getDocumentProperties: () => ({getProperty: k => props[k] || null, setProperty: (k, v) => { props[k] = v; }, deleteProperty: k => { delete props[k]; }})};
const edicao = (aba, a1) => ({source: ss, range: {getSheet: () => ({getName: () => aba}), getA1Notation: () => a1,
  getRow: () => 5, getLastRow: () => 5, getColumn: () => 5, getLastColumn: () => 5}});
vm.runInContext('var r', ctx);
ctx.e = edicao('FICHA', 'E5');
vm.runInContext('r53SalarioLote_(e)', ctx);
assert.strictEqual(leituras, 1);
// Emissão 20/10, 30 dias: fecham 19/11 e 19/12. 1 participação = 50%, 2 = 75%.
assert.deepStrictEqual(livro.map(l => [l[0], l[6], l[9]]),
  [['SAL1:' + EMISSAO + ':' + (EMISSAO + 30), 1, 75000], ['SAL1:' + (EMISSAO + 30) + ':' + (EMISSAO + 60), 2, 112500]]);
assert.strictEqual(Number(props.salario_proximo), EMISSAO + 90);
assert.strictEqual(JSON.parse(grav['dados L2']).inicio, EMISSAO + 60);
// Segunda edição no mesmo dia: não lê nada e não credita de novo.
vm.runInContext('r53SalarioLote_(e)', ctx);
assert.strictEqual(leituras, 1); assert.strictEqual(livro.length, 2);
// Sem data guardada (cópia nova) e livro já em dia: lê uma vez, não grava nada.
delete props.salario_proximo; grav = {};
vm.runInContext('r53SalarioLote_(e)', ctx);
assert.strictEqual(leituras, 2); assert.strictEqual(livro.length, 2); assert.deepStrictEqual(Object.keys(grav), []);
// Troca de paleta e edição em área do salário não fecham; a área própria apaga a data guardada.
ctx.e = edicao('CARTEIRA', 'C27'); vm.runInContext('r53SalarioLote_(e)', ctx); assert.strictEqual(leituras, 2);
props.salario_proximo = '1';
ctx.e = edicao('CONFIGURAÇÃO', 'O41');
ctx.e.range.getRow = () => 41; ctx.e.range.getLastRow = () => 41; ctx.e.range.getColumn = () => 15; ctx.e.range.getLastColumn = () => 15;
vm.runInContext('r53SalarioLote_(e)', ctx);
assert.strictEqual(leituras, 2); assert(!props.salario_proximo);
console.log(JSON.stringify({resultado: 'OK', creditos: livro.map(l => l[9]), limite: 'VM com serviços simulados; não mede o Sheets.'}));
