'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process');
const {ambiente,a1}=require('./apoio_inicializacao');
const root=path.resolve(__dirname,'../..'),g={};vm.createContext(g);for(const n of ['Ficha','Pessoal','Salarios','R53Cartoes1'])vm.runInContext(fs.readFileSync(path.join(root,'apps-script/'+n+'.gs'),'utf8'),g);
const original=new Map(g.ABAS.map(x=>[x.nome,new Map(x.vals.map(v=>[v[0]+','+v[1],v[2]]))]));
for(const x of g.VALORES_CUSTOM_)for(const [r,c,v]of x.vals)original.get(x.nome)?.set(r+','+c,v);
original.get('FICHA PESSOAL').set('86,23',g.SALARIO_.f.total);
const letra=n=>{let s='';while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;};
const valor=(s,a)=>{const p=a1(a);return original.get(s).get(p[0]+','+p[1])??'';};
const nota=(s,a)=>g.ABAS.find(x=>x.nome===s).notas?.find(x=>x[0]===a)?.[1]||'';
const sources=['contrato_formacao','formacao'].map(n=>fs.readFileSync(path.join(root,'r53/inicializacao/'+n+'.gs'),'utf8'));
const nomes=['grau_origem','pericias','oficios_tr','armas','tecnica','familias','equipados','equipaveis','itens','carteira'];
let casos=0;function caso(n,f){try{f();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
function visitar(x,fn){const [r,c,r2,c2]=a1(x.faixa);for(let rr=r;rr<=r2;rr++)for(let cc=c;cc<=c2;cc++)fn(letra(cc)+rr,rr-r,cc-c);}
function preparado(nome){const a=ambiente();for(const f of sources)vm.runInContext(f,a.ctx);a.sheets['FICHA AMALDIÇOADA']={getRange:addr=>a.range('FICHA AMALDIÇOADA',addr)};a.nome=nome;a.c=a.ctx.R53_NOVA_FORMACAO_CONTRATO_.dominios[nome];
 for(const x of a.c.guardas)visitar(x,addr=>{const v=valor(x.aba,addr);a.put(x.aba,addr,typeof v==='string'&&v.startsWith('=')?123:v,typeof v==='string'&&v.startsWith('=')?v:'','INSTRUÇÃO NO RÓTULO');});
 for(const x of a.c.entradas)visitar(x,addr=>a.put(x.aba,addr,x.tipo==='bool'?true:x.tipo==='bonus'?44:'TEXTO PRIVADO ANTIGO','','NOTA PRIVADA ANTIGA'));
 a.put('CONFIGURAÇÃO','AK51','REGRA CUSTOM DA MESA');a.put('CONFIGURAÇÃO','F46',10);a.put('FICHA','AH11',30);a.put('DADOS','CZ54',3700);a.put('FICHA PESSOAL','Q27','HISTÓRIA PRESERVADA');a.put('FICHA PESSOAL','D92','INVENTÁRIO PRESERVADO');
 // O espelho antigo B47 é derivado, não entrada a apagar.
 {const v=valor('FICHA','N439');a.put('FICHA','N439',1,typeof v==='string'&&v.startsWith('=')?v:'');}
 a.previa=()=>a.ctx.r53NovaPerfilPrevia_(a.ss,a.context,a.ctx.r53NovaFormPerfil_(nome));a.aplicar=p=>a.ctx.r53NovaPerfilAplicar_(a.ss,a.context,p.assinatura,a.ctx.r53NovaFormPerfil_(nome));
 a.concluir=p=>{for(let i=0;i<40;i++){const r=a.aplicar(p);if(r.concluido)return r;assert.equal(r.retomar,true);}throw Error('retomadas demais');};return a;
}
function conferir(a){for(const x of a.c.entradas)visitar(x,addr=>{const r=a.range(x.aba,addr),v=valor(x.aba,addr);if(x.tipo==='formula')assert.equal(r.getFormulas()[0][0],v);else{assert.equal(r.getValue(),v);assert.equal(r.getFormulas()[0][0],'');}assert.equal(r.getNotes()[0][0],nota(x.aba,addr));});
 for(const x of a.c.guardas)visitar(x,addr=>{const v=valor(x.aba,addr),r=a.range(x.aba,addr);if(typeof v==='string'&&v.startsWith('='))assert.equal(r.getFormulas()[0][0],v);else assert.equal(r.getValue(),v);assert.equal(r.getNotes()[0][0],(a.c.somenteNotas||[]).some(x=>x.aba==='FICHA PESSOAL'&&x.faixa===addr)?nota(x.aba,addr):'INSTRUÇÃO NO RÓTULO');});
 assert.equal(a.range('CONFIGURAÇÃO','AK51').getValue(),'REGRA CUSTOM DA MESA');assert.equal(a.range('CONFIGURAÇÃO','F46').getValue(),10);assert.equal(a.range('FICHA','AH11').getValue(),30);assert.equal(a.range('DADOS','CZ54').getValue(),3700);
 assert.equal(a.range('FICHA PESSOAL','Q27').getValue(),'HISTÓRIA PRESERVADA');if(a.nome!=='equipaveis')assert.equal(a.range('FICHA PESSOAL','D92').getValue(),'INVENTÁRIO PRESERVADO');assert.equal(a.range('FICHA','N439').getFormulas()[0][0],String(valor('FICHA','N439')).startsWith('=')?valor('FICHA','N439'):'');assert.equal(a.range('EXTRATO','A2').getValue(),'SEGREDO financeiro');
 assert.equal(a.doc.get('r53_recuperacao_personagem'),'recuperação fora deste domínio');
 for(const c of a.cells.values()){assert.equal(c.fmt,'tema');assert.equal(c.dv,'menu');}
 const raw=a.doc.get(a.ctx.r53NovaFormPerfil_(a.nome).diario);assert(Buffer.byteLength(raw)<9000);assert(!raw.includes('PRIVADO'));assert(!raw.includes('NOTA PRIVADA'));assert.equal(JSON.parse(raw).concluido,true);assert(!a.locked());
}
caso('contrato e fontes independentes concordam sem regeneração',()=>{
 execFileSync(process.execPath,['r53/inicializacao/gerar_contrato_formacao.js','--conferir'],{cwd:root});
 const quant={grau_origem:10,pericias:99,oficios_tr:94,armas:65,tecnica:11,familias:19,equipados:5,equipaveis:88,itens:36,carteira:3};
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
caso('normalização do Google após gravar matriz não quebra a pós-condição',()=>{const {variantes}=require('../inicializacao/gerar_contrato_formacao');for(const nome of ['grau_origem','oficios_tr','familias','equipaveis','itens']){const a=preparado(nome);a.hook((f,t)=>{if(f==='depois'&&t==='valores')for(const x of a.c.entradas)if(x.tipo==='formula')visitar(x,(addr,i,j)=>{if(a.range(x.aba,addr).getFormulas()[0][0])a.put(x.aba,addr,999,variantes(x.valores[i][j]).at(-1),a.range(x.aba,addr).getNotes()[0][0]);});});a.concluir(a.previa());for(const x of a.c.entradas)if(x.tipo==='formula')visitar(x,(addr,i,j)=>assert(variantes(x.valores[i][j]).includes(a.range(x.aba,addr).getFormulas()[0][0])));}});
caso('guarda nativa aceita só fórmulas equivalentes sem mudar conta',()=>{const {variantes}=require('../inicializacao/gerar_contrato_formacao');for(const nome of nomes){const a=preparado(nome);for(const x of a.c.guardas)visitar(x,addr=>{const v=valor(x.aba,addr);if(typeof v==='string'&&v.startsWith('='))a.put(x.aba,addr,999,variantes(v).at(-1));});a.concluir(a.previa());}const b=preparado('grau_origem');b.put('FICHA PESSOAL','D51',1,'=1');assert.throws(()=>b.previa(),/protegida/);});
caso('contrato e domínio inexistentes não criam escrita',()=>{const a=preparado('armas');assert.throws(()=>a.ctx.r53NovaFormContrato_('constructor'),/contrato/);a.ctx.R53_NOVA_FORMACAO_CONTRATO_=undefined;assert.throws(()=>a.previa(),/contrato/);assert.equal(a.writes.length,0);});
caso('saldo protegido usa o preparador salarial, não a antiga apresentação mensal',()=>{
 const a=preparado('grau_origem'),antiga=g.VALORES_CUSTOM_.find(x=>x.nome==='FICHA PESSOAL').vals.find(x=>x[0]===86&&x[1]===23)[2];
 assert.notEqual(antiga,g.SALARIO_.f.total);a.put('FICHA PESSOAL','W86',150000,antiga);
 assert.throws(()=>a.previa(),/protegida/);assert.equal(a.writes.length,0);
});
caso('técnica limpa textos e escolhas sem apagar nome, atributo e contas derivados',()=>{
 const a=preparado('tecnica');a.put('CARTEIRA','O27','Técnica declarada preservada');
 a.put('MONTAGENS','B3','cartão antigo fora deste domínio');a.doc.set('r53_amparo_direto','estado antigo fora deste domínio');
 const p=a.ctx.r53NovaFichaTecnicaPrevia(a.ss,a.context);a.concluir(p);conferir(a);
 assert.equal(a.range('CARTEIRA','O27').getValue(),'Técnica declarada preservada');
 assert.equal(a.range('MONTAGENS','B3').getValue(),'cartão antigo fora deste domínio');
 assert.equal(a.doc.get('r53_amparo_direto'),'estado antigo fora deste domínio');
 for(const addr of ['J12','J16','D18','J18','P18','D22','D26','L26','L29','D33','P33'])assert.equal(a.range('FICHA AMALDIÇOADA',addr).getValue(),'');
});
caso('Famílias do livro neutras e custom calculadas sem apagar definições',()=>{
 const a=preparado('familias');a.put('CONFIGURAÇÃO','B2','Família da mesa');
 a.put('DADOS_CRIACAO','B2','Família da mesa');a.put('FICHA AMALDIÇOADA','H37','INTERIOR PRESERVADO');
 a.put('INVOCAÇÕES','D12','Entidade fora deste domínio');
 a.concluir(a.ctx.r53NovaFichaFamiliasPrevia(a.ss,a.context));conferir(a);
 for(const c of ['D','E','F','G','J','K','L','M','P'])assert.equal(a.range('FICHA AMALDIÇOADA',c+'37').getValue(),'Neutra');
 for(let r=41;r<=50;r++)assert.equal(a.range('FICHA AMALDIÇOADA','O'+r).getFormulas()[0][0],valor('FICHA AMALDIÇOADA','O'+r));
 assert.equal(a.range('DADOS_CRIACAO','B2').getValue(),'Família da mesa');assert.equal(a.range('CONFIGURAÇÃO','B2').getValue(),'Família da mesa');
 assert.equal(a.range('FICHA AMALDIÇOADA','H37').getValue(),'INTERIOR PRESERVADO');assert.equal(a.range('INVOCAÇÕES','D12').getValue(),'Entidade fora deste domínio');
});
for(const [nome,aba,addr]of [['familias','FICHA AMALDIÇOADA','O41'],['grau_origem','FICHA PESSOAL','D45'],['oficios_tr','FICHA','W118']])
 caso('fórmula editável desconhecida recusada '+nome,()=>{const a=preparado(nome);a.put(aba,addr,0,'=0');assert.throws(()=>a.previa(),/fórmula pessoal/);assert.equal(a.writes.length,0);});
caso('diários anteriores de formação têm o mesmo layout com os novos domínios',()=>{
 // Hashes fixos: quatro contratos em 73dffda, técnica/Famílias em a92cba8, inventário em 86410be; funciona em clone raso.
 const hashes={equipados:"f4f68778805c2395c41e5a286434016d9e60f7178475b9a714d3f55fffcbf5a4",equipaveis:"d3046b3753c320114d42d676dde31e529a289f3bb002b52c96537f84749b675e",itens:"61e84811f0fe3b4df3ee144dd76d993e53240b6b2cf7d678e6611da8353e47b4",grau_origem:'1e5bd718e6ad714350a5c78aae912ecc1fb4d2fb00d3356adc53e9641afe7d84',pericias:'e652c80f5155dea891a0d60e064310e64e90c15d95b6fcc010f06516d414386d',oficios_tr:'13a407d5e903f4e73fcfc8715ae45cc27c0ca76666b388b6509a26cd2d210c4a',armas:'b9a3bba86f490261484c7a5fc2707af44ec3c8c64196d9ec48dc9f466672e0f7',tecnica:'81acd6d204c867a909e0f48743d9d93442252ca40ceeb3360d90480ce7fb1579',familias:'ce1a4f3cb54899ebfc1e6293602b7c108a311b95f18531aed4949be50ca3d97c'};
 for(const [nome,hash]of Object.entries(hashes))assert.equal(require('node:crypto').createHash('sha256').update(JSON.stringify(preparado(nome).c)).digest('hex'),hash);
});
caso('equipados restaura Soco, mão livre e Traje 1 sem dar inventário ou dinheiro',()=>{
 const a=preparado('equipados');a.concluir(a.ctx.r53NovaFichaEquipadosPrevia(a.ss,a.context));
 for(const [c,v]of [['D64','Soco'],['S64','—'],['AH64','Traje 1'],['L86',0],['AN86','']])assert.equal(a.range('FICHA PESSOAL',c).getValue(),v);
 assert.equal(a.range('FICHA PESSOAL','O86').getValue(),-500);assert.equal(a.range('FICHA PESSOAL','D92').getValue(),'INVENTÁRIO PRESERVADO');
 assert(a.range('FICHA PESSOAL','D64').getNotes()[0][0].includes('EQUIPÁVEIS GUARDADOS'));
 const readOnly=['D66','S66','D86','AF86'];
 for(const c of readOnly){assert.equal(a.range('FICHA PESSOAL',c).getFormulas()[0][0],valor('FICHA PESSOAL',c));assert.equal(a.range('FICHA PESSOAL',c).getNotes()[0][0],'');}
 assert(!a.writes.some(([t,d])=>t==='valores'&&readOnly.some(c=>d==='FICHA PESSOAL!'+c)));
});
caso('nota viva concorrente após queda não é apagada pela retomada',()=>{
 const a=preparado('equipados'),p=a.previa();
 a.hook((fase,t,d)=>{if(fase==='depois'&&t==='notasMatriz'&&d==='FICHA PESSOAL!D66')throw Error('queda na nota');});
 assert.throws(()=>a.concluir(p),/queda na nota/);a.hook(null);
 a.put('FICHA PESSOAL','S66',123,valor('FICHA PESSOAL','S66'),'AVISO ALTERADO DEPOIS');const n=a.writes.length;
 assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);assert.equal(a.range('FICHA PESSOAL','S66').getNotes()[0][0],'AVISO ALTERADO DEPOIS');
});
caso('equipáveis livres perdem dados pessoais mas recuperam fórmulas e instruções',()=>{
 const a=preparado('equipaveis');a.put('CONFIGURAÇÃO','D200','catálogo mantido');a.put('DADOS_CUSTOM','AA2','Arma custom mantida');
 a.put('INVOCAÇÕES','D92','equipamento de entidade fora deste domínio');a.put('FICHA PESSOAL','E98','interior da mescla');
 for(const r of [98,99])for(const c of ['D','K','M','S','U','W','AE','AG','AI','AK','AQ'])a.put('FICHA PESSOAL',c+r,'PERSONAGEM ANTERIOR','','NOTA ANTERIOR');
 a.concluir(a.ctx.r53NovaFichaEquipaveisPrevia(a.ss,a.context));conferir(a);
 for(const r of [98,99]){assert.equal(a.range('FICHA PESSOAL','D'+r).getValue(),'');assert(a.range('FICHA PESSOAL','D'+r).getNotes()[0][0].startsWith('Linha livre:'));assert(a.range('FICHA PESSOAL','AG'+r).getFormulas()[0][0].includes('$K'+r));}
 assert.equal(a.range('FICHA PESSOAL','E98').getValue(),'interior da mescla');assert.equal(a.range('DADOS_CUSTOM','AA2').getValue(),'Arma custom mantida');assert.equal(a.range('CONFIGURAÇÃO','D200').getValue(),'catálogo mantido');assert.equal(a.range('INVOCAÇÕES','D92').getValue(),'equipamento de entidade fora deste domínio');
});
caso('itens limpam os dois lados e restauram Volume sobrescrito sem herdar números',()=>{
 const a=preparado('itens');for(const c of ['V104','AR109'])a.put('FICHA PESSOAL',c,999,'','volume autorizado anterior');
 a.put('DADOS_CUSTOM','AU2','Item custom mantido');a.concluir(a.ctx.r53NovaFichaItensPrevia(a.ss,a.context));conferir(a);
 for(let r=104;r<=109;r++){for(const c of ['D','T','Z','AP'])assert.equal(a.range('FICHA PESSOAL',c+r).getValue(),'');for(const c of ['V','AR'])assert.equal(a.range('FICHA PESSOAL',c+r).getFormulas()[0][0],valor('FICHA PESSOAL',c+r));}
 assert.equal(a.range('DADOS_CUSTOM','AU2').getValue(),'Item custom mantido');
});
for(const [dom,c] of [['equipaveis','AG98'],['equipaveis','AK92'],['itens','AR109']])caso('inventário recusa fórmula personalizada sem sobrescrever '+c,()=>{
 const a=preparado(dom);a.put('FICHA PESSOAL',c,42,'=42');assert.throws(()=>a.previa(),/fórmula pessoal/);assert.equal(a.writes.length,0);
});
caso('contrato de inventário coincide com montagem pública completa, não só recorte do gerador',()=>{
 const full={};vm.createContext(full);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),full);
 const sheet=full.ABAS.find(x=>x.nome==='FICHA PESSOAL'),cells=new Map(sheet.vals.map(x=>[x[0]+','+x[1],x[2]]));
 for(const nome of ['equipados','equipaveis','itens']){const a=preparado(nome);for(const x of a.c.entradas)visitar(x,(addr,i,j)=>{const p=a1(addr);assert.equal(x.valores[i][j],cells.get(p[0]+','+p[1])??'');assert.equal(x.notas[i][j],sheet.notas.find(n=>n[0]===addr)?.[1]||'');});}
});
caso('Volume aceita decimal nativo 0,1 somente na fórmula inteira conhecida',()=>{
 const a=preparado('itens');
 const native='=IF($D104="";"";IF($T104="";1;$T104)*IFERROR(VLOOKUP($D104;DADOS_CUSTOM!$AU$2:$AX$64;2;FALSE);0,1))';
 a.put('FICHA PESSOAL','V104',0,native);const p=a.previa();a.concluir(p);conferir(a);
 for(const f of [native.replace('0,1','0,2'),native.replace('$T104','$T105'),native.replace('$AX$64','$AX$65')]){
  const b=preparado('itens');b.put('FICHA PESSOAL','V104',0,f);assert.throws(()=>b.previa(),/fórmula pessoal/);assert.equal(b.writes.length,0);
 }
});
caso('Volume localizado depois da escrita mantém a retomada e pós-condição',()=>{
 const a=preparado('itens'),{variantesVolume}=require('../inicializacao/gerar_contrato_formacao');
 a.hook((fase,t)=>{if(fase==='depois'&&t==='valores')for(const x of a.c.entradas)if(x.tipo==='formula')visitar(x,(addr,i,j)=>{
  if(a.range(x.aba,addr).getFormulas()[0][0])a.put(x.aba,addr,0,variantesVolume(x.valores[i][j]).at(-1),a.range(x.aba,addr).getNotes()[0][0]);
 });});
 const p=a.previa();a.concluir(p);const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);
 for(const x of a.c.entradas)if(x.tipo==='formula')visitar(x,addr=>assert(a.range(x.aba,addr).getFormulas()[0][0].endsWith(';0,1))')));
});
caso('CARTEIRA limpa só complemento, técnica declarada e resumo, preservando servidor e identidade',()=>{
 const a=preparado('carteira');
 for(const [c,v] of [['Z22','Mesa custom'],['O9','Nome tratado em outro domínio'],['AK22','Jogador'],['C8','FOTO\n顔']])a.put('CARTEIRA',c,v,'','nota preservada');
 a.concluir(a.ctx.r53NovaFichaCarteiraPrevia(a.ss,a.context));conferir(a);
 for(const c of ['O13','O27','O30']){assert.equal(a.range('CARTEIRA',c).getValue(),'');assert.equal(a.range('CARTEIRA',c).getNotes()[0][0],'');}
 assert.equal(a.range('CARTEIRA','Z22').getValue(),'Mesa custom');assert.equal(a.range('CARTEIRA','O9').getValue(),'Nome tratado em outro domínio');assert.equal(a.range('CARTEIRA','AK22').getValue(),'Jogador');
 assert.equal(a.range('CARTEIRA','C8').getValue(),'FOTO\n顔');assert.equal(a.range('CARTEIRA','AT3').getValue(),true);
 const full={};vm.createContext(full);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),full);
 const sheet=full.ABAS.find(x=>x.nome==='CARTEIRA');
 for(const x of a.c.entradas)visitar(x,(addr,i,j)=>{const p=a1(addr);assert.equal(x.valores[i][j],sheet.vals.find(v=>v[0]===p[0]&&v[1]===p[1])[2]);});
 const am=full.ABAS.find(x=>x.nome==='DADOS_AM');
 assert(am.vals.some(x=>typeof x[2]==='string'&&x[2].includes('CARTEIRA!$O$27')),'O27 é o nome realmente consumido');
});
console.log(`${casos} cenários offline de Grau/Origem/treinos/técnica/Famílias/inventário/CARTEIRA aprovados; sem aceite nativo ou criação geral.`);
