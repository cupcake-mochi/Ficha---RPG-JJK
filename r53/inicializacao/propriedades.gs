/** Propriedades financeiras após a limpeza REST; protótipo interno, sem publicação.
 * Não grava células, não cria/remove acionadores e não atesta identidade ao bot.
 * O contexto continua exclusivo do integrador confiável, nunca JSON do cliente.
 */
var R53_NOVA_PROPS_ = {
  versao: 1, diario: 'r53_nova_ficha_propriedades_financeiras_v1',
  escritasPorExecucao: 4, orcamentoMs: 210000
};
function r53NovaPropsExecucao_() {
  var projeto = ScriptApp.getScriptId(), usuario = Session.getTemporaryActiveUserKey();
  if (typeof projeto !== 'string' || !/^[A-Za-z0-9_-]{16,200}$/.test(projeto) ||
      typeof usuario !== 'string' || !usuario || usuario.length > 512)
    r53NovaFinErro_('não foi possível vincular projeto e execução atual.');
  // Chave temporária não é identidade Google nem autorização. Só vincula a retomada.
  return r53NovaFinHash_(['propriedades_execucao_v1', projeto, usuario]);
}
function r53NovaPropsAcionadores_() {
  var lista = ScriptApp.getProjectTriggers();
  if (!Array.isArray(lista)) r53NovaFinErro_('não foi possível conferir as rotinas desta conta.');
  return lista;
}
function r53NovaPropsPrecondicao_(ss, contexto) {
  r53NovaPropsExecucao_();
  if (r53NovaPropsAcionadores_().length !== 0)
    r53NovaFinErro_('há rotinas visíveis desta conta; não limpar propriedades de uma cópia em uso.');
}
function r53NovaPropsOperacoes_(ss) {
  // Mesma lista fechada do financeiro; não aceitar chaves do chamador.
  return r53NovaFinOperacoes_(ss).filter(function(op) { return op.tipo === 'propriedade'; });
}
function r53NovaPropsPreservados_(ss) {
  var celulas = r53NovaFinOperacoes_(ss).filter(function(op) { return op.tipo !== 'propriedade'; })
    .map(function(op) {
      var atual = r53NovaFinLer_(ss, op), h = r53NovaFinHash_(atual);
      if (h !== r53NovaFinHash_(r53NovaFinDepois_(atual, op)))
        r53NovaFinErro_('as células financeiras ainda não estão limpas; não tratar propriedades.');
      return h;
    });
  var outras = [['documento', PropertiesService.getDocumentProperties(), R53_NOVA_FIN_.propriedadesDocumento],
                ['script', PropertiesService.getScriptProperties(), R53_NOVA_FIN_.propriedadesScript]]
    .map(function(item) {
      var todos = item[1].getProperties();
      if (!todos || typeof todos !== 'object' || Array.isArray(todos))
        r53NovaFinErro_('armazenamento de propriedades incompatível.');
      return [item[0], Object.keys(todos).sort().filter(function(k) {
        return item[2].indexOf(k) < 0 && !(item[0] === 'documento' && k === R53_NOVA_PROPS_.diario);
      }).map(function(k) {
        if (typeof todos[k] !== 'string') r53NovaFinErro_('propriedade não textual.');
        return [k, r53NovaFinHash_(todos[k])];
      })];
    });
  return r53NovaFinHash_([r53NovaPropsExecucao_(), r53NovaFinGuardas_(ss), celulas, outras]);
}
function r53NovaPropsPerfil_() {
  return {nome: 'propriedades_financeiras', diario: R53_NOVA_PROPS_.diario, limites: R53_NOVA_PROPS_,
    precondicao: r53NovaPropsPrecondicao_, operacoes: r53NovaPropsOperacoes_, preservados: r53NovaPropsPreservados_,
    pendente: ['ativacao_pelo_responsavel', 'identidade_verificavel_pelo_backend', 'demais_dominios',
               'conferencia_conjunta', 'prova_nativa']};
}
function r53NovaFichaPropriedadesPrevia(ss, contexto) {
  return r53NovaPerfilPrevia_(ss, contexto, r53NovaPropsPerfil_());
}
function r53NovaFichaPropriedadesAplicar(ss, contexto, assinatura) {
  var r = r53NovaPerfilAplicar_(ss, contexto, assinatura, r53NovaPropsPerfil_());
  r.propriedadesPreparadas = r.concluido === true;
  r.ativacaoConcluida = false; r.financeiroConcluido = false;
  r.responsavelVerificadoPeloBot = false;
  return r;
}
/** Inspeção, não ativação. Vê somente os acionadores da conta executante.
 * Nem três acionadores compatíveis provam horário, outras contas ou evento real.
 */
function r53NovaFichaAtivacaoConferir(ss, contexto) {
  r53NovaFinContexto_(ss, contexto); r53NovaPropsExecucao_();
  var projeto = ScriptApp.getScriptId(), lista = r53NovaPropsAcionadores_();
  var esperados = {salarioDiario: [ScriptApp.EventType.CLOCK, ScriptApp.TriggerSource.CLOCK],
    salarioRegistrarEdicao: [ScriptApp.EventType.ON_EDIT, ScriptApp.TriggerSource.SPREADSHEETS],
    salarioAposAbrir: [ScriptApp.EventType.ON_OPEN, ScriptApp.TriggerSource.SPREADSHEETS]};
  var vistos = {}, compativeis = true;
  lista.forEach(function(t) {
    var nome = t.getHandlerFunction(), e = Object.prototype.hasOwnProperty.call(esperados, nome) ? esperados[nome] : null;
    if (!e) { compativeis = false; return; }
    vistos[nome] = (vistos[nome] || 0) + 1;
    if (vistos[nome] > 1 || t.getEventType() !== e[0] || t.getTriggerSource() !== e[1] ||
        (nome !== 'salarioDiario' && t.getTriggerSourceId() !== ss.getId())) compativeis = false;
  });
  var marca = PropertiesService.getScriptProperties().getProperty('salario_edicao');
  var completo = compativeis && lista.length === 3 && Object.keys(esperados).every(function(k) { return vistos[k] === 1; });
  return {versao: 1, rotinasVisiveis: lista.length, rotinasVisiveisCompativeis: completo,
    marcaDoProjetoAtual: marca === projeto, marcaAusente: marca === null,
    ativacaoConcluida: false, financeiroConcluido: false, criacaoDisponivel: false,
    responsavelVerificadoPeloBot: false,
    pendente: ['horario_e_evento_real', 'outras_contas_nao_observadas', 'identidade_verificavel_pelo_backend',
               'demais_dominios', 'conferencia_conjunta', 'prova_nativa']};
}
