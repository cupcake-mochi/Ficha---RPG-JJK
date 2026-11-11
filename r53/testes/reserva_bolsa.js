'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const p=require('../diagnostico-android/preparar_reserva_bolsa'),{formulaLocal}=require('../diagnostico-android/preparar_pilha_5156');
const clone=x=>JSON.parse(JSON.stringify(x));
let checks=0;const t=f=>{f();checks++;};
function snapshot(locale='pt_BR'){
 const sheets=['FICHA','DADOS','DADOS_CUSTOM','FICHA PESSOAL','DADOS_CONFIG','CONFIGURAÇÃO'];
 const cells=p.plano.map(d=>({...d,sheetId:sheets.indexOf(d.aba),[d.addr?'note':'value']:formulaLocal(d.antes,locale)}));
 for(const [aba,r,c]of p.AUX)cells.push({aba,r,c,sheetId:sheets.indexOf(aba),value:null,effective:aba==='FICHA'&&r===11?'Latente':aba==='FICHA'&&r===52?'—':aba==='DADOS_CUSTOM'?r===121?false:'':aba==='DADOS_CONFIG'&&c===5?'':0});
 return {locale,cells};
}
function set(s,a,r,c,v){s.cells.find(x=>!x.addr&&x.aba===a&&x.r===r&&x.c===c).effective=v;return s;}
function ativa(s,bolsa=false,custom=false){set(s,'FICHA',11,24,custom?'Origem QA':bolsa?'Híbrido':'Restrição Celestial · Restrição corporal');set(s,'FICHA',52,19,bolsa?'Bolsa Orgânica':'Reserva Excedente');if(custom){set(s,'DADOS_CUSTOM',121,2,true);set(s,'DADOS_CUSTOM',123,2,bolsa?'Híbrido':'Restrição Celestial · Restrição corporal');}return s;}
for(const locale of ['pt_BR','en_US']){
 const s=snapshot(locale),before=clone(s);
 t(()=>assert.equal(p.planejar(s).requests.length,6));t(()=>assert.deepEqual(s,before));
 const fim=clone(s);for(const d of p.plano){const x=fim.cells.find(x=>x.aba===d.aba&&(d.addr?x.addr===d.addr:!x.addr&&x.r===d.r&&x.c===d.c));x[d.addr?'note':'value']=formulaLocal(d.depois,locale);}
 t(()=>assert.equal(p.planejar(fim,true).requests.length,6));t(()=>assert.throws(()=>p.planejar(fim),/divergente/));
 for(const bolsa of [false,true])for(const custom of [false,true]){
  const s=ativa(snapshot(locale),bolsa,custom),r=bolsa?13:3,baba=bolsa?'FICHA PESSOAL':'FICHA',br=bolsa?86:30,bc=bolsa?12:16;
  t(()=>assert.equal(p.planejar(s).requests.length,6));
  for(const v of [1,-1,0.5,'8','0,5',true]){const x=clone(s);set(x,baba,br,bc,v);const original=clone(x);t(()=>assert.throws(()=>p.planejar(x),/compensação manual/));t(()=>assert.deepEqual(x,original));}
  for(const v of [NaN,Infinity]){const x=clone(s);set(x,baba,br,bc,v);t(()=>assert.throws(()=>p.planejar(x),/compensação manual/));}
  const somar=clone(s);set(somar,'DADOS_CONFIG',r,2,8);t(()=>assert.throws(()=>p.planejar(somar),/compensação manual/));
  const cancelam=clone(s);for(const [row,v]of [[11,8],[12,-8]]){set(cancelam,'CONFIGURAÇÃO',row,3,true);set(cancelam,'CONFIGURAÇÃO',row,4,bolsa?'Limite de carga':'PE máximo');set(cancelam,'CONFIGURAÇÃO',row,5,'somar');set(cancelam,'CONFIGURAÇÃO',row,6,v);}t(()=>assert.throws(()=>p.planejar(cancelam),/CONFIGURAÇÃO linha/));
  const final=clone(somar);set(final,'DADOS_CONFIG',r,3,1);set(final,baba,br,bc,8);t(()=>assert.equal(p.planejar(final).requests.length,6));
  set(final,'DADOS_CONFIG',r,5,'Entrada inválida');t(()=>assert.throws(()=>p.planejar(final),/CONFIGURAÇÃO/));
 }
}
// Sem a capacidade ativa não se declara que um modificador genérico é compensação dela.
const gen=snapshot();set(gen,'FICHA',30,16,10);set(gen,'FICHA PESSOAL',86,12,3);t(()=>assert.equal(p.planejar(gen).requests.length,6));
const invalid=ativa(snapshot(),false,true);set(invalid,'DADOS_CUSTOM',121,2,false);set(invalid,'FICHA',30,16,8);t(()=>assert.equal(p.conferirCompensacoes(invalid).reservaAtiva,false));
for(const mutate of [s=>s.cells.pop(),s=>s.cells.push(clone(s.cells.at(-1))),s=>delete s.cells.at(-1).effective,s=>s.cells.at(-1).effective={errorValue:{type:'N_A'}},s=>s.cells.at(-1).sheetId=999]){
 const s=snapshot();mutate(s);t(()=>assert.throws(()=>p.planejar(s)));
}
const ctx=vm.createContext({});vm.runInContext(require('../../medidas/carregar-ficha').fontes(),ctx);t(()=>assert.equal(ctx.SOBRAS_.length,0));require('../diagnostico-android/preparar_aviso_atributo').reverterModelo(require('../diagnostico-android/preparar_menu_oficios').reverterModelo(ctx.ABAS));require('../diagnostico-android/preparar_buff_decimal').reverterModelo(ctx.ABAS);
const alvo=(a,d)=>{const sh=a.find(a=>a.nome===d.aba);return d.addr?sh.notas.find(x=>x[0]===d.addr)?.[1]:sh.vals.find(x=>x[0]===d.r&&x[1]===d.c)?.[2];};
for(const d of p.plano)t(()=>assert.equal(alvo(ctx.ABAS,d),d.depois));
const errado=clone(ctx.ABAS),ult=p.plano.at(-1),sh=errado.find(a=>a.nome===ult.aba);(ult.addr?sh.notas.find(x=>x[0]===ult.addr):sh.vals.find(x=>x[0]===ult.r&&x[1]===ult.c))[ult.addr?1:2]='divergente';const orig=clone(errado);t(()=>assert.throws(()=>p.reverterModelo(errado),/divergente/));t(()=>assert.deepEqual(errado,orig));
p.reverterModelo(ctx.ABAS);
if(process.argv[3]){const antigo=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),semGeracao=abas=>JSON.stringify(abas.map(({geracao,...a})=>a));t(()=>assert(semGeracao(ctx.ABAS)===semGeracao(antigo),'Mudança fora dos seis alvos ou dos metadados de geração'));}
vm.runInContext(p.molde(),ctx);ctx.r53AjustarReservaBolsa_(ctx.ABAS);
for(const d of p.plano)t(()=>assert.equal(alvo(ctx.ABAS,d),d.depois));
const depois=JSON.stringify(ctx.ABAS);ctx.r53AjustarReservaBolsa_(ctx.ABAS);t(()=>assert.equal(JSON.stringify(ctx.ABAS),depois));
t(()=>assert.throws(()=>p.prepararCodigo('outro código'),/divergente/));
// A restauração da carga deve alcançar só CZ41, inclusive numa colagem maior.
const leve=require('../reserva_bolsa_restaurar').gerar();t(()=>assert.equal(leve.output,fs.readFileSync('apps-script/ReservaBolsa.gs','utf8')));
let f='apagada',escritas=0;const chamadas=[];
const shRest={getName:()=>'DADOS',getParent:()=>({getSpreadsheetLocale:()=>'pt_BR'}),getRange:(r,c)=>{chamadas.push([r,c]);return{getFormula:()=>f,setFormula:x=>{f=x;escritas++;}};}};
const lc=vm.createContext({});vm.runInContext(leve.output,lc);
const evento=(r1,c1,r2=r1,c2=c1,name='DADOS')=>({range:{getSheet:()=>name==='DADOS'?shRest:{getName:()=>name},getRow:()=>r1,getLastRow:()=>r2,getColumn:()=>c1,getLastColumn:()=>c2}});
for(const e of [null,evento(40,104),evento(42,104),evento(41,103),evento(41,105),evento(41,104,41,104,'FICHA')])t(()=>assert.equal(lc.r53RestaurarCargaOrigem_(e),false));
const alheio=evento(19,4);alheio.range.getSheet=()=>{throw Error('Edição comum não deve consultar a aba');};t(()=>assert.equal(lc.r53RestaurarCargaOrigem_(alheio),false));
t(()=>assert.equal(chamadas.length,0));t(()=>assert.equal(lc.r53RestaurarCargaOrigem_(evento(41,104)),true));t(()=>assert.equal(f,formulaLocal(leve.formula,'pt_BR')));t(()=>assert.equal(escritas,1));
t(()=>assert.equal(lc.r53RestaurarCargaOrigem_(evento(40,100,42,110)),true));t(()=>assert.equal(escritas,1));t(()=>assert(chamadas.every(([r,c])=>r===41&&c===104)));
if(process.argv[2]){const code=fs.readFileSync(process.argv[2],'utf8'),novo=p.prepararCodigo(code);new vm.Script(novo);t(()=>assert.throws(()=>p.prepararCodigo(novo),/divergente/));}
if(process.argv[4]){
 const path=require('node:path'),z=require('node:zlib'),parts=[];
 for(const file of ['Ficha','Invocacoes','Analise','Configuracao','Origens']){const m=/var R53_CODIGO_(\d+)_ = ("[^\n]*");/.exec(fs.readFileSync(path.join(process.argv[4],'qa-era-'+file+'.gs'),'utf8'));assert(m);parts[+m[1]]=JSON.parse(m[2]);}
 const src=z.gunzipSync(Buffer.from(parts.join(''),'base64')).toString('utf8'),abas=JSON.parse(JSON.stringify(vm.runInNewContext('(function(){'+src+'})()').__estado().abas)),c=vm.createContext({});
 for(const [file,name]of [['preparar_pilha_5156','r53AjustarPilha516_'],['preparar_integridade_movimento','r53AjustarIntegridadeMovimento_'],['preparar_equipamento','r53AjustarEquipamento_'],['preparar_bencaos_imunidades','r53AjustarBencaosImunidades_'],['preparar_origens_recursos','r53AjustarOrigensRecursos_'],['preparar_reserva_bolsa','r53AjustarReservaBolsa_']]){const patch=require('../diagnostico-android/'+file),code=patch.molde?patch.molde():'var R53_PILHA_516_='+JSON.stringify(patch.plano)+';\n'+fs.readFileSync('r53/diagnostico-android/pilha_5156_molde.gs','utf8');vm.runInContext(code,c);c[name](abas);}
 for(const d of p.plano)t(()=>assert.equal(alvo(abas,d),d.depois));
}
console.log(JSON.stringify({resultado:'OK',verificacoes:checks,alvos:p.plano.length,escopo:'modelo, reversão, locais e bloqueio de possíveis compensações; Google separado'}));
