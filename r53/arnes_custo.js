'use strict';
// Arnês de custo: roda o onEdit instalado (todos os arquivos do projeto) contra a ficha exportada em xlsx e registra
// cada ida ao servidor. Modelo de custo calibrado nas medições de 25-26/10 (MEDICAO-DESEMPENHO).
const fs = require('fs'), vm = require('vm'), zlib = require('zlib'), crypto = require('crypto');

const letras = c => { let s = ''; for (; c; c = Math.floor((c - 1) / 26)) s = String.fromCharCode(65 + (c - 1) % 26) + s; return s; };
const num = t => [...t].reduce((n, x) => n * 26 + x.charCodeAt(0) - 64, 0);
function a1(s) {
  s = String(s).replace(/\$/g, '');
  let m = /^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(s);
  if (m) return [+m[2], num(m[1]), +(m[4] || m[2]), num(m[3] || m[1])];
  m = /^([A-Z]+):([A-Z]+)$/.exec(s); if (m) return [1, num(m[1]), 5000, num(m[2])];
  m = /^(\d+):(\d+)$/.exec(s); if (m) return [+m[1], 1, +m[2], 200];
  m = /^([A-Z]+)(\d+):([A-Z]+)$/.exec(s); if (m) return [+m[2], num(m[1]), 5000, num(m[3])];
  throw new Error('a1 ' + s);
}
function valor(x) { if (x && typeof x === 'object' && x.d) return new Date(x.d); return x === undefined || x === null ? '' : x; }

function criar(dump, opts = {}) {
  const log = []; let pend = 0, lidas = 0; let journal = [];
  const op = (t, o) => {
    const e = Object.assign({ t }, o);
    if (t === 'R') { e.barreira = lidas === 0 || pend > 0; lidas++; pend = 0; }
    if (t === 'W') pend++;
    if (t === 'F') { e.barreira = pend > 0; pend = 0; }
    log.push(e);
  };
  const sheets = new Map();
  class Range {
    constructor(sh, r, c, nr, nc) { Object.assign(this, { sh, r, c, nr, nc }); }
    getSheet() { return this.sh; } getRow() { return this.r; } getColumn() { return this.c; }
    getLastRow() { return this.r + this.nr - 1; } getLastColumn() { return this.c + this.nc - 1; }
    getNumRows() { return this.nr; } getNumColumns() { return this.nc; }
    getA1Notation() { return letras(this.c) + this.r + (this.nr > 1 || this.nc > 1 ? ':' + letras(this.getLastColumn()) + this.getLastRow() : ''); }
    getCell(i, j) { return new Range(this.sh, this.r + i - 1, this.c + j - 1, 1, 1); }
    offset(i, j, nr, nc) { return new Range(this.sh, this.r + i, this.c + j, nr || this.nr, nc || this.nc); }
    _g(k, f) { return Array.from({ length: this.nr }, (_, i) => Array.from({ length: this.nc }, (_, j) => f(this.sh.cel(this.r + i, this.c + j)))); }
    _r(k) { op('R', { k, a: this.sh.n + '!' + this.getA1Notation(), n: this.nr * this.nc, inteira: !!this.inteira }); }
    _w(k) { op('W', { k, a: this.sh.n + '!' + this.getA1Notation(), n: this.nr * this.nc }); }
    getValues() { this._r('valores'); return this._g('v', c => valor(c.v)); }
    getValue() { return this.getValues()[0][0]; }
    getDisplayValues() { this._r('exibidos'); return this._g('v', c => String(valor(c.v))); }
    getDisplayValue() { return this.getDisplayValues()[0][0]; }
    getFormulas() { this._r('fórmulas'); return this._g('f', c => c.f || ''); }
    getFormula() { return this.getFormulas()[0][0]; }
    getFormulasR1C1() { this._r('fórmulasR1C1'); return this._g('f', c => c.f || ''); }
    getFormulaR1C1() { return this.getFormulasR1C1()[0][0]; }
    getNotes() { this._r('notas'); return this._g('n', c => c.n || ''); }
    getNote() { return this.getNotes()[0][0]; }
    getBackgrounds() { this._r('fundos'); return this._g('b', c => '#ffffff'); }
    getBackground() { return this.getBackgrounds()[0][0]; }
    getFontColors() { this._r('fontes'); return this._g('b', c => '#000000'); }
    getRichTextValue() { this._r('rico'); const t = String(valor(this.sh.cel(this.r, this.c).v)); return { getText: () => t, getRuns: () => [] }; }
    getDataValidation() { this._r('validação'); return null; }
    getDataValidations() { this._r('validações'); return this._g('dv', () => null); }
    getMergedRanges() { this._r('mesclas'); return []; }
    isPartOfMerge() { this._r('mescla'); return false; }
    isBlank() { this._r('vazio'); return this._g('v', c => c.v === '' || c.v === undefined || c.v === null).every(l => l.every(Boolean)); }
    isChecked() { return this.getValue() === true; }
    _set(f) { for (let i = 0; i < this.nr; i++) for (let j = 0; j < this.nc; j++) f(this.sh.cel(this.r + i, this.c + j, true), i, j); }
    setValues(m) { this._w('valores'); this._set((c, i, j) => { c.v = m[i][j]; delete c.f; }); return this; }
    setValue(v) { this._w('valor'); this._set(c => { c.v = v; delete c.f; }); return this; }
    setFormula(f) { this._w('fórmula'); this._set(c => { c.f = f; }); return this; }
    setFormulas(m) { this._w('fórmulas'); this._set((c, i, j) => { c.f = m[i][j]; }); return this; }
    setFormulaR1C1(f) { this._w('fórmulaR1C1'); return this; }
    setNote(t) { this._w('nota'); this._set(c => { c.n = t; }); return this; }
    setNotes(m) { this._w('notas'); this._set((c, i, j) => { c.n = m[i][j]; }); return this; }
    clearNote() { return this.setNote(''); }
    setRichTextValue(r) { this._w('rico'); this._set(c => { c.v = r._t; delete c.f; }); return this; }
    clearContent() { this._w('limpar'); this._set(c => { c.v = ''; delete c.f; }); return this; }
    check() { return this.setValue(true); } uncheck() { return this.setValue(false); }
    activate() { return this; }
  }
  // Toda escrita de formato/validação conta como gravação; leitura desconhecida estoura.
  const W = ['setBackground', 'setBackgrounds', 'setFontColor', 'setFontColors', 'setFontWeight', 'setFontWeights', 'setNumberFormat', 'setNumberFormats',
    'setDataValidation', 'setDataValidations', 'clearDataValidations', 'setBorder', 'setWrap', 'setHorizontalAlignment', 'setVerticalAlignment',
    'setFontSize', 'setFontFamily', 'setFontStyle', 'setFontLine', 'insertCheckboxes', 'removeCheckboxes', 'merge', 'breakApart', 'setWrapStrategy',
    'clearFormat', 'setTextRotation', 'setShowHyperlink', 'setFontSizes', 'setFontFamilies', 'setFontStyles', 'setWraps', 'setHorizontalAlignments', 'setVerticalAlignments'];
  // os argumentos ficam no registro (x), para comparar duas versões do código pelo que gravam
  W.forEach(k => { Range.prototype[k] = function () { this._w(k); log[log.length - 1].x = JSON.stringify([...arguments]); return this; }; });
  class Sheet {
    constructor(n, d) { this.n = n; this.d = d; this.cells = new Map(Object.entries(d.cells)); this.rows = d.rows; this.cols = d.cols; }
    cel(r, c, criar) { const k = r + ',' + c; let x = this.cells.get(k);
      if (criar && journal) journal.push([this, k, x ? Object.assign({}, x) : undefined]);
      if (!x) { x = { v: '' }; if (criar) this.cells.set(k, x); } else if (criar) { /* mesma referência, cópia guardada */ } return x; }
    getName() { return this.n; } getSheetName() { return this.n; } getSheetId() { return this.n.length * 1000; }
    getRange(a, c, nr, nc) {
      if (typeof a === 'string') { const [r1, c1, r2, c2] = a1(a); return new Range(this, r1, c1, r2 - r1 + 1, c2 - c1 + 1); }
      return new Range(this, a, c, nr || 1, nc || 1);
    }
    getRangeList(l) { const rs = l.map(x => this.getRange(x)); const o = { getRanges: () => rs };
      ['setValue', 'setFormula', 'setNote', 'check', 'uncheck', 'clearContent', ...W].forEach(k => { o[k] = (...a) => { op('W', { k: 'lista.' + k, a: this.n + '!' + l.join(','), n: l.length }); rs.forEach(r => { const pend0 = pend; (Range.prototype[k]).apply(r, a); }); pend -= 0; return o; }; });
      return o; }
    getDataRange() { const r = new Range(this, 1, 1, this.rows, this.cols); r.inteira = true; return r; }
    getLastRow() { op('R', { k: 'getLastRow', a: this.n, n: 1 }); return this.rows; }
    getLastColumn() { op('R', { k: 'getLastColumn', a: this.n, n: 1 }); return this.cols; }
    getMaxRows() { op('R', { k: 'getMaxRows', a: this.n, n: 1 }); return this.rows; }
    getMaxColumns() { op('R', { k: 'getMaxColumns', a: this.n, n: 1 }); return this.cols; }
    isSheetHidden() { return this.d.hidden; }
    setRowHeights() { op('W', { k: 'alturas', a: this.n, x: JSON.stringify([...arguments]) }); return this; } setRowHeight() { op('W', { k: 'altura', a: this.n, x: JSON.stringify([...arguments]) }); return this; }
    setColumnWidth() { op('W', { k: 'largura', a: this.n }); return this; }
    insertRowsAfter(r, n) { op('W', { k: 'inserir linhas', a: this.n }); this.rows += n; return this; }
    getRowGroup() { op('R', { k: 'grupo', a: this.n, n: 1 }); return null; }
    getParent() { return ss; }
    getImages() { op('R', { k: 'imagens', a: this.n, n: 1 }); return []; }
    getProtections() { op('R', { k: 'proteções', a: this.n, n: 1 }); return []; }
    getConditionalFormatRules() { op('R', { k: 'condicionais', a: this.n, n: 1 }); return []; }
    setConditionalFormatRules() { op('W', { k: 'condicionais', a: this.n }); }
    setTabColor() { op('W', { k: 'cor da aba', a: this.n }); return this; }
    activate() { return this; }
  }
  for (const [n, d] of Object.entries(dump)) sheets.set(n, new Sheet(n, d));
  const nomeados = opts.nomeados || {};
  const ss = {
    getSheetByName: n => sheets.get(n) || null, getSheets: () => [...sheets.values()], getSpreadsheetLocale: () => 'pt_BR', getSpreadsheetTimeZone: () => 'America/Sao_Paulo',
    getId: () => 'ficha', toast: (m) => op('X', { k: 'toast', a: String(m).slice(0, 60) }), getName: () => 'Ficha',
    getRangeByName: n => { op('R', { k: 'nomeado', a: n, n: 1 }); const x = nomeados[n]; if (!x) return null; const [s, r] = x.split('!'); return sheets.get(s).getRange(r); },
    getRange: x => { const m = /^'?([^'!]+)'?!(.+)$/.exec(x); return sheets.get(m[1]).getRange(m[2]); },
    getActiveSheet: () => sheets.get('FICHA'),
  };
  const props = Object.assign({}, opts.props || {}), sprops = Object.assign({}, opts.sprops || {});
  const P = (o, nome) => ({
    getProperty: k => { op('P', { k: nome + '.get', a: k }); return k in o ? o[k] : null; },
    getProperties: () => { op('P', { k: nome + '.getAll' }); return Object.assign({}, o); },
    setProperty: (k, v) => { op('P', { k: nome + '.set', a: k }); o[k] = String(v); },
    setProperties: (m) => { op('P', { k: nome + '.setAll' }); Object.assign(o, m); },
    deleteProperty: k => { op('P', { k: nome + '.del', a: k }); delete o[k]; },
  });
  const blob = (b, t) => ({ _b: Buffer.from(b), getBytes: () => Array.from(Buffer.from(b)), getDataAsString: () => Buffer.from(b).toString('utf8'), setContentType() { return this; } });
  const ctx = {
    console: { log: (...a) => { if (opts.verbose) process.stderr.write(a.join(' ') + '\n'); log.push({ t: 'L', a: a.join(' ').slice(0, 200) }); } },
    SpreadsheetApp: { getActive: () => ss, getActiveSpreadsheet: () => ss, flush: () => op('F', {}),
      newDataValidation: () => { const b = new Proxy({}, { get: (t, k) => k === 'build' ? () => ({}) : () => b }); return b; },
      newRichTextValue: () => { const b = { _t: '', setText(t) { b._t = t; return b; }, setTextStyle() { return b; }, setLinkUrl() { return b; }, build() { return { _t: b._t }; } }; return b; },
      newTextStyle: () => { const b = new Proxy({}, { get: (t, k) => k === 'build' ? () => ({}) : () => b }); return b; },
      getUi: () => { throw new Error('sem UI no gatilho simples'); },
      DataValidationCriteria: {}, BorderStyle: {}, WrapStrategy: {} },
    PropertiesService: { getDocumentProperties: () => P(props, 'doc'), getScriptProperties: () => P(sprops, 'script'), getUserProperties: () => P({}, 'user') },
    LockService: { getDocumentLock: () => ({ tryLock: () => { op('P', { k: 'lock' }); return true; }, waitLock() {}, releaseLock() {}, hasLock: () => true }), getScriptLock: () => ({ tryLock: () => true, releaseLock() {} }) },
    CacheService: { getDocumentCache: () => ({ get: () => null, put() {}, remove() {} }), getScriptCache: () => ({ get: () => null, put() {}, remove() {} }) },
    ScriptApp: { getScriptId: () => 'script', getProjectTriggers: () => [], AuthMode: {} },
    Session: { getActiveUser: () => ({ getEmail: () => '' }), getScriptTimeZone: () => 'America/Sao_Paulo' },
    Utilities: {
      base64Decode: s => Array.from(Buffer.from(s, 'base64')), base64Encode: a => Buffer.from(a).toString('base64'),
      newBlob: (b, t) => blob(typeof b === 'string' ? Buffer.from(b) : Buffer.from(b.map(x => (x + 256) % 256)), t),
      ungzip: b => blob(zlib.gunzipSync(b._b)), gzip: b => blob(zlib.gzipSync(b._b)),
      computeDigest: (alg, s) => Array.from(crypto.createHash('sha256').update(s, 'utf8').digest()).map(x => x > 127 ? x - 256 : x),
      DigestAlgorithm: { SHA_256: 'sha256' }, Charset: { UTF_8: 'utf8' },
      formatDate: (d, tz, f) => { const z = new Date(d.getTime() - 3 * 3600e3); const p = n => String(n).padStart(2, '0');
        return f.replace('yyyy', z.getUTCFullYear()).replace('MM', p(z.getUTCMonth() + 1)).replace('dd', p(z.getUTCDate())).replace('HH', p(z.getUTCHours())).replace('mm', p(z.getUTCMinutes())).replace('ss', p(z.getUTCSeconds())); },
      getUuid: () => crypto.randomUUID(), sleep() {},
    },
    Date, JSON, Math, Object, Array, String, Number, Boolean, RegExp, Error, Proxy, Reflect, isFinite, isNaN, parseInt, parseFloat, Buffer: undefined,
  };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  return { ctx, ss, sheets, log, props, sprops, op, reset() { log.length = 0; pend = 0; lidas = 0; },
    // as células que esta edição mudou de fato (gravar o mesmo que já estava não conta), como estão agora: {aba!r,c: {v, f, n}}
    alteradas() {
      const o = {}, de = x => x ? { v: x.v === undefined ? '' : x.v, f: x.f || '', n: x.n || '' } : { v: '', f: '', n: '' }, vistos = new Set();
      for (const [sh, k, antes] of journal) {
        if (vistos.has(sh.n + '!' + k)) continue; vistos.add(sh.n + '!' + k);
        const a = de(antes), d = de(sh.cells.get(k));
        if (JSON.stringify(a) !== JSON.stringify(d)) o[sh.n + '!' + k] = d;
      }
      return o;
    },
    desfazer() { for (let i = journal.length - 1; i >= 0; i--) { const [sh, k, o] = journal[i]; if (o === undefined) sh.cells.delete(k); else sh.cells.set(k, o); } journal = []; } };
}

// Custo estimado (s), calibrado nas medições do Google de 25-26/10 (MEDICAO-DESEMPENHO): a execução começa em ~2 s
// (o clique, que não lê nada, leva 1,6-3,2 s); a primeira leitura, e toda leitura depois de gravar, espera o recálculo
// (~4,5 s: "gravar célula solta e ler" 4,7-5,3 s); ler uma aba inteira soma ~4,5 s; flush com gravação pendente ~2,5 s,
// e o mesmo para as gravações que sobram no fim; abrir o módulo leve 1,8 s (completo 11,4 s); propriedade ~0,05 s.
// Confere com o medido: CARTEIRA A1 10,6-12,4 s, D64 10,2-11,3 s, Caminho 10,2 s.
function custo(log, modulo) {
  let s = 2, b = 0, pend = 0;
  for (const e of log) {
    if (e.t === 'R') { if (e.barreira) { s += 4.5; b++; } if (e.inteira || e.n > 20000) s += 4.5; else if (e.n > 3000) s += 1; pend = 0; }
    if (e.t === 'W') pend++;
    if (e.t === 'F') { if (pend) { s += 2.5; b++; } pend = 0; }
    if (e.t === 'P') s += 0.05;
    if (e.t === 'M') s += modulo || 1.8;
  }
  if (pend) s += 2.5;
  return { s: Math.round(s * 10) / 10, barreiras: b, leituras: log.filter(e => e.t === 'R').length, gravacoes: log.filter(e => e.t === 'W').length,
    modulo: log.some(e => e.t === 'M') };
}
// O projeto exportado com o módulo do pacote leve trocado pelo mesmo módulo mais os remendos do `desde`-ésimo em diante.
// As fatias viram uma só (R53_CODIGO_NOVO_) e o hash do carregador passa a ser o do módulo novo; serve só ao arnês.
function projetoComIncremento(projeto, dump, desde, ate) {
  const { aplicarIncremento, remendos } = require('./diagnostico-android/instalar_pacote_leve');
  const p = JSON.parse(JSON.stringify(projeto)), cod = p.files.find(f => f.name === 'Codigo');
  const nomes = /Utilities\.base64Decode\(\[([^\]]+)\]/.exec(cod.source)[1];
  const A = criar(dump);
  for (const f of p.files.filter(f => f.type !== 'JSON')) vm.runInContext(f.source + '\n', A.ctx, { filename: f.name });
  const velho = zlib.gunzipSync(Buffer.from(vm.runInContext('[' + nomes + '].join("")', A.ctx), 'base64')).toString('utf8');
  const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
  const hv = /hash!=='([0-9a-f]{64})'/.exec(cod.source)[1];
  if (sha(velho) !== hv) throw Error('módulo do projeto divergente do hash');
  const novo = aplicarIncremento(velho, remendos().slice(0, ate), desde), hn = sha(novo);
  cod.source = cod.source.replace('[' + nomes + ']', '[R53_CODIGO_NOVO_]').replace(hv, hn) +
    '\nvar R53_CODIGO_NOVO_=' + JSON.stringify(zlib.gzipSync(Buffer.from(novo, 'utf8')).toString('base64')) + ';\n';
  return { projeto: p, velho, novo, hashVelho: hv, hashNovo: hn };
}
// Quantos remendos do pacote_leve_remendos.json o módulo do projeto exportado já tem, pelo hash dele: a exportação
// de 25/10 é da cópia de teste (22º); a de 26/10 à noite, da oficial Era da Revolução (38º).
const REMENDOS_POR_HASH = { '9d1cec81': 22, '52fc6903': 38 };
function remendosDoProjeto(projeto) {
  const hv = /hash!=='([0-9a-f]{64})'/.exec(projeto.files.find(f => f.name === 'Codigo').source)[1];
  return REMENDOS_POR_HASH[hv.slice(0, 8)];
}
module.exports = { criar, custo, projetoComIncremento, remendosDoProjeto };
