// Transporte real em VM; casos de interrupção, guarda de conteúdo e preservação.
const assert=require('assert'),fs=require('fs');
const {criaSheets}=require('../medidas/sheets-de-mentira.js');
const src=require('../medidas/carregar-ficha.js').fontes();
const code=fs.readFileSync(require('path').join(__dirname,'../apps-script/Codigo.gs'),'utf8');
let checks=0;
const ok=(name,f)=>{f();checks++;console.log('ok '+name);};
function novo(){
 let now=0;class Clock{getTime(){return now;}}
 const s=criaSheets(src,code,{Date:Clock});s.now=v=>{now=v;};
 s.ctx.ABAS=['A','B','C','D'].map((nome,i)=>({nome,rows:12+i,cols:4+i,oculta:false}));
 s.ss.insertSheet('__montando__',0);s.ss.deleteSheet(s.ss.getSheetByName('Página1'));
 return s;
}
const s=novo();
ok('limite na preparação guarda a primeira aba vazia e o rascunho',()=>{
 assert.equal(s.ctx.prepararAbas_(s.ss,{passou:()=>200001}),null);
 assert.deepEqual(s.P.abas.map(a=>a.nome),['__montando__','A']);
});
const a=s.acha('A');a.maxC=26; // corte entre inserir e ajustar dimensões
ok('retomada corrige dimensões incompletas e conserva identidade da aba',()=>{
 const result=s.ctx.prepararAbas_(s.ss,{passou:()=>0});
 assert.equal(result.length,4);assert.strictEqual(s.acha('A'),a);
 assert.equal(a.maxC,4);assert.equal(a.maxR,12);
 assert.deepEqual(s.P.abas.map(a=>a.nome),['A','B','C','D']);
});
ok('preparação repetida não duplica nem substitui abas vazias',()=>{
 const old=s.P.abas.slice();s.ctx.prepararAbas_(s.ss,{passou:()=>0});
 assert(old.every((a,i)=>s.P.abas[i]===a));
});
ok('conteúdo preenchido bloqueia retomada antes de criar ou apagar',()=>{
 const b=novo();b.ss.insertSheet('A',1).getRange('A1').setValue(0);
 const before=b.P.abas.slice();assert.throws(()=>b.ctx.prepararAbas_(b.ss,{passou:()=>0}),/conteúdo/);
 assert.deepEqual(b.P.abas,before);assert.equal(b.acha('A').v.get('1,1'),0);
});
ok('aba desconhecida bloqueia adoção de preparação anterior',()=>{
 const b=novo();b.ss.insertSheet('estranha',1);
 assert.throws(()=>b.ctx.continuar(),/conteúdo ou aba desconhecida/);
 assert.equal(b.P.props.montagem_parada,undefined);
});
ok('rascunho antigo vazio é adotado como criação; sem rascunho não é',()=>{
 const b=novo();let stage;b.ctx.construir=()=>{stage=b.ctx.RETOMADA_;};
 b.ctx.continuar();assert.equal(stage,-1);assert.equal(b.P.props.montagem_parada,'-1');
 assert.equal(b.ctx.RETOMADA_,null);
 b.ss.insertSheet('A',1);b.ss.deleteSheet(b.ss.getSheetByName('__montando__'));delete b.P.props.montagem_parada;
 assert.throws(()=>b.ctx.continuar(),/não há montagem parada/);
});
ok('falha de serviço em criar uma aba mantém as anteriores para retomada',()=>{
 const b=novo(),insert=b.ss.insertSheet;b.ss.insertSheet=(name,pos)=>{if(name==='B')throw Error('serviço');return insert(name,pos);};
 assert.throws(()=>b.ctx.prepararAbas_(b.ss,{passou:()=>0}),/serviço/);
 const first=b.acha('A');b.ss.insertSheet=insert;b.ctx.prepararAbas_(b.ss,{passou:()=>0});
 assert.strictEqual(b.acha('A'),first);assert.equal(b.P.abas.length,4);
});
ok('continuar em zero preenche a primeira aba sem apagar a preparação',()=>{
 const b=novo();b.ctx.prepararAbas_(b.ss,{passou:()=>0});
 const first=b.acha('A');b.P.props.montagem_parada='0';b.ctx.LIMITE_DA_EXECUCAO_=100;
 b.ctx.montarAba_=(sheet)=>{sheet.getRange('A1').setValue('preenchido');b.now(1000000);return 'ok';};
 b.ctx.continuar();assert.strictEqual(b.acha('A'),first);
 assert.equal(first.v.get('1,1'),'preenchido');assert.equal(b.P.props.montagem_parada,'1');
 assert.equal(b.P.locale,'pt_BR');assert.equal(b.ctx.RETOMADA_,null);
});
console.log(checks+' cenários de transporte passaram; nenhum recálculo ou Google simulado como prova nativa.');
