'use strict';
// Atalho das células livres (26/10/2026). Sem a ficha exportada, confere só as peças puras (retângulos, referências,
// remendo do onEdit). Com ela (nuvem-b47/saidas/atalho/, fora do Git), roda o onEdit instalado inteiro, com e sem o
// atalho, e confere: célula livre sai sem ler a planilha nem abrir o módulo; célula do mapa faz exatamente o mesmo
// de antes; o mapa se desliga com outro módulo; Trilha e Caminho fazem a próxima edição sincronizar as Famílias.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
const { retangulos, referencias } = require('../atalho_livre');
const { preparar, ANTES, DEPOIS } = require('../diagnostico-android/preparar_atalho');
let checks = 0;
const ok = (c, m) => { assert(c, m); checks++; };
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };

// 1. Peças puras
eq(retangulos([[1, 1, 1, 1], [1, 2, 1, 2], [2, 1, 2, 1], [2, 2, 2, 2], [5, 3, 5, 3]]), [[1, 1, 2, 2], [5, 3, 5, 3]], 'retângulos juntam');
eq(retangulos([[1, 1, 1, 3], [2, 2, 2, 2]]), [[1, 1, 1, 3], [2, 2, 2, 2]], 'corridas diferentes não juntam');
const d = { A: {}, 'FICHA AMALDIÇOADA': {} };
eq(referencias('=IF(A1="X!B2",\'FICHA AMALDIÇOADA\'!$P$37&"",SUM(A2:B3))', 'A', d),
  [['A', 1, 1, 1, 1], ['FICHA AMALDIÇOADA', 37, 16, 37, 16], ['A', 2, 1, 3, 2]], 'referências fora das aspas');
const fixo = 'function r53OnEditOriginal_(e){' + ANTES + '}';
const gs = fs.readFileSync(path.join(raiz, 'r53/atalho_livre.gs'), 'utf8');
const um = preparar(fixo, gs);
ok(um.includes(DEPOIS) && um.includes('function r53EdicaoLivre_'), 'remendo aplicado');
eq(preparar(um, gs), um, 'reaplicar troca só o mapa');
assert.throws(() => preparar('function r53OnEditOriginal_(e){}', gs), /divergente/); checks++;

// 2. Integrado, com a ficha exportada
const pasta = path.join(raiz, 'nuvem-b47/saidas/atalho');
const fp = path.join(pasta, 'projeto-leve.json'), fd = path.join(pasta, 'oficial-era.json');
if (!fs.existsSync(fp) || !fs.existsSync(fd)) { console.log('atalho_livre: ' + checks + ' verificações (sem a ficha exportada, integrado pulado)'); process.exit(0); }
const { criar, projetoComIncremento, remendosDoProjeto } = require('../arnes_custo');
let projeto = JSON.parse(fs.readFileSync(fp, 'utf8'));
const dump = JSON.parse(fs.readFileSync(fd, 'utf8'));
// O mapa vale para um módulo só. A exportação é da cópia de teste (até o 22º remendo do pacote leve); se o mapa é do
// módulo com os remendos seguintes (26/10/2026), o projeto recebe esse módulo antes.
if (!projeto.files.find(f => f.name === 'Codigo').source.includes(/var R53_LIVRE_HASHES_=\["([0-9a-f]{64})"/.exec(gs)[1])) {
  const p = projetoComIncremento(projeto, dump, remendosDoProjeto(projeto));
  ok(gs.includes(p.hashNovo), 'mapa de outro módulo');
  projeto = p.projeto;
}
function montar(comAtalho, ajuste) {
  // salário já conferido no período: o fechamento em lote não lê nada nesta edição
  const A = criar(JSON.parse(JSON.stringify(dump)), { props: { salario_proximo: '99999' } });
  for (const f of projeto.files.filter(f => f.type !== 'JSON')) {
    let s = f.source;
    if (f.name === 'Codigo' && comAtalho) {
      // o módulo trocado pelo arnês fica no fim do Codigo, depois do atalho instalado que o preparar substitui
      const novo = /\nvar R53_CODIGO_NOVO_=[^\n]*;\n$/.exec(s);
      s = preparar(novo ? s.slice(0, novo.index) : s, ajuste ? ajuste(gs) : gs) + (novo ? novo[0] : '');
    }
    vm.runInContext(s + '\n', A.ctx, { filename: f.name });
  }
  vm.runInContext('(function(){var o=r53Modulo_;r53Modulo_=function(){__abriu();return o.apply(this,arguments);};r53Modulo_.toString=function(){return String(o);};})();', Object.assign(A.ctx, { __abriu: () => { aberturas++; A.log.push({ t: 'M' }); } }));
  return A;
}
// Cada gatilho é uma execução nova e reabriria o módulo: aqui ele fica aberto, e toda chamada ao r53Modulo_ conta.
function editar(A, aba, r, c, v) {
  const sh = A.ss.getSheetByName(aba), range = sh.getRange(r, c), old = sh.cel(r, c).v, x = sh.cel(r, c, true);
  // a edição anterior pode ter sido no salário, que apaga o próximo fechamento; aqui ele já foi conferido
  A.props.salario_proximo = '99999';
  x.v = v; delete x.f; A.reset();
  A.ctx.__e = { range, source: A.ss, value: v === '' ? undefined : v, oldValue: old === '' ? undefined : old };
  let erro = null; try { vm.runInContext('onEdit(__e)', A.ctx); } catch (err) { erro = err.message; }
  const log = A.log.filter(e => e.t !== 'L').map(e => [e.t, e.k || '', e.a || ''].join(' '));
  A.desfazer();
  return { log, erro };
}
let aberturas = 0;
const novo = montar(true), velho = montar(false);
const mapa = vm.runInContext('R53_LIVRE_', novo.ctx), delta = vm.runInContext('R53_LIVRE_DELTA_', novo.ctx);
const toca = (l, r, c) => l.some(a => r >= a[0] && r <= a[2] && c >= a[1] && c <= a[3]);
// semente fixa: a mesma amostra em toda rodada
let s = 20261026; const rnd = n => { s = (s * 1103515245 + 12345) % 2147483648; return s % n; };
let livres = 0, presas = 0;
for (const aba of Object.keys(mapa)) {
  const sh = novo.ss.getSheetByName(aba);
  for (let k = 0; k < 400; k++) {
    const r = 1 + rnd(sh.rows), c = 1 + rnd(sh.cols), v = ['texto', 7, ''][k % 3];
    const livre = !toca(mapa[aba], r, c);
    if (!livre && presas >= 900) continue;
    // as caixas de ± fazem o mesmo sem abrir o módulo: conferidas no caixas_delta.js
    if (aba === 'FICHA' && Object.prototype.hasOwnProperty.call(delta, novo.ss.getSheetByName(aba).getRange(r, c).getA1Notation())) continue;
    // a caixa do nível acerta a base do XP (lê a DADOS) sem abrir o módulo: conferida no fim daqui e no xp_nivel.js
    if (aba === 'FICHA' && r === 11 && c === 34) continue;
    const a = editar(novo, aba, r, c, v);
    if (livre) {
      livres++;
      ok(!a.erro, aba + ' ' + r + ',' + c + ' erro ' + a.erro);
      ok(!a.log.some(l => /^[RMW] /.test(l) || l === 'M  '), aba + ' ' + r + ',' + c + ' livre leu: ' + a.log.join(' | '));
    } else {
      presas++;
      const b = editar(velho, aba, r, c, v);
      // igual ao de antes, fora as marcas das Famílias
      const limpo = l => l.filter(x => !/r53_amparo_sujo/.test(x) && x !== 'M  ');
      // o módulo é chamado nas duas, com ou sem o atalho
      ok(a.log.includes('M  ') === b.log.includes('M  '), aba + ' ' + r + ',' + c + ' módulo');
      eq(limpo(a.log), limpo(b.log), aba + ' ' + r + ',' + c + ' mudou o que faz');
    }
  }
}
ok(livres > 600 && presas > 300, 'amostra pequena: ' + livres + ' livres, ' + presas + ' do mapa');

// 3. Outro módulo ou catálogo: desliga
const outro = montar(true, g => g.replace(/var R53_LIVRE_HASHES_=\["[0-9a-f]{64}"/, 'var R53_LIVRE_HASHES_=["' + '0'.repeat(64) + '"'));
const [lr, lc] = (() => { const sh = outro.ss.getSheetByName('CARTEIRA'); for (let r = 1; r <= sh.rows; r++) for (let c = 1; c <= sh.cols; c++) if (!toca(mapa.CARTEIRA, r, c)) return [r, c]; })();
ok(editar(outro, 'CARTEIRA', lr, lc, 'x').log.some(l => l.startsWith('R ')), 'hash diferente desliga o atalho');
ok(!editar(novo, 'CARTEIRA', lr, lc, 'x').log.some(l => l.startsWith('R ')), 'mesma célula com o hash certo');

// 4. A Trilha marca; a próxima edição nas quatro abas sincroniza e desmarca
const trilha = editar(novo, 'FICHA', 11, 14, 'Estocada');
ok(trilha.log.includes('P doc.set r53_amparo_sujo'), 'Trilha marca as Famílias');
const depois = editar(novo, 'CARTEIRA', lr, lc, 'x');
ok(depois.log.some(l => l.startsWith('R ') && /DADOS_R53_CATALOGO/.test(l)), 'com a marca, sincroniza: ' + depois.log.join(' | '));
ok(depois.log.includes('P doc.del r53_amparo_sujo'), 'e desmarca');
ok(!editar(novo, 'CARTEIRA', lr, lc, 'y').log.some(l => l.startsWith('R ')), 'desmarcado, volta o atalho');
// FICHA livre não depende da marca
editar(novo, 'FICHA', 11, 4, 'Vanguarda');
const fl = (() => { const sh = novo.ss.getSheetByName('FICHA'); for (let r = 200; r <= sh.rows; r++) for (let c = 1; c <= sh.cols; c++) if (!toca(mapa.FICHA, r, c)) return [r, c]; })();
ok(!editar(novo, 'FICHA', fl[0], fl[1], 'x').log.some(l => /^[RM] /.test(l)), 'FICHA livre segue sem ler com a marca');
// 5. O nível escrito na mão (27/10/2026): a exportação é de antes da base do XP, então ela entra aqui (CY54:CZ54)
const nivel = (A, v) => { const d = A.ss.getSheetByName('DADOS'); d.cel(54, 103, true).v = 'xp base'; d.cel(54, 104, true).v = 0;
  return editar(A, 'FICHA', 11, 34, v); };
const semBase = editar(novo, 'FICHA', 11, 34, 12);
ok(!semBase.erro && !semBase.log.some(l => /^W /.test(l)), 'ficha sem a base: nada gravado');
const n12 = nivel(novo, 12);
ok(!n12.erro && !n12.log.includes('M  '), 'nível escrito: sem erro e sem o módulo: ' + n12.erro);
eq(n12.log.filter(l => /^W /.test(l)).length, 1, 'uma gravação só: ' + n12.log.join(' | '));
ok(n12.log.some(l => /^W /.test(l) && /CZ54/.test(l)), 'nível escrito grava a base: ' + n12.log.join(' | '));
console.log('atalho_livre: ' + checks + ' verificações (' + livres + ' livres, ' + presas + ' do mapa)');
