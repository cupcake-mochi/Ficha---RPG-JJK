'use strict';
// Protocolo de coordenação em VM. O caso financeiro/progressão usa os perfis reais;
// a bateria de falhas usa perfis pequenos controlados, não simula fórmulas Google.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const {ambiente}=require('./apoio_inicializacao'),root=path.resolve(__dirname,'../..');
const nomes=['progressao','identidade','contrato_pessoal','pessoal','contrato_formacao','formacao','validacoes','contrato_memorias','memorias','contrato_montagens','montagens','contrato_cartoes','cartoes','contrato_entidades','entidades','contrato_arte','arte','inventario_imagens','sequencia'];
const scripts=['apps-script/EditorR53.gs',...nomes.map(n=>'r53/inicializacao/'+n+'.gs')].map(n=>new vm.Script(fs.readFileSync(path.join(root,n),'utf8')));
let casos=0,maior=0;function caso(n,fn){try{fn();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
const simples=[{tipo:'imagens',id:'antes'},{tipo:'financeiro',id:''},{tipo:'progressao',id:''}];
function preparado(op={}){
 const a=ambiente(op);a.doc.delete('r53_recuperacao_personagem');for(const s of scripts)s.runInContext(a.ctx);
 a.ctx.R53_REF_CACHE_={segredo:'não reaproveitar'};a.realPlano=a.ctx.r53NovaSeqPlano_;a.realCodigo=a.ctx.r53NovaSeqCodigo_;a.realPerfil=a.ctx.r53NovaSeqPerfil_;
 const cod=a.ctx.r53NovaFinHash_(['fixture-sequencia']);a.estrutura='grade1';a.guard='guarda1';a.chamadas=[];a.bad={};a.seqlock=0;
 // A trava da fixture recusa aquisição recursiva, para flagrar trava duplicada.
 const realLock=a.ctx.LockService.getDocumentLock;
 a.ctx.LockService.getDocumentLock=()=>{const l=realLock();return {tryLock(ms){if(a.locked())throw Error('trava duplicada');if(l.tryLock(ms)){a.seqlock++;return true;}return false;},releaseLock(){a.seqlock--;l.releaseLock();}};};
 if(!op.planoReal)a.ctx.r53NovaSeqPlano_=rec=>[...simples,...rec.map(id=>({tipo:'recuperacao',id}))];
 a.ctx.r53NovaSeqCodigo_=plano=>a.ctx.r53NovaFinHash_([cod,plano,a.guard]);
 a.ctx.r53NovaFichaImagensPrevia=(ss,ctx,fase)=>{
  a.ctx.r53NovaFinContexto_(ss,ctx);if(a.doc.has('inventario_'+fase))throw Error('inventário iniciado');
  return {assinatura:a.ctx.r53NovaFinHash_([a.estrutura,fase])};
 };
 a.ctx.r53NovaInvImagemInspecionarTravado_=(ss,ctx,fase,hash)=>{
  assert(a.locked());assert.equal(hash,a.ctx.r53NovaFinHash_([a.estrutura,fase]));a.chamadas.push('imagem:'+fase);
  const dp=a.ctx.PropertiesService.getDocumentProperties();if(!a.doc.has('inventario_'+fase))a.ctx.r53NovaDiarioSalvar_(dp,'inventario_'+fase,{assinatura:hash});
  return {leituraConcluida:true,contagem:{fora:0,indeterminadas:0,decoracoesAusentes:0,fotos:0,...a.bad.contagem},sobrepostas:0,desenhos:0,...a.bad};
 };
 if(!op.perfisReais)a.ctx.r53NovaSeqPerfil_=fase=>{
  const p=op.planoReal?a.realPerfil(fase):{nome:fase.tipo+'_'+fase.id,diario:'r53_nova_ficha_mock_'+fase.tipo+'_'+fase.id,recibo:true};
  const index=(op.planoReal?a.realPlano([]):a.ctx.r53NovaSeqPlano_([])).findIndex(f=>f.tipo===fase.tipo&&f.id===fase.id)+1;
  return {...p,precondicao:null,recibo:true,limites:{escritasPorExecucao:4,orcamentoMs:210000},pendente:['prova_nativa'],preservados:()=>a.ctx.r53NovaFinHash_(['guarda']),
   operacoes:()=>fase.tipo==='recuperacao'?[{tipo:'propriedade',escopo:'documento',chave:fase.id}]:Array.from({length:op.passos||1},(_,i)=>({tipo:'valor',aba:'FICHA',faixa:'A'+(1000+index*20+i),valor:'inicial'}))};
 };
 const oldInner=a.ctx.r53NovaPerfilAplicarTravado_;
 a.ctx.r53NovaPerfilAplicarTravado_=(ss,ctx,sig,p,inicio)=>{assert(a.locked());a.chamadas.push(p.nome);return oldInner(ss,ctx,sig,p,inicio);};
 a.previa=()=>a.ctx.r53NovaFichaSequenciaPrevia(a.ss,a.context);a.aplicar=p=>a.ctx.r53NovaFichaSequenciaAplicar(a.ss,a.context,p.assinatura);
 a.j=()=>JSON.parse(a.doc.get(a.ctx.R53_NOVA_SEQUENCIA_.diario));
 a.concluir=p=>{for(let i=0;i<3000;i++){const r=a.aplicar(p);assert.equal(r.criacaoDisponivel,false);assert.equal(r.conferenciaConjuntaConcluida,false);assert(!a.locked());assert.equal(a.seqlock,0);for(const [k,v]of a.doc)if(k===a.ctx.R53_NOVA_SEQUENCIA_.diario){maior=Math.max(maior,Buffer.byteLength(v));assert(!/SEGREDO|PRIVADO|copia-descartavel|modelo-sintetico/.test(v));}if(r.fasesPercorridas)return r;}throw Error('retomadas excedidas');};
 return a;
}
caso('manifesto real tem 601 fases, identidades únicas e ordem de dependências',()=>{
 const a=preparado(),p=a.realPlano([]),pos=(tipo,id='')=>p.findIndex(x=>x.tipo===tipo&&x.id===id);
 assert.equal(p.length,601);assert.equal(new Set(p.map(x=>x.tipo+':'+x.id)).size,601);
 assert(pos('imagens','antes')<pos('fotos'));assert(pos('fotos')<pos('identidade'));assert(pos('financeiro')<pos('progressao'));
 assert(pos('formacao','familias')<pos('cartao','feitico.1'));assert(pos('montagens','feitico.1')<pos('memorias','0'));
 assert(pos('cartao','feitico.1')<pos('memorias','0'));assert(pos('pessoal','recursos')>pos('memorias','10'));assert.equal(pos('imagens','depois'),600);
 const perfis=p.filter(f=>f.tipo!=='imagens').map(f=>a.realPerfil(f));assert.equal(perfis.length,599);assert.equal(new Set(perfis.map(x=>x.diario)).size,599);
 const code=a.realCodigo(p);a.ctx.R53_NOVA_FORMACAO_CONTRATO_.dominios.grau_origem.entradas[0].notas[0][0]+=' alterada';assert.notEqual(a.realCodigo(p),code);
});
caso('601 fases sintéticas usam executor real, sequência fixa e retorno sempre bloqueado',()=>{
 const a=preparado({planoReal:true}),p=a.previa();assert.equal(p.fases,601);assert.equal(a.writes.length,0);const r=a.concluir(p);assert.equal(r.fasesConcluidas,601);assert(r.pendente.includes('conferencia_conjunta_e_consistencia_temporal'));
 const w=a.writes.length,c=a.chamadas.length;a.concluir(p);assert.equal(a.writes.length,w);assert.equal(a.chamadas.length,c);
 assert.equal(JSON.stringify(a.ctx.R53_REF_CACHE_),'{}');
});
const basico=preparado();basico.concluir(basico.previa());
for(let k=1;k<=basico.writes.length;k++)for(const momento of ['antes','depois'])caso('queda '+momento+' da gravação '+k+' retoma filho ou cursor sem repetir limpeza',()=>{
 const a=preparado(),p=a.previa();let n=0;a.hook(m=>{if(m===momento&&++n===k)throw Error('queda');});assert.throws(()=>a.concluir(p),/queda/);assert(!a.locked());assert.equal(a.seqlock,0);a.hook(null);a.concluir(p);
 for(const addr of ['FICHA!A1040','FICHA!A1060'])assert.equal(a.writes.filter(([t,x])=>t==='valor'&&x===addr).length,1);
});
caso('prévia da fase é salva em chamada separada da aplicação, mesmo com zero mudanças',()=>{
 const a=preparado(),p=a.previa();a.aplicar(p);assert(a.j().ativo);assert.equal(a.chamadas.length,0);a.aplicar(p);assert.equal(a.j().proxima,1);a.aplicar(p);assert(a.j().ativo);assert.equal(a.chamadas.length,1);
});
caso('mais de quatro passos mantém o mesmo filho até concluir',()=>{
 const a=preparado({passos:10}),p=a.previa();a.aplicar(p);a.aplicar(p);a.aplicar(p);const w=a.writes.length;a.aplicar(p);assert.equal(a.j().proxima,1);assert(a.j().ativo);assert.equal(a.writes.slice(w).filter(([t])=>t==='valor').length,4);a.concluir(p);
});
for(const alterar of [j=>j.proxima=-1,j=>j.proxima=1000,j=>j.ativo={assinatura:'x'},j=>j.extra=1,j=>j.codigo='0'.repeat(64),j=>j.inicioImagens='0'.repeat(64),j=>j.integridade='0'.repeat(64),j=>j.recuperacoes.push('arbitraria')])caso('diário alterado não reinicia nem muda alvo',()=>{
 const a=preparado(),p=a.previa();a.aplicar(p);const j=a.j();alterar(j);a.doc.set(a.ctx.R53_NOVA_SEQUENCIA_.diario,JSON.stringify(j));const w=a.writes.length;assert.throws(()=>a.aplicar(p),/diário|sequência|recuperações/);assert.equal(a.writes.length,w);assert(!a.locked());
});
caso('JSON ilegível, hash errado ou contexto diferente recusam sem escrita',()=>{
 for(const qual of ['json','assinatura','operacao','registrado']){const a=preparado(),p=a.previa();a.aplicar(p);if(qual==='json')a.doc.set(a.ctx.R53_NOVA_SEQUENCIA_.diario,'{');if(qual==='assinatura')p.assinatura='0'.repeat(64);if(qual==='operacao')a.context.operacao+='x';if(qual==='registrado')a.context.arquivosRegistrados.push(a.ss.getId());const w=a.writes.length;assert.throws(()=>a.aplicar(p),/diário|sequência|alvo/);assert.equal(a.writes.length,w);assert(!a.locked());}
});
caso('prévia fica vinculada à estrutura inicial e recusa mudança antes de começar',()=>{
 const a=preparado(),p=a.previa();a.estrutura='outra';assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);
});
caso('contrato alterado após iniciar não escreve mais nada',()=>{
 const a=preparado(),p=a.previa();a.aplicar(p);a.guard+='x';const w=a.writes.length;assert.throws(()=>a.aplicar(p),/contrato mudou/);assert.equal(a.writes.length,w);
});
for(const key of ['r53_nova_ficha_financeiro_v1','r53_nova_ficha_futuro_v9'])caso('fases avulsas anteriores exigem outra cópia '+key,()=>{const a=preparado();a.doc.set(key,'{}');assert.throws(()=>a.previa(),/fases anteriores/);assert.equal(a.writes.length,0);});
caso('prévia inválida não cria diário; quota insuficiente não inicia filho',()=>{
 const a=preparado(),p=a.previa();assert.throws(()=>a.aplicar({assinatura:'x'}),/mudou após/);assert.equal(a.writes.length,0);for(let i=0;i<57;i++)a.doc.set('alheio'+i,'x'.repeat(8000));assert.throws(()=>a.aplicar(p),/espaço seguro/);assert.equal(a.writes.length,0);assert.equal(a.chamadas.length,0);
});
caso('recuperações são capturadas, limpas uma vez e não desaparecem do manifesto',()=>{
 const a=preparado(),keys=['r53_recuperacao_1793037909537','r53_recuperacao_1793037909538'];keys.forEach(k=>a.doc.set(k,'PRIVADO'));const p=a.previa();assert.equal(p.recuperacoes,2);a.concluir(p);assert.deepEqual([...a.j().recuperacoes],keys);for(const k of keys)assert(!a.doc.has(k));a.concluir(p);
});
caso('recuperação nova ou memória desconhecida impede avançar',()=>{
 for(const key of ['r53_recuperacao_1793037909537','r53_recuperacao_desconhecida']){const a=preparado(),p=a.previa();a.aplicar(p);a.doc.set(key,'SEGREDO');const w=a.writes.length;assert.throws(()=>a.aplicar(p),/recuperação|memória pessoal/);assert.equal(a.writes.length,w);}
});
for(const lista of [Array.from({length:33},(_,i)=>'r53_recuperacao_'+(1793037909500+i)),['r53_recuperacao_1793037909538','r53_recuperacao_1793037909537'],['r53_recuperacao_1793037909537','r53_recuperacao_1793037909537'],['x'],null])caso('lista livre, repetida, fora de ordem ou excessiva recusa',()=>{const a=preparado();assert.throws(()=>a.ctx.r53NovaSeqRecuperacoes_(lista),/inválida/);assert.equal(a.writes.length,0);});
for(const [key,value]of [['fora',1],['indeterminadas',1],['decoracoesAusentes',1],['sobrepostas',1],['desenhos',1]])caso('arte problemática impede primeira escrita de personagem '+key,()=>{
 const a=preparado(),p=a.previa();a.bad=key==='sobrepostas'||key==='desenhos'?{[key]:value}:{contagem:{fora:0,indeterminadas:0,decoracoesAusentes:0,fotos:0,[key]:value}};a.aplicar(p);assert.throws(()=>a.aplicar(p),/arte exige revisão/);assert.equal(a.j().proxima,0);assert(a.writes.every(([t])=>t==='propriedade'));
});
caso('foto ainda presente na rodada depois bloqueia avanço final',()=>{
 const a=preparado();a.ctx.r53NovaSeqPlano_=()=>[{tipo:'imagens',id:'antes'},{tipo:'imagens',id:'depois'}];const p=a.previa();a.aplicar(p);a.aplicar(p);a.bad={contagem:{fora:0,indeterminadas:0,decoracoesAusentes:0,fotos:1}};a.aplicar(p);assert.throws(()=>a.aplicar(p),/arte exige revisão/);assert.equal(a.j().proxima,1);
});
for(const op of [{ocupado:true},{ativoDiferente:true},{id:'1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k'}])caso('trava ou alvo recusados preservam dados',()=>{const a=preparado(op);assert.throws(()=>a.aplicar({assinatura:'x'}),/andamento|vinculado|alvo/);assert.equal(a.writes.length,0);assert.equal(a.seqlock,0);});
caso('financeiro e progressão reais: muda nível, retoma depois sem reaplicar financeiro',()=>{
 const a=preparado({perfisReais:true});a.put('CONFIGURAÇÃO','C46','Nível inicial');a.put('CONFIGURAÇÃO','E46',2);a.put('CONFIGURAÇÃO','F46',10);a.put('CONFIGURAÇÃO','G46',10,a.ctx.R53_NOVA_PROG_.regra);a.put('FICHA','AH11',29);
 a.put('DADOS','CY54','xp base');a.put('DADOS','CY47','xp total');a.put('DADOS','CZ54',9999);a.put('DADOS','CZ47',9999,a.ctx.R53_NOVA_PROG_.xp);
 const curva=[0,200,500,800,1300,1800,2300,3000,3700,4400,5300,6200,7100,8200,9300,10400,11700,13000,14300,15800,17300,18800,20500,22200,23900,25600,27300,29000,30700];
 for(let i=0;i<29;i++){a.put('DADOS','AQ'+(i+5),i+2);a.put('DADOS','AR'+(i+5),curva[i],'=DADOS_CONFIG!$Z$'+(i+3));}
 for(let r=15;r<=87;r++)for(let g=0;g<4;g++)a.put('FICHA PESSOAL',['BA','BG','BM','BS'][g]+r,'',a.ctx.r53NovaProgFormulaMissao_(r,g));
 const p=a.previa();a.concluir(p);assert.equal(a.range('FICHA','AH11').getValue(),10);assert.equal(a.range('DADOS','CZ54').getValue(),3700);
 const chamadas=a.chamadas.filter(n=>n==='financeiro').length,w=a.writes.length;a.concluir(p);assert.equal(a.writes.length,w);assert.equal(a.chamadas.filter(n=>n==='financeiro').length,chamadas);
 const old=JSON.parse(a.doc.get(a.ctx.R53_NOVA_FIN_.diario));assert.throws(()=>a.ctx.r53NovaFichaFinanceiroAplicar(a.ss,a.context,old.assinatura),/configuração mudou/);assert.equal(a.writes.length,w);
});
caso('32 recuperações cabem no coordenador e permanecem no manifesto após apagar os dados',()=>{
 const a=preparado();for(let i=0;i<32;i++)a.doc.set('r53_recuperacao_'+(1793037909500+i),'SEGREDO');const p=a.previa();assert.equal(p.recuperacoes,32);a.concluir(p);assert.equal(a.j().recuperacoes.length,32);assert.equal(a.j().proxima,35);
});
caso('filho criado por fora depois do início não é adotado nem apagado',()=>{
 const a=preparado(),p=a.previa();a.aplicar(p);a.aplicar(p);a.doc.set('r53_nova_ficha_mock_financeiro_','{}');const w=a.writes.length;assert.throws(()=>a.aplicar(p),/já existe uma inicialização/);assert.equal(a.writes.length,w);assert.equal(a.j().proxima,1);
});
caso('prazo esgotado do filho mantém assinatura e cursor sem iniciar outra fase',()=>{
 const a=preparado(),original=a.ctx.r53NovaSeqPerfil_;a.ctx.r53NovaSeqPerfil_=fase=>{const p=original(fase);p.limites.orcamentoMs=0;return p;};const p=a.previa();a.aplicar(p);a.aplicar(p);a.aplicar(p);const assinatura=a.j().ativo.assinatura,w=a.writes.length;a.aplicar(p);assert.equal(a.j().ativo.assinatura,assinatura);assert.equal(a.j().proxima,1);assert(a.writes.slice(w).every(([t])=>t==='propriedade'));
});
caso('checkpoints e privacidade continuam dentro do teto por valor',()=>{assert(maior<9000);});
console.log(`${casos} cenários offline da sequência fixa aprovados; maior diário ${maior} bytes. 601 fases de protocolo; prova nativa e conferência conjunta pendentes, criação bloqueada.`);
