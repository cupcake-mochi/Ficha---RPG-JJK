/** Preserve XP/restoration while batching mission writes after their reads. */
function salarioIntegrarMissao_(e,editar) {
  if(!e||!e.range||e.salarioIntegrada_||e.salarioProcessado_||e.range.getSheet().getName()!=='FICHA PESSOAL'||!salarioToca_(e.range,15,87,49,72))return false;
  var called=false,erro;
  function executar(){called=true;e.salarioIntegrada_=true;try{if(salarioMissaoDireta_(e))return;return editar(e);}catch(err){erro=err;throw err;}finally{delete e.salarioIntegrada_;}}
  e.salarioAntesGravar_=executar;
  try{salarioEditar_(e);if(!called)executar();if(erro)throw erro;return true;}
  finally{delete e.salarioAntesGravar_;}
}
