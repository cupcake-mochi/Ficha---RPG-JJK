'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process'),{ambiente}=require('./apoio_inicializacao');
const root=path.resolve(__dirname,'../..');
const sources=['apps-script/EditorR53.gs','r53/inicializacao/contrato_memorias.gs','r53/inicializacao/memorias.gs'].map(n=>fs.readFileSync(path.join(root,n),'utf8'));
const recovery='r53_recuperacao_1793189000000';
let casos=0;function caso(n,f){try{f();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
function preparado(grupo=0,rec=null,op={}){
 const a=ambiente(op);for(const s of sources)vm.runInContext(s,a.ctx);
 // O fixture genérico tem um nome fictício que não é emitido pelo produtor.
 a.doc.delete('r53_recuperacao_personagem');a.c=a.ctx.R53_NOVA_MEMORIAS_CONTRATO_;
 for(const k of a.c.chaves)a.doc.set(k,'CONTEÚDO PRIVADO '+k);
 a.doc.set(recovery,'RECUPERAÇÃO PRIVADA');
 for(const [k,v]of [['paleta_pendente','Noite'],['R53_TABELAS_GERACAO','geração'],['r53_nova_ficha_identidade_textual_v1','diário alheio'],['campanha','configuração']])a.doc.set(k,v);
 a.ctx.R53_REF_CACHE_={versoes:{lista:[['dado pessoal']]},amparo:['Fechada']};
 a.previa=()=>rec?a.ctx.r53NovaFichaRecuperacaoPrevia(a.ss,a.context,rec):a.ctx.r53NovaFichaMemoriasPrevia(a.ss,a.context,grupo);
 a.aplicar=p=>rec?a.ctx.r53NovaFichaRecuperacaoAplicar(a.ss,a.context,rec,p.assinatura):a.ctx.r53NovaFichaMemoriasAplicar(a.ss,a.context,grupo,p.assinatura);
 a.concluir=p=>{for(let n=0;n<30;n++){const r=a.aplicar(p);assert.equal(r.criacaoDisponivel,false);if(r.concluido)return r;assert.equal(r.retomar,true);}throw Error('não concluiu');};
 a.perfil=()=>a.ctx.r53NovaMemPerfil_(grupo,rec||undefined);
 a.alvos=rec?[rec]:a.c.chaves.slice(grupo*a.c.porGrupo,(grupo+1)*a.c.porGrupo);
 a.antes={cells:JSON.stringify([...a.cells]),script:JSON.stringify([...a.script]),doc:new Map(a.doc)};
 return a;
}
function conferir(a){
 for(const k of a.alvos)assert(!a.doc.has(k));
 for(const [k,v]of a.antes.doc)if(!a.alvos.includes(k))assert.equal(a.doc.get(k),v,k);
 assert.equal(JSON.stringify([...a.cells]),a.antes.cells);assert.equal(JSON.stringify([...a.script]),a.antes.script);
 const raw=a.doc.get(a.perfil().diario);assert(raw&&!raw.includes('PRIVAD'));assert(Buffer.byteLength(raw)<9000);assert(JSON.parse(raw).concluido);
 assert.equal(JSON.stringify(a.ctx.R53_REF_CACHE_),'{}');assert(!a.locked());
}
caso('contrato fiel ao editor e fórmulas/IDs públicos, sem regenerar',()=>{
 execFileSync(process.execPath,['r53/inicializacao/gerar_contrato_memorias.js','--conferir'],{cwd:root});
 const a=preparado();assert.equal(a.c.chaves.length,253);assert.equal(new Set(a.c.chaves).size,253);
 assert.deepEqual(Array.from(a.c.chaves.slice(4)),Array.from(a.ctx.R53_EDITOR_.contextos,x=>'r53_classe_visivel_'+x.id));
 const direct=fs.readFileSync(path.join(root,'r53/runtime_direto.gs'),'utf8');
 assert(direct.includes("'r53_recuperacao_'+Date.now()"));assert(direct.includes("'r53_classe_visivel_'+g.id"));
 assert(direct.includes("R53_VERSOES_PROP_='r53_versoes'"));
 assert(fs.readFileSync(path.join(root,'apps-script/Codigo.gs'),'utf8').includes("MARCAS_CUSTOM_PROP_ = 'r53_marcas_custom'"));
});
caso('inspeção só informa chaves e grupos, não valores ou aprovação',()=>{
 const a=preparado(),p=a.ctx.r53NovaFichaMemoriasInspecionar(a.ss,a.context);
 assert.equal(p.grupos,11);assert.equal(p.restantes,253);assert.deepEqual(Array.from(p.recuperacoes),[recovery]);assert.equal(p.criacaoDisponivel,false);assert.equal(a.writes.length,0);assert(!JSON.stringify(p).includes('PRIVAD'));
});
for(let grupo=0;grupo<11;grupo++){
 caso('grupo fixo '+grupo+' limpa só suas propriedades, repete sem escrita',()=>{const a=preparado(grupo),p=a.previa();assert.equal(a.writes.length,0);a.concluir(p);conferir(a);const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);});
 caso('grupo '+grupo+' recusa alteração entre prévia e aplicação',()=>{const a=preparado(grupo),p=a.previa();a.doc.set(a.alvos[0],'alterado');assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);});
 caso('grupo '+grupo+' no máximo quatro exclusões e diário abaixo do limite',()=>{const a=preparado(grupo),r=a.aplicar(a.previa());assert.equal(r.concluido,false);assert.equal(a.writes.filter(x=>x[0]==='excluirPropriedade').length,4);assert(Buffer.byteLength(a.doc.get(a.perfil().diario))<9000);});
}
for(const [grupo,rec]of [[0,null],[10,null],[null,recovery]]){
 const base=preparado(grupo,rec);base.concluir(base.previa());
 for(let i=1;i<=base.writes.length;i++)for(const fase of ['antes','depois'])caso(`queda ${grupo??'recuperação'} ${fase} ${i}`,()=>{
  const a=preparado(grupo,rec),p=a.previa();let n=0;a.hook(f=>{if(f===fase&&++n===i)throw Error('queda');});
  assert.throws(()=>a.concluir(p),/queda/);assert(!a.locked());a.hook(null);a.concluir(p);conferir(a);
 });
}
caso('recuperação conhecida é excluída e repetida sem apagar outra ou guardar seu conteúdo',()=>{
 const a=preparado(null,recovery);a.doc.set('r53_recuperacao_1793189000001','outra');a.antes.doc.set('r53_recuperacao_1793189000001','outra');
 const p=a.previa();assert(!JSON.stringify(p).includes('PRIVAD'));a.concluir(p);conferir(a);const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);
});
caso('todos os grupos e recuperações terminam vazios, mas nunca liberam criação',()=>{
 const a=preparado();for(let grupo=0;grupo<11;grupo++){
  const p=a.ctx.r53NovaFichaMemoriasPrevia(a.ss,a.context,grupo);let r;
  do{r=a.ctx.r53NovaFichaMemoriasAplicar(a.ss,a.context,grupo,p.assinatura);assert.equal(r.criacaoDisponivel,false);}while(!r.concluido);
 }
 const p=a.ctx.r53NovaFichaRecuperacaoPrevia(a.ss,a.context,recovery);a.ctx.r53NovaFichaRecuperacaoAplicar(a.ss,a.context,recovery,p.assinatura);
 const s=a.ctx.r53NovaFichaMemoriasInspecionar(a.ss,a.context);assert.equal(s.restantes,0);assert.equal(s.recuperacoes.length,0);assert.equal(s.criacaoDisponivel,false);
 assert.equal(JSON.stringify([...a.cells]),a.antes.cells);assert.equal(JSON.stringify([...a.script]),a.antes.script);
});
for(const k of ['r53_recuperacao_personagem','r53_recuperacao_1793189000000_extra','r53_classe_visivel_feitico.999','r53_classe_visivel_constructor'])caso('namespace desconhecido recusado '+k,()=>{
 const a=preparado();a.doc.set(k,'NÃO APAGAR');assert.throws(()=>a.previa(),/desconhecida/);assert.equal(a.writes.length,0);assert.equal(a.doc.get(k),'NÃO APAGAR');
});
for(const k of ['salario_extrato','r53_nova_ficha_financeiro_v1','r53_recuperacao_123','r53_recuperacao_1793189000000x',recovery+'\n',null,123])caso('seletor não aceita outra propriedade '+k,()=>{
 const a=preparado();assert.throws(()=>a.ctx.r53NovaFichaRecuperacaoPrevia(a.ss,a.context,k),/identificador/);assert.equal(a.writes.length,0);
});
for(const grupo of [-1,11,0.5,'0',null,NaN])caso('grupo inválido '+grupo,()=>{const a=preparado();assert.throws(()=>a.ctx.r53NovaFichaMemoriasPrevia(a.ss,a.context,grupo),/grupo/);assert.equal(a.writes.length,0);});
caso('recuperação inexistente não cria diário novo',()=>{const a=preparado(null,'r53_recuperacao_1793189999999');assert.throws(()=>a.previa(),/ausente/);assert.equal(a.writes.length,0);});
caso('edição concorrente após queda não é apagada',()=>{const a=preparado(),p=a.previa();a.aplicar(p);a.doc.set(a.alvos[5],'ALTERADO');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);});
caso('propriedade recriada após conclusão não é apagada',()=>{const a=preparado(),p=a.previa();a.concluir(p);a.doc.set(a.alvos[0],'CONTEÚDO PRIVADO '+a.alvos[0]);const n=a.writes.length;assert.throws(()=>a.aplicar(p),/já foi usada/);assert.equal(a.writes.length,n);});
caso('nova recuperação é encontrada na inspeção final, não some na confirmação de outro grupo',()=>{const a=preparado(),p=a.previa();a.aplicar(p);a.doc.set('r53_recuperacao_1793189000002','nova');a.concluir(p);assert(a.ctx.r53NovaFichaMemoriasInspecionar(a.ss,a.context).recuperacoes.includes('r53_recuperacao_1793189000002'));});
caso('contrato/versões do editor mudados recusados',()=>{const a=preparado();a.ctx.R53_EDITOR_.contextos[0].classes.push(8);assert.throws(()=>a.previa(),/editor fora/);assert.equal(a.writes.length,0);});
for(const op of [{id:'1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k'},{ativoDiferente:true},{ocupado:true}])caso('alvo oficial, vínculo ou trava incorretos recusados '+JSON.stringify(op),()=>{const a=preparado(0,null,op);assert.throws(()=>a.concluir(a.previa()),/alvo|documento vinculado|operação em andamento/);assert.equal(a.writes.length,0);});
caso('diário adulterado não é reiniciado',()=>{const a=preparado(),p=a.previa();a.aplicar(p);a.doc.set(a.perfil().diario,'{');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/diário inválido/);assert.equal(a.writes.length,n);});
caso('leitor real do editor não reutiliza a versão em memória após a limpeza',()=>{
 const a=preparado();a.ctx.R53_REF_CACHE_={versoes:{campos:a.ctx.R53_EDITOR_.campos.length,lista:[['ANTIGO',['PERSONAGEM ANTIGO']]]}};
 a.doc.set('r53_versoes',JSON.stringify(a.ctx.R53_REF_CACHE_.versoes));a.concluir(a.previa());
 assert.equal(a.ctx.r53Versoes_().lista.length,0);
});
caso('conteúdo enorme ou malformado é apenas resumido por hash, não copiado ao diário',()=>{
 const a=preparado(null,recovery);a.doc.set(recovery,'PRIVADO '.repeat(1000));a.concluir(a.previa());conferir(a);
});
caso('nova chave desconhecida no meio da execução impede retomada',()=>{
 const a=preparado(),p=a.previa();a.aplicar(p);a.doc.set('r53_recuperacao_formato_novo','preservar');const n=a.writes.length;
 assert.throws(()=>a.aplicar(p),/desconhecida/);assert.equal(a.writes.length,n);
});
caso('outra operação não reutiliza diário de recuperação',()=>{
 const a=preparado(null,recovery),p=a.previa();a.concluir(p);a.context.operacao='outra_operacao_000001';const n=a.writes.length;
 assert.throws(()=>a.aplicar(p),/operação diferente/);assert.equal(a.writes.length,n);
});
console.log(`${casos} cenários offline de memórias/recuperações aprovados; criação e execução nativa pendentes.`);
