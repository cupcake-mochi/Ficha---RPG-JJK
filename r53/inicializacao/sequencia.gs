/** Sequência fixa dos protótipos; sem menu, endpoint, emissão ou criação liberada.
 * Contexto só do integrador confiável. Cópia nova isolada até conferência geral.
 * Uma chamada trabalha em UMA fase; mantém a mesma trava durante filho e cursor.
 */
var R53_NOVA_SEQUENCIA_={versao:2,diario:'r53_nova_ficha_sequencia_v2',limiteRecuperacoes:32};
function r53NovaSeqRecuperacoes_(lista){
  if(!Array.isArray(lista)||lista.length>R53_NOVA_SEQUENCIA_.limiteRecuperacoes||lista.some(function(k,i){
    return typeof k!=='string'||!/^r53_recuperacao_[1-9][0-9]{12}$/.test(k)||i>0&&lista[i-1]>=k;
  }))r53NovaFinErro_('lista de recuperações da sequência inválida.');
  return lista;
}
function r53NovaSeqPlano_(recuperacoes){
  r53NovaSeqRecuperacoes_(recuperacoes);
  var m=r53NovaMemContrato_(),mont=R53_NOVA_MONTAGENS_CONTRATO_,cart=R53_NOVA_CARTOES_CONTRATO_,ent=R53_NOVA_ENTIDADES_CONTRATO_;
  if(!mont||mont.versao!==1||!cart||cart.versao!==1||!ent||ent.versao!==1)
    r53NovaFinErro_('faltam contratos da sequência.');
  var ids=Object.keys(mont.contextos).sort(),out=[];
  if(ids.length!==249||r53NovaFinCanon_(ids)!==r53NovaFinCanon_(Object.keys(cart.contextos).sort())||Object.keys(ent.dominios).length!==73)
    r53NovaFinErro_('domínios da sequência fora do contrato.');
  function add(tipo,id){out.push({tipo:tipo,id:id||''});}
  add('imagens','antes');add('fotos');add('financeiro');add('progressao');add('identidade');add('pessoal','escolhas');
  ['grau_origem','pericias','oficios_tr','armas','tecnica','familias','equipados','equipaveis','itens','carteira'].forEach(function(k){r53NovaFormContrato_(k);add('formacao',k);});
  add('pessoal','condicoes');
  Object.keys(ent.dominios).sort().forEach(function(k){add('entidade',k);});
  ids.forEach(function(k){add('montagens',k);});
  // Classe 0 compartilha linhas: a guarda de um cartão lê entradas do seguinte.
  // Limpar de baixo para cima mantém as guardas, sem adotar dados do vizinho.
  ids.slice().sort(function(a,b){return /^classe0\.[1-5]$/.test(a)&&/^classe0\.[1-5]$/.test(b)?Number(b.split('.')[1])-Number(a.split('.')[1]):a<b?-1:a>b?1:0;})
    .forEach(function(k){add('cartao',k);});
  for(var i=0;i<Math.ceil(m.chaves.length/m.porGrupo);i++)add('memorias',String(i));
  recuperacoes.forEach(function(k){add('recuperacao',k);});
  add('pessoal','recursos');add('imagens','depois');
  if(out.length!==601+recuperacoes.length)r53NovaFinErro_('quantidade de fases incompatível.');
  return out;
}
function r53NovaSeqPerfil_(fase){
  switch(fase.tipo){
    case 'fotos':return r53NovaArtePerfil_();case 'financeiro':return r53NovaFinPerfil_();
    case 'progressao':return r53NovaProgPerfil_();case 'identidade':return r53NovaIdentPerfil_();
    case 'pessoal':return r53NovaPessoalPerfil_(fase.id);case 'formacao':return r53NovaFormPerfil_(fase.id);
    case 'entidade':return r53NovaEntPerfil_(fase.id);case 'montagens':return r53NovaMontPerfil_(fase.id);
    case 'cartao':return r53NovaCartPerfil_(fase.id);case 'memorias':return r53NovaMemPerfil_(Number(fase.id));
    case 'recuperacao':return r53NovaMemPerfil_(null,fase.id);
  }
  r53NovaFinErro_('fase de escrita desconhecida.');
}
// Chaves fixas dos registros; não cria nem interpreta plano fornecido pelo cliente.
function r53NovaSeqChave_(f){
  if(f.tipo==='financeiro')return R53_NOVA_FIN_.diario;
  if(f.tipo==='progressao')return R53_NOVA_PROG_.diario;
  if(f.tipo==='identidade')return R53_NOVA_IDENT_.diario;
  if(f.tipo==='fotos')return 'r53_nova_ficha_fotos_ancoras_v1';
  var prefixos={pessoal:'',formacao:'formacao_',entidade:'entidades_',montagens:'montagens_',cartao:'cartoes_',memorias:'memorias_'};
  if(Object.prototype.hasOwnProperty.call(prefixos,f.tipo))return 'r53_nova_ficha_'+prefixos[f.tipo]+f.id+'_v1';
  if(f.tipo==='recuperacao')return 'r53_nova_ficha_recuperacao_'+f.id.slice('r53_recuperacao_'.length)+'_v1';
  r53NovaFinErro_('fase sem registro conhecido.');
}
function r53NovaSeqRaizRegistros_(vinculo){return r53NovaFinHash_(['registros_perfis_v2',vinculo]);}
// Uma projeção compacta evita reconstruir centenas de elos em cada página da leitura.
// O encadeamento completo é conferido ao fechar a sequência; depois, compara-se o retrato.
function r53NovaSeqRegistros_(dp,plano,vinculo,conferirCadeia){
  var dados=dp.getProperties(),lista=[],cadeia=r53NovaSeqRaizRegistros_(vinculo),n=0;
  plano.forEach(function(f){if(f.tipo==='imagens')return;var k=r53NovaSeqChave_(f),raw=dados[k];
    if(typeof raw!=='string'||raw.length>9000)r53NovaFinErro_('registro concluído do perfil ausente ou excessivo.');
    lista.push([k,raw]);if(conferirCadeia)cadeia=r53NovaFinHash_([cadeia,n++,r53NovaFinHash_(raw)]);
  });
  return {retrato:r53NovaFinHash_(lista),cadeia:conferirCadeia?cadeia:null};
}
function r53NovaSeqCodigo_(plano){
  // Contratos são código confiável do produtor, não dados recebidos do browser.
  // A versão precisa subir se mudar a semântica da sequência/executor sem mudar contratos.
  return r53NovaFinHash_([R53_NOVA_SEQUENCIA_,plano,R53_NOVA_FIN_,R53_NOVA_PROG_,R53_NOVA_IDENT_,
    R53_NOVA_PESSOAL_CONTRATO_,R53_NOVA_FORMACAO_CONTRATO_,R53_NOVA_ENTIDADES_CONTRATO_,
    R53_NOVA_MONTAGENS_CONTRATO_,R53_NOVA_CARTOES_CONTRATO_,R53_NOVA_MEMORIAS_CONTRATO_,R53_NOVA_ARTE_CONTRATO_,R53_NOVO_INVENTARIO_IMAGENS_]);
}
function r53NovaSeqSelar_(j){var x=JSON.parse(JSON.stringify(j));delete x.integridade;return r53NovaFinHash_(x);}
function r53NovaSeqSalvar_(dp,j){j.integridade=r53NovaSeqSelar_(j);r53NovaDiarioSalvar_(dp,R53_NOVA_SEQUENCIA_.diario,j);}
function r53NovaSeqLer_(raw,vinculo){
  var j;try{j=JSON.parse(raw);}catch(e){r53NovaFinErro_('diário da sequência ilegível.');}
  var keys=['assinatura','ativo','codigo','financeiroProtecao','inicioImagens','integridade','perfisRegistrados','proxima','recuperacoes','registrosCadeia','registrosRetrato','versao','vinculo'];
  if(!j||Object.keys(j).sort().join(',')!==keys.join(',')||j.versao!==2||j.vinculo!==vinculo||
    ['assinatura','codigo','inicioImagens','integridade','registrosCadeia','vinculo'].some(function(k){return typeof j[k]!=='string'||!/^[a-f0-9]{64}$/.test(j[k]);})||
    j.registrosRetrato!==null&&(typeof j.registrosRetrato!=='string'||!/^[a-f0-9]{64}$/.test(j.registrosRetrato))||
    j.financeiroProtecao!==null&&(typeof j.financeiroProtecao!=='string'||!/^[a-f0-9]{64}$/.test(j.financeiroProtecao))||
    !Number.isInteger(j.perfisRegistrados)||j.perfisRegistrados<0||!Number.isInteger(j.proxima)||j.proxima<0||j.ativo!==null&&(!j.ativo||Object.keys(j.ativo).join(',')!=='assinatura'||typeof j.ativo.assinatura!=='string'||!/^[a-f0-9]{64}$/.test(j.ativo.assinatura))||
    j.integridade!==r53NovaSeqSelar_(j))r53NovaFinErro_('diário ou vínculo da sequência inválido; não reiniciar.');
  r53NovaSeqRecuperacoes_(j.recuperacoes);return j;
}
function r53NovaSeqRecuperacoesConferir_(j){
  var atual=r53NovaMemInspecionar_().recuperacoes;
  if(atual.some(function(k){return j.recuperacoes.indexOf(k)<0;}))
    r53NovaFinErro_('nova recuperação surgiu durante a sequência; revisão necessária.');
}
function r53NovaSeqPrevia_(ss,ctx){
  var vinculo=r53NovaFinHash_(r53NovaFinContexto_(ss,ctx)),dp=PropertiesService.getDocumentProperties();
  if(dp.getKeys().some(function(k){return /^r53_nova_ficha_/.test(k);}))
    r53NovaFinErro_('há fases anteriores nesta cópia; não iniciar sequência nova.');
  var recuperacoes=r53NovaMemInspecionar_().recuperacoes;r53NovaSeqRecuperacoes_(recuperacoes);
  var plano=r53NovaSeqPlano_(recuperacoes),codigo=r53NovaSeqCodigo_(plano);
  // Medir a estrutura antes de gravar o coordenador; a primeira fase segue sem escrita de célula.
  var inicioImagens=r53NovaFichaImagensPrevia(ss,ctx,'antes').assinatura;
  return {versao:2,vinculo:vinculo,codigo:codigo,inicioImagens:inicioImagens,recuperacoes:recuperacoes,plano:plano,
    assinatura:r53NovaFinHash_([vinculo,codigo,recuperacoes,inicioImagens])};
}
function r53NovaFichaSequenciaPrevia(ss,ctx){
  var p=r53NovaSeqPrevia_(ss,ctx);
  return {assinatura:p.assinatura,fases:p.plano.length,recuperacoes:p.recuperacoes.length,criacaoDisponivel:false};
}
function r53NovaSeqRetorno_(j,plano){
  return {fasesPercorridas:j.proxima===plano.length,retomar:j.proxima<plano.length,
    fasesConcluidas:j.proxima,totalFases:plano.length,fase:j.proxima<plano.length?plano[j.proxima].tipo:'aguarda_conferencia_conjunta',
    conferenciaConjuntaConcluida:false,criacaoDisponivel:false,
    pendente:['conferencia_conjunta_e_consistencia_temporal','autenticidade_da_arte','quota_total_nativa',
      'automacoes_treinos_e_notas','novo_responsavel','integracao_drive_file_e_prova_nativa']};
}
function r53NovaFichaSequenciaAplicar(ss,ctx,assinatura){
  var inicio=Date.now(),lock=LockService.getDocumentLock();if(!lock.tryLock(1500))r53NovaFinErro_('outra operação em andamento.');
  try{
    var vinculo=r53NovaFinHash_(r53NovaFinContexto_(ss,ctx)),dp=PropertiesService.getDocumentProperties(),raw=dp.getProperty(R53_NOVA_SEQUENCIA_.diario),j,plano;
    if(raw!==null){
      j=r53NovaSeqLer_(raw,vinculo);plano=r53NovaSeqPlano_(j.recuperacoes);
      if(j.assinatura!==assinatura||j.assinatura!==r53NovaFinHash_([vinculo,j.codigo,j.recuperacoes,j.inicioImagens])||j.codigo!==r53NovaSeqCodigo_(plano)||
        j.proxima>plano.length||j.perfisRegistrados!==plano.slice(0,j.proxima).filter(function(f){return f.tipo!=='imagens';}).length||j.proxima===plano.length&&(j.ativo!==null||j.registrosRetrato===null)||j.proxima<plano.length&&j.registrosRetrato!==null)r53NovaFinErro_('sequência, operação ou contrato mudou; não reiniciar.');
    }else{
      var p=r53NovaSeqPrevia_(ss,ctx);if(p.assinatura!==assinatura)r53NovaFinErro_('a sequência mudou após a prévia.');
      plano=p.plano;j={versao:2,vinculo:vinculo,codigo:p.codigo,inicioImagens:p.inicioImagens,assinatura:assinatura,recuperacoes:p.recuperacoes,proxima:0,ativo:null,financeiroProtecao:null,perfisRegistrados:0,registrosCadeia:r53NovaSeqRaizRegistros_(vinculo),registrosRetrato:null};
      r53NovaSeqSalvar_(dp,j);
    }
    r53NovaSeqRecuperacoesConferir_(j);
    if(j.proxima===plano.length)return r53NovaSeqRetorno_(j,plano);
    var fase=plano[j.proxima],perfil,hash;
    if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};
    if(fase.tipo!=='imagens'){perfil=r53NovaSeqPerfil_(fase);if(perfil.diario!==r53NovaSeqChave_(fase))r53NovaFinErro_('chave do perfil fora do contrato.');}
    if(j.ativo===null){
      if(fase.tipo==='financeiro')j.financeiroProtecao=r53NovaFinProtecaoCompartilhada_(ss);
      hash=fase.tipo==='imagens'?r53NovaFichaImagensPrevia(ss,ctx,fase.id).assinatura:r53NovaPerfilPrevia_(ss,ctx,perfil).assinatura;
      if(j.proxima===0&&hash!==j.inicioImagens)r53NovaFinErro_('estrutura mudou antes da primeira inspeção.');
      j.ativo={assinatura:hash};r53NovaSeqSalvar_(dp,j);
      // Prévia e aplicação em chamadas separadas: não duplicar leituras caras no mesmo prazo.
      return r53NovaSeqRetorno_(j,plano);
    }
    if(fase.tipo==='financeiro'&&j.financeiroProtecao===null)r53NovaFinErro_('proteção financeira da sequência ausente.');
    // Assinatura durável antes do filho. Se cair depois do filho, retoma o mesmo filho.
    var resultado=fase.tipo==='imagens'?r53NovaInvImagemInspecionarTravado_(ss,ctx,fase.id,j.ativo.assinatura,inicio):
      r53NovaPerfilAplicarTravado_(ss,ctx,j.ativo.assinatura,perfil,inicio);
    if(fase.tipo==='imagens'&&resultado.leituraConcluida){
      var c=resultado.contagem;
      if(c.fora||c.indeterminadas||c.decoracoesAusentes||resultado.sobrepostas||resultado.desenhos||fase.id==='depois'&&c.fotos)
        r53NovaFinErro_('a inspeção de arte exige revisão; nenhuma outra fase será iniciada.');
    }
    if(fase.tipo==='imagens'?resultado.leituraConcluida:resultado.concluido){
      if(fase.tipo!=='imagens'){
        var filho=dp.getProperty(perfil.diario);if(typeof filho!=='string')r53NovaFinErro_('registro concluído do filho ausente.');
        j.registrosCadeia=r53NovaFinHash_([j.registrosCadeia,j.perfisRegistrados,r53NovaFinHash_(filho)]);j.perfisRegistrados++;
      }
      j.proxima++;j.ativo=null;
      if(j.proxima===plano.length){
        var registros=r53NovaSeqRegistros_(dp,plano,j.vinculo,true);
        if(registros.cadeia!==j.registrosCadeia)r53NovaFinErro_('registros concluídos mudaram durante a sequência.');
        j.registrosRetrato=registros.retrato;
      }
      r53NovaSeqSalvar_(dp,j);
    }
    return r53NovaSeqRetorno_(j,plano);
  }finally{if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};lock.releaseLock();}
}
