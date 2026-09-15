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
var PENDENTES_ = [];   // as fórmulas de cada aba, gravadas depois que todas nascem

function construir() {
  var t0 = new Date().getTime();
  var ss = SpreadsheetApp.getActive();
  var feito = [];

  // O idioma da planilha manda na pontuação de TODA fórmula que o script escreve, o setFormula e
  // a regra de cor inclusive: numa planilha em português COUNTIF(a,b) vira #ERROR! e 0.25 não é
  // número. Foi o que o teste de 15/09/2026 mostrou, com as 104 fórmulas de vírgula quebradas.
  // A montagem roda em inglês, e o idioma de antes volta no fim, mesmo se ela parar no meio.
  var idioma = ss.getSpreadsheetLocale();
  ss.setSpreadsheetLocale('en_US');
  try {
    // uma aba de rascunho segura o lugar enquanto as antigas somem
    var velha = ss.getSheetByName('__montando__');
    if (velha) ss.deleteSheet(velha);        // sobra de uma execução que parou no meio
    var temp = ss.insertSheet('__montando__');
    ss.getSheets().forEach(function (a) {
      if (a.getName() !== '__montando__') ss.deleteSheet(a);
    });

    PENDENTES_ = [];
    ABAS.forEach(function (spec) {
      try {
        feito.push(montarAba_(ss, spec));
      } catch (err) {
        throw new Error('parou montando a aba ' + spec.nome + ': ' + err.message);
      }
    });
    ss.deleteSheet(temp);

    // As fórmulas SÓ agora, com as seis abas de pé: gravada antes de a aba citada nascer, a
    // fórmula fica em #REF!. É o mesmo motivo dos menus, logo abaixo.
    feito.push('fórmulas: ' + escreverFormulas_(ss));

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
  } finally {
    ss.setSpreadsheetLocale(idioma);
  }
  feito.push('idioma de volta: ' + idioma);

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
  // as colunas que fogem da largura base, em faixas: a DADOS_INV tem cinco larguras
  (spec.largs || []).forEach(function (g) {
    var c2 = Math.min(g[1], nc);
    if (g[0] <= c2) aba.setColumnWidths(g[0], c2 - g[0] + 1, g[2]);
  });

  // matrizes locais: escrever célula a célula no Sheets é lento demais
  var pad = spec.padrao || ['Roboto', 11, '#F4F1F7'];
  var v = mat_(nr, nc, ''), bg = mat_(nr, nc, '#120F1D');
  var ff = mat_(nr, nc, pad[0]), fs = mat_(nr, nc, pad[1]);
  var fc = mat_(nr, nc, pad[2]), fw = mat_(nr, nc, 'normal');
  var ha = mat_(nr, nc, 'left'), va = mat_(nr, nc, 'middle'), rot = mat_(nr, nc, 0);
  var fst = mat_(nr, nc, 'normal'), wr = mat_(nr, nc, false);

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
      if (e[7]) fst[t[0] - 1][t[1] - 1] = 'italic';
      if (e[8]) wr[t[0] - 1][t[1] - 1] = true;
    }
  });

  var r = aba.getRange(1, 1, nr, nc);
  r.setBackgrounds(bg).setFontFamilies(ff).setFontSizes(fs)
   .setFontColors(fc).setFontWeights(fw)
   .setHorizontalAlignments(ha).setVerticalAlignments(va)
   .setFontStyles(fst).setWraps(wr);
  r.setValues(v);

  // As fórmulas NÃO entram aqui: 47 delas citam uma aba que ainda não nasceu -- a CARTEIRA cita
  // a FICHA, a FICHA cita a DADOS, a INVOCAÇÃO cita a DADOS_INV --, e fórmula gravada antes de a
  // aba existir fica em #REF!. Elas esperam na fila, e o construir() grava todas com as abas de pé.
  // O setFormula lê a pontuação no idioma da planilha, e é por isso que a montagem é em inglês.
  PENDENTES_.push([spec.nome, formulas]);

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

  // As bordas, os quatro lados, com o traço e a cor da planilha viva: uma chamada por lado, traço e
  // cor, com as faixas numa RangeList. Até 15/09/2026 só a de cima entrava, e só em célula com valor.
  var TRACO = { thin: 'SOLID', medium: 'SOLID_MEDIUM', thick: 'SOLID_THICK', dashed: 'DASHED',
                mediumDashed: 'DASHED', dotted: 'DOTTED', hair: 'DOTTED', double: 'DOUBLE' };
  (spec.bordas || []).forEach(function (b) {
    var lado = b[0], traco = SpreadsheetApp.BorderStyle[TRACO[b[1]] || 'SOLID'];
    for (var i = 0; i < b[3].length; i += 400) {
      aba.getRangeList(b[3].slice(i, i + 400)).setBorder(
        lado === 'top' ? true : null, lado === 'left' ? true : null,
        lado === 'bottom' ? true : null, lado === 'right' ? true : null,
        null, null, b[2], traco);
    }
  });

  // As imagens DENTRO da célula, numa caixa mesclada: solta, ela arrasta com o mouse. Decisão do
  // Mizuki em 15/09/2026. A arte já vem no formato da caixa, porque o Sheets encaixa sem esticar.
  spec.imgs.forEach(function (im) {
    if (!ARTE[im[4]]) return;
    var caixa = aba.getRange(im[0], im[1], im[2] - im[0] + 1, im[3] - im[1] + 1);
    if (caixa.getNumRows() > 1 || caixa.getNumColumns() > 1) caixa.merge();
    caixa.getCell(1, 1).setValue(SpreadsheetApp.newCellImage()
      .setSourceUrl('data:image/png;base64,' + ARTE[im[4]]).build());
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

/** As fórmulas da fila, uma a uma, depois que todas as abas existem. */
function escreverFormulas_(ss) {
  var n = 0;
  PENDENTES_.forEach(function (p) {
    var aba = ss.getSheetByName(p[0]);
    p[1].forEach(function (f) {
      aba.getRange(f[0], f[1]).setFormula(f[2]);
      n++;
    });
  });
  return n;
}

/** Os menus suspensos, depois que todas as abas existem. */
function menusSuspensos_(ss) {
  var n = 0;
  ABAS.forEach(function (spec) {
    var aba = ss.getSheetByName(spec.nome);
    (spec.dv || []).forEach(function (d) {
      // O Sheets exporta menu de itens como lista escrita, "a,b,c", e ela nao e intervalo:
      // passar ela ao getRange parou a montagem em 'Range not found' (teste de 15/09/2026).
      var regra = SpreadsheetApp.newDataValidation().setAllowInvalid(true);
      var lista = /^"(.*)"$/.exec(d[1]);
      if (lista) {
        regra.requireValueInList(lista[1].split(','), true);
      } else {
        regra.requireValueInRange(ss.getRange(d[1].replace(/\$/g, '')), true);
      }
      aba.getRange(d[0].replace(/\$/g, '')).setDataValidation(regra.build());
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
    spec.imgs.forEach(function (im) {
      var cel = aba.getRange(im[0], im[1]), val = cel.getValue();
      if (!val || val.valueType !== SpreadsheetApp.ValueType.IMAGE) {
        falhas.push(spec.nome + ': falta a imagem ' + im[4] + ' em ' + cel.getA1Notation());
      }
    });
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
