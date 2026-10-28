/** Cartões visíveis de uma cópia nova. Não executa r53Mostrar_/onEdit:
 * ambos gravam estado adicional fora do diário. Criação continua bloqueada.
 * Requer financeiro, validacoes, contrato_cartoes e EditorR53 confiáveis.
 */
function r53NovaCartContrato_(id) {
  if (typeof R53_NOVA_CARTOES_CONTRATO_ === 'undefined' || R53_NOVA_CARTOES_CONTRATO_.versao !== 1 ||
      typeof R53_EDITOR_ === 'undefined' || !Array.isArray(R53_EDITOR_.contextos)) r53NovaFinErro_('contrato de cartões indisponível.');
  var c = R53_NOVA_CARTOES_CONTRATO_, e = R53_EDITOR_;
  var identidade = [e.esquema, e.amparo, e.campos, e.defaults, e.contextos.map(function(g) {
    return [g.id,g.aba,g.area_editor];
  })];
  if (r53NovaFinHash_(identidade) !== c.editorHash) r53NovaFinErro_('editor fora do contrato de cartões.');
  if (typeof id !== 'string' || !Object.prototype.hasOwnProperty.call(c.contextos,id)) r53NovaFinErro_('cartão desconhecido.');
  var g = e.contextos.filter(function(x) { return x.id === id; })[0];
  if (!g || r53NovaFinHash_([g.id,g.aba,g.cel,g.classes,g.area_editor,g.entradas_diretas,g.menus_diretos,g.portas,g.funcoes_diretas,g.fixa,g.entidade]) !== c.contextos[id].editorHash)
    r53NovaFinErro_('editor fora do contrato de cartões.');
  return c.contextos[id];
}
function r53NovaCartAmparo_(ss, g) {
  var r = r53NovaFinFaixa_(ss,g.amparo), f = r.getFormulas()[0][0], v = r.getValues()[0][0];
  if (g.amparo.formulas.indexOf(r53NovaFinHash_(f)) < 0) r53NovaFinErro_('fórmula de Amparo desconhecida.');
  if (['Fechada','Livre','Neutra','Normal'].indexOf(v) < 0) r53NovaFinErro_('Amparo ainda não calculado ou desconhecido.');
  return v;
}
function r53NovaCartAberta_(g, d, amparo) {
  if (d.key !== 'dano' && g.zeroEspecial && g.classe === 0) return false;
  return d.porta === 'TRUE' || d.porta !== 'FALSE' && amparo !== 'Fechada';
}
function r53NovaCartRegra_(ss, g, d, aberta) {
  var tipo, args;
  if (g.fixa) { tipo = aberta ? 'CHECKBOX' : 'VALUE_IN_LIST'; args = aberta ? [] : [['—'],false]; }
  else { tipo = 'CUSTOM_FORMULA'; args = [r53Formula_(d.formula,ss)]; }
  return {tipo:tipo,argumentos:args,permiteInvalido:false,ajuda:''};
}
function r53NovaCartValidarRegra_(dv, g, d) {
  if (!dv || dv.ajuda || typeof dv.permiteInvalido !== 'boolean') r53NovaFinErro_('validação de função desconhecida.');
  var a = dv.argumentos;
  if (g.fixa) {
    if (dv.tipo === 'CHECKBOX' && a.length === 0) return;
    if (dv.tipo === 'VALUE_IN_LIST' && r53NovaFinCanon_(a) === '[["—"],false]') return;
  } else if (dv.tipo === 'CUSTOM_FORMULA' && a.length === 1 && d.variantes.indexOf(a[0]) >= 0) return;
  r53NovaFinErro_('validação de função desconhecida.');
}
function r53NovaCartPreservados_(ss, id, contratoConfiavel) {
  var g = contratoConfiavel || r53NovaCartContrato_(id), sh = ss.getSheetByName(g.aba);
  if (!sh) r53NovaFinErro_('falta a aba dos cartões.');
  var r = sh.getRange(g.leitura), p = r53Pos_(g.leitura.split(':')[0]), vs = r.getValues(), fs = r.getFormulas();
  g.guardas.forEach(function(x) {
    var a = r53Pos_(x.faixa), i = a[0]-p[0], j = a[1]-p[1];
    if (!vs[i] || !fs[i] || vs[i][j] === undefined || fs[i][j] === undefined) r53NovaFinErro_('leitura do cartão incompleta.');
    if (x.formulas ? x.formulas.indexOf(r53NovaFinHash_(fs[i][j])) < 0 : fs[i][j] || vs[i][j] !== x.valor)
      r53NovaFinErro_('rótulo ou fórmula protegida do cartão desconhecido.');
  });
  var preservados = g.entradas.map(function(x) {
    var cell = sh.getRange(x.faixa), dv = r53NovaValidLer_(cell), d = g.dinamicas[x.faixa];
    // A escrita é somente na âncora. Recusar uma mescla nova que a coloque
    // dentro de outra célula, em vez de apagar conteúdo alheio.
    cell.getMergedRanges().forEach(function(m) {
      var a = r53Pos_(x.faixa);
      if (m.getRow() !== a[0] || m.getColumn() !== a[1]) r53NovaFinErro_('entrada em interior de mescla desconhecida.');
    });
    if (d) { r53NovaCartValidarRegra_(dv,g,d); return [x.faixa,'dinamica']; }
    return [x.faixa,dv];
  });
  return r53NovaFinHash_([R53_NOVA_CARTOES_CONTRATO_.editorHash, g.guardas, preservados, r53NovaCartAmparo_(ss,g)]);
}
function r53NovaCartPerfil_(id) {
  var g = r53NovaCartContrato_(id);
  return {nome:'cartoes_'+id,diario:'r53_nova_ficha_cartoes_'+id+'_v1',limites:{escritasPorExecucao:4,orcamentoMs:210000},
    operacoes:function(ss) {
      var amparo = r53NovaCartAmparo_(ss,g), ops = [];
      g.entradas.forEach(function(x) {
        var d = g.dinamicas[x.faixa], aberta = d && r53NovaCartAberta_(g,d,amparo);
        if (d) ops.push({aba:g.aba,faixa:x.faixa,tipo:'validacao',regra:r53NovaCartRegra_(ss,g,d,aberta),formulasEquivalentes:d.variantes});
        ops.push({aba:g.aba,faixa:x.faixa,tipo:'valor',valor:d&&!aberta?'—':x.valor});
        ops.push({aba:g.aba,faixa:x.faixa,tipo:'nota',valor:x.nota});
      });
      return ops;
    },
    preservados:function(ss) { return r53NovaCartPreservados_(ss,id,g); },
    pendente:['demais_cartoes','montagens_e_memorias','entidades','arte','quota_e_orquestracao','automacoes_e_responsavel','conferencia_conjunta','prova_nativa']};
}
function r53NovaFichaCartaoPrevia(ss,ctx,id) {
  if (typeof R53_REF_CACHE_ !== 'undefined') R53_REF_CACHE_ = {};
  return r53NovaPerfilPrevia_(ss,ctx,r53NovaCartPerfil_(id));
}
function r53NovaFichaCartaoAplicar(ss,ctx,id,hash) {
  if (typeof R53_REF_CACHE_ !== 'undefined') R53_REF_CACHE_ = {};
  try { return r53NovaPerfilAplicar_(ss,ctx,hash,r53NovaCartPerfil_(id)); }
  finally { if (typeof R53_REF_CACHE_ !== 'undefined') R53_REF_CACHE_ = {}; }
}
