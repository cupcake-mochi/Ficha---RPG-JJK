'use strict';
// Serviços simulados; leitura não executa fórmulas nem afirma snapshot nativo.
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert/strict');
const {preparado,seedProgressao}=require('./inicializacao_sequencia');
const fonte=new vm.Script(fs.readFileSync(path.resolve(__dirname,'../inicializacao/conferencia.gs'),'utf8'));
const foco=process.argv[2]==='--foco'?new RegExp(process.argv[3]):null;
let casos=0,maior=0;function caso(n,fn){if(foco&&!foco.test(n))return;try{fn();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
function teste(op={}){
 const a=preparado(op);fonte.runInContext(a.ctx);a.p=a.previa();if(!op.incompleta)a.concluir(a.p);
 a.confPrev=()=>a.ctx.r53NovaFichaConferenciaPrevia(a.ss,a.context,a.p.assinatura);
 a.confLer=p=>a.ctx.r53NovaFichaConferenciaLer(a.ss,a.context,a.p.assinatura,p.assinatura);
 a.confJ=()=>JSON.parse(a.doc.get(a.ctx.R53_NOVA_CONFERENCIA_.diario));
 a.confFim=p=>{for(let i=0;i<1000;i++){const out=a.confLer(p);for(const k of ['criacaoDisponivel','conferenciaConjuntaConcluida','consistenciaTemporalVerificada','imagensAtuaisConferidas'])assert.equal(out[k],false);assert(!a.locked());if(a.doc.has(a.ctx.R53_NOVA_CONFERENCIA_.diario)){const raw=a.doc.get(a.ctx.R53_NOVA_CONFERENCIA_.diario);maior=Math.max(maior,Buffer.byteLength(raw));assert(!/SEGREDO|PRIVADO|copia-descartavel|modelo-sintetico/.test(raw));}if(out.leituraConcluida)return out;}throw Error('leituras demais');};
 return a;
}
function semCelulas(a,fn){const antes=new Map(a.cells),script=new Map(a.script),w=a.writes.length;const r=fn();assert.deepEqual(a.cells,antes);assert.deepEqual(a.script,script);assert(a.writes.slice(w).every(([t,k])=>t==='propriedade'&&k==='doc:'+a.ctx.R53_NOVA_CONFERENCIA_.diario));return r;}
caso('conferência não chama nenhuma limpeza, só grava progresso pequeno',()=>{
 const a=teste(),p=a.confPrev(),n=a.chamadas.length;const r=semCelulas(a,()=>a.confFim(p));assert.equal(r.perfisLidos,2);assert.equal(a.chamadas.length,n);assert(r.retrataSomenteEstaRodada);assert.equal(JSON.stringify(a.ctx.R53_REF_CACHE_),'{}');
 const w=a.writes.length;a.confFim(p);assert.equal(a.writes.length,w);assert.throws(()=>a.confPrev(),/já iniciada/);
});
caso('599 perfis do protocolo são lidos e seus registros conferidos sem limpar novamente',()=>{
 const a=teste({planoReal:true}),p=a.confPrev(),calls=a.chamadas.length;assert.equal(p.perfis,599);semCelulas(a,()=>a.confFim(p));assert.equal(a.chamadas.length,calls);
 const fases=a.realPlano([]).filter(f=>f.tipo!=='imagens');for(const f of fases)assert.equal(a.ctx.r53NovaSeqChave_(f),a.realPerfil(f).diario);
});
caso('uma fase por chamada, assinatura errada não cria checkpoint',()=>{
 const a=teste(),p=a.confPrev(),w=a.writes.length;assert.throws(()=>a.confLer({assinatura:'x'}),/assinatura/);assert.equal(a.writes.length,w);const r=a.confLer(p);assert.equal(r.perfisLidos,1);assert(r.retomar);
});
const base=teste(),bp=base.confPrev(),inicio=base.writes.length;base.confFim(bp);const delta=base.writes.length-inicio;
for(let k=1;k<=delta;k++)for(const fase of ['antes','depois'])caso('queda '+fase+' checkpoint '+k+' não pula perfil nem limpa dados',()=>{
 const a=teste(),p=a.confPrev();let n=0;a.hook(m=>{if(m===fase&&++n===k)throw Error('queda');});assert.throws(()=>a.confFim(p),/queda/);assert(!a.locked());a.hook(null);semCelulas(a,()=>a.confFim(p));assert.equal(a.confJ().proxima,2);
});
for(const qual of ['valor','nota','formula','validacao'])caso('alteração no pós-estado '+qual+' é recusada sem correção',()=>{
 const a=teste({incompleta:true});
 if(['nota','validacao'].includes(qual)){
  const get=a.ctx.r53NovaSeqPerfil_;a.ctx.r53NovaSeqPerfil_=fase=>{const per=get(fase),ops=per.operacoes();per.operacoes=()=>[...ops,qual==='nota'?{tipo:'nota',aba:'FICHA',faixa:'B1',valor:''}:{tipo:'validacao',aba:'FICHA',faixa:'B1',regra:null}];return per;};
 }
 a.concluir(a.p);const p=a.confPrev();
 if(qual==='valor')a.put('FICHA','A1040','SEGREDO');if(qual==='formula')a.put('FICHA','A1040',0,'=0');
 if(qual==='nota')a.put('FICHA','B1','', '', 'nota nova');if(qual==='validacao'){const cell=a.get('FICHA',1,2);a.cells.set('FICHA!1,2',{...cell,dv:{tipo:'CHECKBOX',argumentos:[],permiteInvalido:false,ajuda:''}});}
 const w=a.writes.length;assert.throws(()=>a.confFim(p),/pós-estado/);assert(a.writes.slice(w).every(([t])=>t==='propriedade'));assert.equal(a.confJ().proxima,0);
});
for(const alterar of [j=>j.concluido=false,j=>j.assinatura='0'.repeat(64),j=>j.vinculo='0'.repeat(64),j=>j.resultado='0'.repeat(64),j=>j.extra=1])caso('recibo incompleto/alterado não serve como prova',()=>{
 const a=teste(),p=a.confPrev(),key=a.ctx.r53NovaSeqPerfil_({tipo:'financeiro',id:''}).diario,j=JSON.parse(a.doc.get(key));alterar(j);a.doc.set(key,JSON.stringify(j));assert.throws(()=>a.confFim(p),/registros concluídos mudaram/);
});
caso('recibo sem efeito de fábrica não basta, mesmo íntegro',()=>{
 const a=teste(),p=a.confPrev(),key=a.ctx.r53NovaSeqPerfil_({tipo:'financeiro',id:''}).diario,j=JSON.parse(a.doc.get(key));a.put('FICHA','A1040','dado herdado');j.resultado=a.ctx.r53NovaFinHash_([a.ctx.r53NovaFinHash_(a.ctx.r53NovaFinLer_(a.ss,{aba:'FICHA',faixa:'A1040'}))]);const b={...j};delete b.integridade;j.integridade=a.ctx.r53NovaFinHash_(b);a.doc.set(key,JSON.stringify(j));assert.throws(()=>a.ctx.r53NovaConfPerfilLer_(a.ss,a.context,{tipo:'financeiro',id:''},a.j()),/pós-estado/);
});
caso('registro do filho ausente, grande, JSON inválido ou de outra operação recusa',()=>{
 for(const raw of [null,'x'.repeat(9001),'{',JSON.stringify([])]){const a=teste(),p=a.confPrev(),key=a.ctx.r53NovaSeqPerfil_({tipo:'financeiro',id:''}).diario;if(raw===null)a.doc.delete(key);else a.doc.set(key,raw);assert.throws(()=>a.confFim(p),/registro/);}
});
caso('mudança do registro durante a leitura é detectada',()=>{
 const a=teste(),p=a.confPrev(),ler=a.ctx.r53NovaFinLer_;let changed=false;a.ctx.r53NovaFinLer_=(ss,op)=>{const r=ler(ss,op);if(op.faixa==='A1040'&&!changed){changed=true;a.doc.set(a.ctx.r53NovaSeqPerfil_({tipo:'financeiro',id:''}).diario,'{}');}return r;};assert.throws(()=>a.confFim(p),/registro mudou/);
});
for(const alterar of [j=>j.proxima++,j=>j.cadeia='0'.repeat(64),j=>j.sequencia='0'.repeat(64),j=>j.total++,j=>j.extra=1])caso('checkpoint inválido não é recomeçado',()=>{
 const a=teste(),p=a.confPrev();a.confLer(p);const j=a.confJ();alterar(j);a.doc.set(a.ctx.R53_NOVA_CONFERENCIA_.diario,JSON.stringify(j));const w=a.writes.length;assert.throws(()=>a.confLer(p),/checkpoint/);assert.equal(a.writes.length,w);
});
caso('sequência incompleta, ausente e geração antiga não são adotadas',()=>{
 for(const qual of ['incompleta','ausente','antiga']){const a=teste({incompleta:true});if(qual==='incompleta')a.aplicar(a.p);if(qual==='antiga')a.doc.set('r53_nova_ficha_sequencia_v1','{}');assert.throws(()=>a.confPrev(),/sequência/);}
});
caso('mudança do coordenador ou da operação após a prévia recusa',()=>{
 for(const qual of ['coordenador','operacao']){const a=teste(),p=a.confPrev();if(qual==='operacao')a.context.operacao+='x';else{const j=a.j();j.financeiroProtecao='0'.repeat(64);j.integridade=a.ctx.r53NovaSeqSelar_(j);a.doc.set(a.ctx.R53_NOVA_SEQUENCIA_.diario,JSON.stringify(j));}assert.throws(()=>a.confLer(p),/vínculo|assinatura/);}
});
for(const key of ['r53_versoes','r53_recuperacao_1793037909537','r53_recuperacao_x'])caso('memória pessoal ressurgida impede até leitura concluída '+key,()=>{
 const a=teste(),p=a.confPrev();a.confFim(p);a.doc.set(key,'PRIVADO');const w=a.writes.length;assert.throws(()=>a.confLer(p),/memória/);assert.equal(a.writes.length,w);
});
caso('mudança posterior no registro de uma página anterior também é detectada',()=>{
 const a=teste(),p=a.confPrev();a.confLer(p);const key=a.ctx.R53_NOVA_FIN_.diario;a.doc.set(key,'{}');assert.throws(()=>a.confLer(p),/registros concluídos mudaram/);assert.equal(a.confJ().proxima,1);
});
caso('prazo esgotado não avança; quota insuficiente não começa',()=>{
 const a=teste(),p=a.confPrev();a.ctx.R53_NOVA_CONFERENCIA_.orcamentoMs=0;const zero=a.confPrev();const r=a.confLer(zero);assert.equal(r.perfisLidos,0);assert(r.retomar);
 const b=teste(),q=b.confPrev();for(let i=0;i<57;i++)b.doc.set('alheio'+i,'x'.repeat(8000));const w=b.writes.length;assert.throws(()=>b.confLer(q),/espaço seguro/);assert.equal(b.writes.length,w);
});
caso('página lida não é snapshot: edição posterior não ganha selo de consistência',()=>{
 const a=teste(),p=a.confPrev();a.confLer(p);a.put('FICHA','A1040','alterado depois da página');const r=a.confFim(p);assert(r.leituraConcluida);assert.equal(r.consistenciaTemporalVerificada,false);assert.equal(r.conferenciaConjuntaConcluida,false);assert.equal(r.criacaoDisponivel,false);
});
function real(){const a=teste({incompleta:true,perfisReais:true});seedProgressao(a);a.p=a.previa();a.concluir(a.p);return a;}
caso('diários reais financeiro/progressão conferem depois de mudar nível sem repetir Aplicar',()=>{
 const a=real(),p=a.confPrev(),chamadas=a.chamadas.length;semCelulas(a,()=>a.confFim(p));assert.equal(a.chamadas.length,chamadas);const j=JSON.parse(a.doc.get(a.ctx.R53_NOVA_FIN_.diario));assert.throws(()=>a.ctx.r53NovaFichaFinanceiroAplicar(a.ss,a.context,j.assinatura),/configuração mudou/);
});
for(const qual of ['config','formula','nivel','missao','diario','resultado'])caso('desvio real no financeiro/progressão '+qual+' é recusado',()=>{
 const a=real(),p=a.confPrev();if(qual==='config')a.put('CONFIGURAÇÃO','F46',11);if(qual==='formula')a.put('DADOS_SALARIOS','P11',0,'=1');if(qual==='nivel')a.put('FICHA','AH11',11);if(qual==='missao')a.put('FICHA PESSOAL','AW15','missão nova');
 if(qual==='diario'){const key=a.ctx.R53_NOVA_PROG_.diario,j=JSON.parse(a.doc.get(key));j.concluido=false;a.doc.set(key,JSON.stringify(j));}
 if(qual==='resultado')a.put('DADOS','CZ54',9999);const w=a.writes.length;assert.throws(()=>a.confFim(p),/financeir|fórmula|pós-estado|missões|diário|registros concluídos/);assert(a.writes.slice(w).every(([t])=>t==='propriedade'));
});
caso('mapa direto não tem escritas cruzadas, ordem protege os vizinhos de Classe 0',()=>{
 const {mapear}=require('../inicializacao/mapear_intersecoes'),m=mapear(),a=preparado(),fases=a.realPlano([]),pos=nome=>fases.findIndex(f=>f.tipo!=='imagens'&&a.realPerfil(f).nome===nome);
 assert.deepEqual(m,JSON.parse(fs.readFileSync(path.resolve(__dirname,'../inicializacao/INTERSECOES-2026-10-28.json'),'utf8')));assert.equal(m.perfis,599);assert.equal(m.operacoesCelulares,10178);assert.equal(m.guardasDeclaradas,17316);assert.equal(m.escritasCruzadas.length,0);assert.equal(m.escritasEmGuardas.length,83);
 for(const x of m.escritasEmGuardas){if(x.escritor==='nivel_e_base_xp'&&x.leitor==='financeiro'){assert(pos(x.escritor)>pos(x.leitor));continue;}assert(pos(x.escritor)<pos(x.leitor),JSON.stringify(x));}
});
caso('cinco Classe 0 preenchidos: ordem antiga falha, ordem nova mantém guardas e recibos',()=>{
 const {preparado:cart,maps,descriptor}=require('./inicializacao_cartoes'),a=cart('classe0.1'),contr=a.ctx.R53_NOVA_CARTOES_CONTRATO_,ids=['classe0.1','classe0.2','classe0.3','classe0.4','classe0.5'];new vm.Script(fs.readFileSync(path.resolve(__dirname,'../inicializacao/sequencia.gs'),'utf8')).runInContext(a.ctx);fonte.runInContext(a.ctx);
 const {pos}=require('../inicializacao/gerar_contrato_cartoes');
 for(const id of ids){const g=contr.contextos[id];for(const x of g.guardas){const v=maps.get(g.aba).get(pos(x.faixa).join(','))??'';a.put(g.aba,x.faixa,typeof v==='string'&&v.startsWith('=')?123:v,typeof v==='string'&&v.startsWith('=')?v:'');}}
 for(const id of ids){const g=contr.contextos[id];for(const x of g.entradas){a.put(g.aba,x.faixa,x.chave==='forma'?'Área':x.funcao?true:'PRIVADO','','NOTA PRIVADA');a.setDV(x.faixa,x.funcao?descriptor('CHECKBOX',[]):descriptor('VALUE_IN_LIST',[['catálogo preservado'],true],true));}}
 assert.throws(()=>a.ctx.r53NovaFichaCartaoPrevia(a.ss,a.context,'classe0.1'),/rótulo ou fórmula/);assert.equal(a.writes.length,0);
 for(const id of ids.slice().reverse()){const p=a.ctx.r53NovaFichaCartaoPrevia(a.ss,a.context,id);let done=false;for(let i=0;i<20;i++)if(a.ctx.r53NovaFichaCartaoAplicar(a.ss,a.context,id,p.assinatura).concluido){done=true;break;}assert(done,id);}
 const w=a.writes.length;for(const id of ids)a.ctx.r53NovaConfPerfilLer_(a.ss,a.context,{tipo:'cartao',id},{});assert.equal(a.writes.length,w);
});
console.log(`${foco?"FOCO PARCIAL · ":""}${casos} cenários offline da leitura conjunta aprovados; maior checkpoint ${maior} bytes. Sem limpeza, snapshot consistente ou liberação de criação.`);
