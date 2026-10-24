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
var R53_LOTE_PALETAS_ = /*PALETAS*/null;

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

/** Rodar uma vez pelo editor (na base, antes de copiar): grava o mapa de papéis na aba oculta R53_LOTE. */
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
    marca('enfileirada ' + nome);
  });
  ss.getSheetByName('DADOS').getRange('CZ51').setValue('#' + agora.barra);
  marca('gravações enfileiradas (' + listas + ' listas)');
  SpreadsheetApp.flush();
  marca('flush (fim)');
}
