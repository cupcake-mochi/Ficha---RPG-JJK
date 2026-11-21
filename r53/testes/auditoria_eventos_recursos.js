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
  const letra=n=>{let s='';for(;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
  const coluna=l=>[...l].reduce((n,ch)=>n*26+ch.charCodeAt(0)-64,0);
  function range(a1,c,nr,nc) {
    // 20/11/2026: o redutor passou pelo motor do ± (r53DeltaExecutar_, 15019f2), que lê um bloco por linha/coluna.
    if(typeof a1==='number'){const l=a1;return {getValues:()=>Array.from({length:nr},(_,i)=>Array.from({length:nc},(_,j)=>dados[letra(c+j)+(l+i)]??''))};}
    const inicio=a1.split(':')[0];
    const [p1,p2=p1]=a1.split(':').map(x=>x.match(/^([A-Z]+)(\d+)$/).slice(1));
    return {getA1Notation:()=>a1,getSheet:()=>sheet,getValue:()=>dados[inicio]??'',
      getRow:()=>Number(p1[1]),getColumn:()=>coluna(p1[0]),getNumRows:()=>Number(p2[1])-Number(p1[1])+1,getNumColumns:()=>coluna(p2[0])-coluna(p1[0])+1,
      setValue:v=>{dados[inicio]=v;},clearContent:()=>{
        const [a,b=a]=a1.split(':');
        const [col,row]=a.match(/^([A-Z]+)(\d+)$/).slice(1);
        const [colFim,rowFim]=b.match(/^([A-Z]+)(\d+)$/).slice(1);
        assert.equal(row,rowFim,'mock limitado à mesma linha');
        assert.equal(col.length,1); assert.equal(colFim.length,1);
        for(let c=col.charCodeAt(0);c<=colFim.charCodeAt(0);c++)dados[String.fromCharCode(c)+row]='';
      }};
  }
  const sheet={getRange:range,getName:()=>'INVOCAÇÕES'};
  const ctx={ABAS:[{nome:'INVOCAÇÕES',redutores:[['X13','U13','W13','V13']]}],
    ABA_INVOCACOES_:'INVOCAÇÕES',SpreadsheetApp:{getActive:()=>({getSheetByName:()=>sheet,toast:t=>{throw Error('aviso inesperado: '+t);}}),flush(){}},
    LockService:{getDocumentLock:()=>({tryLock:()=>true,releaseLock(){}})},console,
    cel_:(idx,k)=>idx[k],lerCelulas_:(_,refs)=>Object.fromEntries(refs.map(x=>[x,dados[x]??'']))};
  vm.createContext(ctx);
  vm.runInContext(['aplicaPasso_','tetoTemp_','prenderTemp_','redutorDaInvocacao_','r53DeltaExecutar_','limitesA1_','tocaFaixa_'].map(extrair).join('\n'),ctx);
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
