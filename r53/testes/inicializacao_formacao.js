'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process');
const {ambiente,a1}=require('./apoio_inicializacao');
const root=path.resolve(__dirname,'../..'),g={};vm.createContext(g);for(const n of ['Ficha','Pessoal','Salarios'])vm.runInContext(fs.readFileSync(path.join(root,'apps-script/'+n+'.gs'),'utf8'),g);
const original=new Map(g.ABAS.map(x=>[x.nome,new Map(x.vals.map(v=>[v[0]+','+v[1],v[2]]))]));
for(const x of g.VALORES_CUSTOM_)for(const [r,c,v]of x.vals)original.get(x.nome)?.set(r+','+c,v);
original.get('FICHA PESSOAL').set('86,23',g.SALARIO_.f.total);
const letra=n=>{let s='';while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;};
const valor=(s,a)=>{const p=a1(a);return original.get(s).get(p[0]+','+p[1])??'';};
const nota=(s,a)=>g.ABAS.find(x=>x.nome===s).notas?.find(x=>x[0]===a)?.[1]||'';
const sources=['contrato_formacao','formacao'].map(n=>fs.readFileSync(path.join(root,'r53/inicializacao/'+n+'.gs'),'utf8'));
const nomes=['grau_origem','pericias','oficios_tr','armas'];
let casos=0;function caso(n,f){try{f();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
function visitar(x,fn){const [r,c,r2,c2]=a1(x.faixa);for(let rr=r;rr<=r2;rr++)for(let cc=c;cc<=c2;cc++)fn(letra(cc)+rr,rr-r,cc-c);}
function preparado(nome){const a=ambiente();for(const f of sources)vm.runInContext(f,a.ctx);a.nome=nome;a.c=a.ctx.R53_NOVA_FORMACAO_CONTRATO_.dominios[nome];
 for(const x of a.c.guardas)visitar(x,addr=>{const v=valor(x.aba,addr);a.put(x.aba,addr,typeof v==='string'&&v.startsWith('=')?123:v,typeof v==='string'&&v.startsWith('=')?v:'','INSTRUÇÃO NO RÓTULO');});
 for(const x of a.c.entradas)visitar(x,addr=>a.put(x.aba,addr,x.tipo==='bool'?true:x.tipo==='bonus'?44:'TEXTO PRIVADO ANTIGO','','NOTA PRIVADA ANTIGA'));
 a.put('CONFIGURAÇÃO','AK51','REGRA CUSTOM DA MESA');a.put('CONFIGURAÇÃO','F46',10);a.put('FICHA','AH11',30);a.put('DADOS','CZ54',3700);a.put('FICHA PESSOAL','Q27','HISTÓRIA PRESERVADA');a.put('FICHA PESSOAL','D92','INVENTÁRIO PRESERVADO');
 // O espelho antigo B47 é derivado, não entrada a apagar.
 {const v=valor('FICHA','N439');a.put('FICHA','N439',1,typeof v==='string'&&v.startsWith('=')?v:'');}
 a.previa=()=>a.ctx.r53NovaPerfilPrevia_(a.ss,a.context,a.ctx.r53NovaFormPerfil_(nome));a.aplicar=p=>a.ctx.r53NovaPerfilAplicar_(a.ss,a.context,p.assinatura,a.ctx.r53NovaFormPerfil_(nome));
 a.concluir=p=>{for(let i=0;i<40;i++){const r=a.aplicar(p);if(r.concluido)return r;assert.equal(r.retomar,true);}throw Error('retomadas demais');};return a;
}
function conferir(a){for(const x of a.c.entradas)visitar(x,addr=>{const r=a.range(x.aba,addr),v=valor(x.aba,addr);if(x.tipo==='formula')assert.equal(r.getFormulas()[0][0],v);else{assert.equal(r.getValue(),v);assert.equal(r.getFormulas()[0][0],'');}assert.equal(r.getNotes()[0][0],nota(x.aba,addr));});
 for(const x of a.c.guardas)visitar(x,addr=>{const v=valor(x.aba,addr),r=a.range(x.aba,addr);if(typeof v==='string'&&v.startsWith('='))assert.equal(r.getFormulas()[0][0],v);else assert.equal(r.getValue(),v);assert.equal(r.getNotes()[0][0],'INSTRUÇÃO NO RÓTULO');});
 assert.equal(a.range('CONFIGURAÇÃO','AK51').getValue(),'REGRA CUSTOM DA MESA');assert.equal(a.range('CONFIGURAÇÃO','F46').getValue(),10);assert.equal(a.range('FICHA','AH11').getValue(),30);assert.equal(a.range('DADOS','CZ54').getValue(),3700);
 assert.equal(a.range('FICHA PESSOAL','Q27').getValue(),'HISTÓRIA PRESERVADA');assert.equal(a.range('FICHA PESSOAL','D92').getValue(),'INVENTÁRIO PRESERVADO');assert.equal(a.range('FICHA','N439').getFormulas()[0][0],String(valor('FICHA','N439')).startsWith('=')?valor('FICHA','N439'):'');assert.equal(a.range('EXTRATO','A2').getValue(),'SEGREDO financeiro');
 assert.equal(a.doc.get('r53_recuperacao_personagem'),'recuperação fora deste domínio');
 for(const c of a.cells.values()){assert.equal(c.fmt,'tema');assert.equal(c.dv,'menu');}
 const raw=a.doc.get(a.ctx.r53NovaFormPerfil_(a.nome).diario);assert(Buffer.byteLength(raw)<9000);assert(!raw.includes('PRIVADO'));assert(!raw.includes('NOTA PRIVADA'));assert.equal(JSON.parse(raw).concluido,true);assert(!a.locked());
}
caso('contrato e fontes independentes concordam sem regeneração',()=>{
 execFileSync(process.execPath,['r53/inicializacao/gerar_contrato_formacao.js','--conferir'],{cwd:root});
 const quant={grau_origem:10,pericias:99,oficios_tr:94,armas:65};
 for(const n of nomes){const a=preparado(n);let total=0;for(const x of a.c.entradas)visitar(x,(addr,i,j)=>{total++;assert.equal(x.valores[i][j],valor(x.aba,addr));assert.equal(x.notas[i][j],nota(x.aba,addr));});assert.equal(total,quant[n]);}
});
for(const nome of nomes){
 caso(nome+' aplica e repete sem gravar, sem liberar criação',()=>{const a=preparado(nome),p=a.previa();assert.equal(a.writes.length,0);assert.equal(p.criacaoDisponivel,false);const r=a.concluir(p);assert.equal(r.criacaoDisponivel,false);assert(r.pendente.includes('conferencia_conjunta'));conferir(a);const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);});
 caso(nome+' quatro escritas por chamada e retomada',()=>{const a=preparado(nome),p=a.previa(),r=a.aplicar(p);assert.equal(r.retomar,true);assert.equal(r.concluido,false);assert.equal(a.writes.filter(x=>x[0]!=='propriedade').length,4);a.concluir(p);conferir(a);});
 caso(nome+' edição depois da prévia invalida sem escrever',()=>{const a=preparado(nome),p=a.previa(),x=a.c.entradas[0];a.put(x.aba,x.faixa.split(':')[0],'EDIÇÃO RECENTE');assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);});
 caso(nome+' rótulo ou fórmula protegida adulterada não passa',()=>{const a=preparado(nome),x=a.c.guardas[0];a.put(x.aba,x.faixa.split(':')[0],'OUTRO');assert.throws(()=>a.previa(),/formação não reconhecid/);assert.equal(a.writes.length,0);});
 caso(nome+' fórmula desconhecida na entrada não é apagada',()=>{const a=preparado(nome),x=a.c.entradas[0];a.put(x.aba,x.faixa.split(':')[0],1,'=1');assert.throws(()=>a.previa(),/fórmula inesperada|fórmula pessoal/);assert.equal(a.writes.length,0);});
 caso(nome+' nova nota depois de usado não é sobrescrita',()=>{const a=preparado(nome),p=a.previa();a.concluir(p);const x=a.c.entradas[0],addr=x.faixa.split(':')[0],r=a.range(x.aba,addr);a.put(x.aba,addr,r.getValue(),r.getFormulas()[0][0],'NOTA NOVA');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados|já foi usada/);assert.equal(a.writes.length,n);});
 caso(nome+' imagem em entrada é recusada antes de escrever',()=>{const a=preparado(nome),x=a.c.entradas[0];a.put(x.aba,x.faixa.split(':')[0],{valueType:'IMAGE'});assert.throws(()=>a.previa(),/imagem ou valor/);assert.equal(a.writes.length,0);});
 const b=preparado(nome);b.concluir(b.previa());
 for(let k=1;k<=b.writes.length;k++)for(const fase of ['antes','depois'])caso(nome+' queda '+fase+' '+k,()=>{const a=preparado(nome),p=a.previa();let n=0;a.hook(f=>{if(f===fase&&++n===k)throw Error('queda');});assert.throws(()=>a.concluir(p),/queda/);assert(!a.locked());a.hook(null);a.concluir(p);conferir(a);});
}
caso('Grau volta ao 4 da fábrica, sem deduzir pelo nível 30',()=>{const a=preparado('grau_origem');a.concluir(a.previa());assert.equal(a.range('FICHA PESSOAL','AB11').getValue(),'Grau 4');assert.equal(a.range('FICHA','AH11').getValue(),30);assert.equal(a.range('CARTEIRA','AT3').getValue(),true);assert.equal(a.range('FICHA PESSOAL','O86').getValue(),-500);});
caso('Origem restaura fórmulas e a instrução do menu, não copia a prosa',()=>{const a=preparado('grau_origem');a.concluir(a.previa());for(const col of ['D','R','AH']){assert.equal(a.range('FICHA PESSOAL',col+'44').getValue(),'');assert.equal(a.range('FICHA PESSOAL',col+'45').getFormulas()[0][0],valor('FICHA PESSOAL',col+'45'));}assert(nota('FICHA PESSOAL','D44').length>200);assert.equal(a.range('FICHA PESSOAL','D44').getNotes()[0][0],nota('FICHA PESSOAL','D44'));});
caso('custom B47 usa AL, preserva nomes/mirrors derivados e restaura atributo do ofício',()=>{const a=preparado('oficios_tr');a.concluir(a.previa());assert(a.c.entradas.some(x=>x.faixa==='AL118:AL127'));assert(!a.c.entradas.some(x=>x.faixa==='O118:O127'));assert.equal(a.range('FICHA','W118').getFormulas()[0][0],valor('FICHA','W118'));const b=preparado('pericias');b.concluir(b.previa());assert(b.c.entradas.some(x=>x.faixa==='AL94:AL103'));assert(!b.c.entradas.some(x=>x.faixa==='R94:R103'));});
caso('matriz parcialmente alterada não é assumida como gravação completa',()=>{const a=preparado('pericias'),p=a.previa();a.hook((f,t)=>{if(f==='antes'&&t==='valores'){a.put('FICHA','D80',false);throw Error('queda parcial');}});assert.throws(()=>a.aplicar(p),/queda parcial/);a.hook(null);const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);assert.equal(a.range('FICHA','E80').getValue(),true);});
caso('edição em uma nota da matriz depois de queda impede retomada',()=>{const a=preparado('armas'),p=a.previa();a.hook((f,t)=>{if(f==='depois'&&t==='valores')throw Error('queda');});assert.throws(()=>a.aplicar(p),/queda/);a.hook(null);a.put('FICHA PESSOAL','D72',false,'','NOTA NOVA');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);});
caso('normalização do Google após gravar matriz não quebra a pós-condição',()=>{const {variantes}=require('../inicializacao/gerar_contrato_formacao');for(const nome of ['grau_origem','oficios_tr']){const a=preparado(nome);a.hook((f,t)=>{if(f==='depois'&&t==='valores')for(const x of a.c.entradas)if(x.tipo==='formula')visitar(x,(addr,i,j)=>{if(a.range(x.aba,addr).getFormulas()[0][0])a.put(x.aba,addr,999,variantes(x.valores[i][j]).at(-1),a.range(x.aba,addr).getNotes()[0][0]);});});a.concluir(a.previa());for(const x of a.c.entradas)if(x.tipo==='formula')visitar(x,(addr,i,j)=>assert(variantes(x.valores[i][j]).includes(a.range(x.aba,addr).getFormulas()[0][0])));}});
caso('guarda nativa aceita só fórmulas equivalentes sem mudar conta',()=>{const {variantes}=require('../inicializacao/gerar_contrato_formacao');for(const nome of nomes){const a=preparado(nome);for(const x of a.c.guardas)visitar(x,addr=>{const v=valor(x.aba,addr);if(typeof v==='string'&&v.startsWith('='))a.put(x.aba,addr,999,variantes(v).at(-1));});a.concluir(a.previa());}const b=preparado('grau_origem');b.put('FICHA PESSOAL','D51',1,'=1');assert.throws(()=>b.previa(),/protegida/);});
caso('contrato e domínio inexistentes não criam escrita',()=>{const a=preparado('armas');assert.throws(()=>a.ctx.r53NovaFormContrato_('constructor'),/contrato/);a.ctx.R53_NOVA_FORMACAO_CONTRATO_=undefined;assert.throws(()=>a.previa(),/contrato/);assert.equal(a.writes.length,0);});
caso('saldo protegido usa o preparador salarial, não a antiga apresentação mensal',()=>{
 const a=preparado('grau_origem'),antiga=g.VALORES_CUSTOM_.find(x=>x.nome==='FICHA PESSOAL').vals.find(x=>x[0]===86&&x[1]===23)[2];
 assert.notEqual(antiga,g.SALARIO_.f.total);a.put('FICHA PESSOAL','W86',150000,antiga);
 assert.throws(()=>a.previa(),/protegida/);assert.equal(a.writes.length,0);
});
console.log(`${casos} cenários offline de Grau/Origem/perícias/ofícios/TR/armas aprovados; sem aceite nativo ou criação geral.`);
