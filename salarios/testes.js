'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const code=fs.readFileSync(require('path').join(__dirname,'../apps-script/Salarios.gs'),'utf8');
let checks=0;function eq(a,b){assert.deepStrictEqual(a,b);checks++;}
function fixture(){
 let logs=[],today=46000,failState=false,failLedger=false;
 class Range {
  constructor(s,r,c,h=1,w=1){Object.assign(this,{s,r,c,h,w});}
  getValues(){return Array.from({length:this.h},(_,i)=>Array.from({length:this.w},(_,j)=>this.s.cells.get((this.r+i)+','+(this.c+j))??''));}
  getValue(){return this.getValues()[0][0];}
  getFormula(){let v=this.getValue();return typeof v==='string'&&v.startsWith('=')?v:'';}
  setFormula(v){return this.setValue(v);}
  getNotes(){return Array.from({length:this.h},(_,i)=>Array.from({length:this.w},(_,j)=>this.s.notes.get((this.r+i)+','+(this.c+j))??''));}
  setNotes(a){a.forEach((r,i)=>r.forEach((v,j)=>this.s.notes.set((this.r+i)+','+(this.c+j),v)));return this;}
  setValue(v){return this.setValues([[v]]);}
  setValues(a){if(this.s.name==='SALÁRIOS'&&failLedger)throw Error('falha ledger');if(this.c===12&&failState)throw Error('falha estado');logs.push('write:'+this.s.name);a.forEach((r,i)=>r.forEach((v,j)=>this.s.cells.set((this.r+i)+','+(this.c+j),typeof v==='string'&&v.startsWith("'")?v.slice(1):v)));return this;}
  getSheet(){return this.s;} getRow(){return this.r;} getLastRow(){return this.r+this.h-1;}getColumn(){return this.c;}getLastColumn(){return this.c+this.w-1;}
 }
 class Sheet {
  constructor(name){this.name=name;this.cells=new Map();this.notes=new Map();this.max=1000;}
  getName(){return this.name;}getLastRow(){return Math.max(1,...Array.from(this.cells.keys(),k=>+k.split(',')[0]));}getMaxRows(){return this.max;}insertRowsAfter(_,n){this.max+=n;}
  getRange(r,c,h,w){if(typeof r==='string'){let m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(r),col=s=>Array.from(s).reduce((n,c)=>n*26+c.charCodeAt(0)-64,0);return new Range(this,+m[2],col(m[1]),m[4]?+m[4]-m[2]+1:1,m[3]?col(m[3])-col(m[1])+1:1);}return new Range(this,r,c,h,w);}
 }
 let sheets=Object.fromEntries(['CONFIGURAÇÃO','FICHA PESSOAL','FICHA','CARTEIRA','DADOS_SALARIOS','SALÁRIOS'].map(n=>[n,new Sheet(n)]));
 let ss={getSheetByName:n=>sheets[n]},ui={createMenu(){return {addItem(){return this},addSeparator(){return this},addToUi(){}}}};
 let uuid=0;
 let ctx={console,Date,PropertiesService:{getScriptProperties:()=>({getProperty:()=>null})},ScriptApp:{getScriptId:()=>'qa'},SpreadsheetApp:{getActive:()=>ss,flush(){logs.push('flush')},getUi:()=>ui},LockService:{getDocumentLock:()=>({tryLock(){logs.push('lock');return true},releaseLock(){logs.push('release')}})},Utilities:{getUuid:()=>String(++uuid),formatDate(date,tz,format){let p=new Intl.DateTimeFormat('en-CA',{timeZone:tz,year:'numeric',month:'2-digit',day:'2-digit'}).format(date);if(format==='yyyy-MM-dd')return p;return p.split('-').reverse().join('/');}}};
 vm.createContext(ctx);vm.runInContext(code,ctx);ctx.salarioHoje_=()=>today;
 const put=(name,a,v)=>sheets[name].getRange(a).setValue(v),get=(name,a)=>sheets[name].getRange(a).getValue();
 put('CONFIGURAÇÃO','G323',today);put('CONFIGURAÇÃO','G324',false);put('CONFIGURAÇÃO','G325',true);put('CONFIGURAÇÃO','G326',30);put('CONFIGURAÇÃO','G327',3);put('CONFIGURAÇÃO','G328',.25);put('CONFIGURAÇÃO','G329',true);
 [150000,300000,600000,1200000,2400000].forEach((n,i)=>put('CONFIGURAÇÃO','G'+(339+i),n));[1,1,2,3,0,0].forEach((n,i)=>put('CONFIGURAÇÃO','P'+(339+i),n));
 put('FICHA PESSOAL','AB11','Grau 4');put('FICHA PESSOAL','O86','=150000-500');put('CARTEIRA','O9','Teste');put('DADOS_SALARIOS','L2',JSON.stringify({versao:1,inicio:today,graus:[]}));
 return {ctx,ss,sheets,put,get,logs,day:n=>today=n,now:()=>today,rows:()=>Array.from(ctx.salarioFechamentos_(ss),r=>Array.from(r)),apurar:()=>ctx.salarioSeguro_(ss),failState:v=>failState=v,failLedger:v=>failLedger=v};
}
let f=fixture(),c=f.ctx;
for(const base of [150000,300000,600000,1200000,2400000])for(let p=0;p<=5;p++)eq(c.salarioValor_(base,p,3,.25,true),base*Math.min(1,(p+1)/4));
eq(c.salarioValor_(101,1,3,.25,true),50);eq(c.salarioValor_(101,0,3,.25,false),101);eq(c.salarioValor_(101,0,3,0,true),0);
eq(c.salarioDiaISO_('2026-10-20'),46315);eq(c.salarioDia_(new Date('2026-10-20T01:00:00Z')),46314);eq(c.salarioDia_(new Date('2026-10-20T03:00:00Z')),46315);
eq(c.salarioDia_(c.salarioData_(46315)),46315);
eq(c.salarioPontos_([['a','','Curta',46000,true],['b','','Longa',46029,true],['c','','Final de arco',46030,true],['d','','Curta',46010,false]],46000,46030,{Curta:1,Longa:2,'Final de arco':3}),3);
eq(c.salarioGrauNoFim_([[46000,'Grau 4'],[46030,'Grau 3']],46030),'Grau 4');eq(c.salarioGrauNoFim_([[46000,'Grau 4'],[46030,'Grau 3']],46060),'Grau 3');
f.apurar();f.day(46029);f.apurar();eq(f.rows().length,0);f.day(46030);f.apurar();eq(f.rows().length,1);eq(f.rows()[0][9],37500);eq(f.rows()[0][6],0);f.apurar();eq(f.rows().length,1);eq(f.get('FICHA PESSOAL','O86'),'=150000-500');
f.put('CONFIGURAÇÃO','G323',45000);f.apurar();eq(f.rows().length,1);eq(JSON.parse(f.get('DADOS_SALARIOS','L2')).inicio,46030);
f.day(46090);f.apurar();eq(f.rows().length,3);eq(f.rows()[2][0],'SAL1:46060:46090');
f=fixture();f.apurar();f.day(46010);f.put('FICHA PESSOAL','AW15','Missão A');f.put('FICHA PESSOAL','AX15','Longa');f.apurar();eq(f.get('DADOS_SALARIOS','D2'),46010);f.day(46012);f.put('FICHA PESSOAL','AW15','Missão A corrigida');f.apurar();eq(f.get('DADOS_SALARIOS','D2'),46010);
f.put('FICHA PESSOAL','BC15','Missão A corrigida');f.put('FICHA PESSOAL','BD15','Longa');f.sheets['FICHA PESSOAL'].getRange('BC15').setNotes(f.sheets['FICHA PESSOAL'].getRange('AW15').getNotes());f.apurar();eq(f.get('CONFIGURAÇÃO','G349'),2);
f.day(46030);f.apurar();eq(f.rows()[0][9],112500);eq(f.get('CONFIGURAÇÃO','G349'),0);f.put('FICHA PESSOAL','AX15','Final de arco');f.apurar();eq(f.rows()[0][9],112500);
// A nova missão no dia de fechamento não aumenta o período anterior.
f=fixture();f.apurar();f.day(46030);f.put('FICHA PESSOAL','AW15','Dia de corte');f.put('FICHA PESSOAL','AX15','Final de arco');f.apurar();eq(f.rows()[0][9],37500);eq(f.get('CONFIGURAÇÃO','G349'),3);f.day(46060);f.apurar();eq(f.rows()[1][9],150000);
// Grau é o vigente no final do período, sem promover retroativamente.
f=fixture();f.apurar();f.day(46020);f.put('FICHA PESSOAL','AB11','Grau 3');f.apurar();f.day(46030);f.apurar();eq(f.rows()[0][4],'Grau 3');eq(f.rows()[0][9],75000);
f=fixture();f.apurar();f.day(46030);f.put('FICHA PESSOAL','AB11','Grau 3');f.apurar();eq(f.rows()[0][4],'Grau 4');f.day(46060);f.apurar();eq(f.rows()[1][4],'Grau 3');
// Missões antigas importadas não ganham datas presumidas.
f=fixture();f.put('FICHA PESSOAL','AW15','Anterior à instalação');f.put('FICHA PESSOAL','AX15','Final de arco');f.ctx.salarioSincronizar_(f.ss,{},46000,true);eq(f.get('DADOS_SALARIOS','D2'),'');f.day(46030);f.apurar();eq(f.rows()[0][9],37500);
f=fixture();f.put('CARTEIRA','O9','');f.day(46100);f.apurar();eq(f.rows().length,0);f.put('CARTEIRA','O9','Teste');f.put('CONFIGURAÇÃO','G325',false);f.apurar();eq(f.rows().length,0);f.put('CONFIGURAÇÃO','G325',true);f.apurar();eq(f.rows().length,3);
f=fixture();f.apurar();f.put('CONFIGURAÇÃO','G327',0);f.day(46030);eq(f.apurar(),false);eq(f.rows().length,0);assert.match(f.get('CONFIGURAÇÃO','G331'),/meta/);checks++;
// Uma queda após gravar o livro não duplica o crédito na próxima execução.
f=fixture();f.apurar();f.day(46030);f.failState(true);f.apurar();eq(f.rows().length,1);f.failState(false);f.apurar();eq(f.rows().length,1);
f=fixture();f.apurar();f.day(46030);f.failLedger(true);f.apurar();eq(f.rows().length,0);f.failLedger(false);f.apurar();eq(f.rows().length,1);
f=fixture();f.put('CONFIGURAÇÃO','G324',true);f.day(46100);f.ctx.salarioEditar_({source:f.ss,range:f.sheets['CONFIGURAÇÃO'].getRange('G324')});eq(f.get('CONFIGURAÇÃO','G324'),false);eq(f.ctx.salarioDia_(f.get('CONFIGURAÇÃO','G323')),46100);eq(f.rows().length,0);
eq(f.logs.slice(-2),['flush','release']);
// Duas mesas com o mesmo nome, digitadas em linhas distintas, são participações distintas.
f=fixture();f.put('FICHA PESSOAL','AW15','Treino');f.put('FICHA PESSOAL','AX15','Curta');f.put('FICHA PESSOAL','AW16','Treino');f.put('FICHA PESSOAL','AX16','Longa');f.apurar();eq(f.get('CONFIGURAÇÃO','G349'),3);
f.day(46030);f.apurar();eq(f.rows()[0][9],150000);f.day(46040);f.put('CONFIGURAÇÃO','G323',46040);f.apurar();eq(f.get('CONFIGURAÇÃO','G333').toISOString(),f.ctx.salarioData_(46070).toISOString());eq(f.ctx.salarioDia_(f.get('CONFIGURAÇÃO','G351')),46030);eq(f.rows().length,1);
// Última linha dos quatro blocos e alterações em lote entram na mesma apuração.
f=fixture();for(const [name,type]of [['AW87','AX87'],['BC87','BD87'],['BI87','BJ87'],['BO87','BP87']]){f.put('FICHA PESSOAL',name,'Mesa '+name);f.put('FICHA PESSOAL',type,'Curta');}f.apurar();eq(f.get('CONFIGURAÇÃO','G349'),4);
// Limpar uma linha retira a participação aberta; reutilizar a linha cria nova identidade.
f=fixture();f.put('FICHA PESSOAL','AW15','Uma mesa');f.put('FICHA PESSOAL','AX15','Curta');f.apurar();const firstId=f.get('DADOS_SALARIOS','A2');f.put('FICHA PESSOAL','AW15','');f.apurar();eq(f.get('CONFIGURAÇÃO','G349'),0);f.day(46010);f.put('FICHA PESSOAL','AW15','Outra mesa');f.apurar();eq(f.get('CONFIGURAÇÃO','G349'),1);assert.notStrictEqual(f.get('DADOS_SALARIOS','A3'),firstId);checks++;
// Solos só entram quando a campanha informa o peso; meta e salário são configuráveis.
f=fixture();f.put('FICHA PESSOAL','AW15','Solo');f.put('FICHA PESSOAL','AX15','Solo simples');f.apurar();eq(f.get('CONFIGURAÇÃO','G349'),0);f.put('CONFIGURAÇÃO','P343',2);f.put('CONFIGURAÇÃO','G327',4);f.put('CONFIGURAÇÃO','G339',100001);f.apurar();eq(f.get('CONFIGURAÇÃO','G349'),2);eq(f.get('CONFIGURAÇÃO','G350'),62500);
// Um intervalo customizado respeita a data exata do primeiro vencimento.
f=fixture();f.put('CONFIGURAÇÃO','G326',7);f.apurar();f.day(46006);f.apurar();eq(f.rows().length,0);f.day(46007);f.apurar();eq(f.rows().length,1);
// A ativação é idempotente e desloca a parte salarial para a edição instalável.
f=fixture();let triggers=[],props=new Map();
f.ctx.PropertiesService={getScriptProperties:()=>({getProperty:k=>props.get(k)||null,setProperty:(k,v)=>props.set(k,v)})};
f.ctx.ScriptApp={getScriptId:()=>'qa',getProjectTriggers:()=>triggers,deleteTrigger:t=>{triggers=triggers.filter(v=>v!==t)},newTrigger:name=>{let t={getHandlerFunction:()=>name};let b={timeBased:()=>b,everyDays:()=>b,atHour:()=>b,inTimezone:()=>b,forSpreadsheet:()=>b,onEdit:()=>b,create:()=>{triggers.push(t);return t}};return b}};
f.ctx.ativarSalarioDiario();f.ctx.ativarSalarioDiario();eq(triggers.map(t=>t.getHandlerFunction()),['salarioDiario','salarioRegistrarEdicao']);
f.put('CONFIGURAÇÃO','G324',true);eq(f.ctx.salarioEditar_({source:f.ss,range:f.sheets['CONFIGURAÇÃO'].getRange('G324')}),true);eq(f.get('CONFIGURAÇÃO','G324'),true);
f.ctx.salarioRegistrarEdicao({source:f.ss,range:f.sheets['CONFIGURAÇÃO'].getRange('G324')});eq(f.get('CONFIGURAÇÃO','G324'),false);
f.ctx.desativarSalarioDiario();eq(triggers.map(t=>t.getHandlerFunction()),['salarioRegistrarEdicao']);eq(props.get('salario_edicao'),'qa');
f=fixture();f.put('FICHA PESSOAL','AW18','Missão com caixa textual');f.put('FICHA PESSOAL','AX18','Curta');f.apurar();eq(f.get('DADOS_SALARIOS','F2'),'49:18');eq(typeof f.get('DADOS_SALARIOS','F2'),'string');
console.log(JSON.stringify({resultado:'OK',verificacoes:checks,escopo:'Regras, períodos, data brasileira, registro de missões, Grau, idempotência e falhas de escrita'}));
