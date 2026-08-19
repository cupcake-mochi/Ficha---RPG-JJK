/**
 * Projeto M · a ficha nasce aqui dentro.
 *
 * Rode UMA função: construir(). Ela apaga o que existir e monta as seis abas
 * do zero, nativas: cor, fonte, mesclagem, altura de linha em pixel, menu
 * suspenso, caixa de seleção, imagem no tamanho certo e cor de estado.
 *
 * Por que não é mais um .xlsx importado: a conversão quebrava seis coisas
 * diferentes, e a pior delas era invisível — imagem vinda de importação não
 * aparece para a API, então nem dava para consertar o tamanho dela.
 */

var LOTE = 2000;   // células por escrita; acima disso o Apps Script engasga

function construir() {
  var t0 = new Date().getTime();
  var ss = SpreadsheetApp.getActive();
  var feito = [];

  // uma aba de rascunho segura o lugar enquanto as antigas somem
  var velha = ss.getSheetByName('__montando__');
  if (velha) ss.deleteSheet(velha);        // sobra de uma execução que parou no meio
  var temp = ss.insertSheet('__montando__');
  ss.getSheets().forEach(function (a) {
    if (a.getName() !== '__montando__') ss.deleteSheet(a);
  });

  ABAS.forEach(function (spec) {
    try {
      feito.push(montarAba_(ss, spec));
    } catch (err) {
      throw new Error('parou montando a aba ' + spec.nome + ': ' + err.message);
    }
  });
  ss.deleteSheet(temp);

  // Os menus suspensos SÓ agora: eles apontam para a aba DADOS, e ela é a
  // última a nascer. Aplicar durante a montagem dava 'Range not found'.
  feito.push('menus: ' + menusSuspensos_(ss));

  // a ordem em que elas aparecem é a ordem do ABAS
  ABAS.forEach(function (spec, i) {
    var a = ss.getSheetByName(spec.nome);
    ss.setActiveSheet(a);
    ss.moveActiveSheet(i + 1);
  });
  ss.setActiveSheet(ss.getSheetByName(ABAS[0].nome));

  var idx = indice();
  feito.push('cor de estado: ' + corDeEstado_(ss, idx));
  feito.push('notas: ' + notasDeRegra_(ss, idx));
  feito.push('protegidas: ' + protegerFormulas_(ss, idx));

  var seg = Math.round((new Date().getTime() - t0) / 1000);
  Logger.log('FICHA PRONTA em ' + seg + 's · ' + feito.join(' · '));
}

function montarAba_(ss, spec) {
  var aba = ss.insertSheet(spec.nome);
  var nc = spec.cols, nr = spec.rows;
  aba.setHiddenGridlines(true);
  if (aba.getMaxColumns() > nc) aba.deleteColumns(nc + 1, aba.getMaxColumns() - nc);
  if (aba.getMaxRows() > nr) aba.deleteRows(nr + 1, aba.getMaxRows() - nr);
  if (aba.getMaxColumns() < nc) aba.insertColumnsAfter(aba.getMaxColumns(), nc - aba.getMaxColumns());
  if (aba.getMaxRows() < nr) aba.insertRowsAfter(aba.getMaxRows(), nr - aba.getMaxRows());
  aba.setColumnWidths(1, nc, spec.larg);

  // matrizes locais: escrever célula a célula no Sheets é lento demais
  var v = mat_(nr, nc, ''), bg = mat_(nr, nc, '#120F1D');
  var ff = mat_(nr, nc, 'Roboto'), fs = mat_(nr, nc, 11);
  var fc = mat_(nr, nc, '#F4F1F7'), fw = mat_(nr, nc, 'normal');
  var ha = mat_(nr, nc, 'left'), va = mat_(nr, nc, 'middle'), rot = mat_(nr, nc, 0);

  // fundo em faixas: [linha, colIni, colFim, cor]
  spec.fundos.forEach(function (f) {
    for (var c = f[1]; c <= f[2]; c++) bg[f[0] - 1][c - 1] = f[3];
  });
  var formulas = [];
  spec.vals.forEach(function (t) {
    if (typeof t[2] === 'string' && t[2].charAt(0) === '=') {
      formulas.push([t[0], t[1], t[2]]);     // fórmula não entra em setValues
    } else {
      v[t[0] - 1][t[1] - 1] = t[2];
    }
    if (t.length > 3) {
      var e = spec.estilos[t[3]];
      ff[t[0] - 1][t[1] - 1] = e[0];
      fs[t[0] - 1][t[1] - 1] = e[1];
      if (e[2]) fc[t[0] - 1][t[1] - 1] = e[2];
      fw[t[0] - 1][t[1] - 1] = e[3] ? 'bold' : 'normal';
      ha[t[0] - 1][t[1] - 1] = e[4];
      va[t[0] - 1][t[1] - 1] = e[5] === 'center' ? 'middle' : e[5];
      rot[t[0] - 1][t[1] - 1] = e[6];
    }
  });

  var r = aba.getRange(1, 1, nr, nc);
  r.setBackgrounds(bg).setFontFamilies(ff).setFontSizes(fs)
   .setFontColors(fc).setFontWeights(fw)
   .setHorizontalAlignments(ha).setVerticalAlignments(va);
  r.setValues(v);

  // As fórmulas vêm DEPOIS, e uma a uma, com setFormula.
  //
  // O setValues trata o texto como se o usuário tivesse digitado, e aí a
  // pontuação segue o idioma da planilha: numa planilha em português,
  // COUNTIF(a,b) precisaria ser COUNTIF(a;b) e vira #ERROR!. O setFormula
  // sempre fala a notação americana, e o Google converte.
  formulas.forEach(function (f) {
    aba.getRange(f[0], f[1]).setFormula(f[2]);
  });

  // A rotação NÃO entra em lote: setTextRotations quer objetos TextRotation, e
  // não graus, então uma matriz de números é recusada. Como só a lombada é
  // girada -- duas células por aba --, uma chamada por célula sai barato.
  for (var i = 0; i < nr; i++) {
    for (var j = 0; j < nc; j++) {
      if (rot[i][j]) aba.getRange(i + 1, j + 1).setTextRotation(rot[i][j]);
    }
  }

  // altura em PIXEL, calculada pela maior letra da linha. Era isto que estava
  // cortando o 'd20 + 0' pela metade no caminho antigo.
  aba.setRowHeights(1, nr, 21);
  var linhas = Object.keys(spec.alturas).map(Number).sort(function (a, b) { return a - b; });
  var ini = null, ant = null, alt = null;
  linhas.concat([null]).forEach(function (l) {
    var h = l === null ? null : spec.alturas[String(l)];
    if (ini !== null && (l === null || l !== ant + 1 || h !== alt)) {
      aba.setRowHeights(ini, ant - ini + 1, alt);
      ini = null;
    }
    if (l !== null && ini === null) { ini = l; alt = h; }
    ant = l;
  });

  spec.merges.forEach(function (mg) {
    aba.getRange(mg[0], mg[1], mg[2] - mg[0] + 1, mg[3] - mg[1] + 1).merge();
  });

  // as réguas: a linha fina embaixo do valor, que substitui a caixa
  agrupar_(spec.bordas).forEach(function (g) {
    aba.getRange(g.lin, g.c1, 1, g.c2 - g.c1 + 1)
       .setBorder(true, null, null, null, null, null, g.cor,
                  SpreadsheetApp.BorderStyle.SOLID);
  });

  spec.imgs.forEach(function (im) {
    if (!ARTE[im[4]]) return;
    var blob = Utilities.newBlob(Utilities.base64Decode(ARTE[im[4]]), 'image/png', im[4]);
    var img = aba.insertImage(blob, im[1], im[0]);
    img.setWidth(im[2]).setHeight(im[3]);   // o tamanho é nosso, não do Sheets
  });

  // as caixas de seleção, nas posições que o gerador mediu
  (spec.caixas || []).forEach(function (cx) {
    aba.getRange(cx[1], cx[0], cx[2], 1).insertCheckboxes();
  });

  if (spec.oculta) aba.hideSheet();
  return spec.nome + ': ' + spec.vals.length + ' células, ' + formulas.length +
       ' fórmulas, ' + spec.imgs.length + ' imagens';
}

function mat_(nr, nc, valor) {
  var m = [];
  for (var i = 0; i < nr; i++) {
    var l = [];
    for (var j = 0; j < nc; j++) l.push(valor);
    m.push(l);
  }
  return m;
}

/** junta bordas vizinhas da mesma linha numa faixa só, para não fazer 600 chamadas */
function agrupar_(bordas) {
  var por = {};
  bordas.forEach(function (b) {
    var k = b[0] + '|' + b[2];
    (por[k] = por[k] || []).push(b[1]);
  });
  var saida = [];
  Object.keys(por).forEach(function (k) {
    var p = k.split('|'), cols = por[k].sort(function (a, b) { return a - b; });
    var ini = cols[0], ant = cols[0];
    for (var i = 1; i <= cols.length; i++) {
      if (i === cols.length || cols[i] !== ant + 1) {
        saida.push({ lin: Number(p[0]), c1: ini, c2: ant, cor: p[1] });
        if (i < cols.length) { ini = cols[i]; }
      }
      ant = cols[i];
    }
  });
  return saida;
}


/** Os menus suspensos, depois que todas as abas existem. */
function menusSuspensos_(ss) {
  var n = 0;
  ABAS.forEach(function (spec) {
    var aba = ss.getSheetByName(spec.nome);
    (spec.dv || []).forEach(function (d) {
      var fonte = ss.getRange(d[1].replace(/\$/g, ''));
      aba.getRange(d[0].replace(/\$/g, '')).setDataValidation(
        SpreadsheetApp.newDataValidation()
          .requireValueInRange(fonte, true).setAllowInvalid(true).build());
      n++;
    });
  });
  return n + ' menu(s)';
}

/**
 * Confere a ficha montada, sem mexer em nada. Rode esta se quiser saber se
 * ficou tudo de pé -- ela não altera a planilha.
 */
function verificar() {
  var ss = SpreadsheetApp.getActive();
  var falhas = [];
  ABAS.forEach(function (spec) {
    var aba = ss.getSheetByName(spec.nome);
    if (!aba) { falhas.push('falta a aba ' + spec.nome); return; }
    if (aba.getImages().length !== spec.imgs.length) {
      falhas.push(spec.nome + ': ' + aba.getImages().length + ' imagens, esperava ' + spec.imgs.length);
    }
  });
  var idx = indice();
  ['vida_max', 'defesa', 'maestria', 'cd de feitiço'].forEach(function (k) {
    if (!idx[k]) falhas.push('o índice não tem ' + k);
  });
  var fontes = {};
  ABAS.forEach(function (spec) {
    (spec.estilos || []).forEach(function (e) { fontes[e[0]] = true; });
  });
  Logger.log(falhas.length ? ('PROBLEMAS: ' + falhas.join(' · '))
                           : ('TUDO DE PÉ · fontes usadas: ' + Object.keys(fontes).join(', ')));
}
