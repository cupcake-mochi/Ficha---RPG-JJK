/**
 * Só na CÓPIA de teste (26/10/2026): quanto custa cada leitura do caminho das missões logo depois de uma edição,
 * conforme ela seja a primeira ou não. Rodar medirLeiturasMissao() pelo editor. Cada rodada escreve uma missão em
 * AW15:AX15 (como o jogador), lê numa ordem e apaga; o resultado vai para a aba R53_MEDIDA_MISSAO.
 */
function medirLeiturasMissao() {
  var ss = SpreadsheetApp.getActive(), fp = ss.getSheetByName('FICHA PESSOAL'), reg = ss.getSheetByName('DADOS_SALARIOS');
  var leituras = {
    registros: function () { return reg.getRange('A2:G').getValues(); },
    literais: function () { return fp.getRange(15, 49, 73, 2).getValues(); },
    notas: function () { return fp.getRange(15, 49, 73, 24).getNotes(); },
    painel15: function () { return fp.getRange(15, 49, 73, 24).getValues(); },
    painel11: function () { return fp.getRange(11, 49, 77, 24).getValues(); },
    cabecalho: function () { return fp.getRange('AW11:BC11').getValues(); },
    dados: function () { return ss.getSheetByName('DADOS').getRange('AQ4:DP100').getValues(); }
  };
  var ordens = [
    ['registros', 'notas', 'painel11'],
    ['literais', 'notas', 'registros', 'cabecalho'],
    ['notas', 'literais', 'registros', 'cabecalho'],
    ['painel15', 'notas', 'registros', 'cabecalho'],
    ['cabecalho', 'literais', 'notas', 'registros'],
    ['registros', 'notas', 'painel11'],
    ['literais', 'notas', 'registros', 'cabecalho']
  ];
  var aba = ss.getSheetByName('R53_MEDIDA_MISSAO') || ss.insertSheet('R53_MEDIDA_MISSAO');
  var tipos = ['Curta', 'Longa'];
  ordens.forEach(function (ordem, k) {
    var t0 = Date.now(), marcas = [];
    fp.getRange('AW15:AX15').setValues([['Medida ' + k, tipos[k % 2]]]);
    SpreadsheetApp.flush();
    marcas.push('gravar+flush ' + (Date.now() - t0));
    ordem.forEach(function (n) { var t = Date.now(); leituras[n](); marcas.push(n + ' ' + (Date.now() - t)); });
    var t1 = Date.now();
    fp.getRange('AW15:AX15').clearContent();
    SpreadsheetApp.flush();
    marcas.push('apagar+flush ' + (Date.now() - t1));
    aba.appendRow([new Date(), k, marcas.join(' | ')]);
    Utilities.sleep(3000);
  });
}
