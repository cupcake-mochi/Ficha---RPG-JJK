// SÓ NA CÓPIA DE TESTE (26/10/2026). Duas experiências, cada uma ligada por uma função rodada pelo editor:
//  experimentoBordas(): as bordas das seis abas passam a usar a vaga ACCENT5 do tema; a troca de paleta passa a
//    escrever a régua da paleta nas vagas ACCENT5 e ACCENT6 (o app Android desenha a borda de tema com a vaga
//    seguinte, teste de 23/10). Antes de pintar, guarda as bordas atuais na aba R53_EXP_BORDAS para voltar.
//  experimentoListas(): as 225 listas da DADOS_CUSTOM trocam INDIRECT(SWITCH(x; "rótulo"; "'aba'!faixa"; ...)) por
//    CHOOSE(MATCH(x; {rótulos}; 0); faixa; ...), que não é volátil. Antes de ficar, confere em todos os estados dos
//    seletores da CONFIGURAÇÃO que as listas mostram o mesmo; se algo diferir, volta as fórmulas de antes.
// O resultado de cada uma vai para a aba R53_MEDIDA.

var R53_EXP_PROP_BORDAS_ = 'r53_exp_bordas_tema';

function r53ExpRegistrar_(texto) {
  var sh = SpreadsheetApp.getActive().getSheetByName('R53_MEDIDA');
  if (sh) sh.appendRow([new Date(), 'EXPERIMENTO', '', '', String(texto).slice(0, 49000), '']);
  console.log(texto);
}

function r53ExpPintarTema_(hex) {
  var tema = SpreadsheetApp.getActive().getSpreadsheetTheme(), t0 = Date.now(), marcas = [];
  var cor = SpreadsheetApp.newColor().setRgbColor('#' + hex).build();
  tema.setConcreteColor(SpreadsheetApp.ThemeColorType.ACCENT5, cor); marcas.push('ACCENT5 ' + (Date.now() - t0));
  tema.setConcreteColor(SpreadsheetApp.ThemeColorType.ACCENT6, cor); marcas.push('ACCENT6 ' + (Date.now() - t0));
  return marcas;
}

// A troca de paleta de sempre e, com a experiência ligada, as duas vagas do tema no fim.
var r53LoteTrocarSemTema_ = r53LoteTrocar_;
r53LoteTrocar_ = function (e) {
  var r = r53LoteTrocarSemTema_(e);
  // 26/10: bordas pelo tema descartadas pelo Mizuki; a troca de paleta não mexe mais no tema.
  if (true || PropertiesService.getDocumentProperties().getProperty(R53_EXP_PROP_BORDAS_) !== 'sim') return r;
  var agora = r53LoteCores_(e && e.value !== undefined ? e.value : e.range.getDisplayValue());
  if (agora && agora.regua) {
    var t0 = Date.now();
    R53_EXP_MARCAS_.push('tema: ' + r53ExpPintarTema_(agora.regua).join(', '));
  }
  return r;
};

function experimentoBordas() {
  var ss = SpreadsheetApp.getActive(), id = ss.getId(), pedidos = [], lados = 0, BLOCO = 120, guarda = [];
  var agora = r53LoteCores_(ss.getSheetByName('CARTEIRA').getRange('C27').getDisplayValue());
  if (!agora || !agora.regua) throw new Error('Paleta da C27 não reconhecida');
  r53ExpPintarTema_(agora.regua);
  R53_LOTE_ABAS_.forEach(function (nome) {
    var sh = ss.getSheetByName(nome);
    if (!sh) return;
    var nl = sh.getMaxRows(), nc = sh.getMaxColumns();
    for (var r0 = 0; r0 < nl; r0 += BLOCO) {
      var r1 = Math.min(nl, r0 + BLOCO), a1 = "'" + nome + "'!" + sh.getRange(r0 + 1, 1, r1 - r0, nc).getA1Notation();
      var resp = Sheets.Spreadsheets.get(id, {ranges: [a1], fields: 'sheets.data.rowData.values.userEnteredFormat.borders'});
      var linhas = ((((resp.sheets || [])[0] || {}).data || [])[0] || {}).rowData || [], rows = [], mudou = 0;
      for (var i = 0; i < r1 - r0; i++) {
        var vals = (linhas[i] && linhas[i].values) || [], row = [];
        for (var c = 0; c < nc; c++) {
          var b = vals[c] && vals[c].userEnteredFormat && vals[c].userEnteredFormat.borders, nb = {};
          ['top', 'bottom', 'left', 'right'].forEach(function (lado) {
            var x = b && b[lado];
            if (!x || !x.style || x.style === 'NONE') return;
            nb[lado] = {style: x.style, colorStyle: {themeColor: 'ACCENT5'}};
            mudou++;
          });
          row.push({userEnteredFormat: {borders: nb}});
        }
        rows.push({values: row});
      }
      if (!mudou) continue;
      guarda.push(JSON.stringify({aba: nome, r0: r0, bordas: linhas}));
      pedidos.push({updateCells: {range: {sheetId: sh.getSheetId(), startRowIndex: r0, endRowIndex: r1,
        startColumnIndex: 0, endColumnIndex: nc}, rows: rows, fields: 'userEnteredFormat.borders'}});
      lados += mudou;
    }
  });
  // as bordas de antes, para voltar se a experiência não servir
  var aba = ss.getSheetByName('R53_EXP_BORDAS') || ss.insertSheet('R53_EXP_BORDAS');
  aba.hideSheet();
  var celulas = [];
  guarda.forEach(function (g) { for (var i = 0; i < g.length; i += 45000) celulas.push([g.slice(i, i + 45000)]); });
  aba.clear();
  if (celulas.length) aba.getRange(1, 1, celulas.length, 1).setValues(celulas);
  var t0 = Date.now();
  if (pedidos.length) Sheets.Spreadsheets.batchUpdate({requests: pedidos}, id);
  PropertiesService.getDocumentProperties().setProperty(R53_EXP_PROP_BORDAS_, 'sim');
  r53ExpRegistrar_('BORDAS no tema: ' + lados + ' lados em ' + pedidos.length + ' blocos, gravação ' + (Date.now() - t0) +
    ' ms; régua ' + agora.regua + '; cópia das bordas de antes em ' + celulas.length + ' células da R53_EXP_BORDAS');
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

function experimentoListas() {
  var ss = SpreadsheetApp.getActive(), dc = ss.getSheetByName('DADOS_CUSTOM'), cfg = ss.getSheetByName('CONFIGURAÇÃO');
  var t00 = Date.now(), nl = dc.getMaxRows(), nc = dc.getMaxColumns();
  var grade = dc.getRange(1, 1, nl, nc), formulas = grade.getFormulas();
  var alvos = [], rotulos = {}, seletores = {};
  formulas.forEach(function (l, i) { l.forEach(function (f, j) {
    if (f.indexOf('INDIRECT(') < 0) return;
    alvos.push([i, j, f, r53ExpSemIndirect_(f)]);
    (f.match(/"[^"]+"(?=[;,]"'?[^"]*'?!)/g) || []).forEach(function (r) { if (r.indexOf('!') < 0) rotulos[r.slice(1, -1)] = 1; });
    (f.match(/'CONFIGURAÇÃO'!\$[A-Z]+\$\d+/g) || []).forEach(function (s) { seletores[s.split('!')[1].replace(/\$/g, '')] = 1; });
  }); });
  // os seletores das linhas de baixo (coluna B da DADOS_CUSTOM) espelham a CONFIGURAÇÃO
  dc.getRange(1, 2, nl, 1).getFormulas().forEach(function (l) {
    var m = /'CONFIGURAÇÃO'!\$([A-Z]+)\$(\d+)/.exec(l[0]); if (m) seletores[m[1] + m[2]] = 1;
  });
  var sel = Object.keys(seletores), estados = [''].concat(Object.keys(rotulos), ['Nada disso']);
  // Cada seletor só aceita os próprios rótulos: a validação sai durante a leitura e volta igual no fim.
  // Os estados são muitos para uma execução só: o progresso fica numa propriedade e cada rodada continua de onde parou.
  var props = PropertiesService.getDocumentProperties(), CHAVE = 'r53_exp_listas';
  var p = JSON.parse(props.getProperty(CHAVE) || 'null') || { fase: 'antes', k: 0, antes: [], depois: [] };
  var faixas = sel.map(function (a1) { return cfg.getRange(a1); });
  var originais = faixas.map(function (r) { return r.getValue(); }), regras = faixas.map(function (r) { return r.getDataValidation(); });
  var resumo = function () { return Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, JSON.stringify(grade.getDisplayValues()))); };
  var relatorio = alvos.length + ' fórmulas, ' + sel.length + ' seletores, ' + estados.length + ' estados', fim = false;
  try {
    faixas.forEach(function (r) { r.clearDataValidations(); });
    while (Date.now() - t00 < 240000 && !fim) {
      if (p.k < estados.length) {
        cfg.getRangeList(sel).setValue(estados[p.k]);
        SpreadsheetApp.flush();
        p[p.fase].push(resumo());
        p.k++;
        props.setProperty(CHAVE, JSON.stringify(p));
      } else if (p.fase === 'antes') {
        alvos.forEach(function (a) { dc.getRange(a[0] + 1, a[1] + 1).setFormula(a[3]); });
        p.fase = 'depois'; p.k = 0;
        props.setProperty(CHAVE, JSON.stringify(p));
      } else {
        fim = true;
      }
    }
    if (fim) {
      var dif = estados.filter(function (s, k) { return p.antes[k] !== p.depois[k]; });
      if (dif.length) {
        alvos.forEach(function (a) { dc.getRange(a[0] + 1, a[1] + 1).setFormula(a[2]); });
        relatorio = 'LISTAS: DIFERENTE, voltei as fórmulas de antes. ' + relatorio + '. Estados com diferença: ' + dif.map(function (s) { return s || '(vazio)'; }).join(', ');
      } else {
        relatorio = 'LISTAS: iguais em todos os estados, ficaram sem INDIRECT. ' + relatorio;
      }
      props.deleteProperty(CHAVE);
    } else {
      props.setProperty(CHAVE, JSON.stringify(p));
      relatorio = 'LISTAS: parcial, fase ' + p.fase + ' em ' + p.k + ' de ' + estados.length + ' estados. Rode experimentoListas de novo. ' + relatorio;
    }
  } finally {
    faixas.forEach(function (r, k) { r.setValue(originais[k]); if (regras[k]) r.setDataValidation(regras[k]); });
    SpreadsheetApp.flush();
  }
  r53ExpRegistrar_(relatorio + ' (' + Math.round((Date.now() - t00) / 1000) + ' s)');
}
