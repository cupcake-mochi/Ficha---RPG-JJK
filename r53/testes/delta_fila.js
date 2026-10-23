'use strict';
// Compara toda a geração com a base auditada; só barras e Sementes podem mudar.
const vm = require('vm'), cp = require('child_process'), assert = require('assert');
const loader = require('../../medidas/carregar-ficha');
function read(source) {
  const ctx = {}; vm.createContext(ctx); vm.runInContext(source, ctx);
  assert.strictEqual(ctx.SOBRAS_.length, 0);
  return JSON.parse(JSON.stringify(ctx.ABAS));
}
const before = read(loader.arquivos().map(name => cp.execFileSync('git',
  ['show', 'fa54ab633313b2f230c4c669041b6d552a66c9c6:apps-script/' + name],
  {encoding:'utf8', maxBuffer:100000000})).join('\n'));
const after = read(loader.fontes());
const expected = new Set([
  ...[26,30,34].map(row => `FICHA.vals.${row},19.0`),
  'FICHA AMALDIÇOADA.dv.0.1',
  ...[2,3,4].map(row => `DADOS_AM.vals.${row},97.0`),
  ...[2,3,4,5].map(row => `DADOS_AM.vals.${row},93`),
  'DADOS_AM.vals.5,97'
]);
const changed = [];
function compare(a,b,path) {
  if (JSON.stringify(a) === JSON.stringify(b)) return;
  if (a && b && typeof a === 'object' && typeof b === 'object') {
    for (const key of new Set([...Object.keys(a),...Object.keys(b)])) {
      if (key !== 'geracao') compare(a[key],b[key],path+'.'+key);
    }
  } else {
    assert(expected.has(path), 'Mudança inesperada: '+path); changed.push(path);
  }
}
function normalize(sheet) {
  sheet.vals = Object.fromEntries(sheet.vals.map(v => [v[0]+','+v[1],v.slice(2)]));
  return sheet;
}
assert.strictEqual(after.length,before.length);
for (let i=0;i<before.length;i++) compare(normalize(before[i]),normalize(after[i]),after[i].nome);
assert.deepStrictEqual(new Set(changed),expected);
const sheet = name => after.find(s => s.nome === name);
for (const row of [26,30,34]) assert(sheet('FICHA').vals[row+',19'][0].includes(`IF(OR(N($D$${row})<=0,N($J$${row})<=0),""`));
const names = ['Domínio Simples','Energia Reversa','Pétala','Aptidão Própria'];
for (let i=0;i<4;i++) {
  const row = i+2;
  assert.strictEqual(sheet('DADOS_AM').vals[row+',93'][0], names[i]);
  assert.strictEqual(sheet('DADOS_AM').vals[row+',97'][0],
    `=IF($A$2=2,IFERROR(INDEX($CO$2:$CO$5,${i+1}),""),IF($A$2>=3,IFERROR(INDEX($CQ$2:$CQ$4,${i+1}),""),""))`);
}
assert.strictEqual(sheet('FICHA AMALDIÇOADA').dv[0][1], 'DADOS_AM!$CS$2:$CS$5');
console.log(JSON.stringify({resultado:'OK',abas:after.length,mudancas_autorizadas:changed.length,
  demais_campos_iguais:true,escopo:'Fonte gerada; não compara a ficha preenchida'}));
