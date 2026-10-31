'use strict';
// Só VM offline. Não afirma identidade Google, evento real ou ativação instalada.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {ambiente}=require('./apoio_inicializacao');
const fonte=fs.readFileSync(path.join(__dirname,'../inicializacao/propriedades.gs'),'utf8');
let casos=0;function caso(nome,fn){try{fn();casos++;}catch(e){e.message=nome+': '+e.message;throw e;}}
function criar(op={}){
 const a=ambiente(op);if(!op.sujo)a.complete(a.preview());a.writes.length=0;
 // Estado REST: células já limpas, mas as cinco propriedades ainda não tratadas.
 for(const k of a.ctx.R53_NOVA_FIN_.propriedadesDocumento)a.doc.set(k,'DADO_PRIVADO_'+k);
 for(const k of a.ctx.R53_NOVA_FIN_.propriedadesScript)a.script.set(k,'DADO_PRIVADO_'+k);
 const rt={projeto:'projeto_sintetico_0001',usuario:'chave_temporaria_privada',triggers:[]};
 a.ctx.ScriptApp={getScriptId:()=>rt.projeto,getProjectTriggers:()=>rt.triggers,
  EventType:{CLOCK:'CLOCK',ON_EDIT:'ON_EDIT',ON_OPEN:'ON_OPEN'},TriggerSource:{CLOCK:'CLOCK',SPREADSHEETS:'SPREADSHEETS'},
  newTrigger(){throw Error('não pode criar acionador');},deleteTrigger(){throw Error('não pode apagar acionador');}};
 a.ctx.Session={getTemporaryActiveUserKey:()=>rt.usuario};vm.runInContext(fonte,a.ctx);
 a.pp=()=>a.ctx.r53NovaFichaPropriedadesPrevia(a.ss,a.context);
 a.pa=p=>a.ctx.r53NovaFichaPropriedadesAplicar(a.ss,a.context,p.assinatura);
 a.pc=p=>{for(let i=0;i<10;i++){const r=a.pa(p);if(r.concluido)return r;assert(r.retomar);}throw Error('não terminou');};
 a.inspecao=()=>a.ctx.r53NovaFichaAtivacaoConferir(a.ss,a.context);return Object.assign(a,{rt});
}
const json=x=>JSON.parse(JSON.stringify(x));
caso('prévia sem escrita nem valores privados',()=>{const a=criar(),p=a.pp();assert.equal(p.alteracoes,5);assert.equal(p.dominio,'propriedades_financeiras');assert.equal(a.writes.length,0);assert(!JSON.stringify(p).includes('DADO_PRIVADO'));assert(!JSON.stringify(p).includes(a.rt.usuario));});
caso('limpa apenas cinco chaves, preserva células, propriedades alheias e diário antigo',()=>{
 const a=criar(),cells=json([...a.cells]),doc=json([...a.doc].filter(([k])=>!a.ctx.R53_NOVA_FIN_.propriedadesDocumento.includes(k))),script=json([...a.script].filter(([k])=>!a.ctx.R53_NOVA_FIN_.propriedadesScript.includes(k))),p=a.pp(),r=a.pc(p);
 assert(r.propriedadesPreparadas);for(const k of ['criacaoDisponivel','ativacaoConcluida','financeiroConcluido','responsavelVerificadoPeloBot'])assert.equal(r[k],false);
 assert.deepEqual(json([...a.cells]),cells);
 for(const[k,v]of doc)assert.equal(a.doc.get(k),v);for(const[k,v]of script)assert.equal(a.script.get(k),v);
 assert.equal(a.writes.filter(([t])=>t==='excluirPropriedade').length,5);assert(a.writes.every(([t])=>['propriedade','excluirPropriedade'].includes(t)));
 const j=a.doc.get(a.ctx.R53_NOVA_PROPS_.diario);assert(!/DADO_PRIVADO|chave_temporaria_privada/.test(j));assert(Buffer.byteLength(j)<9000);
 const n=a.writes.length;a.pc(p);assert.equal(a.writes.length,n);
});
caso('passos limitados e retomada',()=>{const a=criar(),p=a.pp();a.ctx.R53_NOVA_PROPS_.escritasPorExecucao=1;const r=a.pa(p);assert(!r.concluido);assert(r.retomar);assert(!r.propriedadesPreparadas);a.pc(p);assert(!a.locked());});
const base=criar();base.pc(base.pp());
for(let i=1;i<=base.writes.length;i++)for(const fase of ['antes','depois'])caso(`queda ${fase} ${i}`,()=>{
 const a=criar(),p=a.pp();let n=0;a.hook(f=>{if(f===fase&&++n===i)throw Error('queda');});assert.throws(()=>a.pc(p),/queda/);assert(!a.locked());a.hook(null);a.pc(p);assert.equal(a.writes.filter(([t])=>t==='excluirPropriedade').length,5);
});
caso('células sujas não são limpas por este domínio',()=>{const a=criar({sujo:true});assert.throws(()=>a.pp(),/células financeiras/);assert.equal(a.writes.length,0);});
for(const[k,valor]of [['EXTRATO','resíduo'],['SALÁRIOS','resíduo'],['DADOS_SALARIOS','resíduo']])caso('resíduo '+k,()=>{const a=criar();a.put(k,'A2',valor);assert.throws(()=>a.pp(),/células financeiras/);assert.equal(a.writes.length,0);});
caso('nota residual impede limpar propriedades',()=>{const a=criar();a.put('FICHA PESSOAL','AW15','','','resíduo');assert.throws(()=>a.pp(),/células financeiras/);assert.equal(a.writes.length,0);});
caso('propriedade alheia alterada após a prévia recusa sem apagar',()=>{const a=criar(),p=a.pp();a.script.set('paleta','mudou');assert.throws(()=>a.pa(p),/mudou após/);assert.equal(a.writes.length,0);});
caso('resíduo novo após conclusão nunca volta a ser apagado',()=>{const a=criar(),p=a.pp();a.pc(p);a.doc.set('salario_extrato','nova');const n=a.writes.length;assert.throws(()=>a.pa(p),/editados|já foi usada/);assert.equal(a.doc.get('salario_extrato'),'nova');assert.equal(a.writes.length,n);});
for(const campo of ['usuario','projeto'])caso('outra execução '+campo,()=>{const a=criar(),p=a.pp();a.rt[campo]+='_outra';assert.throws(()=>a.pa(p),/mudou após/);assert.equal(a.writes.length,0);});
caso('vínculo sem chave de execução recusa',()=>{const a=criar();a.rt.usuario='';assert.throws(()=>a.pp(),/vincular/);assert.equal(a.writes.length,0);});
caso('rotina visível impede limpeza e não é apagada',()=>{const a=criar();a.rt.triggers=[{}];assert.throws(()=>a.pp(),/rotinas visíveis/);assert.equal(a.writes.length,0);assert.equal(a.rt.triggers.length,1);});
caso('rotina criada durante pausa impede retomada',()=>{const a=criar(),p=a.pp();a.ctx.R53_NOVA_PROPS_.escritasPorExecucao=1;a.pa(p);a.rt.triggers=[{}];const n=a.writes.length;assert.throws(()=>a.pa(p),/rotinas visíveis/);assert.equal(a.writes.length,n);});
for(const id of ['1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k','1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw'])caso('oficial recusada '+id.slice(0,4),()=>{const a=criar();a.ss.getId=()=>id;a.context.destino=id;assert.throws(()=>a.pp(),/cópia nova/);assert.equal(a.writes.length,0);});
for(const[k,v]of [['responsavelConfirmado',false],['copiaNovaConfirmada',false],['arquivosRegistrados',['copia-descartavel']]])caso('contexto inválido '+k,()=>{const a=criar();a.context[k]=v;assert.throws(()=>a.pp(),/cópia nova/);assert.equal(a.writes.length,0);});
function trigger(nome,tipo,origem='SPREADSHEETS',id='copia-descartavel'){return{getHandlerFunction:()=>nome,getEventType:()=>tipo,getTriggerSource:()=>origem,getTriggerSourceId:()=>id};}
function instalados(a){a.rt.triggers=[trigger('salarioDiario','CLOCK','CLOCK'),trigger('salarioRegistrarEdicao','ON_EDIT'),trigger('salarioAposAbrir','ON_OPEN')];a.script.set('salario_edicao',a.rt.projeto);}
caso('inspeção vazia não significa ativação e não escreve',()=>{const a=criar();a.script.delete('salario_edicao');const r=a.inspecao();assert.equal(r.rotinasVisiveis,0);assert(r.marcaAusente);assert(!r.rotinasVisiveisCompativeis);assert(!r.ativacaoConcluida);assert.equal(a.writes.length,0);});
caso('três rotinas visíveis e marca correta continuam sem atestado ao backend',()=>{const a=criar();instalados(a);const r=a.inspecao();assert(r.rotinasVisiveisCompativeis);assert(r.marcaDoProjetoAtual);for(const k of ['criacaoDisponivel','ativacaoConcluida','financeiroConcluido','responsavelVerificadoPeloBot'])assert.equal(r[k],false);assert.equal(a.writes.length,0);assert(!JSON.stringify(r).includes(a.rt.projeto));});
for(const modo of ['arquivo','evento','duplicada','desconhecida','marca'])caso('inspeção detecta '+modo,()=>{const a=criar();instalados(a);if(modo==='arquivo')a.rt.triggers[1]=trigger('salarioRegistrarEdicao','ON_EDIT','SPREADSHEETS','outro');if(modo==='evento')a.rt.triggers[1]=trigger('salarioRegistrarEdicao','ON_OPEN');if(modo==='duplicada')a.rt.triggers.push(a.rt.triggers[0]);if(modo==='desconhecida')a.rt.triggers[0]=trigger('__proto__','CLOCK','CLOCK');if(modo==='marca')a.script.set('salario_edicao','outro');const r=a.inspecao();assert(!(r.rotinasVisiveisCompativeis&&r.marcaDoProjetoAtual));assert(!r.ativacaoConcluida);assert.equal(a.writes.length,0);});
caso('chaves já ausentes não são excluídas outra vez',()=>{const a=criar();for(const k of a.ctx.R53_NOVA_FIN_.propriedadesDocumento)a.doc.delete(k);for(const k of a.ctx.R53_NOVA_FIN_.propriedadesScript)a.script.delete(k);const p=a.pp();assert.equal(p.alteracoes,0);assert(a.pc(p).propriedadesPreparadas);assert(!a.writes.some(([t])=>t==='excluirPropriedade'));});
caso('propriedade alvo editada durante pausa recusa sem apagá-la',()=>{const a=criar(),p=a.pp();a.ctx.R53_NOVA_PROPS_.escritasPorExecucao=1;a.pa(p);a.doc.set('salario_trocas','valor novo de outra ação');const n=a.writes.length;assert.throws(()=>a.pa(p),/editados/);assert.equal(a.doc.get('salario_trocas'),'valor novo de outra ação');assert.equal(a.writes.length,n);});
caso('mudança alheia durante aplicação deixa diário incompleto',()=>{const a=criar();a.ctx.R53_NOVA_PROPS_.escritasPorExecucao=5;const p=a.pp();a.hook((f,t)=>{if(f==='depois'&&t==='excluirPropriedade')a.script.set('paleta','mudança concorrente');});assert.throws(()=>a.pc(p),/pós-condição/);a.hook(null);assert.equal(JSON.parse(a.doc.get(a.ctx.R53_NOVA_PROPS_.diario)).concluido,false);assert.equal(a.script.get('paleta'),'mudança concorrente');const n=a.writes.length;assert.throws(()=>a.pa(p),/estrutura, fórmula ou configuração/);assert.equal(a.writes.length,n);});
caso('documento vinculado diferente recusa sem escrever',()=>{const a=criar();a.ctx.SpreadsheetApp.getActive=()=>({getId:()=> 'outro'});assert.throws(()=>a.pp(),/documento vinculado/);assert.equal(a.writes.length,0);});
caso('assinatura do financeiro não autoriza propriedades',()=>{const a=criar(),p=JSON.parse(a.doc.get(a.ctx.R53_NOVA_FIN_.diario));assert.throws(()=>a.pa(p),/mudou após/);assert.equal(a.writes.length,0);});
console.log(`${casos} cenários de propriedades e inspeção aprovados; sem ativação nativa ou liberação da criação.`);
