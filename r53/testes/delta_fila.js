'use strict';
// Compara toda a geração com a base auditada (f484f49, 27/10/2026); só muda o que a lista diz.
// A base anterior, fa54ab6, só aceitava as 12 mudanças das barras e das Sementes e ficou para trás
// com o Caminho.gs, o Eventos.gs e as 17 mudanças que vieram depois.
const vm = require('vm'), cp = require('child_process'), assert = require('assert');
const loader = require('../../medidas/carregar-ficha');
function read(source) {
  const ctx = {}; vm.createContext(ctx); vm.runInContext(source, ctx);
  assert.strictEqual(ctx.SOBRAS_.length, 0);
  return JSON.parse(JSON.stringify(ctx.ABAS));
}
const before = read(loader.arquivos().map(name => cp.execFileSync('git',
  ['show', 'f484f49ade742c435c41367b19a321f910ee8316:apps-script/' + name],
  {encoding:'utf8', maxBuffer:100000000})).join('\n'));
const after = read(loader.fontes());
// 27/10/2026, o nível escrito na mão: a base do XP (CY54/CZ54), o XP total somando ela e a nota do XP total.
// E o NÍVEL da FICHA (AH11) como menu estrito de 1 a 30.
const expected = new Set(['DADOS.vals.47,104.0', 'DADOS.vals.54,103', 'DADOS.vals.54,104', 'FICHA PESSOAL.notas.14.1',
  'FICHA.dv.AH11', 'FICHA.menus_estritos']);
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
  // os menus pela faixa: um menu novo no meio da lista não desloca os outros (27/10/2026, o NÍVEL da FICHA)
  if (Array.isArray(sheet.dv)) sheet.dv = Object.fromEntries(sheet.dv.map(d => [d[0], d.slice(1)]));
  return sheet;
}
assert.strictEqual(after.length,before.length);
for (let i=0;i<before.length;i++) compare(normalize(before[i]),normalize(after[i]),after[i].nome);
assert.deepStrictEqual(new Set(changed),expected);
const sheet = name => after.find(s => s.nome === name);
assert(sheet('DADOS').vals['47,104'][0].endsWith('+N(DADOS!$CZ$54)'));
assert.deepStrictEqual(sheet('DADOS').vals['54,103'], ['xp base',5]);
assert.deepStrictEqual(sheet('DADOS').vals['54,104'], [0,7]);
for (const row of [26,30,34]) assert(sheet('FICHA').vals[row+',19'][0].includes(`IF(OR(N($D$${row})<=0,N($J$${row})<=0),""`));
const names = ['Domínio Simples','Energia Reversa','Pétala','Aptidão Própria'];
for (let i=0;i<4;i++) {
  const row = i+2;
  assert.strictEqual(sheet('DADOS_AM').vals[row+',93'][0], names[i]);
  assert.strictEqual(sheet('DADOS_AM').vals[row+',97'][0],
    `=IF($A$2=2,IFERROR(INDEX($CO$2:$CO$5,${i+1}),""),IF($A$2>=3,IFERROR(INDEX($CQ$2:$CQ$4,${i+1}),""),""))`);
}
assert.deepStrictEqual(sheet('FICHA AMALDIÇOADA').dv.J16, ['DADOS_AM!$CS$2:$CS$5']);
assert.deepStrictEqual(sheet('FICHA').dv.AH11, ['"' + Array.from({length:30}, (_, i) => i + 1).join(',') + '"']);
console.log(JSON.stringify({resultado:'OK',abas:after.length,mudancas_autorizadas:changed.length,
  demais_campos_iguais:true,escopo:'Fonte gerada; não compara a ficha preenchida'}));
