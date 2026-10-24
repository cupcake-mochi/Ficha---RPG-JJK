/** Execução manual única, pelo proprietário, numa cópia candidata.
 * Usa a ativação idempotente já existente (diário, edição e abertura) e
 * registra o diagnóstico de leitura antes e depois. Não reemite créditos,
 * não apaga históricos, não executa construir/continuar.
 */
function prepararCopiaAndroid() {
  var antes = auditarContextoAndroid();
  var ativacao = ativarSalarioDiario();
  var depois = auditarContextoAndroid();
  var resumo = {projeto: depois.projeto, planilha: depois.planilha, ativacao: ativacao,
    acionadoresAntes: (antes.acionadores || []).map(function(t) { return t.funcao; }),
    acionadoresDepois: (depois.acionadores || []).map(function(t) { return t.funcao + ':' + t.evento; }),
    agendaApontaEsteProjeto: depois.salarios && depois.salarios.agendaApontaEsteProjeto,
    edicaoMarcada: depois.salarios && depois.salarios.edicaoInstalavelMarcadaNesteProjeto};
  console.log('RESUMO ' + JSON.stringify(resumo));
  return resumo;
}
