/** Cópias sem acionadores: o fechamento vencido acontece na primeira edição
 * depois do vencimento. Com a conferência diária ativa neste projeto, não faz
 * nada (o diário já fecha). Só lê a data guardada; apura no máximo uma vez por
 * período, com o mesmo bloqueio e a mesma regra da conferência manual.
 */
function r53SalarioNaEdicao_(e) {
  try {
    if (PropertiesService.getScriptProperties().getProperty('salario_edicao') === ScriptApp.getScriptId()) return;
    var props = PropertiesService.getDocumentProperties(), proximo = Number(props.getProperty('salario_proximo'));
    var hoje = salarioHoje_();
    if (proximo && hoje < proximo) return;
    var ss = e && e.source || SpreadsheetApp.getActive();
    if (!salarioPronto_(ss)) return;
    var t0 = Date.now(), r = salarioSeguro_(ss, 1500);
    if (r && isFinite(r.proximo)) props.setProperty('salario_proximo', String(r.proximo));
    var valor = JSON.stringify({em: Date.now(), ms: Date.now() - t0, novos: r ? r.novos : null, proximo: r ? r.proximo : null});
    var meta = ss.getDeveloperMetadata().filter(function(m) { return m.getKey() === 'r53_salario_medicao'; })[0];
    if (meta) meta.setValue(valor); else ss.addDeveloperMetadata('r53_salario_medicao', valor);
  } catch (err) { console.log('salário na edição: ' + err.message); }
}
