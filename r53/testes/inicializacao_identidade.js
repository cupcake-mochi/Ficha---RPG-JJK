'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const {ambiente,a1}=require('./apoio_inicializacao');
const raiz=path.resolve(__dirname,'../..'), g={};vm.createContext(g);
for(const nome of ['Ficha','Pessoal'])vm.runInContext(fs.readFileSync(path.join(raiz,'apps-script/'+nome+'.gs'),'utf8'),g);
const fonte=fs.readFileSync(path.join(raiz,'r53/inicializacao/identidade.gs'),'utf8');
let casos=0;function caso(nome,fn){try{fn();casos++;}catch(e){e.message=nome+': '+e.message;throw e;}}
function preparado(){
 const a=ambiente();vm.runInContext(fonte,a.ctx);
 const aba=n=>(n==='FICHA PESSOAL'?g.VALORES_CUSTOM_:g.ABAS).find(s=>s.nome===n);
 const value=(n,addr)=>{const [r,c]=a1(addr);return aba(n).vals.find(x=>x[0]===r&&x[1]===c)?.[2];};
 for(const x of a.ctx.R53_NOVA_IDENT_.campos){a.put(x[0],x[2],value(x[0],x[2]));a.put(x[0],x[1],'PESSOA ANTIGA '+x[1],'','NOTA PRIVADA '+x[1]);}
 for(const [s,addr]of [['FICHA','AB2'],['FICHA PESSOAL','Q11'],['FICHA PESSOAL','D10']])a.put(s,addr,'',value(s,addr));
 a.put('CARTEIRA','C8',value('CARTEIRA','C8'));a.put('CARTEIRA','Z22','SERVIDOR DA MESA');
 a.put('CONFIGURAÇÃO','AK51','CATÁLOGO DA MESA');a.put('FICHA PESSOAL','Q22',value('FICHA PESSOAL','Q22'),'','INSTRUÇÃO DO CABEÇALHO');
 a.previa=()=>a.ctx.r53NovaFichaIdentidadePrevia(a.ss,a.context);
 a.aplicar=p=>a.ctx.r53NovaFichaIdentidadeAplicar(a.ss,a.context,p.assinatura);
 a.concluir=p=>{for(let i=0;i<20;i++){const r=a.aplicar(p);if(r.concluido)return r;assert.equal(r.retomar,true);}throw Error('retomadas excedidas');};
 a.fabricados=aba;return a;
}
function verificar(a){
 for(const [i,x]of a.ctx.R53_NOVA_IDENT_.campos.entries()){
  assert.equal(a.range(x[0],x[1]).getValue(),i===0?a.ctx.R53_NOVA_IDENT_.nome:'');
  assert.equal(a.range(x[0],x[1]).getNotes()[0][0],'');
  assert.equal(a.range(x[0],x[2]).getValue(),x[3]);
 }
 assert.equal(a.range('CARTEIRA','Z22').getValue(),'SERVIDOR DA MESA');
 assert.equal(a.range('CONFIGURAÇÃO','AK51').getValue(),'CATÁLOGO DA MESA');
 assert.equal(a.range('FICHA PESSOAL','Q22').getNotes()[0][0],'INSTRUÇÃO DO CABEÇALHO');
 for(const c of a.cells.values()){assert.equal(c.fmt,'tema');assert.equal(c.dv,'menu');}
 const j=a.doc.get(a.ctx.R53_NOVA_IDENT_.diario);assert(!j.includes('PESSOA ANTIGA'));assert(!j.includes('NOTA PRIVADA'));assert(Buffer.byteLength(j)<9000);
 assert.equal(JSON.parse(j).concluido,true);assert(!a.locked());
}
caso('entradas e cabeçalhos existem no produtor e não têm nota de fábrica',()=>{
 const a=preparado();assert.equal(a.ctx.R53_NOVA_IDENT_.campos.length,14);
 for(const x of a.ctx.R53_NOVA_IDENT_.campos){const [r,c]=a1(x[1]);assert(a.fabricados(x[0]).vals.some(v=>v[0]===r&&v[1]===c));assert.equal(Object.fromEntries(a.fabricados(x[0]).notas||[])[x[1]]||'','');}
});
caso('limpa somente textos e notas de entrada',()=>{const a=preparado(),p=a.previa();assert.equal(a.writes.length,0);const r=a.concluir(p);assert.equal(r.criacaoDisponivel,false);assert(r.pendente.includes('fotos_e_imagens_sobrepostas'));verificar(a);const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);});
caso('perfil de identidade não limpa o financeiro ou inventário',()=>{const a=preparado();a.concluir(a.previa());assert.equal(a.range('EXTRATO','A2').getValue(),'SEGREDO financeiro');assert.equal(a.range('FICHA PESSOAL','D92').getValue(),'inventário antigo fora deste domínio');});
for(const k of [['CARTEIRA','O8'],['FICHA PESSOAL','Q26'],['FICHA PESSOAL','D30']])caso('rótulo incompatível '+k.join('!'),()=>{const a=preparado();a.put(...k,'mudou');assert.throws(()=>a.previa(),/layout/);assert.equal(a.writes.length,0);});
for(const [s,addr]of [['CARTEIRA','O9'],['FICHA PESSOAL','Q27']])caso('não apaga fórmula pessoal desconhecida '+addr,()=>{const a=preparado();a.put(s,addr,10,'=10');assert.throws(()=>a.previa(),/fórmula inesperada/);assert.equal(a.writes.length,0);});
for(const [s,addr]of [['FICHA','AB2'],['FICHA PESSOAL','Q11'],['FICHA PESSOAL','D10']])caso('espelho alterado '+addr,()=>{const a=preparado();a.put(s,addr,0,'=0');assert.throws(()=>a.previa(),/espelho/);assert.equal(a.writes.length,0);});
caso('CellImage é recusada antes de limpar textos',()=>{const a=preparado();a.put('CARTEIRA','C8',{valueType:'IMAGE'});assert.throws(()=>a.previa(),/imagem ou valor/);assert.equal(a.writes.length,0);});
caso('IMAGE por fórmula não é confundida com foto vazia',()=>{const a=preparado();a.put('CARTEIRA','C8','', '=IMAGE("https://example.invalid/foto.png")');assert.throws(()=>a.previa(),/foto pessoal/);assert.equal(a.writes.length,0);});
caso('foto preenchida como texto também exige revisão',()=>{const a=preparado();a.put('CARTEIRA','C8','outra foto');assert.throws(()=>a.previa(),/foto pessoal/);assert.equal(a.writes.length,0);});
caso('prévia não contém história ou notas antigas',()=>{const a=preparado(),p=a.previa();assert(!JSON.stringify(p).includes('PESSOA ANTIGA'));assert(!JSON.stringify(p).includes('NOTA PRIVADA'));});
caso('texto editado depois da prévia não é apagado',()=>{const a=preparado(),p=a.previa();a.put('FICHA PESSOAL','Q27','história nova');assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);});
const base=preparado();base.concluir(base.previa());
for(let i=1;i<=base.writes.length;i++)for(const fase of ['antes','depois'])caso(`retoma queda ${fase} ${i}`,()=>{
 const a=preparado(),p=a.previa();let n=0;a.hook(f=>{if(f===fase&&++n===i)throw Error('queda');});assert.throws(()=>a.concluir(p),/queda/);assert(!a.locked());a.hook(null);a.concluir(p);verificar(a);
});
caso('nota editada após queda não é sobrescrita',()=>{const a=preparado(),p=a.previa();a.hook((f,k)=>{if(f==='depois'&&k==='valor')throw Error('queda');});assert.throws(()=>a.aplicar(p),/queda/);a.hook(null);a.put('CARTEIRA','O9',a.ctx.R53_NOVA_IDENT_.nome,'','nota nova');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados/);assert.equal(a.writes.length,n);});
caso('não reinicializa identidade já usada',()=>{const a=preparado(),p=a.previa();a.concluir(p);a.put('CARTEIRA','O9','novo nome');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados|já foi usada/);assert.equal(a.writes.length,n);});
console.log(`${casos} cenários offline de textos pessoais aprovados; imagens/arte e inicialização geral pendentes.`);
