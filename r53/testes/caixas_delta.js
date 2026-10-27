'use strict';
// Atalho das caixas de ± da FICHA (27/10/2026). Precisa do projeto exportado (nuvem-b47/saidas/atalho/projeto-leve.json,
// fora do Git, o das oficiais antes dos cortes da noite); dele sai o projeto de hoje pelo preparar_cortes_noite.js.
//  1. A conta: r53LivreDelta_ grava o mesmo que o aplicarDelta_ do módulo, na mesma ordem, em todas as combinações de
//     ±, atual, máximo e temporária (número, texto, vazio, decimal, negativo).
//  2. O onEdit inteiro, antes e depois, numa ficha esparsa (só as linhas das barras) e, se existir, na ficha exportada
//     (oficial-era.json): as mesmas células mudam, as mesmas gravações e propriedades; depois, uma leitura e o módulo
//     fechado. Colagem em várias células, outro módulo ou erro antes de gravar caem no caminho de sempre.
const fs = require('fs'), path = require('path'), vm = require('vm'), zlib = require('zlib'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
let checks = 0;
const ok = (c, m) => { assert(c, m); checks++; };
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const pasta = path.join(raiz, 'nuvem-b47/saidas/atalho');
const fp = path.join(pasta, 'projeto-leve.json'), fd = path.join(pasta, 'oficial-era.json');
const gs = fs.readFileSync(path.join(raiz, 'r53/atalho_livre.gs'), 'utf8');
new vm.Script(gs); checks++;
if (!fs.existsSync(fp)) { console.log('caixas_delta: ' + checks + ' verificação (sem o projeto exportado, pulado)'); process.exit(0); }
const { criar, remendosDoProjeto } = require('../arnes_custo');
const { preparar } = require('../diagnostico-android/preparar_atalho');
const base = JSON.parse(fs.readFileSync(fp, 'utf8'));
if (remendosDoProjeto(base) !== 38) { console.log('caixas_delta: a exportação não é a das oficiais de 26/10, pulado'); process.exit(0); }
const g = require('../diagnostico-android/preparar_cortes_noite').gerar(base);
ok(gs.includes(g.esperado.modulo), 'o atalho não é do módulo de hoje');

// O projeto de hoje (o das oficiais): Codigo, EditorR53 e os pedaços do módulo dos cortes da noite.
const gz = zlib.gzipSync(Buffer.from(g.modulo, 'utf8')).toString('base64'), fat = [];
for (let i = 0; i < gz.length; i += 850000) fat.push(gz.slice(i, i + 850000));
// O Codigo instalado tem o atalho de 895d1ec (sem as caixas de ±); o gerador dos cortes lê o atalho do disco.
const sha = t => require('crypto').createHash('sha256').update(t, 'utf8').digest('hex');
const gsInstalado = require('child_process').execSync('git show 895d1ec:r53/atalho_livre.gs', { cwd: raiz, maxBuffer: 1 << 26 }).toString('utf8');
const codigoInstalado = preparar(g.codigoNovo, gsInstalado);
eq(sha(codigoInstalado).slice(0, 8), 'dc1aa740', 'Codigo das oficiais');
eq(g.esperado.editor.slice(0, 8), 'c3d31096', 'EditorR53 das oficiais');
eq(g.esperado.modulo.slice(0, 8), '9dc3480a', 'módulo das oficiais');
const hoje = base.files.filter(f => f.type !== 'JSON').map(f => {
  const r = /^(\/\/[^\n]*\n)var R53_CODIGO_(\d+)_ = ("[^\n]*");\n?$/.exec(f.source);
  if (r) return { name: f.name, source: r[1] + 'var R53_CODIGO_' + r[2] + '_ = ' + JSON.stringify(fat[+r[2]] || '') + ';\n' };
  return { name: f.name, source: f.name === 'Codigo' ? codigoInstalado : f.name === 'EditorR53' ? g.editorNovo : f.source };
});

// ---------- 1. A conta, contra o aplicarDelta_ do módulo ----------
const LINHAS = [26, 30, 34];
function fichaEsparsa(atual, max, temp, passo, linha) {
  const cells = {};
  for (const l of LINHAS) { cells[l + ',4'] = { v: 7 }; cells[l + ',10'] = { v: 12 }; cells[l + ',32'] = { v: 1 }; }
  const put = (c, v) => { if (v !== undefined) cells[linha + ',' + c] = { v }; else delete cells[linha + ',' + c]; };
  put(4, atual); put(10, max); put(32, temp); put(39, passo);
  return { FICHA: { rows: 462, cols: 50, hidden: false, cells } };
}
const A0 = criar({}, {});
vm.runInContext(gs + '\n', A0.ctx);
const delta = vm.runInContext('R53_LIVRE_DELTA_', A0.ctx);
eq(Object.keys(delta).sort(), ['AM26', 'AM30', 'AM34'], 'as três caixas');
eq(LINHAS.map(l => delta['AM' + l]).map(x => [x.a, x.m, x.t]), LINHAS.map(l => ['D' + l, 'J' + l, 'AF' + l]), 'atual, máximo e temp das barras');
const marca = '\nreturn {"acabar":';
const comDelta = g.modulo.replace(marca, '\nreturn {"__delta":function(e){return aplicarDelta_(e,indiceEstatico_());},"acabar":');
ok(comDelta !== g.modulo, 'fim do módulo');
// Um contexto para cada caminho, compilado uma vez; cada combinação escreve as quatro células e desfaz no fim.
const ctxConta = {};
for (const caminho of ['modulo', 'atalho']) {
  const A = criar(fichaEsparsa(undefined, undefined, undefined, undefined, 26), {});
  if (caminho === 'modulo') { A.ctx.__code = comDelta; vm.runInContext('var __m=(new Function(__code))();', A.ctx); }
  else vm.runInContext(gs + '\n', A.ctx);
  ctxConta[caminho] = A;
}
function rodarConta(caminho, dump, linha) {
  const A = ctxConta[caminho], sh = A.ss.getSheetByName('FICHA');
  for (const c of [4, 10, 32, 39]) { const x = sh.cel(linha, c, true), d = dump.FICHA.cells[linha + ',' + c]; x.v = d ? d.v : ''; }
  A.reset();
  A.ctx.__e = { range: sh.getRange('AM' + linha), source: A.ss };
  let erro = null;
  try { vm.runInContext(caminho === 'modulo' ? '__m.__delta(__e)' : 'r53LivreDelta_(__e.range)', A.ctx); } catch (err) { erro = err.message; }
  const out = { erro, alteradas: A.alteradas(), escritas: A.log.filter(e => e.t === 'W').map(e => e.k + ' ' + e.a), leituras: A.log.filter(e => e.t === 'R').map(e => e.a) };
  A.desfazer();
  return out;
}
const atuais = [10, 0, 25, '', 'abc', 5.5, -4], maximos = [20, 0, '', 'x'], temps = [undefined, 0, 3, -2, 'x', 2.5, 30];
const passos = [-3, 3, -15, 25, 0, '', 'x', '-2', 1.5, -0.5, true, false];
let contas = 0;
for (const linha of LINHAS) for (const a of atuais) for (const m of maximos) for (const t of temps) for (const p of passos) {
  if ((contas++ % 3) && linha !== 26) continue;   // energia e integridade numa amostra; a vida inteira
  const d = fichaEsparsa(a, m, t, p, linha);
  const x = rodarConta('modulo', d, linha), y = rodarConta('atalho', d, linha);
  const nome = 'AM' + linha + ' ' + JSON.stringify([a, m, t, p]);
  eq(y.erro, x.erro, nome + ' erro');
  eq(y.alteradas, x.alteradas, nome + ' células');
  eq(y.escritas, x.escritas, nome + ' gravações');
  eq(y.leituras, ['FICHA!D' + linha + ':AM' + linha], nome + ' uma leitura');
}

// ---------- 2. O onEdit inteiro, antes e depois ----------
let aberturas = 0;
function montar(dump, comAtalho, ajuste) {
  const A = criar(JSON.parse(JSON.stringify(dump)), { props: { salario_proximo: '99999' } });
  for (const f of hoje) {
    let s = f.source;
    if (f.name === 'Codigo' && comAtalho) s = preparar(s, ajuste ? ajuste(gs) : gs);
    vm.runInContext(s + '\n', A.ctx, { filename: f.name });
  }
  vm.runInContext('(function(){var o=r53Modulo_;r53Modulo_=function(){__abriu();return o.apply(this,arguments);};r53Modulo_.toString=function(){return String(o);};})();',
    Object.assign(A.ctx, { __abriu: () => { aberturas++; A.log.push({ t: 'M' }); } }));
  return A;
}
function editar(A, a1, v, opts = {}) {
  const sh = A.ss.getSheetByName('FICHA'), range = sh.getRange(a1), x = sh.cel(range.r, range.c, true), old = x.v;
  A.props.salario_proximo = '99999';
  if (opts.estado) for (const [k, val] of Object.entries(opts.estado)) { const rg = sh.getRange(k), c = sh.cel(rg.r, rg.c, true); c.v = val; delete c.f; }
  x.v = v; delete x.f; A.reset();
  A.ctx.__e = { range, source: A.ss, value: v === '' ? undefined : v, oldValue: old === '' ? undefined : old };
  let erro = null; try { vm.runInContext('onEdit(__e)', A.ctx); } catch (err) { erro = err.message; }
  const r = { erro, alteradas: A.alteradas(), modulo: A.log.some(e => e.t === 'M'),
    escritas: A.log.filter(e => e.t === 'W').map(e => [e.k, e.a, e.x || ''].join(' ')),
    props: A.log.filter(e => e.t === 'P' && /\.(set|setAll|del)$/.test(e.k)).map(e => e.k + ' ' + (e.a || '')),
    leituras: A.log.filter(e => e.t === 'R').length };
  A.desfazer();
  return r;
}
function comparar(dump, rotulo, estados) {
  const novo = montar(dump, true), velho = montar(dump, false);
  let n = 0;
  for (const linha of LINHAS) for (const p of [-3, 3, -40, 40, 0, '', 'x', 1.5]) for (const est of estados(linha)) {
    const a1 = 'AM' + linha, a = editar(novo, a1, p, { estado: est }), b = editar(velho, a1, p, { estado: est });
    const nome = rotulo + ' ' + a1 + ' ' + JSON.stringify([p, est]);
    eq(a.erro, b.erro, nome + ' erro');
    eq(a.alteradas, b.alteradas, nome + ' células');
    eq(a.escritas, b.escritas, nome + ' gravações');
    eq(a.props, b.props, nome + ' propriedades');
    ok(b.modulo && !a.modulo, nome + ' o módulo abriu no atalho');
    ok(a.leituras === 1, nome + ' leituras: ' + a.leituras);
    n++;
  }
  // colagem em duas células: o caminho de sempre
  const cola = { range: null };
  for (const A of [novo, velho]) {
    const sh = A.ss.getSheetByName('FICHA'); A.reset();
    A.ctx.__e = { range: sh.getRange('AM26:AN26'), source: A.ss };
    try { vm.runInContext('onEdit(__e)', A.ctx); } catch (err) {}
    cola[A === novo ? 'novo' : 'velho'] = A.log.filter(e => e.t === 'W').map(e => e.k + ' ' + e.a).join('|');
    if (A === novo) ok(A.log.some(e => e.t === 'M'), rotulo + ' colagem abre o módulo');
    A.desfazer();
  }
  eq(cola.novo, cola.velho, rotulo + ' colagem igual');
  // outro módulo: o atalho se desliga
  const outro = montar(dump, true, s => s.replace(/var R53_LIVRE_HASHES_=\["[0-9a-f]{64}"/, 'var R53_LIVRE_HASHES_=["' + '0'.repeat(64) + '"'));
  ok(editar(outro, 'AM26', -3).modulo, rotulo + ' hash diferente desliga');
  // erro antes de gravar: o módulo faz como sempre, e o ± sai aplicado uma vez só
  const falha = montar(dump, true, s => s.replace('v=ficha.getRange(x.l[0],x.l[1],x.l[2],x.l[3]).getValues()', 'v=ficha.getRange(x.l[0],x.l[1],x.l[2],x.l[3]).getValues(),__=null.x'));
  const f1 = editar(falha, 'AM26', -3, { estado: { D26: 10, J26: 20, AF26: 0 } }), f2 = editar(velho, 'AM26', -3, { estado: { D26: 10, J26: 20, AF26: 0 } });
  ok(f1.modulo, rotulo + ' erro antes de gravar abre o módulo');
  eq(f1.alteradas, f2.alteradas, rotulo + ' erro antes de gravar: mesmo resultado');
  return n;
}
const esparsos = linha => [{}, { ['D' + linha]: 10, ['J' + linha]: 20, ['AF' + linha]: 4 }, { ['D' + linha]: 2, ['J' + linha]: 0, ['AF' + linha]: '' }];
// a ficha esparsa leva todas as abas, vazias, fora as linhas das barras da FICHA
const vazio = { FICHA: fichaEsparsa(10, 20, 0, undefined, 26).FICHA };
for (const s of ['CARTEIRA', 'FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'FICHA PESSOAL', 'CONFIGURAÇÃO', 'DADOS', 'DADOS_PROGRESSAO', 'MONTAGENS', 'DADOS_R53', 'DADOS_R53_CATALOGO'])
  vazio[s] = { rows: 100, cols: 50, hidden: false, cells: {} };
let integrados = comparar(vazio, 'esparsa', esparsos), real = 0;
if (fs.existsSync(fd)) {
  const dump = JSON.parse(fs.readFileSync(fd, 'utf8'));
  real = comparar(dump, 'exportada', linha => [{}, ...esparsos(linha)]);
}
// ---------- 3. O trecho do console, num editor de mentira ----------
const pc = require('../diagnostico-android/preparar_caixas_delta').gerar(base);
eq(pc.codigo, codigoInstalado, 'o instalador parte do Codigo das oficiais');
async function rodarTrecho(fontes) {
  const modelos = fontes.map(f => ({ nome: f.name, v: f.source, getValue() { return this.v; }, setValue(x) { this.v = x; this.gravado = true; } }));
  const box = { monaco: { editor: { getModels: () => modelos } }, crypto: globalThis.crypto, TextEncoder, String, JSON, Error, Promise, Uint8Array };
  vm.createContext(box);
  return { r: await vm.runInContext('(async () => { return ' + pc.trecho.replace(/^await /, '') + '; })()', box), modelos };
}
(async () => {
  const t = await rodarTrecho(hoje);
  ok(typeof t.r === 'object', 'o trecho recusou: ' + t.r);
  eq(sha(t.modelos.find(m => m.nome === 'Codigo').v), pc.esperado.codigo, 'Codigo gravado');
  eq(t.modelos.find(m => m.nome === 'Codigo').v, preparar(codigoInstalado, gs), 'Codigo gravado igual ao do arnês');
  ok(t.modelos.filter(m => m.gravado).length === 1, 'só o Codigo muda');
  for (const troca of [s => s + ' ', s => s.replace('R53_LIVRE_FAMILIAS_=', 'R53_LIVRE_FAMILIAS_ =')]) {
    const x = await rodarTrecho(hoje.map(f => f.name === 'Codigo' ? { name: f.name, source: troca(f.source) } : f));
    ok(typeof x.r === 'string' && /^ERRO, nada gravado/.test(x.r) && x.modelos.every(m => !m.gravado), 'Codigo diferente não recusou: ' + x.r);
  }
  console.log('caixas_delta: ' + checks + ' verificações (' + contas + ' contas, ' + integrados + ' edições na ficha esparsa, ' +
    (real ? real + ' na exportada' : 'sem a ficha exportada') + '; trecho do console ' + sha(pc.trecho).slice(0, 8) + ', Codigo ' +
    pc.esperado.codigo_antes.slice(0, 8) + ' → ' + pc.esperado.codigo.slice(0, 8) + ')');
})().catch(err => { console.error(err); process.exit(1); });
