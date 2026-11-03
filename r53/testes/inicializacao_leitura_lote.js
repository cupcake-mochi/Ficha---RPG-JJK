'use strict';
// Só VM offline. Conta chamadas de leitura; não mede latência do Google.
// Sonda nativa de 03/11: ~3 s por chamada lenta, quase sem depender do tamanho.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {ambiente}=require('./apoio_inicializacao');
let casos=0;function caso(n,f){try{f();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
const LEITURAS=['getFormulas','getValues','getNotes'];
function contar(a){
 const c={n:0};
 for(const[nome,sh]of Object.entries(a.sheets)){const orig=sh.getRange;sh.getRange=addr=>{const r=orig(addr);
  for(const m of LEITURAS){const f=r[m];r[m]=()=>{c.n++;return f();};}return r;};}
 return c;
}
function criar(op={}){
 const a=ambiente(op);if(!op.sujo)a.complete(a.preview());
 for(const k of a.ctx.R53_NOVA_FIN_.propriedadesDocumento)a.doc.set(k,'DADO_PRIVADO_'+k);
 for(const k of a.ctx.R53_NOVA_FIN_.propriedadesScript)a.script.set(k,'DADO_PRIVADO_'+k);
 const rt={projeto:'projeto_sintetico_0001',usuario:'execucao_sintetica',triggers:[],creates:0};
 a.ctx.ScriptApp={getScriptId:()=>rt.projeto,getProjectTriggers:()=>rt.triggers,
  EventType:{CLOCK:'CLOCK',ON_EDIT:'ON_EDIT',ON_OPEN:'ON_OPEN'},TriggerSource:{CLOCK:'CLOCK',SPREADSHEETS:'SPREADSHEETS'},
  newTrigger(nome){let tipo,src;const b={timeBased(){tipo='CLOCK';src='CLOCK';return b;},everyDays(){return b;},atHour(){return b;},inTimezone(){return b;},
   forSpreadsheet(s){src=s.getId();return b;},onEdit(){tipo='ON_EDIT';return b;},onOpen(){tipo='ON_OPEN';return b;},create(){const id='id-'+(++rt.creates);
   const t={getUniqueId:()=>id,getHandlerFunction:()=>nome,getEventType:()=>tipo,getTriggerSource:()=>tipo==='CLOCK'?'CLOCK':'SPREADSHEETS',getTriggerSourceId:()=>src};rt.triggers.push(t);return t;}};return b;},
  deleteTrigger(){throw Error('não apagar rotinas');}};
 a.ctx.Session={getTemporaryActiveUserKey:()=>rt.usuario};
 for(const f of ['propriedades.gs','ativacao.gs'])vm.runInContext(fs.readFileSync(path.join(__dirname,'../inicializacao',f),'utf8'),a.ctx);
 a.writes.length=0;a.rt=rt;
 a.pp=()=>a.ctx.r53NovaFichaPropriedadesPrevia(a.ss,a.context);
 a.pa=p=>a.ctx.r53NovaFichaPropriedadesAplicar(a.ss,a.context,p.assinatura);
 return a;
}
// Oráculo: as leituras separadas de antes do lote, mantidas aqui só para comparar.
function oraculoCelulas(a){return a.ctx.r53NovaFinOperacoes_(a.ss).filter(op=>op.tipo!=='propriedade').map(op=>a.ctx.r53NovaFinLer_(a.ss,op));}
function oraculoGuardas(a){
 const c=a.ctx,esperadas=c.r53NovaFinFormulas_();
 const saida=c.R53_NOVA_FIN_.formulas.map((x,i)=>{const f=a.ss.getSheetByName(x[0]).getRange(x[1]).getFormulas();
  assert.equal(f.length,esperadas[i].length);return [x[0],x[1],f];});
 saida.push(['nivel',c.r53NovaFinLer_(a.ss,{aba:'FICHA',faixa:'AH11'})]);
 saida.push(['campanha',c.r53NovaFinLer_(a.ss,{aba:'CONFIGURAÇÃO',faixa:'E46:G46'})]);
 return saida;
}
function lote(a){const c=a.ctx,ops=c.r53NovaFinOperacoes_(a.ss).filter(op=>op.tipo!=='propriedade');
 return {ops,l:c.r53NovaFinLote_(a.ss,c.r53NovaFinPedidos_(ops).concat(c.r53NovaFinGuardasPedidos_()))};}
const json=x=>JSON.parse(JSON.stringify(x));
function sujar(a){
 a.put('EXTRATO','B5',-500,'','nota de lançamento');a.put('SALÁRIOS','L7',new Date(46000*864e5));
 a.put('DADOS_SALARIOS','N2',46000);a.put('DADOS_SALARIOS','J9','troca');a.put('DADOS_SALARIOS','K3','fora do contrato');
 a.put('FICHA PESSOAL','BD40','Padrão','','[Salário: id · data]');a.put('FICHA PESSOAL','O86',-500);a.put('FICHA PESSOAL','BA20',99,'=XP()');
 a.put('FICHA PESSOAL','BI11','missão');a.put('FICHA PESSOAL','BO11','03/11/2026');a.put('CONFIGURAÇÃO','O39',true);a.put('CARTEIRA','AT3',true);
}
for(const modo of ['limpa','suja','5000 linhas'])caso('lote devolve o mesmo que as leituras separadas · '+modo,()=>{
 const a=criar(modo==='5000 linhas'?{rows:5000}:{});if(modo==='suja')sujar(a);
 const {ops,l}=lote(a);
 assert.deepEqual(json(ops.map(op=>a.ctx.r53NovaFinLerDoLote_(l,op))),json(oraculoCelulas(a)));
 assert.deepEqual(json(a.ctx.r53NovaFinGuardas_(a.ss,l)),json(oraculoGuardas(a)));
 assert.deepEqual(json(a.ctx.r53NovaFinGuardas_(a.ss)),json(oraculoGuardas(a)));
 assert.equal(a.writes.length,0);
});
caso('fórmula em entrada sai como fórmula e valor nulo, igual à leitura separada',()=>{
 const a=criar();a.put('FICHA PESSOAL','AY30',3,'=1+2');const {ops,l}=lote(a);
 const i=ops.findIndex(op=>op.faixa==='AW15:AZ87'&&op.tipo!=='notas'),r=a.ctx.r53NovaFinLerDoLote_(l,ops[i]);
 assert.equal(r.formulas[15][2],'=1+2');assert.equal(r.valores[15][2],null);
});
caso('imagem no lote é recusada como antes',()=>{const a=criar();a.put('FICHA PESSOAL','O86',{valueType:'IMAGE'});
 const {ops,l}=lote(a);assert.throws(()=>ops.forEach(op=>a.ctx.r53NovaFinLerDoLote_(l,op)),/imagem ou valor/);});
caso('aba ausente mantém a mensagem de cada leitura',()=>{
 const a=criar();delete a.sheets['CARTEIRA'];const {ops,l}=lote(a);
 assert.throws(()=>ops.forEach(op=>a.ctx.r53NovaFinLerDoLote_(l,op)),/falta uma aba do contrato financeiro/);
 const b=criar();delete b.sheets['FICHA'];assert.throws(()=>b.ctx.r53NovaFinGuardas_(b.ss),/falta uma aba/);
});
caso('faixa fora do pedido é recusada',()=>{const a=criar(),{l}=lote(a);
 assert.throws(()=>l('FICHA PESSOAL','A1','v','x'),/fora do pedido/);assert.throws(()=>l('EXTRATO','A2:C10','x','x'),/fora do pedido/);});
caso('preservação completa: 18 chamadas, antes 46',()=>{
 const a=criar(),c=contar(a);oraculoCelulas(a);oraculoGuardas(a);const antes=c.n;c.n=0;
 a.ctx.r53NovaPropsPreservados_(a.ss);assert.equal(c.n,18);c.n=0;a.ctx.r53NovaAtivacaoPreservados_(a.ss);assert.equal(c.n,18);
 assert.equal(antes,46);c.n=0;a.ctx.r53NovaFinGuardas_(a.ss);assert.equal(c.n,7);
});
caso('hash da preservação não muda com o lote',()=>{
 const a=criar(),c=a.ctx,h=c.r53NovaFinHash_;
 const ops=c.r53NovaFinOperacoes_(a.ss).filter(op=>op.tipo!=='propriedade');
 const celulas=oraculoCelulas(a).map(x=>h(x)),guardas=oraculoGuardas(a);
 const d=Object.fromEntries(a.doc),s=Object.fromEntries(a.script);
 const outras=[Object.keys(d).sort().filter(k=>k!==c.R53_NOVA_ATIVACAO_.diario).map(k=>[k,h(d[k])]),
  Object.keys(s).sort().filter(k=>k!=='salario_edicao').map(k=>[k,h(s[k])])];
 assert.equal(ops.length,celulas.length);assert.equal(c.r53NovaAtivacaoPreservados_(a.ss),h([guardas,celulas,outras]));
});
function leiturasCompletas(a){const r={n:0};for(const k of ['r53NovaPropsPreservados_','r53NovaAtivacaoPreservados_']){const f=a.ctx[k];a.ctx[k]=ss=>{r.n++;return f(ss);};}return r;}
caso('propriedades: aplicar novo faz 2 leituras completas (antes 3); retomada sem escrita faz 1',()=>{
 const a=criar(),p=a.pp(),r=leiturasCompletas(a);a.ctx.R53_NOVA_PROPS_.escritasPorExecucao=5;
 assert(a.pa(p).concluido);assert.equal(r.n,2);r.n=0;assert(a.pa(p).concluido);assert.equal(r.n,1);
 assert.equal(a.writes.filter(([t])=>t==='excluirPropriedade').length,5);
});
function relogio(a,custo){const t={v:0};a.ctx.Date={now:()=>t.v};const f=a.ctx.r53NovaPropsPreservados_;
 a.ctx.r53NovaPropsPreservados_=ss=>{t.v+=custo;return f(ss);};return t;}
caso('orçamento reserva a conferência final: leitura lenta devolve retomar antes de ler de novo',()=>{
 const a=criar(),p=a.pp();a.ctx.R53_NOVA_PROPS_.escritasPorExecucao=5;const t=relogio(a,120000),r=leiturasCompletas(a);
 const x=a.pa(p);assert.equal(x.concluido,false);assert.equal(x.retomar,true);assert.equal(r.n,1);
 assert.equal(a.writes.filter(([k])=>k==='excluirPropriedade').length,5);
 t.v=0;r.n=0;const y=a.pa(p);assert(y.concluido);assert.equal(r.n,1);
});
caso('orçamento com leitura rápida conclui numa chamada',()=>{
 const a=criar(),p=a.pp();a.ctx.R53_NOVA_PROPS_.escritasPorExecucao=5;relogio(a,50000);assert(a.pa(p).concluido);
});
caso('orçamento logo abaixo do limite ainda confere; no limite devolve retomar',()=>{
 for(const[custo,conclui]of [[104999,true],[105000,false]]){const a=criar(),p=a.pp();a.ctx.R53_NOVA_PROPS_.escritasPorExecucao=5;relogio(a,custo);assert.equal(a.pa(p).concluido,conclui,String(custo));}
});
caso('ativação: primeira chamada rápida faz 3 leituras completas e já cria a 1ª rotina',()=>{
 const a=criar(),p=a.pp();for(let i=0;i<5&&!a.pa(p).concluido;i++);const r=leiturasCompletas(a);
 const x=a.ctx.r53NovaFichaAtivacaoAplicar(a.ss,a.context);assert.equal(x.rotinasInstaladasNestaConta,1);assert.equal(r.n,3);
 r.n=0;a.ctx.r53NovaFichaAtivacaoAplicar(a.ss,a.context);assert.equal(r.n,2);
});
caso('ativação: captura lenta reserva a conferência e para antes de criar',()=>{
 const a=criar(),p=a.pp();for(let i=0;i<5&&!a.pa(p).concluido;i++);
 const t={v:0};a.ctx.Date={now:()=>t.v};const f=a.ctx.r53NovaAtivacaoPreservados_;a.ctx.r53NovaAtivacaoPreservados_=ss=>{t.v+=90000;return f(ss);};
 const x=a.ctx.r53NovaFichaAtivacaoAplicar(a.ss,a.context);assert.equal(x.rotinasInstaladasNestaConta,0);assert.equal(x.retomar,true);assert.equal(a.rt.creates,0);
});
console.log(`${casos} cenários de leitura em lote aprovados; contagem de chamadas na VM, latência só medida no Google.`);
