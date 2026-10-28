'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process');
const {ambiente,a1}=require('./apoio_inicializacao');
const {contrato,visitar,variantes,letra}=require('../inicializacao/gerar_contrato_entidades');
const root=path.resolve(__dirname,'../..'),full={};vm.createContext(full);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),full);
const sheet=full.ABAS.find(s=>s.nome==='INVOCAÇÕES'),orig=new Map(sheet.vals.map(([r,c,v])=>[r+','+c,v])),notes=new Map(sheet.notas);
const scripts=['validacoes','formacao','contrato_entidades','entidades'].map(n=>new vm.Script(fs.readFileSync(path.join(root,'r53/inicializacao/'+n+'.gs'),'utf8')));
const nomes=Object.keys(contrato.dominios),acumulados=new Map();let casos=0,entradas=0,bytes=0,maiorPendente=0;
function caso(nome,fn){try{fn();casos++;}catch(e){e.message=nome+': '+e.message;throw e;}}
function preparar(id='1_identidade',op={}){
 const a=ambiente({...op,validarEntradas:true});for(const s of scripts)s.runInContext(a.ctx);a.id=id;a.c=a.ctx.r53NovaEntContrato_(id);
 a.sheets['INVOCAÇÕES']={getRange:addr=>{
 const x=a.c.entradas.find(x=>x.faixa===addr);return {...a.range('INVOCAÇÕES',addr),getMergedRanges:()=> (x?.mesclas||[]).map(m=>({getRow:()=>m[0],getColumn:()=>m[1],getLastRow:()=>m[2],getLastColumn:()=>m[3]}))};
 }};
 a.setDV=(addr,d)=>{const [r,c]=a1(addr);a.cells.set('INVOCAÇÕES!'+r+','+c,{...a.get('INVOCAÇÕES',r,c),dv:d});};
 a.rawDV=d=>{if(!d)return null;const out=JSON.parse(JSON.stringify(d));if(op.estritos)out.permiteInvalido=false;if(d.tipo==='VALUE_IN_RANGE'){
 const ref=d.argumentos[0];out.argumentos=[{getA1Notation:()=>ref.faixa,getSheet:()=>({getName:()=>ref.aba,getParent:()=>({getId:()=>a.ss.getId()})})},true];}return out;};
 for(const x of a.c.guardas){const [r,c]=a1(x.faixa),v=orig.get(r+','+c),f=typeof v==='string'&&v.startsWith('=')?v:'';a.put('INVOCAÇÕES',x.faixa,f?999:v,f,'INSTRUÇÃO PRESERVADA');}
 if(a.c.foto)a.put('INVOCAÇÕES',a.c.foto,'FOTO\n式神','','FOTO INTACTA');
 // Inicializar também os domínios vizinhos da mesma entidade com dados antigos:
 // uma etapa não pode apagar nem exigir que outra já esteja vazia.
 for(const [n,d]of Object.entries(contrato.dominios).filter(([n,d])=>d.entidade===a.c.entidade))for(const x of d.entradas)visitar(x.faixa,addr=>{
  const [r,c]=a1(addr),i=r-a1(x.faixa)[0],j=c-a1(x.faixa)[1],dv=x.validacoes[i][j];
  const valor=dv?.tipo==='VALUE_IN_LIST'?dv.argumentos[0].at(-1):'DADO PRIVADO';
  a.put('INVOCAÇÕES',addr,valor,'','NOTA PRIVADA');a.setDV(addr,a.rawDV(dv));
 });
 a.put('CONFIGURAÇÃO','F139',7);a.put('DADOS_CRIACAO','H11','Família custom * ?');a.put('DADOS_ENTIDADES','A2','Tipo custom');
 a.put('MONTAGENS','B7','CARTÃO FORA DESTE DOMÍNIO');a.put('FICHA AMALDIÇOADA','E64','CARTÃO VISÍVEL FORA');
 a.doc.set('r53_versoes','CACHE PERSISTENTE FORA');a.ctx.R53_REF_CACHE_={versoes:'antigo'};
 for(const [k,v]of op.diarios||[])a.doc.set(k,v);
 a.antes={cells:new Map(a.cells),doc:new Map(a.doc),script:new Map(a.script)};
 a.previa=()=>a.ctx.r53NovaFichaEntidadePrevia(a.ss,a.context,id);
 a.aplicar=p=>a.ctx.r53NovaFichaEntidadeAplicar(a.ss,a.context,id,p.assinatura);
 a.concluir=p=>{for(let n=0;n<30;n++){const r=a.aplicar(p);assert.equal(r.criacaoDisponivel,false);const raw=a.doc.get(a.ctx.r53NovaEntPerfil_(id).diario);if(!r.concluido)maiorPendente=Math.max(maiorPendente,Buffer.byteLength(raw));if(r.concluido)return r;assert(r.retomar);}throw Error('retomadas demais');};return a;
}
function conferir(a){const alvos=new Set();for(const x of a.c.entradas)visitar(x.faixa,(addr,r,c)=>{
 const [r0,c0]=a1(x.faixa),i=r-r0,j=c-c0,cell=a.get('INVOCAÇÕES',r,c);alvos.add('INVOCAÇÕES!'+r+','+c);
 if(x.tipo==='formula')assert(x.equivalentes[i][j].includes(cell.f));else{assert.equal(cell.v,x.valores[i][j]);assert.equal(cell.f,'');}
 assert.equal(cell.n,x.notas[i][j]);assert.equal(cell.fmt,'tema');assert.equal(cell.dv,a.antes.cells.get('INVOCAÇÕES!'+r+','+c).dv);
 });for(const [k,v]of a.antes.cells)if(!alvos.has(k))assert.deepEqual(a.cells.get(k),v,k);
 for(const [k,v]of a.antes.doc)assert.equal(a.doc.get(k),v,k);assert.deepEqual(a.script,a.antes.script);
 const raw=a.doc.get(a.ctx.r53NovaEntPerfil_(a.id).diario);assert.equal(JSON.parse(raw).recibo,1);assert(!/PRIVAD/.test(raw));assert(Buffer.byteLength(raw)<9000);assert(!a.locked());assert.equal(JSON.stringify(a.ctx.R53_REF_CACHE_),'{}');return raw;
}
caso('contrato reproduzível, 73 perfis e 1165 entradas explícitas sem cartões',()=>{
 execFileSync(process.execPath,['r53/inicializacao/gerar_contrato_entidades.js','--conferir'],{cwd:root});assert.equal(nomes.length,73);
 const vistos=new Set();let n=0;for(const [id,d]of Object.entries(contrato.dominios))for(const x of d.entradas)visitar(x.faixa,(addr,r,c)=>{
 const key='INVOCAÇÕES!'+addr;assert(!vistos.has(key));vistos.add(key);n++;
 const i=r-a1(x.faixa)[0],j=c-a1(x.faixa)[1];assert.equal(x.valores[i][j],orig.get(r+','+c)??'');assert.equal(x.notas[i][j],notes.get(addr)||'');
 for(const card of full.R53_EDITOR_.contextos.filter(c=>c.aba==='INVOCAÇÕES')){assert(!Object.values(card.entradas_diretas).includes(addr));assert(!Object.values(card.cel).includes(addr));}
 });assert.equal(n,1165);
});
for(const id of nomes)caso(id+' restaura apenas seus alvos, acumula recibo e repete sem gravar',()=>{
 const a=preparar(id,{diarios:acumulados,estritos:true}),p=a.previa();assert.equal(a.writes.length,0);assert.equal(p.criacaoDisponivel,false);a.concluir(p);const raw=conferir(a);
 acumulados.set(a.ctx.r53NovaEntPerfil_(id).diario,raw);bytes+=Buffer.byteLength(raw);for(const x of a.c.entradas)visitar(x.faixa,()=>entradas++);
 const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);
});
for(const id of ['1_identidade','1_atributos_treinos','1_recursos','1_familias','1_inventario','1_talentos_expansao','conjunto']){
 const base=preparar(id);base.concluir(base.previa());
 for(let k=1;k<=base.writes.length;k++)for(const fase of ['antes','depois'])caso(id+' queda '+fase+' '+k,()=>{
  const a=preparar(id),p=a.previa();let n=0;a.hook(f=>{if(f===fase&&++n===k)throw Error('queda');});assert.throws(()=>a.concluir(p),/queda/);assert(!a.locked());a.hook(null);a.concluir(p);conferir(a);
 });
 caso(id+' edição entre prévia e aplicação recusa sem escrever',()=>{const a=preparar(id),p=a.previa();a.put('INVOCAÇÕES',a.c.entradas[0].faixa.split(':')[0],'MUDOU');assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);});
 caso(id+' nova nota após conclusão não permite limpar novamente',()=>{const a=preparar(id),p=a.previa();a.concluir(p);const addr=a.c.entradas[0].faixa.split(':')[0],r=a.range('INVOCAÇÕES',addr);a.put('INVOCAÇÕES',addr,r.getValue(),r.getFormulas()[0][0],'NOTA NOVA');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/já foi usada/);assert.equal(a.writes.length,n);});
 caso(id+' imagem na entrada não é apagada',()=>{const a=preparar(id);a.put('INVOCAÇÕES',a.c.entradas[0].faixa.split(':')[0],{valueType:'IMAGE'});assert.throws(()=>a.previa(),/imagem ou valor/);assert.equal(a.writes.length,0);});
}
for(const id of ['1_recursos','12_recursos','1_familias','12_familias'])caso(id+' fórmulas reconhecidas normalizadas e desconhecidas recusadas',()=>{
 const a=preparar(id);for(const x of a.c.entradas)if(x.tipo==='formula')visitar(x.faixa,(addr,r,c)=>a.put('INVOCAÇÕES',addr,77,x.equivalentes[r-a1(x.faixa)[0]][c-a1(x.faixa)[1]].at(-1),'NOTA PRIVADA'));
 const p=a.previa();a.hook((fase,tipo)=>{if(fase==='depois'&&tipo==='valores')for(const x of a.c.entradas)if(x.tipo==='formula')visitar(x.faixa,(addr,r,c)=>{
  const range=a.range('INVOCAÇÕES',addr);if(range.getFormulas()[0][0])a.put('INVOCAÇÕES',addr,55,x.equivalentes[r-a1(x.faixa)[0]][c-a1(x.faixa)[1]].at(-1),range.getNotes()[0][0]);
 });});a.concluir(p);conferir(a);
 const b=preparar(id),x=b.c.entradas.find(x=>x.tipo==='formula');b.put('INVOCAÇÕES',x.faixa.split(':')[0],1,'=1');assert.throws(()=>b.previa(),/fórmula pessoal/);assert.equal(b.writes.length,0);
});
for(const id of ['1_identidade','12_identidade'])caso(id+' foto em célula ou por fórmula exige arte, sem apagá-la',()=>{
 for(const [v,f]of [[{valueType:'IMAGE'},''],['','=IMAGE("https://example.invalid/a")'],['nome anterior','']]){const a=preparar(id);a.put('INVOCAÇÕES',a.c.foto,v,f);assert.throws(()=>a.previa(),/foto da entidade/);assert.equal(a.writes.length,0);}
 const a=preparar(id);a.put('INVOCAÇÕES',a.c.foto,'');a.concluir(a.previa());assert.equal(a.range('INVOCAÇÕES',a.c.foto).getValue(),'');
});
caso('barra de vida pt_BR é variante exata, sem afrouxar referência, limite ou cor',()=>{
 const a=preparar(),f=orig.get('15,21'),pt='=IFERROR(SPARKLINE(DADOS_INVOC!$GH$2;{"charttype"\\"bar";"max"\\MAX(1;DADOS_INVOC!$GF$2);"color1"\\DADOS_INVOC!$DB$12});"")';assert(variantes(f).includes(pt));
 a.put('INVOCAÇÕES','U15','',pt);a.concluir(a.previa());
 for(const wrong of [pt.replace('$GH$2','$GH$3'),pt.replace('MAX(1;','MAX(2;'),pt.replace('$DB$12','$DB$13')]){const b=preparar();b.put('INVOCAÇÕES','U15','',wrong);assert.throws(()=>b.previa(),/protegida/);assert.equal(b.writes.length,0);}
});
caso('matriz de atributos parcialmente gravada não é assumida como completa',()=>{const a=preparar('1_atributos_treinos'),p=a.previa();a.hook((f,t)=>{if(f==='antes'&&t==='valores'){a.put('INVOCAÇÕES','O20',0);throw Error('queda parcial');}});assert.throws(()=>a.aplicar(p),/queda parcial/);a.hook(null);const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);});
caso('nota concorrente após queda não é apagada',()=>{const a=preparar('1_inventario'),p=a.previa();a.aplicar(p);a.put('INVOCAÇÕES','Y33',7,'','NOTA NOVA');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);});
caso('alteração de rigidez do menu durante retomada é detectada',()=>{const a=preparar('1_identidade'),p=a.previa();a.aplicar(p);a.setDV('I43',{...a.get('INVOCAÇÕES',43,9).dv,permiteInvalido:false});const n=a.writes.length;assert.throws(()=>a.aplicar(p),/estrutura/);assert.equal(a.writes.length,n);});
for(const dv of [null,{tipo:'VALUE_IN_LIST',argumentos:[['outra'],true],permiteInvalido:false,ajuda:''},{tipo:'CUSTOM_FORMULA',argumentos:['=TRUE'],permiteInvalido:true,ajuda:''}])caso('menu desconhecido é recusado '+JSON.stringify(dv),()=>{const a=preparar();a.setDV('I43',dv);assert.throws(()=>a.previa(),/menu da entidade/);assert.equal(a.writes.length,0);});
caso('range de menu de outro arquivo não é aceito',()=>{const a=preparar(),old=a.get('INVOCAÇÕES',43,9).dv,ref=old.argumentos[0];a.setDV('I43',{...old,argumentos:[{getA1Notation:ref.getA1Notation,getSheet:()=>({getName:()=> 'DADOS_ENTIDADES',getParent:()=>({getId:()=> 'outro-arquivo'})})},true]});assert.throws(()=>a.previa(),/menu da entidade/);assert.equal(a.writes.length,0);});
caso('mescla nova que cruza âncoras conhecidas impede limpar',()=>{const a=preparar(),range=a.sheets['INVOCAÇÕES'].getRange;a.sheets['INVOCAÇÕES'].getRange=addr=>({...range(addr),getMergedRanges:()=>addr==='I13'?[{getRow:()=>12,getColumn:()=>9}]:[]});assert.throws(()=>a.previa(),/mescla/);assert.equal(a.writes.length,0);});
for(const [id,range,merge]of [['1_identidade','I13',[13,9,13,10]],['1_atributos_treinos','O20:S20',[20,15,20,19]],['1_identidade','I13',null]])caso('geometria da mescla deve ser exata '+id+range+JSON.stringify(merge),()=>{
 const a=preparar(id),fn=a.sheets['INVOCAÇÕES'].getRange;a.sheets['INVOCAÇÕES'].getRange=addr=>({...fn(addr),getMergedRanges:()=>addr===range?(merge?[{getRow:()=>merge[0],getColumn:()=>merge[1],getLastRow:()=>merge[2],getLastColumn:()=>merge[3]}]:[]):fn(addr).getMergedRanges()});
 assert.throws(()=>a.previa(),/mescla/);assert.equal(a.writes.length,0);
});
for(const id of ['constructor','__proto__','13_identidade','1_qualquer','I13',null,1])caso('grupo não confiável '+id,()=>{const a=preparar();assert.throws(()=>a.ctx.r53NovaFichaEntidadePrevia(a.ss,a.context,id),/desconhecido/);assert.equal(a.writes.length,0);});
for(const op of [{id:'1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k'},{ativoDiferente:true},{ocupado:true}])caso('alvo/trava inválidos '+JSON.stringify(op),()=>{const a=preparar('1_recursos',op);assert.throws(()=>a.concluir(a.previa()),/alvo|vinculado|andamento/);assert.equal(a.writes.length,0);});
caso('máximo de quatro escritas e sem conceder recursos ou estoque',()=>{const a=preparar('12_recursos'),p=a.previa(),r=a.aplicar(p);assert(!r.concluido);assert(r.retomar);assert.equal(a.writes.filter(([t])=>t!=='propriedade').length,4);a.concluir(p);conferir(a);});
caso('73 recibos e maior diário pendente respeitam limites, sem apagar nenhum registro',()=>{assert.equal(acumulados.size,73);assert(bytes<40000);assert(maiorPendente<9000);assert.equal(entradas,1165);});
console.log(`${casos} cenários offline de entidades aprovados; ${entradas} entradas em 73 perfis, recibos ${bytes} bytes, maior diário pendente ${maiorPendente}. Arte, automações, orquestração e prova nativa pendentes.`);
