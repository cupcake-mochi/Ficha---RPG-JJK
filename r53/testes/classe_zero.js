'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const p = require('../diagnostico-android/preparar_classe_zero');
const rt = require('../pratica_cotidiana_runtime');
const {formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');
const {norm} = require('../diagnostico-android/preparar_pratica_cotidiana');
const key = d => [d.aba, d.r, d.c].join(':');
const tabs = ['DADOS_CUSTOM', 'FICHA AMALDIÇOADA', 'DADOS_R53'];

const c = vm.createContext({});
vm.runInContext(require('../../medidas/carregar-ficha').fontes(), c);
assert.equal(c.SOBRAS_.length, 0);
assert.equal(p.plano.length, 23);
assert.equal(new Set(p.plano.map(key)).size, 23);
assert.deepEqual([...new Set(p.plano.map(d => d.aba))], tabs);
const editor = c.R53_EDITOR_;
assert.equal(p.reverterEditor(editor).contextos.length, 251);
assert.equal(p.plano.filter(d => d.cartao).length, 12);

const novo = new Map(p.plano.map(d => [key(d), d]));
const antiga = rt.dados([]);
const atual = rt.dados();
assert.equal(atual.length, antiga.length + 10);
assert.deepEqual(atual.slice(antiga.length), p.plano.filter(d => d.aba === 'DADOS_R53').map(d => [d.aba,d.r,d.c,d.depois]));
let curto = 0;
for (const [i, [aba, r, c, v]] of antiga.entries()) {
  const d = novo.get(key({aba, r, c}));
  if (d) curto++;
  assert.deepEqual(atual[i], [aba, r, c, d ? d.depois : v]);
}
assert.equal(curto, 3);
for (const d of p.plano) {
  const aba = c.ABAS.find(a => a.nome === d.aba);
  const direct = aba.vals.find(v => v[0] === d.r && v[1] === d.c);
  const bloco = (aba.abaixo ?? []).find(b => b[0] < d.r && d.r <= b[2] && b[1] <= d.c && d.c <= b[3]);
  const origem = bloco && aba.vals.find(v => v[0] === bloco[0] && v[1] === d.c);
  const formula = direct?.[2] ?? (origem && require('../../medidas/sheets-de-mentira').deslocaFormula(origem[2], d.r-bloco[0]));
  assert.equal(formula, d.depois, key(d));
  if (d.cartao) assert.equal(editor.contextos.find(g => g.id === d.cartao).formulas[d.a1], d.depois);
}
vm.runInContext(p.molde(), c);
const bases = [{nome:'FICHA AMALDIÇOADA', vals:p.plano.filter(d => d.aba === 'FICHA AMALDIÇOADA' && d.r <= 327)
  .map(d => [d.r, d.c, d.antes, 0])}];
assert.equal(bases[0].vals.length, 10);
const divergente = structuredClone(bases);
divergente.at(-1).vals.at(-1)[2] = 'fora do snapshot';
const antes = JSON.stringify(divergente);
assert.throws(() => c.r53AjustarClasseZero_(divergente), /alvo divergente/);
assert.equal(JSON.stringify(divergente), antes);
c.r53AjustarClasseZero_(bases);
const aplicado = JSON.stringify(bases);
c.r53AjustarClasseZero_(bases);
assert.equal(JSON.stringify(bases), aplicado);

for (const locale of ['pt_BR', 'en_US']) {
  const snap = {locale, cells: p.plano.map(d => ({...d, sheetId: tabs.indexOf(d.aba), value: formulaLocal(d.antes, locale)}))};
  const requests = p.planejar(snap).requests;
  assert.equal(requests.length, p.plano.length);
  for (const [i, q] of requests.entries()) {
    assert.equal(q.updateCells.fields, 'userEnteredValue');
    assert.equal(q.updateCells.rows[0].values[0].userEnteredValue.formulaValue,
      norm(formulaLocal(p.plano[i].depois, locale)));
  }
  const updated = {...snap, cells: snap.cells.map(d => ({...d, value: formulaLocal(d.depois, locale)}))};
  assert.equal(p.planejar(updated, true).requests.length, p.plano.length);
  assert.throws(() => p.planejar(updated), /divergente/);
}

assert.throws(() => p.prepararCodigo('outro projeto'), /PR71/);
assert.throws(() => p.prepararEditor('outro editor'), /PR71/);
if (process.argv[2]) {
  for (const ficha of ['era', 'ciclo']) {
    const ler = nome => fs.readFileSync(process.argv[2] + '/' + ficha + '-' + nome + '-antes.gs', 'utf8');
    const codigo = p.prepararCodigo(ler('Codigo'));
    const editor = p.prepararEditor(ler('Editor'));
    new vm.Script(codigo);
    new vm.Script(editor);
  }
}
console.log(JSON.stringify({resultado:'OK', alvos:p.plano.length, editor:12, curto, transportePrivado:!!process.argv[2]}));
