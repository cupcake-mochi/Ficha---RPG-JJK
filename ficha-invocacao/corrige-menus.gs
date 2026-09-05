/**
 * Corrige os menus suspensos da aba INVOCAÇÃO.
 *
 * Ao copiar as abas da planilha avulsa para dentro da ficha, o Sheets
 * achatou sete dos nove menus em listas literais e deixou os outros dois
 * como intervalo — só que apontando para a aba DADOS do player, e não
 * para DADOS_INV. Este script devolve os nove ao dono do dado, que é a
 * DADOS_INV, e acerta os valores digitados que saíram da lista achatada.
 *
 * Como rodar: Extensões > Apps Script, cole, salve, execute corrigeMenus.
 *
 * Ele NÃO cria a coluna DEGRAU -- isso é o migra-degrau.gs. Os dois convivem
 * em qualquer ordem: este mexe só nos menus, aquele só na repartição da faixa.
 */

// A terceira coluna diz se o menu BLOQUEIA valor de fora da lista.
// Traço e Comando não podem bloquear: é digitando por cima do menu que o
// jogador escreve um dos seus, como o capítulo 16 deixa. O resto bloqueia --
// ali valor de fora não é escolha de sabor, é fórmula lendo lixo.
var MENUS = [
  ['Z19',       'A2:A5',   true],   // tipo
  ['AK19',      'B2:B4',   true],   // trilha
  ['D22',       'E2:E5',   true],   // sintonia (o traço "—" mora aqui)
  ['D43',       'C2:C6',   true],   // atributo do acerto
  ['Z43',       'F2:F3',   true],   // defesa usa, do dono
  ['O46',       'D2:D5',   true],   // qual TR ela treina
  ['Z46',       'G2:G3',   true],   // o físico dela usa
  ['D80:D88',   'H2:H15',  false],  // traço  · aceita o seu, digitado
  ['Z80:Z85',   'I2:I9',   false]   // comando · idem
];

// valores que ficaram fora do dono depois do achatamento
var VALORES = [
  ['Z19', 'técnica'],
  ['D43', 'Força'],
  ['Z43', 'Inteligência'],
  ['Z46', 'Força'],
  ['O46', 'Físico']
];

function corrigeMenus() {
  var ss = SpreadsheetApp.getActive();
  var inv = ss.getSheetByName('INVOCAÇÃO');
  var dados = ss.getSheetByName('DADOS_INV');
  if (!inv || !dados) throw new Error('faltou INVOCAÇÃO ou DADOS_INV');

  for (var i = 0; i < MENUS.length; i++) {
    var b = SpreadsheetApp.newDataValidation()
      .requireValueInRange(dados.getRange(MENUS[i][1]), true)
      .setAllowInvalid(!MENUS[i][2]);
    if (!MENUS[i][2]) {
      b.setHelpText('Escolha do catálogo, ou digite o nome do seu e ' +
                    'preencha o DEGRAU.');
    }
    inv.getRange(MENUS[i][0]).setDataValidation(b.build());
  }

  for (var j = 0; j < VALORES.length; j++) {
    inv.getRange(VALORES[j][0]).setValue(VALORES[j][1]);
  }

  SpreadsheetApp.getUi().alert(
    'Menus corrigidos: ' + MENUS.length + ' apontam para DADOS_INV, ' +
    VALORES.length + ' valores acertados.');
}
