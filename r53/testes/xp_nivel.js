'use strict';
// O nível escrito na mão (27/10/2026). Com o nível 10 escrito e 250 de XP, a caixa de falta pedia 4.150 (o acumulado do
// 11 menos o XP, que contava do zero) em vez dos 450 que faltam do 10 para o 11. Agora o XP total da DADOS soma uma base
// (CZ54), e o atalho acerta a base quando alguém escreve o nível: subindo, o XP vai para o acumulado do nível novo;
// descendo, guarda a mesma fração do caminho até o próximo. Confere a conta em todos os pares de nível, a caixa da
// DADOS que o gerador escreve e o atalho com uma planilha de mentira.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
const { NIVEL } = require('../atalho_livre');
let checks = 0;
const ok = (c, m) => { assert(c, m); checks++; };
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };

// 1. O Ficha.gs gerado: a base na DADOS e o XP total somando ela; a curva onde o atalho lê
const inteiro = fs.readFileSync(path.join(raiz, 'apps-script/Ficha.gs'), 'utf8');
const ini = inteiro.indexOf('"nome":"DADOS"'), fim = inteiro.indexOf('"nome":"DADOS_AM"');
ok(ini > 0 && fim > ini, 'a aba DADOS no Ficha.gs');
const ficha = inteiro.slice(ini, fim);
const celula = (l, c) => { const m = new RegExp('\\[' + l + ',' + c + ',("(?:[^"\\\\]|\\\\.)*"|-?[\\d.]+),\\d+\\]').exec(ficha); return m ? JSON.parse(m[1]) : undefined; };
eq(celula(47, 103), 'xp total', 'CY47');
ok(String(celula(47, 104)).endsWith('+N(DADOS!$CZ$54)'), 'o XP total soma a base: ' + celula(47, 104));
eq(celula(54, 103), 'xp base', 'CY54');
eq(celula(54, 104), 0, 'a base nasce zero');
eq([celula(4, 43), celula(4, 44)], ['nível', 'xp acumulado'], 'cabeçalho da curva');
// a curva é conta da DADOS_CONFIG (a campanha pode trocar); os valores vêm da oficial exportada, ou da curva do livro
ok([5, 33].every(l => celula(l, 43) === l - 3 && /^=DADOS_CONFIG!\$Z\$\d+$/.test(celula(l, 44))), 'curva do 2 ao 30 na DADOS');
const fd = path.join(raiz, 'nuvem-b47/saidas/atalho/oficial-era.json');
const LIVRO = [0, 200, 500, 800, 1300, 1800, 2300, 3000, 3700, 4400, 5300, 6200, 7100, 8200, 9300, 10400, 11700, 13000,
  14300, 15800, 17300, 18800, 20500, 22200, 23900, 25600, 27300, 29000, 30700];
let curva = LIVRO.map((x, i) => [i + 2, x]);
if (fs.existsSync(fd)) {
  const c = JSON.parse(fs.readFileSync(fd, 'utf8')).DADOS.cells;
  const exportada = [];
  for (let l = 5; l <= 33; l++) exportada.push([Number(c[l + ',43'].v), Number(c[l + ',44'].v)]);
  eq(exportada, curva, 'a curva da oficial é a do livro');
  curva = exportada;
}
const dvFicha = /"dv":(\[\[.*?\]\]),\n/.exec(inteiro.slice(inteiro.indexOf('"nome":"FICHA"'), inteiro.indexOf('"nome":"FICHA AMALDIÇOADA"')));
const menuNivel = JSON.parse(dvFicha[1]).filter(d => d[0] === 'AH11');
eq(menuNivel, [['AH11', '"' + Array.from({ length: 30 }, (_, i) => i + 1).join(',') + '"']], 'o NÍVEL é menu de 1 a 30');
ok(/"menus_estritos":\[[^\]]*"AH11"/.test(inteiro.slice(inteiro.indexOf('"nome":"FICHA"'), inteiro.indexOf('"nome":"FICHA AMALDIÇOADA"'))), 'e estrito');
eq(NIVEL, { nivel: 'AH11', contas: 'CY47:CZ54', base: 7, celula: 'CZ54', curva: 'AQ5:AR33' }, 'endereços do atalho');

// 2. A conta, no atalho gerado
const gs = fs.readFileSync(path.join(raiz, 'r53/atalho_livre.gs'), 'utf8');
const ctx = { console, PropertiesService: { getDocumentProperties: () => ({ deleteProperty() {}, getProperty() { return null; } }) } };
vm.createContext(ctx); vm.runInContext(gs, ctx);
const alvo = (t, n, o) => ctx.r53LivreNivelAlvo_(curva, t, n, o);
const acum = k => k < 2 ? 0 : (curva.find(l => l[0] === k) || [])[1];
eq(alvo(0, 10, 1), 3700, 'escreveu 10 sem XP: começo do 10');
eq(alvo(0, 10, 0), 3700, 'sem nível antes: começo do 10');
eq(4400 - (3700 + 250), 450, 'o caso do Mizuki: falta 450 com uma missão de 250');
eq(alvo(3950, 8, 10), 2300 + Math.floor((250 / 700) * 700), 'desceu do 10 com 250 de 700: a mesma fração do 8');
eq(alvo(4050, 9, 10), 3000 + Math.floor((350 / 700) * 700), 'metade do 10 vira metade do 9');
eq(alvo(3800, 10, 9), null, 'o XP já cabe no 10: nada');
eq(alvo(5000, 10, 9), null, 'subiu, e o XP passa do 11 (o feito segurou o nível): o XP fica');
eq(alvo(3950, 1, 10), 0, 'descer até o 1 zera');
eq(alvo(0, 30, 1), 30700, 'o 30 é o topo');
eq(alvo(0, 31, 30), null, 'fora da curva: nada');
let pares = 0;
for (let o = 0; o <= 30; o++) for (let n = 1; n <= 30; n++) for (const t of [0, 1, 199, 250, 3700, 3950, 4399, 14300, 15000, 30700, 40000]) {
  if (o === n) continue;
  const a = alvo(t, n, o), fim = a === null ? t : a, an = acum(n), prox = n < 30 ? acum(n + 1) : null;
  ok(Number.isInteger(fim) && fim >= 0, 'XP inteiro e sem sinal');
  if (prox !== null && prox > an && (a !== null || o > n || t < an)) ok(fim >= an && fim < prox, `o ${o}→${n} com ${t}: ${fim} fora do nível`);
  if (a === null) ok((t >= an && (prox === null || t < prox)) || (o <= n && t >= an), `o ${o}→${n} com ${t}: devia acertar`);
  if (o > n && t >= acum(o) && o < 30 && prox !== null && prox > an) {
    const span = acum(o + 1) - acum(o), feito = Math.min(t - acum(o), span);
    const k = fim - an, alvo = feito * (prox - an);
    ok(k * span <= alvo && (alvo < (k + 1) * span || fim === prox - 1), `o ${o}→${n} com ${t}: ${feito}/${span} virou ${k}/${prox - an}`);
  }
  pares++;
}

// 3. O atalho numa planilha de mentira
function planilha(o) {
  const dados = { CY47: 'xp total', CZ47: o.total, CY54: o.rotulo === undefined ? 'xp base' : o.rotulo, CZ54: o.base || 0 };
  const grav = [];
  const linhas = a => { const m = /^([A-Z]+)(\d+):([A-Z]+)(\d+)$/.exec(a); return [m[1], +m[2], m[3], +m[4]]; };
  const DADOS = {
    getRange(a) {
      if (a === NIVEL.curva) return { getValues: () => curva.map(l => l.slice()) };
      if (a === NIVEL.contas) { const [, l1, , l2] = linhas(a); const v = []; for (let l = l1; l <= l2; l++) v.push([dados['CY' + l] ?? '', dados['CZ' + l] ?? '']); return { getValues: () => v }; }
      if (a === NIVEL.celula) return { setValue(x) { grav.push([a, x]); } };
      throw Error('leitura fora do esperado: ' + a);
    },
  };
  const ss = { getSheetByName: n => n === 'DADOS' ? DADOS : null };
  const col = o.celula === 'AH12' ? [12, 34] : [11, 34];
  const range = { getRow: () => col[0], getLastRow: () => col[0], getColumn: () => col[1], getLastColumn: () => col[1],
    getA1Notation: () => o.celula || 'AH11', getSheet: () => ({ getName: () => 'FICHA', getParent: () => ss }) };
  return { e: { source: ss, range, value: o.valor, oldValue: o.antes }, grav };
}
const roda = o => { const p = planilha(o); ctx.r53LivreNivel_(p.e); return p.grav; };
eq(roda({ total: 0, valor: '10', antes: '1' }), [['CZ54', 3700]], 'o nível 10 escrito: base 3.700');
eq(roda({ total: 3950, base: 3700, valor: '8', antes: '10' }), [['CZ54', 3700 + 2550 - 3950]], 'desceu: a base acompanha');
eq(roda({ total: 3800, valor: '10', antes: '9' }), [], 'já cabe: não grava');
eq(roda({ total: 0, valor: '10', antes: '1', rotulo: '' }), [], 'ficha sem a base: não grava');
eq(roda({ total: 0, valor: '', antes: '10' }), [], 'apagou o nível: nada');
eq(roda({ total: 0, valor: 'dez', antes: '1' }), [], 'texto: nada');
eq(roda({ total: 0, valor: '10.5', antes: '1' }), [], 'quebrado: nada');
eq(roda({ total: 3950, valor: '0', antes: '10' }), [], 'zero: nada');
eq(roda({ total: 3950, valor: '-3', antes: '10' }), [], 'negativo: nada');
eq(roda({ total: 3950, valor: '31', antes: '10' }), [], 'acima do 30: nada');
eq(roda({ total: 3950, valor: '8', antes: 'dez' }), [], 'antes inválido conta como subir, e o XP já passa do 8: fica');
eq(roda({ total: 0, valor: '10' }), [['CZ54', 3700]], 'sem o valor de antes: como subir');
// pelo r53EdicaoLivre_: a caixa do nível acerta a base e o resto segue como antes
const p = planilha({ total: 0, valor: '10', antes: '1' });
ctx.r53EdicaoLivre_(p.e);
eq(p.grav, [['CZ54', 3700]], 'r53EdicaoLivre_ chama o acerto');
const q = planilha({ total: 0, valor: '10', antes: '1', celula: 'AH12' });
ctx.r53EdicaoLivre_(q.e);
eq(q.grav, [], 'outra célula da FICHA não mexe na base');

console.log(`xp_nivel: ${checks} verificações (${pares} combinações de nível e XP)`);
