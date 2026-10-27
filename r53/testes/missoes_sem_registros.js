'use strict';
// Missões sem a leitura dos registros quando nada pode mudar (27/10/2026). O mesmo painel de missões da FICHA PESSOAL
// recebe a mesma sequência de edições pelo Salarios.gs de antes (57117fb) e pelo de agora, cada um no seu Sheets de
// mentira. Depois de cada edição as abas inteiras (células e notas) e as gravações têm que sair iguais; a de agora só
// pode deixar de ler a DADOS_SALARIOS. Mais as quatro edições medidas na cópia da Era e o registro atrasado.
const fs = require('fs'), path = require('path'), assert = require('assert'), { execSync } = require('child_process');
const { ambiente, col } = require('./missoes_ambiente');
const { preparar } = require('../diagnostico-android/preparar_missoes_sem_registros');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const raiz = path.resolve(__dirname, '..', '..');
const antes = execSync('git show 57117fb:apps-script/Salarios.gs', { cwd: raiz }).toString('utf8');
// O de agora já tem o XP congelado; sem marca nas notas ele faz o mesmo, e é ele que roda contra o de 57117fb.
const agora = fs.readFileSync(path.join(raiz, 'apps-script/Salarios.gs'), 'utf8');
// Depois desta troca veio a do XP congelado (27/10, preparar_xp_atualizar.js), com o próprio teste.
const comXp = require('../diagnostico-android/preparar_xp_atualizar').preparar;
eq(comXp(preparar(antes)), agora, 'o preparador reproduz o Salarios.gs');
assert.throws(() => preparar(preparar(antes)), /já presentes/); checks++;
assert.throws(() => preparar(antes.replace("getRange('A2:G')", "getRange('A2:H')")), /divergente/); checks++;

const OP = { espelhos: true, xp: 450, nivel: 6, limiar: 0, painel: [], registros: [] };
const letra = c => { let s = ''; for (; c > 0; c = Math.floor((c - 1) / 26)) s = String.fromCharCode(65 + (c - 1) % 26) + s; return s; };
function par() {
  const v = ambiente(antes, OP), n = ambiente(agora, OP);
  // Uma edição: grava os valores nas duas fichas e roda o onEdit das missões; devolve se a de agora leu os registros.
  function editar(r, c, valores, nome) {
    const out = [];
    for (const a of [v, n]) {
      const sh = a.abas['FICHA PESSOAL'];
      valores.forEach((l, i) => l.forEach((x, j) => sh.cells.set((r + i) + ',' + (c + j), x)));
      const e = { source: { getSheetByName: x => a.abas[x] || null }, range: sh.getRange(r, c, valores.length, valores[0].length) };
      if (valores.length === 1 && valores[0].length === 1) e.value = valores[0][0];
      a.idas.length = 0; a.escritas.length = 0;
      eq(a.ctx.salarioIntegrarMissao_(e, () => {}), true, nome);
      out.push(a.idas.some(x => /^DADOS_SALARIOS valores/.test(x)));
    }
    eq(n.retrato(), v.retrato(), nome + ': abas');
    eq(n.escritas, v.escritas, nome + ': gravações');
    eq(out[0], true, nome + ': a de antes sempre lia os registros');
    return out[1];
  }
  return { v, n, editar };
}

// As quatro edições medidas na cópia da Era (27/10): só as duas que formam ou desfazem a missão leem os registros.
{
  const p = par(), AW = col('AW');
  eq([p.editar(15, AW, [['Caçada']], 'nome sem tipo'), p.editar(15, AW + 1, [['Curta']], 'tipo'),
    p.editar(15, AW + 1, [['']], 'apaga o tipo'), p.editar(15, AW, [['']], 'apaga o nome')], [false, true, true, false]);
  eq(p.n.abas['FICHA PESSOAL'].notes.get('15,49'), '', 'a marca da caixa sem nome sai sem ler os registros');
  eq(p.n.abas.DADOS_SALARIOS.cells.get('2,5'), false, 'o registro ficou inativo');
}
// Tipo primeiro, nome depois; modificadores; colar e apagar a caixa inteira; lista fora do lugar.
{
  const p = par(), BC = col('BC');
  eq([p.editar(20, BC + 1, [['Longa']], 'tipo sem nome'), p.editar(20, BC, [['Ritual']], 'nome com tipo'),
    p.editar(20, BC + 2, [['Difícil']], 'modificador'), p.editar(20, BC, [['Ritual do porto']], 'corrige o nome'),
    p.editar(21, BC + 1, [['Inválido']], 'tipo fora da lista'), p.editar(21, BC, [['Sem tipo']], 'nome com tipo inválido'),
    p.editar(22, BC, [['Colada', 'Curta']], 'cola nome e tipo'), p.editar(20, BC, [['', '', '', '']], 'apaga a caixa'),
    p.editar(25, BC + 2, [['x', 'y'], ['z', 'w']], 'bloco de modificadores')],
  [false, true, false, true, false, false, true, true, false]);
}
// Sequência sorteada (semente fixa), sempre conferindo as duas fichas iguais depois de cada edição.
let pulou = 0, total = 0;
{
  let s = 20261027; const sorte = n => { s = (s * 1103515245 + 12345) % 2147483648; return s % n; };
  const p = par(), nomes = ['Missão A', 'Missão B', 'Caçada', '', ''], tipos = ['Curta', 'Longa', 'Final de arco', '', 'Inválido'];
  for (let k = 0; k < 400; k++) {
    const g = [49, 55, 61, 67][sorte(4)], l = 15 + sorte(6), q = sorte(10);
    const [c, val] = q < 4 ? [g, [[nomes[sorte(5)]]]] : q < 8 ? [g + 1, [[tipos[sorte(5)]]]] : q < 9 ? [g + 2, [[sorte(2) ? 'x' : '']]] :
      [g, [[nomes[sorte(5)], tipos[sorte(5)]]]];
    const leu = p.editar(l, c, val, 'sorteio ' + k + ' ' + letra(c) + l);
    total++; if (!leu) pulou++;
  }
  eq(p.n.abas.DADOS_SALARIOS.cells.size > 0, true, 'o sorteio formou missões');
}
// Um registro atrasado (uma edição que estourou o tempo antes de gravar a nota): a edição que não forma missão deixa
// ele como está, e a próxima que forma ou desfaz uma missão acerta igual à de antes.
{
  const p = par(), AW = col('AW');
  for (const a of [p.v, p.n]) a.abas.DADOS_SALARIOS.cells.set('2,1', 'idVelho'), a.abas.DADOS_SALARIOS.cells.set('2,5', true), a.abas.DADOS_SALARIOS.cells.set('2,6', '49:30');
  const v = p.v, n = p.n, sh = x => x.abas['FICHA PESSOAL'];
  for (const a of [v, n]) { sh(a).cells.set('16,49', 'Só nome'); a.idas.length = 0; a.ctx.salarioIntegrarMissao_({ source: { getSheetByName: x => a.abas[x] }, range: sh(a).getRange(16, 49), value: 'Só nome' }, () => {}); }
  eq(n.abas.DADOS_SALARIOS.cells.get('2,5'), true, 'agora: o atrasado espera'); eq(v.abas.DADOS_SALARIOS.cells.get('2,5'), false, 'antes: acertava já');
  for (const a of [v, n]) { sh(a).cells.set('16,50', 'Curta'); a.ctx.salarioIntegrarMissao_({ source: { getSheetByName: x => a.abas[x] }, range: sh(a).getRange(16, 50), value: 'Curta' }, () => {}); }
  eq(n.retrato(), v.retrato(), 'a edição seguinte que forma missão deixa as duas iguais');
}
console.log(JSON.stringify({ checks, resultado: 'OK', sorteio: pulou + ' de ' + total + ' edições sem ler a DADOS_SALARIOS',
  escopo: 'mesmas abas e gravações que o Salarios.gs de 57117fb depois de cada edição; só some a leitura dos registros quando a caixa fica sem missão antes e depois' }));
