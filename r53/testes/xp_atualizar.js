'use strict';
// O XP digitado em cima da caixa de XP da FICHA (27/10/2026). Um Sheets de mentira (missoes_ambiente.js) em que o XP de
// cada caixa sai do tipo e o XP total é a soma mais a base da DADOS, recalculados a cada leitura. Roda o atalho
// (r53LivreXp_, do atalho_livre.gs gerado) e as edições do painel (salarioIntegrarMissao_ do Salarios.gs) em sequência:
// missões, XP atualizado, missão antiga corrigida e apagada, missões novas em caixa vazia e em caixa reaproveitada,
// XP para baixo, a trava do feito, valores inválidos e a ficha sem a base. Confere o XP total, o nível e as marcas.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const { ambiente } = require('./missoes_ambiente');
const { r53LivreXpNivel_, r53LivreXpNota_ } = require('../atalho_livre');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const raiz = path.resolve(__dirname, '..', '..');
const salarios = fs.readFileSync(path.join(raiz, 'apps-script/Salarios.gs'), 'utf8');
const atalho = fs.readFileSync(path.join(raiz, 'r53/atalho_livre.gs'), 'utf8');
const TIPOS = { 'Curta': 50, 'Padrão': 100, 'Longa': 200, 'Final de arco': 400, 'Solo simples': 75, 'Solo complexa': 150 };
const COLS = [49, 55, 61, 67], FORMULA = '=DADOS!$CZ$47';

// ---------- 1. As peças soltas ----------
// A curva da Era exportada (DADOS!AQ5:AR33): do nível 2 (0 de XP) ao 30.
const ACUM = [0, 200, 500, 800, 1300, 1800, 2300, 3000, 3700, 4400, 5300, 6200, 7100, 8200, 9300, 10400, 11700, 13000, 14300,
  15800, 17300, 18800, 20500, 22200, 23900, 25600, 27300, 29000, 30700];
const curva = ACUM.map((x, i) => [i + 2, x]);
eq(r53LivreXpNivel_(curva, 0, 1, 20), 2, 'como a subida pelas missões: 0 de XP já é o 2');
eq(r53LivreXpNivel_(curva, 1000, 3, 20), 5); eq(r53LivreXpNivel_(curva, 3699, 15, 20), 9); eq(r53LivreXpNivel_(curva, 3700, 15, 20), 10);
eq(r53LivreXpNivel_(curva, 99999, 5, 20), 20, 'trava do feito'); eq(r53LivreXpNivel_(curva, 99999, 21, 20), 30, 'feito já passado');
eq(r53LivreXpNivel_(curva, 9300, 25, 20), 16, 'desce mesmo acima do limiar'); eq(r53LivreXpNivel_(curva, 99999, 5, 0), 30, 'sem limiar');
eq(r53LivreXpNivel_([[1, 0], [2, 100]], 50, 1, 20), 1); eq(r53LivreXpNivel_([[2, 100]], 50, 1, 20), 1, 'abaixo da primeira linha');
eq(r53LivreXpNota_('', '[XP congelado: 50]'), '[XP congelado: 50]');
eq(r53LivreXpNota_('obs\n[Salário: id1 · 01/01/2026]', '[XP congelado: 50 · id1]'), 'obs\n[XP congelado: 50 · id1]\n[Salário: id1 · 01/01/2026]');
// A nota só com a marca do salário começa com quebra (salarioSincronizar_); a marca nova entra no lugar dela, e o
// salário, ao regravar, chega ao mesmo texto (semMarca + quebra + marca): a nota não fica mudando.
eq(r53LivreXpNota_('\n[Salário: id1 · 01/01/2026]', '[XP congelado: 9]'), '[XP congelado: 9]\n[Salário: id1 · 01/01/2026]');
eq(r53LivreXpNota_('obs\n[XP congelado: 50 · id1]\n[Salário: id1 · x]', '[XP congelado: 70 · id1]'), 'obs\n[XP congelado: 70 · id1]\n[Salário: id1 · x]');
eq(r53LivreXpNota_('obs\n[XP congelado: 50 · id1]\n[Salário: id1 · x]', ''), 'obs\n[Salário: id1 · x]');
eq(r53LivreXpNota_('[XP congelado: 50]', ''), '');

// ---------- 2. A ficha de mentira ----------
function ficha(opcoes) {
  opcoes = opcoes || {};
  const a = ambiente(salarios, { espelhos: true, xp: 0, nivel: 1, limiar: 20, painel: [], registros: [] });
  vm.runInContext(atalho, a.ctx);
  const P = a.abas['FICHA PESSOAL'].cells, D = a.abas.DADOS.cells, F = a.abas.FICHA.cells;
  if (!opcoes.semBase) { D.set('54,103', 'xp base'); D.set('54,104', 0); }
  for (let r = 5; r <= 34; r++) { D.delete(r + ',43'); D.delete(r + ',44'); }
  curva.forEach(([n, x], i) => { D.set((5 + i) + ',43', n); D.set((5 + i) + ',44', x); });
  const acum = n => n < 2 ? 0 : ACUM[n - 2];
  F.set('11,40', FORMULA);
  function recalcular() {
    let soma = 0;
    for (const c of COLS) for (let l = 15; l <= 87; l++) {
      const xp = TIPOS[String(P.get(l + ',' + (c + 1)) || '').trim()];
      P.set(l + ',' + (c + 4), xp === undefined ? '' : xp); soma += xp || 0;
    }
    const total = soma + (Number(D.get('54,104')) || 0), nivel = Number(F.get('11,34')) || 0;
    D.set('47,104', total); D.set('48,104', nivel); P.set('11,49', total);
    P.set('11,55', nivel >= 30 ? '—' : Math.max(0, acum(nivel + 1) - total));
  }
  const proto = Object.getPrototypeOf(a.abas.DADOS.getRange(1, 1));
  for (const k of ['getValues', 'getValue', 'getNotes']) { const f = proto[k]; proto[k] = function () { recalcular(); return f.apply(this, arguments); }; }
  recalcular();
  const ss = { getSheetByName: n => a.abas[n] || null };
  function missao(a1, valor) {
    const m = /^([A-Z]+)(\d+)$/.exec(a1), col = Array.from(m[1]).reduce((n, ch) => n * 26 + ch.charCodeAt(0) - 64, 0);
    P.set(m[2] + ',' + col, valor);
    const e = { source: ss, range: a.abas['FICHA PESSOAL'].getRange(+m[2], col), value: valor === '' ? undefined : valor };
    assert.strictEqual(a.ctx.salarioIntegrarMissao_(e, () => { throw Error('o módulo não devia abrir'); }), true);
    recalcular();
  }
  function xp(valor) {
    F.set('11,40', valor);
    const e = { source: ss, range: a.abas.FICHA.getRange(11, 40), value: valor === '' ? undefined : String(valor) };
    const r = a.ctx.r53LivreXp_(e); recalcular(); return r;
  }
  const leia = {
    total: () => { recalcular(); return D.get('47,104'); }, nivel: () => F.get('11,34'), base: () => D.get('54,104'),
    nota: a1 => { const m = /^([A-Z]+)(\d+)$/.exec(a1), col = Array.from(m[1]).reduce((n, ch) => n * 26 + ch.charCodeAt(0) - 64, 0); return a.abas['FICHA PESSOAL'].notes.get(m[2] + ',' + col) || ''; },
    caixa: () => F.get('11,40')
  };
  return { a, missao, xp, leia, F, D, P };
}
const marca = s => (/\[XP congelado: ([^\]]*)\]/.exec(s) || [])[1] || null;
const idDe = s => (/\[Salário: ([^\] ·]+) · /.exec(s) || [])[1] || null;

// ---------- 3. A sequência ----------
{
  const f = ficha(), L = f.leia;
  f.missao('AW15', 'Missão A'); f.missao('AX15', 'Curta'); f.missao('BC15', 'Missão B'); f.missao('BD15', 'Longa');
  eq(L.total(), 250); eq(L.nivel(), 3, 'as missões sobem o nível como sempre');
  const idA = idDe(L.nota('AW15')), idB = idDe(L.nota('BC15')); assert(idA && idB); checks++;

  // Atualizar para 1000: a base fica 750, as duas congeladas, o nível vai a 5, a conta volta.
  eq(f.xp(1000), true); eq(L.total(), 1000); eq(L.base(), 750); eq(L.nivel(), 5); eq(L.caixa(), FORMULA);
  eq(marca(L.nota('AW15')), '50 · ' + idA); eq(marca(L.nota('BC15')), '200 · ' + idB);
  eq(idDe(L.nota('AW15')), idA, 'a marca do salário continua');
  eq(L.nota('AW15').indexOf('[XP congelado') < L.nota('AW15').indexOf('[Salário'), true, 'congelado antes do salário');

  // Missão antiga corrigida (Curta → Longa): o total não mexe; a marca acompanha.
  f.missao('AX15', 'Longa'); eq(L.total(), 1000); eq(marca(L.nota('AW15')), '200 · ' + idA);
  f.missao('AW15', 'Missão A corrigida'); eq(L.total(), 1000); eq(idDe(L.nota('AW15')), idA, 'corrigir o nome conserva o id');

  // Missão antiga apagada, nome primeiro e tipo depois: o total não mexe em nenhum passo; a marca sai no fim.
  f.missao('BC15', ''); eq(L.total(), 1000); eq(marca(L.nota('BC15')), '200 · ' + idB, 'sem nome, ainda congelada');
  f.missao('BD15', ''); eq(L.total(), 1000); eq(marca(L.nota('BC15')), null); eq(L.nota('BC15'), '');

  // Missão nova em caixa vazia e na caixa que ficou livre: somam por cima.
  f.missao('BI15', 'Missão C'); f.missao('BJ15', 'Padrão'); eq(L.total(), 1100); eq(marca(L.nota('BI15')), null);
  f.missao('BC15', 'Missão D'); f.missao('BD15', 'Curta'); eq(L.total(), 1150); eq(L.nivel(), 5);

  // Caixa congelada reaproveitada sem apagar o tipo: apagar o nome segura o total; o nome novo conta a missão inteira.
  f.missao('AW15', ''); eq(L.total(), 1150);
  f.missao('AW15', 'Missão E'); eq(L.total(), 1350); eq(L.nivel(), 6, 'missão nova sobe o nível'); eq(marca(L.nota('AW15')), null); assert(idDe(L.nota('AW15')) !== idA); checks++;

  // Tipo antes do nome numa caixa nova: o tipo sozinho já conta (como sempre), e o nome não muda nada.
  f.missao('BP16', 'Curta'); eq(L.total(), 1400); f.missao('BO16', 'Missão F'); eq(L.total(), 1400);

  // XP para baixo: o nível desce junto; tudo o que tem XP fica congelado de novo.
  eq(f.xp(500), true); eq(L.total(), 500); eq(L.nivel(), 4); eq(L.caixa(), FORMULA);
  for (const a1 of ['AW15', 'BC15', 'BI15', 'BO16']) assert(marca(L.nota(a1)), a1 + ' congelada'), checks++;
  f.missao('BP16', 'Final de arco'); eq(L.total(), 500, 'corrigir a recém-congelada não mexe');
  f.missao('BI17', 'Missão G'); f.missao('BJ17', 'Solo simples'); eq(L.total(), 575);

  // Trava do feito: até o 20 o XP não passa sozinho; com o nível já acima do limiar, segue.
  eq(f.xp(99999), true); eq(L.nivel(), 20); eq(L.total(), 99999);
  f.F.set('11,34', 21); eq(f.xp(99999), true); eq(L.nivel(), 30);
  eq(f.xp(0), true); eq(L.nivel(), 2); eq(L.total(), 0);

  // Apagar a caixa e valores inválidos: só a conta volta, nada mais muda.
  const antes = JSON.stringify([L.base(), L.nivel(), ...['AW15', 'BC15'].map(L.nota)]);
  for (const v of ['', 'abc', '-5', '1.5', '=1+1']) {
    eq(f.xp(v), true, 'caixa com ' + JSON.stringify(v)); eq(L.caixa(), FORMULA); eq(JSON.stringify([L.base(), L.nivel(), ...['AW15', 'BC15'].map(L.nota)]), antes);
  }
  eq(L.total(), 0);
}
// ---------- 4. Ficha sem a base do XP: o atalho não grava nada e o módulo faz como sempre ----------
{
  const f = ficha({ semBase: true });
  f.missao('AW15', 'Missão A'); f.missao('AX15', 'Curta');
  const n = f.leia.nota('AW15');
  eq(f.xp(1000), false); eq(f.leia.nota('AW15'), n); eq(f.D.get('54,104'), undefined);
}
// ---------- 5. O roteamento: a FICHA!AN11 vai para o atalho do XP antes do mapa do módulo ----------
eq(/if\(aba==='FICHA'&&R53_LIVRE_XP_\.caixas\.indexOf\(r\.getA1Notation\(\)\)>=0&&r53LivreXp_\(e\)\)return true;/.test(atalho), true);
eq(atalho.indexOf('r53LivreXp_(e))return true') < atalho.indexOf('if(!lista||r53LivreToca_(lista,r)'), true);
console.log(JSON.stringify({ checks, resultado: 'OK', escopo: 'XP digitado na FICHA!AN11: base, congelamento das missões antigas, missões novas por cima, nível nos dois sentidos com a trava do feito, valores inválidos' }));
