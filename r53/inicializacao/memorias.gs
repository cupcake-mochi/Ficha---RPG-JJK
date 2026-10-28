/** Estado pessoal do editor de uma CÓPIA NOVA, isolada e não registrada.
 * Não limpa MONTAGENS, não altera script/user properties, não executa eventos.
 * Requer financeiro.gs, contrato_memorias.gs e EditorR53 confiáveis.
 * Grupos fixos + uma recuperação por diário evitam manifestos dinâmicos que
 * perderiam os alvos após a primeira exclusão. Criação permanece bloqueada.
 */
function r53NovaMemContrato_() {
  if (typeof R53_NOVA_MEMORIAS_CONTRATO_ === 'undefined' || R53_NOVA_MEMORIAS_CONTRATO_.versao !== 1 ||
      typeof R53_EDITOR_ === 'undefined' || !Array.isArray(R53_EDITOR_.contextos))
    r53NovaFinErro_('contrato de memórias não disponível.');
  var c = R53_NOVA_MEMORIAS_CONTRATO_;
  if (r53NovaFinHash_([R53_EDITOR_.storage, R53_EDITOR_.contextos.map(function(g) { return [g.id, g.classes]; })]) !== c.editorHash)
    r53NovaFinErro_('editor fora do contrato de memórias.');
  return c;
}
function r53NovaMemInspecionar_() {
  var c = r53NovaMemContrato_(), keys = PropertiesService.getDocumentProperties().getKeys();
  var recuperacoes = [], restantes = 0;
  keys.forEach(function(k) {
    if (c.chaves.indexOf(k) >= 0) { restantes++; return; }
    if (/^r53_recuperacao_[1-9][0-9]{12}$/.test(k)) { recuperacoes.push(k); return; }
    // Não tratar um futuro formato, nome parecido ou contexto desconhecido
    // como autorização para apagá-lo. Nunca incluir seu nome/valor no erro.
    if (/^r53_(recuperacao_|classe_visivel_)/.test(k))
      r53NovaFinErro_('memória pessoal desconhecida; revisar o produtor antes de continuar.');
  });
  return {grupos: Math.ceil(c.chaves.length / c.porGrupo), restantes: restantes,
          recuperacoes: recuperacoes.sort(), criacaoDisponivel: false};
}
function r53NovaFichaMemoriasInspecionar(ss, ctx) {
  r53NovaFinContexto_(ss, ctx);
  return r53NovaMemInspecionar_();
}
function r53NovaMemPerfil_(grupo, recuperacao) {
  var c = r53NovaMemContrato_(), chaves, nome;
  if (recuperacao !== undefined) {
    if (typeof recuperacao !== 'string' || !/^r53_recuperacao_[1-9][0-9]{12}$/.test(recuperacao))
      r53NovaFinErro_('identificador de recuperação inválido.');
    chaves = [recuperacao]; nome = 'recuperacao_' + recuperacao.slice('r53_recuperacao_'.length);
  } else {
    if (!Number.isInteger(grupo) || grupo < 0 || grupo >= Math.ceil(c.chaves.length / c.porGrupo))
      r53NovaFinErro_('grupo de memórias inválido.');
    chaves = c.chaves.slice(grupo * c.porGrupo, (grupo + 1) * c.porGrupo); nome = 'memorias_' + grupo;
  }
  var diario = 'r53_nova_ficha_' + nome + '_v1';
  return {nome: nome, diario: diario, limites: {escritasPorExecucao: 4, orcamentoMs: 210000},
    precondicao: function() {
      r53NovaMemInspecionar_();
      if (recuperacao !== undefined) {
        var p = PropertiesService.getDocumentProperties();
        if (p.getProperty(recuperacao) === null && p.getProperty(diario) === null)
          r53NovaFinErro_('recuperação ausente; não iniciar um diário vazio.');
      }
    },
    operacoes: function() { return chaves.map(function(k) { return {tipo: 'propriedade', escopo: 'documento', chave: k}; }); },
    preservados: function() { r53NovaMemInspecionar_(); return c.editorHash; },
    pendente: ['demais_grupos_e_recuperacoes', 'celulas_e_montagens', 'fotos', 'automacoes_e_notas_vivas',
               'novo_responsavel', 'conferencia_conjunta', 'prova_nativa']};
}
function r53NovaFichaMemoriasPrevia(ss, ctx, grupo) {
  return r53NovaPerfilPrevia_(ss, ctx, r53NovaMemPerfil_(grupo));
}
function r53NovaFichaMemoriasAplicar(ss, ctx, grupo, hash) {
  try { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaMemPerfil_(grupo)); }
  finally { if (typeof R53_REF_CACHE_ !== 'undefined') R53_REF_CACHE_ = {}; }
}
function r53NovaFichaRecuperacaoPrevia(ss, ctx, recuperacao) {
  return r53NovaPerfilPrevia_(ss, ctx, r53NovaMemPerfil_(null, recuperacao));
}
function r53NovaFichaRecuperacaoAplicar(ss, ctx, recuperacao, hash) {
  try { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaMemPerfil_(null, recuperacao)); }
  finally { if (typeof R53_REF_CACHE_ !== 'undefined') R53_REF_CACHE_ = {}; }
}
