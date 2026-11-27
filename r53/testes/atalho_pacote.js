'use strict';
// Etapa 6 da versão rápida (26/11/2026): o atalho das edições livres no pacote do repositório (r53/atalho_pacote.js).
// 1. Sem ficha: o onEdit do pacote chama o atalho só se ele existir; o AtalhoLivre.gs, se estiver no pacote, é do mesmo
//    módulo e catálogo (senão ele se desligaria calado) e está no manifesto.
// 2. Com a ficha exportada (nuvem-b47/saidas/atalho/pacote-ficha.json, fora do Git, gravada pelo atalho_pacote.js): roda
//    o onEdit do pacote inteiro, com e sem o atalho, e confere que a célula livre sai sem ler a planilha nem abrir o
//    módulo, e que a célula do mapa faz o mesmo de antes.
// Uso: node r53/testes/atalho_pacote.js (da raiz do repositório). Sem o pacote (r53/saidas/pacote-script), pula.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..'), pasta = path.join(raiz, 'r53/saidas/pacote-script');
let checks = 0;
const ok = (c, m) => { assert(c, m); checks++; };
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
if (!fs.existsSync(path.join(pasta, 'Codigo.gs'))) { console.log('atalho_pacote: sem o pacote (rode r53/empacotar_script.py), pulado'); process.exit(0); }
const ler = n => fs.readFileSync(path.join(pasta, n), 'utf8').replace(/\r\n/g, '\n');
const codigo = ler('Codigo.gs');

// 1. A chamada no onEdit: antes do Caminho e do editor, com typeof (o pacote sem o atalho segue como antes).
const onEdit = codigo.slice(codigo.indexOf('function onEdit(e){'), codigo.indexOf('\n', codigo.indexOf('function onEdit(e){')));
const iLivre = onEdit.indexOf('if(typeof r53EdicaoLivre_==="function"){if(r53EdicaoLivre_(e))');
ok(iLivre > 0, 'onEdit do pacote sem o atalho');
ok(iLivre < onEdit.indexOf('if(r53EditarCaminho_(e))return;'), 'o atalho tem de vir antes do Caminho');
ok(onEdit.indexOf('r53LivreConferido_(e)') > onEdit.indexOf('r53Editar_(e))return;'), 'o r53LivreConferido_ vem antes do editor');
ok(onEdit.indexOf('salarioEditar_(e)') < iLivre, 'o salário tem de vir antes do atalho');
const temAtalho = fs.existsSync(path.join(pasta, 'AtalhoLivre.gs'));
if (temAtalho) {
  const at = ler('AtalhoLivre.gs');
  const hashes = JSON.parse(/^var R53_LIVRE_HASHES_=(.*);$/m.exec(at)[1]);
  eq(hashes[0], /if\(hash!=='([0-9a-f]{64})'\)/.exec(codigo)[1], 'o atalho é de outro módulo: rode r53/atalho_pacote.js de novo');
  eq(hashes[1], /if\(hash!=="([0-9a-f]{64})"\)throw Error\("Editor: catálogo divergente"\)/.exec(ler('EditorR53.gs'))[1], 'o atalho é de outro catálogo');
  ok(JSON.parse(ler('manifesto.json')).arquivos['AtalhoLivre.gs'], 'o atalho fora do manifesto');
  ok(!at.includes('\r'), 'atalho gravado com \\r');
}

// 2. Integrado, com a ficha exportada.
const fd = path.join(raiz, 'nuvem-b47/saidas/atalho/pacote-ficha.json');
if (!temAtalho || !fs.existsSync(fd)) { console.log('atalho_pacote: ' + checks + ' verificações (sem o atalho ou a ficha exportada, integrado pulado)'); process.exit(0); }
const { criar } = require('../arnes_custo');
const dump = JSON.parse(fs.readFileSync(fd, 'utf8'));
const { projeto } = require('../atalho_pacote');
const arquivos = projeto(pasta).files;
let aberturas = 0;
function montar(comAtalho) {
  // A cópia já conferida uma vez (ANALISE marcada como desatualizada): a marca não grava de novo a cada edição.
  const A = criar(JSON.parse(JSON.stringify(dump)), { props: { analise_estado: 'desatualizada' } });
  for (const f of arquivos) vm.runInContext(f.source + '\n', A.ctx, { filename: f.name });
  if (comAtalho) vm.runInContext(ler('AtalhoLivre.gs') + '\n', A.ctx, { filename: 'AtalhoLivre' });
  vm.runInContext('(function(){var o=r53Modulo_;r53Modulo_=function(){__abriu();return o.apply(this,arguments);};r53Modulo_.toString=function(){return String(o);};})();',
    Object.assign(A.ctx, { __abriu: () => { aberturas++; A.log.push({ t: 'M' }); } }));
  return A;
}
function editar(A, aba, r, c, v) {
  const sh = A.ss.getSheetByName(aba), range = sh.getRange(r, c), old = sh.cel(r, c).v, x = sh.cel(r, c, true);
  x.v = v; delete x.f; A.reset();
  A.ctx.__e = { range, source: A.ss, value: v === '' ? undefined : v, oldValue: old === '' ? undefined : old };
  let erro = null; try { vm.runInContext('onEdit(__e)', A.ctx); } catch (err) { erro = err.message; }
  const log = A.log.filter(e => e.t !== 'L').map(e => [e.t, e.k || '', e.a || ''].join(' '));
  A.desfazer();
  return { log, erro };
}
const novo = montar(true), velho = montar(false);
const mapa = vm.runInContext('R53_LIVRE_', novo.ctx), delta = vm.runInContext('R53_LIVRE_DELTA_', novo.ctx);
const toca = (l, r, c) => l.some(a => r >= a[0] && r <= a[2] && c >= a[1] && c <= a[3]);
let s = 20261126; const rnd = n => { s = (s * 1103515245 + 12345) % 2147483648; return s % n; };
let livres = 0, presas = 0;
// O que muda com o atalho, fora o que ele faz de propósito: as marcas das Famílias e a abertura do módulo.
const limpo = l => l.filter(x => !/r53_amparo_sujo/.test(x) && x !== 'M  ');
for (const aba of Object.keys(mapa)) {
  const sh = novo.ss.getSheetByName(aba);
  for (let k = 0; k < 150; k++) {
    const r = 1 + rnd(sh.rows), c = 1 + rnd(sh.cols), v = ['texto', 7, ''][k % 3];
    const livre = !toca(mapa[aba], r, c);
    if (!livre && presas >= 300) continue;
    if (aba === 'FICHA' && Object.prototype.hasOwnProperty.call(delta, sh.getRange(r, c).getA1Notation())) continue;
    if (aba === 'FICHA' && r === 11 && (c === 34 || c >= 40 && c <= 46)) continue; // nível e XP: atalho próprio
    const a = editar(novo, aba, r, c, v);
    if (livre) {
      livres++;
      ok(!a.erro, aba + ' ' + r + ',' + c + ' erro ' + a.erro);
      ok(!a.log.some(l => /^[RMW] /.test(l) || l === 'M  '), aba + ' ' + r + ',' + c + ' livre leu: ' + a.log.join(' | '));
    } else {
      presas++;
      const b = editar(velho, aba, r, c, v);
      eq(limpo(a.log), limpo(b.log), aba + ' ' + r + ',' + c + ' mudou o que faz');
    }
  }
}
ok(livres > 300 && presas > 100, 'amostra pequena: ' + livres + ' livres, ' + presas + ' do mapa');
// O ± da vida (FICHA): o atalho faz a conta sem abrir o módulo, e a vida fica igual à de antes.
for (const [cd, x] of Object.entries(delta)) {
  const nova = montar(true), antiga = montar(false), conta = A => {
    const f = A.ss.getSheetByName('FICHA'), put = (a1, v) => { const p = f.getRange(a1); const c = f.cel(p.getRow(), p.getColumn(), true); c.v = v; delete c.f; };
    put(x.a, 20); put(x.m, 20); if (x.t) put(x.t, 0); put(cd, -3); aberturas = 0; A.reset();
    A.ctx.__e = { range: f.getRange(cd), source: A.ss, value: '-3' };
    vm.runInContext('onEdit(__e)', A.ctx);
    return { atual: f.cel(f.getRange(x.a).getRow(), f.getRange(x.a).getColumn()).v, abriu: aberturas };
  };
  const n = conta(nova), o = conta(antiga);
  eq(n.atual, o.atual, 'o ± de ' + cd + ' deu outra conta');
  eq(n.abriu, 0, 'o ± de ' + cd + ' abriu o módulo');
}
console.log('atalho_pacote: ' + checks + ' verificações (' + livres + ' livres, ' + presas + ' do mapa, ' + Object.keys(delta).length + ' caixas de ±)');
