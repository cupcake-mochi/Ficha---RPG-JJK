'use strict';
// Caixas que esticam na CONFIGURAÇÃO (26/10/2026, remendos 34 e 35): escrever numa caixa só refaz as linhas dela e as
// das caixas que dividem linha com essas, em cadeia. Com a ficha exportada (nuvem-b47/saidas/atalho/, fora do Git),
// escreve um texto longo e depois apaga, em cada uma das caixas da aba, com o módulo de antes (até o 33º) e o de
// depois, e confere: as mesmas células; toda altura que o novo grava é a que o antigo grava; e toda linha que o novo
// deixa de gravar fica com a altura de partida, a que o antigo gravaria sem mudança de texto. Também com um texto
// longo já na caixa vizinha, para as linhas divididas.
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const ok = (c, m) => { assert(c, m); checks++; };
const pasta = path.join(raiz, 'nuvem-b47/saidas/atalho');
const fp = path.join(pasta, 'projeto-leve.json'), fd = path.join(pasta, 'oficial-era.json');
if (!fs.existsSync(fp) || !fs.existsSync(fd)) { console.log('caixas_horizontais: sem a ficha exportada, pulado'); process.exit(0); }
const { criar, custo, projetoComIncremento, remendosDoProjeto } = require('../arnes_custo');
const projeto = JSON.parse(fs.readFileSync(fp, 'utf8')), dump = JSON.parse(fs.readFileSync(fd, 'utf8'));
// Compara módulos montados a partir do 22º remendo: só roda com a exportação da cópia de teste de 25/10.
if (remendosDoProjeto(projeto) !== 22) { console.log('caixas_horizontais: a exportação está noutro módulo (' + remendosDoProjeto(projeto) + 'º remendo), pulado'); process.exit(0); }
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const { novo: antigo, hashVelho: hv } = projetoComIncremento(projeto, dump, 22, 33);
const { novo } = projetoComIncremento(projeto, dump, 22);
ok(antigo !== novo, 'o 34º e o 35º mudam o módulo');

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
// as alturas que a edição gravou: {linha: altura}
function editar(A, a1, v, preparo) {
  const sh = A.ss.getSheetByName('CONFIGURAÇÃO'), rg = sh.getRange(a1), r = rg.getRow(), c = rg.getColumn();
  const guardados = (preparo || []).map(([b, t]) => { const x = sh.cel(sh.getRange(b).getRow(), sh.getRange(b).getColumn(), true), o = x.v; x.v = t; return [x, o]; });
  const x = sh.cel(r, c, true), old = x.v; x.v = v; delete x.f; A.reset();
  A.ctx.__e = { range: sh.getRange(r, c), source: A.ss, value: v === '' ? undefined : v, oldValue: old === '' ? undefined : old };
  let erro = null; try { vm.runInContext('onEdit(__e)', A.ctx); } catch (err) { erro = err.message; }
  const h = {};
  A.log.filter(e => e.t === 'W' && e.k === 'alturas' && e.a === 'CONFIGURAÇÃO').forEach(e => { const [l, n, alt] = JSON.parse(e.x); for (let k = 0; k < n; k++) h[l + k] = alt; });
  const conteudo = JSON.stringify(A.alteradas()), k = custo(A.log);
  A.desfazer(); x.v = old; guardados.reverse().forEach(([y, o]) => { y.v = o; });
  return { erro, h, conteudo, s: k.s, leituras: A.log.filter(e => e.t === 'R').reduce((n, e) => n + e.n, 0) };
}
const V = montar(antigo), N = montar(novo);
const est = vm.runInContext('R53_MODULO_.__estado()', V.ctx);
const grupo = est.abas.filter(s => s.nome === 'CONFIGURAÇÃO')[0].esticam;
ok(grupo.length >= 1, 'grupos da CONFIGURAÇÃO');
const caixas = [].concat(...grupo.map(g => g.textos));
const longo = 'Teste de medição: golpe que concentra energia amaldiçoada no punho, causa dano extra e empurra o alvo três metros; uma vez por cena, pode repetir o ataque se errar. '.repeat(3);
let sa = 0, sn = 0, la = 0, ln = 0, n = 0;
caixas.forEach((c, i) => {
  const a1 = c[1][0], sh = V.ss.getSheetByName('CONFIGURAÇÃO'), rg = sh.getRange(a1), atual = sh.cel(rg.getRow(), rg.getColumn()).v;
  // a vizinha: a próxima caixa que divide a primeira linha, com texto longo antes da edição
  const viz = caixas.find(d => d !== c && d[2] <= c[2] && d[2] + d[3] > c[2]);
  const cenarios = [[longo, null], ['', null]];
  if (viz && i % 4 === 0) cenarios.push(['', [[viz[1][0], longo]]], [longo, [[viz[1][0], longo]]]);
  for (const [v, prep] of cenarios) {
    const base = editar(V, a1, atual, prep), a = editar(V, a1, v, prep), b = editar(N, a1, v, prep), onde = a1 + ' ' + JSON.stringify(v.slice(0, 10)) + (prep ? ' com vizinha' : '');
    eq(b.erro, a.erro, onde + ' erro');
    eq(b.conteudo, a.conteudo, onde + ' células');
    for (const l of Object.keys(b.h)) eq(b.h[l], a.h[l], onde + ' altura gravada da linha ' + l);
    for (const l of Object.keys(a.h)) if (!(l in b.h)) eq(a.h[l], base.h[l], onde + ' linha ' + l + ' que o novo não grava');
    ok(b.s <= a.s + 0.01, onde + ' ficou mais caro: ' + a.s + ' → ' + b.s);
    sa += a.s; sn += b.s; la += a.leituras; ln += b.leituras; n++;
  }
});
console.log('caixas_horizontais: ' + checks + ' verificações, ' + caixas.length + ' caixas, ' + n + ' edições; custo modelado somado ' +
  Math.round(sa) + ' → ' + Math.round(sn) + ' s; células lidas ' + la + ' → ' + ln + '; módulo novo ' + sha(novo).slice(0, 8));
