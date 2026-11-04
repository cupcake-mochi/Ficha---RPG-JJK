/** Páginas somente de leitura para o integrador conferir versões Drive fora do
 * Apps Script. Sem Drive/UrlFetch, escrita de célula ou checkpoint no documento.
 * O integrador precisa cercar PLANO e CADA PÁGINA com observações autenticadas.
 * Não é endpoint publicado, autorização de cliente, snapshot de cálculos ou selo.
 */
var R53_NOVA_CONFERENCIA_PAGINAS_={protocolo:'carteira-conferencia-pagina-1',porPagina:4,limitePerfis:631,orcamentoMs:180000};
function r53NovaConfPagPlano_(ss,ctx,assinaturaSequencia){
  var s=r53NovaConfSeq_(ss,ctx,assinaturaSequencia),c=R53_NOVA_CONFERENCIA_PAGINAS_;
  if(!s.perfis.length||s.perfis.length>c.limitePerfis)r53NovaFinErro_('perfis fora do limite das páginas.');
  return {sequencia:s,assinatura:r53NovaFinHash_([c,s.hash,s.perfis]),paginas:Math.ceil(s.perfis.length/c.porPagina)};
}
function r53NovaConfPagRetorno_(p){
  return {protocolo:R53_NOVA_CONFERENCIA_PAGINAS_.protocolo,assinatura:p.assinatura,sequencia:p.sequencia.hash,
    perfis:p.sequencia.perfis.length,porPagina:R53_NOVA_CONFERENCIA_PAGINAS_.porPagina,paginas:p.paginas,
    criacaoDisponivel:false,conferenciaConjuntaConcluida:false,imagensAtuaisConferidas:false,consistenciaTemporalVerificada:false};
}
function r53NovaFichaConferenciaPlano(ss,ctx,assinaturaSequencia){
  var lock=LockService.getDocumentLock();if(!lock.tryLock(1500))r53NovaFinErro_('outra operação em andamento.');
  try{
    if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};
    return r53NovaConfPagRetorno_(r53NovaConfPagPlano_(ss,ctx,assinaturaSequencia));
  }finally{if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};lock.releaseLock();}
}
function r53NovaFichaConferenciaPagina(ss,ctx,assinaturaSequencia,assinatura,pagina){
  var inicio=Date.now(),lock=LockService.getDocumentLock();if(!lock.tryLock(1500))r53NovaFinErro_('outra operação em andamento.');
  try{
    if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};
    var p=r53NovaConfPagPlano_(ss,ctx,assinaturaSequencia),c=R53_NOVA_CONFERENCIA_PAGINAS_;
    if(assinatura!==p.assinatura||!Number.isInteger(pagina)||pagina<0||pagina>=p.paginas)
      r53NovaFinErro_('página ou assinatura inválida; nenhum endereço livre é aceito.');
    var fases=p.sequencia.perfis.slice(pagina*c.porPagina,(pagina+1)*c.porPagina),estados=[];
    fases.forEach(function(f){
      if(Date.now()-inicio>=c.orcamentoMs)r53NovaFinErro_('prazo da página esgotado; repita somente a leitura.');
      if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};
      estados.push(r53NovaConfPerfilLer_(ss,ctx,f,p.sequencia.diario));
    });
    if(r53NovaConfPagPlano_(ss,ctx,assinaturaSequencia).assinatura!==p.assinatura)
      r53NovaFinErro_('sequência ou registros mudaram durante a página.');
    if(Date.now()-inicio>=c.orcamentoMs)r53NovaFinErro_('prazo da página esgotado; resultado não confirmado.');
    var out=r53NovaConfPagRetorno_(p);out.pagina=pagina;out.lidos=estados.length;
    out.estado=r53NovaFinHash_([p.assinatura,pagina,estados]);return out;
  }finally{if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};lock.releaseLock();}
}
