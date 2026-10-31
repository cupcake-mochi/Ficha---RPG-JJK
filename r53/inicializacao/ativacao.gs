/** Protótipo interno: instala rotinas apenas na cópia e conta executantes.
 * Sem endpoint, reset financeiro ou atestado de identidade para as Guias.
 */
var R53_NOVA_ATIVACAO_ = {diario: 'r53_nova_ficha_ativacao_local_v1',
  nomes: ['r53NovaCopiaSalarioDiario', 'r53NovaCopiaSalarioEdicao', 'r53NovaCopiaSalarioAbrir']};
function r53NovaAtivacaoPreservados_(ss) {
  var celulas = r53NovaFinOperacoes_(ss).filter(function(op) { return op.tipo !== 'propriedade'; })
    .map(function(op) {
      var atual = r53NovaFinLer_(ss, op);
      if (r53NovaFinHash_(atual) !== r53NovaFinHash_(r53NovaFinDepois_(atual, op)))
        r53NovaFinErro_('a cópia já foi usada; não ativar automaticamente.');
      return r53NovaFinHash_(atual);
    });
  var outras = [PropertiesService.getDocumentProperties(), PropertiesService.getScriptProperties()]
    .map(function(p, i) {
      var d = p.getProperties();
      return Object.keys(d).sort().filter(function(k) {
        return !(i === 0 && k === R53_NOVA_ATIVACAO_.diario) && !(i === 1 && k === 'salario_edicao');
      }).map(function(k) { return [k, r53NovaFinHash_(d[k])]; });
    });
  return r53NovaFinHash_([r53NovaFinGuardas_(ss), celulas, outras]);
}
function r53NovaAtivacaoSalvar_(dp, j) {
  delete j.integridade;
  j.integridade = r53NovaFinHash_(j);
  r53NovaDiarioSalvar_(dp, R53_NOVA_ATIVACAO_.diario, j);
}
function r53NovaAtivacaoLista_(ss, j) {
  var lista = r53NovaPropsAcionadores_();
  if (lista.length !== j.ids.length) r53NovaFinErro_('rotina não registrada; revisão manual necessária, sem nova instalação.');
  var tipos = [ScriptApp.EventType.CLOCK, ScriptApp.EventType.ON_EDIT, ScriptApp.EventType.ON_OPEN];
  j.ids.forEach(function(id, i) {
    var encontrados = lista.filter(function(t) { return t.getUniqueId() === id; });
    if (encontrados.length !== 1) r53NovaFinErro_('rotina registrada ausente ou duplicada.');
    var t = encontrados[0];
    if (t.getHandlerFunction() !== R53_NOVA_ATIVACAO_.nomes[i] || t.getEventType() !== tipos[i] ||
        t.getTriggerSource() !== (i === 0 ? ScriptApp.TriggerSource.CLOCK : ScriptApp.TriggerSource.SPREADSHEETS) ||
        (i !== 0 && t.getTriggerSourceId() !== ss.getId()))
      r53NovaFinErro_('rotina incompatível; nada foi substituído.');
  });
}
function r53NovaFichaAtivacaoAplicar(ss, contexto) {
  var lock = LockService.getDocumentLock();
  if (!lock || !lock.tryLock(1000)) r53NovaFinErro_('outra inicialização está em andamento.');
  try {
    var vinculo = r53NovaFinHash_([r53NovaFinContexto_(ss, contexto), r53NovaPropsExecucao_()]);
    var dp = PropertiesService.getDocumentProperties(), sp = PropertiesService.getScriptProperties();
    var raw = dp.getProperty(R53_NOVA_ATIVACAO_.diario), j;
    if (!raw) {
      // Verificar o diário terminal original antes de criar o primeiro efeito.
      var propsRaw = dp.getProperty(R53_NOVA_PROPS_.diario), props;
      try { props = JSON.parse(propsRaw); } catch (e) { r53NovaFinErro_('propriedades ainda não preparadas.'); }
      if (!props || props.concluido !== true) r53NovaFinErro_('propriedades ainda não preparadas.');
      r53NovaPerfilAplicarTravado_(ss, contexto, props.assinatura, r53NovaPropsPerfil_(), Date.now());
      if (r53NovaPropsAcionadores_().length || sp.getProperty('salario_edicao') !== null)
        r53NovaFinErro_('cópia já possui rotinas ou marca de edição.');
      j = {versao: 1, vinculo: vinculo, preservados: r53NovaAtivacaoPreservados_(ss),
           ids: [], pendente: false, marcando: false, concluido: false};
      r53NovaAtivacaoSalvar_(dp, j);
    } else {
      try { j = JSON.parse(raw); } catch (e) { r53NovaFinErro_('diário de ativação inválido.'); }
      if (!j || j.versao !== 1 || !Array.isArray(j.ids) || j.ids.length > 3 ||
          j.ids.some(function(id) { return typeof id !== 'string' || !id || id.length > 200; }) ||
          typeof j.pendente !== 'boolean' || typeof j.marcando !== 'boolean' || typeof j.concluido !== 'boolean')
        r53NovaFinErro_('diário de ativação inválido.');
      var integridade = j.integridade; delete j.integridade;
      if (integridade !== r53NovaFinHash_(j) || j.vinculo !== vinculo)
        r53NovaFinErro_('diário ou execução diferente; não retomar.');
    }
    if (j.preservados !== r53NovaAtivacaoPreservados_(ss))
      r53NovaFinErro_('células ou propriedades mudaram; revisão manual necessária.');
    // Não adotar rotina encontrada após resposta perdida: horário do CLOCK não é inspecionável.
    if (j.pendente) r53NovaFinErro_('criação de rotina incerta; conferir manualmente, sem repetir.');
    r53NovaAtivacaoLista_(ss, j);
    var marca = sp.getProperty('salario_edicao'), projeto = ScriptApp.getScriptId();
    if (marca !== null && !(j.ids.length === 3 && (j.marcando || j.concluido) && marca === projeto))
      r53NovaFinErro_('marca de edição incompatível.');
    if (j.concluido) {
      if (marca !== projeto) r53NovaFinErro_('marca de edição removida após conclusão.');
    } else if (j.ids.length < 3) {
      // Um acionador por chamada. Diário persistido antes da criação não idempotente.
      j.pendente = true; r53NovaAtivacaoSalvar_(dp, j);
      var i = j.ids.length, builder = ScriptApp.newTrigger(R53_NOVA_ATIVACAO_.nomes[i]);
      var trigger = i === 0 ? builder.timeBased().everyDays(1).atHour(3).inTimezone('America/Sao_Paulo').create() :
        (i === 1 ? builder.forSpreadsheet(ss).onEdit().create() : builder.forSpreadsheet(ss).onOpen().create());
      var id = trigger.getUniqueId();
      if (typeof id !== 'string' || !id || id.length > 200) r53NovaFinErro_('identificador de rotina inválido.');
      j.ids.push(id); j.pendente = false; r53NovaAtivacaoSalvar_(dp, j);
      r53NovaAtivacaoLista_(ss, j);
    } else {
      j.marcando = true; r53NovaAtivacaoSalvar_(dp, j);
      sp.setProperty('salario_edicao', projeto);
      if (sp.getProperty('salario_edicao') !== projeto) r53NovaFinErro_('marca de edição não confirmada.');
      j.concluido = true; j.marcando = false; r53NovaAtivacaoSalvar_(dp, j);
    }
    if (j.preservados !== r53NovaAtivacaoPreservados_(ss))
      r53NovaFinErro_('preservação após ativação divergiu; revisar manualmente.');
    return {versao: 1, rotinasInstaladasNestaConta: j.ids.length, instalacaoLocalConcluida: j.concluido,
      retomar: !j.concluido, ativacaoConcluida: false, financeiroConcluido: false,
      criacaoDisponivel: false, responsavelVerificadoPeloBot: false,
      pendente: ['evento_real', 'outras_contas_nao_observadas', 'identidade_verificavel_pelo_backend', 'demais_dominios']};
  } finally { lock.releaseLock(); }
}

// Durante a instalação as rotinas próprias não executam efeitos salariais.
// Isso evita a edição instalável junto da edição simples antes da marca final.
function r53NovaAtivacaoEvento_(e, indice, executar) {
  if (!e || typeof e.triggerUid !== 'string') return;
  var dp = PropertiesService.getDocumentProperties(), j;
  try { j = JSON.parse(dp.getProperty(R53_NOVA_ATIVACAO_.diario)); } catch (err) { return; }
  if (!j || j.concluido !== true || j.pendente !== false || j.marcando !== false ||
      !Array.isArray(j.ids) || j.ids.length !== 3 || j.ids[indice] !== e.triggerUid ||
      PropertiesService.getScriptProperties().getProperty('salario_edicao') !== ScriptApp.getScriptId()) return;
  var integridade = j.integridade; delete j.integridade;
  if (integridade !== r53NovaFinHash_(j)) return;
  var ss = SpreadsheetApp.getActive();
  if (!ss || (indice !== 0 && (!e.source || e.source.getId() !== ss.getId()))) return;
  return executar(e);
}
function r53NovaCopiaSalarioDiario(e) { return r53NovaAtivacaoEvento_(e, 0, salarioDiario); }
function r53NovaCopiaSalarioEdicao(e) { return r53NovaAtivacaoEvento_(e, 1, salarioRegistrarEdicao); }
function r53NovaCopiaSalarioAbrir(e) { return r53NovaAtivacaoEvento_(e, 2, salarioAposAbrir); }
