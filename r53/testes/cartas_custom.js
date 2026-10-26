'use strict';
// Cartas das habilidades custom (26/10/2026, remendos 36 e 37): numa edição nos textos e nomes das habilidades por
// nível da CONFIGURAÇÃO (AK50:AX64), do lado cujo custom a FICHA não usa (DADOS_PROGRESSAO!K7 para o Caminho, K8 para
// a Trilha, em 0), as cartas não são refeitas. Com a ficha exportada (nuvem-b47/saidas/atalho/, fora do Git), edita
// cada célula dessa faixa e uma borda em volta, com as quatro combinações das marcas, pelo módulo até o 35º e pelo
// novo, e confere as mesmas células (valores, fórmulas, notas) e o mesmo resto das gravações; e que o novo não custa
// mais e, com a marca do lado em 0, não lê a FICHA.
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const ok = (c, m) => { assert(c, m); checks++; };
const pasta = path.join(raiz, 'nuvem-b47/saidas/atalho');
const fp = path.join(pasta, 'projeto-leve.json'), fd = path.join(pasta, 'oficial-era.json');
if (!fs.existsSync(fp) || !fs.existsSync(fd)) { console.log('cartas_custom: sem a ficha exportada, pulado'); process.exit(0); }
const { criar, custo, projetoComIncremento } = require('../arnes_custo');
const projeto = JSON.parse(fs.readFileSync(fp, 'utf8')), dump = JSON.parse(fs.readFileSync(fd, 'utf8'));
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const { novo: antigo, hashVelho: hv } = projetoComIncremento(projeto, dump, 22, 35);
const { novo } = projetoComIncremento(projeto, dump, 22);
ok(antigo !== novo, 'o 36º e o 37º mudam o módulo');

function montar(modulo) {
  const A = criar(JSON.parse(JSON.stringify(dump)), { props: { salario_proximo: '99999' } });
  A.ctx.__codigo = modulo;
  for (const f of projeto.files.filter(f => f.type !== 'JSON')) {
    let s = f.source;
    if (f.name === 'Codigo') s = s.replace(/var code=Utilities\.ungzip\([^\n]*\.getDataAsString\('UTF-8'\);/, () => 'var code=__codigo;').replace(hv, sha(modulo));
    vm.runInContext(s + '\n', A.ctx, { filename: f.name });
  }
  vm.runInContext('r53Modulo_()', A.ctx);
  return A;
}
function editar(A, r, c, v, k7, k8) {
  const p = A.ss.getSheetByName('DADOS_PROGRESSAO'), m7 = p.cel(7, 11, true), m8 = p.cel(8, 11, true), o7 = m7.v, o8 = m8.v;
  m7.v = k7; m8.v = k8;
  const sh = A.ss.getSheetByName('CONFIGURAÇÃO'), x = sh.cel(r, c, true), old = x.v, oldf = x.f; x.v = v; delete x.f; A.reset();
  A.ctx.__e = { range: sh.getRange(r, c), source: A.ss, value: v === '' ? undefined : v, oldValue: old === '' ? undefined : old };
  let erro = null; try { vm.runInContext('onEdit(__e)', A.ctx); } catch (err) { erro = err.message; }
  const conteudo = /^(lista\.)?(valores|valor|fórmula|fórmulas|nota|notas|rico|limpar|setValue|setFormula|setNote|check|uncheck|clearContent)$/;
  const grav = A.log.filter(e => e.t === 'W' && !conteudo.test(e.k)).map(e => [e.k, e.a || '', e.x || ''].join(' '));
  const alt = JSON.stringify(A.alteradas()), s = custo(A.log).s, ficha = A.log.some(e => e.t === 'R' && /^FICHA!/.test(e.a || ''));
  A.desfazer(); x.v = old; if (oldf) x.f = oldf; m7.v = o7; m8.v = o8;
  return { erro, grav, alt, s, ficha };
}
const V = montar(antigo), N = montar(novo);
let n = 0, sa = 0, sn = 0, pulos = 0;
for (let r = 48; r <= 66; r++) for (let c = 35; c <= 52; c++) for (const [k7, k8] of [[0, 0], [1, 0], [0, 1], [1, 1]]) {
  const v = (r + c) % 2 ? 'Texto de teste da habilidade custom, longo o bastante para pedir mais de uma linha na caixa.' : '';
  const a = editar(V, r, c, v, k7, k8), b = editar(N, r, c, v, k7, k8), onde = 'CONFIGURAÇÃO ' + r + ',' + c + ' K7=' + k7 + ' K8=' + k8;
  eq(b.erro, a.erro, onde + ' erro');
  eq(b.alt, a.alt, onde + ' células');
  eq(b.grav, a.grav, onde + ' gravações');
  ok(b.s <= a.s + 0.01, onde + ' ficou mais caro: ' + a.s + ' → ' + b.s);
  const dentro = r >= 50 && r <= 64 && c >= 37 && c <= 50, semUso = (c <= 44 ? k7 : k8) !== 1;
  if (dentro && semUso && a.ficha) { ok(!b.ficha, onde + ' leu a FICHA'); pulos++; }
  if (!dentro || !semUso) eq(b.ficha, a.ficha, onde + ' leitura da FICHA');
  sa += a.s; sn += b.s; n++;
}
ok(pulos > 100, 'casos em que as cartas deixam de ser refeitas: ' + pulos);
console.log('cartas_custom: ' + checks + ' verificações, ' + n + ' edições (' + pulos + ' sem refazer as cartas); custo modelado somado ' +
  Math.round(sa) + ' → ' + Math.round(sn) + ' s; módulo novo ' + sha(novo).slice(0, 8));
