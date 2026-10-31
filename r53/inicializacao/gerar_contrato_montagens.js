'use strict';
// Contrato extraído somente das fontes públicas. Nenhum endereço vem do jogador.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const {fontes}=require('../../medidas/carregar-ficha');
const {separadores}=require('./gerar_contrato_pessoal');
const root=path.resolve(__dirname,'../..'),g={};vm.createContext(g);vm.runInContext(fontes(),g);
const e=g.R53_EDITOR_,s=g.ABAS.find(x=>x.nome===e.storage);
const digest=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const letra=n=>{let t='';while(n){n--;t=String.fromCharCode(65+n%26)+t;n=Math.floor(n/26);}return t;};
function variantes(f){
 const quoted=x=>x.replace(/"(?:[^"]|"")*"|[^"]+/g,t=>t[0]==='"'?t:t.replace(/'(DADOS_AM|DADOS_INVOC)'!/g,'$1!'));
 return [...new Set([f,separadores(f),quoted(f),quoted(separadores(f))])];
}
if(e.storage!=='MONTAGENS'||e.esquema!==3||!s||e.campos.length!==33||e.contextos.length!==249)throw Error('revisar esquema do editor');
if(s.dv.length)throw Error('MONTAGENS ganhou validações; revisar antes de inicializar');
const cells=new Map(s.vals.map(x=>[x[0]+','+x[1],x[2]])),notes=new Map(s.notas||[]),usados=new Set();
const value=(r,c)=>cells.get(r+','+c)??'';
const guard=v=>typeof v==='string'&&v.startsWith('=')?{formulas:variantes(v).map(digest)}:{valor:v};
const assinatura=ed=>[ed.esquema,ed.storage,ed.campos,Object.keys(ed.defaults).sort().map(k=>[k,ed.defaults[k]]),ed.contextos.map(c=>[c.id,c.aba,c.cel.nome,c.editor,c.classes])];
const contrato={versao:1,editorHash:digest(assinatura(e)),campos:e.campos,defaults:e.defaults,contextos:{}};
for(const c of e.contextos){
 if(!/^[-a-z0-9.]+$/.test(c.id)||Object.hasOwn(contrato.contextos,c.id)||!Number.isInteger(c.editor)||c.editor<5||c.editor+34>s.rows||!c.classes.length||c.classes.length+1>s.cols)throw Error('contexto inválido');
 const faixa='B'+(c.editor+2)+':'+letra(c.classes.length+1)+(c.editor+34);
 for(let r=c.editor;r<=c.editor+34;r++)for(let col=1;col<=c.classes.length+1;col++){
  const key=r+','+col;if(usados.has(key))throw Error('blocos sobrepostos');usados.add(key);
  if(r<c.editor+2||col===1)continue;
  if(s.merges.some(m=>r>=m[0]&&r<=m[2]&&col>=m[1]&&col<=m[3]))throw Error('entrada mesclada');
  if(value(r,col)!==e.defaults[e.campos[r-c.editor-2][0]])throw Error('default divergente em '+key);
  if(notes.has(letra(col)+r))throw Error('nova nota de entrada; revisar contrato');
 }
 if(value(c.editor,1)!=='="'+c.id+' · "&\''+c.aba+'\'!'+c.cel.nome)throw Error('título não corresponde ao cartão');
 if(value(c.editor+1,1)!=='Classe preparada')throw Error('cabeçalho alterado');
 for(let i=0;i<33;i++)if(value(c.editor+2+i,1)!==e.campos[i][1])throw Error('campo fora de ordem');
 c.classes.forEach((cl,j)=>{if(cl!==null&&value(c.editor+1,j+2)!==cl)throw Error('Classe fora de ordem');if(cl===null&&!String(value(c.editor+1,j+2)).startsWith('='))throw Error('Classe máxima deve continuar calculada');});
 contrato.contextos[c.id]={editor:c.editor,classes:c.classes,faixa,
  leitura:'A'+c.editor+':'+letra(c.classes.length+1)+(c.editor+34),
  titulo:guard(value(c.editor,1)),cabecalho:Array.from({length:c.classes.length+1},(_,j)=>guard(value(c.editor+1,j+1)))};
}
const text='/** Versões dos 249 cartões; gerado das fontes públicas, sem dados pessoais. */\nvar R53_NOVA_MONTAGENS_CONTRATO_ = '+JSON.stringify(contrato,null,2)+';\n';
if(require.main===module){const file=path.join(__dirname,'contrato_montagens.gs');if(process.argv.includes('--conferir')){if(fs.readFileSync(file,'utf8')!==text)throw Error('contrato de MONTAGENS desatualizado');console.log('Contrato de MONTAGENS igual às fontes.');}else fs.writeFileSync(file,text);}
module.exports={contrato,variantes,assinatura,letra};
