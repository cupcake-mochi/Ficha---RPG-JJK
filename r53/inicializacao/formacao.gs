/** Grau, Origem, treinos, técnica, Famílias e inventário de cópia nova. Sem integração no bot/pacote.
 * Requer financeiro.gs e contrato_formacao.gs confiáveis e da mesma versão.
 * Não concede treinos, aprova capacidades ou executa eventos de Caminho.
 */
function r53NovaFormContrato_(nome) {
  if (typeof R53_NOVA_FORMACAO_CONTRATO_ === 'undefined' || R53_NOVA_FORMACAO_CONTRATO_.versao !== 1 ||
      !Object.prototype.hasOwnProperty.call(R53_NOVA_FORMACAO_CONTRATO_.dominios, nome))
    r53NovaFinErro_('contrato de formação não disponível.');
  return R53_NOVA_FORMACAO_CONTRATO_.dominios[nome];
}
function r53NovaFormPos_(a) {
  var m = /^([A-Z]+)([0-9]+)(?::([A-Z]+)([0-9]+))?$/.exec(a);
  if (!m) r53NovaFinErro_('endereço de formação inválido.');
  var col = function(s) { var n = 0; for (var i = 0; i < s.length; i++) n = n * 26 + s.charCodeAt(i) - 64; return n; };
  return [Number(m[2]), col(m[1]), Number(m[4] || m[2]), col(m[3] || m[1])];
}
function r53NovaFormOperacoes_(nome) {
  var ops = [];
  r53NovaFormContrato_(nome).entradas.forEach(function(x) {
    ops.push({aba: x.aba, faixa: x.faixa, tipo: 'matriz', valores: x.valores,
              formulasLivres: x.tipo === 'formula', formulasEquivalentes: x.equivalentes});
    ops.push({aba: x.aba, faixa: x.faixa, tipo: 'notas_matriz', notas: x.notas});
  });
  (r53NovaFormContrato_(nome).somenteNotas || []).forEach(function(x) {
    ops.push({aba: x.aba, faixa: x.faixa, tipo: 'notas_matriz', notas: x.notas});
  });
  return ops;
}
function r53NovaFormPreservados_(ss, nome) {
  var c = r53NovaFormContrato_(nome), leituras = {};
  Object.keys(c.leituras).forEach(function(aba) {
    var sh = ss.getSheetByName(aba);
    if (!sh) r53NovaFinErro_('falta uma aba da formação.');
    var a = c.leituras[aba], r = sh.getRange(a);
    leituras[aba] = {pos: r53NovaFormPos_(a), valores: r.getValues(), formulas: r.getFormulas()};
  });
  function celula(aba, r, col, qual) {
    var l = leituras[aba], p = l && l.pos, dados = l && l[qual];
    if (!p || r < p[0] || r > p[2] || col < p[1] || col > p[3] ||
        !dados[r - p[0]] || dados[r - p[0]][col - p[1]] === undefined)
      r53NovaFinErro_('leitura de formação incompleta.');
    return dados[r - p[0]][col - p[1]];
  }
  var out = c.guardas.map(function(x) {
    var p = r53NovaFormPos_(x.faixa);
    return [x.aba, x.faixa, x.celulas.map(function(l, i) { return l.map(function(v, j) {
      var f = celula(x.aba, p[0] + i, p[1] + j, 'formulas');
      if (v.formulas) {
        if (v.formulas.indexOf(r53NovaFinHash_(f)) < 0) r53NovaFinErro_('fórmula protegida da formação não reconhecida.');
        return ['formula', v.formulas[0]];
      }
      if (f || celula(x.aba, p[0] + i, p[1] + j, 'valores') !== v.valor)
        r53NovaFinErro_('rótulo da formação não reconhecido.');
      return ['literal', v.valor];
    }); })];
  });
  c.entradas.forEach(function(x) {
    if (x.tipo !== 'formula') return;
    var p = r53NovaFormPos_(x.faixa);
    x.valores.forEach(function(l, i) { l.forEach(function(v, j) {
      var f = celula(x.aba, p[0] + i, p[1] + j, 'formulas');
      if (f && x.equivalentes[i][j].indexOf(f) < 0)
        r53NovaFinErro_('fórmula pessoal de formação não reconhecida.');
    }); });
  });
  return r53NovaFinHash_(out);
}
function r53NovaFormPerfil_(nome) {
  return {nome: nome, diario: 'r53_nova_ficha_formacao_' + nome + '_v1',
          limites: {escritasPorExecucao: 4, orcamentoMs: 210000},
          operacoes: function() { return r53NovaFormOperacoes_(nome); },
          preservados: function(ss) { return r53NovaFormPreservados_(ss, nome); },
          pendente: ['outros_dominios_da_copia', 'cartoes_e_sincronizacao_de_familias', 'notas_vivas_e_equipamento_das_entidades', 'entidades_e_cartoes',
                     'fotos_e_recuperacoes', 'automacoes_e_novo_responsavel', 'conferencia_conjunta', 'prova_nativa']};
}
function r53NovaFichaGrauOrigemPrevia(ss, ctx) { return r53NovaPerfilPrevia_(ss, ctx, r53NovaFormPerfil_('grau_origem')); }
function r53NovaFichaGrauOrigemAplicar(ss, ctx, hash) { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaFormPerfil_('grau_origem')); }
function r53NovaFichaPericiasPrevia(ss, ctx) { return r53NovaPerfilPrevia_(ss, ctx, r53NovaFormPerfil_('pericias')); }
function r53NovaFichaPericiasAplicar(ss, ctx, hash) { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaFormPerfil_('pericias')); }
function r53NovaFichaOficiosTRPrevia(ss, ctx) { return r53NovaPerfilPrevia_(ss, ctx, r53NovaFormPerfil_('oficios_tr')); }
function r53NovaFichaOficiosTRAplicar(ss, ctx, hash) { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaFormPerfil_('oficios_tr')); }
function r53NovaFichaArmasPrevia(ss, ctx) { return r53NovaPerfilPrevia_(ss, ctx, r53NovaFormPerfil_('armas')); }
function r53NovaFichaArmasAplicar(ss, ctx, hash) { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaFormPerfil_('armas')); }

function r53NovaFichaTecnicaPrevia(ss, ctx) { return r53NovaPerfilPrevia_(ss, ctx, r53NovaFormPerfil_('tecnica')); }
function r53NovaFichaTecnicaAplicar(ss, ctx, hash) { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaFormPerfil_('tecnica')); }
function r53NovaFichaFamiliasPrevia(ss, ctx) { return r53NovaPerfilPrevia_(ss, ctx, r53NovaFormPerfil_('familias')); }
function r53NovaFichaFamiliasAplicar(ss, ctx, hash) { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaFormPerfil_('familias')); }

function r53NovaFichaEquipadosPrevia(ss, ctx) { return r53NovaPerfilPrevia_(ss, ctx, r53NovaFormPerfil_('equipados')); }
function r53NovaFichaEquipadosAplicar(ss, ctx, hash) { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaFormPerfil_('equipados')); }
function r53NovaFichaEquipaveisPrevia(ss, ctx) { return r53NovaPerfilPrevia_(ss, ctx, r53NovaFormPerfil_('equipaveis')); }
function r53NovaFichaEquipaveisAplicar(ss, ctx, hash) { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaFormPerfil_('equipaveis')); }
function r53NovaFichaItensPrevia(ss, ctx) { return r53NovaPerfilPrevia_(ss, ctx, r53NovaFormPerfil_('itens')); }
function r53NovaFichaItensAplicar(ss, ctx, hash) { return r53NovaPerfilAplicar_(ss, ctx, hash, r53NovaFormPerfil_('itens')); }
