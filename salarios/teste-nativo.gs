/** Somente na cópia QA. Nunca instalar na ficha oficial. */
function testarSalariosNativo() {
 var ss=SpreadsheetApp.getActive();
 if(ss.getId()!=='19zzS-vbwOK63FQOCKnCKzc_PMaHdWU-9Ud_YmScde_s')throw Error('Teste permitido somente na cópia QA de salários.');
 var cfg=ss.getSheetByName('CONFIGURAÇÃO'),pp=ss.getSheetByName('FICHA PESSOAL'),car=ss.getSheetByName('CARTEIRA'),hoje=salarioHoje_(),asserts=0;
 function igual(a,b){if(a!==b)throw Error('Divergência '+JSON.stringify([a,b]));asserts++;}
 car.getRange('O9').setValue('QA salários');pp.getRange('O86').setFormula('=150000-500');SpreadsheetApp.flush();
 cfg.getRange('G323').setValue(salarioData_(hoje-90));
 // Duas missões em períodos diferentes, com terceira exatamente no limite.
 pp.getRange('AW15:AX17').setValues([['QA curta','Curta'],['QA longa','Longa'],['QA arco','Final de arco']]);
 var st=salarioEstado_(ss),ms=salarioSincronizar_(ss,st,hoje,false),ds=ss.getSheetByName('DADOS_SALARIOS');
 ms.forEach(function(r,i){ds.getRange(i+2,4).setValue(hoje-[80,50,30][i]);});
 var a=salarioBloqueado_(ss,function(){return salarioApurar_(ss,hoje);});
 igual(a.novos,3);var p=salarioFechamentos_(ss);igual(p.length,3);igual(p[0][9],75000);igual(p[1][9],112500);igual(p[2][9],150000);
 igual(pp.getRange('O86').getFormula(),'=150000-500');SpreadsheetApp.flush();igual(pp.getRange('W86').getValue(),487000);
 var b=salarioBloqueado_(ss,function(){return salarioApurar_(ss,hoje);});igual(b.novos,0);igual(salarioFechamentos_(ss).length,3);
 // Reemissão mantém o livro e a fronteira anterior.
 cfg.getRange('G324').setValue(true);salarioEditar_({source:ss,range:cfg.getRange('G324')});igual(cfg.getRange('G324').getValue(),false);igual(salarioDia_(cfg.getRange('G323').getValue()),hoje);igual(salarioFechamentos_(ss).length,3);
 // Corrigir uma missão já paga não reescreve salário fechado.
 pp.getRange('AX15').setValue('Final de arco');salarioBloqueado_(ss,function(){return salarioApurar_(ss,hoje);});igual(salarioFechamentos_(ss)[0][9],75000);
 console.log(JSON.stringify({resultado:'OK',verificacoes:asserts,pagamentos:p.map(function(r){return {inicio:salarioDia_(r[1]),fim:salarioDia_(r[2]),pontos:r[6],ienes:r[9]};}),saldoManual:pp.getRange('O86').getFormula(),total:pp.getRange('W86').getValue()}));
}

function testarSalariosNativoRapido() {
 var ss=SpreadsheetApp.getActive(),inicio=Date.now();
 if(ss.getId()!=='19zzS-vbwOK63FQOCKnCKzc_PMaHdWU-9Ud_YmScde_s')throw Error('Teste permitido apenas na cópia QA.');
 var antes=salarioFechamentos_(ss),res=conferirSalarios(),depois=salarioFechamentos_(ss);
 if(antes.length!==3||depois.length!==3||res.novos!==0)throw Error('Idempotência divergente.');
 if(depois[0][9]!==75000||depois[1][9]!==112500||depois[2][9]!==150000)throw Error('Pagamentos divergentes.');
 console.log(JSON.stringify({resultado:'OK',duracao_ms:Date.now()-inicio,novos:res.novos,pagamentos:depois.map(function(r){return {pontos:r[6],parcela:r[8],ienes:r[9]};})}));
}
