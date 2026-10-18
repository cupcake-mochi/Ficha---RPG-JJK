// Altura compartilhada entre listas independentes: limpar uma lista não
// pode cortar o texto que continua preenchido em outra, mesmo recolhida.
const fs=require('fs'), vm=require('vm'), assert=require('assert');
const root=require('path').resolve(__dirname,'..');
const context={};vm.createContext(context);
vm.runInContext(require(root+'/medidas/carregar-ficha.js').fontes(),context);
vm.runInContext(fs.readFileSync(root+'/apps-script/Codigo.gs','utf8'),context);
vm.runInContext(fs.readFileSync(root+'/apps-script/Habilidades.gs','utf8'),context);
const spec=context.ABAS.find(a=>a.nome==='CONFIGURAÇÃO');
assert(spec.horizontal);assert.equal(spec.rows,400);assert.equal(spec.cols,238);
const values={},heights={},calls={};
function point(a){const [,col,row]=/^([A-Z]+)(\d+)$/.exec(a);return[+row,[...col].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0)];}
const sheet={getRange(...args){
  assert.equal(args.length,4,'ler todos os painéis numa única chamada');
  calls.batch=(calls.batch||0)+1;
  return{getDisplayValues(){const rows=Array.from({length:spec.rows},()=>Array(spec.cols).fill(''));
    for(const [a,text] of Object.entries(values)){const[r,c]=point(a);rows[r-1][c-1]=text;}return rows;}};
},setRowHeights(r,n,h){for(let k=0;k<n;k++)heights[r+k]=h;}};
context.SpreadsheetApp={getActive(){return{getSheetByName(){return sheet;}};}};
const group=spec.esticam[0];assert.equal(spec.esticam.length,1);
// Escolher caixas de categorias diferentes que compartilham uma linha.
const panel=c=>Math.floor((point(c[1][0])[1]-1)/17);
let pair;
for(const a of group.textos){const b=group.textos.find(b=>panel(a)!==panel(b)&&a[2]===b[2]&&a[3]===b[3]);if(b){pair=[a,b];break;}}
assert(pair,'existem textos sobrepostos entre categorias');
function edit(a,text){values[a]=text;calls.batch=0;const[r,c]=point(a);
  const event={range:{getRow:()=>r,getColumn:()=>c,getNumRows:()=>1,getNumColumns:()=>1,getSheet:()=>sheet}};
  const n=context.esticarCaixas_(event,'CONFIGURAÇÃO');assert.equal(n,1);assert.equal(calls.batch,1);
}
const[a,b]=pair;const ar=a[1][0],br=b[1][0];
const long='Requisitos e efeitos precisam continuar legíveis em todas as listas. '.repeat(160);
edit(ar,'Texto curto.');const baseline=heights[a[2]];
edit(br,long);const expanded=heights[b[2]];assert(expanded>baseline);
edit(ar,'');assert.equal(heights[b[2]],expanded,'limpar outro painel preserva o texto longo');
edit(br,'');assert.equal(heights[a[2]],baseline,'limpar todos restaura o piso original');
for(const[r,h] of Object.entries(heights))assert(h>=Math.max(25,spec.alturas[r]||0));
assert.equal(spec.links_paineis.length,13);
console.log(JSON.stringify({resultado:'OK',cenarios:4,paineis:spec.horizontal.secoes.length,linhas:spec.rows,colunas:spec.cols,leitura_em_lote_por_edicao:1}));
