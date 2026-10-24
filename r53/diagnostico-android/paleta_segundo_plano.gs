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
    PropertiesService.getDocumentProperties().setProperty('paleta_agendada_em', String(Date.now()));
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
  r53GravarMedicaoPaleta_({inicioExecucao: inicio, voltas: voltas, duracaoMs: Date.now() - inicio});
  console.log('paleta em segundo plano: ' + voltas + ' voltas, ' + (Date.now() - inicio) + ' ms');
}
/** Cartões e salários encerram a edição antes do módulo: com troca pendente,
 * avança um trecho da paleta também nessas edições (cópias sem acionadores). */
function r53ContinuarPaletaPendente_(e) {
  try {
    if (PropertiesService.getDocumentProperties().getProperty('paleta_pendente')) r53PaletaLeve_().continuar(e);
  } catch (err) { console.log('paleta pendente: ' + err.message); }
}
/** Medição legível pela API (metadados do desenvolvedor, invisíveis na ficha). */
function r53GravarMedicaoPaleta_(extra) {
  try {
    var p = PropertiesService.getDocumentProperties().getProperties(), ss = SpreadsheetApp.getActive();
    var execucoes = [];
    var meta = ss.getDeveloperMetadata().filter(function(m) { return m.getKey() === 'r53_paleta_medicao'; })[0];
    try { execucoes = JSON.parse(meta.getValue()).execucoes || []; } catch (err) {}
    execucoes.push(extra);
    var valor = JSON.stringify({em: Date.now(), agendadaEm: Number(p.paleta_agendada_em) || null,
      pendente: p.paleta_pendente || null, ultima: p.paleta_ultima_troca || null,
      tempos: p.paleta_tempos || null, execucoes: execucoes.slice(-12)});
    if (meta) meta.setValue(valor); else ss.addDeveloperMetadata('r53_paleta_medicao', valor);
  } catch (err) { console.log('medição: ' + err.message); }
}
