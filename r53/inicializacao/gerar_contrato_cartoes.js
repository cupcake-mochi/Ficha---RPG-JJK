'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const {fontes}=require('../../medidas/carregar-ficha'),{separadores}=require('./gerar_contrato_pessoal');
const root=path.resolve(__dirname,'../..'),g={};vm.createContext(g);vm.runInContext(fontes(),g);
const e=g.R53_EDITOR_,sheets=new Map(g.ABAS.map(s=>[s.nome,{...s,cells:new Map(s.vals.map(x=>[x[0]+','+x[1],x[2]])),notes:new Map(s.notas||[])}]));
for(const s of g.VALORES_CUSTOM_||[])for(const [r,c,v]of s.vals)sheets.get(s.nome)?.cells.set(r+','+c,v);
const pos=a=>{const m=/^([A-Z]+)(\d+)$/.exec(a);if(!m)throw Error('endereço inválido');return [+m[2],[...m[1]].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0)];};
const letra=n=>{let s='';while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;};
const canon=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canon).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canon(v[k])).join(',')+'}';
const hash=v=>crypto.createHash('sha256').update(canon(v)).digest('hex');
function variantes(f){const aspas=s=>s.replace(/"(?:[^"]|"")*"|[^"]+/g,t=>t[0]==='"'?t:t.replace(/'(DADOS_R53|DADOS_R53_CATALOGO|DADOS_INVOC|DADOS_AM|DADOS_CRIACAO|MONTAGENS)'!/g,'$1!'));return [...new Set([f,separadores(f),aspas(f),aspas(separadores(f))])];}
const guard=v=>typeof v==='string'&&v.startsWith('=')?{formulas:variantes(v).map(hash)}:{valor:v};
const assinatura=ed=>[ed.esquema,ed.amparo,ed.campos,ed.defaults,ed.contextos.map(c=>[c.id,c.aba,c.area_editor])];
const assinaturaCartao=c=>[c.id,c.aba,c.cel,c.classes,c.area_editor,c.entradas_diretas,c.menus_diretos,c.portas,c.funcoes_diretas,c.fixa,c.entidade];
const contrato={versao:1,editorHash:hash(assinatura(e)),contextos:{}};
const occupied=new Set();
for(const c of e.contextos){
 const s=sheets.get(c.aba),[r1,c1,r2,c2]=c.area_editor,ids=new Set(),entradas=[];
 const items=[...['classe','nome','como'].filter(k=>c.cel[k]).map(k=>[k,c.cel[k]]),...Object.entries(c.entradas_diretas)];
 for(const [chave,faixa]of items){
  const [r,col]=pos(faixa),v=s.cells.get(r+','+col)??'',global=c.aba+'!'+faixa;
  if(ids.has(faixa)||occupied.has(global)||r<r1||r>r2||col<c1||col>c2)throw Error('entrada sobreposta/fora '+global);
  if(typeof v==='string'&&v.startsWith('='))throw Error('entrada é fórmula '+global);
  if(s.merges.some(m=>r>=m[0]&&r<=m[2]&&col>=m[1]&&col<=m[3]&&(r!==m[0]||col!==m[1])))throw Error('interior de mescla '+global);
  ids.add(faixa);occupied.add(global);
  const funcao=Object.keys(c.funcoes_diretas).find(k=>c.funcoes_diretas[k]===faixa)||null;
  if(funcao&&(c.fixa?v!==false:v!==0))throw Error('default de função inesperado');
  entradas.push({chave,faixa,valor:v,nota:s.notes.get(faixa)||'',funcao});
 }
 const guardas=[];
 for(const [rc,v]of s.cells){const [r,col]=rc.split(',').map(Number),a=letra(col)+r;if(r>=r1&&r<=r2&&col>=c1&&col<=c2&&!ids.has(a)&&v!=='')guardas.push({faixa:a,...guard(v)});}
 // Amparo consultado sem cache, pela mesma referência estrutural do editor.
 const amp=letra(24+(c.entidade===null||c.entidade===undefined?0:c.entidade+1))+'10';
 if(e.amparo.aba!=='DADOS_R53_CATALOGO'||e.amparo.faixa!=='X10:AJ10')throw Error('referência de Amparo mudou');
 const ampFormula=sheets.get(e.amparo.aba).cells.get(pos(amp).join(','));
 if(typeof ampFormula!=='string'||!ampFormula.startsWith('='))throw Error('Amparo sem fórmula');
 const dinamicas={};
 for(const [key,where]of Object.entries(c.funcoes_diretas)){
  const porta=c.portas[key],ampExpr="'DADOS_R53'!$AS$"+c.linha+'<>"Fechada"',zeroExpr="AND('DADOS_R53'!$C$"+c.linha+'<>0,'+ampExpr+')';if(!['TRUE','FALSE',ampExpr].includes(porta)&&!(c.classes[0]===0&&c.classes.length>1&&porta===zeroExpr))throw Error('porta nova');
  let formula=null;if(!c.fixa){const i=['dano','cura','vt'].indexOf(key)+1;formula='='+c.menus_diretos['pontos'+i].formula;}
  dinamicas[where]={key,porta,formula,variantes:formula?variantes(formula):[]};
 }
 contrato.contextos[c.id]={editorHash:hash(assinaturaCartao(c)),aba:c.aba,leitura:letra(c1)+r1+':'+letra(c2)+r2,entradas,guardas,dinamicas,fixa:c.fixa,
  classe:entradas.find(x=>x.chave==='classe')?.valor??c.classes[0],zeroEspecial:c.classes.length>1&&c.classes[0]===0,
  amparo:{aba:e.amparo.aba,faixa:amp,...guard(ampFormula)}};
}
const text='/** Cartões visíveis: entradas explícitas e guardas das fontes públicas. */\nvar R53_NOVA_CARTOES_CONTRATO_ = '+JSON.stringify(contrato,null,2)+';\n';
if(require.main===module){const file=path.join(__dirname,'contrato_cartoes.gs');if(process.argv.includes('--conferir')){if(fs.readFileSync(file,'utf8')!==text)throw Error('contrato de cartões desatualizado');console.log('Contrato de cartões igual às fontes.');}else fs.writeFileSync(file,text);}
module.exports={contrato,assinatura,variantes,pos,letra,hash};
