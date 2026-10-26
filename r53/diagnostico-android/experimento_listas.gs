// SÓ NA CÓPIA DE TESTE (26/10/2026, segunda versão). As listas da DADOS_CUSTOM trocam
// INDIRECT(SWITCH(x; "rótulo"; "'aba'!faixa"; ...)) por CHOOSE(IFERROR(MATCH(x; {rótulos}; 0); n); faixa; ...), que não
// é volátil. Rodar experimentoListas() pelo editor até o registro dizer "iguais" ou "DIFERENTE". Antes de trocar, lê a
// DADOS_CUSTOM em todos os estados dos seletores da CONFIGURAÇÃO; depois de trocar, lê de novo; se algum estado
// diferir, volta as fórmulas de antes. Diferente da primeira versão, a lista de fórmulas (antes e depois) fica na aba
// oculta R53_EXP_LISTAS desde a primeira rodada, então uma rodada que continua depois da troca não perde o original.
// voltarListas() devolve as fórmulas de antes a qualquer momento.

function r53ExpRegistrar_(texto) {
  var ss = SpreadsheetApp.getActive(), sh = ss.getSheetByName('R53_MEDIDA') || ss.insertSheet('R53_MEDIDA').hideSheet();
  sh.appendRow([new Date(), 'EXPERIMENTO', String(texto).slice(0, 49000)]);
  console.log(texto);
}

// --- listas sem INDIRECT ---
function r53ExpFecha_(s, i) {
  var d = 0, q = false;
  for (var j = i; j < s.length; j++) {
    var ch = s.charAt(j);
    if (q) { if (ch === '"') { if (s.charAt(j + 1) === '"') { j++; continue; } q = false; } }
    else if (ch === '"') q = true;
    else if (ch === '(') d++;
    else if (ch === ')') { d--; if (d === 0) return j; }
  }
  throw new Error('parêntese sem par');
}
function r53ExpArgs_(s, sep) {
  var out = [], d = 0, q = false, cur = '';
  for (var i = 0; i < s.length; i++) {
    var ch = s.charAt(i);
    if (q) { cur += ch; if (ch === '"') { if (s.charAt(i + 1) === '"') { cur += '"'; i++; continue; } q = false; } continue; }
    if (ch === '"') { q = true; cur += ch; }
    else if (ch === '(' || ch === '{') { d++; cur += ch; }
    else if (ch === ')' || ch === '}') { d--; cur += ch; }
    else if (ch === sep && d === 0) { out.push(cur); cur = ''; }
    else cur += ch;
  }
  out.push(cur);
  return out;
}
function r53ExpRef_(lit) {
  if (lit.charAt(0) !== '"' || lit.charAt(lit.length - 1) !== '"') throw new Error('faixa não literal: ' + lit);
  var r = lit.slice(1, -1).replace(/""/g, '"');
  if (!/^'[^']+'!\$[A-Z]+\$\d+:\$[A-Z]+\$\d+$/.test(r)) throw new Error('faixa inesperada: ' + r);
  return r;
}
function r53ExpSemIndirect_(f) {
  var sep = null;
  while (true) {
    var i = f.indexOf('INDIRECT(SWITCH(');
    if (i < 0) break;
    var a = i + 'INDIRECT('.length, b = r53ExpFecha_(f, a + 'SWITCH'.length), e = r53ExpFecha_(f, i + 'INDIRECT'.length);
    if (e !== b + 1) throw new Error('INDIRECT com mais que o SWITCH');
    var dentro = f.slice(a + 'SWITCH('.length, b);
    if (!sep) sep = r53ExpArgs_(dentro, ';').length > 1 ? ';' : ',';
    var xs = r53ExpArgs_(dentro, sep), x = xs[0], pares = xs.slice(1);
    if (pares.length % 2 !== 1) throw new Error('SWITCH sem padrão');
    var rot = [], refs = [];
    for (var k = 0; k + 1 < pares.length; k += 2) {
      if (!/^"[^"*?~]+"$/.test(pares[k])) throw new Error('rótulo inesperado: ' + pares[k]);
      rot.push(pares[k]); refs.push(r53ExpRef_(pares[k + 1]));
    }
    refs.push(r53ExpRef_(pares[pares.length - 1]));
    var corpo = 'CHOOSE(IFERROR(MATCH(' + x + sep + '{' + rot.join(';') + '}' + sep + '0)' + sep + (rot.length + 1) + ')' + sep + refs.join(sep) + ')';
    f = f.slice(0, i) + corpo + f.slice(e + 1);
  }
  if (f.indexOf('INDIRECT') >= 0) throw new Error('sobrou INDIRECT');
  return f;
}

var R53_EXP_LISTAS_ = 'R53_EXP_LISTAS', R53_EXP_CHAVE_ = 'r53_exp_listas2';

/** Lê (ou monta na primeira rodada) a lista guardada: [linha, coluna, fórmula antes, fórmula depois]. */
function r53ExpAlvos_(ss, dc) {
  var sh = ss.getSheetByName(R53_EXP_LISTAS_);
  if (sh && sh.getLastRow() > 1) {
    var v = sh.getRange(1, 1, sh.getLastRow(), 4).getValues();
    return { alvos: v.slice(1).map(function (l) { return [Number(l[0]), Number(l[1]), String(l[2]), String(l[3])]; }), meta: JSON.parse(v[0][0]) };
  }
  var formulas = dc.getRange(1, 1, dc.getMaxRows(), dc.getMaxColumns()).getFormulas(), alvos = [], rotulos = {}, seletores = {};
  formulas.forEach(function (l, i) { l.forEach(function (f, j) {
    if (f.indexOf('INDIRECT(') < 0) return;
    alvos.push([i + 1, j + 1, f, r53ExpSemIndirect_(f)]);
    (f.match(/"[^"]+"(?=[;,]"'?[^"]*'?!)/g) || []).forEach(function (r) { if (r.indexOf('!') < 0) rotulos[r.slice(1, -1)] = 1; });
    (f.match(/'CONFIGURAÇÃO'!\$[A-Z]+\$\d+/g) || []).forEach(function (s) { seletores[s.split('!')[1].replace(/\$/g, '')] = 1; });
  }); });
  formulas.forEach(function (l) { var m = /'CONFIGURAÇÃO'!\$([A-Z]+)\$(\d+)/.exec(l[1] || ''); if (m) seletores[m[1] + m[2]] = 1; });
  if (!alvos.length) throw new Error('Nenhum INDIRECT na DADOS_CUSTOM: já trocada? Rode voltarListas() antes.');
  var meta = { sel: Object.keys(seletores), estados: [''].concat(Object.keys(rotulos), ['Nada disso']) };
  sh = sh || ss.insertSheet(R53_EXP_LISTAS_);
  sh.hideSheet();
  // As fórmulas vão como texto (apóstrofo na frente), para a aba guardada não calcular nada.
  var texto = function (f) { return "'" + f; };
  sh.getRange(1, 1, alvos.length + 1, 4).setValues([["'" + JSON.stringify(meta), '', '', '']].concat(alvos.map(function (a) { return [a[0], a[1], texto(a[2]), texto(a[3])]; })));
  SpreadsheetApp.flush();
  return { alvos: alvos, meta: meta };
}

function experimentoListas() {
  var ss = SpreadsheetApp.getActive(), dc = ss.getSheetByName('DADOS_CUSTOM'), cfg = ss.getSheetByName('CONFIGURAÇÃO');
  var t00 = Date.now(), g = r53ExpAlvos_(ss, dc), alvos = g.alvos, sel = g.meta.sel, estados = g.meta.estados;
  var grade = dc.getRange(1, 1, dc.getMaxRows(), dc.getMaxColumns());
  var props = PropertiesService.getDocumentProperties();
  var p = JSON.parse(props.getProperty(R53_EXP_CHAVE_) || 'null') || { fase: 'antes', k: 0, antes: [], depois: [] };
  var faixas = sel.map(function (a1) { return cfg.getRange(a1); });
  var originais = faixas.map(function (r) { return r.getValue(); }), regras = faixas.map(function (r) { return r.getDataValidation(); });
  var resumo = function () { return Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, JSON.stringify(grade.getDisplayValues()))); };
  var gravar = function (k) { alvos.forEach(function (a) { dc.getRange(a[0], a[1]).setFormula(a[k]); }); };
  var relatorio = alvos.length + ' fórmulas, ' + sel.length + ' seletores, ' + estados.length + ' estados', fim = false;
  try {
    faixas.forEach(function (r) { r.clearDataValidations(); });
    while (Date.now() - t00 < 240000 && !fim) {
      if (p.k < estados.length) {
        cfg.getRangeList(sel).setValue(estados[p.k]);
        SpreadsheetApp.flush();
        p[p.fase].push(resumo());
        p.k++;
        props.setProperty(R53_EXP_CHAVE_, JSON.stringify(p));
      } else if (p.fase === 'antes') {
        gravar(3);
        SpreadsheetApp.flush();
        p.fase = 'depois'; p.k = 0;
        props.setProperty(R53_EXP_CHAVE_, JSON.stringify(p));
      } else fim = true;
    }
    if (fim) {
      var dif = estados.filter(function (s, k) { return p.antes[k] !== p.depois[k]; });
      if (dif.length) {
        gravar(2);
        relatorio = 'LISTAS: DIFERENTE, voltei as fórmulas de antes. ' + relatorio + '. Estados com diferença: ' + dif.map(function (s) { return s || '(vazio)'; }).join(', ');
      } else relatorio = 'LISTAS: iguais em todos os estados, ficaram sem INDIRECT. ' + relatorio;
      props.deleteProperty(R53_EXP_CHAVE_);
    } else relatorio = 'LISTAS: parcial, fase ' + p.fase + ' em ' + p.k + ' de ' + estados.length + ' estados. Rode experimentoListas de novo. ' + relatorio;
  } finally {
    faixas.forEach(function (r, k) { r.setValue(originais[k]); if (regras[k]) r.setDataValidation(regras[k]); });
    SpreadsheetApp.flush();
  }
  r53ExpRegistrar_(relatorio + ' (' + Math.round((Date.now() - t00) / 1000) + ' s)');
}

/** Devolve as fórmulas de antes (com INDIRECT) e zera o progresso. */
function voltarListas() {
  var ss = SpreadsheetApp.getActive(), sh = ss.getSheetByName(R53_EXP_LISTAS_);
  if (!sh) throw new Error('Nada guardado');
  var g = r53ExpAlvos_(ss, ss.getSheetByName('DADOS_CUSTOM'));
  g.alvos.forEach(function (a) { ss.getSheetByName('DADOS_CUSTOM').getRange(a[0], a[1]).setFormula(a[2]); });
  PropertiesService.getDocumentProperties().deleteProperty(R53_EXP_CHAVE_);
  r53ExpRegistrar_('LISTAS: voltaram as fórmulas de antes (' + g.alvos.length + ')');
}
