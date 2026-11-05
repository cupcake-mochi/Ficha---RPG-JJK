'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync('apps-script/CuraRecebida.gs','utf8')+'\n'+fs.readFileSync('apps-script/Socorro.gs','utf8'),c={};vm.createContext(c);vm.runInContext(source,c);
let n=0;const t=f=>{f();n++;},base={atual:0,maximo:23,classe:1,sequelas:0,integridade:20,integridadeMax:20,regras:[.25,1/3,.5,15,3],corpo:'Corpo Próprio',corporal:false};
for(const [max,cl,want] of [[23,1,[6,8,12]],[93,3,[24,31,45]],[395,7,[99,105,105]],[1,1,[1,1,1]]])for(let k=1;k<=3;k++)t(()=>assert.equal(c.r53SocorroNovaQueda_({...base,maximo:max,classe:cl},k).necessario,want[k-1]));
const zeroDuplo = c.r53SocorroNovaQueda_({...base, integridade: 0}, 2);
t(()=>assert.deepEqual([zeroDuplo.status,zeroDuplo.escolha,zeroDuplo.janela,zeroDuplo.necessario], ['Derrotado',0,0,0]));
t(()=>assert.equal(c.r53SocorroNovaQueda_({...base, integridadeMax: 0, integridade: 0}, 2).status,'Morrendo'));
t(()=>assert.equal(c.r53SocorroNovaQueda_({...base, integridadeMax: 0, integridade: ''}, 2).escolha,2));
t(()=>assert.throws(()=>c.r53SocorroNovaQueda_({...base, integridade: ''}, 2), /Confira a Integridade/));
const lerRegistro = estado => c.r53SocorroLer_({getSheetByName: () => ({
  getRange: a => ({getValue: () => a === 'A2' ? 'SOCORRO_R53_1' : JSON.stringify(estado)})
})});
t(()=>assert.equal(lerRegistro(zeroDuplo).escolha,0));
t(()=>assert.equal(lerRegistro({...zeroDuplo,status:'Encerrado no descanso'}).escolha,0));
t(()=>assert.throws(()=>lerRegistro({...zeroDuplo,status:'Morrendo',janela:3}), /Escolha ou tratamento/));

let q=c.r53SocorroNovaQueda_(base,1),x=c.r53SocorroContaCura_(q,base,3);t(()=>assert.equal(x.vida,0));t(()=>assert.equal(x.estado.tratamento,3));t(()=>assert.equal(x.saiu,false));
x=c.r53SocorroContaCura_(x.estado,{...base,maximo:40},3);t(()=>assert.equal(x.vida,6));t(()=>assert.equal(x.estado.referencia,23));t(()=>assert.equal(x.estado.necessario,6));t(()=>assert.equal(x.saiu,true));t(()=>assert.equal(q.tratamento,0));
x=c.r53SocorroContaCura_(q,{...base,maximo:4},9);t(()=>assert.equal(x.vida,4));t(()=>assert.equal(x.estado.tratamento,9));
x=c.r53SocorroContaCura_(q,{...base,corpo:'Corpo Exaurido',corporal:true},9);t(()=>assert.equal(x.vida,0));t(()=>assert.equal(x.estado.tratamento,4));
t(()=>assert.equal(c.r53SocorroContaCura_(q,{...base,corpo:'Corpo Exaurido',corporal:true},1).estado.tratamento,1));
for(const seq of [0,1,2,3,5])t(()=>assert.equal(c.r53SocorroNovaQueda_({...base,sequelas:seq},1).janela,Math.max(0,3-seq)));
for(const patch of [{atual:1},{maximo:0},{classe:0},{sequelas:-1},{regras:[.25,1/3,.5,15,1.5]}])t(()=>assert.throws(()=>c.r53SocorroNovaQueda_({...base,...patch},1)));
const derrotado = {...q, status: 'Derrotado', janela: 0, tratamento: 4};
const exaurido = {...base, corpo: 'Corpo Exaurido', corporal: true};
for (const [estado, atual, bruto, manual, vida, conversao] of [
  [derrotado, 0, 6, false, 7, 4], [derrotado, 4, 6, true, 7, 0],
  [derrotado, 0, 6, true, 3, 0], [derrotado, 4, 6, false, 11, 4],
  [{...derrotado, tratamentoConvertido: true}, 0, 6, undefined, 3, 0],
  [derrotado, 22, 6, false, 23, 1], [derrotado, 23, 6, true, 23, 0],
  [derrotado, 0, 0, undefined, 0, 0]
]) {
  const resultado = c.r53SocorroContaCura_(estado, {...exaurido, atual}, bruto, manual);
  t(()=>assert.deepEqual([resultado.vida, resultado.convertido, resultado.saiu, resultado.estado.status,
    resultado.estado.janela, resultado.estado.tratamento],
    [vida, conversao, false, 'Derrotado', 0, 4]));
  t(()=>assert.equal(Boolean(resultado.estado.tratamentoConvertido), bruto > 0));
}
t(()=>assert.throws(()=>c.r53SocorroContaCura_(derrotado, exaurido, 6), /Confirme se/));
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
for(const mode of ['cancel','no','changed','integridade mudou','busy']){
 let writes=0,reads=0,alerts=[];
 const ss2={toast(){}};
 const ctx={SpreadsheetApp:{getActive:()=>ss2,getUi:()=>({Button:{OK:'OK',YES:'YES'},ButtonSet:{OK_CANCEL:1,YES_NO:2},prompt:()=>({getSelectedButton:()=>mode==='cancel'?'CANCEL':'OK',getResponseText:()=> '1'}),alert:(...a)=>{alerts.push(a);return mode==='no'?'NO':'YES';}})},LockService:{getDocumentLock:()=>({tryLock:()=>mode!=='busy',releaseLock(){}})}};
 vm.createContext(ctx);vm.runInContext(source,ctx);ctx.r53SocorroRecursos_=()=>({...base,...(reads++ ? (mode==='changed' ? {maximo:40} : mode==='integridade mudou' ? {integridade:0} : {}) : {})});ctx.r53SocorroLer_=()=>null;ctx.r53SocorroGravar_=()=>writes++;ctx.registrarQueda();t(()=>assert.equal(writes,0));
}
// A entrada real do menu grava apenas o registro e a vida depois da derrota.
for (const [conversao, confirmacao, vidaEsperada, vidaInicial = 0] of [
  ['CANCEL', null, 0], ['NO', 'NO', 0], ['NO', 'YES', 7], ['YES', 'YES', 3], ['YES', 'YES', 23, 23]
]) {
  const confirmacoes = [];
  let registro = derrotado, vida = vidaInicial;
  const ss = {
    getId: () => 'QA',
    getSheetByName: nome => nome === 'SOCORRO' ? {getSheetId: () => 2} : {getSheetId: () => 1},
    toast() {}
  };
  const ui = {
    Button: {OK: 'OK', YES: 'YES', NO: 'NO'}, ButtonSet: {},
    prompt: () => ({getSelectedButton: () => 'OK', getResponseText: () => '6'}),
    alert: titulo => {confirmacoes.push(titulo); return titulo === 'Conferir tratamento após a derrota' ? conversao : confirmacao;}
  };
  c.SpreadsheetApp = {getActive: () => ss, getUi: () => ui};
  c.LockService = {getDocumentLock: () => ({tryLock: () => true, releaseLock() {}})};
  c.r53SocorroLer_ = () => registro;
  c.r53LerCura_ = () => ({...exaurido, atual: vida});
  c.r53SocorroRecursos_ = () => ({...exaurido, atual: vida, caixas: [true, false, false], extras: 0});
  c.Sheets.Spreadsheets.batchUpdate = ({requests}) => {
    const escritas = requests.filter(r => r.updateCells?.fields === 'userEnteredValue').map(r => r.updateCells);
    assert.deepEqual(Array.from(escritas, r => [r.start.sheetId, r.start.rowIndex]),
      vidaInicial === vidaEsperada ? [[2, 0]] : [[2, 0], [1, 25]]);
    registro = JSON.parse(escritas[0].rows[1].values[1].userEnteredValue.stringValue);
    if (escritas[1]) vida = escritas[1].rows[0].values[0].userEnteredValue.numberValue;
  };
  c.aplicarCuraRecebida();
  t(()=>assert.deepEqual(confirmacoes, ['Conferir tratamento após a derrota', ...(confirmacao ? ['Confirmar cura após a derrota'] : [])]));
  t(()=>assert.equal(vida, vidaEsperada));
  t(()=>assert.equal(Boolean(registro.tratamentoConvertido), confirmacao === 'YES'));
  t(()=>assert.deepEqual([registro.status, registro.janela, registro.tratamento], ['Derrotado', 0, 4]));
}
// Uma perda posterior de Integridade termina a janela, conservando o tratamento.
const emAndamento = {...q, tratamento: 3, janela: 2};
t(()=>assert.throws(()=>c.r53SocorroContaCura_(emAndamento, {...base, integridade: 0}, 6), /Integridade esgotada/));
let atualizado, resumoQueda;
c.SpreadsheetApp = {
  getActive: () => ({toast(){}}),
  getUi: () => ({Button:{YES:'YES'},ButtonSet:{},alert:(titulo,texto)=>{resumoQueda=texto;return 'YES';},
    prompt:()=>{throw Error('Insistir não pode ser oferecido');}})
};
c.r53SocorroLer_ = () => emAndamento;
c.r53SocorroRecursos_ = () => ({...base, integridade: 0});
c.r53SocorroGravar_ = (ss, estado, recursos, vida, sequela) => {atualizado = {estado,vida,sequela};};
c.registrarQueda();
t(()=>assert.match(resumoQueda,/durante Morrendo/));
t(()=>assert.deepEqual({...atualizado.estado},{...emAndamento,status:'Derrotado',janela:0,derrotaIntegridade:true}));
t(()=>assert.deepEqual([atualizado.vida,atualizado.sequela],[null,false]));

const molde = [{nome:'FICHA',vals:[[37,4,'=FÓRMULA_DIVERGENTE',0]]}];
t(()=>assert.throws(()=>c.r53AjustarIndicadorIntegridade_(molde), /fórmula D37 divergente/));
const trecho = fs.readFileSync('apps-script/Ficha.gs','utf8').match(/\[37,4,("(?:[^"\\]|\\.)*Estágio 4(?:[^"\\]|\\.)*"),\d+\]/);
const formula = JSON.parse(trecho[1]);
const revisao = require('../diagnostico-android/integridade_movimento_plano.json')
  .find(d => d.aba === 'FICHA' && d.r === 37 && d.c === 4);
t(() => assert.equal(formula, revisao.depois));
const comGuarda = revisao.antes;
molde[0].vals[0][2] = comGuarda.replace('OR($D$34="",$J$34=0)', '$D$34=""');
c.r53AjustarIndicadorIntegridade_(molde);
t(() => assert.equal(molde[0].vals[0][2], comGuarda));
c.r53AjustarIndicadorIntegridade_(molde);
t(() => assert.equal(molde[0].vals[0][2], comGuarda));
console.log(JSON.stringify({resultado:'OK',verificacoes:n}));
