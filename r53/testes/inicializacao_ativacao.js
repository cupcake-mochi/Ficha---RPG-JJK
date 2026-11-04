'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {ambiente}=require('./apoio_inicializacao');
let casos=0;function caso(n,f){if(process.argv[2]&&n!==process.argv[2])return;try{f();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
const json=x=>JSON.parse(JSON.stringify(x));
function criar(){
 const a=ambiente();a.complete(a.preview());
 const rt={projeto:'projeto_sintetico_0001',usuario:'execucao_sintetica',triggers:[],creates:[],hook:null};
 const app={getScriptId:()=>rt.projeto,getProjectTriggers:()=>rt.triggers,
  EventType:{CLOCK:'CLOCK',ON_EDIT:'ON_EDIT',ON_OPEN:'ON_OPEN'},TriggerSource:{CLOCK:'CLOCK',SPREADSHEETS:'SPREADSHEETS'},
  newTrigger(nome){let tipo,source,args=[];const b={timeBased(){tipo='CLOCK';source='CLOCK';return b;},everyDays(n){args.push(['days',n]);return b;},atHour(n){args.push(['hour',n]);return b;},inTimezone(n){args.push(['zone',n]);return b;},forSpreadsheet(ss){source=ss.getId();return b;},onEdit(){tipo='ON_EDIT';return b;},onOpen(){tipo='ON_OPEN';return b;},create(){
   if(rt.hook)rt.hook('antes');const id='id-'+(rt.creates.length+1);rt.creates.push({nome,args});
   const t={getUniqueId:()=>id,getHandlerFunction:()=>nome,getEventType:()=>tipo,getTriggerSource:()=>tipo==='CLOCK'?'CLOCK':'SPREADSHEETS',getTriggerSourceId:()=>source};rt.triggers.push(t);if(rt.hook)rt.hook('depois');return t;}};return b;},deleteTrigger(){throw Error('não apagar rotinas');}};
 a.ctx.ScriptApp=app;a.ctx.Session={getTemporaryActiveUserKey:()=>rt.usuario};
 for(const f of ['propriedades.gs','ativacao.gs'])vm.runInContext(fs.readFileSync(path.join(__dirname,'../inicializacao',f),'utf8'),a.ctx);
 const p=a.ctx.r53NovaFichaPropriedadesPrevia(a.ss,a.context);for(let i=0;i<5;i++){if(a.ctx.r53NovaFichaPropriedadesAplicar(a.ss,a.context,p.assinatura).concluido)break;}
 a.writes.length=0;a.rt=rt;a.run=()=>a.ctx.r53NovaFichaAtivacaoAplicar(a.ss,a.context);
 a.done=()=>{for(let i=0;i<5;i++){const r=a.run();if(r.instalacaoLocalConcluida)return r;}throw Error('não concluiu');};return a;
}
caso('instala exatamente três rotinas, preserva células e propriedades e repete sem efeito',()=>{
 const a=criar(),cells=json([...a.cells]),doc=json([...a.doc]),script=json([...a.script]),r=a.done();assert.equal(a.rt.creates.length,3);
 assert.deepEqual(a.rt.creates[0].args,[['days',1],['hour',3],['zone','America/Sao_Paulo']]);assert.equal(r.rotinasInstaladasNestaConta,3);
 for(const k of ['criacaoDisponivel','financeiroConcluido','ativacaoConcluida','responsavelVerificadoPeloBot'])assert.equal(r[k],false);
 assert.deepEqual(json([...a.cells]),cells);for(const[k,v]of doc)assert.equal(a.doc.get(k),v);for(const[k,v]of script)assert.equal(a.script.get(k),v);
 const w=a.writes.length;assert(a.run().instalacaoLocalConcluida);assert.equal(a.writes.length,w);assert.equal(a.rt.creates.length,3);
 assert(!JSON.stringify(r).includes(a.rt.usuario));assert(!JSON.stringify(r).includes(a.rt.projeto));
});
for(let i=0;i<3;i++)caso('retoma após rotina registrada '+i,()=>{const a=criar();for(let n=0;n<=i;n++)a.run();a.done();assert.equal(a.rt.creates.length,3);});
for(const fase of ['antes','depois'])caso('criação incerta '+fase+' não é reenviada',()=>{const a=criar();a.rt.hook=f=>{if(f===fase)throw Error('queda');};assert.throws(a.run,/queda/);const n=a.rt.creates.length;a.rt.hook=null;assert.throws(a.run,/incerta/);assert.equal(a.rt.creates.length,n);assert.equal(a.script.get('salario_edicao'),undefined);});
for(const campo of ['usuario','projeto'])caso('troca de '+campo+' recusa',()=>{const a=criar();a.run();a.rt[campo]+='-outro';assert.throws(a.run,/execução diferente/);assert.equal(a.rt.creates.length,1);});
caso('não apaga rotina desconhecida',()=>{const a=criar();a.rt.triggers.push({});assert.throws(a.run,/rotinas visíveis/);assert.equal(a.rt.triggers.length,1);assert.equal(a.rt.creates.length,0);});
caso('perda de rotina registrada recusa sem recriar',()=>{const a=criar();a.run();a.rt.triggers=[];assert.throws(a.run,/rotina não registrada/);assert.equal(a.rt.creates.length,1);});
caso('resíduo ou configuração modificada recusa sem limpar',()=>{const a=criar();a.run();a.put('EXTRATO','A2','novo');assert.throws(a.run,/já foi usada/);assert.equal(a.rt.creates.length,1);});
caso('marca prematura recusa',()=>{const a=criar();a.run();a.script.set('salario_edicao',a.rt.projeto);assert.throws(a.run,/marca de edição/);assert.equal(a.rt.creates.length,1);});
caso('propriedade alheia modificada recusa',()=>{const a=criar();a.run();a.script.set('outra','mudou');assert.throws(a.run,/propriedades mudaram/);assert.equal(a.rt.creates.length,1);});
caso('diário adulterado recusa',()=>{const a=criar();a.run();const k=a.ctx.R53_NOVA_ATIVACAO_.diario,j=JSON.parse(a.doc.get(k));j.concluido=true;a.doc.set(k,JSON.stringify(j));assert.throws(a.run,/diário ou execução/);});
caso('sem conclusão das propriedades recusa',()=>{const a=criar();a.doc.delete(a.ctx.R53_NOVA_PROPS_.diario);assert.throws(a.run,/propriedades ainda/);assert.equal(a.rt.creates.length,0);});
caso('eventos só após concluir, com UID e fonte corretos',()=>{const a=criar(),chamadas=[];a.ctx.salarioRegistrarEdicao=e=>chamadas.push(e);a.run();a.run();const e={triggerUid:'id-2',source:a.ss};a.ctx.r53NovaCopiaSalarioEdicao(e);assert.equal(chamadas.length,0);a.done();a.ctx.r53NovaCopiaSalarioEdicao(e);assert.equal(chamadas.length,1);a.ctx.r53NovaCopiaSalarioEdicao({...e,triggerUid:'outro'});a.ctx.r53NovaCopiaSalarioEdicao({...e,source:{getId:()=> 'outro'}});assert.equal(chamadas.length,1);});
for(const fase of ['antes','depois'])caso('queda na marca final '+fase+' retoma sem recriar',()=>{
 const a=criar();a.run();a.run();a.run();let disparou=false;
 a.hook((f,t,k)=>{if(!disparou&&f===fase&&t==='propriedade'&&k==='script:salario_edicao'){disparou=true;throw Error('queda marca');}});
 assert.throws(a.run,/queda marca/);a.hook(null);assert(a.run().instalacaoLocalConcluida);assert.equal(a.rt.creates.length,3);
});
for(const fase of ['antes','depois'])caso('queda ao confirmar criação '+fase+' nunca duplica',()=>{
 const a=criar();let contador=0;
 a.hook((f,t,k)=>{if(f===fase&&t==='propriedade'&&k==='doc:'+a.ctx.R53_NOVA_ATIVACAO_.diario&&++contador===3)throw Error('queda diario');});
 assert.throws(a.run,/queda diario/);a.hook(null);
 const n=a.rt.creates.length;try{a.run();}catch(e){assert.match(e.message,/incerta/);}
 assert.equal(a.rt.creates.length,n+(fase==='depois'?1:0)); // confirmação durável pode avançar; criação incerta recusa.
 assert(a.rt.creates.length<=2);
});
for(const modo of ['tipo','fonte','nome','id'])caso('rotina adulterada '+modo+' recusa sem substituir',()=>{
 const a=criar();a.run();const t=a.rt.triggers[0];
 const f={tipo:'getEventType',fonte:'getTriggerSource',nome:'getHandlerFunction',id:'getUniqueId'}[modo];t[f]=()=> 'outro';
 assert.throws(a.run,/rotina/);assert.equal(a.rt.creates.length,1);
});
caso('marca removida após conclusão recusa e eventos não executam',()=>{
 const a=criar();a.done();a.script.delete('salario_edicao');assert.throws(a.run,/marca de edição removida/);
 const chamadas=[];a.ctx.salarioDiario=()=>chamadas.push(1);a.ctx.r53NovaCopiaSalarioDiario({triggerUid:'id-1'});assert.equal(chamadas.length,0);
});
for(const modo of ['oficial','modelo','cadastrada','responsavel'])caso('contexto inválido '+modo+' sem instalação',()=>{
 const a=criar();if(modo==='oficial'){a.ss.getId=()=>a.ctx.R53_NOVA_FIN_.oficiais[0];a.context.destino=a.ss.getId();}
 if(modo==='modelo')a.context.modelo=a.context.destino;
 if(modo==='cadastrada')a.context.arquivosRegistrados=[a.context.destino];
 if(modo==='responsavel')a.context.responsavelConfirmado=false;
 assert.throws(a.run,/cópia nova/);assert.equal(a.rt.creates.length,0);
});
caso('conferência de propriedades sem orçamento não autoriza instalar',()=>{const a=criar();a.ctx.r53NovaPerfilAplicarTravado_=()=>({concluido:false,retomar:true});assert.throws(a.run,/conferência das propriedades não terminou/);assert.equal(a.rt.creates.length,0);assert.equal(a.doc.get(a.ctx.R53_NOVA_ATIVACAO_.diario),undefined);});
caso('falha de preservação não publica diário ativo nem executa evento',()=>{
 const a=criar();a.run();a.run();a.run();const chamadas=[];
 a.ctx.salarioRegistrarEdicao=()=>chamadas.push(1);
 a.hook((fase,t,k)=>{
  if(fase==='depois'&&t==='propriedade'&&k==='script:salario_edicao')a.script.set('concorrente','alterada');
  if(fase==='depois'&&t==='propriedade'&&k==='doc:'+a.ctx.R53_NOVA_ATIVACAO_.diario){
   const j=JSON.parse(a.doc.get(a.ctx.R53_NOVA_ATIVACAO_.diario));
   if(j.concluido)a.ctx.r53NovaCopiaSalarioEdicao({triggerUid:'id-2',source:a.ss});
  }
 });
 assert.throws(a.run,/preservação/);a.hook(null);
 assert.equal(JSON.parse(a.doc.get(a.ctx.R53_NOVA_ATIVACAO_.diario)).concluido,false);
 assert.equal(chamadas.length,0);assert.equal(a.rt.creates.length,3);
});
function prepararLento(a, atraso=180000) {
 let tempo=0; a.ctx.Date={now:()=>tempo};
 const salvar=a.ctx.r53NovaAtivacaoSalvar_;
 a.ctx.r53NovaAtivacaoSalvar_=(dp,j)=>{salvar(dp,j);tempo=atraso;};
 const r=a.run(); a.ctx.r53NovaAtivacaoSalvar_=salvar;
 return r;
}
caso('preparo lento persiste sem criar e retoma sem refazer propriedades',()=>{
 const a=criar(),r=prepararLento(a);
 assert.equal(r.rotinasInstaladasNestaConta,0);assert.equal(r.retomar,true);
 assert.equal(r.instalacaoLocalConcluida,false);assert.equal(a.rt.creates.length,0);
 assert.equal(a.locked(),false);
 assert.equal(a.script.get('salario_edicao'),undefined);
 for(const k of ['criacaoDisponivel','financeiroConcluido','ativacaoConcluida','responsavelVerificadoPeloBot'])assert.equal(r[k],false);
 a.ctx.r53NovaPerfilAplicarTravado_=()=>{throw Error('não repetir propriedades');};
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../inicializacao/ativacao.gs'),'utf8'),a.ctx);
 a.done();assert.equal(a.rt.creates.length,3);
});
caso('preparo abaixo do orçamento mantém a primeira instalação na mesma chamada',()=>{
 const a=criar(),r=prepararLento(a,179999);
 assert.equal(r.rotinasInstaladasNestaConta,1);assert.equal(a.rt.creates.length,1);
 assert.equal(r.retomar,true);assert.equal(a.locked(),false);
});
caso('preparo lento não autoriza eventos nem ignora edição na retomada',()=>{
 const a=criar();prepararLento(a);let chamadas=0;a.ctx.salarioRegistrarEdicao=()=>chamadas++;
 a.ctx.r53NovaCopiaSalarioEdicao({triggerUid:'id-2',source:a.ss});assert.equal(chamadas,0);
 a.put('EXTRATO','A2','edição posterior');assert.throws(a.run,/já foi usada/);
 assert.equal(a.rt.creates.length,0);
});
caso('preparo lento não adota rotina alheia na retomada',()=>{
 const a=criar();prepararLento(a);a.rt.triggers.push({});
 assert.throws(a.run,/rotina não registrada/);assert.equal(a.rt.creates.length,0);
});
// ---- Pulso de ativação (metadados de desenvolvedor DOCUMENT) ----
const CAMPOS_PULSO=['arquivo','operacao','quando','rotina','sequencia'];
const itensPulso=(a,r)=>{const m=a.meta.filter(x=>x.key==='r53_pulso_'+r);assert(m.length<=1);return m.length?JSON.parse(m[0].value).itens:[];};
function relogio(a,t0=1800000000000){const r={t:t0};a.ctx.Date={now:()=>r.t};return r;}
caso('pulso de instalação só depois da conclusão, visível ao bot, e repetição não grava',()=>{
 const a=criar();a.run();a.run();a.run();assert.equal(a.meta.length,0);
 const r=a.run();assert.equal(r.instalacaoLocalConcluida,true);assert.equal(r.pulsoInstalacaoPresente,true);
 assert.equal(a.meta.length,1);assert.equal(a.meta[0].vis,'DOCUMENT');
 const [p]=itensPulso(a,'instalacao');assert.deepEqual(Object.keys(p).sort(),CAMPOS_PULSO);
 assert.equal(p.rotina,'instalacao');assert.equal(p.operacao,a.context.operacao);assert.equal(p.arquivo,a.ss.getId());assert.equal(p.sequencia,1);
 const w=a.writes.length;assert.equal(a.run().pulsoInstalacaoPresente,true);assert.equal(a.writes.length,w);assert.equal(a.meta.length,1);
});
caso('falha ao gravar o pulso de instalação não desfaz a instalação e a repetição grava',()=>{
 const a=criar();a.run();a.run();a.run();const f=a.ss.createDeveloperMetadataFinder;a.ss.createDeveloperMetadataFinder=()=>{throw Error('metadado indisponível');};
 const r=a.run();assert.equal(r.instalacaoLocalConcluida,true);assert.equal(r.pulsoInstalacaoPresente,false);assert.equal(a.meta.length,0);
 a.ss.createDeveloperMetadataFinder=f;assert.equal(a.run().pulsoInstalacaoPresente,true);assert.equal(a.meta.length,1);assert.equal(a.rt.creates.length,3);
});
caso('pulso de evento só depois do trabalho concluir, com o formato esperado',()=>{
 const a=criar();a.done();const vistos=[];
 for(const [nome,fn,uid] of [['diario','salarioDiario','id-1'],['edicao','salarioRegistrarEdicao','id-2'],['abertura','salarioAposAbrir','id-3']])
  a.ctx[fn]=()=>vistos.push([nome,itensPulso(a,nome).length]);
 const ck=json([...a.cells]),dp=a.doc.get(a.ctx.R53_NOVA_ATIVACAO_.diario),sp=json([...a.script]),r=relogio(a);
 const ev={triggerUid:'id-2',source:a.ss};
 a.ctx.r53NovaCopiaSalarioDiario({triggerUid:'id-1'});a.ctx.r53NovaCopiaSalarioEdicao(ev);a.ctx.r53NovaCopiaSalarioAbrir({triggerUid:'id-3',source:a.ss});
 assert.deepEqual(vistos,[['diario',0],['edicao',0],['abertura',0]]);
 for(const n of ['diario','edicao','abertura']){const [p]=itensPulso(a,n);assert.deepEqual(Object.keys(p).sort(),CAMPOS_PULSO);
  assert.equal(p.rotina,n);assert.equal(p.sequencia,1);assert.equal(p.quando,1800000000);assert.equal(p.arquivo,a.ss.getId());assert.equal(p.operacao,a.context.operacao);
  assert(/^[A-Za-z0-9_-]{1,128}$/.test(p.operacao)&&/^[A-Za-z0-9_-]{1,128}$/.test(p.arquivo));}
 assert(a.meta.every(m=>m.vis==='DOCUMENT'));
 assert.deepEqual(json([...a.cells]),ck);assert.deepEqual(json([...a.script]),sp);assert.equal(a.doc.get(a.ctx.R53_NOVA_ATIVACAO_.diario),dp);
 assert(a.run().instalacaoLocalConcluida);assert.equal(a.rt.creates.length,3);// preservação continua batendo
});
caso('sequência do diário cresce e edição/abertura respeitam o intervalo',()=>{
 const a=criar();a.done();a.ctx.salarioDiario=()=>{};a.ctx.salarioRegistrarEdicao=()=>{};const r=relogio(a);const ev={triggerUid:'id-2',source:a.ss};
 for(let i=0;i<7;i++){a.ctx.r53NovaCopiaSalarioDiario({triggerUid:'id-1'});r.t+=86400000;}
 const d=itensPulso(a,'diario');assert.equal(d.length,5);assert.deepEqual(d.map(p=>p.sequencia),[3,4,5,6,7]);
 a.ctx.r53NovaCopiaSalarioEdicao(ev);r.t+=60000;a.ctx.r53NovaCopiaSalarioEdicao(ev);assert.equal(itensPulso(a,'edicao').length,1);
 r.t+=600000;a.ctx.r53NovaCopiaSalarioEdicao(ev);assert.deepEqual(itensPulso(a,'edicao').map(p=>p.sequencia),[1,2]);
});
caso('erro no trabalho não gera pulso e o erro sobe',()=>{
 const a=criar();a.done();a.ctx.salarioRegistrarEdicao=()=>{throw Error('falha salarial');};
 assert.throws(()=>a.ctx.r53NovaCopiaSalarioEdicao({triggerUid:'id-2',source:a.ss}),/falha salarial/);assert.equal(itensPulso(a,'edicao').length,0);
});
caso('antes da conclusão, ou com UID/fonte errados, nenhum pulso',()=>{
 const a=criar();a.run();a.run();a.ctx.salarioRegistrarEdicao=()=>{};
 a.ctx.r53NovaCopiaSalarioEdicao({triggerUid:'id-2',source:a.ss});assert.equal(a.meta.length,0);
 a.done();a.ctx.r53NovaCopiaSalarioEdicao({triggerUid:'outro',source:a.ss});a.ctx.r53NovaCopiaSalarioEdicao({triggerUid:'id-2',source:{getId:()=>'outro'}});
 assert.equal(a.meta.filter(m=>m.key!=='r53_pulso_instalacao').length,0);
});
caso('falha do pulso, trava ocupada ou pulso ilegível não quebram o evento nem são sobrescritos',()=>{
 const a=criar();a.done();let n=0;a.ctx.salarioRegistrarEdicao=()=>++n;a.ctx.salarioDiario=()=>++n;a.ctx.salarioAposAbrir=()=>++n;relogio(a);
 const ev={triggerUid:'id-2',source:a.ss},f=a.ss.createDeveloperMetadataFinder,lk=a.ctx.LockService;
 a.ss.createDeveloperMetadataFinder=()=>{throw Error('sem metadado');};assert.equal(a.ctx.r53NovaCopiaSalarioEdicao(ev),1);
 a.ss.createDeveloperMetadataFinder=f;a.ctx.LockService={getDocumentLock:()=>({tryLock:()=>false,releaseLock(){throw Error('não deveria soltar');}})};
 assert.equal(a.ctx.r53NovaCopiaSalarioEdicao(ev),2);assert.equal(itensPulso(a,'edicao').length,0);
 a.ctx.LockService=lk;a.meta.push({key:'r53_pulso_diario',value:'{lixo',vis:'DOCUMENT'});
 a.ctx.r53NovaCopiaSalarioDiario({triggerUid:'id-1'});assert.equal(a.meta.find(m=>m.key==='r53_pulso_diario').value,'{lixo');
 a.meta.push({key:'r53_pulso_abertura',value:'{"versao":1,"itens":[]}',vis:'DOCUMENT'},{key:'r53_pulso_abertura',value:'{"versao":1,"itens":[]}',vis:'DOCUMENT'});
 a.ctx.r53NovaCopiaSalarioAbrir({triggerUid:'id-3',source:a.ss});assert(a.meta.filter(m=>m.key==='r53_pulso_abertura').every(m=>m.value==='{"versao":1,"itens":[]}'));
 assert.equal(a.locked(),false);
});
caso('pulso invisível ao bot (PROJECT) não é aceito como existente',()=>{
 const a=criar();a.meta.push({key:'r53_pulso_instalacao',value:'{"versao":1,"itens":[]}',vis:'PROJECT'});
 a.done();assert.equal(a.meta.filter(m=>m.vis==='DOCUMENT'&&m.key==='r53_pulso_instalacao').length,1);
});
console.log(`${casos} cenários de ativação local aprovados; sem evento Google real ou atestado ao backend.`);
