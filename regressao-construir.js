// Roda no node, sem Sheets: o construir() inteiro, do começo ao fim, num Sheets de mentira que é RIGOROSO.
//
// Por que existe (01/10/2026): o construir() ganhou a FICHA PESSOAL — nota de caixa, formato de número, cor de aviso,
// grupo de linhas, grupo de colunas dentro de outro, fórmula gravada em lote, trava por faixa — e nenhum validador
// executava esse caminho. Os outros testes rodam função a função; este roda o script como o editor do Apps Script roda.
//
// O que o Sheets de mentira cobra, porque o de verdade cobra:
//   - método que não existe no Apps Script estoura (a lista de nomes mora em REAIS, e não sai do código testado);
//   - faixa fora do tamanho da aba estoura;
//   - matriz de tamanho diferente da faixa estoura (setValues, setBackgrounds, setFormulas...);
//   - mesclar por cima de um pedaço de outra mesclagem estoura;
//   - pedir um grupo de linhas ou de colunas que não existe estoura.
// Depois do construir() ele confere o que ficou na planilha, e usa a planilha montada: escolhe o Caminho na FICHA,
// marca um grupo de treino e anota uma missão, passando pelo onEdit de verdade.
//
// node regressao-construir.js
'use strict';
const fs = require('fs'), vm = require('vm'), path = require('path');
const RAIZ = __dirname;
const GS = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Codigo.gs'), 'utf8');
const FICHA_SRC = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Ficha.gs'), 'utf8');
const ABAS = JSON.parse(FICHA_SRC.match(/var ABAS = ([\s\S]*?);\n\nvar ARTE = /)[1]);

let falhas = 0;
const ok = (nome, cond, det = '') => { console.log((cond ? '  ok    ' : '  FALHA ') + nome + (cond ? '' : '  <- ' + det)); if (!cond) falhas++; };

// ---------------------------------------------------------------------------------------------
// os nomes que o Apps Script tem, por tipo de objeto (da documentação do Spreadsheet Service)
// ---------------------------------------------------------------------------------------------
const REAIS = {
  Spreadsheet: 'getSpreadsheetLocale setSpreadsheetLocale getSheetByName insertSheet deleteSheet getSheets setActiveSheet moveActiveSheet getRange getRangeByName setNamedRange getNamedRanges removeNamedRange getId toast getActiveSheet getName getNumSheets getRangeList getUrl getSpreadsheetTimeZone rename',
  Sheet: 'getName setName setHiddenGridlines getMaxColumns getMaxRows deleteColumns deleteRows deleteColumn deleteRow insertColumnsAfter insertRowsAfter insertColumnAfter insertRowAfter setColumnWidths setColumnWidth setRowHeights setRowHeight getRange getRangeList hideSheet showSheet isSheetHidden setConditionalFormatRules getConditionalFormatRules clearConditionalFormatRules setRowGroupControlPosition setColumnGroupControlPosition getRowGroup getColumnGroup getRowGroupDepth getColumnGroupDepth getRowGroupControlPosition getColumnGroupControlPosition getProtections getDataRange getLastRow getLastColumn getImages getParent getSheetId activate getIndex setFrozenRows setFrozenColumns getColumnWidth getRowHeight hideColumns showColumns hideRows showRows collapseAllColumnGroups collapseAllRowGroups expandAllColumnGroups expandAllRowGroups setTabColor protect getSheetName getSheetValues clear',
  Range: 'setBackgrounds setFontFamilies setFontSizes setFontColors setFontWeights setHorizontalAlignments setVerticalAlignments setFontStyles setWraps setValues setValue getValue getValues getDisplayValue getDisplayValues setFormula setFormulas getFormula getFormulas getFormulaR1C1 getFormulasR1C1 setFormulaR1C1 setFormulasR1C1 setTextRotation merge mergeAcross mergeVertically breakApart isPartOfMerge getMergedRanges getNumRows getNumColumns getRow getColumn getLastRow getLastColumn getCell getA1Notation getSheet setBorder insertCheckboxes removeCheckboxes setNumberFormat setNumberFormats getNumberFormat setNote setNotes clearNote getNote getNotes shiftRowGroupDepth shiftColumnGroupDepth setDataValidation setDataValidations getDataValidation clearDataValidations protect getBackground getBackgrounds getFontColor getFontColors setBackground setFontColor setFontFamily setFontSize setFontWeight setFontStyle setFontLine setHorizontalAlignment setVerticalAlignment setWrap setWrapStrategy clearContent clearFormat clear check uncheck isChecked activate offset copyTo getHeight getWidth isBlank setShowHyperlink setRichTextValue getRichTextValue getGridId',
  RangeList: 'setBorder check uncheck setBackground setFontColor getRanges activate clearContent insertCheckboxes removeCheckboxes setValue setNote setFormula setNumberFormat setFontFamily setFontSize setHorizontalAlignment setVerticalAlignment setWrap setFontWeight setFontStyle clear clearNote clearFormat clearDataValidations setDataValidation breakApart setTextRotation trimWhitespace',
  Group: 'collapse expand getControlIndex getDepth getRange isCollapsed remove',
  Protection: 'setDescription getDescription setWarningOnly isWarningOnly remove getRange addEditor addEditors removeEditor removeEditors getEditors canEdit setRange getProtectionType canDomainEdit setDomainEdit getRangeName setRangeName setNamedRange setUnprotectedRanges getUnprotectedRanges',
  NamedRange: 'getName getRange remove setName setRange',
  DataValidationBuilder: 'setAllowInvalid requireValueInList requireValueInRange requireCheckbox setHelpText build requireFormulaSatisfied requireNumberBetween requireTextContains copy withCriteria',
  ConditionalFormatRuleBuilder: 'whenFormulaSatisfied whenTextContains whenTextDoesNotContain whenTextEqualTo whenTextStartsWith whenTextEndsWith whenCellEmpty whenCellNotEmpty whenNumberGreaterThan whenNumberLessThan whenNumberEqualTo whenNumberBetween setBackground setFontColor setBold setItalic setUnderline setStrikethrough setRanges build copy',
  CellImageBuilder: 'setSourceUrl setAltTextTitle setAltTextDescription build toBuilder getAltTextTitle getAltTextDescription getContentUrl getUrl',
  SpreadsheetApp: 'getActive getActiveSpreadsheet getActiveSheet getActiveRange flush newCellImage newDataValidation newConditionalFormatRule newRichTextValue newTextStyle getUi openById openByUrl create',
};
const NOMES = Object.fromEntries(Object.entries(REAIS).map(([k, v]) => [k, new Set(v.split(' '))]));
const CHAMADAS = {};
/** embrulha o objeto: método fora da lista do Apps Script estoura; método da lista que o teste não imita, também */
function rigoroso(tipo, obj) {
  return new Proxy(obj, { get(alvo, nome) {
    if (typeof nome === 'symbol' || nome === 'then' || nome === 'toJSON' || nome === 'inspect' || nome === 'constructor') return alvo[nome];
    if (nome in alvo) {
      if (typeof alvo[nome] === 'function' && NOMES[tipo].has(nome)) CHAMADAS[tipo + '.' + nome] = (CHAMADAS[tipo + '.' + nome] || 0) + 1;
      return alvo[nome];
    }
    if (!NOMES[tipo].has(nome)) throw new Error(`o Apps Script não tem ${tipo}.${nome}()`);
    throw new Error(`o Sheets de mentira ainda não imita ${tipo}.${nome}()`);
  } });
}

const letras = (c) => { let s = ''; while (c > 0) { const m = (c - 1) % 26; s = String.fromCharCode(65 + m) + s; c = Math.floor((c - 1) / 26); } return s; };
const numero = (t) => [...t].reduce((n, ch) => n * 26 + ch.charCodeAt(0) - 64, 0);
function partes(a1) {
  const m = /^(?:'([^']+)'|([^!']+))!(.+)$/.exec(a1);
  const aba = m ? (m[1] || m[2]) : null, resto = (m ? m[3] : a1).replace(/\$/g, '');
  const f = /^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(resto);
  if (!f) throw new Error('endereço que o Sheets não entende: ' + a1);
  const r1 = Number(f[2]), c1 = numero(f[1]), r2 = Number(f[4] || f[2]), c2 = numero(f[3] || f[1]);
  return { aba, r: r1, c: c1, nl: r2 - r1 + 1, nc: c2 - c1 + 1 };
}

function criaSheets() {
  const P = { locale: 'en_US', abas: [], nomeados: {}, props: {}, ativa: null };
  const acha = (nome) => P.abas.find((a) => a.nome === nome) || null;

  function criaAba(nome) {
    const A = { nome, maxR: 1000, maxC: 26, v: new Map(), f: new Map(), notas: new Map(), merges: [], dv: new Map(), cf: [], caixas: new Set(),
                fmt: new Map(), prot: [], oculta: false, grade: true, profL: new Map(), profC: new Map(), fechL: [], fechC: [], posL: 'AFTER', posC: 'AFTER',
                bordas: 0, larg: new Map(), alt: new Map() };
    const dentro = (r, c, nl, nc, que) => {
      if (!(Number.isInteger(r) && Number.isInteger(c) && Number.isInteger(nl) && Number.isInteger(nc)) || r < 1 || c < 1 || nl < 1 || nc < 1
          || r + nl - 1 > A.maxR || c + nc - 1 > A.maxC) {
        throw new Error(`${que}: a faixa ${letras(c)}${r}:${letras(c + nc - 1)}${r + nl - 1} sai da aba ${nome} (${A.maxR} x ${A.maxC})`);
      }
    };
    // o valor de uma fórmula que o script lê de volta: o endereço em ADDRESS, e a referência direta a uma célula
    const calcula = (f) => {
      const semEspaco = f.replace(/\s/g, '');
      const end = [...f.matchAll(/ADDRESS\(ROW\((?:'[^']+'|[A-ZÇÃ_]+)!\$?([A-Z]+)\$?(\d+)\),COLUMN\([^)]*\),4\)/g)].map((m) => m[1] + m[2]);
      if (end.length && semEspaco.startsWith('=ADDRESS(')) return end.join(':');
      const ref = /^=(?:(?:'([^']+)'|([A-ZÇÃ_]+))!)?\$?([A-Z]+)\$?(\d+)$/.exec(f);
      if (ref) { const B = (ref[1] || ref[2]) ? acha(ref[1] || ref[2]) : A; return B ? B.le(Number(ref[4]), numero(ref[3])) : '#REF!'; }
      if (f === '=TRUE') return true;
      return f;                                            // o resto fica como texto: quem precisa da conta é o LibreOffice
    };
    A.le = (r, c) => { const k = r + ',' + c; return A.f.has(k) ? calcula(A.f.get(k)) : (A.v.has(k) ? A.v.get(k) : ''); };
    const blocoDe = (r, c) => A.merges.find((m) => r >= m[0] && r <= m[2] && c >= m[1] && c <= m[3]);
    const matriz = (m, nl, nc, que) => {
      if (!Array.isArray(m) || m.length !== nl || m.some((l) => !Array.isArray(l) || l.length !== nc)) {
        throw new Error(`${que}: a matriz não tem o tamanho da faixa (${nl} x ${nc}) na aba ${nome}`);
      }
    };
    const range = (r, c, nl = 1, nc = 1) => {
      dentro(r, c, nl, nc, 'getRange');
      const cada = (fn) => { for (let i = 0; i < nl; i++) for (let j = 0; j < nc; j++) fn(r + i, c + j, i, j); };
      const formato = (que) => (m) => { matriz(m, nl, nc, que); return R; };
      const R = rigoroso('Range', {
        getRow: () => r, getColumn: () => c, getNumRows: () => nl, getNumColumns: () => nc, getLastRow: () => r + nl - 1, getLastColumn: () => c + nc - 1,
        getA1Notation: () => letras(c) + r + (nl > 1 || nc > 1 ? ':' + letras(c + nc - 1) + (r + nl - 1) : ''),
        getSheet: () => A.api, getCell: (i, j) => range(r + i - 1, c + j - 1),
        setBackgrounds: formato('setBackgrounds'), setFontFamilies: formato('setFontFamilies'), setFontSizes: formato('setFontSizes'),
        setFontColors: formato('setFontColors'), setFontWeights: formato('setFontWeights'), setHorizontalAlignments: formato('setHorizontalAlignments'),
        setVerticalAlignments: formato('setVerticalAlignments'), setFontStyles: formato('setFontStyles'), setWraps: formato('setWraps'),
        getBackgrounds: () => [...Array(nl)].map(() => Array(nc).fill('#120F1D')), getFontColors: () => [...Array(nl)].map(() => Array(nc).fill('#F4F1F7')),
        getBackground: () => '#120F1D',
        setValues: (m) => { matriz(m, nl, nc, 'setValues'); cada((i, j, a, b) => { A.f.delete(i + ',' + j); if (m[a][b] === '') A.v.delete(i + ',' + j); else A.v.set(i + ',' + j, m[a][b]); }); return R; },
        setValue: (x) => { A.f.delete(r + ',' + c); A.v.set(r + ',' + c, x); return R; },
        getValue: () => A.le(r, c), getValues: () => [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => A.le(r + i, c + j))),
        setFormula: (f) => { if (typeof f !== 'string' || f[0] !== '=') throw new Error('setFormula sem fórmula em ' + nome); A.f.set(r + ',' + c, f); return R; },
        setFormulas: (m) => { matriz(m, nl, nc, 'setFormulas'); cada((i, j, a, b) => { if (typeof m[a][b] !== 'string' || m[a][b][0] !== '=') throw new Error('setFormulas com célula sem fórmula em ' + nome); A.f.set(i + ',' + j, m[a][b]); }); return R; },
        getFormula: () => A.f.get(r + ',' + c) || '', getFormulas: () => [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => A.f.get((r + i) + ',' + (c + j)) || '')),
        getFormulasR1C1: () => [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => A.f.get((r + i) + ',' + (c + j)) || '')),
        setFormulaR1C1: (f) => { A.f.set(r + ',' + c, f); return R; },
        setTextRotation: (g) => { if (typeof g !== 'number') throw new Error('setTextRotation quer graus'); return R; },
        merge: () => {
          for (const m of A.merges) {
            const cruza = r <= m[2] && r + nl - 1 >= m[0] && c <= m[3] && c + nc - 1 >= m[1];
            const contem = r <= m[0] && c <= m[1] && r + nl - 1 >= m[2] && c + nc - 1 >= m[3];
            if (cruza && !contem) throw new Error(`merge: ${R.getA1Notation()} pega um pedaço da mesclagem ${letras(m[1])}${m[0]}:${letras(m[3])}${m[2]} na aba ${nome}`);
          }
          A.merges = A.merges.filter((m) => !(r <= m[0] && c <= m[1] && r + nl - 1 >= m[2] && c + nc - 1 >= m[3]));
          A.merges.push([r, c, r + nl - 1, c + nc - 1]);
          return R;
        },
        isPartOfMerge: () => { let algum = false; cada((i, j) => { if (blocoDe(i, j)) algum = true; }); return algum; },
        getMergedRanges: () => { const vistos = new Set(), out = []; cada((i, j) => { const m = blocoDe(i, j); if (m && !vistos.has(m)) { vistos.add(m); out.push(range(m[0], m[1], m[2] - m[0] + 1, m[3] - m[1] + 1)); } }); return out; },
        setBorder: (...a) => { if (a.length !== 8) throw new Error('setBorder quer oito argumentos'); A.bordas++; return R; },
        insertCheckboxes: () => { cada((i, j) => A.caixas.add(i + ',' + j)); return R; },
        setNumberFormat: (f) => { if (typeof f !== 'string') throw new Error('setNumberFormat quer texto'); cada((i, j) => A.fmt.set(i + ',' + j, f)); return R; },
        setNote: (t) => { if (t === '' || t === null) A.notas.delete(r + ',' + c); else A.notas.set(r + ',' + c, String(t)); return R; },
        clearNote: () => { cada((i, j) => A.notas.delete(i + ',' + j)); return R; }, getNote: () => A.notas.get(r + ',' + c) || '',
        shiftRowGroupDepth: (d) => { for (let i = r; i < r + nl; i++) A.profL.set(i, (A.profL.get(i) || 0) + d); return R; },
        shiftColumnGroupDepth: (d) => { for (let j = c; j < c + nc; j++) A.profC.set(j, (A.profC.get(j) || 0) + d); return R; },
        setDataValidation: (regra) => { if (!regra || !regra.__regra) throw new Error('setDataValidation sem regra montada'); cada((i, j) => A.dv.set(i + ',' + j, regra)); return R; },
        getDataValidation: () => A.dv.get(r + ',' + c) || null,
        protect: () => { const p = { desc: '', aviso: false, a1: R.getA1Notation() }; A.prot.push(p);
          const api = rigoroso('Protection', { setDescription: (d) => { p.desc = d; return api; }, getDescription: () => p.desc, setWarningOnly: (b) => { p.aviso = b; return api; },
            remove: () => { A.prot = A.prot.filter((x) => x !== p); } }); p.api = api; return api; },
        setBackground: () => R, setFontColor: () => R, setFontFamily: () => R, setFontSize: () => R, setFontWeight: () => R, setFontStyle: () => R,
        setHorizontalAlignment: () => R, setVerticalAlignment: () => R,
        clearContent: () => { cada((i, j) => { A.v.delete(i + ',' + j); A.f.delete(i + ',' + j); }); return R; },
      });
      return R;
    };
    const porA1 = (a1) => { const p = partes(a1); return range(p.r, p.c, p.nl, p.nc); };
    const grupo = (prof, fechados, idx, d, que) => {
      if ((prof.get(idx) || 0) < d) throw new Error(`${que}(${idx}, ${d}): não há grupo dessa profundidade ali, na aba ${nome}`);
      let a = idx, b = idx;
      while ((prof.get(a - 1) || 0) >= d) a--;
      while ((prof.get(b + 1) || 0) >= d) b++;
      return rigoroso('Group', { collapse: () => { fechados.push([a, b, d]); }, getDepth: () => d, isCollapsed: () => fechados.some((g) => g[0] === a && g[1] === b && g[2] === d) });
    };
    A.api = rigoroso('Sheet', {
      getName: () => A.nome, setHiddenGridlines: (b) => { A.grade = !b; }, getMaxColumns: () => A.maxC, getMaxRows: () => A.maxR,
      deleteColumns: (ini, n) => { if (ini + n - 1 !== A.maxC) throw new Error('o teste só apaga colunas do fim'); A.maxC -= n; },
      deleteRows: (ini, n) => { if (ini + n - 1 !== A.maxR) throw new Error('o teste só apaga linhas do fim'); A.maxR -= n; },
      insertColumnsAfter: (depois, n) => { if (depois !== A.maxC) throw new Error('o teste só insere colunas no fim'); A.maxC += n; },
      insertRowsAfter: (depois, n) => { if (depois !== A.maxR) throw new Error('o teste só insere linhas no fim'); A.maxR += n; },
      setColumnWidths: (ini, n, px) => { dentro(1, ini, 1, n, 'setColumnWidths'); for (let j = ini; j < ini + n; j++) A.larg.set(j, px); },
      setRowHeights: (ini, n, px) => { dentro(ini, 1, n, 1, 'setRowHeights'); for (let i = ini; i < ini + n; i++) A.alt.set(i, px); },
      getRange: (a, b, c, d) => (typeof a === 'string' ? porA1(a) : range(a, b, c, d)),
      getRangeList: (lista) => { const rs = lista.map(porA1); return rigoroso('RangeList', {
        setBorder: (...a) => { if (a.length !== 8) throw new Error('setBorder quer oito argumentos'); A.bordas++; },
        check: () => rs.forEach((x) => { if (!A.caixas.has(x.getRow() + ',' + x.getColumn())) throw new Error('check numa célula que não é caixa de seleção: ' + x.getA1Notation()); x.setValue(true); }),
        uncheck: () => rs.forEach((x) => { if (!A.caixas.has(x.getRow() + ',' + x.getColumn())) throw new Error('uncheck numa célula que não é caixa de seleção: ' + x.getA1Notation()); x.setValue(false); }),
      }); },
      hideSheet: () => { A.oculta = true; },
      setConditionalFormatRules: (regras) => { if (!regras.every((x) => x && x.__regraCf)) throw new Error('regra de cor que não foi montada'); A.cf = regras; },
      setRowGroupControlPosition: (p) => { if (p !== 'BEFORE' && p !== 'AFTER') throw new Error('posição de controle inválida'); A.posL = p; },
      setColumnGroupControlPosition: (p) => { if (p !== 'BEFORE' && p !== 'AFTER') throw new Error('posição de controle inválida'); A.posC = p; },
      getRowGroup: (i, d) => grupo(A.profL, A.fechL, i, d, 'getRowGroup'), getColumnGroup: (i, d) => grupo(A.profC, A.fechC, i, d, 'getColumnGroup'),
      getProtections: () => A.prot.map((p) => p.api),
      getDataRange: () => range(1, 1, Math.max(1, A.api.getLastRow()), Math.max(1, A.api.getLastColumn())),
      getLastRow: () => Math.max(0, ...[...A.v.keys(), ...A.f.keys()].map((k) => Number(k.split(',')[0]))),
      getLastColumn: () => Math.max(0, ...[...A.v.keys(), ...A.f.keys()].map((k) => Number(k.split(',')[1]))),
      getImages: () => [],
    });
    return A;
  }

  const ss = rigoroso('Spreadsheet', {
    getSpreadsheetLocale: () => P.locale, setSpreadsheetLocale: (l) => { P.locale = l; },
    getSheetByName: (n) => { const a = acha(n); return a ? a.api : null; },
    insertSheet: (n) => { if (acha(n)) throw new Error('já existe a aba ' + n); const A = criaAba(n); P.abas.push(A); P.ativa = A; return A.api; },
    deleteSheet: (s) => { const n = s.getName(); if (P.abas.length === 1) throw new Error('o Sheets não deixa apagar a última aba'); P.abas = P.abas.filter((a) => a.nome !== n); },
    getSheets: () => P.abas.map((a) => a.api),
    setActiveSheet: (s) => { P.ativa = acha(s.getName()); return s; },
    moveActiveSheet: (pos) => { const i = P.abas.indexOf(P.ativa); P.abas.splice(i, 1); P.abas.splice(pos - 1, 0, P.ativa); },
    getRange: (a1) => { const p = partes(a1); const A = p.aba ? acha(p.aba) : P.ativa; if (!A) throw new Error('Range not found: ' + a1); return A.api.getRange(p.r, p.c, p.nl, p.nc); },
    getRangeByName: (n) => P.nomeados[n] || null,
    setNamedRange: (n, r) => { P.nomeados[n] = r; },
    getNamedRanges: () => Object.keys(P.nomeados).map((n) => rigoroso('NamedRange', { getName: () => n, getRange: () => P.nomeados[n], remove: () => { delete P.nomeados[n]; } })),
    getId: () => 'planilha-de-mentira', toast: () => {},
  });
  const ctx = {
    console: { log: () => {} }, Logger: { log: (m) => { P.registro = String(m); } }, Date, Math, JSON,
    Utilities: { sleep: () => {}, base64Decode: (s) => Array.from(Buffer.from(s, 'base64')), base64Encode: (a) => Buffer.from(a).toString('base64') },
    SpreadsheetApp: rigoroso('SpreadsheetApp', {
      getActive: () => ss, flush: () => {},
      newCellImage: () => { const b = {}; const api = rigoroso('CellImageBuilder', {
        setSourceUrl: (u) => { if (!/^data:image\/png;base64,/.test(u)) throw new Error('imagem sem data:image/png'); b.url = u; return api; },
        setAltTextTitle: (t) => { b.titulo = t; return api; }, setAltTextDescription: (d) => { b.desc = d; return api; },
        build: () => ({ valueType: 'IMAGE', getAltTextTitle: () => b.titulo, getAltTextDescription: () => b.desc }) }); return api; },
      newDataValidation: () => { const o = { __regra: true }; const api = rigoroso('DataValidationBuilder', {
        setAllowInvalid: (b) => { o.invalido = b; return api; },
        requireValueInList: (lista, seta) => { if (!Array.isArray(lista) || !lista.length) throw new Error('lista de menu vazia'); o.lista = lista; return api; },
        requireValueInRange: (r, seta) => { if (!r || typeof r.getA1Notation !== 'function') throw new Error('requireValueInRange sem faixa'); o.faixa = r.getSheet().getName() + '!' + r.getA1Notation(); return api; },
        build: () => o }); return api; },
      newConditionalFormatRule: () => { const o = { __regraCf: true }; const api = rigoroso('ConditionalFormatRuleBuilder', {
        whenFormulaSatisfied: (f) => { o.formula = f; return api; }, whenTextContains: (t) => { if (!t) throw new Error('whenTextContains sem texto'); o.contem = t; return api; },
        setBackground: (c) => { o.fundo = c; return api; }, setFontColor: (c) => { o.fonte = c; return api; },
        setRanges: (rs) => { if (!Array.isArray(rs) || !rs.length || !rs.every((x) => x && typeof x.getA1Notation === 'function')) throw new Error('setRanges sem faixa'); o.faixas = rs.map((x) => x.getA1Notation()); return api; },
        build: () => { if (!o.faixas) throw new Error('regra de cor sem faixa'); return o; } }); return api; },
    }),
    PropertiesService: { getDocumentProperties: () => ({ getProperty: (k) => (k in P.props ? P.props[k] : null), setProperty: (k, v) => { P.props[k] = String(v); },
      setProperties: (o) => Object.assign(P.props, o), deleteProperty: (k) => { delete P.props[k]; } }) },
    LockService: { getDocumentLock: () => ({ tryLock: () => true, releaseLock: () => {} }) },
    ScriptApp: { getProjectTriggers: () => [] },
  };
  // os enumerados não passam pelo rigoroso: são valores, e o nome errado dá undefined, que o Sheets de mentira recusa
  ctx.SpreadsheetApp = new Proxy(ctx.SpreadsheetApp, { get(o, k) {
    if (k === 'BorderStyle') return new Proxy({}, { get: (_, n) => { if (!['SOLID', 'SOLID_MEDIUM', 'SOLID_THICK', 'DASHED', 'DOTTED', 'DOUBLE'].includes(n)) throw new Error('BorderStyle.' + String(n) + ' não existe'); return n; } });
    if (k === 'GroupControlTogglePosition') return { BEFORE: 'BEFORE', AFTER: 'AFTER' };
    if (k === 'ProtectionType') return { RANGE: 'RANGE', SHEET: 'SHEET' };
    if (k === 'ValueType') return { IMAGE: 'IMAGE' };
    return o[k];
  } });
  vm.createContext(ctx); vm.runInContext(FICHA_SRC, ctx); vm.runInContext(GS, ctx);
  // a planilha nova do Google nasce com uma aba só
  P.abas.push(criaAba('Página1')); P.ativa = P.abas[0];
  return { P, ss, ctx, acha };
}

// ---------------------------------------------------------------------------------------------
console.log('O construir() DO COMEÇO AO FIM');
const S = criaSheets();
let erro = null;
try { S.ctx.construir(); } catch (e) { erro = e; }
ok('o construir() roda inteiro, sem chamar nada que o Apps Script não tem e sem sair de nenhuma aba', !erro, erro ? erro.message : '');
if (erro) { console.log('\n>>> O construir() PAROU: ' + erro.message); process.exit(1); }
const { P } = S;
ok('as abas nascem na ordem do ABAS, e a planilha termina em português', P.abas.map((a) => a.nome).join('|') === ABAS.map((a) => a.nome).join('|') && P.locale === 'pt_BR',
   P.abas.map((a) => a.nome).join(', ') + ' · ' + P.locale);
ok('cada aba fica do tamanho que o gerador mediu', ABAS.every((s) => { const A = S.acha(s.nome); return A.maxR === s.rows && A.maxC === s.cols; }),
   ABAS.map((s) => { const A = S.acha(s.nome); return `${s.nome} ${A.maxR}x${A.maxC} (${s.rows}x${s.cols})`; }).join(' · '));
ok('as ocultas ficam ocultas, e só elas', ABAS.every((s) => S.acha(s.nome).oculta === !!s.oculta));
const formulasDoAbas = (s) => s.vals.filter((t) => typeof t[2] === 'string' && t[2][0] === '=');
ok('toda fórmula do ABAS chega à célula dela, igual',
   ABAS.every((s) => formulasDoAbas(s).every((t) => S.acha(s.nome).f.get(t[0] + ',' + t[1]) === t[2])),
   ABAS.map((s) => s.nome + ' ' + formulasDoAbas(s).filter((t) => S.acha(s.nome).f.get(t[0] + ',' + t[1]) !== t[2]).length).join(' · '));
const totalF = ABAS.reduce((n, s) => n + formulasDoAbas(s).length, 0);
ok(`as ${totalF} fórmulas vão em lotes, e não uma chamada por célula`, CHAMADAS['Range.setFormulas'] > 0 && CHAMADAS['Range.setFormulas'] < totalF / 2 && !CHAMADAS['Range.setFormula'],
   `${CHAMADAS['Range.setFormulas']} chamadas de setFormulas, ${CHAMADAS['Range.setFormula'] || 0} de setFormula`);
ok('toda mesclagem do ABAS existe na aba', ABAS.every((s) => s.merges.every((m) => S.acha(s.nome).merges.some((x) => x.join() === m.join()))));
ok('todo menu do ABAS vira validação na célula dele',
   ABAS.every((s) => (s.dv || []).every((d) => d[0].replace(/\$/g, '').split(' ').every((f) => { const p = partes(f); return S.acha(s.nome).dv.has(p.r + ',' + p.c); }))));
ok('toda caixa de seleção medida vira caixa', ABAS.every((s) => (s.caixas || []).every((c) => S.acha(s.nome).caixas.has(c[1] + ',' + c[0]) && S.acha(s.nome).caixas.has((c[1] + c[2] - 1) + ',' + c[0]))));
ok('a caixa da paleta nasce na CARTEIRA, com os três intervalos nomeados', ['PALETA_ESCOLHIDA', 'PALETA_ROTULO', 'PALETA_AVISO'].every((n) => P.nomeados[n]) && /paleta: criada em CARTEIRA!/.test(P.registro || ''),
   String(P.registro).slice(0, 200));
ok('o registro do construir() fala da ficha pessoal', /ficha pessoal: \d+ nota/.test(P.registro || ''), String(P.registro).slice(-200));

console.log('\nA FICHA PESSOAL, MONTADA');
const NOME = 'FICHA PESSOAL';
const spec = ABAS.find((a) => a.nome === NOME), A = S.acha(NOME);
ok(`as ${spec.notas.length} notas de caixa estão nas células delas`, spec.notas.every((n) => { const p = partes(n[0]); return A.notas.get(p.r + ',' + p.c) === n[1]; }));
ok('o formato de número chega à caixa dos ienes', spec.formatos.length >= 1 && spec.formatos.every((f) => { const p = partes(f[0]); return A.fmt.get(p.r + ',' + p.c) === f[1]; }));
ok(`as ${spec.condicional.length} regras de cor de aviso ficam na aba, cada uma na faixa dela`,
   A.cf.length === spec.condicional.length && A.cf.every((r, i) => r.contem === spec.condicional[i].contem && r.faixas.join() === spec.condicional[i].faixas.join()
   && (r.fundo || null) === (spec.condicional[i].fundo || null) && r.fonte === spec.condicional[i].fonte), JSON.stringify(A.cf).slice(0, 200));
const [gl] = spec.grupos.lin, [painel, ext] = spec.grupos.col;
const prof = (m, a, b) => { const s = new Set(); for (let i = a; i <= b; i++) s.add(m.get(i) || 0); return [...s].join(','); };
ok('o treino é um grupo de linhas aberto, com o botão em cima', prof(A.profL, gl[0], gl[1]) === '1' && !(A.profL.get(gl[0] - 1) || 0) && !(A.profL.get(gl[1] + 1) || 0)
   && A.fechL.length === 0 && A.posL === 'BEFORE', `profundidade ${prof(A.profL, gl[0], gl[1])}, fechados ${JSON.stringify(A.fechL)}`);
ok('o painel de XP é um grupo de colunas fechado, com o botão antes dele', prof(A.profC, painel[0], ext[0] - 1) === '1' && !(A.profC.get(painel[0] - 1) || 0)
   && A.fechC.some((g) => g[0] === painel[0] && g[1] === painel[1] && g[2] === 1) && A.posC === 'BEFORE', JSON.stringify(A.fechC));
ok('a extensão é um grupo dentro do painel, e também nasce fechada', prof(A.profC, ext[0], ext[1]) === '2' && A.fechC.some((g) => g[0] === ext[0] && g[1] === ext[1] && g[2] === 2), JSON.stringify(A.fechC));
ok('a extensão fecha antes do painel (de dentro para fora)', A.fechC.findIndex((g) => g[2] === 2) < A.fechC.findIndex((g) => g[2] === 1));
ok(`as fórmulas da aba estão travadas em ${spec.protegidas.length} faixas, só com aviso`, A.prot.length === spec.protegidas.length && A.prot.every((p) => p.aviso && p.desc.indexOf('fórmula · ' + NOME + '!') === 0),
   `${A.prot.length} travas`);
const F = S.acha('FICHA'), idx = S.ctx.indice();
const travada = (a1) => F.prot.some((p) => p.a1 === a1 && p.aviso);
ok('na FICHA, o XP e o EQUIPAMENTO são fórmula travada com aviso, e o EQUIPAMENTO não tem mais menu',
   [idx['xp'], idx['equipamento']].every((a1) => { const p = partes(a1); return F.f.has(p.r + ',' + p.c) && travada(a1); })
   && !F.dv.has(partes(idx['equipamento']).r + ',' + partes(idx['equipamento']).c), `xp ${idx['xp']}, equipamento ${idx['equipamento']}`);
ok('o nível da FICHA continua digitável: valor solto, sem trava', (() => { const p = partes(idx['nivel']); return !F.f.has(p.r + ',' + p.c) && !travada(idx['nivel']); })());
const vivas = S.ctx.tabelaDaDados_(S.ss.getSheetByName('DADOS').getDataRange().getValues(), 'nota viva', ['texto da nota', 'caixa da nota']);
ok('as três notas que mudam com a ficha nascem escritas', vivas.length === 3 && vivas.every((n) => { const p = partes(n['caixa da nota']); return A.notas.has(p.r + ',' + p.c); }));

console.log('\nA PLANILHA MONTADA, EM USO (pelo onEdit de verdade)');
const ed = (aba, a1, value, oldValue) => ({ range: S.ss.getSheetByName(aba).getRange(a1), value, oldValue });
const t = S.ctx.caixasDeTreino_(S.ss.getSheetByName('DADOS').getDataRange().getValues());
const marcadas = () => t.armas.concat(t.grupos).filter((x) => { const p = partes(x.caixa); return A.le(p.r, p.c) === true; }).length;
let erroUso = null;
try {
  S.ss.getSheetByName('FICHA').getRange(idx['caminho']).setValue('Bastião');
  S.ctx.onEdit(ed('FICHA', idx['caminho'], 'Bastião', 'Escolha seu Caminho'));
} catch (e) { erroUso = e; }
ok('escolher Bastião na FICHA passa por todos os gatilhos dela sem erro e marca as 65 caixas de treino', !erroUso && marcadas() === 65, erroUso ? erroUso.message : marcadas() + ' marcadas');
try {
  S.ss.getSheetByName('FICHA').getRange(idx['caminho']).setValue('Emanador');
  S.ctx.onEdit(ed('FICHA', idx['caminho'], 'Emanador', 'Bastião'));
} catch (e) { erroUso = e; }
ok('trocar para Emanador deixa só Arma de Fogo e Balestra', !erroUso && marcadas() === 11, erroUso ? erroUso.message : marcadas() + ' marcadas');
const g = t.grupos.find((x) => x.categoria === 'Massa');
try { S.ss.getSheetByName(NOME).getRange(g.caixa).setValue(true); S.ctx.pessoalEditada_(ed(NOME, g.caixa, 'TRUE')); } catch (e) { erroUso = e; }
ok('marcar o grupo Massa na aba montada marca as cinco armas dele', !erroUso && marcadas() === 11 + 1 + t.armas.filter((x) => x.categoria === 'Massa').length, erroUso ? erroUso.message : marcadas() + ' marcadas');
const ip = S.ctx.indicePessoal_();
try {
  const px = partes(ip['xp total']); A.f.delete(px.r + ',' + px.c); A.v.set(px.r + ',' + px.c, 500);       // o LibreOffice é quem faz a soma; aqui o total é posto à mão
  const m3 = S.ctx.limitesA1_(ip['missões 3']);
  S.ctx.pessoalEditada_(ed(NOME, letras(m3.c1 + 1) + m3.l1, 'Longa'));
} catch (e) { erroUso = e; }
ok('anotar missão na extensão, com 500 de XP, sobe o nível da FICHA para o 4', !erroUso && F.le(partes(idx['nivel']).r, partes(idx['nivel']).c) === 4, erroUso ? erroUso.message : String(F.le(partes(idx['nivel']).r, partes(idx['nivel']).c)));
let erroSel = null;
try { S.ctx.onSelectionChange({ range: S.ss.getSheetByName(NOME).getRange('D10') }); S.ctx.onOpen({}); } catch (e) { erroSel = e; }
ok('clicar numa célula e abrir a planilha não estouram', !erroSel, erroSel ? erroSel.message : '');

console.log('\nO PESO DO construir(), EM CHAMADAS');
const peso = ['Range.merge', 'Range.setFormulas', 'Range.protect', 'RangeList.setBorder', 'Range.setDataValidation', 'Range.setNote', 'Range.insertCheckboxes', 'Range.setTextRotation']
  .map((k) => k.split('.')[1] + ' ' + (CHAMADAS[k] || 0)).join(' · ');
console.log('       ' + peso);

console.log('');
if (falhas) { console.log(`>>> ${falhas} FALHA(S) NO construir()`); process.exit(1); }
console.log('>>> O construir() MONTA A PLANILHA INTEIRA, E A PLANILHA MONTADA FUNCIONA');
