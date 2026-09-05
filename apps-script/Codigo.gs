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
                 'e é gasta antes da vida normal — a caixinha de ± desconta ' +
                 'daqui primeiro e só o que sobrar desce na vida. Dano com ' +
                 'Rasga Escudo ignora isto: edite a vida na mão.',
    'energia_temp': 'Energia temporária acumula até o teto que a fonte declarar ' +
                    '(hoje só o Braseiro concede, e o teto dele é 2). Some no fim ' +
                    'da cena, e a caixinha de ± queima daqui antes do seu PE.',
    'integridade_temp': 'Nenhuma regra do manual concede integridade temporária. ' +
                        'O campo está aqui pela forma das outras duas reservas: ' +
                        'se algo conceder, a caixinha de ± desconta daqui primeiro.',
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
 * A conta da caixinha de +/-, sem planilha nenhuma em volta.
 *
 * Ela mora separada porque e o unico lugar do projeto onde duas decisoes se
 * encontram: a A4 (a caixinha) e a A2 (a temporaria gasta primeiro). O
 * regressao-delta.js roda esta funcao contra o exemplo publicado no
 * manual-temporario.md, e o Apps Script nao pode ser testado de fora.
 *
 * Perda come a temporaria antes de tocar a reserva. Ganho nao devolve
 * temporaria: ela e um extra por cima, e quem concede e a fonte, no campo
 * TEMP. Quem toma dano com `Rasga Escudo` -- que ignora a temporaria -- edita
 * a reserva na mao; a A4 mantem o atual editavel exatamente para isso.
 */
function aplicaPasso_(atual, max, temp, passo) {
  atual = Number(atual) || 0;
  max = Number(max) || 0;
  temp = Math.max(0, Number(temp) || 0);
  passo = Number(passo) || 0;

  var novo = atual;
  if (passo < 0) {
    var comido = Math.min(temp, -passo);
    temp = temp - comido;
    novo = atual - (-passo - comido);
  } else {
    novo = atual + passo;
  }
  return {
    atual: Math.max(0, max ? Math.min(novo, max) : novo),
    temp: temp
  };
}

/**
 * Decisão A4: digita -9 na caixinha, o script aplica no atual e limpa.
 * O atual continua editável à mão — sem sinal o gatilho não roda, e sem isso
 * a ficha viraria pedra no meio da sessão.
 *
 * Decisão A2: o passo negativo come a temporária antes da reserva, e o campo
 * TEMP desce junto. Sem isso a caixinha descontava direto da vida e a
 * temporária ficava parada na tela, valendo nada.
 */
function aplicarDelta_(e, idx) {
  var ficha = SpreadsheetApp.getActive().getSheetByName('FICHA');
  ['vida', 'energia', 'integridade'].forEach(function (r) {
    var cd = cel_(idx, r + '_delta');
    if (!cd || cd !== e.range.getA1Notation()) return;
    var passo = Number(e.range.getValue());
    if (!passo) return;
    var atual = ficha.getRange(cel_(idx, r));
    var ct = cel_(idx, r + '_temp');
    var temp = ct ? ficha.getRange(ct) : null;
    var antes = temp ? Math.max(0, Number(temp.getValue()) || 0) : 0;

    var fim = aplicaPasso_(atual.getValue(),
                           ficha.getRange(cel_(idx, r + '_max')).getValue(),
                           antes, passo);

    atual.setValue(fim.atual);
    if (temp && fim.temp !== antes) temp.setValue(fim.temp);
    e.range.clearContent();
  });
}

// =====================================================================
// O AUTOTESTE, para rodar de dentro do editor do Apps Script.
//
// O onEdit e gatilho simples: dispara sozinho ao digitar e nao se executa
// a mao -- chamado pelo seletor de funcao ele quebra, porque o `e` vem
// vazio. Entao o que se roda aqui e isto, que nao toca na planilha.
//
// Os mesmos casos moram no regressao-delta.js, que roda no node lendo os
// numeros do manual-temporario.md. Aqui eles estao escritos a mao de
// proposito: o Apps Script nao le o repositorio, e o que se quer saber no
// editor e se a colagem entrou, nao se a regra mudou.
// =====================================================================
function testeDelta() {
  var casos = [
    ['exemplo do manual (18 temp, 20 de dano)', [40, 40, 18, -20], 38, 0],
    ['dano menor que a temporaria',             [40, 40, 18,  -5], 40, 13],
    ['sem temporaria',                          [19, 19,  0,  -9], 10, 0],
    ['cura nao devolve temporaria',             [10, 19,  5,   4], 14, 5],
    ['cura nao passa do maximo',                [17, 19,  0,   9], 19, 0]
  ];
  var falhou = 0;
  casos.forEach(function (c) {
    var r = aplicaPasso_(c[1][0], c[1][1], c[1][2], c[1][3]);
    var ok = (r.atual === c[2] && r.temp === c[3]);
    if (!ok) falhou++;
    Logger.log((ok ? 'OK   ' : 'FALHA') + ' \u00b7 ' + c[0] +
               ' \u00b7 atual ' + r.atual + ' (esperado ' + c[2] + ')' +
               ' \u00b7 temp ' + r.temp + ' (esperado ' + c[3] + ')');
  });
  Logger.log(falhou ? (falhou + ' FALHA(S)') : 'as 5 passaram');
}
