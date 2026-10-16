// Regressão focal do catálogo real: altura compartilhada e custo do gatilho.
const fs = require('fs'), vm = require('vm'), assert = require('assert'), path = require('path');
const model = JSON.parse(fs.readFileSync(process.argv[2] || path.join(__dirname, 'nuvem-b47/saidas/pecas-modelo.json'), 'utf8'));
const spec = model.layout.abas.find(a => a.nome === 'CONFIGURAÇÃO');
const values = {}, heights = {}, calls = {};
const sheet = {getRange(a1) { return {getDisplayValue() { return values[a1] || ''; }}; },
  setRowHeights(r, n, h) { for (let i=0;i<n;i++) heights[r+i]=h; }};
const ctx = {ABAS:[spec], SpreadsheetApp:{getActive(){return {getSheetByName(){return sheet;}};}}};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync('apps-script/Codigo.gs','utf8'),ctx);
vm.runInContext(fs.readFileSync('apps-script/Habilidades.gs','utf8'),ctx);
const edit = (a1, value) => {
  values[a1]=value;
  const [,col,row]=/^([A-Z]+)(\d+)$/.exec(a1), r=Number(row);
  const c=[...col].reduce((x,ch)=>x*26+ch.charCodeAt(0)-64,0);
  Object.keys(calls).forEach(k=>delete calls[k]);
  const read=(k,v)=>{calls[k]=(calls[k]||0)+1;return v;};
  const result=ctx.esticarCaixas_({range:{getSheet(){return sheet;},
    getRow(){return read('row',r);},getColumn(){return read('col',c);},
    getNumRows(){return read('rows',1);},getNumColumns(){return read('cols',1);}}},'CONFIGURAÇÃO');
  assert.deepStrictEqual(calls,{row:1,col:1,rows:1,cols:1},'não multiplicar chamadas ao serviço pelo número de cartões');
  return result;
};
const left='Teste visual temporário. '+('Requisitos e incompatibilidades precisam continuar legíveis, sem cortar o texto nem abrir a borda. '.repeat(24));
const right='Teste visual do cartão vizinho. '+('O campo maior precisa preservar o espaço de ambos os cartões e continuar inteiro depois que o texto da esquerda for apagado. '.repeat(28))+'Fim do teste.';
const first=model.registros.find(g=>g.tipo==='melhoria'&&g.n===1);
const neighbor=model.registros.find(g=>g.tipo==='melhoria'&&g.n===2);
const lastRecord=model.registros.filter(g=>g.tipo==='restricao').at(-1);
const a=first.requisitos,b=neighbor.requisitos,r=Number(a.match(/\d+/)[0]);
assert.strictEqual(edit(a,left),1);assert.strictEqual(heights[r],110);
assert.strictEqual(edit(b,right),1);assert.strictEqual(heights[r],186);
edit(a,'');assert.strictEqual(heights[r],186);
edit(b,'');for(let i=r;i<=r+3;i++)assert.strictEqual(heights[i],25);
const last='Teste temporário da última Restrição. '+('O efeito precisa aparecer por inteiro, com bordas contínuas, e voltar ao tamanho normal quando for apagado. '.repeat(25))+'Fim da Restrição.';
const z=lastRecord.efeito,lr=Number(z.match(/\d+/)[0]);
// Slot 30 is on the narrower right card (558 px; the old final slot was
// on the 669 px left card). The same text needs 81 px per row here.
assert.strictEqual(edit(z,last),1);for(let i=lr;i<=lr+6;i++)assert.strictEqual(heights[i],81);
edit(z,'');for(let i=lr;i<=lr+6;i++)assert.strictEqual(heights[i],25);
assert.strictEqual(edit('A1',''),0);
console.log(JSON.stringify({resultado:'OK',grupos:spec.esticam.length,cenarios:7,leituras_limites_por_edicao:4}));
