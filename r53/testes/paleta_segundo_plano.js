'use strict';
// VM: agenda pela edição instalável, continua até terminar e se reagenda.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const src=fs.readFileSync(path.join(__dirname,'../diagnostico-android/paleta_segundo_plano.gs'),'utf8');
function cenario(passosRestantes,duracao){
 let pend=passosRestantes>0?'tema':null,triggers=[],agora=0,chamadas=0;
 const ctx={console:{log(){}},Date:{now:()=>agora},Utilities:{sleep:ms=>{agora+=ms;}},
  PropertiesService:{getDocumentProperties:()=>({getProperty:k=>k==='paleta_pendente'?pend:null})},
  ScriptApp:{getProjectTriggers:()=>triggers.slice(),deleteTrigger:t=>{triggers=triggers.filter(x=>x!==t);},
   newTrigger:h=>({timeBased:()=>({after:ms=>({create:()=>{const t={getHandlerFunction:()=>h,ms};triggers.push(t);return t;}})})})},
  r53PaletaLeve_:()=>({continuar:()=>{chamadas++;agora+=duracao;if(--passosRestantes<=0)pend=null;}})};
 vm.createContext(ctx);vm.runInContext(src,ctx);
 return {ctx,get triggers(){return triggers;},get chamadas(){return chamadas;},setPend:v=>{pend=v;}};
}
// Edição fora da paleta sem pendência: nada agendado.
let c=cenario(0,1000);c.ctx.r53AgendarPaleta_({range:{getSheet:()=>({getName:()=>'FICHA'}),getA1Notation:()=>'D5'}});assert.strictEqual(c.triggers.length,0);
// Escolha da paleta: agenda uma vez, sem duplicar.
c=cenario(3,20000);const ed={range:{getSheet:()=>({getName:()=>'CARTEIRA'}),getA1Notation:()=>'C27'}};
c.ctx.r53AgendarPaleta_(ed);c.ctx.r53AgendarPaleta_(ed);assert.strictEqual(c.triggers.length,1);
// Execução termina em 3 voltas e não reagenda.
c.ctx.paletaEmSegundoPlano();assert.strictEqual(c.chamadas,3);assert.strictEqual(c.triggers.length,0);
// Trabalho longo: para antes de 270 s e reagenda uma vez.
c=cenario(100,25000);c.ctx.paletaEmSegundoPlano();assert(c.chamadas>=10&&c.chamadas<=11);assert.strictEqual(c.triggers.length,1);
console.log(JSON.stringify({resultado:'OK',cenarios:4}));
