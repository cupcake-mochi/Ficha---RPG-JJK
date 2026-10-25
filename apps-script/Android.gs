/** Otimizações sem retirar campos do contrato ANALISE12/esquema2. */
function r53LiteralAnalise_(formula) {
  if (typeof formula !== 'string') return null;
  var match = /^="((?:[^"]|"")*)"$/.exec(formula);
  return match ? match[1].replace(/""/g, '"') : null;
}

/** Uma vez após a montagem: endereços fixos viram texto literal, não contas.
 * A recuperação de edições usa o mesmo literal em devolverConta_.
 * Não grava nas colunas A/B/D, nem em uma fórmula C que não seja constante.
 */
function otimizarAnaliseAndroid() {
  var ss = SpreadsheetApp.getActive(), sheet = ss.getSheetByName('ANALISE');
  if (!sheet) throw new Error('ANALISE ausente');
  var last = sheet.getLastRow();
  if (last < 2) return { convertidas: 0 };
  var formulas = sheet.getRange(2, 3, last - 1, 1).getFormulas();
  var values = sheet.getRange(2, 3, last - 1, 1).getValues();
  var count = 0, start = 0, rows = [];
  function flush() {
    if (!rows.length) return;
    sheet.getRange(start, 3, rows.length, 1).setRichTextValues(rows);
    count += rows.length;
    rows = [];
  }
  formulas.forEach(function (row, index) {
    var text = r53LiteralAnalise_(row[0]);
    if (text === null) { flush(); return; }
    if (values[index][0] !== text) throw new Error('Constante divergente: ANALISE!C' + (index + 2));
    if (!rows.length) start = index + 2;
    // O serviço consome um apóstrofo inicial mesmo em RichTextValue.
    // Dobre somente esse prefixo; o valor lido continuará exatamente igual.
    var escaped = text.charAt(0) === "'" ? "'" + text : text;
    rows.push([SpreadsheetApp.newRichTextValue().setText(escaped).build()]);
    if (rows.length === 500) flush();
  });
  flush();
  var result = { convertidas: count };
  console.log(JSON.stringify(result));
  return result;
}

/** Diagnóstico curto: não carrega o módulo de tabelas nem muda a paleta. */
function diagnosticarAndroid() {
  var ss=SpreadsheetApp.getActive(), props=PropertiesService.getDocumentProperties();
  var named=ss.getRangeByName('PALETA_ESCOLHIDA');
  var result={planilha:ss.getId(),paleta:named?named.getCell(1,1).getValue():null,
    pendente:props.getProperty('paleta_pendente'),atual:props.getProperty('paleta_atual'),
    feitos:props.getProperty('paleta_feito'),tempos:props.getProperty('paleta_tempos')};
  console.log(JSON.stringify(result));
  return result;
}
