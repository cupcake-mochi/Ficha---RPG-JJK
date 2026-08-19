/**
 * Projeto M · o que roda DEPOIS da ficha estar montada.
 *
 * O Ficha.gs constrói a planilha. Este arquivo cuida do que depende de ela já
 * existir: cor de estado, notas de regra, proteção de fórmula, e o gatilho que
 * faz a caixinha de ± funcionar.
 *
 * Nenhum endereço de célula está escrito aqui. Tudo sai do índice que a
 * própria ficha publica na aba DADOS, então o layout pode mudar sem quebrar
 * este arquivo.
 */

var IDX_COL_CAMPO = 53;   // BA
var IDX_COL_CEL   = 54;   // BB

function indice() {
  var dados = SpreadsheetApp.getActive().getSheetByName('DADOS');
  var vals = dados.getRange(1, IDX_COL_CAMPO, dados.getLastRow(), 2).getValues();
  var m = {};
  vals.forEach(function (l) { if (l[0] && l[1]) m[l[0]] = String(l[1]); });
  return m;
}

function cel_(idx, chave) {
  return idx[chave] ? idx[chave].replace(/\$/g, '') : null;
}

/**
 * A decisão A5: osso cheio, âmbar abaixo da metade, vermelho abaixo de um
 * quarto. Os hex estão repetidos aqui porque o Apps Script não lê o
 * repositório — se eles mudarem lá, o conferir-decisoes.py acende.
 */
function corDeEstado_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  var regras = [];
  ['vida', 'energia', 'integridade'].forEach(function (r) {
    var atual = idx[r], max = idx[r + '_max'];
    if (!atual || !max) return;
    var alvo = ficha.getRange(cel_(idx, r));
    [[0.25, '#C2334D'], [0.5, '#D89B3A']].forEach(function (par) {
      regras.push(SpreadsheetApp.newConditionalFormatRule()
        .whenFormulaSatisfied('=AND(N(' + max + ')>0,' + atual + '/' + max +
                              '<=' + par[0] + ')')
        .setFontColor(par[1]).setRanges([alvo]).build());
    });
  });
  ficha.setConditionalFormatRules(regras);
  return regras.length + ' regra(s)';
}

/** A regra aparece ao passar o mouse, sem gastar pixel na tela. */
function notasDeRegra_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  var notas = {
    'proteção': 'Traje e Revestimento DESLIGAM a proteção da aptidão e entregam a ' +
                'deles no lugar. Deixe o equipamento vazio para usar a aptidão.',
    'maestria': 'Vira 2 no nível 10, 3 no 18, 4 no 26. Não é "a cada oito níveis".',
    'cd de feitiço': 'Não existe atributo de conjuração na ficha padrão: o 2 é fixo.',
    'vida_temp': 'Vida temporária não empilha: fica a maior. Some no fim da cena, ' +
                 'e é gasta antes da vida normal.',
    'equipamento': 'Enquanto o catálogo do capítulo 12 não entra, digite aqui a ' +
                   'proteção do equipamento. Vazio = usa a da aptidão.'
  };
  var n = 0;
  Object.keys(notas).forEach(function (k) {
    var c = cel_(idx, k);
    if (c) { ficha.getRange(c).setNote(notas[k]); n++; }
  });
  return n + ' nota(s)';
}

/** O jogador não apaga a Vida máxima sem querer. Avisa, não bloqueia. */
function protegerFormulas_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  var travar = ['vida_max', 'energia_max', 'integridade_max', 'defesa', 'proteção',
                'iniciativa', 'maestria', 'cd de feitiço', 'conjuração',
                'corpo a corpo', 'à distância', 'espaços de feitiço',
                'refino de graça', 'classe máxima', 'classe 0 grátis'];
  var n = 0;
  travar.forEach(function (k) {
    var c = cel_(idx, k);
    if (!c) return;
    var p = ficha.getRange(c).protect();
    p.setDescription('fórmula · ' + k);
    p.setWarningOnly(true);   // o mestre precisa poder mexer
    n++;
  });
  return n + ' célula(s)';
}

// =====================================================================
// GATILHO SIMPLES · roda sozinho, inclusive na cópia de cada jogador,
// e não pede autorização de ninguém.
// =====================================================================
function onEdit(e) {
  if (!e || !e.range) return;
  var aba = e.range.getSheet().getName();
  if (aba !== 'FICHA') return;
  aplicarDelta_(e, indice());
}

/**
 * Decisão A4: digita -9 na caixinha, o script aplica no atual e limpa.
 * O atual continua editável à mão — sem sinal o gatilho não roda, e sem isso
 * a ficha viraria pedra no meio da sessão.
 */
function aplicarDelta_(e, idx) {
  var ficha = SpreadsheetApp.getActive().getSheetByName('FICHA');
  ['vida', 'energia', 'integridade'].forEach(function (r) {
    var cd = cel_(idx, r + '_delta');
    if (!cd || cd !== e.range.getA1Notation()) return;
    var passo = Number(e.range.getValue());
    if (!passo) return;
    var atual = ficha.getRange(cel_(idx, r));
    var max = Number(ficha.getRange(cel_(idx, r + '_max')).getValue()) || 0;
    var novo = Number(atual.getValue()) + passo;
    atual.setValue(Math.max(0, max ? Math.min(novo, max) : novo));
    e.range.clearContent();
  });
}
