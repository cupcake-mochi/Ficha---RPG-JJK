/** Escolhas básicas e estado de cena de uma cópia nova.
 * Requer financeiro.gs e contrato_pessoal.gs do mesmo código confiável.
 * Sem endpoint/evento/pacote. Não inicializa personagem inteiro nem libera criação.
 */
function r53NovaPessoalContrato_(nome) {
  if (typeof R53_NOVA_PESSOAL_CONTRATO_ === 'undefined' || R53_NOVA_PESSOAL_CONTRATO_.versao !== 1 ||
      ['escolhas', 'recursos', 'condicoes'].indexOf(nome) < 0) r53NovaFinErro_('contrato pessoal não disponível.');
  return R53_NOVA_PESSOAL_CONTRATO_[nome];
}
function r53NovaPessoalOperacoes_(nome) {
  var ops = [];
  r53NovaPessoalContrato_(nome).campos.forEach(function(x) {
    ops.push({aba: 'FICHA', faixa: x.faixa, tipo: x.formula ? 'formula' : 'valor',
              valor: x.valor, formula: x.formula, formulasLivres: !!x.formula});
    // Restaurar instruções de fábrica nas entradas, sem deixar notas de outro
    // personagem. Não apagar a instrução de Sequelas extras, por exemplo.
    ops.push({aba: 'FICHA', faixa: x.faixa, tipo: 'nota', valor: x.nota});
  });
  return ops;
}
function r53NovaPessoalPreservados_(ss, nome) {
  var c = r53NovaPessoalContrato_(nome), sh = ss.getSheetByName('FICHA');
  if (!sh) r53NovaFinErro_('falta a FICHA.');
  // Faixa delimitada deste contrato: duas leituras em bloco, em vez de uma
  // consulta Google por rótulo/fórmula. Não guardar os dados entre chamadas.
  var r = sh.getRange('D10:AT70'), valores = r.getValues(), fs = r.getFormulas();
  function ler(a, matriz) {
    var m = /^([A-Z]+)([0-9]+)$/.exec(a), col = 0;
    if (!m) r53NovaFinErro_('endereço pessoal inválido.');
    for (var i = 0; i < m[1].length; i++) col = col * 26 + m[1].charCodeAt(i) - 64;
    var lin = Number(m[2]) - 10, cc = col - 4;
    if (lin < 0 || lin >= 61 || cc < 0 || cc >= 43 || !matriz[lin] || matriz[lin][cc] === undefined)
      r53NovaFinErro_('faixa pessoal incompleta.');
    return matriz[lin][cc];
  }
  var headers = Object.keys(c.cabecalhos).map(function(a) {
    var v = ler(a, valores);
    if (ler(a, fs) || v !== c.cabecalhos[a]) r53NovaFinErro_('rótulo pessoal fora do contrato.');
    return [a, v];
  });
  var formulas = c.formulas.map(function(x) {
    var f = ler(x.faixa, fs);
    if (x.hashes.indexOf(r53NovaFinHash_(f)) < 0)
      r53NovaFinErro_('fórmula pessoal protegida fora do contrato.');
    return [x.faixa, f];
  });
  c.campos.forEach(function(x) {
    if (!x.formula) return;
    var f = ler(x.faixa, fs);
    // Valores atuais podem ter virado números no jogo. Fórmula pessoal
    // diferente da ligação original ao máximo exige revisão; não apagá-la.
    if (f && f !== x.formula) r53NovaFinErro_('fórmula do recurso atual não reconhecida.');
  });
  return r53NovaFinHash_([headers, formulas]);
}
function r53NovaPessoalPerfil_(nome) {
  return {nome: nome === 'escolhas' ? 'escolhas_basicas' : nome === 'recursos' ? 'recursos_e_bonus' : 'condicoes_e_descanso',
          diario: 'r53_nova_ficha_' + nome + '_v1',
          limites: {escritasPorExecucao: 4, orcamentoMs: 210000},
          operacoes: function() { return r53NovaPessoalOperacoes_(nome); },
          preservados: function(ss) { return r53NovaPessoalPreservados_(ss, nome); },
          pendente: ['financeiro', 'identidade_e_imagens', 'nivel_e_base_xp',
                     'escolhas_recursos_e_condicoes_restantes',
                     'grau_treinos_e_origem_completos', 'inventario', 'entidades_e_cartoes',
                     'recuperacoes_e_automacoes', 'conferencia_conjunta', 'prova_nativa']};
}
function r53NovaFichaEscolhasPrevia(ss, contexto) {
  return r53NovaPerfilPrevia_(ss, contexto, r53NovaPessoalPerfil_('escolhas'));
}
function r53NovaFichaEscolhasAplicar(ss, contexto, assinatura) {
  return r53NovaPerfilAplicar_(ss, contexto, assinatura, r53NovaPessoalPerfil_('escolhas'));
}
function r53NovaFichaRecursosPrevia(ss, contexto) {
  return r53NovaPerfilPrevia_(ss, contexto, r53NovaPessoalPerfil_('recursos'));
}
function r53NovaFichaRecursosAplicar(ss, contexto, assinatura) {
  return r53NovaPerfilAplicar_(ss, contexto, assinatura, r53NovaPessoalPerfil_('recursos'));
}

function r53NovaFichaCondicoesPrevia(ss, contexto) {
  return r53NovaPerfilPrevia_(ss, contexto, r53NovaPessoalPerfil_('condicoes'));
}
function r53NovaFichaCondicoesAplicar(ss, contexto, assinatura) {
  return r53NovaPerfilAplicar_(ss, contexto, assinatura, r53NovaPessoalPerfil_('condicoes'));
}
