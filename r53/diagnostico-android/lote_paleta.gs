/**
 * Troca de paleta num lote só pelo SpreadsheetApp (teste em cópia descartável, 24/10/2026).
 *
 * Bordas e imagens ficam fixas (decisão do Mizuki, 24/10/2026); só fundo e letra mudam. Na primeira medição, cada
 * leitura custou ~5 s mesmo na CARTEIRA (52×47), então a troca não lê a grade: mapearLote(), rodada uma vez pelo
 * editor, guarda na aba oculta R53_LOTE quais faixas têm cada papel. A troca lê só esse mapa, enfileira as gravações
 * por papel e faz um flush no fim. A aba vai junto numa cópia, e o acionador simples também.
 */
var R53_LOTE_ABAS_ = ['CARTEIRA', 'FICHA', 'FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'FICHA PESSOAL', 'GLOSSÁRIO'];
var R53_LOTE_PAPEIS_ = ['fundo', 'tinta', 'painel', 'painel_alto', 'papel', 'menu_grande', 'texto', 'texto_fraco',
                        'acento', 'painel_baixo', 'bloco', 'linha', 'regua'];
var R53_LOTE_MAPA_ = 'R53_LOTE';
var R53_LOTE_LINHAS_ = 40, R53_LOTE_PEDACO_ = 45000, R53_LOTE_LISTA_ = 400;
var R53_LOTE_BORDA_ = {red: 0x85 / 255, green: 0x7F / 255, blue: 0x99 / 255}; // #857F99, escolhida pelo Mizuki
var R53_LOTE_PALETAS_ = /*PALETAS*/null;
// Arte da ficha (PNG de paleta de uma cor só, do construir()) e onde cada uma mora: {aba: [[linha, coluna, nome]]}.
var R53_LOTE_ARTE_ = /*ARTE*/null, R53_LOTE_IMGS_ = /*IMGS*/null;

function r53LoteCores_(nome) {
  var p = String(nome || '').trim().split(' · ');
  var t = R53_LOTE_PALETAS_[p[0]];
  return t && (p[1] === 'Claro' || p[1] === 'Escuro') ? t[p[1] === 'Claro' ? 'claro' : 'escuro'] : null;
}

function r53LoteA1_(r, c) {
  var s = '';
  for (var n = c + 1; n > 0; n = Math.floor((n - 1) / 26)) s = String.fromCharCode(65 + (n - 1) % 26) + s;
  return s + (r + 1);
}

/** Agrupa uma grade de chaves (null = cor fixa) em retângulos A1 por chave: faixas por linha, emendadas para baixo. */
function r53LoteFaixas_(chaves) {
  var saida = {}, abertas = {};
  var fechar = function (k) {
    var a = abertas[k], ini = r53LoteA1_(a.r0, a.c0), fim = r53LoteA1_(a.r1, a.c1);
    (saida[a.chave] = saida[a.chave] || []).push(ini === fim ? ini : ini + ':' + fim);
    delete abertas[k];
  };
  for (var r = 0; r <= chaves.length; r++) {
    var linha = chaves[r] || [], vistas = {};
    for (var c = 0; c < linha.length; c++) {
      if (linha[c] == null) continue;
      var c0 = c;
      while (c + 1 < linha.length && linha[c + 1] === linha[c0]) c++;
      var k = c0 + ',' + c + ',' + linha[c0];
      vistas[k] = true;
      if (abertas[k] && abertas[k].r1 === r - 1) abertas[k].r1 = r;
      else { if (abertas[k]) fechar(k); abertas[k] = {chave: linha[c0], r0: r, r1: r, c0: c0, c1: c}; }
    }
    Object.keys(abertas).forEach(function (k) { if (!vistas[k]) fechar(k); });
  }
  return saida;
}

/** Descobre a paleta pintada pelas cores de fundo que mais batem com os papéis. */
function r53LotePaletaPintada_(grades) {
  var conta = {};
  grades.forEach(function (g) { g.forEach(function (l) { l.forEach(function (x) { x = String(x).toLowerCase(); conta[x] = (conta[x] || 0) + 1; }); }); });
  var melhor = null, nota = -1;
  Object.keys(R53_LOTE_PALETAS_).forEach(function (nome) {
    ['claro', 'escuro'].forEach(function (modo) {
      var t = R53_LOTE_PALETAS_[nome][modo], n = 0, usadas = {};
      R53_LOTE_PAPEIS_.forEach(function (p) { var h = '#' + t[p].toLowerCase(); if (!usadas[h]) { usadas[h] = 1; n += conta[h] || 0; } });
      if (n > nota) { nota = n; melhor = {nome: nome, modo: modo, cores: t}; }
    });
  });
  return melhor;
}

/** Chaves de papel de cada célula, dada a paleta pintada hoje. */
function r53LoteChaves_(antes, fundos, letras) {
  var h = function (x) { return '#' + String(x).toLowerCase(); };
  var papelDaCor = {};
  R53_LOTE_PAPEIS_.forEach(function (p) { if (!(h(antes[p]) in papelDaCor)) papelDaCor[h(antes[p])] = p; });
  var mesmo = function (mapa, papel, cor) { return mapa && mapa[papel] && h(mapa[papel]) === cor; };
  var b = [], f = [];
  for (var r = 0; r < fundos.length; r++) {
    b.push([]); f.push([]);
    for (var c = 0; c < fundos[r].length; c++) {
      var fb = String(fundos[r][c]).toLowerCase(), fl = String(letras[r][c]).toLowerCase(), papel = papelDaCor[fb];
      b[r].push(papel || null);
      f[r].push(fl === h(antes.texto) ? 'texto'
        : papel && mesmo(antes.osso_por_papel, papel, fl) ? 'osso.' + papel
        : papel && mesmo(antes.aviso_por_papel, papel, fl) ? 'aviso.' + papel
        : papelDaCor[fl] || null);
    }
  }
  return {b: b, f: f};
}

/**
 * Bordas da aba por lado e estilo, em faixas que setBorder pinta só por fora: topo e base em trechos de uma linha,
 * esquerda e direita em trechos de uma coluna (numa faixa mais alta, setBorder(top) pintaria só a primeira linha).
 * Lê pela API do Sheets, porque o SpreadsheetApp não lê borda. Chave: "lado|ESTILO".
 */
function r53LoteMapaBordas_(ss, sh) {
  var nl = sh.getMaxRows(), nc = sh.getMaxColumns(), BLOCO = 120, lados = ['top', 'bottom', 'left', 'right'], grade = {};
  lados.forEach(function (l) { grade[l] = []; });
  for (var r0 = 0; r0 < nl; r0 += BLOCO) {
    var r1 = Math.min(nl, r0 + BLOCO), a1 = "'" + sh.getName() + "'!" + sh.getRange(r0 + 1, 1, r1 - r0, nc).getA1Notation();
    var resp = Sheets.Spreadsheets.get(ss.getId(), {ranges: [a1], fields: 'sheets.data.rowData.values.userEnteredFormat.borders'});
    var linhas = ((((resp.sheets || [])[0] || {}).data || [])[0] || {}).rowData || [];
    for (var i = 0; i < r1 - r0; i++) {
      var vals = (linhas[i] && linhas[i].values) || [];
      lados.forEach(function (l) { grade[l].push([]); });
      for (var c = 0; c < nc; c++) {
        var b = vals[c] && vals[c].userEnteredFormat && vals[c].userEnteredFormat.borders;
        lados.forEach(function (l) {
          var x = b && b[l];
          grade[l][r0 + i].push(x && x.style && x.style !== 'NONE' ? l + '|' + x.style : null);
        });
      }
    }
  }
  var saida = {};
  lados.forEach(function (l) {
    var vertical = l === 'left' || l === 'right', g = grade[l];
    var nA = vertical ? nc : nl, nB = vertical ? nl : nc;
    for (var a = 0; a < nA; a++) {
      for (var b = 0; b < nB; b++) {
        var v = vertical ? g[b][a] : g[a][b];
        if (!v) continue;
        var b0 = b;
        while (b + 1 < nB && (vertical ? g[b + 1][a] : g[a][b + 1]) === v) b++;
        var ini = vertical ? r53LoteA1_(b0, a) : r53LoteA1_(a, b0), fim = vertical ? r53LoteA1_(b, a) : r53LoteA1_(a, b);
        (saida[v] = saida[v] || []).push(ini === fim ? ini : ini + ':' + fim);
      }
    }
  });
  return saida;
}

/** Rodar uma vez pelo editor (na base, antes de copiar): grava o mapa de papéis e de bordas na aba oculta R53_LOTE. */
function mapearLote() {
  var ss = SpreadsheetApp.getActive(), lidas = [];
  R53_LOTE_ABAS_.forEach(function (nome) {
    var sh = ss.getSheetByName(nome);
    if (!sh) return;
    var faixa = sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns());
    lidas.push({nome: nome, fundos: faixa.getBackgrounds(), letras: faixa.getFontColors()});
  });
  var antes = r53LotePaletaPintada_(lidas.map(function (a) { return a.fundos; }));
  var mapa = {paleta: antes.nome + ' · ' + (antes.modo === 'claro' ? 'Claro' : 'Escuro'), abas: {}}, faixas = 0;
  lidas.forEach(function (a) {
    var k = r53LoteChaves_(antes.cores, a.fundos, a.letras);
    mapa.abas[a.nome] = {b: r53LoteFaixas_(k.b), f: r53LoteFaixas_(k.f)};
    ['b', 'f'].forEach(function (t) { Object.keys(mapa.abas[a.nome][t]).forEach(function (p) { faixas += mapa.abas[a.nome][t][p].length; }); });
    mapa.abas[a.nome].r = r53LoteMapaBordas_(ss, ss.getSheetByName(a.nome));
    Object.keys(mapa.abas[a.nome].r).forEach(function (k) { faixas += mapa.abas[a.nome].r[k].length; });
  });
  var json = JSON.stringify(mapa), linhas = [];
  for (var i = 0; i < json.length; i += R53_LOTE_PEDACO_) linhas.push([json.slice(i, i + R53_LOTE_PEDACO_)]);
  if (linhas.length > R53_LOTE_LINHAS_) throw new Error('Mapa grande demais: ' + json.length + ' caracteres');
  while (linhas.length < R53_LOTE_LINHAS_) linhas.push(['']);
  var sh = ss.getSheetByName(R53_LOTE_MAPA_) || ss.insertSheet(R53_LOTE_MAPA_);
  sh.getRange(1, 1, R53_LOTE_LINHAS_, 1).setNumberFormat('@').setValues(linhas);
  sh.hideSheet();
  console.log('MAPA paleta pintada: ' + mapa.paleta + ' · faixas: ' + faixas + ' · caracteres: ' + json.length);
}

function r53LoteTrocar_(e) {
  var t0 = Date.now(), ss = SpreadsheetApp.getActive();
  var marca = function (o) { console.log('LOTE ' + o + ' ' + (Date.now() - t0) + ' ms'); };
  marca('início');
  var nomeNovo = e && e.value !== undefined ? e.value : e.range.getDisplayValue();
  var agora = r53LoteCores_(nomeNovo);
  if (!agora) { marca('paleta não reconhecida: ' + nomeNovo); return; }
  var abaMapa = ss.getSheetByName(R53_LOTE_MAPA_);
  if (!abaMapa) { marca('sem mapa: rode mapearLote() pelo editor'); return; }
  var mapa = JSON.parse(abaMapa.getRange(1, 1, R53_LOTE_LINHAS_, 1).getValues().map(function (l) { return l[0]; }).join(''));
  marca('mapa lido');
  var cor = function (chave) {
    var p = chave.split('.');
    return '#' + (p.length === 2 ? (agora[p[0] + '_por_papel'] || {})[p[1]] || agora.texto : agora[chave]);
  };
  var listas = 0;
  Object.keys(mapa.abas).forEach(function (nome) {
    var sh = ss.getSheetByName(nome), aba = mapa.abas[nome];
    if (!sh) return;
    [['b', 'setBackground'], ['f', 'setFontColor']].forEach(function (par) {
      Object.keys(aba[par[0]]).forEach(function (chave) {
        var faixas = aba[par[0]][chave];
        for (var i = 0; i < faixas.length; i += R53_LOTE_LISTA_) {
          sh.getRangeList(faixas.slice(i, i + R53_LOTE_LISTA_))[par[1]](cor(chave));
          listas++;
        }
      });
    });
    var regua = '#' + agora.regua, LADO = {top: 0, left: 1, bottom: 2, right: 3};
    Object.keys(aba.r || {}).forEach(function (chave) {
      var p = chave.split('|'), lados = [null, null, null, null, null, null], faixas = aba.r[chave];
      lados[LADO[p[0]]] = true;
      for (var i = 0; i < faixas.length; i += R53_LOTE_LISTA_) {
        var rl = sh.getRangeList(faixas.slice(i, i + R53_LOTE_LISTA_));
        rl.setBorder(lados[0], lados[1], lados[2], lados[3], null, null, regua, SpreadsheetApp.BorderStyle[p[1]]);
        listas++;
      }
    });
    // O canto chanfrado da moldura emenda na borda: segue a régua junto com ela.
    (R53_LOTE_IMGS_[nome] || []).forEach(function (im) {
      if (!/^carteira-canto/.test(im[2])) return;
      sh.getRange(im[0], im[1]).setValue(SpreadsheetApp.newCellImage()
        .setSourceUrl('data:image/png;base64,' + r53LotePng_(R53_LOTE_ARTE_[im[2]], regua.toUpperCase()))
        .setAltTextTitle('PM-ARTE:' + im[2]).setAltTextDescription(regua.toUpperCase()).build());
    });
    marca('enfileirada ' + nome);
  });
  ss.getSheetByName('DADOS').getRange('CZ51').setValue('#' + agora.barra);
  marca('gravações enfileiradas (' + listas + ' listas)');
  SpreadsheetApp.flush();
  marca('flush (fim)');
}

/**
 * Rodar uma vez pelo editor (na base, antes de copiar): pinta toda borda das abas visíveis com o #857F99, mantendo
 * lado, espessura e estilo. Lê pela API do Sheets em blocos de 120 linhas e grava num batchUpdate só, porque cada
 * gravação paga o recálculo da ficha inteira.
 */
function fixarBordasLote() {
  var ss = SpreadsheetApp.getActive(), id = ss.getId(), pedidos = [], lados = 0, BLOCO = 120;
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
            nb[lado] = {style: x.style, colorStyle: {rgbColor: R53_LOTE_BORDA_}};
            mudou++;
          });
          row.push({userEnteredFormat: {borders: nb}});
        }
        rows.push({values: row});
      }
      if (!mudou) continue;
      pedidos.push({updateCells: {range: {sheetId: sh.getSheetId(), startRowIndex: r0, endRowIndex: r1,
        startColumnIndex: 0, endColumnIndex: nc}, rows: rows, fields: 'userEnteredFormat.borders'}});
      lados += mudou;
    }
    console.log('BORDAS lida ' + nome + ' · lados até aqui: ' + lados);
  });
  if (pedidos.length) Sheets.Spreadsheets.batchUpdate({requests: pedidos}, id);
  console.log('BORDAS fim · ' + lados + ' lados pintados com #857F99 em ' + pedidos.length + ' blocos');
}

var R53_LOTE_CRC_ = null;
function r53LoteCrc_(bytes, ini, fim) {
  if (!R53_LOTE_CRC_) {
    R53_LOTE_CRC_ = [];
    for (var n = 0; n < 256; n++) {
      var c = n;
      for (var k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      R53_LOTE_CRC_.push(c >>> 0);
    }
  }
  var crc = 0xFFFFFFFF;
  for (var i = ini; i < fim; i++) crc = R53_LOTE_CRC_[(crc ^ bytes[i]) & 255] ^ (crc >>> 8);
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

/** Mesma conta do pngComCor_ (Codigo.gs): reescreve o bloco PLTE com uma cor só e refaz o CRC. Devolve base64. */
function r53LotePng_(b64, hex) {
  var bytes = Utilities.base64Decode(b64), sb = function (v) { return v > 127 ? v - 256 : v; };
  var rgb = [parseInt(hex.substr(1, 2), 16), parseInt(hex.substr(3, 2), 16), parseInt(hex.substr(5, 2), 16)];
  for (var pos = 8; pos + 12 <= bytes.length;) {
    var len = ((bytes[pos] & 255) * 16777216) + ((bytes[pos + 1] & 255) << 16) + ((bytes[pos + 2] & 255) << 8) + (bytes[pos + 3] & 255);
    if (String.fromCharCode(bytes[pos + 4] & 255, bytes[pos + 5] & 255, bytes[pos + 6] & 255, bytes[pos + 7] & 255) === 'PLTE') {
      for (var i = 0; i < len; i++) bytes[pos + 8 + i] = sb(rgb[i % 3]);
      var crc = r53LoteCrc_(bytes, pos + 4, pos + 8 + len);
      for (var j = 0; j < 4; j++) bytes[pos + 8 + len + j] = sb((crc >>> (24 - 8 * j)) & 255);
      return Utilities.base64Encode(bytes);
    }
    pos += 12 + len;
  }
  throw new Error('PNG sem bloco de paleta');
}

/**
 * Rodar uma vez pelo editor (na base, antes de copiar): pinta a arte da ficha (pinceladas, moldura, gotinhas, selo)
 * com o mesmo #857F99 da borda, e a troca de paleta deixa de mexer nela. Só a imagem com o título de alt PM-ARTE: é
 * tocada; a foto do jogador fica como está.
 */
function fixarArteLote() {
  var ss = SpreadsheetApp.getActive(), cor = '#857F99', feitas = 0;
  Object.keys(R53_LOTE_IMGS_).forEach(function (nome) {
    var sh = ss.getSheetByName(nome);
    if (!sh) return;
    R53_LOTE_IMGS_[nome].forEach(function (im) {
      var cel = sh.getRange(im[0], im[1]), v = cel.getValue();
      if (!v || v.valueType !== SpreadsheetApp.ValueType.IMAGE || String(v.getAltTextTitle()) !== 'PM-ARTE:' + im[2]) {
        console.log('ARTE pulada ' + nome + ' ' + cel.getA1Notation() + ' (' + im[2] + ')');
        return;
      }
      cel.setValue(SpreadsheetApp.newCellImage().setSourceUrl('data:image/png;base64,' + r53LotePng_(R53_LOTE_ARTE_[im[2]], cor))
        .setAltTextTitle('PM-ARTE:' + im[2]).setAltTextDescription(cor).build());
      feitas++;
    });
  });
  console.log('ARTE fim · ' + feitas + ' imagens pintadas com ' + cor);
}
