'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const patch = require('../diagnostico-android/preparar_integridade_movimento');
const {formulaLocal} = require('../diagnostico-android/preparar_pilha_5156');

const key = d => [d.aba, d.addr || d.r + ',' + d.c].join('!');
assert.equal(new Set(patch.plano.map(key)).size, patch.plano.length);
const ctx = vm.createContext({});
vm.runInContext(require('../../medidas/carregar-ficha').fontes(), ctx);
require('../diagnostico-android/preparar_aviso_atributo').reverterModelo(require('../diagnostico-android/preparar_menu_oficios').reverterModelo(require('../diagnostico-android/preparar_especializacao').reverterModelo(ctx.ABAS)));require('../diagnostico-android/preparar_buff_decimal').reverterModelo(ctx.ABAS);require('../diagnostico-android/preparar_reserva_bolsa').reverterModelo(ctx.ABAS);
require('../diagnostico-android/preparar_origens_recursos').reverterModelo(ctx.ABAS);
assert.equal(ctx.SOBRAS_.length, 0);
vm.runInContext(patch.molde(), ctx);
const abas = [...new Set(patch.plano.map(d => d.aba))].map(nome => ({nome, vals: [], notas: []}));
const alvo = (modelo, d) => {
  const aba = modelo.find(a => a.nome === d.aba);
  return d.addr ? aba.notas.find(v => v[0] === d.addr)?.[1] :
    aba.vals.find(v => v[0] === d.r && v[1] === d.c)?.[2];
};
for (const d of patch.plano) {
  const posterior = [
    ...require('../diagnostico-android/bencaos_imunidades_plano.json'),
    ...require('../diagnostico-android/conjuracao_integridade_plano.json'),
  ].find(x => key(x) === key(d));
  if (posterior) assert.equal(posterior.antes, d.depois, key(d));
  assert.equal(alvo(ctx.ABAS, d), posterior ? posterior.depois : d.depois, key(d));
  const aba = abas.find(a => a.nome === d.aba);
  if (d.addr) aba.notas.push([d.addr, d.antes]);
  else aba.vals.push([d.r, d.c, d.antes, 91]);
}
const invalido = JSON.parse(JSON.stringify(abas));
const ultimo = patch.plano.at(-1);
const abaInvalida = invalido.find(a => a.nome === ultimo.aba);
const v = ultimo.addr ? abaInvalida.notas.find(a => a[0] === ultimo.addr) :
  abaInvalida.vals.find(a => a[0] === ultimo.r && a[1] === ultimo.c);
v[ultimo.addr ? 1 : 2] = 'divergente';
const antesInvalido = JSON.stringify(invalido);
assert.throws(() => ctx.r53AjustarIntegridadeMovimento_(invalido), /alvo divergente/);
assert.equal(JSON.stringify(invalido), antesInvalido);
ctx.r53AjustarIntegridadeMovimento_(abas);
for (const d of patch.plano) assert.equal(alvo(abas, d), d.depois, key(d));
const depois = JSON.stringify(abas);
ctx.r53AjustarIntegridadeMovimento_(abas);
assert.equal(JSON.stringify(abas), depois);

const nativos = patch.alvosNativos();
assert.equal(new Set(nativos.map(key)).size, nativos.length);
for (const locale of ['pt_BR', 'en_US']) {
  const snapshot = {locale, cells: nativos.map(d => ({...d, sheetId: abas.findIndex(a => a.nome === d.aba),
    [d.addr ? 'note' : 'value']: formulaLocal(d.antes, locale)}))};
  assert.equal(patch.planejar(snapshot).requests.length, nativos.length);
  const aplicado = {...snapshot, cells: snapshot.cells.map(d => ({...d,
    [d.addr ? 'note' : 'value']: formulaLocal(d.depois, locale)}))};
  assert.equal(patch.planejar(aplicado, true).requests.length, nativos.length);
  assert.throws(() => patch.planejar(aplicado), /divergente/);
}
assert.throws(() => patch.prepararCodigo('outro projeto'), /incompatível/);
if (process.argv[2]) {
  const path = require('node:path'), zlib = require('node:zlib');
  const ler = nome => fs.readFileSync(path.join(process.argv[2], 'qa-era-' + nome + '.gs'), 'utf8');
  const fonte = require('../diagnostico-android/preparar_recursos_fila').preparar(ler('Codigo'));
  const novo = patch.prepararCodigo(fonte);
  new vm.Script(novo);
  assert.throws(() => patch.prepararCodigo(novo), /incompatível/);

  const partes = [];
  for (const nome of ['Ficha', 'Invocacoes', 'Analise', 'Configuracao', 'Origens']) {
    const trecho = ler(nome).match(/var R53_CODIGO_(\d+)_ = ("[^\n]*");/);
    partes[+trecho[1]] = JSON.parse(trecho[2]);
  }
  const instalado = vm.createContext({code: zlib.gunzipSync(Buffer.from(partes.join(''), 'base64')).toString('utf8')});
  for (const nome of ['pilha_5156_runtime', 'recursos_fila_runtime']) {
    vm.runInContext(fs.readFileSync('r53/diagnostico-android/' + nome + '.gs', 'utf8'), instalado);
  }
  const reais = vm.runInContext('(new Function(code))().__estado().abas', instalado);
  ctx.R53_PILHA_516_ = require('../diagnostico-android/pilha_5156_plano.json');
  vm.runInContext(fs.readFileSync('r53/diagnostico-android/pilha_5156_molde.gs', 'utf8'), ctx);
  ctx.r53AjustarPilha516_(reais);
  ctx.r53AjustarIntegridadeMovimento_(reais);
  for (const d of patch.plano) assert.equal(alvo(reais, d), d.depois, key(d));
  console.log(JSON.stringify({codigo: require('../diagnostico-android/preparar_recursos_fila').sha(novo)}));
}
console.log(JSON.stringify({resultado: 'OK', alvosModelo: patch.plano.length, alvosNativos: nativos.length, pacotePrivado: !!process.argv[2]}));
