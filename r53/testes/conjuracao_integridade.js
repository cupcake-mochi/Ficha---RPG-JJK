'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const p = require('../diagnostico-android/preparar_conjuracao_integridade');
const {formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');
const {norm} = require('../diagnostico-android/preparar_pratica_cotidiana');
const key = d => [d.aba, d.r, d.c].join(':');

const vmContext = vm.createContext({});
vm.runInContext(require('../../medidas/carregar-ficha').fontes(), vmContext);
assert.equal(vmContext.SOBRAS_.length, 0);
const tabs = [...new Set(p.plano.map(d => d.aba))];
assert.deepEqual(tabs, ['FICHA', 'FICHA AMALDIÇOADA']);
assert.equal(p.plano.length, 41);
assert.equal(new Set(p.plano.map(key)).size, 41);
const alcance = require('../diagnostico-android/preparar_alcance_cura');
const apoio = require('../diagnostico-android/preparar_alcance_beneficios');
const posteriores = new Map(alcance.plano.map(d => [key(d), d]));
const maisRecentes = new Map(apoio.plano.map(d => [key(d), d]));
const tempo = require('../diagnostico-android/preparar_tempo_feiticos');
const novos = new Map(tempo.plano.map(d => [key(d), d]));
const config = alcance.reverterEditor(apoio.reverterEditor(tempo.reverterEditor(vmContext.R53_EDITOR_)));
const anterior = p.reverterEditor(config);
assert.equal(anterior.contextos.length, 251);
for (const d of p.plano) {
  const a = vmContext.ABAS.find(a => a.nome === d.aba);
  const posterior = posteriores.get(key(d));
  const maisRecente = maisRecentes.get(key(d));
  if (posterior) assert.equal(posterior.antes, d.depois, key(d));
  if (maisRecente) assert.equal(maisRecente.antes, posterior?.depois ?? d.depois, key(d));
  const novo = novos.get(key(d));
  const esperado = maisRecente?.depois ?? posterior?.depois ?? d.depois;
  if (novo) assert.equal(novo.antes, esperado, key(d));
  assert.equal(a.vals.find(v => v[0] === d.r && v[1] === d.c)[2], novo?.depois ?? esperado, key(d));
  if (d.cartao) {
    assert.equal(config.contextos.find(g => g.id === d.cartao).formulas[d.a1], d.depois, d.cartao);
  }
}
const bases = tabs.map(nome => ({
  nome, vals: p.plano.filter(d => d.aba === nome).map(d => [d.r, d.c, d.antes, 91]),
}));
vm.runInContext(p.molde(), vmContext);
const bad = structuredClone(bases);
bad.at(-1).vals.at(-1)[2] = 'divergente';
const badBefore = JSON.stringify(bad);
assert.throws(() => vmContext.r53AjustarConjuracao_(bad), /alvo divergente/);
assert.equal(JSON.stringify(bad), badBefore);
vmContext.r53AjustarConjuracao_(bases);
const aplicado = JSON.stringify(bases);
vmContext.r53AjustarConjuracao_(bases);
assert.equal(JSON.stringify(bases), aplicado);

for (const locale of ['pt_BR', 'en_US']) {
  const snap = {locale, cells: p.plano.map(d => ({
    ...d, sheetId: tabs.indexOf(d.aba), value: formulaLocal(d.antes, locale),
  }))};
  const requests = p.planejar(snap).requests;
  assert.equal(requests.length, 41);
  for (const [i, q] of requests.entries()) {
    const d = p.plano[i];
    assert.equal(q.updateCells.fields, 'userEnteredValue');
    assert.equal(q.updateCells.rows[0].values[0].userEnteredValue.formulaValue,
      norm(formulaLocal(d.depois, locale)));
  }
  const updated = {...snap, cells: snap.cells.map(d => ({...d, value: formulaLocal(d.depois, locale)}))};
  assert.equal(p.planejar(updated, true).requests.length, 41);
  assert.throws(() => p.planejar(updated), /divergente/);
}
assert.throws(() => p.prepararCodigo('outro projeto'), /PR70/);
assert.throws(() => p.prepararEditor('outro editor'), /PR70/);
if (process.argv[2]) {
  const dir = process.argv[2];
  const read = file => fs.readFileSync(dir + '/' + file, 'utf8');
  const codigo = p.prepararCodigo(read('era-nova-Codigo-fronteira-final-relido.gs'));
  const editor = p.prepararEditor(read('era-nova-EditorR53-salvo.gs'));
  new vm.Script(codigo);
  new vm.Script(editor);
  vmContext.r53AjustarConjuracao_(JSON.parse(read('base-modelo-instalado.json')).abas);
}
console.log(JSON.stringify({resultado: 'OK', alvos: 41, cartoes: 40, transportePrivado: !!process.argv[2]}));
