'use strict';
// O Sheets de mentira das missões da FICHA PESSOAL: abas com células e notas num Map, cada ida ao servidor anotada em
// idas e cada gravação em escritas. Usado pelo missoes_enxutas.js (26/10) e pelo missoes_sem_registros.js (27/10).
const vm = require('vm');
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
  // BC11 como a ficha calcula: o XP do próximo nível (curva da DADOS) menos o total; — no nível máximo.
  pos('FICHA PESSOAL', 'BC11', op.falta !== undefined ? op.falta : (+op.nivel || 0) >= 30 ? '—' : Math.max(0, (+op.nivel || 0) * 100 - (+op.xp || 0)));
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
module.exports = { ambiente, col };
