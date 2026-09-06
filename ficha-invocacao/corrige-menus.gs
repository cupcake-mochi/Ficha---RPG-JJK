/**
 * Corrige os menus suspensos da aba INVOCAÇÃO.
 *
 * Ao copiar as abas da planilha avulsa para dentro da ficha, o Sheets
 * achatou os menus em listas literais e deixou os que sobraram como
 * intervalo -- só que apontando para a aba DADOS do player, e não para a
 * DADOS_INV. Este script devolve cada um ao dono do dado e acerta os
 * valores que sobraram fora da lista depois do achatamento.
 *
 * Como rodar: Extensões > Apps Script, cole, salve, execute corrigeMenus.
 *
 * ELE NÃO MEXE NO NOME DO TRAÇO NEM DO COMANDO -- e isso é de propósito.
 * A primeira versão deste arquivo devolvia menu àquelas duas faixas com
 * setAllowInvalid(true), que é exatamente o estado "avisar" do Sheets: o
 * triângulo vermelho. O tira-triangulo.gs tirou aquele menu de lá por
 * decisão sua, e o aviso âmbar da linha de baixo é que faz o trabalho
 * agora. Rodar a versão antiga desfazia o tira-triangulo.
 *
 * Ele também não cria a coluna DEGRAU -- isso é o migra-degrau.gs. Os três
 * convivem em qualquer ordem: este mexe só nos sete menus fechados.
 */

// Os sete menus que BLOQUEIAM valor de fora da lista. Aqui valor de fora
// não é escolha de sabor, é fórmula lendo lixo.
// As faixas conferidas contra o invocacao.json: as nove listas da DADOS_INV
// nascem em A..I, cada uma começando na linha 2.
var MENUS = [
  ['Z19',  'A2:A5',  'tipo'],
  ['AK19', 'B2:B4',  'trilha'],
  ['D22',  'E2:E5',  'rota de sintonia'],
  ['D43',  'C2:C6',  'atributo do acerto'],
  ['Z43',  'F2:F3',  'a defesa dela usa'],
  ['O46',  'D2:D5',  'qual TR ela treina'],
  ['Z46',  'G2:G3',  'o Físico dela usa']
];

function corrigeMenus() {
  var ss = SpreadsheetApp.getActive();
  var inv = ss.getSheetByName('INVOCAÇÃO');
  var dados = ss.getSheetByName('DADOS_INV');
  if (!inv || !dados) throw new Error('faltou INVOCAÇÃO ou DADOS_INV');

  var trocados = [];

  for (var i = 0; i < MENUS.length; i++) {
    var cel = inv.getRange(MENUS[i][0]);
    var faixa = dados.getRange(MENUS[i][1]);
    var lista = faixa.getValues().map(function (l) { return String(l[0]); });

    // Primeiro o valor, depois a validação: o menu fechado não apaga o que
    // já está escrito na célula, só barra a digitação seguinte -- então uma
    // célula com "Intêligencia" dentro continuaria com ela para sempre.
    var atual = String(cel.getValue());
    if (lista.indexOf(atual) < 0) {
      cel.setValue(lista[0]);
      trocados.push(MENUS[i][0] + ' (' + MENUS[i][2] + '): "' + atual +
                    '" estava fora da lista, virou "' + lista[0] + '"');
    }

    cel.setDataValidation(
      SpreadsheetApp.newDataValidation()
        .requireValueInRange(faixa, true)
        .setAllowInvalid(false)
        .build());
  }

  SpreadsheetApp.getUi().alert(
    MENUS.length + ' menus agora leem a DADOS_INV.' +
    (trocados.length ? '\n\nValores acertados:\n· ' + trocados.join('\n· ')
                     : '\n\nNenhum valor estava fora da lista.') +
    '\n\nO nome do Traço e do Comando não foi tocado: eles seguem sem menu, ' +
    'como o tira-triangulo.gs deixou.');
}
