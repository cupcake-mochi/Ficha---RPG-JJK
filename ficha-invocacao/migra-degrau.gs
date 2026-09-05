/**
 * Abre a coluna DEGRAU nas linhas de Traço e Comando da aba INVOCAÇÃO.
 *
 * O capítulo 16, na seção "Traço e Comando próprios", deixa o jogador
 * escrever entradas fora dos dois catálogos: ele escreve o efeito, acha na
 * régua o degrau em que ele cai, e leva pro mestre. A ficha só oferecia os
 * fixos do menu, então o próprio não tinha onde entrar.
 *
 * O que este script faz, e por que nesta ordem:
 *
 *   1. escreve as duas réguas como lista na DADOS_INV, em AP e AQ -- duas
 *      colunas que estão livres depois do índice de campos, para nada que já
 *      existe sair de lugar (as fórmulas da INVOCAÇÃO apontam para as letras
 *      de hoje)
 *   2. reparte a faixa de 20 colunas de cada linha em três: nome, DEGRAU e
 *      pontos. A largura total não muda, então o resto da aba não anda
 *   3. troca a fórmula do preço: nome do catálogo continua valendo o preço do
 *      catálogo, e nome escrito à mão cai no degrau
 *   4. deixa o menu do nome ACEITAR valor de fora da lista, senão não há como
 *      digitar o nome do seu
 *
 * Ele lê as células do índice que a própria ficha publica na DADOS_INV, então
 * não tem endereço escrito no código -- só a repartição da faixa, que é o que
 * ele está mudando.
 *
 * Rodar UMA vez: Extensões > Apps Script, cole, execute abrirDegrau.
 * Rodar de novo não faz mal: ele confere se a coluna já existe e para.
 */

// as duas réguas do capítulo 16. Se elas mudarem lá, mudam aqui -- e o
// conferir-invocacao.py acende, porque ele mede a lista da planilha contra a
// régua do capítulo.
var REGUA = {
  traco:   [2, 3, 5, 7, 8],
  comando: [0, 4, 8]
};

// a repartição da faixa: nome, degrau, pontos. Soma 20, que é a largura de
// hoje -- por isso nada em volta se move.
var LARG_NOME = 11, LARG_DEGRAU = 4, LARG_PONTOS = 5;

var PAINEL_ALTO = '#3D2E78', TEXTO_FRACO = '#998BA9';

function abrirDegrau() {
  var ss = SpreadsheetApp.getActive();
  var inv = ss.getSheetByName('INVOCAÇÃO');
  var dados = ss.getSheetByName('DADOS_INV');
  if (!inv || !dados) throw new Error('faltou INVOCAÇÃO ou DADOS_INV');

  var idx = indiceInv_(dados);
  var col = { traco: {}, comando: {} };

  // 1. as réguas viradas em lista, no fim da DADOS_INV
  ['traco', 'comando'].forEach(function (g, i) {
    var c = colunaLivre_(dados) + i;
    dados.getRange(1, c).setValue('degrau_' + g);
    var vals = [['—']].concat(REGUA[g].map(function (v) { return [v]; }));
    dados.getRange(2, c, vals.length, 1).setValues(vals);
    col[g].lista = dados.getRange(2, c, vals.length, 1);
  });

  var mexidas = 0;
  ['traco', 'comando'].forEach(function (g) {
    var linhas = linhasDoGrupo_(idx, g);
    if (!linhas.length) throw new Error('o índice não publica slot de ' + g);

    var c0 = linhas[0].colNome;          // onde a faixa começa
    var cDeg = c0 + LARG_NOME;
    var cPts = cDeg + LARG_DEGRAU;
    var fim = cPts + LARG_PONTOS - 1;

    if (inv.getRange(linhas[0].lin, cDeg).getDataValidation()) return;  // já feito

    // 2a. o cabeçalho do grupo, repartido em três
    var rh = linhas[0].lin - 1;
    inv.getRange(rh, c0, 1, fim - c0 + 1).breakApart();
    var titulo = inv.getRange(rh, c0).getValue();
    inv.getRange(rh, c0, 1, LARG_NOME).merge().setValue(titulo);
    inv.getRange(rh, cDeg, 1, LARG_DEGRAU).merge().setValue('DEGRAU')
       .setFontFamily('Oswald').setFontSize(8).setFontColor(TEXTO_FRACO)
       .setHorizontalAlignment('left').setBackground(PAINEL_ALTO);
    inv.getRange(rh, cPts, 1, LARG_PONTOS).merge().setValue('PONTOS')
       .setFontFamily('Oswald').setFontSize(8).setFontColor(TEXTO_FRACO)
       .setHorizontalAlignment('right').setBackground(PAINEL_ALTO);

    // 2b. cada linha de slot
    var menuNome = SpreadsheetApp.newDataValidation()
      .requireValueInRange(dados.getRange(faixaDaLista_(dados, g)), true)
      .setAllowInvalid(true)          // é isto que deixa digitar o seu
      .setHelpText('Escolha do catálogo, ou digite o nome do seu e preencha o DEGRAU.')
      .build();
    var menuDegrau = SpreadsheetApp.newDataValidation()
      .requireValueInRange(col[g].lista, true)
      .setAllowInvalid(false)         // o degrau sai da régua, e só dela
      .setHelpText('O degrau da régua em que o efeito cai. Só para entrada sua.')
      .build();

    linhas.forEach(function (s) {
      var fundo = inv.getRange(s.lin, cPts).getBackground();
      inv.getRange(s.lin, c0, 1, cPts - c0).breakApart();
      inv.getRange(s.lin, c0, 1, LARG_NOME).merge().setDataValidation(menuNome);
      inv.getRange(s.lin, cDeg, 1, LARG_DEGRAU).merge()
         .setValue('—').setDataValidation(menuDegrau)
         .setFontFamily('Oswald').setFontSize(10).setFontColor(TEXTO_FRACO)
         .setHorizontalAlignment('center').setBackground(fundo);

      // 3. o preço cai no degrau quando o nome não está no catálogo
      var f = inv.getRange(s.lin, cPts).getFormula();
      var alvo = colLetra_(cDeg) + s.lin;
      inv.getRange(s.lin, cPts).setFormula(
        f.replace(/,\s*0\s*\)\s*$/, ',N($' + alvo + '))')
         .replace(/;\s*0\s*\)\s*$/, ';N($' + alvo + '))'));
      mexidas++;
    });
  });

  SpreadsheetApp.getUi().alert(
    mexidas + ' linha(s) ganharam a coluna DEGRAU. Nome do catálogo continua ' +
    'valendo o preço do catálogo; nome digitado à mão cai no degrau.');
}

// --- apoio ---------------------------------------------------------------

/** o índice que a ficha publica na DADOS_INV: campo -> célula */
function indiceInv_(dados) {
  var c = 0;
  for (var i = 1; i <= dados.getLastColumn(); i++) {
    if (dados.getRange(2, i).getValue() === 'campo') { c = i; break; }
  }
  if (!c) throw new Error('a DADOS_INV não publica o índice de campos');
  var vals = dados.getRange(3, c, dados.getLastRow() - 2, 2).getValues();
  var m = {};
  vals.forEach(function (l) { if (l[0] && l[1]) m[String(l[0])] = String(l[1]); });
  return m;
}

/** as linhas de slot de um grupo, com a coluna em que o nome começa */
function linhasDoGrupo_(idx, grupo) {
  var saida = [];
  Object.keys(idx).forEach(function (k) {
    var m = k.match(new RegExp('^' + grupo + '_(\\d+)$'));
    if (!m) return;
    var cel = idx[k].replace(/\$/g, '');
    var p = cel.match(/^([A-Z]+)(\d+)$/);
    saida.push({ n: Number(m[1]), lin: Number(p[2]), colNome: colNum_(p[1]) });
  });
  return saida.sort(function (a, b) { return a.n - b.n; });
}

/** primeira coluna livre depois de tudo que já está escrito na aba */
function colunaLivre_(aba) {
  return aba.getLastColumn() + 2;
}

/** o intervalo A1 da lista de nomes daquele grupo, pelo título na linha 1 */
function faixaDaLista_(dados, grupo) {
  for (var i = 1; i <= dados.getLastColumn(); i++) {
    if (dados.getRange(1, i).getValue() === grupo) {
      var n = 0;
      while (dados.getRange(2 + n, i).getValue() !== '') n++;
      return colLetra_(i) + '2:' + colLetra_(i) + (1 + n);
    }
  }
  throw new Error('a DADOS_INV não tem a lista ' + grupo);
}

function colLetra_(n) {
  var s = '';
  while (n > 0) { var r = (n - 1) % 26; s = String.fromCharCode(65 + r) + s; n = (n - 1 - r) / 26; }
  return s;
}

function colNum_(s) {
  var n = 0;
  for (var i = 0; i < s.length; i++) n = n * 26 + (s.charCodeAt(i) - 64);
  return n;
}
