/** Entradas pessoais das 12 entidades e do conjunto, em cópia nova isolada.
 * Requer financeiro/formacao/validacoes/contrato_entidades confiáveis.
 * Não altera configurações, cartões R53, MONTAGENS, imagens ou automações.
 */
function r53NovaEntContrato_(id) {
  if (typeof R53_NOVA_ENTIDADES_CONTRATO_ === 'undefined' || R53_NOVA_ENTIDADES_CONTRATO_.versao !== 1 ||
      typeof id !== 'string' || !Object.prototype.hasOwnProperty.call(R53_NOVA_ENTIDADES_CONTRATO_.dominios,id))
    r53NovaFinErro_('grupo de entidade desconhecido.');
  var c=R53_NOVA_ENTIDADES_CONTRATO_.dominios[id];
  if(c.entidade===null)return c;
  var comum=R53_NOVA_ENTIDADES_CONTRATO_.entidades[c.entidade];
  if(!comum)r53NovaFinErro_('contrato comum da entidade ausente.');
  return {entidade:c.entidade,aba:c.aba,entradas:c.entradas,guardas:comum.guardas,leituras:comum.leituras,foto:comum.foto};
}
function r53NovaEntOperacoes_(id) {
  var out=[];
  r53NovaEntContrato_(id).entradas.forEach(function(x) {
    out.push({aba:x.aba,faixa:x.faixa,tipo:'matriz',valores:x.valores,
      formulasLivres:x.tipo==='formula',formulasEquivalentes:x.equivalentes});
    out.push({aba:x.aba,faixa:x.faixa,tipo:'notas_matriz',notas:x.notas});
  });
  return out;
}
function r53NovaEntPreservados_(ss,id) {
  var c=r53NovaEntContrato_(id),sh=ss.getSheetByName(c.aba),leituras=[];
  if (!sh) r53NovaFinErro_('falta a aba das entidades.');
  c.leituras.forEach(function(a) {
    var r=sh.getRange(a);leituras.push({pos:r53NovaFormPos_(a),valores:r.getValues(),formulas:r.getFormulas()});
  });
  function cel(a,qual) {
    var p=r53NovaFormPos_(a),l=leituras.filter(function(x){return p[0]>=x.pos[0]&&p[0]<=x.pos[2]&&p[1]>=x.pos[1]&&p[1]<=x.pos[3];})[0];
    if (!l || !l[qual][p[0]-l.pos[0]] || l[qual][p[0]-l.pos[0]][p[1]-l.pos[1]]===undefined)
      r53NovaFinErro_('leitura da entidade incompleta.');
    return l[qual][p[0]-l.pos[0]][p[1]-l.pos[1]];
  }
  var guardas=c.guardas.map(function(x) {
    var f=cel(x.faixa,'formulas');
    if (x.formulas) {
      if (x.formulas.indexOf(r53NovaFinHash_(f))<0) r53NovaFinErro_('fórmula protegida da entidade desconhecida.');
      return [x.faixa,x.formulas[0]];
    }
    if (f || cel(x.faixa,'valores')!==x.valor) r53NovaFinErro_('rótulo da entidade desconhecido.');
    return [x.faixa,x.valor];
  });
  if (c.foto) {
    var f=cel(c.foto,'formulas'),v=cel(c.foto,'valores');
    if (f || v!=='' && v!=='FOTO\n式神') r53NovaFinErro_('foto da entidade exige a etapa de arte antes de continuar.');
    guardas.push(['foto',v]);
  }
  // Menus de fábrica são protegidos, nunca regravados. A origem dos dados pode
  // conter cadastros custom da mesa; comparamos a referência, não seu conteúdo.
  var menus=[];
  c.entradas.forEach(function(x) {
    var r=sh.getRange(x.faixa),p=r53NovaFormPos_(x.faixa),dv=r.getDataValidations();
    if (!Array.isArray(dv)||dv.length!==x.valores.length) r53NovaFinErro_('validações da entidade incompletas.');
    var mesclas=r.getMergedRanges().map(function(m) {
      if(['getRow','getColumn','getLastRow','getLastColumn'].some(function(k){return typeof m[k]!=='function';}))
        r53NovaFinErro_('mescla da entidade incompleta.');
      return [m.getRow(),m.getColumn(),m.getLastRow(),m.getLastColumn()];
    });
    var ordenar=function(v){return v.map(function(m){return m.join(',');}).sort();};
    if(r53NovaFinCanon_(ordenar(mesclas))!==r53NovaFinCanon_(ordenar(x.mesclas)))
      r53NovaFinErro_('mescla da entidade fora do contrato.');
    x.valores.forEach(function(l,i) {
      if (!Array.isArray(dv[i])||dv[i].length!==l.length) r53NovaFinErro_('validações da entidade incompletas.');
      l.forEach(function(v,j) {
        var addr=r53NovaEntLetra_(p[1]+j)+(p[0]+i),f=cel(addr,'formulas');
        if (x.tipo==='formula' && f && x.equivalentes[i][j].indexOf(f)<0)
          r53NovaFinErro_('fórmula pessoal da entidade desconhecida.');
        var d=r53NovaValidDescrever_(dv[i][j]),esperado=x.validacoes[i][j];
        if (esperado && esperado.tipo==='VALUE_IN_RANGE') {
          esperado={tipo:esperado.tipo,permiteInvalido:esperado.permiteInvalido,ajuda:esperado.ajuda,
            argumentos:[{aba:esperado.argumentos[0].aba,faixa:esperado.argumentos[0].faixa,documento:ss.getId()},esperado.argumentos[1]]};
        }
        // Os modelos publicados tornaram estes mesmos menus estritos. Preservar
        // ambas as versões conhecidas; a escolha real entra no fingerprint.
        if (esperado && d && typeof d.permiteInvalido==='boolean') {
          esperado={tipo:esperado.tipo,argumentos:esperado.argumentos,ajuda:esperado.ajuda,permiteInvalido:d.permiteInvalido};
        }
        if (r53NovaFinCanon_(d)!==r53NovaFinCanon_(esperado)) r53NovaFinErro_('menu da entidade fora do contrato.');
        menus.push([addr,d]);
      });
    });
  });
  return r53NovaFinHash_([guardas,menus]);
}
function r53NovaEntLetra_(n) {
  var s='';while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;
}
function r53NovaEntPerfil_(id) {
  r53NovaEntContrato_(id);
  return {recibo:true,nome:'entidades_'+id,diario:'r53_nova_ficha_entidades_'+id+'_v1',
    limites:{escritasPorExecucao:4,orcamentoMs:210000},
    operacoes:function(){return r53NovaEntOperacoes_(id);},preservados:function(ss){return r53NovaEntPreservados_(ss,id);},
    pendente:['demais_entidades','cartoes_e_montagens','memorias_finais','arte','automacoes_e_novo_responsavel','conferencia_conjunta','prova_nativa']};
}
function r53NovaFichaEntidadePrevia(ss,ctx,id) {
  if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};
  return r53NovaPerfilPrevia_(ss,ctx,r53NovaEntPerfil_(id));
}
function r53NovaFichaEntidadeAplicar(ss,ctx,id,assinatura) {
  if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};
  try{return r53NovaPerfilAplicar_(ss,ctx,assinatura,r53NovaEntPerfil_(id));}
  finally{if(typeof R53_REF_CACHE_!=='undefined')R53_REF_CACHE_={};}
}
