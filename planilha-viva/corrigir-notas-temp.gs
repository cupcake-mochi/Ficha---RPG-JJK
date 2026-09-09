/**
 * Escreve as notas dos três campos TEMP na aba FICHA.
 *
 * POR QUE: a nota da vida temporária (AF23) dizia TRÊS das quatro regras e
 * omitia a quarta — o TETO DE METADE DA VIDA MÁXIMA. Ele não é invenção: o
 * livro publica no capítulo 10, "Como Jogar", e a peça 1 §5.1.1 do
 * JJK---Project é a dona da conta. Sem o teto, empilhar é sempre melhor que
 * atacar, e um Apoio de Classe 1 entrega 9 num Emanador de nível 2 cujo teto é 7.
 *
 * E AF27 e AF31 não tinham nota nenhuma. A de AF31 avisa que regra nenhuma
 * concede integridade temporária — o campo fica assim mesmo, por decisão do
 * Mizuki na v0.222, como espaço do mestre. O B17 fechou aí.
 *
 * ⚠ Isto existe como script separado porque o emitir_gs.py NÃO carrega nota —
 * o transporte para o Apps Script leva valor, fórmula, formato e caixa de
 * seleção, e para por aí. O gerador Python já escreve as três no .xlsx.
 *
 * COMO USAR:
 *   Extensões → Apps Script → cole num arquivo novo → salve → Executar.
 *   Roda quantas vezes quiser: ele sobrescreve as mesmas três notas.
 */
function corrigirNotasDosCamposTemp() {
  var ficha = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('FICHA');
  if (!ficha) {
    throw new Error('Não achei a aba FICHA.');
  }

  var notas = {
    'AF23':
      'Vida temporária é anteparo, e não vida.\n' +
      '• É gasta antes da vida normal.\n' +
      '• Não empilha: duas fontes, fica a maior.\n' +
      '• Teto: metade da sua vida máxima.\n' +
      '• Some no fim da cena.\n' +
      'Livro, cap. 10. A Melhoria Rasga Escudo ignora ela.',
    'AF27':
      'Energia temporária gasta como PE, e gasta primeiro.\n' +
      '• Acumula até o teto que a própria fonte declarar.\n' +
      '• Hoje só o Braseiro concede, e o teto dele é 2.\n' +
      '• Some no fim da cena.',
    'AF31':
      '⚠ Regra nenhuma concede integridade temporária hoje.\n' +
      'O campo fica assim mesmo — é espaço do mestre: se alguma coisa na mesa ' +
      'conceder, anote aqui.\n' +
      'A ficha já trata ele como as outras duas: um delta negativo come a ' +
      'temporária antes da Integridade, e ela nunca fica negativa.'
  };

  var log = [];
  Object.keys(notas).forEach(function (cel) {
    var antes = ficha.getRange(cel).getNote();
    ficha.getRange(cel).setNote(notas[cel]);
    log.push(cel + ': ' + (antes ? 'reescrita' : 'criada'));
  });

  Logger.log(log.join('\n'));
  SpreadsheetApp.getUi().alert(
    'Notas dos campos TEMP: ' + log.length + ' células.\n\n' + log.join('\n')
  );
}
