/** Fotos nas 13 caixas conhecidas + espelho pessoal de cópia nova isolada.
 * Não buscar URL, baixar imagem, remover sobreposição/desenho ou repintar.
 * Requer financeiro/formacao/validacoes/contrato_arte confiáveis.
 * Não oferece prova global de ausência de dados pessoais fora das âncoras.
 */
function r53NovaArteContrato_() {
  if(typeof R53_NOVA_ARTE_CONTRATO_==='undefined'||R53_NOVA_ARTE_CONTRATO_.versao!==1||R53_NOVA_ARTE_CONTRATO_.campos.length!==14)
    r53NovaFinErro_('contrato de fotos indisponível.');
  return R53_NOVA_ARTE_CONTRATO_;
}
function r53NovaArteFormula_(f) {
  if(typeof f!=='string'||!/^=IMAGE\(/i.test(f))return false;
  var texto=false,n=0;
  for(var i=7;i<f.length;i++) {
    var c=f.charAt(i);
    if(c==='"'){if(texto&&f.charAt(i+1)==='"'){i++;continue;}texto=!texto;}
    if(!texto){if(c==='(')n++;if(c===')'){if(n===0)return i===f.length-1;n--;}}
  }
  return false;
}
function r53NovaArteLer_(ss,op) {
  var r=r53NovaFinFaixa_(ss,op),f=r.getFormulas()[0][0];
  if(f) {
    if(f!==op.formulaDestino&&!r53NovaArteFormula_(f))r53NovaFinErro_('fórmula de foto desconhecida; revisão necessária.');
    return {tipo:'formula',hash:r53NovaFinHash_(f)};
  }
  var v=r.getValue();
  if(typeof v==='string')return {tipo:'texto',valor:v};
  if(!v||!SpreadsheetApp.ValueType||v.valueType!==SpreadsheetApp.ValueType.IMAGE)
    r53NovaFinErro_('valor da foto desconhecido; nada será apagado.');
  // URL é credencial temporária. Usar só dentro do hash, sem logs/retornos ou
  // PropertiesService. Não tomar alt text como identidade do conteúdo.
  try {
    var url=v.getContentUrl(),titulo=v.getAltTextTitle(),descricao=v.getAltTextDescription();
    if(typeof url!=='string'||!/^https:\/\//.test(url)||typeof titulo!=='string'||typeof descricao!=='string')throw new Error();
    return {tipo:'imagem',hash:r53NovaFinHash_([url,titulo,descricao])};
  } catch(err) {r53NovaFinErro_('não foi possível identificar a foto; revisão necessária.');}
}
function r53NovaArteDepois_(op) {
  return op.formulaDestino?{tipo:'formula',hash:r53NovaFinHash_(op.formulaDestino)}:{tipo:'texto',valor:op.valor};
}
function r53NovaArtePreservados_(ss) {
  var c=r53NovaArteContrato_(),abas=ss.getSheets();
  if(!Array.isArray(abas)||!abas.length||abas.length>c.limiteAbas)r53NovaFinErro_('abas fora do limite da inspeção de fotos.');
  var nomes=abas.map(function(sh){
    // O construtor usa arte em célula. Sobreposições/desenhos podem ser
    // pessoais ou decoração custom: não há autorização por posição/título.
    var imagens,desenhos;
    try {imagens=sh.getImages();desenhos=sh.getDrawings();}
    catch(err){r53NovaFinErro_('não foi possível inspecionar imagens soltas/desenhos.');}
    if(!Array.isArray(imagens)||!Array.isArray(desenhos))r53NovaFinErro_('inspeção de imagens/desenhos incompleta.');
    if(imagens.length||desenhos.length)r53NovaFinErro_('imagem sobreposta ou desenho exige revisão separada.');
    return sh.getName();
  }).sort();
  var guardas=c.campos.map(function(x){
    var sh=ss.getSheetByName(x.aba);if(!sh)r53NovaFinErro_('falta uma aba de fotos.');
    if(sh.getRange(x.guarda.faixa).getFormula()||sh.getRange(x.guarda.faixa).getValue()!==x.guarda.valor)
      r53NovaFinErro_('layout de fotos desconhecido.');
    var r=sh.getRange(x.faixa),m=r.getMergedRanges().map(function(v){return [v.getRow(),v.getColumn(),v.getLastRow(),v.getLastColumn()];});
    if(r53NovaFinCanon_(m)!==r53NovaFinCanon_(x.mesclas))r53NovaFinErro_('mescla da foto fora do contrato.');
    var dv=r53NovaValidLer_(r);if(dv!==null)r53NovaFinErro_('validação inesperada na foto.');
    return [x.aba,x.faixa,x.mesclas,x.guarda];
  });
  return r53NovaFinHash_([nomes,guardas]);
}
function r53NovaArtePerfil_() {
  var c=r53NovaArteContrato_();
  return {recibo:true,nome:'fotos_ancoras',diario:'r53_nova_ficha_fotos_ancoras_v1',limites:{escritasPorExecucao:4,orcamentoMs:210000},
    operacoes:function(){var ops=[];c.campos.forEach(function(x){ops.push({tipo:'foto',aba:x.aba,faixa:x.faixa,valor:x.valor,formulaDestino:x.formulaDestino});ops.push({tipo:'nota',aba:x.aba,faixa:x.faixa,valor:x.nota});});return ops;},
    preservados:r53NovaArtePreservados_,pendente:['imagens_fora_das_ancoras','decoracao_custom_e_desenhos','orquestracao','automacoes_e_responsavel','conferencia_conjunta','prova_nativa']};
}
function r53NovaFichaFotosPrevia(ss,ctx) {return r53NovaPerfilPrevia_(ss,ctx,r53NovaArtePerfil_());}
function r53NovaFichaFotosAplicar(ss,ctx,hash) {return r53NovaPerfilAplicar_(ss,ctx,hash,r53NovaArtePerfil_());}
