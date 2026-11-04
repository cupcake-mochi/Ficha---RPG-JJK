'use strict';
// Diagnóstico: executa a ação real com serviços simulados. Não é teste nativo nem aprovação mecânica.
const fs=require('fs'),vm=require('vm');
let vida=0,writes=[];
const ui={Button:{OK:'OK',YES:'YES'},ButtonSet:{OK_CANCEL:1,YES_NO:2},prompt:()=>({getSelectedButton:()=> 'OK',getResponseText:()=> '3'}),alert:()=> 'YES'};
const ficha={getRange:a=>({getValues:()=>[[vida,0,0,0,0,0,23]],getValue:()=> 'Corpo Próprio',setValue:v=>{writes.push({celula:a,valor:v});vida=v;}})};
const ctx={SpreadsheetApp:{getUi:()=>ui,getActive:()=>({getSheetByName:n=>n==='FICHA'?ficha:{getRange:()=>({getValue:()=>false})},toast(){}}),flush(){}},LockService:{getDocumentLock:()=>({tryLock:()=>true,releaseLock(){}})}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync('apps-script/CuraRecebida.gs','utf8'),ctx);ctx.aplicarCuraRecebida();
console.log(JSON.stringify({cenario:'Morrendo, Aguentar, máximo de referência 23, cura 3',esperado:{vida:0,tratamento:3,necessario:6},observado:{vida,writes},conforme:vida===0,escopo:'Ação real em mock; nenhuma chamada Google'}));
