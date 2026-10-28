'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process'),{ambiente,a1}=require('./apoio_inicializacao');
const {contrato,variantes,letra}=require('../inicializacao/gerar_contrato_montagens');
const root=path.resolve(__dirname,'../..'),native={};vm.createContext(native);
vm.runInContext(require('../../medidas/carregar-ficha').fontes(),native);
const sheet=native.ABAS.find(s=>s.nome==='MONTAGENS'),original=new Map(sheet.vals.map(x=>[x[0]+','+x[1],x[2]]));
const sources=['apps-script/EditorR53.gs','r53/inicializacao/contrato_montagens.gs','r53/inicializacao/montagens.gs'].map(p=>fs.readFileSync(path.join(root,p),'utf8'));
let casos=0;function caso(nome,fn){try{fn();casos++;}catch(e){e.message=nome+': '+e.message;throw e;}}
function visitar(faixa,fn){const [r,c,r2,c2]=a1(faixa);for(let rr=r;rr<=r2;rr++)for(let cc=c;cc<=c2;cc++)fn(letra(cc)+rr,rr,cc);}
function preparado(id='feitico.1',op={}){
 const a=ambiente(op);for(const s of sources)vm.runInContext(s,a.ctx);
 a.id=id;a.c=a.ctx.R53_NOVA_MONTAGENS_CONTRATO_.contextos[id];a.sheets.MONTAGENS={getRange:(addr,c,nr,nc)=>{
  const range=typeof addr==='string'?addr:letra(c)+addr+':'+letra(c+nc-1)+(addr+nr-1),p=a1(range);
  return {...a.range('MONTAGENS',range),getDataValidations:()=>Array.from({length:p[2]-p[0]+1},()=>Array(p[3]-p[1]+1).fill(a.validation||null)),getMergedRanges:()=>a.merged?[{}]:[]};
 }};
 visitar(a.c.leitura,(addr,r,c)=>{const v=original.get(r+','+c)??'';a.put('MONTAGENS',addr,typeof v==='string'&&v.startsWith('=')?123:v,typeof v==='string'&&v.startsWith('=')?v:'','NOTA NO RÓTULO');});
 visitar(a.c.faixa,addr=>a.put('MONTAGENS',addr,'DADO PRIVADO','','NOTA PRIVADA'));
 a.put('MONTAGENS','L1','fora do bloco');a.put('FICHA AMALDIÇOADA','E64','CARTÃO VISÍVEL');a.put('INVOCAÇÕES','I13','NOME DA ENTIDADE');
 a.ctx.R53_REF_CACHE_={versoes:{lista:[['ANTIGO',['DADO PRIVADO']]]}};
 a.previa=()=>a.ctx.r53NovaFichaMontagensPrevia(a.ss,a.context,id);
 a.aplicar=p=>a.ctx.r53NovaFichaMontagensAplicar(a.ss,a.context,id,p.assinatura);
 a.concluir=p=>{for(let i=0;i<10;i++){const r=a.aplicar(p);assert.equal(r.criacaoDisponivel,false);if(r.concluido)return r;}throw Error('retomadas demais');};
 for(const [k,v]of op.diarios||[])a.doc.set(k,v);
 a.antes={cells:new Map(a.cells),doc:new Map(a.doc),script:JSON.stringify([...a.script])};return a;
}
function conferir(a){
 const alvos=new Set();visitar(a.c.faixa,(addr,r,c)=>{alvos.add('MONTAGENS!'+r+','+c);const x=a.get('MONTAGENS',r,c);assert.equal(x.v,original.get(r+','+c)??'');assert.equal(x.f,'');assert.equal(x.n,'');assert.equal(x.fmt,'tema');assert.equal(x.dv,'menu');});
 for(const [key,v]of a.antes.cells)if(!alvos.has(key))assert.deepEqual(a.cells.get(key),v,key);
 for(const [k,v]of a.antes.doc)assert.equal(a.doc.get(k),v,k);assert.equal(JSON.stringify([...a.script]),a.antes.script);
 const raw=a.doc.get(a.ctx.r53NovaMontPerfil_(a.id).diario);assert(Buffer.byteLength(raw)<9000);assert(!raw.includes('PRIVAD'));assert(JSON.parse(raw).concluido);assert(!a.locked());assert.equal(JSON.stringify(a.ctx.R53_REF_CACHE_),'{}');
}
caso('contrato regenerável, fontes integrais, sem fabricar novos valores',()=>{
 execFileSync(process.execPath,['r53/inicializacao/gerar_contrato_montagens.js','--conferir'],{cwd:root});
 assert.equal(Object.keys(contrato.contextos).length,249);assert.equal(contrato.campos.length,33);
 for(const c of Object.values(contrato.contextos))visitar(c.faixa,(_,r,col)=>assert.equal(original.get(r+','+col)??'',contrato.defaults[contrato.campos[r-c.editor-2][0]]));
});
let bytes=0,positions=0;const acumulados=new Map();
for(const id of Object.keys(contrato.contextos))caso(id+' limpa todas as Classes, preserva vizinhos e repete sem escrita',()=>{
 const a=preparado(id,{diarios:acumulados}),p=a.previa();assert.equal(a.writes.length,0);assert.equal(p.criacaoDisponivel,false);a.concluir(p);conferir(a);
 const raw=a.doc.get(a.ctx.r53NovaMontPerfil_(id).diario);acumulados.set(a.ctx.r53NovaMontPerfil_(id).diario,raw);assert.equal(JSON.parse(raw).recibo,1);bytes+=Buffer.byteLength(raw);positions+=33*a.c.classes.length;
 const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);
});
const amostras=[...new Set(native.R53_EDITOR_.contextos.map(c=>c.modo))].map(m=>native.R53_EDITOR_.contextos.find(c=>c.modo===m).id);
for(const id of amostras){
 const b=preparado(id);b.concluir(b.previa());
 for(let i=1;i<=b.writes.length;i++)for(const fase of ['antes','depois'])caso(id+' queda '+fase+' '+i,()=>{
  const a=preparado(id),p=a.previa();let n=0;a.hook(f=>{if(f===fase&&++n===i)throw Error('queda');});assert.throws(()=>a.concluir(p),/queda/);assert(!a.locked());a.hook(null);a.concluir(p);conferir(a);
 });
 caso(id+' edição após a prévia não é apagada',()=>{const a=preparado(id),p=a.previa();a.put('MONTAGENS',a.c.faixa.split(':')[0],'NOVA EDIÇÃO');assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);});
 caso(id+' fórmula em entrada não é apagada',()=>{const a=preparado(id);a.put('MONTAGENS',a.c.faixa.split(':')[0],123,'=1');assert.throws(()=>a.previa(),/fórmula inesperada/);assert.equal(a.writes.length,0);});
 caso(id+' rótulos e fórmulas desconhecidos impedem escrita',()=>{const a=preparado(id);a.put('MONTAGENS','A'+a.c.editor,0,'=1');assert.throws(()=>a.previa(),/fórmula protegida/);assert.equal(a.writes.length,0);const b=preparado(id);b.put('MONTAGENS','A'+(b.c.editor+2),'OUTRO CAMPO');assert.throws(()=>b.previa(),/rótulo/);assert.equal(b.writes.length,0);});
 caso(id+' cartão usado depois não pode ser reinicializado',()=>{const a=preparado(id),p=a.previa();a.concluir(p);a.put('MONTAGENS',a.c.faixa.split(':')[0],true);const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados|já foi usada/);assert.equal(a.writes.length,n);});
}
caso('matriz parcialmente escrita exige revisão; não tenta completar sobre edição',()=>{
 const a=preparado(),p=a.previa();a.hook((fase,tipo)=>{if(fase==='antes'&&tipo==='valores'){a.put('MONTAGENS','B7',false);throw Error('queda parcial');}});assert.throws(()=>a.aplicar(p),/queda parcial/);a.hook(null);const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);
});
caso('nota concorrente depois de queda bloqueia retomada',()=>{
 const a=preparado(),p=a.previa();a.hook((fase,tipo)=>{if(fase==='depois'&&tipo==='valores')throw Error('queda');});assert.throws(()=>a.aplicar(p),/queda/);a.hook(null);a.put('MONTAGENS','B7',false,'','OUTRA NOTA');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);
});
caso('resultado recalculado de título/Classe não invalida, fórmula alterada sim',()=>{
 for(const id of ['maxima.1','entidade.1.maxima.1']){
  const a=preparado(id),p=a.previa(),r=a.c.editor+1,f=a.range('MONTAGENS','B'+r).getFormulas()[0][0];a.put('MONTAGENS','B'+r,7,variantes(f).at(-1),'NOTA NO RÓTULO');a.concluir(p);
  const b=preparado(id);b.put('MONTAGENS','B'+(b.c.editor+1),8,f+'+1');assert.throws(()=>b.previa(),/fórmula protegida/);assert.equal(b.writes.length,0);
 }
});
for(const change of [e=>e.campos.reverse(),e=>e.defaults.preparada=true,e=>e.contextos[0].editor++,e=>e.contextos[0].classes.push(8),e=>e.esquema++])caso('editor alterado falha antes de escrever',()=>{const a=preparado();change(a.ctx.R53_EDITOR_);assert.throws(()=>a.previa(),/editor fora/);assert.equal(a.writes.length,0);});
for(const id of ['constructor','__proto__','feitico.999','B7:H39','feitico.1\n',null,0])caso('ID não confiável recusado '+id,()=>{const a=preparado();assert.throws(()=>a.ctx.r53NovaFichaMontagensPrevia(a.ss,a.context,id),/cartão desconhecido/);assert.equal(a.writes.length,0);});
for(const op of [{id:'1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k'},{ativoDiferente:true},{ocupado:true}])caso('contexto recusado '+JSON.stringify(op),()=>{const a=preparado('feitico.1',op);assert.throws(()=>a.concluir(a.previa()),/alvo|documento vinculado|operação em andamento/);assert.equal(a.writes.length,0);});
caso('modelo registrado não é alvo',()=>{const a=preparado();a.context.arquivosRegistrados=[a.ss.getId()];assert.throws(()=>a.previa(),/alvo não comprovado/);assert.equal(a.writes.length,0);});
caso('diário corrompido e assinatura de outro cartão não são reaproveitados',()=>{
 const a=preparado(),p=a.previa();a.concluir(p);a.doc.set(a.ctx.r53NovaMontPerfil_(a.id).diario,'{');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/diário inválido/);assert.equal(a.writes.length,n);
 const b=preparado('classe0.1');assert.throws(()=>b.aplicar(p),/mudou após/);assert.equal(b.writes.length,0);
});
for(const tipo of ['validation','merged'])caso('estrutura de entrada alterada: '+tipo,()=>{const a=preparado();a[tipo]=true;assert.throws(()=>a.previa(),/validação ou mescla/);assert.equal(a.writes.length,0);});
caso('leitor real volta aos defaults depois de limpar armazenamento e cache persistente',()=>{
 const a=preparado(),g=a.ctx.R53_EDITOR_.contextos[0],old=Array(33).fill('ANTIGO');
 a.doc.set('r53_versoes',JSON.stringify({campos:33,lista:[[g.editor+':2',old]]}));a.ctx.R53_REF_CACHE_={};
 assert.deepEqual(Array.from(a.ctx.r53LerVersao_(a.ss,g,1)),old);
 a.concluir(a.previa());
 // Limpar as células não elimina o cache persistente: a ordem é obrigatória.
 assert.deepEqual(Array.from(a.ctx.r53LerVersao_(a.ss,g,1)),old);
 for(const file of ['contrato_memorias','memorias'])vm.runInContext(fs.readFileSync(path.join(root,'r53/inicializacao/'+file+'.gs'),'utf8'),a.ctx);
 a.doc.delete('r53_recuperacao_personagem');
 const p=a.ctx.r53NovaFichaMemoriasPrevia(a.ss,a.context,0);let r;
 do{r=a.ctx.r53NovaFichaMemoriasAplicar(a.ss,a.context,0,p.assinatura);}while(!r.concluido);
 assert.equal(r.criacaoDisponivel,false);
 for(const cl of g.classes)assert.deepEqual(Array.from(a.ctx.r53LerVersao_(a.ss,g,cl)),Array.from(contrato.campos,f=>contrato.defaults[f[0]]));
});
caso('mesmo todos os diários de MONTAGENS cabem sem valores privados; reserva não certifica quota global',()=>{assert.equal(acumulados.size,249);assert(bytes<150000);});
console.log(`${casos} cenários offline de MONTAGENS aprovados; ${positions} posições em 249 cartões; ${bytes} bytes de diários. Cartões visíveis e execução nativa pendentes.`);
