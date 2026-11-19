'use strict';
// Diagnóstico, não teste de aprovação: executa helpers reais com Range simulado.
// Não substitui a reprodução de colagem pelo navegador do Google Sheets.
const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const source=fs.readFileSync('apps-script/Codigo.gs','utf8');
function extrair(nome) {
  const start=source.indexOf('function '+nome+'('), end=source.indexOf('\nfunction ',start+1);
  assert(start>=0 && end>start); return source.slice(start,end);
}
const resultados=[];
function ambiente(valores) {
  const dados={...valores};
  function range(a1) {
    const inicio=a1.split(':')[0];
    return {getA1Notation:()=>a1,getSheet:()=>sheet,getValue:()=>dados[inicio]??'',
      setValue:v=>{dados[inicio]=v;},clearContent:()=>{
        const [a,b=a]=a1.split(':');
        const [col,row]=a.match(/^([A-Z]+)(\d+)$/).slice(1);
        const [colFim,rowFim]=b.match(/^([A-Z]+)(\d+)$/).slice(1);
        assert.equal(row,rowFim,'mock limitado à mesma linha');
        assert.equal(col.length,1); assert.equal(colFim.length,1);
        for(let c=col.charCodeAt(0);c<=colFim.charCodeAt(0);c++)dados[String.fromCharCode(c)+row]='';
      }};
  }
  const sheet={getRange:range};
  const ctx={ABAS:[{nome:'INVOCAÇÕES',redutores:[['X13','U13','W13','V13']]}],
    ABA_INVOCACOES_:'INVOCAÇÕES',SpreadsheetApp:{getActive:()=>({getSheetByName:()=>sheet})},
    cel_:(idx,k)=>idx[k],lerCelulas_:(_,refs)=>Object.fromEntries(refs.map(x=>[x,dados[x]??'']))};
  vm.createContext(ctx);
  vm.runInContext(['aplicaPasso_','tetoTemp_','prenderTemp_','redutorDaInvocacao_'].map(extrair).join('\n'),ctx);
  return {ctx,dados,range};
}
function registrar(nome,esperado,obtido){resultados.push({nome,esperado,obtido,conforme:JSON.stringify(esperado)===JSON.stringify(obtido)});}
for(const faixa of ['X13','X13:Y13']) {
  const a=ambiente({U13:10,V13:20,W13:3,X13:-5,Y13:7});
  a.ctx.redutorDaInvocacao_({range:a.range(faixa)});
  registrar('delta entidade '+faixa,{U13:8,V13:20,W13:0,X13:'',Y13:7},a.dados);
}
for(const faixa of ['AF26','AF26:AR26']) {
  const a=ambiente({AF26:15,J26:20,AM26:7});
  a.ctx.prenderTemp_({range:a.range(faixa)},{vida_temp:'AF26',vida_max:'J26'});
  registrar('teto temporário '+faixa,{AF26:10,J26:20,AM26:7},a.dados);
}
console.log(JSON.stringify({escopo:'Helpers reais isolados; eventos nativos pendentes',casos:resultados.length,
  conformes:resultados.filter(x=>x.conforme).length,divergencias:resultados.filter(x=>!x.conforme),resultados},null,2));
