'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {plano, planejar, prepararCodigo, molde} = require('../diagnostico-android/preparar_equipamento');
const {chave, formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');

function alvo(abas, d) {
  const aba = abas.find(x => x.nome === d.aba);
  return d.addr ? aba.notas.find(v => v[0] === d.addr)?.[1] :
    aba.vals.find(v => v[0] === d.r && v[1] === d.c)?.[2];
}
const ctx = vm.createContext({});
vm.runInContext(require('../../medidas/carregar-ficha').fontes(), ctx);
assert.equal(ctx.SOBRAS_.length, 0);
assert.equal(new Set(plano.celulas.map(chave)).size, plano.celulas.length);
for (const d of plano.celulas) assert.equal(alvo(ctx.ABAS, d), d.depois, chave(d));
const pessoal = ctx.ABAS.find(a => a.nome === 'FICHA PESSOAL');
assert.equal(JSON.stringify(pessoal.validacoes_formula), JSON.stringify(plano.validacoes));
assert.equal(plano.validacoes.length, 8);

const original = [
  {nome: 'FICHA PESSOAL', notas: [], vals: []},
  {nome: 'DADOS', vals: []}
];
for (const d of plano.celulas) {
  const aba = original.find(a => a.nome === d.aba);
  if (d.addr) aba.notas.push([d.addr, d.antes]);
  else if (d.antes !== null) aba.vals.push([d.r, d.c, d.antes, 0]);
}
const quebrado = JSON.parse(JSON.stringify(original));
quebrado[1].vals[0][2] = 'alteração de usuário';
const antes = JSON.stringify(quebrado);
vm.runInContext(molde(), ctx);
assert.throws(() => ctx.r53AjustarEquipamento_(quebrado), /alvo divergente/);
assert.equal(JSON.stringify(quebrado), antes);
ctx.r53AjustarEquipamento_(original);
for (const d of plano.celulas) assert.equal(alvo(original, d), d.depois, chave(d));
const depois = JSON.stringify(original);
ctx.r53AjustarEquipamento_(original);
assert.equal(JSON.stringify(original), depois);

for (const locale of ['pt_BR', 'en_US']) {
  function snap(aplicado) {
    return {locale, cells: [
      ...plano.celulas.map(d => ({...d, sheetId: d.aba === 'DADOS' ? 1 : 2,
        [d.addr ? 'note' : 'value']: formulaLocal(aplicado ? d.depois : d.antes, locale)})),
      ...plano.validacoes.map(([addr, f]) => ({aba: 'FICHA PESSOAL', sheetId: 2, r: +addr.slice(1), c: 11,
        validation: aplicado ? {strict: true, condition: {type: 'CUSTOM_FORMULA',
          values: [{userEnteredValue: formulaLocal(f, locale)}]}} : undefined}))
    ]};
  }
  const s = snap(false);
  const p = planejar(s);
  assert.equal(p.requests.length, plano.celulas.length + 8);
  assert.equal(planejar(snap(true), true).requests.length, p.requests.length);
  s.cells.at(-1).validation = {strict: true};
  assert.throws(() => planejar(s), /Validação divergente/);
}
assert.throws(() => prepararCodigo('outro projeto'), /incompatível/);
if (process.argv[2]) {
  const codigo = fs.readFileSync(process.argv[2], 'utf8');
  const novo = prepararCodigo(codigo);
  new vm.Script(novo);
  assert.throws(() => prepararCodigo(novo), /incompatível/);
  if (process.argv[3]) fs.writeFileSync(process.argv[3], novo);
}
console.log(JSON.stringify({resultado: 'OK', alvos: plano.celulas.length, validacoes: plano.validacoes.length}));
