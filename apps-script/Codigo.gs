/**
 * Projeto M · a parte da ficha que o .xlsx não carrega.
 *
 * O .xlsx é o veículo do layout. Quem faz a ficha ser ficha é isto aqui:
 * caixa de seleção nativa, proteção de fórmula, formatação condicional,
 * entrada por delta e a trava de montagem de feitiço.
 *
 * NADA de endereço de célula está escrito neste arquivo. Tudo sai do índice
 * que a própria ficha publica na aba DADOS — se o layout mudar, o script
 * continua achando os campos.
 *
 * Duas funções importam:
 *   montarFicha()  você roda UMA vez, na ficha-modelo. Pede autorização.
 *   onEdit(e)      gatilho simples. Roda sozinho, inclusive nas cópias que
 *                  os jogadores fizerem, e NÃO pede autorização de ninguém.
 */

var IDX_COL_CAMPO = 53;   // BA
var IDX_COL_CEL   = 54;   // BB

/** Lê o índice de células que a ficha publica na DADOS. */
function indice() {
  var dados = SpreadsheetApp.getActive().getSheetByName('DADOS');
  var n = dados.getLastRow();
  var vals = dados.getRange(1, IDX_COL_CAMPO, n, 2).getValues();
  var m = {};
  vals.forEach(function (l) { if (l[0] && l[1]) m[l[0]] = String(l[1]); });
  return m;
}

// =====================================================================
// RODE UMA VEZ
// =====================================================================
function montarFicha() {
  var ss = SpreadsheetApp.getActive();
  var idx = indice();
  aplicarFonte_(ss);
  caixasDeSelecao_(ss);
  corDeEstado_(ss, idx);
  protegerFormulas_(ss, idx);
  notasDeRegra_(ss, idx);
  SpreadsheetApp.getUi().alert(
    'Ficha montada.\n\n' +
    'Os jogadores copiam este modelo pronto e não rodam nada. ' +
    'O delta e o descanso funcionam na cópia sem autorização, porque são ' +
    'gatilho simples.');
}

/** Resolve o Calibri: o .xlsx deixa fonte solta em célula pintada sem estilo. */
function aplicarFonte_(ss) {
  ss.getSheets().forEach(function (aba) {
    if (aba.getName() === 'MESA') {
      // decisão C4: a MESA usa só a fonte de corpo. O app de celular troca
      // sem avisar qualquer fonte fora da lista curta do Sheets.
      aba.getDataRange().setFontFamily('Roboto');
    }
  });
}

/** O .xlsx não carrega caixa de seleção — ela só existe como texto. */
function caixasDeSelecao_(ss) {
  var ficha = ss.getSheetByName('FICHA');
  var marca = SpreadsheetApp.newDataValidation().requireCheckbox().build();
  // as colunas de marca das perícias, ofícios e testes: a primeira coluna de
  // cada bloco, achada pelo rótulo em vez de decorada
  [[4, 'PERÍCIAS'], [18, 'PERÍCIAS'], [4, 'OFÍCIOS'], [28, 'OFÍCIOS']]
    .forEach(function (par) {
      var col = par[0];
      var lin = acharBloco_(ficha, par[1]);
      if (lin > 0) ficha.getRange(lin, col, 13, 1).setDataValidation(marca);
    });
}

function acharBloco_(aba, titulo) {
  var achou = aba.createTextFinder(titulo).matchEntireCell(false).findNext();
  return achou ? achou.getRow() + 1 : -1;
}

/**
 * A decisão A5 em formatação condicional: osso cheio, âmbar abaixo da metade,
 * vermelho abaixo de um quarto. Os hex saem do decisoes-ficha.json e estão
 * repetidos aqui de propósito — o Apps Script não lê o repositório. Se eles
 * mudarem lá, o conferir-decisoes.py acende.
 */
function corDeEstado_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  var regras = ficha.getConditionalFormatRules();
  ['vida', 'energia', 'integridade'].forEach(function (r) {
    var atual = idx[r], max = idx[r + '_max'];
    if (!atual || !max) return;
    var alvo = ficha.getRange(atual.replace(/\$/g, ''));
    [['<=0.25', '#C2334D'], ['<=0.5', '#D89B3A']].forEach(function (par) {
      regras.push(SpreadsheetApp.newConditionalFormatRule()
        .whenFormulaSatisfied('=AND(' + max + '>0,' + atual + '/' + max + par[0] + ')')
        .setFontColor(par[1]).setRanges([alvo]).build());
    });
  });
  ficha.setConditionalFormatRules(regras);
}

/** O jogador não apaga a Vida máxima sem querer. */
function protegerFormulas_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  var travar = ['vida_max', 'energia_max', 'integridade_max', 'defesa', 'proteção',
                'iniciativa', 'maestria', 'cd de feitiço', 'conjuração',
                'corpo a corpo', 'à distância', 'espaços de feitiço',
                'refino de graça', 'classe máxima', 'classe 0 grátis'];
  travar.forEach(function (k) {
    if (!idx[k]) return;
    var p = ficha.getRange(idx[k].replace(/\$/g, '')).protect();
    p.setDescription('fórmula · ' + k);
    p.setWarningOnly(true);      // avisa em vez de bloquear: mestre precisa poder mexer
  });
}

/** A regra fica no cabeçalho, ao passar o mouse, sem gastar pixel. */
function notasDeRegra_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  var notas = {
    'proteção': 'Traje e Revestimento DESLIGAM a proteção da aptidão e entregam a ' +
                'deles no lugar. Deixe o campo de equipamento vazio para usar a aptidão.',
    'maestria': 'Vira 2 no nível 10, 3 no 18, 4 no 26. Não é "a cada oito níveis".',
    'cd de feitiço': 'Não existe atributo de conjuração na ficha padrão: o 2 é fixo.',
    'vida_temp': 'Vida temporária não empilha: fica a maior. Some no fim da cena, ' +
                 'e é gasta antes da vida normal.'
  };
  Object.keys(notas).forEach(function (k) {
    if (idx[k]) ficha.getRange(idx[k].replace(/\$/g, '')).setNote(notas[k]);
  });
}

// =====================================================================
// GATILHO SIMPLES · roda sozinho, na cópia de qualquer jogador
// =====================================================================
function onEdit(e) {
  if (!e || !e.range) return;
  var aba = e.range.getSheet().getName();
  if (aba !== 'FICHA' && aba !== 'MESA') return;
  var idx = indice();
  aplicarDelta_(e, idx);
}

/**
 * Decisão A4: o jogador digita -9 na caixinha, o script aplica no atual e
 * limpa a caixinha. O atual continua editável à mão — sem sinal o gatilho
 * não roda, e sem isso a ficha viraria pedra no meio da sessão.
 */
function aplicarDelta_(e, idx) {
  var ficha = SpreadsheetApp.getActive().getSheetByName('FICHA');
  ['vida', 'energia', 'integridade'].forEach(function (r) {
    var cd = idx[r + '_delta'], ca = idx[r];
    if (!cd || !ca) return;
    var caixa = ficha.getRange(cd.replace(/\$/g, ''));
    if (caixa.getA1Notation() !== e.range.getA1Notation()) return;
    var passo = Number(e.range.getValue());
    if (!passo) return;
    var atual = ficha.getRange(ca.replace(/\$/g, ''));
    var max = Number(ficha.getRange(idx[r + '_max'].replace(/\$/g, '')).getValue()) || 0;
    var novo = Number(atual.getValue()) + passo;
    atual.setValue(Math.max(0, max ? Math.min(novo, max) : novo));
    caixa.clearContent();
  });
}

// =====================================================================
// A ARTE, sem depender de URL nenhuma
// =====================================================================
/**
 * Decisão C5: a arte é desenhada por código e entra em base64, pela CellImage.
 * Assim ela não depende de arquivo hospedado em lugar nenhum, e a ficha
 * continua inteira mesmo offline.
 *
 * Cole o base64 de cada peça em ARTE. O arte/gera.py imprime eles com:
 *   python3 arte/gera.py --base64
 */
var ARTE = {
  // 'selo': 'iVBORw0KGgo...'
};

function colarArte(nomeDaPeca, aba, celula) {
  if (!ARTE[nomeDaPeca]) throw new Error('peça sem base64 em ARTE: ' + nomeDaPeca);
  var img = SpreadsheetApp.newCellImage()
    .setSourceUrl('data:image/png;base64,' + ARTE[nomeDaPeca])
    .setAltTextTitle(nomeDaPeca)
    .build();
  SpreadsheetApp.getActive().getSheetByName(aba).getRange(celula).setValue(img);
}
