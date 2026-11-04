'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict'),{execFileSync}=require('child_process');
const {ambiente,a1}=require('./apoio_inicializacao'),{contrato}=require('../inicializacao/gerar_contrato_arte');
const root=path.resolve(__dirname,'../..'),scripts=['validacoes','formacao','contrato_arte','arte'].map(n=>new vm.Script(fs.readFileSync(path.join(root,'r53/inicializacao/'+n+'.gs'),'utf8')));
let casos=0;function caso(nome,fn){try{fn();casos++;}catch(e){e.message=nome+': '+e.message;throw e;}}
function imagem(url='https://google.example.invalid/CONTEUDO-PRIVADO',titulo='FOTO PRIVADA',desc='DESCRIÇÃO PRIVADA'){
 return {valueType:'IMAGE',getContentUrl:()=>url,getAltTextTitle:()=>titulo,getAltTextDescription:()=>desc};
}
function preparado(op={}){
 const a=ambiente(op);for(const s of scripts)s.runInContext(a.ctx);a.ctx.SpreadsheetApp.ValueType={IMAGE:'IMAGE'};a.imagens=[];a.desenhos=[];
 for(const x of contrato.campos){if(!a.sheets[x.aba])a.sheets[x.aba]={getRange:addr=>a.range(x.aba,addr)};a.put(x.aba,x.guarda.faixa,x.guarda.valor);
 a.put(x.aba,x.faixa,imagem(),'','NOTA PRIVADA');const [r,c]=a1(x.faixa);a.cells.set(x.aba+'!'+r+','+c,{...a.get(x.aba,r,c),dv:null});}
 for(const x of contrato.decoracoes)if(!a.sheets[x.aba])a.sheets[x.aba]={getRange:addr=>a.range(x.aba,addr)};
 for(const [name,sh]of Object.entries(a.sheets)){
  const base=sh.getRange;sh.getRange=addr=>{const x=contrato.campos.find(x=>x.aba===name&&x.faixa===addr);return {...base(addr),getMergedRanges:()=> (x?.mesclas||[]).map(m=>({getRow:()=>m[0],getColumn:()=>m[1],getLastRow:()=>m[2],getLastColumn:()=>m[3]}))};};
  sh.getName=()=>name;sh.getImages=()=>a.imagens;sh.getDrawings=()=>a.desenhos;
 }
 a.ss.getSheets=()=>Object.values(a.sheets);
 for(const x of contrato.decoracoes)a.put(x.aba,x.faixa,imagem('https://google.example.invalid/ARTE','PM-ARTE:'+x.arquivo,'fabrica'));
 a.put('CONFIGURAÇÃO','AK51','CATÁLOGO CUSTOM');a.put('MONTAGENS','B7','CARTÃO PRESERVADO');a.doc.set('r53_versoes','CACHE PERSISTENTE');
 a.antes={cells:new Map(a.cells),doc:new Map(a.doc),script:new Map(a.script)};
 a.previa=()=>a.ctx.r53NovaFichaFotosPrevia(a.ss,a.context);
 a.aplicar=p=>a.ctx.r53NovaFichaFotosAplicar(a.ss,a.context,p.assinatura);
 a.concluir=p=>{for(let i=0;i<20;i++){const r=a.aplicar(p);assert.equal(r.criacaoDisponivel,false);if(r.concluido)return r;assert(r.retomar);}throw Error('retomadas demais');};return a;
}
function conferir(a){const alvos=new Set();for(const x of contrato.campos){const r=a.range(x.aba,x.faixa),[row,col]=a1(x.faixa);alvos.add(x.aba+'!'+row+','+col);
 assert.equal(r.getFormulas()[0][0],x.formulaDestino||'');if(!x.formulaDestino)assert.equal(r.getValue(),x.valor);assert.equal(r.getNotes()[0][0],x.nota);
 const cell=a.get(x.aba,row,col);assert.equal(cell.fmt,'tema');assert.equal(cell.dv,null);
 }for(const [k,v]of a.antes.cells)if(!alvos.has(k))assert.deepEqual(a.cells.get(k),v,k);
 for(const [k,v]of a.antes.doc)assert.equal(a.doc.get(k),v);assert.deepEqual(a.script,a.antes.script);assert(!a.locked());
 const j=a.doc.get(a.ctx.r53NovaArtePerfil_().diario);assert.equal(JSON.parse(j).recibo,1);assert(!/PRIVAD|google\.example|https:/.test(j));return j;
}
caso('contrato reproduzível: 13 fotos, um espelho e dez decorações fora dos alvos',()=>{
 execFileSync(process.execPath,['r53/inicializacao/gerar_contrato_arte.js','--conferir'],{cwd:root});assert.equal(contrato.campos.length,14);assert.equal(contrato.decoracoes.length,10);
 const alvos=new Set(contrato.campos.map(x=>x.aba+'!'+x.faixa));for(const d of contrato.decoracoes)assert(!alvos.has(d.aba+'!'+d.faixa));
 assert.equal(contrato.campos.at(-2).faixa,'AB1170');
});
caso('limpa fotos em célula e notas, restaura espelho, preserva decoração/catálogos',()=>{const a=preparado(),p=a.previa();assert.equal(a.writes.length,0);assert(!/PRIVAD|https:/.test(JSON.stringify(p)));a.concluir(p);conferir(a);const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);});
caso('quatro escritas por chamada, diário sem URL/alt/texto privado e sem liberar criação',()=>{const a=preparado(),p=a.previa(),r=a.aplicar(p);assert(!r.concluido&&r.retomar);assert.equal(a.writes.filter(([k])=>k!=='propriedade').length,4);const j=a.doc.get(a.ctx.r53NovaArtePerfil_().diario);assert(!/PRIVAD|https:/.test(j));assert(Buffer.byteLength(j)<9000);a.concluir(p);conferir(a);});
const base=preparado();base.concluir(base.previa());
for(let k=1;k<=base.writes.length;k++)for(const fase of ['antes','depois'])caso('queda '+fase+' '+k,()=>{const a=preparado(),p=a.previa();let n=0;a.hook(f=>{if(f===fase&&++n===k)throw Error('queda');});assert.throws(()=>a.concluir(p),/queda/);assert(!a.locked());a.hook(null);a.concluir(p);conferir(a);});
for(const x of contrato.campos)for(const valor of ['', 'https://example.invalid/foto-pessoal', 'legenda antiga'])caso(x.aba+'!'+x.faixa+' texto/URL vira padrão '+valor,()=>{const a=preparado();a.put(x.aba,x.faixa,valor,'','NOTA PRIVADA');a.concluir(a.previa());conferir(a);});
for(const f of ['=IMAGE("https://example.invalid/PESSOAL")','=image(A1;4;120;240)','=IMAGE(IF(A1="a";B2;B3))'])caso('fórmula de imagem é removida sem buscar URL '+f,()=>{const a=preparado();a.put('CARTEIRA','C8',imagem(),f);a.concluir(a.previa());conferir(a);});
for(const f of ['=1','=CARTEIRA!A1','=IMAGE("x")+SUM(A1)','=IMAGE("x")+1','=IMAGE("x"','=IMAGE("x") '])caso('fórmula desconhecida recusa '+f,()=>{const a=preparado();a.put('CARTEIRA','C8',1,f);assert.throws(()=>a.previa(),/fórmula de foto/);assert.equal(a.writes.length,0);});
caso('espelho já correto também perde nota pessoal sem trocar sua fórmula',()=>{const a=preparado();a.put('FICHA PESSOAL','D10',imagem(),'=CARTEIRA!$C$8','NOTA PRIVADA');a.concluir(a.previa());conferir(a);});
for(const value of [7,true,{valueType:'IMAGE'},imagem(''),imagem('http://example.invalid'),{...imagem(),getContentUrl:()=>{throw Error('https://SEGREDO');}}])caso('imagem/valor desconhecido não é apagado '+String(value),()=>{const a=preparado();a.put('CARTEIRA','C8',value);let err;try{a.previa();}catch(e){err=e;}assert(err);assert(!err.message.includes('https://SEGREDO'));assert.equal(a.writes.length,0);});
caso('URL de conteúdo mudou após prévia: recusa sem limpar',()=>{const a=preparado(),p=a.previa();a.put('CARTEIRA','C8',imagem('https://google.example.invalid/OUTRA'));const n=a.writes.length;assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,n);});
caso('URLs diferentes em cada leitura falham antes de escrever',()=>{const a=preparado();let n=0;a.put('CARTEIRA','C8',{...imagem(),getContentUrl:()=> 'https://google.example.invalid/'+ ++n});const p=a.previa();assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);});
caso('URL expirou antes de escrever uma foto pendente: revisão, sem nova limpeza',()=>{const a=preparado(),p=a.previa();a.aplicar(p);a.put('INVOCAÇÕES','I246',imagem('https://google.example.invalid/EXPIRADA'));const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);});
caso('após a foto já ter sido limpa, a retomada independe da URL antiga',()=>{const a=preparado(),p=a.previa();a.aplicar(p);const before=a.get('CARTEIRA',8,3);assert.equal(before.v,'FOTO\n顔');a.concluir(p);conferir(a);});
caso('imagem nova com mesmo alt text é detectada pelo conteúdo identificado',()=>{const a=preparado(),p=a.previa();a.put('CARTEIRA','C8',imagem('https://google.example.invalid/NOVO-MESMO-ALT'));assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);});
for(const field of ['imagens','desenhos'])caso(field+' soltos bloqueiam antes de apagar e nunca chamam remove',()=>{const a=preparado();a[field].push({remove:()=>{throw Error('não deve remover');}});assert.throws(()=>a.previa(),/sobreposta|desenho/);assert.equal(a.writes.length,0);});
caso('sobreposição adicionada durante retomada bloqueia mais escritas',()=>{const a=preparado(),p=a.previa();a.aplicar(p);a.imagens.push({});const n=a.writes.length;assert.throws(()=>a.aplicar(p),/sobreposta|desenho/);assert.equal(a.writes.length,n);});
caso('mudança no conjunto de abas invalida retomada',()=>{const a=preparado(),p=a.previa();a.aplicar(p);a.sheets.extra={getName:()=> 'EXTRA',getImages:()=>[],getDrawings:()=>[]};const n=a.writes.length;assert.throws(()=>a.aplicar(p),/estrutura/);assert.equal(a.writes.length,n);});
caso('foto usada após conclusão não é apagada novamente',()=>{const a=preparado(),p=a.previa();a.concluir(p);a.put('CARTEIRA','C8',imagem());const n=a.writes.length;assert.throws(()=>a.aplicar(p),/já foi usada/);assert.equal(a.writes.length,n);});
caso('nota concorrente não é apagada pela retomada',()=>{const a=preparado(),p=a.previa();a.aplicar(p);a.put('INVOCAÇÕES','I246',imagem(),'','OUTRA NOTA');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);});
caso('mescla fora do contrato, validação extra e rótulo diferente recusam',()=>{
 for(const tipo of ['merge','validation','rotulo']){const a=preparado();if(tipo==='merge'){const old=a.sheets.CARTEIRA.getRange;a.sheets.CARTEIRA.getRange=addr=>({...old(addr),getMergedRanges:()=>[]});}
 if(tipo==='validation'){const c=a.get('CARTEIRA',8,3);a.cells.set('CARTEIRA!8,3',{...c,dv:{tipo:'CHECKBOX',argumentos:[],permiteInvalido:true}});}
 if(tipo==='rotulo')a.put('CARTEIRA','O8','OUTRO');assert.throws(()=>a.previa(),/mescla|validação|layout/);assert.equal(a.writes.length,0);}
});
for(const op of [{id:'1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k'},{ativoDiferente:true},{ocupado:true}])caso('alvo/trava inválidos '+JSON.stringify(op),()=>{const a=preparado(op);assert.throws(()=>a.concluir(a.previa()),/alvo|vinculado|andamento/);assert.equal(a.writes.length,0);});
caso('objetos pessoais fora das caixas ficam explícitos como pendência, não certificado de limpeza global',()=>{const a=preparado();a.put('CARTEIRA','AR45',imagem());const r=a.concluir(a.previa());assert(r.pendente.includes('imagens_fora_das_ancoras'));assert.equal(a.get('CARTEIRA',45,44).v.valueType,'IMAGE');conferir(a);});
console.log(`${casos} cenários offline de fotos em âncoras aprovados; 13 fotos + espelho, dez decorações preservadas. URLs temporárias, arte fora das âncoras e prova nativa continuam limitações.`);
