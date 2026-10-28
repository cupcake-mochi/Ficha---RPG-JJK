/** Versões guardadas em MONTAGENS de uma cópia nova, isolada e não registrada.
 * Uma prévia/diário por cartão. Não limpa o cartão visível, entidades ou caches
 * persistentes. Não executar o editor entre os domínios da inicialização.
 * Requer financeiro.gs, contrato_montagens.gs e EditorR53 confiáveis.
 */
function r53NovaMontContrato_(id) {
  if (typeof R53_NOVA_MONTAGENS_CONTRATO_ === 'undefined' || R53_NOVA_MONTAGENS_CONTRATO_.versao !== 1 ||
      typeof R53_EDITOR_ === 'undefined' || !Array.isArray(R53_EDITOR_.contextos))
    r53NovaFinErro_('contrato de MONTAGENS não disponível.');
  var c = R53_NOVA_MONTAGENS_CONTRATO_, e = R53_EDITOR_;
  var identidade = [e.esquema, e.storage, e.campos, Object.keys(e.defaults).sort().map(function(k) { return [k, e.defaults[k]]; }), e.contextos.map(function(g) {
    return [g.id, g.aba, g.cel.nome, g.editor, g.classes];
  })];
  if (r53NovaFinHash_(identidade) !== c.editorHash)
    r53NovaFinErro_('editor fora do contrato de MONTAGENS.');
  if (typeof id !== 'string' || !Object.prototype.hasOwnProperty.call(c.contextos, id))
    r53NovaFinErro_('cartão desconhecido; nenhum endereço livre é aceito.');
  return c;
}
function r53NovaMontPreservados_(ss, id) {
  var c = r53NovaMontContrato_(id), g = c.contextos[id], sh = ss.getSheetByName('MONTAGENS');
  if (!sh) r53NovaFinErro_('falta a aba MONTAGENS.');
  var r = sh.getRange(g.leitura), vs = r.getValues(), fs = r.getFormulas();
  var alvo = sh.getRange(g.faixa), dv = alvo.getDataValidations();
  if (!Array.isArray(dv) || dv.length !== 33 || dv.some(function(l) {
    return !Array.isArray(l) || l.length !== g.classes.length || l.some(function(v) { return v !== null; });
  }) || alvo.getMergedRanges().length)
    r53NovaFinErro_('validação ou mescla inesperada em MONTAGENS.');
  function cel(i, j, esperado) {
    if (!vs[i] || !fs[i] || vs[i][j] === undefined || fs[i][j] === undefined)
      r53NovaFinErro_('leitura de MONTAGENS incompleta.');
    if (esperado.formulas) {
      if (esperado.formulas.indexOf(r53NovaFinHash_(fs[i][j])) < 0)
        r53NovaFinErro_('fórmula protegida de MONTAGENS não reconhecida.');
    } else if (fs[i][j] || vs[i][j] !== esperado.valor)
      r53NovaFinErro_('rótulo de MONTAGENS não reconhecido.');
  }
  cel(0, 0, g.titulo);
  g.cabecalho.forEach(function(v, j) { cel(1, j, v); });
  c.campos.forEach(function(v, i) { cel(i + 2, 0, {valor: v[1]}); });
  // Resultados calculados (nome e Classe máxima) podem mudar ao limpar outros
  // domínios. A proteção compara a fórmula exata, não o resultado do cálculo.
  return r53NovaFinHash_([c.editorHash, g.titulo, g.cabecalho]);
}
function r53NovaMontPerfil_(id) {
  var c = r53NovaMontContrato_(id), g = c.contextos[id];
  return {nome: 'montagens_' + id, diario: 'r53_nova_ficha_montagens_' + id + '_v1',
    limites: {escritasPorExecucao: 4, orcamentoMs: 210000},
    operacoes: function() {
      return [{aba: 'MONTAGENS', faixa: g.faixa, tipo: 'matriz', valores: c.campos.map(function(campo) {
        return g.classes.map(function() { return c.defaults[campo[0]]; });
      })}, {aba: 'MONTAGENS', faixa: g.faixa, tipo: 'notas_matriz', notas: c.campos.map(function() {
        return g.classes.map(function() { return ''; });
      })}];
    },
    preservados: function(ss) { return r53NovaMontPreservados_(ss, id); },
    pendente: ['demais_cartoes_montagens', 'cartoes_visiveis_e_validacoes', 'entidades', 'memorias_e_recuperacoes',
               'arte', 'automacoes_e_novo_responsavel', 'conferencia_conjunta', 'prova_nativa']};
}
function r53NovaFichaMontagensPrevia(ss, ctx, id) {
  return r53NovaPerfilPrevia_(ss, ctx, r53NovaMontPerfil_(id));
}
function r53NovaFichaMontagensAplicar(ss, ctx, id, hash) {
  try { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaMontPerfil_(id)); }
  finally { if (typeof R53_REF_CACHE_ !== 'undefined') R53_REF_CACHE_ = {}; }
}
