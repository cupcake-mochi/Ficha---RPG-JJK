/**
 * Conserta o #ERROR! da linha de aviso, embaixo dos blocos de Traço e Comando.
 *
 * A CAUSA, e ela já estava escrita neste projeto: numa planilha em português o
 * separador de argumento é ponto e vírgula, e `IF(a,b,c)` vira erro de
 * análise. O `Ficha.gs` deste repositório tem a função `paraLocal_` com o
 * comentário: *"Eu supus duas vezes que o setFormula resolvia isso sozinho, e
 * duas vezes estava errado."* O tira-triangulo.gs supôs uma terceira vez.
 *
 * Este arquivo não supõe: ele PERGUNTA à planilha qual pontuação ela aceita,
 * escrevendo uma fórmula de teste numa célula descartável e olhando o
 * resultado. É uma ida ao servidor, uma vez.
 *
 * Rodar: Extensões > Apps Script, arquivo novo, cole, execute consertaAviso.
 */

var AMBAR = '#D89B3A', PAINEL = '#1E1733';
var SEP = null;

function consertaAviso() {
  var ss = SpreadsheetApp.getActive();
  var inv = ss.getSheetByName('INVOCAÇÃO');
  var dados = ss.getSheetByName('DADOS_INV');
  if (!inv || !dados) throw new Error('faltou INVOCAÇÃO ou DADOS_INV');

  separador_(ss);
  var idx = indice_(dados);

  var faixas = ['traco', 'comando'].map(function (g) {
    var s = slots_(idx, g);
    if (!s.length) throw new Error('o índice não publica slot de ' + g);
    return { col: s[0].col, r1: s[0].lin, r2: s[s.length - 1].lin,
             deg: s[0].col + 11, tab: tabela_(dados, g) };
  });

  // a contagem de cada grupo, montada uma vez e reusada nos dois lados do IF
  var contas = faixas.map(function (f) {
    var nome = letra_(f.col) + f.r1 + ':' + letra_(f.col) + f.r2;
    var deg  = letra_(f.deg) + f.r1 + ':' + letra_(f.deg) + f.r2;
    return 'SUMPRODUCT((' + nome + '<>"")*(' + nome + '<>"—")*' +
           '(COUNTIF(' + f.tab + ',' + nome + ')=0)*' +
           '((' + deg + '="—")+(' + deg + '="")))';
  });
  var soma = contas.join('+');
  var f = '=IF(' + soma + '=0,"","⚠ "&(' + soma + ')&' +
          '" entrada(s) escrita(s) à mão sem DEGRAU escolhido — elas estão ' +
          'custando 0. Ache na régua do CATÁLOGO o degrau em que o efeito cai.")';

  var lin = Math.max(faixas[0].r2, faixas[1].r2) + 1;
  var alvo = inv.getRange(lin, faixas[0].col,
                          1, faixas[1].col + 19 - faixas[0].col + 1);
  if (alvo.isPartOfMerge()) alvo.breakApart();
  alvo.merge().setFormula(paraLocal_(f))
      .setFontFamily('Roboto').setFontSize(9).setFontColor(AMBAR)
      .setBackground(PAINEL).setVerticalAlignment('middle');

  var lido = inv.getRange(lin, faixas[0].col).getDisplayValue();
  SpreadsheetApp.getUi().alert(
    'Aviso reescrito com o separador "' + SEP + '", que é o que esta planilha ' +
    'aceita.\n\nA célula agora mostra: ' +
    (lido === '' ? '(vazia — nenhuma entrada sem degrau, que é o certo)' : lido));
}

/**
 * Pergunta à planilha qual pontuação ela aceita, em vez de supor.
 * Mesmo método do Ficha.gs, e pelo mesmo motivo.
 */
function separador_(ss) {
  if (SEP) return SEP;
  var aba = ss.getSheets()[0];
  var alvo = aba.getRange(aba.getMaxRows(), aba.getMaxColumns());
  var antes = alvo.getFormula() || alvo.getValue();
  alvo.setFormula('=IF(1=1,"v","f")');
  SEP = (alvo.getValue() === 'v') ? ',' : ';';
  if (antes === '') alvo.clearContent(); else alvo.setValue(antes);
  Logger.log('esta planilha aceita "' + SEP + '" como separador de argumento');
  return SEP;
}

/**
 * Troca a vírgula pelo separador da planilha, sem tocar em vírgula que é TEXTO
 * (entre aspas) nem em vírgula dentro de chaves, que separa COLUNA de matriz e
 * usa outra pontuação. Nenhuma das duas aparece nesta fórmula, mas a função
 * fica igual à do Ficha.gs de propósito: duas cópias divergentes da mesma
 * conversão é como este projeto perdeu versão antes.
 */
function paraLocal_(f) {
  if (SEP === ',') return f;
  var fora = true, chaves = 0, saida = '';
  for (var i = 0; i < f.length; i++) {
    var ch = f.charAt(i);
    if (ch === '"') fora = !fora;
    else if (fora && ch === '{') chaves++;
    else if (fora && ch === '}') chaves--;
    if (ch === ',' && fora) saida += (chaves > 0 ? '\\' : SEP);
    else saida += ch;
  }
  return saida;
}

// --- apoio, igual ao do tira-triangulo.gs -------------------------------

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
