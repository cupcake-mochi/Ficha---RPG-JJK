'use strict';
// Cadeia onEdit real em Sheets simulado. Não mede gatilho Google nem recalcula fórmulas.
// Abas existem nas dimensões publicadas; somente os recursos sob teste são preenchidos.
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const {criaSheets}=require('../../medidas/sheets-de-mentira');
const {fontes}=require('../../medidas/carregar-ficha');
const logs=[];
const {ctx,ss}=criaSheets(fontes(),fs.readFileSync('apps-script/Codigo.gs','utf8'),
  {console:{log:(...args)=>logs.push(args.join(' '))}});
for(const spec of ctx.ABAS){
  const sheet=ss.insertSheet(spec.nome);
  if(spec.cols>26)sheet.insertColumnsAfter(26,spec.cols-26);
  if(spec.rows>1000)sheet.insertRowsAfter(1000,spec.rows-1000);
}
for(const name of ['MONTAGENS','DADOS_R53'])if(!ss.getSheetByName(name))ss.insertSheet(name);
const resultados=[];
function executar(sheet,a1,esperado,ler,nome){
  logs.length=0;
  ctx.onEdit({source:ss,range:sheet.getRange(a1)});
  assert.deepEqual(logs,[],'Falha intermediária invalida a simulação: '+nome);
  const obtido=ler();
  resultados.push({nome,esperado,obtido,conforme:JSON.stringify(esperado)===JSON.stringify(obtido)});
}
const entidade=ss.getSheetByName('INVOCAÇÕES');
const redutores=ctx.ABAS.find(s=>s.nome==='INVOCAÇÕES').redutores;
assert.equal(redutores.length,12);
for(const [i,[delta,atual,temp,max]] of redutores.entries()){
  for(const [a,v]of [[atual,10],[max,20],[temp,15],[delta,'']])entidade.getRange(a).setValue(v);
  executar(entidade,temp,10,()=>entidade.getRange(temp).getValue(),'teto entidade '+(i+1));
}
for(const a1 of ['X13','X13:Y13']){
  for(const[a,v]of Object.entries({U13:10,V13:20,W13:3,X13:-5,Y13:7}))entidade.getRange(a).setValue(v);
  executar(entidade,a1,[[8,20,0,'',7]],()=>entidade.getRange('U13:Y13').getValues(),'delta entidade '+a1);
}
const ficha=ss.getSheetByName('FICHA');
for(const a1 of ['AF26','AF26:AR26']){
  for(const[a,v]of Object.entries({D26:10,J26:20,AF26:15,AM26:''}))ficha.getRange(a).setValue(v);
  executar(ficha,a1,10,()=>ficha.getRange('AF26').getValue(),'teto personagem '+a1);
}
for(const [atual,max,temp,delta] of [['D26','J26','AF26','AM26'],['D30','J30','AF30','AM30']]){
  for(const[a,v]of [[atual,0],[max,0],[temp,0],[delta,5]])ficha.getRange(a).setValue(v);
  executar(ficha,delta,0,()=>ficha.getRange(atual).getValue(),'ganho com máximo zero '+atual);
}
for(const [sheet,atual,max,temp,delta] of [[ficha,'D26','J26','AF26','AM26'],[entidade,'U13','V13','W13','X13']]){
  for(const queued of [false,true]){
    for(const[a,v]of [[atual,20],[max,20],[temp,0]])sheet.getRange(a).setValue(v);
    logs.length=0;
    if(queued){
      // As duas edições já chegaram à célula antes da primeira execução.
      sheet.getRange(delta).setValue(-3);
      ctx.onEdit({source:ss,range:sheet.getRange(delta),value:'-5'});
      ctx.onEdit({source:ss,range:sheet.getRange(delta),value:'-3',oldValue:'-5'});
    }else{
      for(const v of [-5,-3]){sheet.getRange(delta).setValue(v);ctx.onEdit({source:ss,range:sheet.getRange(delta),value:String(v)});}
    }
    assert.deepEqual(logs,[]);
    const obtido=sheet.getRange(atual).getValue();
    resultados.push({nome:'dois gastos '+sheet.getName()+(queued?' enfileirados':' processados separadamente'),
      esperado:12,obtido,conforme:obtido===12});
  }
}
vm.runInContext(fs.readFileSync('r53/atalho_livre.gs','utf8'),ctx);
for(const modo of ['máximo zero','separados','enfileirados']){
  for(const[a,v]of Object.entries({D26:modo==='máximo zero'?0:20,J26:modo==='máximo zero'?0:20,AF26:0}))ficha.getRange(a).setValue(v);
  logs.length=0;
  if(modo==='máximo zero'){ficha.getRange('AM26').setValue(5);ctx.r53LivreDelta_(ficha.getRange('AM26'));}
  else if(modo==='enfileirados'){ficha.getRange('AM26').setValue(-3);ctx.r53LivreDelta_(ficha.getRange('AM26'));ctx.r53LivreDelta_(ficha.getRange('AM26'));}
  else for(const v of [-5,-3]){ficha.getRange('AM26').setValue(v);ctx.r53LivreDelta_(ficha.getRange('AM26'));}
  assert.deepEqual(logs,[]);
  const esperado=modo==='máximo zero'?0:12,obtido=ficha.getRange('D26').getValue();
  resultados.push({nome:'atalho real '+modo,esperado,obtido,conforme:esperado===obtido});
}
console.log(JSON.stringify({escopo:'onEdit completo e atalho locais, sem recálculo e sem navegador',
  casos:resultados.length,conformes:resultados.filter(x=>x.conforme).length,
  divergencias:resultados.filter(x=>!x.conforme),resultados},null,2));
