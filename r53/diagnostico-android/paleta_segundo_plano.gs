/** Android: o app não dispara onSelectionChange, então a troca de cores parava
 * depois da CARTEIRA. A edição instalável (salarioRegistrarEdicao) agenda esta
 * continuação; ela roda como o proprietário, em trechos de até 25 s, e se
 * reagenda até a paleta pendente terminar. Só aparência; não toca em fórmulas.
 */
var PALETA_AGENDADA_ = 'paletaEmSegundoPlano';
function r53AgendarPaleta_(e) {
  try {
    if (!e || !e.range) return;
    var naEscolha = e.range.getSheet().getName() === 'CARTEIRA' && e.range.getA1Notation() === 'C27';
    if (!naEscolha && !PropertiesService.getDocumentProperties().getProperty('paleta_pendente')) return;
    r53GarantirPaletaAgendada_(20000);
  } catch (err) { console.log('paleta agendada: ' + err.message); }
}
function r53GarantirPaletaAgendada_(espera) {
  var ja = ScriptApp.getProjectTriggers().some(function(t) { return t.getHandlerFunction() === PALETA_AGENDADA_; });
  if (!ja) ScriptApp.newTrigger(PALETA_AGENDADA_).timeBased().after(espera).create();
}
function paletaEmSegundoPlano() {
  ScriptApp.getProjectTriggers().forEach(function(t) {
    if (t.getHandlerFunction() === PALETA_AGENDADA_) ScriptApp.deleteTrigger(t);
  });
  var props = PropertiesService.getDocumentProperties(), inicio = Date.now(), voltas = 0;
  while (props.getProperty('paleta_pendente') && Date.now() - inicio < 270000 && voltas < 40) {
    r53PaletaLeve_().continuar({r53Inicio_: Date.now()});
    voltas++;
    Utilities.sleep(500);
  }
  if (props.getProperty('paleta_pendente')) r53GarantirPaletaAgendada_(30000);
  console.log('paleta em segundo plano: ' + voltas + ' voltas, ' + (Date.now() - inicio) + ' ms');
}
