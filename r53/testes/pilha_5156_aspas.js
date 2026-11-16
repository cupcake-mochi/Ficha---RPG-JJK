'use strict';
const assert=require('node:assert/strict');
const p=require('../diagnostico-android/preparar_pilha_5156');
let checks=0;
const test=f=>{f();checks++;};
const plan=[{aba:'FICHA',r:26,c:10,antes:'=IF(\'FICHA\'!A1="\'FICHA\'! e ""oi""",\'DADOS_PROGRESSAO\'!B2,\'FICHA PESSOAL\'!C3)',depois:'=\'FICHA\'!A1+1'}];
const snapshot={locale:'en_US',cells:[{aba:'FICHA',r:26,c:10,sheetId:17,value:'=IF(FICHA!A1="\'FICHA\'! e ""oi""",DADOS_PROGRESSAO!B2,\'FICHA PESSOAL\'!C3)'}]};
const original=JSON.stringify(snapshot);
const requests=p.planejarCelulas(snapshot,false,plan);
test(()=>assert.equal(requests.requests.length,1));
test(()=>assert.equal(requests.requests[0].updateCells.rows[0].values[0].userEnteredValue.formulaValue,plan[0].depois));
test(()=>assert.equal(JSON.stringify(snapshot),original));
for(const value of [snapshot.cells[0].value.replace('A1','A2'),snapshot.cells[0].value.replace(' e ',' E '),snapshot.cells[0].value.replace('FICHA PESSOAL','FICHA OUTRA')]){
 test(()=>assert.throws(()=>p.planejarCelulas({...snapshot,cells:[{...snapshot.cells[0],value}]},false,plan),/divergente/));
}
test(()=>assert.equal(p.planejarCelulas({...snapshot,cells:[{...snapshot.cells[0],value:'=FICHA!A1+1'}]},true,plan).requests.length,1));
test(()=>assert.throws(()=>p.planejarCelulas({locale:'en_US',cells:[{aba:'FICHA',addr:'J26',sheetId:17,note:'=FICHA!A1'}]},false,[{aba:'FICHA',addr:'J26',antes:"='FICHA'!A1",depois:'nova'}]),/divergente/));
test(()=>assert.equal(p.formulaComparavel("Texto 'FICHA'!"),"Texto 'FICHA'!"));
test(()=>assert.equal(p.formulaComparavel("='FICHA PESSOAL'!A1"),"='FICHA PESSOAL'!A1"));
test(()=>assert.equal(p.formulaComparavel("='O''FICHA'!A1"),"='O''FICHA'!A1"));
test(()=>assert.equal(p.formulaComparavel("='FICHA''FICHA'!A1"),"='FICHA''FICHA'!A1"));
// Aplicação e reversão em pt_BR com literal de texto que parece referência.
const local=[{aba:'FICHA',r:1,c:1,antes:'=IF(\'FICHA\'!A1=1,"\'FICHA\'!",0)',depois:'=\'FICHA\'!A1+2'}];
test(()=>assert.equal(p.planejarCelulas({locale:'pt_BR',cells:[{aba:'FICHA',r:1,c:1,sheetId:17,value:'=IF(FICHA!A1=1;"\'FICHA\'!";0)'}]},false,local).requests.length,1));
console.log(JSON.stringify({resultado:'OK',verificacoes:checks}));
