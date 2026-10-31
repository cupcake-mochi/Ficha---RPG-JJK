'use strict';
// V8/serviços em VM. Não prova versão Drive, cálculo ou execução nativa remota.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const {preparado}=require('./inicializacao_sequencia');
const sources=['conferencia','conferencia_paginas'].map(n=>new vm.Script(fs.readFileSync(path.resolve(__dirname,'../inicializacao/'+n+'.gs'),'utf8')));
let casos=0;function caso(n,fn){try{fn();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
function ambiente(op={}){
 const a=preparado(op);for(const s of sources)s.runInContext(a.ctx);
 if(op.recuperacoes)for(let i=0;i<op.recuperacoes;i++)a.doc.set('r53_recuperacao_'+(1793037909500+i),'PRIVADO');
 a.p=a.previa();if(!op.incompleta)a.concluir(a.p);
 a.plano=()=>a.ctx.r53NovaFichaConferenciaPlano(a.ss,a.context,a.p.assinatura);
 a.pagina=(p,i)=>a.ctx.r53NovaFichaConferenciaPagina(a.ss,a.context,a.p.assinatura,p.assinatura,i);
 return a;
}
function somenteLeitura(a,fn){const d=new Map(a.doc),s=new Map(a.script),c=new Map(a.cells),w=a.writes.length;const r=fn();assert.equal(a.writes.length,w);assert.deepEqual(a.doc,d);assert.deepEqual(a.script,s);assert.deepEqual(a.cells,c);assert(!a.locked());return r;}
function privado(r){const texto=JSON.stringify(r);assert(!/PRIVADO|SEGREDO|copia-descartavel|modelo-sintetico/.test(texto));for(const k of ['criacaoDisponivel','conferenciaConjuntaConcluida','imagensAtuaisConferidas','consistenciaTemporalVerificada'])assert.equal(r[k],false);}
module.exports={ambiente};
if(require.main===module){
caso('plano e página não escrevem sequer checkpoint, têm esquema fixo privado',()=>{
 const a=ambiente(),p=somenteLeitura(a,()=>a.plano());assert.equal(p.protocolo,'carteira-conferencia-pagina-1');assert.equal(p.perfis,2);assert.equal(p.porPagina,4);assert.equal(p.paginas,1);privado(p);
 a.hook(()=>{throw Error('qualquer gravação é proibida');});const r=somenteLeitura(a,()=>a.pagina(p,0));assert.equal(r.lidos,2);assert.equal(r.pagina,0);assert.match(r.estado,/^[a-f0-9]{64}$/);privado(r);
 assert.deepEqual(a.pagina(p,0),r);a.hook(null);assert.equal(JSON.stringify(a.ctx.R53_REF_CACHE_),'{}');
});
caso('631 perfis e recuperações em 158 páginas, sem truncar nem reaplicar',()=>{
 const a=ambiente({planoReal:true,recuperacoes:32}),p=a.plano(),calls=a.chamadas.length;assert.equal(p.perfis,631);assert.equal(p.paginas,158);let lidos=0;
 somenteLeitura(a,()=>{for(let i=0;i<p.paginas;i++){const r=a.pagina(p,i);assert.equal(r.pagina,i);assert.equal(r.paginas,158);assert.equal(r.assinatura,p.assinatura);assert.equal(r.lidos,i===157?3:4);lidos+=r.lidos;privado(r);}});
 assert.equal(lidos,631);assert.equal(a.chamadas.length,calls);assert(!a.doc.has(a.ctx.R53_NOVA_CONFERENCIA_.diario));
});
for(const i of [-1,1,2.5,'0',true,null,NaN,Infinity])caso('índice arbitrário recusado '+String(i),()=>{
 const a=ambiente(),p=a.plano();assert.throws(()=>somenteLeitura(a,()=>a.pagina(p,i)),/página ou assinatura/);assert(!a.locked());
});
caso('assinatura diferente ou sequência incompleta não permite ler',()=>{
 const a=ambiente(),p=a.plano();p.assinatura='0'.repeat(64);assert.throws(()=>somenteLeitura(a,()=>a.pagina(p,0)),/assinatura/);
 const b=ambiente({incompleta:true});assert.throws(()=>b.plano(),/sequência/);assert(!b.locked());
});
caso('prazo esgotado não devolve página parcial nem deixa checkpoint',()=>{
 const a=ambiente(),p=a.plano();a.ctx.R53_NOVA_CONFERENCIA_PAGINAS_.orcamentoMs=0;const atual=a.plano();assert.notEqual(atual.assinatura,p.assinatura);
 assert.throws(()=>somenteLeitura(a,()=>a.pagina(atual,0)),/prazo da página/);assert(!a.locked());
});
caso('erro de perfil ou mudança durante a página não devolvem sucesso',()=>{
 const a=ambiente(),p=a.plano();a.put('FICHA','A1040','mudou');assert.throws(()=>somenteLeitura(a,()=>a.pagina(p,0)),/pós-estado/);
 const b=ambiente(),q=b.plano(),ler=b.ctx.r53NovaConfPerfilLer_;let mudou=false;
 b.ctx.r53NovaConfPerfilLer_=(...args)=>{const h=ler(...args);if(!mudou){mudou=true;b.doc.set(b.ctx.R53_NOVA_FIN_.diario,'{}');}return h;};
 assert.throws(()=>b.pagina(q,0),/registros concluídos/);assert(!b.locked());
});
caso('trava duplicada não é adquirida e falha libera a trava',()=>{
 const a=ambiente(),p=a.plano();const lock=a.ctx.LockService.getDocumentLock();lock.tryLock(1);assert.throws(()=>a.plano(),/trava duplicada/);lock.releaseLock();
 assert.equal(a.pagina(p,0).lidos,2);assert(!a.locked());
});
caso('metadados externos mudados exigem outra assinatura, sem redefinir leitura antiga',()=>{
 const a=ambiente(),p=a.plano();a.guard+='x';assert.throws(()=>a.pagina(p,0),/sequência/);assert(!a.locked());
});
caso('contrato de interoperabilidade deriva das respostas reais do produtor em VM',()=>{
 const {texto}=require('./gerar_contrato_paginas');assert.equal(texto(),fs.readFileSync(path.resolve(__dirname,'fixtures/conferencia_paginas_v1.json'),'utf8'));
});
console.log(`${casos} cenários offline de páginas sem gravação aprovados; 631 perfis em 158 páginas. Versão Drive externa e prova nativa pendentes; criação bloqueada.`);

}
