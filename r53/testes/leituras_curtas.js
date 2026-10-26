'use strict';
// Leituras curtas (26/10/2026): saltos, cartas da FICHA, caixas que esticam e habilidades custom da CONFIGURAÇÃO deixam
// de ler abas inteiras. Com a ficha exportada (nuvem-b47/saidas/atalho/, fora do Git), roda o onEdit do projeto leve
// com o módulo instalado e com o mesmo módulo mais os remendos do 23º em diante, célula a célula no mapa onde o
// script age, e confere que deixam as mesmas células (valores, fórmulas, notas), os mesmos formatos e alturas e que o
// novo não custa mais. Regravar a mesma fórmula não conta: o salto religa só o que se escreveu por cima, e os outros
// já estavam com a ligação certa (caixa, alvo e nome são fixos na DADOS_AM e na DADOS_INVOC).
const fs = require('fs'), path = require('path'), vm = require('vm'), zlib = require('zlib'), crypto = require('crypto'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
const DESDE = 22;
let checks = 0;
const ok = (c, m) => { assert(c, m); checks++; };
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const pasta = path.join(raiz, 'nuvem-b47/saidas/atalho');
const fp = path.join(pasta, 'projeto-leve.json'), fd = path.join(pasta, 'oficial-era.json');
if (!fs.existsSync(fp) || !fs.existsSync(fd)) { console.log('leituras_curtas: sem a ficha exportada, pulado'); process.exit(0); }
const { criar, custo, projetoComIncremento } = require('../arnes_custo');
const projeto = JSON.parse(fs.readFileSync(fp, 'utf8')), dump = JSON.parse(fs.readFileSync(fd, 'utf8'));
const codigo = projeto.files.find(f => f.name === 'Codigo').source;
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');

// O módulo instalado, tirado das fatias do projeto, e o novo pelo incremento.
const { velho, novo, hashVelho: hv } = projetoComIncremento(projeto, dump, DESDE);

function montar(modulo, hash) {
  const A = criar(JSON.parse(JSON.stringify(dump)), { props: { salario_proximo: '99999' } });
  A.ctx.__codigo = modulo;
  for (const f of projeto.files.filter(f => f.type !== 'JSON')) {
    let s = f.source;
    if (f.name === 'Codigo') {
      s = s.replace(/var code=Utilities\.ungzip\([^\n]*\.getDataAsString\('UTF-8'\);/, () => 'var code=__codigo;').replace(hv, hash);
      assert(s.includes('var code=__codigo;'), 'carregador');
    }
    vm.runInContext(s + '\n', A.ctx, { filename: f.name });
  }
  vm.runInContext('r53Modulo_()', A.ctx);
  return A;
}
function editar(A, aba, r, c, v) {
  const sh = A.ss.getSheetByName(aba), range = sh.getRange(r, c), old = sh.cel(r, c).v, x = sh.cel(r, c, true);
  A.props.salario_proximo = '99999';
  x.v = v; delete x.f; A.reset();
  A.ctx.__e = { range, source: A.ss, value: v === '' ? undefined : v, oldValue: old === '' ? undefined : old };
  let erro = null; try { vm.runInContext('onEdit(__e)', A.ctx); } catch (err) { erro = err.message; }
  // conteúdo (valor, fórmula, nota) se compara pelas células que mudaram; formatos e alturas, pela gravação
  const conteudo = /^(lista\.)?(valores|valor|fórmula|fórmulas|nota|notas|rico|limpar|setValue|setFormula|setNote|check|uncheck|clearContent)$/;
  const grav = A.log.filter(e => e.t === 'W' && !conteudo.test(e.k)).map(e => [e.k, e.a || '', e.x || ''].join(' '));
  const k = custo(A.log), alt = JSON.parse(JSON.stringify(A.alteradas(), (c, x) => typeof x === 'string' && /^\d{4}-\d\d-\d\dT/.test(x) ? 'data' : x)), inteiras = A.log.filter(e => e.t === 'R' && e.inteira).map(e => e.a);
  const ops = A.log.filter(e => e.t === 'R' || e.t === 'F').map(e => e.t + (e.barreira ? '*' : '') + ' ' + (e.a || '') + (e.inteira ? ' INTEIRA' : '')).join(' | ');
  A.desfazer();
  return { erro, grav, alt, s: k.s, inteiras, ops, props: JSON.stringify(A.props) };
}

// A exportação em xlsx perde as fórmulas dos saltos (HYPERLINK vira texto). A ficha de partida volta a tê-las como o
// acabamento deixa: o código de antes religa todas ao se escrever num salto, e essas fórmulas entram nas duas.
{
  const A = montar(velho, hv);
  for (const [aba, r, c] of [['FICHA AMALDIÇOADA', 7, 4], ['INVOCAÇÕES', 21, 4]]) {
    const sh = A.ss.getSheetByName(aba), x = sh.cel(r, c, true), old = x.v; x.v = 'x'; delete x.f; A.reset();
    A.ctx.__e = { range: sh.getRange(r, c), source: A.ss, value: 'x', oldValue: old };
    vm.runInContext('onEdit(__e)', A.ctx);
    const alt = A.alteradas(); A.desfazer();
    let n = 0;
    for (const [k, v] of Object.entries(alt)) if (/^=HYPERLINK\(/.test(v.f)) { const [nome, rc] = k.split('!'); dump[nome].cells[rc] = Object.assign({}, dump[nome].cells[rc], { f: v.f }); n++; }
    ok(n >= 10, aba + ': saltos religados ' + n);
  }
}
const V = montar(velho, hv), N = montar(novo, sha(novo));

// O mapa do atalho: as células onde o script age. Mais uma amostra das livres, com semente fixa.
const box = {}; vm.createContext(box); vm.runInContext(fs.readFileSync(path.join(raiz, 'r53/atalho_livre.gs'), 'utf8'), box);
const mapa = vm.runInContext('R53_LIVRE_', box);
let s = 20261026; const rnd = n => { s = (s * 1103515245 + 12345) % 2147483648; return s % n; };
const casos = [];
for (const aba of Object.keys(mapa)) {
  const sh = V.ss.getSheetByName(aba), vistos = new Set();
  for (const [r1, c1, r2, c2] of mapa[aba]) for (let r = r1; r <= Math.min(r2, sh.rows); r++) for (let c = c1; c <= Math.min(c2, sh.cols); c++) {
    if (vistos.has(r + ',' + c)) continue; vistos.add(r + ',' + c);
    casos.push([aba, r, c]);
  }
  for (let k = 0; k < 60; k++) casos.push([aba, 1 + rnd(sh.rows), 1 + rnd(sh.cols)]);
}
const valores = ['texto', 3, ''];
let antes = 0, depois = 0, piores = [], caros = [];
for (const [i, [aba, r, c]] of casos.entries()) {
  const v = valores[i % 3];
  const a = editar(V, aba, r, c, v), b = editar(N, aba, r, c, v), onde = aba + ' ' + r + ',' + c + ' (' + JSON.stringify(v) + ')';
  eq(b.erro, a.erro, onde + ' erro');
  eq(b.grav, a.grav, onde + ' gravações');
  eq(b.alt, a.alt, onde + ' células');
  eq(b.props, a.props, onde + ' propriedades');
  ok(b.s <= a.s + 0.01, onde + ' ficou mais caro: ' + a.s + ' → ' + b.s);
  antes += a.s; depois += b.s;
  if (b.s >= 8) caros.push([b.s, onde, b.ops]);
  if (a.s - b.s >= 4) piores.push([a.s - b.s, onde, a.s, b.s, a.inteiras.join(','), b.inteiras.join(',')]);
}
piores.sort((x, y) => y[0] - x[0]);
const grupos = {};
for (const p of piores) { const k = p[1].split(' ').slice(0, -2).join(' ') + ' ' + p[4] + ' → ' + (p[5] || 'nenhuma'); (grupos[k] = grupos[k] || []).push(p); }
if (process.argv.includes('--ganho')) for (const [k, l] of Object.entries(grupos)) console.log(l.length + '×  ' + k + '  ex. ' + l[0][1] + ': ' + l[0][2] + ' → ' + l[0][3] + ' s');
if (process.argv.includes('--caros')) {
  const g = {}; for (const c of caros) { const k = c[1].split(' ').slice(0, -2).join(' ') + ' · ' + c[2].replace(/![A-Z]+\d+(:[A-Z]+\d+)?/g, '!_'); (g[k] = g[k] || []).push(c); }
  Object.entries(g).sort((x, y) => y[1][0][0] - x[1][0][0]).slice(0, 25).forEach(([k, l]) => console.log(l[0][0] + ' s  ' + l.length + '×  ex. ' + l[0][1] + '  ' + l[0][2].slice(0, 400)));
}
console.log('leituras_curtas: ' + checks + ' verificações, ' + casos.length + ' edições; custo modelado somado ' + Math.round(antes) + ' → ' + Math.round(depois) + ' s; módulo novo ' + sha(novo).slice(0, 8));
