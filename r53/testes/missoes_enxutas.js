'use strict';
// Missões enxutas (26/10/2026): a mesma edição no painel de missões da FICHA PESSOAL, pelo código de antes e pelo de
// depois do preparar_missoes_enxutas.js, num Sheets de mentira que conta as idas. Confere que as duas deixam as mesmas
// células, notas e nível, e que a de depois vai menos vezes ao servidor. Sem os espelhos da DADOS, cai na leitura antiga.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
const {preparar: comExtrato} = require('../diagnostico-android/preparar_salario_extrato.js');
const {preparar: comMissoes} = require('../diagnostico-android/preparar_missoes.js');
const {preparar: enxutas} = require('../diagnostico-android/preparar_missoes_enxutas.js');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };

const base = comExtrato({files: [{name: 'Codigo', source: fs.readFileSync(path.join(__dirname, 'salarios-com-formula.gs'), 'utf8')}]}).files[0].source;
const antes = comMissoes(base), depois = enxutas(antes);
// Depois delas veio a troca de 27/10 (missões sem a leitura dos registros), que tem o próprio teste.
eq(require('../diagnostico-android/preparar_missoes_sem_registros.js').preparar(depois), fs.readFileSync(path.join(raiz, 'apps-script/Salarios.gs'), 'utf8'), 'o Salarios.gs é o resultado do preparador');
assert.throws(() => enxutas(depois), /já presentes/); checks++;
assert.throws(() => enxutas(antes.replace("getRange('AQ4:DP100')", "getRange('AQ4:DP99')")), /divergente/); checks++;

const { ambiente } = require('./missoes_ambiente');

let idasAntes = 0, idasDepois = 0, casos = 0;
const cenarios = [];
for (const espelhos of [true, false]) for (const [xp, nivel, limiar] of [[0, 1, 0], [450, 2, 0], [450, 6, 0], [500, 5, 0], [2500, 3, 10], [99999, 21, 20], [99999, 30, 0], ['', 4, 0]])
  for (const [onde, valor, painel, registros] of [
    ['AW15', 'Missão A', [['AX15', 'Curta']], []],
    ['AX16', 'Longa', [['AW16', 'Missão B']], []],
    ['BC20', '', [['BD20', 'Padrão']], [['idX', 'Missão velha', 'Padrão', 46001, true, '55:20', 46001]]],
    ['AW15', 'Missão A corrigida', [['AX15', 'Curta']], [['idA', 'Missão A', 'Curta', 46002, true, '49:15', 46002]]],
  ]) cenarios.push({espelhos, xp, nivel, limiar, onde, valor, painel, registros});
for (const op of cenarios) {
  const rodar = source => {
    const a = ambiente(source, op), e = a.evento(op.onde, op.valor);
    if (op.registros.length && op.registros[0][0] === 'idA') a.abas['FICHA PESSOAL'].notes.set('15,49', 'x\n[Salário: idA · 01/01/2026]');
    a.idas.length = 0;
    let original = 0;
    eq(a.ctx.salarioIntegrarMissao_(e, () => { original++; }), true);
    return {a, original};
  };
  const v = rodar(antes), n = rodar(depois), onde = JSON.stringify(op);
  eq(n.a.retrato(), v.a.retrato(), onde + ' células e notas');
  eq(n.original, v.original, onde + ' onEdit de sempre');
  eq(n.a.escritas.map(x => x.join(' ')), v.a.escritas.map(x => x.join(' ')), onde + ' gravações');
  assert(n.a.idas.length < v.a.idas.length, onde + ' idas ' + v.a.idas.length + ' → ' + n.a.idas.length); checks++;
  eq(n.a.idas.some(x => /L2|12 1×1/.test(x) && /DADOS_SALARIOS valor/.test(x)), false, onde + ' sem ler o estado');
  eq(n.a.idas.filter(x => /última linha|linhas$/.test(x)), [], onde + ' sem getLastRow/getMaxRows');
  if (op.espelhos) eq(n.a.idas.filter(x => /^(FICHA|FICHA PESSOAL) valor /.test(x)), [], onde + ' XP e nível pelos espelhos');
  const falta = n.a.abas['FICHA PESSOAL'].cells.get('11,55');
  eq(n.a.idas.some(x => /^DADOS valores/.test(x)), !(falta === '—' || falta > 0), onde + ' DADOS só quando o nível pode subir');
  idasAntes += v.a.idas.filter(x => x !== 'flush').length; idasDepois += n.a.idas.filter(x => x !== 'flush').length; casos++;
}
// O caso comum, contado à parte: nome de missão novo, com os espelhos.
const um = s => { const a = ambiente(s, cenarios[0]), e = a.evento('AW15', 'Missão A'); a.idas.length = 0; a.ctx.salarioIntegrarMissao_(e, () => {}); return a.idas.filter(x => x !== 'flush'); };
const [l1, l2] = [um(antes), um(depois)];
console.log(JSON.stringify({checks, casos, resultado: 'OK', leituras_caso_comum: l1.length + ' → ' + l2.length, leituras_somadas: idasAntes + ' → ' + idasDepois,
  depois: l2, escopo: 'mesmas células, notas, nível e onEdit; sem L2, getLastRow e getMaxRows; XP e nível pelos espelhos da DADOS'}));
