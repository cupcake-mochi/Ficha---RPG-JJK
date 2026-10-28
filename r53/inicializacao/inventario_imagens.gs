/** Inventário paginado, sem alteração de células/imagens. Só grava progresso.
 * Não é snapshot consistente, prova de pixels, autorização ou selo de criação.
 * Requer financeiro/arte/contrato_arte confiáveis. Antes/depois são rodadas fixas.
 */
var R53_NOVO_INVENTARIO_IMAGENS_={versao:1,celulasPorPagina:4096,colunasPorBloco:64,
  paginasPorExecucao:4,orcamentoMs:180000,limiteAbas:50,limiteCelulas:3000000,limitePaginas:4096,amostraMaxima:8};
function r53NovaInvImagemFase_(fase){
  if(fase!=='antes'&&fase!=='depois')r53NovaFinErro_('rodada de imagens desconhecida.');
  return 'r53_nova_ficha_inventario_imagens_'+fase+'_v1';
}
function r53NovaInvImagemPlano_(ss,ctx,fase){
  r53NovaInvImagemFase_(fase);
  var vinculo=r53NovaFinContexto_(ss,ctx),lim=R53_NOVO_INVENTARIO_IMAGENS_,c=r53NovaArteContrato_(),abas,lista=[],paginas=[],total=0;
  try{abas=ss.getSheets();}catch(e){r53NovaFinErro_('não foi possível medir as abas da inspeção.');}
  if(!Array.isArray(abas)||!abas.length||abas.length>lim.limiteAbas)r53NovaFinErro_('abas fora do limite da inspeção.');
  abas.forEach(function(sh){
    var id,nome,nr,nc,imgs,draw;
    try{id=sh.getSheetId();nome=sh.getName();nr=sh.getMaxRows();nc=sh.getMaxColumns();imgs=sh.getImages();draw=sh.getDrawings();}
    catch(e){r53NovaFinErro_('não foi possível medir a grade ou os objetos da inspeção.');}
    if(!Number.isInteger(id)||id<0||typeof nome!=='string'||!nome||!Number.isInteger(nr)||nr<1||!Number.isInteger(nc)||nc<1||
       !Array.isArray(imgs)||!Array.isArray(draw)||lista.some(function(s){return s.id===id||s.nome===nome;}))
      r53NovaFinErro_('metadados de inspeção inválidos.');
    total+=nr*nc;if(total>lim.limiteCelulas)r53NovaFinErro_('grade excede o limite da inspeção; nada será truncado.');
    lista.push({id:id,nome:nome,linhas:nr,colunas:nc,sobrepostas:imgs.length,desenhos:draw.length,sh:sh});
  });
  lista.sort(function(a,b){return a.id-b.id;});
  // Fotos e decorações conhecidas precisam caber; não aceitar aba ausente como zero imagens.
  c.campos.concat(c.decoracoes).forEach(function(x){
    var s=lista.filter(function(a){return a.nome===x.aba;})[0],p=/^([A-Z]+)([0-9]+)$/.exec(x.faixa),col=0;
    for(var i=0;p&&i<p[1].length;i++)col=col*26+p[1].charCodeAt(i)-64;
    if(!s||!p||Number(p[2])>s.linhas||col>s.colunas)r53NovaFinErro_('âncora conhecida fora da grade inventariada.');
  });
  lista.forEach(function(s){for(var col=1;col<=s.colunas;col+=lim.colunasPorBloco){
    var nc=Math.min(lim.colunasPorBloco,s.colunas-col+1),altura=Math.floor(lim.celulasPorPagina/nc);
    for(var r=1;r<=s.linhas;r+=altura){paginas.push({id:s.id,aba:s.nome,sh:s.sh,linha:r,coluna:col,linhas:Math.min(altura,s.linhas-r+1),colunas:nc});if(paginas.length>lim.limitePaginas)r53NovaFinErro_('páginas excedem o limite da inspeção; nada será truncado.');}
  }});
  var layout=r53NovaFinHash_([lim,c,lista.map(function(s){return [s.id,s.nome,s.linhas,s.colunas,s.sobrepostas,s.desenhos];})]);
  return {vinculo:r53NovaFinHash_([vinculo,fase]),layout:layout,paginas:paginas,celulas:total,
    sobrepostas:lista.reduce(function(n,s){return n+s.sobrepostas;},0),desenhos:lista.reduce(function(n,s){return n+s.desenhos;},0)};
}
function r53NovaInvImagemFormula_(f){
  if(typeof f!=='string'||f.charAt(0)!=='=')return false;
  var aspas='',out='';
  for(var i=0;i<f.length;i++){
    var ch=f.charAt(i);
    if(aspas){if(ch===aspas){if(f.charAt(i+1)===aspas){i++;continue;}aspas='';}out+=' ';}
    else if(ch==='"'||ch==="'"){aspas=ch;out+=' ';}else out+=ch;
  }
  return /\bIMAGE\s*\(/i.test(out);
}
function r53NovaInvImagemLer_(p){
  var vs,fs;
  try{var range=p.sh.getRange(p.linha,p.coluna,p.linhas,p.colunas);vs=range.getValues();fs=range.getFormulas();}
  catch(e){r53NovaFinErro_('não foi possível ler a página de imagens; progresso mantido.');}
  if(!Array.isArray(vs)||!Array.isArray(fs)||vs.length!==p.linhas||fs.length!==p.linhas)
    r53NovaFinErro_('página de imagens incompleta.');
  var c=r53NovaArteContrato_(),fotos={},decoracoes={},marcas=[],n={celulas:0,fotos:0,decoracoesMarcadas:0,decoracoesAusentes:0,fora:0,indeterminadas:0,formulasImagem:0},amostra=[];
  function apontar(r,col,tipo){marcas.push([r,col,tipo]);if(amostra.length<R53_NOVO_INVENTARIO_IMAGENS_.amostraMaxima)amostra.push({abaId:p.id,linha:r,coluna:col,tipo:tipo});}
  function coord(a){var m=/^([A-Z]+)([0-9]+)$/.exec(a),col=0;for(var i=0;i<m[1].length;i++)col=col*26+m[1].charCodeAt(i)-64;return [Number(m[2]),col];}
  c.campos.forEach(function(x){if(x.aba===p.aba)fotos[coord(x.faixa).join(',')]=true;});
  c.decoracoes.forEach(function(x){if(x.aba===p.aba)decoracoes[coord(x.faixa).join(',')]=x;});
  for(var i=0;i<p.linhas;i++){
    if(!Array.isArray(vs[i])||!Array.isArray(fs[i])||vs[i].length!==p.colunas||fs[i].length!==p.colunas)
      r53NovaFinErro_('linha da inspeção de imagens incompleta.');
    for(var j=0;j<p.colunas;j++){
      var v=vs[i][j],f=fs[i][j],r=p.linha+i,col=p.coluna+j;
      if(typeof f!=='string')r53NovaFinErro_('fórmula da inspeção ilegível.');
      n.celulas++;
      var foto=fotos[r+','+col]===true,dec=decoracoes[r+','+col];
      var imagem=false,incerta=false,titulo;
      if(v&&typeof v==='object'){
        try{if(Object.prototype.toString.call(v)!=='[object Date]'){imagem=!!SpreadsheetApp.ValueType&&v.valueType===SpreadsheetApp.ValueType.IMAGE;if(!imagem)incerta=true;}}
        catch(e){incerta=true;}
      }
      var formula=r53NovaInvImagemFormula_(f);if(formula)n.formulasImagem++;
      if(incerta){n.indeterminadas++;apontar(r,col,'objeto_ilegivel');continue;}
      if(imagem||formula){
        if(foto){n.fotos++;marcas.push([r,col,'foto']);}
        else if(dec&&imagem&&!f){
          try{titulo=v.getAltTextTitle();}catch(e){titulo=null;}
          if(titulo==='PM-ARTE:'+dec.arquivo){n.decoracoesMarcadas++;marcas.push([r,col,'decoracao_marcada']);}
          else{n.fora++;apontar(r,col,'decoracao_nao_reconhecida');}
        }else{n.fora++;apontar(r,col,'imagem_fora_das_fotos');}
      }else if(dec){n.decoracoesAusentes++;apontar(r,col,'decoracao_ausente');}
    }
  }
  return {contagem:n,amostra:amostra,hash:r53NovaFinHash_(marcas)};
}
function r53NovaInvImagemSelar_(j){var x=JSON.parse(JSON.stringify(j));delete x.integridade;return r53NovaFinHash_(x);}
function r53NovaInvImagemLerDiario_(raw,plano,assinatura){
  var j;try{j=JSON.parse(raw);}catch(e){r53NovaFinErro_('diário da inspeção inválido.');}
  var nomes=['celulas','fotos','decoracoesMarcadas','decoracoesAusentes','fora','indeterminadas','formulasImagem'];
  var campos=['amostra','assinatura','cadeia','concluido','contagem','integridade','layout','proxima','totalPaginas','versao','vinculo'];
  var enderecos=['abaId','coluna','linha','tipo'];
  var tipos=['objeto_ilegivel','decoracao_nao_reconhecida','imagem_fora_das_fotos','decoracao_ausente'];
  if(!j||Object.keys(j).sort().join(',')!==campos.join(',')||j.versao!==1||j.assinatura!==assinatura||j.vinculo!==plano.vinculo||j.layout!==plano.layout||j.totalPaginas!==plano.paginas.length||
     !Number.isInteger(j.proxima)||j.proxima<0||j.proxima>j.totalPaginas||typeof j.concluido!=='boolean'||j.concluido!==(j.proxima===j.totalPaginas)||
     ['assinatura','vinculo','layout','cadeia','integridade'].some(function(k){return typeof j[k]!=='string'||!/^[a-f0-9]{64}$/.test(j[k]);})||
     !j.contagem||Object.keys(j.contagem).sort().join(',')!==nomes.slice().sort().join(',')||nomes.some(function(k){return !Number.isInteger(j.contagem[k])||j.contagem[k]<0;})||
     j.contagem.celulas!==plano.paginas.slice(0,j.proxima).reduce(function(n,p){return n+p.linhas*p.colunas;},0)||
     j.contagem.fotos+j.contagem.decoracoesMarcadas+j.contagem.decoracoesAusentes+j.contagem.fora+j.contagem.indeterminadas>j.contagem.celulas||j.contagem.formulasImagem>j.contagem.celulas||
     !Array.isArray(j.amostra)||j.amostra.length>R53_NOVO_INVENTARIO_IMAGENS_.amostraMaxima||j.amostra.some(function(x){
       return !x||Object.keys(x).sort().join(',')!==enderecos.join(',')||tipos.indexOf(x.tipo)<0||
         !Number.isInteger(x.abaId)||!Number.isInteger(x.linha)||!Number.isInteger(x.coluna)||
         !plano.paginas.slice(0,j.proxima).some(function(p){return x.abaId===p.id&&x.linha>=p.linha&&x.linha<p.linha+p.linhas&&x.coluna>=p.coluna&&x.coluna<p.coluna+p.colunas;});
     })||j.integridade!==r53NovaInvImagemSelar_(j))
    r53NovaFinErro_('diário ou vínculo da inspeção inválido; não reiniciar nessa cópia.');
  return j;
}
function r53NovaFichaImagensPrevia(ss,ctx,fase){
  var chave=r53NovaInvImagemFase_(fase),p=r53NovaInvImagemPlano_(ss,ctx,fase);
  if(PropertiesService.getDocumentProperties().getProperty(chave)!==null)r53NovaFinErro_('rodada de imagens já iniciada; retome a mesma.');
  return {assinatura:r53NovaFinHash_([p.vinculo,p.layout,p.paginas.length]),paginas:p.paginas.length,celulas:p.celulas,criacaoDisponivel:false};
}
function r53NovaFichaImagensInspecionar(ss,ctx,fase,assinatura){
  var inicio=Date.now(),chave=r53NovaInvImagemFase_(fase),lock=LockService.getDocumentLock();
  if(!lock.tryLock(1500))r53NovaFinErro_('outra operação em andamento.');
  try{
    var p=r53NovaInvImagemPlano_(ss,ctx,fase),esperada=r53NovaFinHash_([p.vinculo,p.layout,p.paginas.length]),dp=PropertiesService.getDocumentProperties(),raw=dp.getProperty(chave),j;
    if(assinatura!==esperada)r53NovaFinErro_('grade, abas ou objetos mudaram após a prévia.');
    if(raw!==null)j=r53NovaInvImagemLerDiario_(raw,p,assinatura);
    else{
      j={versao:1,assinatura:assinatura,vinculo:p.vinculo,layout:p.layout,totalPaginas:p.paginas.length,proxima:0,concluido:false,
        cadeia:r53NovaFinHash_(['inventario_imagens_v1',p.layout]),contagem:{celulas:0,fotos:0,decoracoesMarcadas:0,decoracoesAusentes:0,fora:0,indeterminadas:0,formulasImagem:0},amostra:[]};
      j.integridade=r53NovaInvImagemSelar_(j);r53NovaDiarioSalvar_(dp,chave,j);
    }
    for(var i=0;!j.concluido&&i<R53_NOVO_INVENTARIO_IMAGENS_.paginasPorExecucao&&Date.now()-inicio<R53_NOVO_INVENTARIO_IMAGENS_.orcamentoMs;i++){
      var res=r53NovaInvImagemLer_(p.paginas[j.proxima]),next=JSON.parse(JSON.stringify(j));
      Object.keys(next.contagem).forEach(function(k){next.contagem[k]+=res.contagem[k];});
      next.amostra=next.amostra.concat(res.amostra).slice(0,R53_NOVO_INVENTARIO_IMAGENS_.amostraMaxima);
      next.cadeia=r53NovaFinHash_([next.cadeia,j.proxima,res.hash]);next.proxima++;next.concluido=next.proxima===next.totalPaginas;
      next.integridade=r53NovaInvImagemSelar_(next);r53NovaDiarioSalvar_(dp,chave,next);j=next;
    }
    return {leituraConcluida:j.concluido,retomar:!j.concluido,paginasLidas:j.proxima,totalPaginas:j.totalPaginas,contagem:j.contagem,
      sobrepostas:p.sobrepostas,desenhos:p.desenhos,amostra:j.amostra,amostraLimitada:j.contagem.fora+j.contagem.indeterminadas+j.contagem.decoracoesAusentes>j.amostra.length,
      retrataSomenteEstaRodada:true,consistenciaTemporalVerificada:false,autenticidadeDecoracaoVerificada:false,criacaoDisponivel:false};
  }finally{lock.releaseLock();}
}
