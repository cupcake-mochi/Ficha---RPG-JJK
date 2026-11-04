'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync('apps-script/CuraRecebida.gs','utf8')+'\n'+fs.readFileSync('apps-script/Socorro.gs','utf8'),c={};vm.createContext(c);vm.runInContext(source,c);
let n=0;const t=f=>{f();n++;},base={atual:0,maximo:23,classe:1,sequelas:0,regras:[.25,1/3,.5,15,3],corpo:'Corpo Próprio',corporal:false};
for(const [max,cl,want] of [[23,1,[6,8,12]],[93,3,[24,31,45]],[395,7,[99,105,105]],[1,1,[1,1,1]]])for(let k=1;k<=3;k++)t(()=>assert.equal(c.r53SocorroNovaQueda_({...base,maximo:max,classe:cl},k).necessario,want[k-1]));
let q=c.r53SocorroNovaQueda_(base,1),x=c.r53SocorroContaCura_(q,base,3);t(()=>assert.equal(x.vida,0));t(()=>assert.equal(x.estado.tratamento,3));t(()=>assert.equal(x.saiu,false));
x=c.r53SocorroContaCura_(x.estado,{...base,maximo:40},3);t(()=>assert.equal(x.vida,6));t(()=>assert.equal(x.estado.referencia,23));t(()=>assert.equal(x.estado.necessario,6));t(()=>assert.equal(x.saiu,true));t(()=>assert.equal(q.tratamento,0));
x=c.r53SocorroContaCura_(q,{...base,maximo:4},9);t(()=>assert.equal(x.vida,4));t(()=>assert.equal(x.estado.tratamento,9));
x=c.r53SocorroContaCura_(q,{...base,corpo:'Corpo Exaurido',corporal:true},9);t(()=>assert.equal(x.vida,0));t(()=>assert.equal(x.estado.tratamento,4));
t(()=>assert.equal(c.r53SocorroContaCura_(q,{...base,corpo:'Corpo Exaurido',corporal:true},1).estado.tratamento,1));
for(const seq of [0,1,2,3,5])t(()=>assert.equal(c.r53SocorroNovaQueda_({...base,sequelas:seq},1).janela,Math.max(0,3-seq)));
for(const patch of [{atual:1},{maximo:0},{classe:0},{sequelas:-1},{regras:[.25,1/3,.5,15,1.5]}])t(()=>assert.throws(()=>c.r53SocorroNovaQueda_({...base,...patch},1)));
const derrotado = {...q, status: 'Derrotado', janela: 0, tratamento: 4};
const exaurido = {...base, corpo: 'Corpo Exaurido', corporal: true};
for (const [estado, atual, bruto, vida, conversao] of [
  [derrotado, 0, 6, 7, 4], [derrotado, 4, 6, 7, 0],
  [{...derrotado, tratamentoConvertido: true}, 0, 6, 3, 0],
  [derrotado, 22, 6, 23, 0], [derrotado, 0, 0, 0, 0]
]) {
  const resultado = c.r53SocorroContaCura_(estado, {...exaurido, atual}, bruto);
  t(()=>assert.deepEqual([resultado.vida, resultado.convertido, resultado.saiu, resultado.estado.status,
    resultado.estado.janela, resultado.estado.tratamento],
    [vida, conversao, false, 'Derrotado', 0, 4]));
  t(()=>assert.equal(Boolean(resultado.estado.tratamentoConvertido), vida !== atual));
}
t(()=>assert.throws(()=>c.r53SocorroContaCura_(q,{...base,atual:1},99)));
t(()=>assert.equal(c.r53SocorroContaCura_(q,base,0).estado.tratamento,0));
// Testa o lote real: registro, vida e uma única Sequela juntos; falha do serviço não tem fallback parcial.
let batches=[],ss={getId:()=> 'QA',getSheets:()=>[],getSheetByName:name=>name==='FICHA'?{getSheetId:()=>1}:null};
c.Sheets={Spreadsheets:{batchUpdate:(r,id)=>batches.push(r)}};
c.r53SocorroGravar_(ss,x.estado,{caixas:[true,false,false],extras:0},6,true);
t(()=>assert.equal(batches.length,1));let updates=batches[0].requests.filter(r=>r.updateCells).map(r=>r.updateCells);t(()=>assert.equal(updates.find(r=>r.start.rowIndex===25).rows[0].values[0].userEnteredValue.numberValue,6));t(()=>assert.equal(updates.find(r=>r.start.rowIndex===47).start.columnIndex,7));t(()=>assert.equal(updates.filter(r=>r.start.rowIndex===47).length,1));
batches=[];c.r53SocorroGravar_(ss,q,{caixas:[true,true,true],extras:2},6,true);t(()=>assert.equal(batches[0].requests.find(r=>r.updateCells&&r.updateCells.start.rowIndex===49).updateCells.rows[0].values[0].userEnteredValue.numberValue,3));
c.Sheets.Spreadsheets.batchUpdate=()=>{throw Error('falha do serviço');};t(()=>assert.throws(()=>c.r53SocorroGravar_(ss,q,base,0,false)));
// Cancelar e detectar conflito entre diálogo e gravação não escrevem.
for(const mode of ['cancel','no','changed','busy']){
 let writes=0,reads=0,alerts=[];
 const ss2={toast(){}};
 const ctx={SpreadsheetApp:{getActive:()=>ss2,getUi:()=>({Button:{OK:'OK',YES:'YES'},ButtonSet:{OK_CANCEL:1,YES_NO:2},prompt:()=>({getSelectedButton:()=>mode==='cancel'?'CANCEL':'OK',getResponseText:()=> '1'}),alert:(...a)=>{alerts.push(a);return mode==='no'?'NO':'YES';}})},LockService:{getDocumentLock:()=>({tryLock:()=>mode!=='busy',releaseLock(){}})}};
 vm.createContext(ctx);vm.runInContext(source,ctx);ctx.r53SocorroRecursos_=()=>({...base,maximo:mode==='changed'&&reads++?40:23});ctx.r53SocorroLer_=()=>null;ctx.r53SocorroGravar_=()=>writes++;ctx.registrarQueda();t(()=>assert.equal(writes,0));
}
// A entrada real do menu grava apenas o registro e a vida depois da derrota.
for (const [confirmacao, vidaEsperada] of [['NO', 0], ['YES', 7]]) {
  const confirmacoes = [];
  let registro = derrotado, vida = 0;
  const ss = {
    getId: () => 'QA',
    getSheetByName: nome => nome === 'SOCORRO' ? {getSheetId: () => 2} : {getSheetId: () => 1},
    toast() {}
  };
  const ui = {
    Button: {OK: 'OK', YES: 'YES'}, ButtonSet: {},
    prompt: () => ({getSelectedButton: () => 'OK', getResponseText: () => '6'}),
    alert: titulo => {confirmacoes.push(titulo); return confirmacao;}
  };
  c.SpreadsheetApp = {getActive: () => ss, getUi: () => ui};
  c.LockService = {getDocumentLock: () => ({tryLock: () => true, releaseLock() {}})};
  c.r53SocorroLer_ = () => registro;
  c.r53LerCura_ = () => ({...exaurido, atual: vida});
  c.r53SocorroRecursos_ = () => ({...exaurido, atual: vida, caixas: [true, false, false], extras: 0});
  c.Sheets.Spreadsheets.batchUpdate = ({requests}) => {
    const escritas = requests.filter(r => r.updateCells?.fields === 'userEnteredValue').map(r => r.updateCells);
    assert.deepEqual(Array.from(escritas, r => [r.start.sheetId, r.start.rowIndex]), [[2, 0], [1, 25]]);
    registro = JSON.parse(escritas[0].rows[1].values[1].userEnteredValue.stringValue);
    vida = escritas[1].rows[0].values[0].userEnteredValue.numberValue;
  };
  c.aplicarCuraRecebida();
  t(()=>assert.deepEqual(confirmacoes, ['Confirmar cura após a derrota']));
  t(()=>assert.equal(vida, vidaEsperada));
  t(()=>assert.deepEqual([registro.status, registro.janela, registro.tratamento], ['Derrotado', 0, 4]));
}
console.log(JSON.stringify({resultado:'OK',verificacoes:n}));
