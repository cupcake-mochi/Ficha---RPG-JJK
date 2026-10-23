/**
 * Paleta por tema da planilha (teste em cópia descartável, 23/10/2026).
 *
 * Os papéis com volume (texto, fundo, tinta, painel, painel_alto, papel, menu_grande e a régua das bordas) passam a
 * apontar para as vagas do tema da planilha. A troca de paleta reescreve só as vagas e repinta à mão o resto miúdo,
 * listado pela migração na aba oculta R53_TEMA. As imagens ficam como estão.
 *
 * ACCENT6 repete a régua: o app Android desenha a borda de tema com a vaga seguinte (teste no telefone, 23/10/2026;
 * fundo e letra vieram certos). A borda usa ACCENT5: o navegador lê ACCENT5 e o Android lê ACCENT6, as duas iguais.
 *
 * migrarParaTema() roda uma vez pelo editor, na cópia. Se o tempo apertar, ela para entre abas e pede outra rodada.
 */
var R53_TEMA_ABA_ = 'R53_TEMA';
var R53_TEMA_ABAS_ = ['CARTEIRA', 'FICHA', 'FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'FICHA PESSOAL', 'GLOSSÁRIO'];
var R53_TEMA_FUNDO_ = {fundo: 'BACKGROUND', tinta: 'ACCENT1', painel: 'ACCENT2', painel_alto: 'ACCENT3',
                       papel: 'ACCENT4', menu_grande: 'HYPERLINK'};
var R53_TEMA_BORDA_ = 'ACCENT5';
// Ordem de desempate quando duas funções têm o mesmo hex: as que vão pro tema primeiro.
var R53_TEMA_PAPEIS_ = ['fundo', 'tinta', 'painel', 'painel_alto', 'papel', 'menu_grande', 'texto', 'texto_fraco',
                        'acento', 'painel_baixo', 'bloco', 'linha', 'regua'];
var R53_TEMA_PROP_ = 'r53_tema_migradas';
var R53_TEMA_PALETAS_ = /*PALETAS*/null;

function r53TemaCores_(nome) {
  var p = String(nome || '').trim().split(' · ');
  var t = R53_TEMA_PALETAS_[p[0]];
  return t && (p[1] === 'Claro' || p[1] === 'Escuro') ? t[p[1] === 'Claro' ? 'claro' : 'escuro'] : null;
}

function r53TemaAtivo_(ss) {
  var aba = ss.getSheetByName(R53_TEMA_ABA_);
  return !!aba && aba.getRange('A1').getValue() === 'ativo';
}

function r53TemaVagas_(ss, t) {
  var tema = ss.getSpreadsheetTheme() || ss.resetSpreadsheetTheme();
  var T = SpreadsheetApp.ThemeColorType;
  var cor = function (hex) { return SpreadsheetApp.newColor().setRgbColor('#' + hex).build(); };
  tema.setConcreteColor(T.TEXT, cor(t.texto));
  Object.keys(R53_TEMA_FUNDO_).forEach(function (papel) {
    tema.setConcreteColor(T[R53_TEMA_FUNDO_[papel]], cor(t[papel]));
  });
  tema.setConcreteColor(T.ACCENT5, cor(t.regua));
  tema.setConcreteColor(T.ACCENT6, cor(t.regua));
  ss.setSpreadsheetTheme(tema);
}

/** Cor do resto miúdo: f:papel (fundo), t:papel (letra), o:fundo (osso sobre esse fundo), a:fundo (aviso). */
function r53TemaHexResto_(t, chave) {
  var tipo = chave.slice(0, 1), papel = chave.slice(2), hex;
  if (tipo === 'f' || tipo === 't') hex = t[papel];
  else if (tipo === 'o') hex = (t.osso_por_papel || {})[papel];
  else if (tipo === 'a') hex = (t.aviso_por_papel || {})[papel];
  return hex ? '#' + hex : null;
}

function migrarParaTema() {
  var ss = SpreadsheetApp.getActive(), props = PropertiesService.getDocumentProperties();
  var nome = ss.getSheetByName('CARTEIRA').getRange('C27').getDisplayValue();
  var t = r53TemaCores_(nome);
  if (!t) throw Error('Paleta atual não reconhecida em CARTEIRA!C27: ' + nome);
  if (props.getProperty('paleta_pendente')) throw Error('Há troca de paleta pendente; deixe terminar antes de migrar.');
  var aba = ss.getSheetByName(R53_TEMA_ABA_);
  if (!aba) {
    aba = ss.insertSheet(R53_TEMA_ABA_);
    aba.hideSheet();
    aba.getRange('A1:B1').setValues([['migrando', nome]]);
  } else if (aba.getRange('B1').getValue() !== nome) {
    throw Error('A migração começou com outra paleta; volte para ' + aba.getRange('B1').getValue());
  }
  // As vagas primeiro: cada célula convertida já aparece com a cor certa.
  r53TemaVagas_(ss, t);
  var feitas = JSON.parse(props.getProperty(R53_TEMA_PROP_) || '{}'), inicio = Date.now();
  R53_TEMA_ABAS_.forEach(function (nomeAba, i) {
    if (feitas[nomeAba] || Date.now() - inicio > 200000) return;
    var t1 = Date.now(), r = r53TemaMigrarAba_(ss, nomeAba, t);
    aba.getRange(i + 2, 1, 1, 1 + r.pedacos.length).setValues([[nomeAba].concat(r.pedacos)]);
    delete r.pedacos;
    r.ms = Date.now() - t1;
    feitas[nomeAba] = r;
    props.setProperty(R53_TEMA_PROP_, JSON.stringify(feitas));
    console.log('MIGRADA ' + nomeAba + ' ' + JSON.stringify(r));
  });
  var faltam = R53_TEMA_ABAS_.filter(function (n) { return !feitas[n]; });
  if (faltam.length) {
    console.log('RODE DE NOVO migrarParaTema: faltam ' + faltam.join(', '));
    return {faltam: faltam};
  }
  aba.getRange('A1').setValue('ativo');
  console.log('RESUMO tema ativo · ' + nome + ' · ' + JSON.stringify(feitas));
  return feitas;
}

function r53TemaMigrarAba_(ss, nomeAba, t) {
  var sh = ss.getSheetByName(nomeAba);
  if (!sh) return {ausente: true, pedacos: ['{}']};
  var nl = sh.getMaxRows(), nc = sh.getMaxColumns(), faixa = sh.getRange(1, 1, nl, nc);
  var fundos = faixa.getBackgrounds(), fontes = faixa.getFontColors();
  var porHex = {};
  R53_TEMA_PAPEIS_.forEach(function (p) {
    var h = '#' + String(t[p]).toLowerCase();
    if (!(h in porHex)) porHex[h] = p;
  });
  var porHexOsso = function (mapa, fundo, h) { return mapa && mapa[fundo] && ('#' + mapa[fundo].toLowerCase()) === h; };
  var texto = '#' + t.texto.toLowerCase();
  var deTema = {}, deRgb = {};
  var tema = function (tipo) {
    return deTema[tipo] || (deTema[tipo] = SpreadsheetApp.newColor().setThemeColor(SpreadsheetApp.ThemeColorType[tipo]).build());
  };
  var rgb = function (h) { return deRgb[h] || (deRgb[h] = SpreadsheetApp.newColor().setRgbColor(h).build()); };
  var resto = {}, n = {fundoTema: 0, letraTema: 0, resto: 0, bordas: 0};
  var anota = function (chave, r, c) { ((resto[chave] = resto[chave] || {})[r] = resto[chave][r] || []).push(c); n.resto++; };
  var objFundo = [], objLetra = [];
  for (var r = 0; r < nl; r++) {
    var lf = [], ll = [];
    for (var c = 0; c < nc; c++) {
      var hb = String(fundos[r][c]).toLowerCase(), pb = porHex[hb];
      if (pb && R53_TEMA_FUNDO_[pb]) { lf.push(tema(R53_TEMA_FUNDO_[pb])); n.fundoTema++; }
      else { lf.push(rgb(hb)); if (pb) anota('f:' + pb, r, c); }
      var hl = String(fontes[r][c]).toLowerCase();
      if (hl === texto) { ll.push(tema('TEXT')); n.letraTema++; continue; }
      ll.push(rgb(hl));
      if (pb && porHexOsso(t.osso_por_papel, pb, hl)) anota('o:' + pb, r, c);
      else if (pb && porHexOsso(t.aviso_por_papel, pb, hl)) anota('a:' + pb, r, c);
      else if (porHex[hl]) anota('t:' + porHex[hl], r, c);
    }
    objFundo.push(lf); objLetra.push(ll);
  }
  faixa.setBackgroundObjects(objFundo);
  faixa.setFontColorObjects(objLetra);
  SpreadsheetApp.flush();
  n.bordas = r53TemaBordas_(ss, sh, nl, nc, '#' + t.regua.toLowerCase());
  // Resto em faixas A1 por linha, em pedaços que cabem numa célula.
  var lista = {};
  Object.keys(resto).forEach(function (k) {
    lista[k] = [];
    Object.keys(resto[k]).forEach(function (r) {
      var cols = resto[k][r].sort(function (a, b) { return a - b; }), i = 0;
      while (i < cols.length) {
        var j = i;
        while (j + 1 < cols.length && cols[j + 1] === cols[j] + 1) j++;
        lista[k].push(sh.getRange(+r + 1, cols[i] + 1, 1, cols[j] - cols[i] + 1).getA1Notation());
        i = j + 1;
      }
    });
  });
  var json = JSON.stringify(lista), pedacos = [];
  for (var p = 0; p < json.length; p += 45000) pedacos.push(json.slice(p, p + 45000));
  n.pedacos = pedacos.length ? pedacos : ['{}'];
  return n;
}

function r53TemaHexDe_(x) {
  var c = (x.colorStyle && x.colorStyle.rgbColor) || x.color;
  if (!c || (x.colorStyle && x.colorStyle.themeColor)) return null;
  return '#' + ['red', 'green', 'blue'].map(function (k) {
    return ('0' + Math.round((c[k] || 0) * 255).toString(16)).slice(-2);
  }).join('');
}

function r53TemaBordas_(ss, sh, nl, nc, regua) {
  var id = ss.getId(), sid = sh.getSheetId(), trocadas = 0, LOTE = 120;
  for (var r0 = 0; r0 < nl; r0 += LOTE) {
    var r1 = Math.min(nl, r0 + LOTE);
    var a1 = "'" + sh.getName() + "'!" + sh.getRange(r0 + 1, 1, r1 - r0, nc).getA1Notation();
    var resp = Sheets.Spreadsheets.get(id, {ranges: [a1], fields: 'sheets.data.rowData.values.userEnteredFormat.borders'});
    var dados = ((resp.sheets || [])[0] || {}).data || [];
    var linhas = (dados[0] || {}).rowData || [];
    var rows = [], mudou = 0;
    for (var i = 0; i < r1 - r0; i++) {
      var vals = (linhas[i] && linhas[i].values) || [], row = [];
      for (var c = 0; c < nc; c++) {
        var b = vals[c] && vals[c].userEnteredFormat && vals[c].userEnteredFormat.borders, nb = {};
        ['top', 'bottom', 'left', 'right'].forEach(function (lado) {
          var x = b && b[lado];
          if (!x || !x.style || x.style === 'NONE') return;
          var y = {style: x.style};
          if (r53TemaHexDe_(x) === regua) { y.colorStyle = {themeColor: R53_TEMA_BORDA_}; mudou++; }
          else if (x.colorStyle) y.colorStyle = x.colorStyle;
          else if (x.color) y.colorStyle = {rgbColor: x.color};
          nb[lado] = y;
        });
        row.push({userEnteredFormat: {borders: nb}});
      }
      rows.push({values: row});
    }
    if (!mudou) continue;
    Sheets.Spreadsheets.batchUpdate({requests: [{updateCells: {
      range: {sheetId: sid, startRowIndex: r0, endRowIndex: r1, startColumnIndex: 0, endColumnIndex: nc},
      rows: rows, fields: 'userEnteredFormat.borders'}}]}, id);
    trocadas += mudou;
  }
  return trocadas;
}

/** Troca pelo tema, chamada no onEdit da CARTEIRA!C27 quando a migração terminou. */
function r53TemaTrocar_(e) {
  var t0 = Date.now(), ss = SpreadsheetApp.getActive();
  var nome = e && e.value !== undefined ? e.value : e.range.getDisplayValue();
  var t = r53TemaCores_(nome);
  if (!t) return;
  r53TemaVagas_(ss, t);
  var tVagas = Date.now() - t0;
  var aba = ss.getSheetByName(R53_TEMA_ABA_), chamadas = 0;
  var linhas = aba.getRange(2, 1, R53_TEMA_ABAS_.length, aba.getLastColumn()).getValues();
  linhas.forEach(function (linha) {
    var sh = linha[0] && ss.getSheetByName(linha[0]);
    if (!sh) return;
    var resto = JSON.parse(linha.slice(1).join('') || '{}'), porCor = {f: {}, l: {}};
    Object.keys(resto).forEach(function (k) {
      var hex = r53TemaHexResto_(t, k);
      if (!hex) return;
      var alvo = porCor[k.slice(0, 1) === 'f' ? 'f' : 'l'];
      alvo[hex] = (alvo[hex] || []).concat(resto[k]);
    });
    ['f', 'l'].forEach(function (tipo) {
      Object.keys(porCor[tipo]).forEach(function (hex) {
        var a1 = porCor[tipo][hex];
        for (var i = 0; i < a1.length; i += 400) {
          var rl = sh.getRangeList(a1.slice(i, i + 400));
          if (tipo === 'f') rl.setBackground(hex); else rl.setFontColor(hex);
          chamadas++;
        }
      });
    });
  });
  ss.getSheetByName('DADOS').getRange('CZ51').setValue('#' + t.barra);
  PropertiesService.getDocumentProperties().deleteProperty('paleta_pendente');
  SpreadsheetApp.flush();
  var medicao = JSON.stringify({em: Date.now(), paleta: nome, vagasMs: tVagas, totalMs: Date.now() - t0, chamadas: chamadas});
  var md = ss.createDeveloperMetadataFinder().withKey('r53_tema_medicao').find();
  if (md.length) md[0].setValue(medicao); else ss.addDeveloperMetadata('r53_tema_medicao', medicao);
}
