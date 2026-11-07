'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const zlib = require('node:zlib');
const p = require('../diagnostico-android/preparar_liberacoes');
const rt = require('../pratica_cotidiana_runtime');
const {blocoMontagens} = require('../diagnostico-android/preparar_fragil_fica');
const {formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');
const {norm} = require('../diagnostico-android/preparar_pratica_cotidiana');

const alvos = p.formulas();
assert.deepEqual(alvos.map(d => [d.r, d.c]), [[38,183], [39,183], [40,183]]);
assert.throws(() => p.prepararCodigo('outro projeto'), /PR84/);

for (const locale of ['pt_BR', 'en_US']) {
  const snapshot = {locale, cells: alvos.map(({aba,r,c}) => ({aba,r,c,sheetId:40,value:'=""'}))};
  const plano = p.prepararCelulas(snapshot);
  const reversao = plano.reverter(plano.final);
  assert.equal(plano.pedidos.length, 3);
  assert.equal(reversao.length, 3);
  for (const [i,d] of alvos.entries()) {
    assert.equal(plano.pedidos[i].updateCells.fields, 'userEnteredValue');
    assert.deepEqual(plano.pedidos[i].updateCells.start, {sheetId:40,rowIndex:d.r-1,columnIndex:182});
    assert.equal(plano.pedidos[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue,
      norm(formulaLocal(d.depois, locale)));
    assert.equal(reversao[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue, '=""');
    assert.ok(d.depois.includes('nível mínimo '+10*(i+1)));
  }
  for (const mutate of [s => s.cells.pop(), s => s.cells.push(s.cells[0]),
      s => {s.cells[0].r=37;}, s => {s.cells[2].value='=TRUE';}]) {
    const alterado = structuredClone(snapshot);
    mutate(alterado);
    assert.throws(() => p.prepararCelulas(alterado));
  }
  const alterado = structuredClone(plano.final);
  alterado.cells[0].value = '=TRUE';
  assert.throws(() => plano.reverter(alterado), /Célula divergente/);

  const writes = new Map();
  let loads = 0;
  const ctx = vm.createContext({Utilities: {
    base64Decode: s => Buffer.from(s,'base64'), newBlob: x => x,
    ungzip: x => { loads++; return {getDataAsString: () => zlib.gunzipSync(x).toString()}; },
  }, r53CargaFormulaNoIdioma_: formulaLocal});
  vm.runInContext(rt.gerar(),ctx);
  function editar(aba,r,c,rr=r,cc=c) {
    writes.clear();
    return ctx.r53PraticaRestaurar_({range: {
      getRow:()=>r, getLastRow:()=>rr, getColumn:()=>c, getLastColumn:()=>cc,
      getSheet:()=>({getName:()=>aba, getParent:()=>({getSpreadsheetLocale:()=>locale}),
        getRange:(row,col)=>({setValues: values=>values.forEach((line,y)=>line.forEach((v,x)=>{
          const k=(row+y)+':'+(col+x);assert.ok(!writes.has(k));writes.set(k,v);
        }))}),
      }),
    }});
  }
  assert.equal(editar('FICHA',38,183),false);
  assert.equal(editar('DADOS_R53',38,182),false);
  assert.equal(loads,0);
  for (const d of alvos) {
    assert.equal(editar(d.aba,d.r,d.c),true);
    assert.deepEqual([...writes],[[d.r+':'+d.c,formulaLocal(d.depois,locale)]]);
  }
  assert.equal(editar('DADOS_R53',37,183,40,183),false);
  assert.equal(writes.size,3);
  for (const d of alvos) assert.equal(writes.get(d.r+':'+d.c),formulaLocal(d.depois,locale));
  assert.equal(editar('DADOS_R53',46,183),false);
  assert.equal(writes.size,0);
  const legado = rt.dados().find(([aba,r,c])=>aba==='DADOS_R53'&&r===41&&c===183);
  assert.equal(editar('DADOS_R53',41,183),true);
  assert.equal(writes.get('41:183'),formulaLocal(legado[3],locale));
  assert.equal(editar('DADOS_R53',38,180),true);
  assert.equal(writes.size,1);
  assert.equal(loads,2);
}

if (process.argv[2]) {
  const src=fs.readFileSync(process.argv[2],'utf8');
  const novo=p.prepararCodigo(src);
  new vm.Script(novo);
  const strip=s=>s.replace(blocoMontagens(s),'').split(p.faixaMontagens(s)).join('');
  assert.equal(strip(novo),strip(src));
  assert.throws(()=>p.prepararCodigo(novo),/PR84/);
}
console.log(JSON.stringify({resultado:'OK',formulas:3,locales:2,transporte:!!process.argv[2]}));
