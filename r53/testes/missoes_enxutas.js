'use strict';
// Missões enxutas (26/10/2026): a mesma edição no painel de missões da FICHA PESSOAL, pelo código de antes e pelo de
// depois do preparar_missoes_enxutas.js, num Sheets de mentira que conta as idas. Confere que as duas deixam as mesmas
// células, notas e nível, e que a de depois vai menos vezes ao servidor. Sem os espelhos da DADOS, cai na leitura antiga.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
const {preparar: comExtrato} = require('../diagnostico-android/preparar_salario_extrato.js');
const {preparar: comMissoes} = require('../diagnostico-android/preparar_missoes.js');
const {preparar: enxutas} = require('../diagnostico-android/preparar_missoes_enxutas.js');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };

const base = comExtrato({files: [{name: 'Codigo', source: fs.readFileSync(path.join(__dirname, 'salarios-com-formula.gs'), 'utf8')}]}).files[0].source;
const antes = comMissoes(base), depois = enxutas(antes);
eq(depois, fs.readFileSync(path.join(raiz, 'apps-script/Salarios.gs'), 'utf8'), 'o Salarios.gs é o resultado do preparador');
assert.throws(() => enxutas(depois), /já presentes/); checks++;
assert.throws(() => enxutas(antes.replace("getRange('AQ4:DP100')", "getRange('AQ4:DP99')")), /divergente/); checks++;

const col = s => Array.from(s).reduce((n, c) => n * 26 + c.charCodeAt(0) - 64, 0);
function ambiente(source, op) {
  const idas = [], escritas = [];
  class Range {
    constructor(s, r, c, h = 1, w = 1) { Object.assign(this, {s, r, c, h, w}); }
    ler(m) { return Array.from({length: this.h}, (_, i) => Array.from({length: this.w}, (_, j) => m.get((this.r + i) + ',' + (this.c + j)) ?? '')); }
    getValues() { idas.push(this.s.name + ' valores ' + this.a1()); return this.ler(this.s.cells); }
    getValue() { idas.push(this.s.name + ' valor ' + this.a1()); return this.ler(this.s.cells)[0][0]; }
    getNotes() { idas.push(this.s.name + ' notas ' + this.a1()); return this.ler(this.s.notes); }
    a1() { return this.r + ',' + this.c + ' ' + this.h + '×' + this.w; }
    gravar(m, a, k) { escritas.push([this.s.name, k, this.a1(), JSON.stringify(a)]); a.forEach((l, i) => l.forEach((v, j) => m.set((this.r + i) + ',' + (this.c + j), typeof v === 'string' && v.startsWith("'") ? v.slice(1) : v))); return this; }
    setValues(a) { return this.gravar(this.s.cells, a, 'valores'); }
    setValue(v) { return this.gravar(this.s.cells, [[v]], 'valor'); }
    setFormula(v) { return this.gravar(this.s.cells, [[v]], 'fórmula'); }
    setNotes(a) { return this.gravar(this.s.notes, a, 'notas'); }
    getSheet() { return this.s; } getRow() { return this.r; } getLastRow() { return this.r + this.h - 1; }
    getColumn() { return this.c; } getLastColumn() { return this.c + this.w - 1; }
  }
  class Sheet {
    constructor(name) { this.name = name; this.cells = new Map(); this.notes = new Map(); this.max = 1000; }
    getName() { return this.name; }
    getLastRow() { idas.push(this.name + ' última linha'); return Math.max(1, ...Array.from(this.cells.keys(), k => +k.split(',')[0])); }
    getMaxRows() { idas.push(this.name + ' linhas'); return this.max; }
    insertRowsAfter(_, n) { this.max += n; }
    getRange(r, c, h, w) {
      if (typeof r !== 'string') return new Range(this, r, c, h, w);
      const m = /^([A-Z]+)(\d+)(?::([A-Z]+)(\d*))?$/.exec(r);
      return new Range(this, +m[2], col(m[1]), m[4] ? +m[4] - m[2] + 1 : m[3] ? this.max - m[2] + 1 : 1, m[3] ? col(m[3]) - col(m[1]) + 1 : 1);
    }
  }
  const abas = Object.fromEntries(['CONFIGURAÇÃO', 'FICHA PESSOAL', 'FICHA', 'CARTEIRA', 'DADOS_SALARIOS', 'SALÁRIOS', 'DADOS'].map(n => [n, new Sheet(n)]));
  const pos = (aba, a1, v) => { const m = /^([A-Z]+)(\d+)$/.exec(a1); abas[aba].cells.set(m[2] + ',' + col(m[1]), v); };
  // A DADOS como o gerador a deixa: curva em AQ:AR, limiar em CW, índices em BA:BB e DO:DP, espelhos em CY:CZ.
  pos('DADOS', 'AQ4', 'nível'); pos('DADOS', 'AR4', 'xp acumulado'); pos('DADOS', 'CW4', 'limiar do feito'); pos('DADOS', 'CW5', op.limiar);
  for (let i = 1; i <= 30; i++) { pos('DADOS', 'AQ' + (i + 4), i); pos('DADOS', 'AR' + (i + 4), (i - 1) * 100); }
  pos('DADOS', 'BA9', 'nivel'); pos('DADOS', 'BB9', 'AH11'); pos('DADOS', 'DO10', 'xp total'); pos('DADOS', 'DP10', 'AW11');
  if (op.espelhos) { pos('DADOS', 'CY47', 'xp total'); pos('DADOS', 'CZ47', op.xp); pos('DADOS', 'CY48', 'nível'); pos('DADOS', 'CZ48', op.nivel); }
  pos('FICHA PESSOAL', 'AW11', op.xp); pos('FICHA', 'AH11', op.nivel);
  pos('DADOS_SALARIOS', 'L2', JSON.stringify({inicio: 46000}));
  for (const [a1, v] of op.painel) pos('FICHA PESSOAL', a1, v);
  for (const l of op.registros || []) l.forEach((v, j) => abas.DADOS_SALARIOS.cells.set((op.registros.indexOf(l) + 2) + ',' + (j + 1), v));
  const ss = {getSheetByName: n => abas[n] || null};
  let uuid = 0;
  const ctx = {console: {log() {}}, Date, JSON, Math,
    PropertiesService: {getScriptProperties: () => ({getProperty: () => null})}, ScriptApp: {getScriptId: () => 'qa'},
    SpreadsheetApp: {getActive: () => ss, flush() { idas.push('flush'); }},
    LockService: {getDocumentLock: () => ({tryLock: () => true, releaseLock() {}})},
    Utilities: {getUuid: () => 'id' + (++uuid), formatDate: d => new Date(d).toISOString().slice(0, 10)}};
  vm.createContext(ctx); vm.runInContext(source, ctx);
  ctx.salarioHoje_ = () => 46010; ctx.SALARIO_.formula = true; ctx.r53Formula_ = f => f;
  const evento = (a1, v) => { const m = /^([A-Z]+)(\d+)$/.exec(a1); pos('FICHA PESSOAL', a1, v); return {source: ss, value: v, range: abas['FICHA PESSOAL'].getRange(+m[2], col(m[1]))}; };
  return {ctx, abas, idas, escritas, evento,
    retrato: () => Object.fromEntries(Object.entries(abas).map(([n, s]) => [n, {c: [...s.cells].sort(), n: [...s.notes].sort()}]))};
}

let idasAntes = 0, idasDepois = 0, casos = 0;
const cenarios = [];
for (const espelhos of [true, false]) for (const [xp, nivel, limiar] of [[0, 1, 0], [450, 2, 0], [450, 6, 0], [2500, 3, 10], [99999, 21, 20], ['', 4, 0]])
  for (const [onde, valor, painel, registros] of [
    ['AW15', 'Missão A', [['AX15', 'Curta']], []],
    ['AX16', 'Longa', [['AW16', 'Missão B']], []],
    ['BC20', '', [['BD20', 'Padrão']], [['idX', 'Missão velha', 'Padrão', 46001, true, '55:20', 46001]]],
    ['AW15', 'Missão A corrigida', [['AX15', 'Curta']], [['idA', 'Missão A', 'Curta', 46002, true, '49:15', 46002]]],
  ]) cenarios.push({espelhos, xp, nivel, limiar, onde, valor, painel, registros});
for (const op of cenarios) {
  const rodar = source => {
    const a = ambiente(source, op), e = a.evento(op.onde, op.valor);
    if (op.registros.length && op.registros[0][0] === 'idA') a.abas['FICHA PESSOAL'].notes.set('15,49', 'x\n[Salário: idA · 01/01/2026]');
    a.idas.length = 0;
    let original = 0;
    eq(a.ctx.salarioIntegrarMissao_(e, () => { original++; }), true);
    return {a, original};
  };
  const v = rodar(antes), n = rodar(depois), onde = JSON.stringify(op);
  eq(n.a.retrato(), v.a.retrato(), onde + ' células e notas');
  eq(n.original, v.original, onde + ' onEdit de sempre');
  eq(n.a.escritas.map(x => x.join(' ')), v.a.escritas.map(x => x.join(' ')), onde + ' gravações');
  assert(n.a.idas.length < v.a.idas.length, onde + ' idas ' + v.a.idas.length + ' → ' + n.a.idas.length); checks++;
  eq(n.a.idas.some(x => /L2|12 1×1/.test(x) && /DADOS_SALARIOS valor/.test(x)), false, onde + ' sem ler o estado');
  eq(n.a.idas.filter(x => /última linha|linhas$/.test(x)), [], onde + ' sem getLastRow/getMaxRows');
  if (op.espelhos) eq(n.a.idas.filter(x => /^(FICHA|FICHA PESSOAL) valor /.test(x)), [], onde + ' XP e nível pelos espelhos');
  idasAntes += v.a.idas.filter(x => x !== 'flush').length; idasDepois += n.a.idas.filter(x => x !== 'flush').length; casos++;
}
// O caso comum, contado à parte: nome de missão novo, com os espelhos.
const um = s => { const a = ambiente(s, cenarios[0]), e = a.evento('AW15', 'Missão A'); a.idas.length = 0; a.ctx.salarioIntegrarMissao_(e, () => {}); return a.idas.filter(x => x !== 'flush'); };
const [l1, l2] = [um(antes), um(depois)];
console.log(JSON.stringify({checks, casos, resultado: 'OK', leituras_caso_comum: l1.length + ' → ' + l2.length, leituras_somadas: idasAntes + ' → ' + idasDepois,
  depois: l2, escopo: 'mesmas células, notas, nível e onEdit; sem L2, getLastRow e getMaxRows; XP e nível pelos espelhos da DADOS'}));
