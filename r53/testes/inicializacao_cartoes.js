'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict'),{execFileSync}=require('child_process');
const {ambiente,a1}=require('./apoio_inicializacao');
const {contrato,variantes,pos,letra}=require('../inicializacao/gerar_contrato_cartoes');
const root=path.resolve(__dirname,'../..'),original={};vm.createContext(original);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),original);
const maps=new Map(original.ABAS.map(s=>[s.nome,new Map(s.vals.map(x=>[x[0]+','+x[1],x[2]]))]));
for(const s of original.VALORES_CUSTOM_||[])for(const [r,c,v]of s.vals)maps.get(s.nome)?.set(r+','+c,v);
const sourceNames=['apps-script/EditorR53.gs',...['validacoes','contrato_cartoes','cartoes'].map(n=>'r53/inicializacao/'+n+'.gs')];
const scripts=sourceNames.map(p=>new vm.Script(fs.readFileSync(path.join(root,p),'utf8')));
let casos=0,bytes=0,maxBytes=0,entradas=0;
const foco=process.argv[2]==='--foco'?new RegExp(process.argv[3]):null;
function caso(nome,fn){if(foco&&!foco.test(nome))return;try{fn();casos++;}catch(e){e.message=nome+': '+e.message;throw e;}}
function descriptor(tipo,args,invalid=false){return {tipo,argumentos:args,permiteInvalido:invalid,ajuda:''};}
function preparado(id='feitico.1',amparo='Neutra',op={}){
 const a=ambiente({...op,validarEntradas:true});for(const s of scripts)s.runInContext(a.ctx);a.id=id;a.g=a.ctx.R53_NOVA_CARTOES_CONTRATO_.contextos[id];const g=a.g;
 for(const name of [g.aba,g.amparo.aba])a.sheets[name]={getRange:addr=>a.range(name,addr)};
 const value=(aba,addr)=>maps.get(aba).get(pos(addr).join(','))??'';
 for(const x of g.guardas){const v=value(g.aba,x.faixa),f=typeof v==='string'&&v.startsWith('=')?v:'';a.put(g.aba,x.faixa,f?123:v,f,'INSTRUÇÃO PRESERVADA');}
 a.put(g.amparo.aba,g.amparo.faixa,amparo,value(g.amparo.aba,g.amparo.faixa));
 a.setDV=(addr,d)=>{const [r,c]=pos(addr);a.cells.set(g.aba+'!'+r+','+c,{...a.get(g.aba,r,c),dv:d});};
 for(const x of g.entradas){a.put(g.aba,x.faixa,'TEXTO PRIVADO','','NOTA PRIVADA');const d=g.dinamicas[x.faixa];a.setDV(x.faixa,d?(g.fixa?descriptor('VALUE_IN_LIST',[['—'],false]):descriptor('CUSTOM_FORMULA',[op.locale==='en_US'?d.formula:d.variantes.at(-1)])):descriptor('VALUE_IN_LIST',[['catálogo preservado'],true],true));}
 a.put('MONTAGENS','B7','VERSÃO FORA DESTE DOMÍNIO');a.put('INVOCAÇÕES','I13','NOME DA ENTIDADE');a.put('FICHA AMALDIÇOADA','D37','Livre');
 a.doc.set('r53_versoes','CACHE PERSISTENTE');
 a.previa=()=>a.ctx.r53NovaFichaCartaoPrevia(a.ss,a.context,id);
 a.aplicar=p=>a.ctx.r53NovaFichaCartaoAplicar(a.ss,a.context,id,p.assinatura);
 a.concluir=p=>{for(let i=0;i<30;i++){const r=a.aplicar(p);assert.equal(r.criacaoDisponivel,false);if(r.concluido)return r;assert.equal(r.retomar,true);}throw Error('retomadas demais');};
 a.antes={cells:new Map(a.cells),doc:new Map(a.doc),script:JSON.stringify([...a.script])};return a;
}
function conferir(a){assert.equal(JSON.stringify(a.ctx.R53_REF_CACHE_),'{}');const alvos=new Set();for(const x of a.g.entradas){const [r,c]=pos(x.faixa),cell=a.get(a.g.aba,r,c),d=a.g.dinamicas[x.faixa];let v=x.valor;
 if(d){const amp=a.range(a.g.amparo.aba,a.g.amparo.faixa).getValue(),open=a.ctx.r53NovaCartAberta_(a.g,d,amp);if(!open)v='—';const actual=JSON.parse(JSON.stringify(cell.dv)),expected=a.ctx.r53NovaCartRegra_(a.ss,a.g,d,open);if(actual.tipo==='CUSTOM_FORMULA'&&d.variantes.includes(actual.argumentos[0]))actual.argumentos=Array.from(expected.argumentos);if(actual.tipo==='CHECKBOX'&&JSON.stringify(actual.argumentos)==='[true,false]')actual.argumentos=[];assert.equal(JSON.stringify(actual),JSON.stringify(expected));}
 else assert.deepEqual(cell.dv,a.antes.cells.get(a.g.aba+'!'+r+','+c).dv);
 assert.equal(cell.v,v);assert.equal(cell.f,'');assert.equal(cell.n,x.nota);assert.equal(cell.fmt,'tema');alvos.add(a.g.aba+'!'+r+','+c);
 }for(const [k,v]of a.antes.cells)if(!alvos.has(k))assert.deepEqual(a.cells.get(k),v,k);
 for(const [k,v]of a.antes.doc)assert.equal(a.doc.get(k),v);assert.equal(JSON.stringify([...a.script]),a.antes.script);
 const raw=a.doc.get(a.ctx.r53NovaCartPerfil_(a.id).diario);assert(Buffer.byteLength(raw)<9000);assert(!raw.includes('PRIVAD'));assert(JSON.parse(raw).concluido);assert(!a.locked());return raw;
}
caso('contrato reproduzível e alvos literais do fonte completo',()=>{
 execFileSync(process.execPath,['r53/inicializacao/gerar_contrato_cartoes.js','--conferir'],{cwd:root});assert.equal(Object.keys(contrato.contextos).length,249);
 for(const g of Object.values(contrato.contextos))for(const x of g.entradas){const v=maps.get(g.aba).get(pos(x.faixa).join(','))??'';assert.equal(x.valor,v);assert(!String(v).startsWith('='));}
});
for(const id of Object.keys(contrato.contextos))caso(id+' inicializa com quatro escritas por chamada e repete sem alterar',()=>{
 const a=preparado(id),p=a.previa();assert.equal(a.writes.length,0);assert.equal(p.criacaoDisponivel,false);const r=a.aplicar(p);assert.equal(r.concluido,false);assert.equal(a.writes.filter(x=>x[0]!=='propriedade').length,4);a.concluir(p);const raw=conferir(a);bytes+=Buffer.byteLength(raw);maxBytes=Math.max(maxBytes,Buffer.byteLength(raw));entradas+=a.g.entradas.length;
 const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);
});
const modos=[...new Set(original.R53_EDITOR_.contextos.map(c=>c.modo))].map(m=>original.R53_EDITOR_.contextos.find(c=>c.modo===m).id);
for(const id of modos){
 for(const amp of ['Fechada','Livre','Normal'])caso(id+' resolve portas '+amp,()=>{const a=preparado(id,amp);a.concluir(a.previa());conferir(a);});
 const base=preparado(id);base.concluir(base.previa());
 // Cada escrita de dados/validação/nota e os dois checkpoints do diário.
 for(let k=1;k<=base.writes.length;k++)for(const fase of ['antes','depois'])caso(id+' queda '+fase+' '+k,()=>{const a=preparado(id),p=a.previa();let n=0;a.hook(f=>{if(f===fase&&++n===k)throw Error('queda');});assert.throws(()=>a.concluir(p),/queda/);assert(!a.locked());a.hook(null);a.concluir(p);conferir(a);});
 caso(id+' fórmula desconhecida na entrada impede apagar',()=>{const a=preparado(id);a.put(a.g.aba,a.g.entradas[0].faixa,7,'=1');assert.throws(()=>a.previa(),/fórmula inesperada/);assert.equal(a.writes.length,0);});
}
for(const id of ['entidade.1.ext.1','entidade.12.ext.3'])caso(id+' troca Classe 0 antiga pela Classe 1 de fábrica antes de resolver funções',()=>{
 const a=preparado(id,'Livre'),classe=a.g.entradas.find(x=>x.chave==='classe');
 assert.equal(maps.get(a.g.aba).get(pos(classe.faixa).join(',')),1);a.put(a.g.aba,classe.faixa,0);
 a.concluir(a.previa());conferir(a);assert.equal(a.range(a.g.aba,classe.faixa).getValue(),1);
 for(const x of a.g.entradas)if(['cura','vt'].includes(x.funcao))assert.equal(a.range(a.g.aba,x.faixa).getValue(),0);
 const zero={...a.g,classe:0};for(const d of Object.values(a.g.dinamicas))if(d.key!=='dano')assert.equal(a.ctx.r53NovaCartAberta_(zero,d,'Livre'),false);
});
caso('validação é gravada antes do valor e queda entre ambas é retomada',()=>{const a=preparado('entidade.1.bas.1'),p=a.previa();a.hook((f,t)=>{if(f==='depois'&&t==='validacao')throw Error('queda');});assert.throws(()=>a.concluir(p),/queda/);a.hook(null);a.concluir(p);conferir(a);});
caso('Amparo alterado após prévia impede a primeira escrita',()=>{const a=preparado(),p=a.previa(),r=a.range(a.g.amparo.aba,a.g.amparo.faixa);a.put(a.g.amparo.aba,a.g.amparo.faixa,'Fechada',r.getFormulas()[0][0]);assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);});
caso('Amparo alterado durante a retomada não aceita o plano antigo',()=>{const a=preparado(),p=a.previa();a.aplicar(p);const r=a.range(a.g.amparo.aba,a.g.amparo.faixa);a.put(a.g.amparo.aba,a.g.amparo.faixa,'Fechada',r.getFormulas()[0][0]);const n=a.writes.length;assert.throws(()=>a.aplicar(p),/estrutura/);assert.equal(a.writes.length,n);});
for(const bad of ['',null,'#REF!',42,'estado novo'])caso('Amparo inválido '+bad,()=>{const a=preparado('feitico.1',bad);assert.throws(()=>a.previa(),/Amparo ainda/);assert.equal(a.writes.length,0);});
for(const dv of [null,descriptor('VALUE_IN_LIST',[['—','dano'],false]),descriptor('CUSTOM_FORMULA',['=TRUE']),descriptor('CHECKBOX',['sim','não']),{...descriptor('CHECKBOX',[]),ajuda:'nova ajuda'}])caso('validação desconhecida não é substituída '+JSON.stringify(dv),()=>{const a=preparado('entidade.1.bas.1');a.setDV('J76',dv);assert.throws(()=>a.previa(),/validação de função/);assert.equal(a.writes.length,0);});
caso('mudança em menu preservado bloqueia retomada',()=>{const a=preparado(),p=a.previa();a.aplicar(p);a.setDV('E69',descriptor('VALUE_IN_LIST',[['OUTRA LISTA'],true],true));const n=a.writes.length;assert.throws(()=>a.aplicar(p),/estrutura/);assert.equal(a.writes.length,n);});
caso('edição de nota após queda não é apagada',()=>{const a=preparado(),p=a.previa();a.aplicar(p);a.put(a.g.aba,'D66','TEXTO PRIVADO','','NOVA NOTA');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);});
caso('não reinicializa cartão usado nem remove diário corrompido',()=>{const a=preparado(),p=a.previa();a.concluir(p);a.put(a.g.aba,'E64','NOVO PERSONAGEM');let n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados|já foi usada/);assert.equal(a.writes.length,n);a.doc.set(a.ctx.r53NovaCartPerfil_(a.id).diario,'{');assert.throws(()=>a.aplicar(p),/diário inválido/);assert.equal(a.writes.length,n);});
for(const op of [{id:'1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k'},{ativoDiferente:true},{ocupado:true}])caso('alvo ou trava inválidos '+JSON.stringify(op),()=>{const a=preparado('feitico.1','Neutra',op);assert.throws(()=>a.concluir(a.previa()),/alvo|vinculado|andamento/);assert.equal(a.writes.length,0);});
for(const id of ['constructor','__proto__','feitico.999',null])caso('ID não confiável '+id,()=>{const a=preparado();assert.throws(()=>a.ctx.r53NovaFichaCartaoPrevia(a.ss,a.context,id),/desconhecido/);assert.equal(a.writes.length,0);});
caso('mudança no contrato do editor impede escrita',()=>{const a=preparado();a.ctx.R53_EDITOR_.contextos[0].portas.dano='FALSE';assert.throws(()=>a.previa(),/editor fora/);assert.equal(a.writes.length,0);});
caso('guarda ou Amparo com fórmula diferente recusados',()=>{for(const amp of [true,false]){const a=preparado();if(amp)a.put(a.g.amparo.aba,a.g.amparo.faixa,'Livre','=1');else{const x=a.g.guardas[0];a.put(a.g.aba,x.faixa,1,'=1');}assert.throws(()=>a.previa(),/desconhecid/);assert.equal(a.writes.length,0);}});
caso('checkbox padrão explícito é aceito, mas texto equivalente não é',()=>{const a=preparado('classe0.1');a.setDV('Q323',descriptor('CHECKBOX',[true,false]));a.concluir(a.previa());conferir(a);});
caso('idioma inglês preserva vírgulas nas fórmulas de validação',()=>{const a=preparado('feitico.1','Neutra',{locale:'en_US'});a.concluir(a.previa());conferir(a);assert(a.get(a.g.aba,71,5).dv.argumentos[0].includes(','));});
caso('imagem em entrada não é apagada',()=>{const a=preparado();a.put(a.g.aba,'E64',{valueType:'IMAGE'});assert.throws(()=>a.previa(),/imagem ou valor/);assert.equal(a.writes.length,0);});
caso('nova mescla com âncora diferente impede limpar entrada',()=>{const a=preparado(),base=a.sheets[a.g.aba].getRange;a.sheets[a.g.aba].getRange=addr=>({...base(addr),getMergedRanges:()=>addr==='E64'?[{getRow:()=>64,getColumn:()=>4}]:[]});assert.throws(()=>a.previa(),/interior de mescla/);assert.equal(a.writes.length,0);});
caso('fórmula de validação com conta alterada não é normalizada',()=>{const a=preparado(),d=a.g.dinamicas.E71;a.setDV('E71',descriptor('CUSTOM_FORMULA',[d.formula+'+1']));assert.throws(()=>a.previa(),/validação de função/);assert.equal(a.writes.length,0);});
caso('quota agregada é sinalizada como impedimento da integração, sem ignorar limite individual',()=>{assert(bytes>500*1024);assert(maxBytes<9000);});
console.log(`${foco?"FOCO PARCIAL · ":""}${casos} cenários offline de cartões visíveis aprovados; ${entradas} entradas; diários ${bytes} bytes, maior ${maxBytes}. Quota conjunta e prova nativa pendentes.`);
