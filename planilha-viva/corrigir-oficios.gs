/**
 * Corrige o atributo dos 11 ofícios na aba FICHA — hoje todos apontam para
 * INTELIGÊNCIA, e só 3 deles (Herbalismo, Burocracia, Culinária) estão certos
 * por coincidência. Fonte: peça 7 §6 do JJK---Project ("atributo padrão | a
 * vizinha que decide").
 *
 * COMO USAR:
 *   Extensões → Apps Script → cole isto num arquivo novo → salve → Executar
 *   (o Google pode pedir permissão na primeira vez — autorize, é a sua própria
 *   planilha). Roda uma vez só; rodar de novo não faz mal, só reescreve os
 *   mesmos 8 valores.
 */
function corrigirAtributoDosOficios() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var ficha = ss.getSheetByName('FICHA');
  if (!ficha) {
    throw new Error('Não achei a aba FICHA.');
  }

  // celula -> [oficio, atributo certo]. So as 8 que estao erradas hoje.
  var correcoes = {
    'K75': ['Condução',     'DESTREZA'],
    'K76': ['Arrombamento', 'DESTREZA'],
    'K78': ['Forja',        'FORÇA'],
    'K79': ['Caligrafia',   'DESTREZA'],
    'X75': ['Entalhador',   'DESTREZA'],
    'X76': ['Alfaiate',     'DESTREZA'],
    'X78': ['Jogatina',     'ESSÊNCIA'],
    'X79': ['Instrumento',  'ESSÊNCIA'],
  };

  var log = [];
  Object.keys(correcoes).forEach(function (cel) {
    var oficio = correcoes[cel][0];
    var certo = correcoes[cel][1];
    var antes = ficha.getRange(cel).getValue();
    ficha.getRange(cel).setValue(certo);
    log.push(oficio + ' (' + cel + '): ' + antes + ' -> ' + certo);
  });

  Logger.log(log.join('\n'));
  SpreadsheetApp.getUi().alert(
    'Ofícios corrigidos: ' + log.length + ' células.\n\n' + log.join('\n')
  );
}
