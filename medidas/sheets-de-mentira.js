// O Sheets de mentira, RIGOROSO, que roda o construir() no node. Mora aqui desde 01/10/2026 porque dois programas o
// usam: o regressao-construir.js, que confere a planilha montada, e o medidas/comparar-construir.js, que compara a
// montagem de duas versões do script. Ele guarda tudo o que o construir() grava: valor, fórmula, formato, borda,
// mesclagem, nota, menu, caixa de seleção, trava, grupo, altura e largura.
'use strict';
const vm = require('vm');

// ---------------------------------------------------------------------------------------------
// os nomes que o Apps Script tem, por tipo de objeto (da documentação do Spreadsheet Service)
// ---------------------------------------------------------------------------------------------
const REAIS = {
  Spreadsheet: 'getSpreadsheetLocale setSpreadsheetLocale getSheetByName insertSheet deleteSheet getSheets setActiveSheet moveActiveSheet getRange getRangeByName setNamedRange getNamedRanges removeNamedRange getId toast getActiveSheet getName getNumSheets getRangeList getUrl getSpreadsheetTimeZone rename',
  Sheet: 'getName setName setHiddenGridlines getMaxColumns getMaxRows deleteColumns deleteRows deleteColumn deleteRow insertColumnsAfter insertRowsAfter insertColumnAfter insertRowAfter setColumnWidths setColumnWidth setRowHeights setRowHeight getRange getRangeList hideSheet showSheet isSheetHidden setConditionalFormatRules getConditionalFormatRules clearConditionalFormatRules setRowGroupControlPosition setColumnGroupControlPosition getRowGroup getColumnGroup getRowGroupDepth getColumnGroupDepth getRowGroupControlPosition getColumnGroupControlPosition getProtections getDataRange getLastRow getLastColumn getImages getParent getSheetId activate getIndex setFrozenRows setFrozenColumns getColumnWidth getRowHeight hideColumns showColumns hideRows showRows collapseAllColumnGroups collapseAllRowGroups expandAllColumnGroups expandAllRowGroups expandRowGroupsUpToDepth expandColumnGroupsUpToDepth setTabColor protect getSheetName getSheetValues clear',
  Range: 'setBackgrounds setFontFamilies setFontSizes setFontColors setFontWeights setHorizontalAlignments setVerticalAlignments setFontStyles setWraps setValues setValue getValue getValues getDisplayValue getDisplayValues setFormula setFormulas getFormula getFormulas getFormulaR1C1 getFormulasR1C1 setFormulaR1C1 setFormulasR1C1 setTextRotation merge mergeAcross mergeVertically breakApart isPartOfMerge getMergedRanges getNumRows getNumColumns getRow getColumn getLastRow getLastColumn getCell getA1Notation getSheet setBorder insertCheckboxes removeCheckboxes setNumberFormat setNumberFormats getNumberFormat setNote setNotes clearNote getNote getNotes shiftRowGroupDepth shiftColumnGroupDepth setDataValidation setDataValidations getDataValidation getDataValidations clearDataValidations protect getBackground getBackgrounds getFontColor getFontColors setBackground setFontColor setFontFamily setFontSize setFontWeight setFontStyle setFontLine setHorizontalAlignment setVerticalAlignment setWrap setWrapStrategy clearContent clearFormat clear check uncheck isChecked activate offset copyTo getHeight getWidth isBlank setShowHyperlink setRichTextValue getRichTextValue getGridId',
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
// A fórmula como ela fica quando o Sheets a copia `dl` linhas abaixo e `dc` colunas à direita: a linha e a coluna de
// toda referência sem cifrão andam, e o que está entre aspas fica como está. É a mesma conta do `desloca` do
// ficha/emitir_gs.py, que decide quais fórmulas saem do ABAS para serem preenchidas por cópia.
function deslocaFormula(f, dl, dc) {
  return f.split(/("(?:[^"]|"")*")/).map((p, i) => (i % 2 ? p : p.replace(/(?<![A-Za-z0-9_.])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![A-Za-z0-9_(])/g,
    (_, ac, col, al, lin) => ac + (ac || !dc ? col : letras(numero(col) + dc)) + al + (al ? lin : Number(lin) + dl)))).join('');
}
function partes(a1) {
  const m = /^(?:'([^']+)'|([^!']+))!(.+)$/.exec(a1);
  const aba = m ? (m[1] || m[2]) : null, resto = (m ? m[3] : a1).replace(/\$/g, '');
  const f = /^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(resto);
  if (!f) throw new Error('endereço que o Sheets não entende: ' + a1);
  const r1 = Number(f[2]), c1 = numero(f[1]), r2 = Number(f[4] || f[2]), c2 = numero(f[3] || f[1]);
  return { aba, r: r1, c: c1, nl: r2 - r1 + 1, nc: c2 - c1 + 1 };
}

// `extras` troca peças do ambiente: o teste passa um relógio que corre, para a montagem achar que demorou
function criaSheets(FICHA_SRC, GS, extras) {
  const P = { locale: 'en_US', abas: [], nomeados: {}, props: {}, ativa: null, registros: [], orfas: [] };
  // O que o Sheets de verdade estraga calado, e este anota em P.orfas: a fórmula gravada antes de a aba citada existir
  // (ou antes de ela ter a linha e a coluna citadas) fica em #REF!, e a fórmula com vírgula ou ponto decimal gravada
  // com a planilha fora do inglês vira #ERROR!.
  const semAspas = (f) => f.replace(/"[^"]*"/g, '""');
  const confereFormula = (onde, f) => {
    const limpa = semAspas(f);
    if (P.locale !== 'en_US' && (limpa.includes(',') || /\d\.\d/.test(limpa))) P.orfas.push(`${onde}: fórmula com vírgula ou ponto gravada em ${P.locale}`);
    for (const m of limpa.matchAll(/(?:'([^']+)'|([A-Za-zÀ-ÿ_][\wÀ-ÿ]*))!\$?([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?/g)) {
      const B = acha(m[1] || m[2]);
      if (!B) { P.orfas.push(`${onde}: cita a aba ${m[1] || m[2]}, que ainda não existe`); continue; }
      if (numero(m[5] || m[3]) > B.maxC || Number(m[6] || m[4]) > B.maxR) P.orfas.push(`${onde}: cita ${m[0]}, fora do tamanho da aba (${B.maxR} x ${B.maxC})`);
    }
  };
  const acha = (nome) => P.abas.find((a) => a.nome === nome) || null;

  function criaAba(nome) {
    const A = { nome, maxR: 1000, maxC: 26, v: new Map(), f: new Map(), notas: new Map(), merges: [], dv: new Map(), cf: [], caixas: new Set(),
                fmt: new Map(), prot: [], oculta: false, grade: true, profL: new Map(), profC: new Map(), fechL: [], fechC: [], posL: 'AFTER', posC: 'AFTER',
                bordas: 0, larg: new Map(), alt: new Map(), est: new Map(), lados: new Map() };
    const poe = (i, j, que, val) => { const k = i + ',' + j; if (!A.est.has(k)) A.est.set(k, {}); A.est.get(k)[que] = val; };
    const borda = (r, c, nl, nc, a) => { if (a.length !== 8) throw new Error('setBorder quer oito argumentos'); A.bordas++;
      const marca = (i, j, lado) => A.lados.set(i + ',' + j + ',' + lado, a[6] + '|' + a[7]);
      for (let i = r; i < r + nl; i++) for (let j = c; j < c + nc; j++) {
        if (a[0] && i === r) marca(i, j, 'cima'); if (a[1] && j === c) marca(i, j, 'esquerda');
        if (a[2] && i === r + nl - 1) marca(i, j, 'baixo'); if (a[3] && j === c + nc - 1) marca(i, j, 'direita');
        if (a[4] || a[5]) marca(i, j, 'dentro'); } };
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
      const formato = (que) => (m) => { matriz(m, nl, nc, que); cada((i, j, a, b) => poe(i, j, que, m[a][b])); return R; };
      const um = (que) => (x) => { cada((i, j) => poe(i, j, que, x)); return R; };
      const grava = (i, j, x) => { const k = i + ',' + j; if (typeof x === 'string' && x[0] === '=') { confereFormula(nome + '!' + letras(j) + i, x); A.v.delete(k); A.f.set(k, x); } else { A.f.delete(k); if (x === '') A.v.delete(k); else A.v.set(k, x); } };
      const mescla = (r0, c0, l, n) => {
        for (const m of A.merges) {
          const cruza = r0 <= m[2] && r0 + l - 1 >= m[0] && c0 <= m[3] && c0 + n - 1 >= m[1];
          const contem = r0 <= m[0] && c0 <= m[1] && r0 + l - 1 >= m[2] && c0 + n - 1 >= m[3];
          if (cruza && !contem) throw new Error(`merge: ${letras(c0)}${r0}:${letras(c0 + n - 1)}${r0 + l - 1} pega um pedaço da mesclagem ${letras(m[1])}${m[0]}:${letras(m[3])}${m[2]} na aba ${nome}`);
        }
        A.merges = A.merges.filter((m) => !(r0 <= m[0] && c0 <= m[1] && r0 + l - 1 >= m[2] && c0 + n - 1 >= m[3]));
        if (l > 1 || n > 1) A.merges.push([r0, c0, r0 + l - 1, c0 + n - 1]);
      };
      const R = rigoroso('Range', {
        getRow: () => r, getColumn: () => c, getNumRows: () => nl, getNumColumns: () => nc, getLastRow: () => r + nl - 1, getLastColumn: () => c + nc - 1,
        getA1Notation: () => letras(c) + r + (nl > 1 || nc > 1 ? ':' + letras(c + nc - 1) + (r + nl - 1) : ''),
        getSheet: () => A.api, getCell: (i, j) => range(r + i - 1, c + j - 1),
        setBackgrounds: formato('setBackgrounds'), setFontFamilies: formato('setFontFamilies'), setFontSizes: formato('setFontSizes'),
        setFontColors: formato('setFontColors'), setFontWeights: formato('setFontWeights'), setHorizontalAlignments: formato('setHorizontalAlignments'),
        setVerticalAlignments: formato('setVerticalAlignments'), setFontStyles: formato('setFontStyles'), setWraps: formato('setWraps'),
        getBackgrounds: () => [...Array(nl)].map(() => Array(nc).fill('#120F1D')), getFontColors: () => [...Array(nl)].map(() => Array(nc).fill('#F4F1F7')),
        getBackground: () => '#120F1D',
        setValues: (m) => { matriz(m, nl, nc, 'setValues'); cada((i, j, a, b) => grava(i, j, m[a][b])); return R; },
        setValue: (x) => { grava(r, c, x); return R; },
        getValue: () => A.le(r, c), getValues: () => [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => A.le(r + i, c + j))),
        setFormula: (f) => { if (typeof f !== 'string' || f[0] !== '=') throw new Error('setFormula sem fórmula em ' + nome); confereFormula(nome + '!' + letras(c) + r, f); A.f.set(r + ',' + c, f); return R; },
        setFormulas: (m) => { matriz(m, nl, nc, 'setFormulas'); cada((i, j, a, b) => { if (typeof m[a][b] !== 'string' || m[a][b][0] !== '=') throw new Error('setFormulas com célula sem fórmula em ' + nome); confereFormula(nome + '!' + letras(j) + i, m[a][b]); A.f.set(i + ',' + j, m[a][b]); }); return R; },
        getFormula: () => A.f.get(r + ',' + c) || '', getFormulas: () => [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => A.f.get((r + i) + ',' + (c + j)) || '')),
        getFormulasR1C1: () => [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => A.f.get((r + i) + ',' + (c + j)) || '')),
        setFormulaR1C1: (f) => { A.f.set(r + ',' + c, f); return R; },
        setTextRotation: (g) => { if (typeof g !== 'number') throw new Error('setTextRotation quer graus'); cada((i, j) => poe(i, j, 'rotacao', g)); return R; },
        merge: () => { mescla(r, c, nl, nc); return R; },
        mergeAcross: () => { for (let i = r; i < r + nl; i++) mescla(i, c, 1, nc); return R; },
        mergeVertically: () => { for (let j = c; j < c + nc; j++) mescla(r, j, nl, 1); return R; },
        isPartOfMerge: () => { let algum = false; cada((i, j) => { if (blocoDe(i, j)) algum = true; }); return algum; },
        getMergedRanges: () => { const vistos = new Set(), out = []; cada((i, j) => { const m = blocoDe(i, j); if (m && !vistos.has(m)) { vistos.add(m); out.push(range(m[0], m[1], m[2] - m[0] + 1, m[3] - m[1] + 1)); } }); return out; },
        setBorder: (...a) => { borda(r, c, nl, nc, a); return R; },
        breakApart: () => { A.merges = A.merges.filter((m) => !(m[0] >= r && m[2] <= r + nl - 1 && m[1] >= c && m[3] <= c + nc - 1)); return R; },
        // A cópia. Sem tipo, é a colagem comum: valor, fórmula (com as referências andando), formato, formato de número
        // e mesclagem. Com PASTE_FORMAT, só o formato, o formato de número e a mesclagem. O destino que é um múltiplo
        // do molde recebe o molde repetido, como no Sheets.
        copyTo: (destino, tipo, transposto) => {
          if (!destino || typeof destino.getA1Notation !== 'function') throw new Error('copyTo sem faixa de destino');
          if (tipo !== undefined && tipo !== 'PASTE_NORMAL' && tipo !== 'PASTE_FORMAT' && tipo !== 'PASTE_FORMULA') throw new Error('copyTo com um tipo que o teste não imita: ' + tipo);
          if (transposto) throw new Error('copyTo transposto: o teste não imita');
          if (destino.getSheet().getName() !== nome) throw new Error('copyTo para outra aba: o teste não imita');
          const dr = destino.getRow(), dcl = destino.getColumn(), dnl = destino.getNumRows(), dnc = destino.getNumColumns();
          if (dnl % nl || dnc % nc) throw new Error(`copyTo: o destino ${destino.getA1Notation()} não é múltiplo do molde ${R.getA1Notation()}`);
          const formato = tipo === undefined || tipo === 'PASTE_NORMAL' || tipo === 'PASTE_FORMAT', conteudo = tipo !== 'PASTE_FORMAT';
          const doMolde = A.merges.filter((m) => m[0] >= r && m[2] <= r + nl - 1 && m[1] >= c && m[3] <= c + nc - 1).map((m) => m.slice());
          if (A.merges.some((m) => m[0] <= r + nl - 1 && m[2] >= r && m[1] <= c + nc - 1 && m[3] >= c && !doMolde.some((x) => x.join() === m.join()))) throw new Error('copyTo: o molde corta uma mesclagem ao meio, em ' + R.getA1Notation());
          for (let br = 0; br < dnl; br += nl) for (let bc = 0; bc < dnc; bc += nc) {
            const dl = dr + br - r, dc = dcl + bc - c;
            for (let i = r; i < r + nl; i++) for (let j = c; j < c + nc; j++) {
              const de = i + ',' + j, para = (i + dl) + ',' + (j + dc);
              if (conteudo) {
                A.v.delete(para); A.f.delete(para);
                if (A.f.has(de)) { const nova = deslocaFormula(A.f.get(de), dl, dc); confereFormula(nome + '!' + letras(j + dc) + (i + dl), nova); A.f.set(para, nova); }
                else if (A.v.has(de)) A.v.set(para, A.v.get(de));
              }
              if (formato) {
                if (A.est.has(de)) A.est.set(para, Object.assign({}, A.est.get(de))); else A.est.delete(para);
                if (A.fmt.has(de)) A.fmt.set(para, A.fmt.get(de)); else A.fmt.delete(para);
              }
            }
            if (formato) {
              const l1 = dr + br, c1 = dcl + bc;
              A.merges = A.merges.filter((m) => !(m[0] >= l1 && m[2] <= l1 + nl - 1 && m[1] >= c1 && m[3] <= c1 + nc - 1));
              if (P.copiaTrazMesclagem !== false) doMolde.forEach((m) => { range(m[0] + dl, m[1] + dc, m[2] - m[0] + 1, m[3] - m[1] + 1).merge(); CHAMADAS['Range.merge']--; });
            }
          }
          return R;
        },
        setDataValidations: (m) => { matriz(m, nl, nc, 'setDataValidations'); cada((i, j, a, b) => { const k = i + ',' + j, regra = m[a][b];
          if (regra !== null && !(regra && regra.__regra)) throw new Error('setDataValidations com uma regra que não foi montada');
          A.dv.delete(k); A.caixas.delete(k);
          if (regra && regra.caixa) A.caixas.add(k); else if (regra) A.dv.set(k, regra); }); return R; },
        getDataValidations: () => [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => A.dv.get((r + i) + ',' + (c + j)) || null)),
        insertCheckboxes: () => { cada((i, j) => A.caixas.add(i + ',' + j)); return R; },
        setNumberFormat: (f) => { if (typeof f !== 'string') throw new Error('setNumberFormat quer texto'); cada((i, j) => A.fmt.set(i + ',' + j, f)); return R; },
        setNote: (t) => { if (t === '' || t === null) A.notas.delete(r + ',' + c); else A.notas.set(r + ',' + c, String(t)); return R; },
        clearNote: () => { cada((i, j) => A.notas.delete(i + ',' + j)); return R; }, getNote: () => A.notas.get(r + ',' + c) || '',
        getNotes: () => [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => A.notas.get((r + i) + ',' + (c + j)) || '')),
        setNotes: (m) => { matriz(m, nl, nc, 'setNotes'); cada((i, j, a, b) => { if (m[a][b] === '' || m[a][b] === null) A.notas.delete(i + ',' + j); else A.notas.set(i + ',' + j, String(m[a][b])); }); return R; },
        shiftRowGroupDepth: (d) => { for (let i = r; i < r + nl; i++) A.profL.set(i, (A.profL.get(i) || 0) + d); return R; },
        shiftColumnGroupDepth: (d) => { for (let j = c; j < c + nc; j++) A.profC.set(j, (A.profC.get(j) || 0) + d); return R; },
        setDataValidation: (regra) => { if (!regra || !regra.__regra) throw new Error('setDataValidation sem regra montada'); cada((i, j) => A.dv.set(i + ',' + j, regra)); return R; },
        getDataValidation: () => A.dv.get(r + ',' + c) || null,
        protect: () => { const p = { desc: '', aviso: false, a1: R.getA1Notation() }; A.prot.push(p);
          const api = rigoroso('Protection', { setDescription: (d) => { p.desc = d; return api; }, getDescription: () => p.desc, setWarningOnly: (b) => { p.aviso = b; return api; },
            remove: () => { A.prot = A.prot.filter((x) => x !== p); } }); p.api = api; return api; },
        setBackground: um('setBackgrounds'), setFontColor: um('setFontColors'), setFontFamily: um('setFontFamilies'), setFontSize: um('setFontSizes'), setFontWeight: um('setFontWeights'), setFontStyle: um('setFontStyles'),
        setHorizontalAlignment: um('setHorizontalAlignments'), setVerticalAlignment: um('setVerticalAlignments'),
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
      const eh = (g) => g[0] === a && g[1] === b && g[2] === d;
      return rigoroso('Group', { collapse: () => { if (!fechados.some(eh)) fechados.push([a, b, d]); },
        expand: () => { const i = fechados.findIndex(eh); if (i >= 0) fechados.splice(i, 1); },
        getDepth: () => d, isCollapsed: () => fechados.some(eh) });
    };
    // todos os grupos que as profundidades formam: em cada profundidade, cada corrida de linhas que chega nela
    const todosOsGrupos = (prof) => { const out = [], max = Math.max(0, ...prof.values()), fim = Math.max(0, ...prof.keys());
      for (let d = 1; d <= max; d++) { let ini = null; for (let i = 1; i <= fim + 1; i++) { const dentro = (prof.get(i) || 0) >= d;
        if (dentro && ini === null) ini = i; if (!dentro && ini !== null) { out.push([ini, i - 1, d]); ini = null; } } }
      return out; };
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
        setBorder: (...a) => { rs.forEach((x) => borda(x.getRow(), x.getColumn(), x.getNumRows(), x.getNumColumns(), a)); },
        setNumberFormat: (f) => { rs.forEach((x) => { x.setNumberFormat(f); CHAMADAS['Range.setNumberFormat']--; }); },
        check: () => rs.forEach((x) => { if (!A.caixas.has(x.getRow() + ',' + x.getColumn())) throw new Error('check numa célula que não é caixa de seleção: ' + x.getA1Notation()); x.setValue(true); }),
        uncheck: () => rs.forEach((x) => { if (!A.caixas.has(x.getRow() + ',' + x.getColumn())) throw new Error('uncheck numa célula que não é caixa de seleção: ' + x.getA1Notation()); x.setValue(false); }),
      }); },
      hideSheet: () => { A.oculta = true; },
      setConditionalFormatRules: (regras) => { if (!regras.every((x) => x && x.__regraCf)) throw new Error('regra de cor que não foi montada');
        regras.forEach((x) => { if (x.formula) confereFormula(nome + ', regra de cor', x.formula); }); A.cf = regras; },
      setRowGroupControlPosition: (p) => { if (p !== 'BEFORE' && p !== 'AFTER') throw new Error('posição de controle inválida'); A.posL = p; },
      setColumnGroupControlPosition: (p) => { if (p !== 'BEFORE' && p !== 'AFTER') throw new Error('posição de controle inválida'); A.posC = p; },
      getRowGroup: (i, d) => grupo(A.profL, A.fechL, i, d, 'getRowGroup'), getColumnGroup: (i, d) => grupo(A.profC, A.fechC, i, d, 'getColumnGroup'),
      collapseAllRowGroups: () => { A.fechL.length = 0; todosOsGrupos(A.profL).forEach((g) => A.fechL.push(g)); },
      getSheetId: () => 1000 + P.abas.indexOf(A),
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
    insertSheet: (n, pos) => { if (acha(n)) throw new Error('já existe a aba ' + n); if (pos !== undefined && !(Number.isInteger(pos) && pos >= 0 && pos <= P.abas.length)) throw new Error('insertSheet: posição ' + pos + ' com ' + P.abas.length + ' aba(s)');
      const A = criaAba(n); if (pos === undefined) P.abas.push(A); else P.abas.splice(pos, 0, A); P.ativa = A; return A.api; },
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
    console: { log: () => {} }, Logger: { log: (m) => { P.registro = String(m); P.registros.push(String(m)); } }, Date, Math, JSON,
    Utilities: { sleep: () => {}, base64Decode: (s) => Array.from(Buffer.from(s, 'base64')), base64Encode: (a) => Buffer.from(a).toString('base64') },
    SpreadsheetApp: rigoroso('SpreadsheetApp', {
      getActive: () => ss, flush: () => {},
      newCellImage: () => { const b = {}; const api = rigoroso('CellImageBuilder', {
        setSourceUrl: (u) => { if (!/^data:image\/png;base64,/.test(u)) throw new Error('imagem sem data:image/png'); b.url = u; return api; },
        setAltTextTitle: (t) => { b.titulo = t; return api; }, setAltTextDescription: (d) => { b.desc = d; return api; },
        build: () => ({ valueType: 'IMAGE', getAltTextTitle: () => b.titulo, getAltTextDescription: () => b.desc, toJSON: () => 'IMAGEM ' + b.titulo + ' ' + b.desc + ' ' + b.url.length }) }); return api; },
      newDataValidation: () => { const o = { __regra: true }; const api = rigoroso('DataValidationBuilder', {
        setAllowInvalid: (b) => { o.invalido = b; return api; },
        requireValueInList: (lista, seta) => { if (!Array.isArray(lista) || !lista.length) throw new Error('lista de menu vazia'); o.lista = lista; return api; },
        requireCheckbox: () => { o.caixa = true; return api; },
        requireValueInRange: (r, seta) => { if (!r || typeof r.getA1Notation !== 'function') throw new Error('requireValueInRange sem faixa'); o.faixa = r.getSheet().getName() + '!' + r.getA1Notation(); return api; },
        build: () => o }); return api; },
      newConditionalFormatRule: () => { const o = { __regraCf: true }; const api = rigoroso('ConditionalFormatRuleBuilder', {
        whenFormulaSatisfied: (f) => { o.formula = f; return api; }, whenTextContains: (t) => { if (!t) throw new Error('whenTextContains sem texto'); o.contem = t; return api; },
        whenTextStartsWith: (t) => { if (!t) throw new Error('whenTextStartsWith sem texto'); o.comeca = t; return api; },
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
    if (k === 'CopyPasteType') return new Proxy({}, { get: (_, n) => { if (!['PASTE_NORMAL', 'PASTE_FORMAT', 'PASTE_FORMULA', 'PASTE_VALUES', 'PASTE_NO_BORDERS', 'PASTE_DATA_VALIDATION', 'PASTE_CONDITIONAL_FORMATTING', 'PASTE_COLUMN_WIDTHS'].includes(n)) throw new Error('CopyPasteType.' + String(n) + ' não existe'); return n; } });
    if (k === 'ProtectionType') return { RANGE: 'RANGE', SHEET: 'SHEET' };
    if (k === 'ValueType') return { IMAGE: 'IMAGE' };
    return o[k];
  } });
  Object.assign(ctx, extras || {});
  vm.createContext(ctx); vm.runInContext(FICHA_SRC, ctx); vm.runInContext(GS, ctx);
  // a planilha nova do Google nasce com uma aba só
  P.abas.push(criaAba('Página1')); P.ativa = P.abas[0];
  return { P, ss, ctx, acha };
}

// ---------------------------------------------------------------------------------------------
// o retrato da planilha montada: tudo o que o construir() deixou, em texto, para comparar duas montagens
// ---------------------------------------------------------------------------------------------
function retrato(P) {
  const mapa = (m) => Object.fromEntries([...m.entries()].sort((a, b) => String(a[0]).localeCompare(String(b[0]))).map(([k, v]) => [k, typeof v === 'object' && v !== null ? JSON.stringify(v) : v]));
  const abas = {};
  for (const A of P.abas) {
    // as travas pelo que cobrem: célula por célula, com aviso ou sem
    const travadas = {};
    for (const p of A.prot) { const f = partes(p.a1); for (let i = f.r; i < f.r + f.nl; i++) for (let j = f.c; j < f.c + f.nc; j++) travadas[i + ',' + j] = p.aviso ? 'aviso' : 'bloqueio'; }
    abas[A.nome] = {
      tamanho: A.maxR + 'x' + A.maxC, oculta: A.oculta, grade: A.grade, valores: mapa(A.v), formulas: mapa(A.f), formato: mapa(A.est), bordas: mapa(A.lados),
      mesclagens: A.merges.map((m) => m.join()).sort(), notas: mapa(A.notas), menus: mapa(A.dv), caixas: [...A.caixas].sort(), numeros: mapa(A.fmt),
      cores_de_aviso: A.cf.map((r) => JSON.stringify(r)), grupos: { linhas: mapa(A.profL), colunas: mapa(A.profC), fechadasL: A.fechL.map(String), fechadasC: A.fechC.map(String), posL: A.posL, posC: A.posC },
      larguras: mapa(A.larg), alturas: mapa(A.alt), travas: A.prot.length, travadas: Object.fromEntries(Object.keys(travadas).sort().map((k) => [k, travadas[k]])),
    };
  }
  return { ordem: P.abas.map((a) => a.nome), idioma: P.locale, nomeados: Object.fromEntries(Object.keys(P.nomeados).sort().map((n) => [n, P.nomeados[n].getSheet().getName() + '!' + P.nomeados[n].getA1Notation()])), abas };
}

module.exports = { criaSheets, retrato, partes, letras, numero, deslocaFormula, CHAMADAS, zeraChamadas: () => { for (const k of Object.keys(CHAMADAS)) delete CHAMADAS[k]; } };
