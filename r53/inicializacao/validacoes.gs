/** Adaptador de validações para o executor. Descritores vêm do produtor,
 * nunca do navegador. Somente caixa padrão, lista e fórmula são graváveis.
 */
function r53NovaValidLer_(r) {
  var dv = r.getDataValidation();
  if (!dv) return null;
  var tipo = String(dv.getCriteriaType()), args = dv.getCriteriaValues();
  function valor(v) {
    if (Array.isArray(v)) return v.map(valor);
    if (v && typeof v.getA1Notation === 'function')
      return {aba: v.getSheet().getName(), faixa: v.getA1Notation(), documento: v.getSheet().getParent().getId()};
    if (Object.prototype.toString.call(v) === '[object Date]') return {data: v.toISOString()};
    if (v === null || ['string', 'boolean', 'number'].indexOf(typeof v) >= 0) return v;
    r53NovaFinErro_('argumento de validação não reconhecido.');
  }
  args = args.map(valor);
  // Checkbox padrão pode vir sem argumentos ou com o par booleano explícito.
  if (tipo === 'CHECKBOX' && (args.length === 0 || args.length === 2 && args[0] === true && args[1] === false)) args = [];
  return {tipo: tipo, argumentos: args, permiteInvalido: dv.getAllowInvalid(), ajuda: dv.getHelpText() || ''};
}
function r53NovaValidGravar_(r, d) {
  var b = SpreadsheetApp.newDataValidation();
  if (d.tipo === 'CHECKBOX' && d.argumentos.length === 0) b.requireCheckbox();
  else if (d.tipo === 'VALUE_IN_LIST' && d.argumentos.length === 2 && Array.isArray(d.argumentos[0]) && typeof d.argumentos[1] === 'boolean')
    b.requireValueInList(d.argumentos[0], d.argumentos[1]);
  else if (d.tipo === 'CUSTOM_FORMULA' && d.argumentos.length === 1 && typeof d.argumentos[0] === 'string')
    b.requireFormulaSatisfied(d.argumentos[0]);
  else r53NovaFinErro_('validação de destino não suportada.');
  b.setAllowInvalid(d.permiteInvalido);
  if (d.ajuda) b.setHelpText(d.ajuda);
  r.setDataValidation(b.build());
}
