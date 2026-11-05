'use strict';
// Mesma rotina do descanso, sem inicializar catálogos, restauradores ou cartas.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
function gerar() {
 const source=fs.readFileSync(path.join(root,'apps-script/Codigo.gs'),'utf8');
 const {ctx}=require('../medidas/sheets-de-mentira').criaSheets(require('../medidas/carregar-ficha').fontes(),source);
 const completo=ctx.indiceEstatico_(),idx={};
 const keys=['descanso','último descanso','vida','energia','integridade','vida_max','energia_max','integridade_max','origem','marcante','menor 1','menor 2','classe máxima','exaustão','sequela 1','sequela 2','sequela 3','sequela extras'];
 for(const k of keys){if(!completo[k])throw Error('Descanso sem endereço '+k);idx[k]=completo[k];}
 if(idx.descanso.split(':')[0]!=='D45')throw Error('Endereço do menu mudou; atualizar o limite do dispatcher');
 const nomes=['cel_','limitesA1_','lerCelulas_','regraDoDescanso_','contaDoDescanso_','textoDoDescanso_','descansar_','r53DescansarComQueda'];
 const corpo=(n)=>{let a=source.indexOf('function '+n+'('),b=source.indexOf('\n}',a);if(a<0||b<0)throw Error('Função ausente '+n);const x=source.slice(a,b+2);new Function(x);return x;};
 const a=source.indexOf('var SEM_DESCANSO_ = '),b=source.indexOf('function regraDoDescanso_(',a);
 const constantes=source.slice(a,b);
 const output='// GERADO por r53/descanso_leve.js; funções extraídas de Codigo.gs.\nvar R53_DESCANSO_LEVE_;\n'+
  'function r53DescansoLeve_(){return R53_DESCANSO_LEVE_||(R53_DESCANSO_LEVE_=(function(){\n'+
  constantes+'\nfunction indiceEstatico_(){return '+JSON.stringify(idx)+';}\n'+nomes.map(corpo).join('\n')+
  '\nreturn {editar:function(e){return descansar_(e,indiceEstatico_());},comQueda:r53DescansarComQueda};\n})());}\n'+
  `function r53DescansoEdit_(e){
 if(!e||!e.range)return false;var r=e.range;
 if(r.getSheet().getName()!=='FICHA'||r.getRow()!==45||r.getColumn()!==4||r.getNumRows()!==1||r.getNumColumns()>10)return false;
 var tipo=e.value;if(tipo!==undefined&&['Curto · lugar propício','Curto · fora','Longo · lugar propício','Longo · fora'].indexOf(String(tipo))<0)return true;
 var lock=LockService.getDocumentLock();if(!lock.tryLock(1000)){SpreadsheetApp.getActive().toast('Outra operação está em andamento. Escolha o descanso novamente após ela terminar.','Descanso',6);return true;}
 try{r53DescansoLeve_().editar(e);}finally{try{SpreadsheetApp.flush();}finally{lock.releaseLock();}}return true;
}\n`;
 new Function(output);return {output,idx,nomes};
}
if(require.main===module){const r=gerar();fs.writeFileSync(path.join(root,'apps-script/Descanso.gs'),r.output);console.log(JSON.stringify({bytes:r.output.length,funcoes:r.nomes.length}));}
module.exports={gerar};
