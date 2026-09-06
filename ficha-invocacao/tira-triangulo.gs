/**
 * Tira o triângulo de aviso do nome do Traço e do Comando, e conserta a barra
 * de vida quando o campo "vida agora" está vazio.
 *
 * TRÊS COISAS, e o motivo de cada uma:
 *
 * 1. O menu do nome sai. A validação do Sheets tem três estados e nenhum
 *    serve: "rejeitar" bloqueia o nome próprio, "avisar" deixa passar mas
 *    marca com o triângulo, e não existe menu que aceite texto de fora em
 *    silêncio. Pior: o triângulo acende no acerto (`Lança negra` com degrau)
 *    e no erro (`Escallada`, digitado torto, custando zero) do mesmo jeito --
 *    então ele não distingue os dois e não serve de aviso. A aba CATÁLOGO já
 *    lista as 20 entradas com o que cada uma faz, que é de onde se escolhe de
 *    verdade.
 *
 * 2. Entra um aviso que serve. Ele acende SÓ no caso perigoso: nome escrito
 *    que não está no catálogo E sem degrau escolhido -- que é o que está
 *    custando zero sem ninguém ver.
 *
 * 3. A vida agora passa a nascer cheia, como fórmula, do mesmo jeito que a
 *    ficha de player faz com a vida, a energia e a integridade. Enquanto ela
 *    estava vazia a barra desenhava cheia e mentia. O jogador digita por cima
 *    quando toma dano, e a barra ganha uma guarda: campo vazio, barra vazia.
 *
 * Rodar UMA vez: Extensões > Apps Script, arquivo novo, cole, execute
 * tiraTriangulo. Ele não desfaz nada do migra-degrau.
 */

var AMBAR = '#D89B3A', PAINEL = '#1E1733';

function tiraTriangulo() {
  var ss = SpreadsheetApp.getActive();
  var inv = ss.getSheetByName('INVOCAÇÃO');
  var dados = ss.getSheetByName('DADOS_INV');
  if (!inv || !dados) throw new Error('faltou INVOCAÇÃO ou DADOS_INV');
  var idx = indice_(dados);

  // ---------- 1 e 2 · o nome perde o menu, e entra o aviso ----------------
  var faixas = [];
  ['traco', 'comando'].forEach(function (g) {
    var linhas = slots_(idx, g);
    if (!linhas.length) throw new Error('o índice não publica slot de ' + g);
    var col = linhas[0].col;
    var r1 = linhas[0].lin, r2 = linhas[linhas.length - 1].lin;
    inv.getRange(r1, col, r2 - r1 + 1, 1).setDataValidation(null);
    faixas.push({ grupo: g, col: col, r1: r1, r2: r2,
                  degrau: col + 11, tab: tabela_(dados, g) });
  });

  // o aviso vai na linha da nota, embaixo dos dois blocos
  var lAviso = Math.max(faixas[0].r2, faixas[1].r2) + 1;
  var partes = faixas.map(function (f) {
    var nome = letra_(f.col) + f.r1 + ':' + letra_(f.col) + f.r2;
    var deg = letra_(f.degrau) + f.r1 + ':' + letra_(f.degrau) + f.r2;
    // Conta as linhas em que HÁ nome, o nome NÃO está no catálogo, e o
    // degrau não foi escolhido.
    //
    // COUNTIF e nao MATCH: dentro de SUMPRODUCT o MATCH nao distribui sobre a
    // faixa de forma confiavel no Sheets, e o COUNTIF distribui.
    //
    // E o degrau se testa por "—" ou vazio, e nao por N()=0: o degrau `0` e'
    // valido no Comando (o `Investir` custa zero), e testar por zero acusaria
    // um Comando proprio no degrau 0 como se ele estivesse sem degrau.
    return 'SUMPRODUCT((' + nome + '<>"")*(' + nome + '<>"—")*' +
           '(COUNTIF(' + f.tab + ',' + nome + ')=0)*' +
           '((' + deg + '="—")+(' + deg + '="")))';
  });
  var f = '=IF(' + partes[0] + '+' + partes[1] + '=0,"",' +
          '"⚠ "&(' + partes[0] + '+' + partes[1] + ')&' +
          '" entrada(s) escrita(s) à mão sem DEGRAU escolhido — elas estão ' +
          'custando 0. Ache na régua do CATÁLOGO o degrau em que o efeito cai.")';
  var alvo = inv.getRange(lAviso, faixas[0].col,
                          1, faixas[1].col + 19 - faixas[0].col + 1);
  if (alvo.isPartOfMerge()) alvo.breakApart();
  alvo.merge().setFormula(f)
      .setFontFamily('Roboto').setFontSize(9).setFontColor(AMBAR)
      .setBackground(PAINEL).setVerticalAlignment('middle');

  // ---------- 3 · a vida agora nasce cheia, e a barra ganha guarda -------
  var cVida = cel_(idx, 'vida'), cMax = cel_(idx, 'vida_max');
  if (cVida && cMax) {
    if (inv.getRange(cVida).getValue() === '') {
      inv.getRange(cVida).setFormula('=' + cMax);
    }
    var barra = achaBarra_(inv, cVida);
    if (barra) {
      var atual = barra.getFormula();
      if (atual.indexOf('SPARKLINE') >= 0 && atual.indexOf('$' + cVida + '="") ') < 0) {
        // envolve o que já existe: campo vazio -> celula vazia, sem desenhar
        var corpo = atual.replace(/^=/, '');
        barra.setFormula('=IF(' + cMax + '="","",IF(' + cVida + '="","",' +
                         corpo + '))');
      }
    }
  }

  SpreadsheetApp.getUi().alert(
    'Pronto. O nome do Traço e do Comando não tem mais menu nem triângulo; ' +
    'o aviso âmbar embaixo dos blocos acende só quando uma entrada escrita à ' +
    'mão está sem DEGRAU. A vida agora nasce cheia e a barra não desenha com ' +
    'o campo vazio.');
}

// --- apoio ---------------------------------------------------------------

function indice_(dados) {
  var c = 0;
  for (var i = 1; i <= dados.getLastColumn(); i++) {
    if (dados.getRange(2, i).getValue() === 'campo') { c = i; break; }
  }
  if (!c) throw new Error('a DADOS_INV não publica o índice de campos');
  var v = dados.getRange(3, c, dados.getLastRow() - 2, 2).getValues();
  var m = {};
  v.forEach(function (l) { if (l[0] && l[1]) m[String(l[0])] = String(l[1]); });
  return m;
}

function cel_(idx, k) { return idx[k] ? idx[k].replace(/\$/g, '') : null; }

function slots_(idx, grupo) {
  var out = [];
  Object.keys(idx).forEach(function (k) {
    var m = k.match(new RegExp('^' + grupo + '_(\\d+)$'));
    if (!m) return;
    var p = idx[k].replace(/\$/g, '').match(/^([A-Z]+)(\d+)$/);
    out.push({ n: Number(m[1]), lin: Number(p[2]), col: num_(p[1]) });
  });
  return out.sort(function (a, b) { return a.n - b.n; });
}

/** o intervalo A1 ABSOLUTO da coluna de nomes da tabela de preço do grupo */
function tabela_(dados, grupo) {
  var titulo = 'tab_' + grupo;
  for (var i = 1; i <= dados.getLastColumn(); i++) {
    if (dados.getRange(1, i).getValue() === titulo) {
      var n = 0;
      while (dados.getRange(3 + n, i).getValue() !== '') n++;
      return "DADOS_INV!$" + letra_(i) + "$3:$" + letra_(i) + "$" + (2 + n);
    }
  }
  throw new Error('a DADOS_INV não tem a tabela ' + titulo);
}

/** a celula da barra: a unica com SPARKLINE que cita a vida agora */
function achaBarra_(inv, cVida) {
  var fs = inv.getDataRange().getFormulas();
  for (var r = 0; r < fs.length; r++) {
    for (var c = 0; c < fs[r].length; c++) {
      var f = fs[r][c];
      if (f && f.indexOf('SPARKLINE') >= 0 && f.indexOf(cVida) >= 0) {
        return inv.getRange(r + 1, c + 1);
      }
    }
  }
  return null;
}

function letra_(n) {
  var s = '';
  while (n > 0) { var r = (n - 1) % 26; s = String.fromCharCode(65 + r) + s; n = (n - 1 - r) / 26; }
  return s;
}

function num_(s) {
  var n = 0;
  for (var i = 0; i < s.length; i++) n = n * 26 + (s.charCodeAt(i) - 64);
  return n;
}
