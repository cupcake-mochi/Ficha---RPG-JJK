/** Somente a cópia descartável criada para esta rodada. Nunca publicar na oficial. */
function testeCarteiraR2() {
  var ss=SpreadsheetApp.getActive();
  if(ss.getId()!=='1lsb_bCr4Ev3U4aN1OcLshn16sdhgsPNjCZQ2NxoIueY')throw Error('Teste bloqueado fora da cópia QA.');
  var cfg=ss.getSheetByName('CONFIGURAÇÃO'),p=ss.getSheetByName('FICHA PESSOAL'),hoje=salarioHoje_();
  if(salarioFechamentos_(ss).length)throw Error('QA já contém pagamentos; não repetir a preparação.');
  ss.getSheetByName('CARTEIRA').getRange('O9').setValue('QA Salários · Carteira R2');
  cfg.getRange('O38').setValue(salarioData_(hoje-60));p.getRange('O86').setFormula('=150000-500');
  p.getRange('AW15:AX15').setValues([['QA · Final de arco','Final de arco']]);
  var estado={versao:1,inicio:hoje-60,graus:[[hoje-60,'Grau 4']],ultimaEmissao:hoje-60};salarioSalvarEstado_(ss,estado);
  var ms=salarioSincronizar_(ss,estado,hoje,false);ms[0][3]=hoje-59;
  ss.getSheetByName('DADOS_SALARIOS').getRange('D2').setValue(hoje-59);
  var config=salarioConfig_(ss);salarioApurar_(ss,hoje,{config:config,estado:estado,missoes:ms});
  var pagos=salarioFechamentos_(ss);
  if(pagos.length!==2||pagos[0][9]!==150000||pagos[1][9]!==37500)throw Error('Créditos fora do esperado: '+JSON.stringify(pagos));
  salarioApurar_(ss,hoje,{config:config,estado:salarioEstado_(ss),missoes:ms});
  if(salarioFechamentos_(ss).length!==2)throw Error('Crédito duplicado.');
  if(p.getRange('O86').getFormula()!=='=150000-500'||p.getRange('W86').getValue()!==337000)throw Error('Ajuste manual ou total incorreto.');
  console.log(JSON.stringify({resultado:'OK',integral:150000,reduzido:37500,creditos:2,manual:149500,total:337000,duplicacao:false}));
}
