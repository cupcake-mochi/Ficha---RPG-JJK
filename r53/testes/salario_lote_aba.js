'use strict';
// Conferência do salário sem perguntar a aba depois do flush (26/10/2026): o salario_lote.gs de antes e o de agora
// tomam as mesmas decisões (apagar o próximo fechamento, conferir ou não) e o de agora não chama a planilha depois
// do flush, onde cada chamada esperava o recálculo da edição (4,6–4,8 s medidos na cópia).
const fs=require('fs'),vm=require('vm'),assert=require('assert'),{execSync}=require('child_process');
let checks=0;
function eq(a,b,m){assert.deepStrictEqual(a,b,m);checks++;}
const novo=fs.readFileSync('r53/diagnostico-android/salario_lote.gs','utf8');
const antigo=execSync('git show 3e77909:r53/diagnostico-android/salario_lote.gs').toString('utf8');
assert.notStrictEqual(novo,antigo);
function rodar(fonte,aba,l,c,demora){
 const log=[];let flush=false,depois=0,agora=0;
 const sheet={getName(){if(flush)depois++;log.push('getName');return aba;}};
 const range={getSheet(){if(flush)depois++;return sheet;},getA1Notation(){if(flush)depois++;return String.fromCharCode(64+c)+l;},
  getRow:()=>l,getLastRow:()=>l,getColumn:()=>c,getLastColumn:()=>c};
 const props={deleteProperty:k=>log.push('apaga '+k),getProperty:()=>null};
 const ctx={console:{log(){}},Date:{now:()=>agora},
  PropertiesService:{getDocumentProperties:()=>props},
  SpreadsheetApp:{flush(){flush=true;log.push('flush');},getActive:()=>'ss'},
  SALARIO_:{config:'CONFIGURAÇÃO'},
  salarioToca_:(r,l1,l2,c1,c2)=>r.getRow()<=l2&&r.getLastRow()>=l1&&r.getColumn()<=c2&&r.getLastColumn()>=c1,
  r53OnEditOriginal_(){log.push('edição');agora+=demora;return 'feito';}};
 vm.createContext(ctx);vm.runInContext(fonte,ctx);
 ctx.r53SalarioConferir_=(ss,t0,p)=>{log.push('confere');return false;};
 const out=ctx.r53SalarioOnEdit_({range,source:'ss'});
 return {out,decisoes:log.filter(x=>x!=='getName'),depois};
}
const casos=[
 ['FICHA AMALDIÇOADA',524,2,2000],['FICHA',20,10,6000],['FICHA',20,10,9000],
 ['CARTEIRA',27,3,1000],['CARTEIRA',3,46,1000],['CARTEIRA',10,20,1000],
 ['FICHA PESSOAL',15,49,1000],['FICHA PESSOAL',11,29,1000],['FICHA PESSOAL',86,25,1000],['FICHA PESSOAL',40,10,1000],
 ['CONFIGURAÇÃO',40,15,1000],['CONFIGURAÇÃO',51,37,1000]];
let antes=0;
for(const c of casos){
 const a=rodar(antigo,...c),b=rodar(novo,...c);
 eq(b.out,a.out,c.join(' '));eq(b.decisoes,a.decisoes,c.join(' '));
 eq(b.depois,0,c.join(' ')+': chamada à planilha depois do flush');antes+=a.depois;
}
assert(antes>0,'o de antes chamava a planilha depois do flush');checks++;
console.log(JSON.stringify({checks,resultado:'OK',escopo:casos.length+' edições: mesmas decisões do salário; chamadas à planilha depois do flush '+antes+' → 0'}));
