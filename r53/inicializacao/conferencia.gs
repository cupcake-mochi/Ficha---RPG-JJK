/** Leitura conjunta dos pós-estados dos perfis, NUNCA chama Aplicar/limpeza.
 * Checkpoint de leitura não é snapshot consistente, aprovação ou selo de criação.
 * Requer sequência v2 concluída, contexto confiável e código do mesmo produtor.
 */
var R53_NOVA_CONFERENCIA_={versao:1,diario:'r53_nova_ficha_conferencia_perfis_v1',orcamentoMs:180000};
function r53NovaConfSeq_(ss,ctx,assinatura){
  var dp=PropertiesService.getDocumentProperties(),v=r53NovaFinHash_(r53NovaFinContexto_(ss,ctx)),raw=dp.getProperty(R53_NOVA_SEQUENCIA_.diario);
  if(raw===null)r53NovaFinErro_('sequência atual ausente; não adotar fases avulsas.');
  var j=r53NovaSeqLer_(raw,v),plano=r53NovaSeqPlano_(j.recuperacoes);
  if(j.assinatura!==assinatura||assinatura!==r53NovaFinHash_([v,j.codigo,j.recuperacoes,j.inicioImagens])||
     j.codigo!==r53NovaSeqCodigo_(plano)||j.proxima!==plano.length||j.ativo!==null||j.financeiroProtecao===null||j.registrosRetrato===null||j.perfisRegistrados!==plano.filter(function(f){return f.tipo!=='imagens';}).length)
    r53NovaFinErro_('sequência atual ainda não terminou ou mudou.');
  var m=r53NovaMemInspecionar_();if(m.restantes||m.recuperacoes.length)
    r53NovaFinErro_('memórias pessoais reapareceram; não conferir como limpa.');
  if(r53NovaSeqRegistros_(dp,plano,j.vinculo,false).retrato!==j.registrosRetrato)
    r53NovaFinErro_('registros concluídos mudaram depois da sequência.');
  return {diario:j,hash:r53NovaFinHash_(j),perfis:plano.filter(function(f){return f.tipo!=='imagens';})};
}
function r53NovaConfPerfilLer_(ss,ctx,fase,sequencia){
  var p=r53NovaSeqPerfil_(fase),dp=PropertiesService.getDocumentProperties(),raw=dp.getProperty(p.diario),j;
  if(typeof raw!=='string'||r53NovaDiarioBytes_(raw)>9000)r53NovaFinErro_('registro do perfil ausente ou excessivo.');
  try{j=JSON.parse(raw);}catch(e){r53NovaFinErro_('registro do perfil ilegível.');}
  if(!j||typeof j!=='object'||Array.isArray(j))r53NovaFinErro_('registro do perfil inválido.');
  if(p.precondicao)p.precondicao(ss,ctx);
  var ops=p.operacoes(ss,ctx),vinculo=r53NovaFinContexto_(ss,ctx),hashes=['assinatura','layout','preservados','resultado','vinculo','integridade'];
  var meta,esperados;
  if(Object.prototype.hasOwnProperty.call(j,'recibo')){
    if(p.recibo!==true||j.recibo!==1||j.concluido!==true||Object.keys(j).sort().join(',')!=='assinatura,concluido,integridade,layout,preservados,recibo,resultado,vinculo'||
      hashes.some(function(k){return typeof j[k]!=='string'||!/^[a-f0-9]{64}$/.test(j[k]);}))r53NovaFinErro_('recibo do perfil inválido.');
    var base={recibo:j.recibo,concluido:j.concluido,assinatura:j.assinatura,vinculo:j.vinculo,layout:j.layout,preservados:j.preservados,resultado:j.resultado};
    if(j.integridade!==r53NovaFinHash_(base)||j.vinculo!==r53NovaReciboVinculo_(vinculo,p)||j.layout!==r53NovaFinHash_(ops))
      r53NovaFinErro_('recibo do perfil ou vínculo mudou.');
    meta=j;
  }else{
    var x=j.plano;
    if(Object.keys(j).sort().join(',')!=='assinatura,concluido,plano'||j.concluido!==true||!x||
       Object.keys(x).sort().join(',')!=='alteracoes,layout,passos,preservados,vinculo'||!Number.isInteger(x.alteracoes)||x.alteracoes<0||
       !Array.isArray(x.passos)||x.passos.length!==ops.length||x.alteracoes>x.passos.length||
       x.passos.some(function(t){return !t||Object.keys(t).sort().join(',')!=='antes,depois'||['antes','depois'].some(function(k){return typeof t[k]!=='string'||!/^[a-f0-9]{64}$/.test(t[k]);});})||
       ['layout','preservados'].some(function(k){return typeof x[k]!=='string'||!/^[a-f0-9]{64}$/.test(x[k]);})||
       j.assinatura!==r53NovaFinHash_(x)||r53NovaFinCanon_(x.vinculo)!==r53NovaFinCanon_(vinculo)||x.layout!==r53NovaFinHash_(ops))
      r53NovaFinErro_('diário do perfil incompleto, inválido ou de outra operação.');
    meta=x;esperados=x.passos.map(function(t){return t.depois;});
  }
  function guarda(){
    if(fase.tipo==='financeiro'){
      // Só o nível muda pela progressão; a projeção foi capturada ANTES do financeiro.
      if(!sequencia||sequencia.financeiroProtecao!==r53NovaFinProtecaoCompartilhada_(ss))
        r53NovaFinErro_('proteção financeira compartilhada mudou.');
    }else if(meta.preservados!==p.preservados(ss))r53NovaFinErro_('guarda do perfil mudou após a inicialização.');
  }
  guarda();
  var estados=ops.map(function(op,i){
    var atual=r53NovaFinLer_(ss,op),h=r53NovaFinHash_(atual),depois=r53NovaFinHash_(r53NovaFinDepois_(atual,op));
    if(h!==depois||esperados&&h!==esperados[i])r53NovaFinErro_('pós-estado do perfil diverge; nenhuma limpeza será repetida.');
    return h;
  });
  guarda();
  if(!esperados&&meta.resultado!==r53NovaFinHash_(estados))r53NovaFinErro_('resultado do recibo não corresponde ao estado atual.');
  if(dp.getProperty(p.diario)!==raw)r53NovaFinErro_('registro mudou durante a leitura do perfil.');
  return r53NovaFinHash_([p.nome,p.diario,r53NovaFinHash_(j),meta.layout,estados]);
}
function r53NovaConfSelar_(j){var c=JSON.parse(JSON.stringify(j));delete c.integridade;return r53NovaFinHash_(c);}
function r53NovaConfAssinatura_(s){return r53NovaFinHash_([R53_NOVA_CONFERENCIA_,s.hash,s.perfis]);}
function r53NovaFichaConferenciaPrevia(ss,ctx,assinaturaSequencia){
  var s=r53NovaConfSeq_(ss,ctx,assinaturaSequencia);
  if(PropertiesService.getDocumentProperties().getProperty(R53_NOVA_CONFERENCIA_.diario)!==null)r53NovaFinErro_('leitura conjunta já iniciada; retome a mesma.');
  return {assinatura:r53NovaConfAssinatura_(s),perfis:s.perfis.length,criacaoDisponivel:false};
}
function r53NovaFichaConferenciaLer(ss,ctx,assinaturaSequencia,assinatura){
  var inicio=Date.now(),lock=LockService.getDocumentLock();if(!lock.tryLock(1500))r53NovaFinErro_('outra operação em andamento.');
  try{
    if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};
    var s=r53NovaConfSeq_(ss,ctx,assinaturaSequencia),dp=PropertiesService.getDocumentProperties(),raw=dp.getProperty(R53_NOVA_CONFERENCIA_.diario),j,esperada=r53NovaConfAssinatura_(s);
    if(assinatura!==esperada)r53NovaFinErro_('assinatura da leitura conjunta mudou.');
    if(raw===null){
      j={versao:1,assinatura:assinatura,sequencia:s.hash,total:s.perfis.length,proxima:0,cadeia:r53NovaFinHash_(['conferencia_perfis_v1',s.hash])};
      j.integridade=r53NovaConfSelar_(j);r53NovaDiarioSalvar_(dp,R53_NOVA_CONFERENCIA_.diario,j);
    }else{
      try{j=JSON.parse(raw);}catch(e){r53NovaFinErro_('checkpoint da leitura ilegível.');}
      if(!j||Object.keys(j).sort().join(',')!=='assinatura,cadeia,integridade,proxima,sequencia,total,versao'||j.versao!==1||
        ['assinatura','cadeia','integridade','sequencia'].some(function(k){return typeof j[k]!=='string'||!/^[a-f0-9]{64}$/.test(j[k]);})||
        j.assinatura!==assinatura||j.sequencia!==s.hash||j.total!==s.perfis.length||!Number.isInteger(j.proxima)||j.proxima<0||j.proxima>j.total||j.integridade!==r53NovaConfSelar_(j))
        r53NovaFinErro_('checkpoint ou vínculo da leitura inválido; não reiniciar.');
    }
    if(j.proxima<j.total&&Date.now()-inicio<R53_NOVA_CONFERENCIA_.orcamentoMs){
      var h=r53NovaConfPerfilLer_(ss,ctx,s.perfis[j.proxima],s.diario);
      // Sem snapshot consistente. Confirmar ao menos que o coordenador não mudou.
      if(r53NovaConfSeq_(ss,ctx,assinaturaSequencia).hash!==s.hash)r53NovaFinErro_('sequência mudou durante a conferência.');
      if(Date.now()-inicio<R53_NOVA_CONFERENCIA_.orcamentoMs){
        j.cadeia=r53NovaFinHash_([j.cadeia,j.proxima,h]);j.proxima++;j.integridade=r53NovaConfSelar_(j);
        r53NovaDiarioSalvar_(dp,R53_NOVA_CONFERENCIA_.diario,j);
      }
    }
    return {leituraConcluida:j.proxima===j.total,retomar:j.proxima<j.total,perfisLidos:j.proxima,totalPerfis:j.total,
      retrataSomenteEstaRodada:true,consistenciaTemporalVerificada:false,imagensAtuaisConferidas:false,conferenciaConjuntaConcluida:false,criacaoDisponivel:false,
      pendente:['consistencia_temporal_e_arte_atual','quota_total_nativa','automacoes_treinos_notas_e_responsavel','integracao_drive_file_e_prova_nativa']};
  }finally{if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};lock.releaseLock();}
}
