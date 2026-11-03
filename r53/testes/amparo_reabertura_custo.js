'use strict';
// Fechar e reabrir o Amparo com os cartões pessoais preenchidos, sem Google, com as abas do tamanho real.
//
// 02/11/2026: a medição na cópia de teste (logs R53T no painel Execuções) mostrou que a reabertura estourava os 30 s
// por ler a MONTAGENS inteira (9465×9, ~11 s) e a FICHA AMALDIÇOADA inteira (557×20, ~6 s), somadas ao recálculo da
// troca (~7 s na primeira leitura). O modelo de custo do arnês (r53/arnes_custo.js) cobra ~4,5 s por aba inteira,
// seja qual for o tamanho, e não enxergava isso; por isso aqui a régua é a quantidade de células lidas. Na cópia,
// lendo só as faixas, a reabertura caiu de 30,8 s (estouro) para 15,8 s (fechar: 15,4 s).
//
// Três casos: (1) fechar e reabrir; (2) gravar um cartão com o Amparo fechado e reabrir; (3) fechar e reabrir o Amparo
// da primeira entidade, cujos cartões ficam na INVOCAÇÕES. Em todos, cada Cura e PV temp. tem de voltar ao valor de
// antes de fechar (no caso 2, ao valor novo).
//
// Uso: node r53/testes/amparo_reabertura_custo.js [EditorR53.gs]
const fs = require('fs'), vm = require('vm');
const { criar } = require('../arnes_custo.js');

const arquivo = process.argv[2] || 'apps-script/EditorR53.gs';
const src = fs.readFileSync(arquivo, 'utf8');

function montar() {
  const sondagem = criar({});
  vm.runInContext(src + '\n', sondagem.ctx, { filename: arquivo });
  const cfg = sondagem.ctx.R53_EDITOR_;
  if (!cfg || cfg.esquema !== 3) throw new Error('R53_EDITOR_ esquema 3 não encontrado em ' + arquivo);
  // Tamanhos medidos na cópia em 02/11/2026: FICHA AMALDIÇOADA 557×20, MONTAGENS 9465×9.
  const linhasStorage = Math.max(9465, Math.max(...cfg.contextos.map(g => g.editor)) + 2 + cfg.campos.length);
  const A = criar({
    'FICHA AMALDIÇOADA': { cells: {}, rows: 557, cols: 20 },
    INVOCAÇÕES: { cells: {}, rows: 2000, cols: 220 },
    MONTAGENS: { cells: {}, rows: linhasStorage, cols: 9 },
    DADOS_R53_CATALOGO: { cells: {}, rows: 20, cols: 50 },
    DADOS_AM: { cells: {}, rows: 20, cols: 230 },
    DADOS_INVOC: { cells: {}, rows: 20, cols: 180 },
  });
  vm.runInContext(src + '\n', A.ctx, { filename: arquivo });
  const ss = A.ss, fields = cfg.campos.map(f => f[0]);
  const setCel = (aba, a1, v) => ss.getSheetByName(aba).getRange(a1).setValue(v);

  setCel('DADOS_AM', 'HM4', 8);
  for (let i = 2; i <= 13; i++) ss.getSheetByName('DADOS_INVOC').getRange('FP' + i).setValue(8);
  for (const g of cfg.contextos) {
    const sh = ss.getSheetByName(g.aba);
    sh.getRange(g.cel.nome).setValue(g.id);
    if (g.cel.classe) sh.getRange(g.cel.classe).setValue(g.classes[0] === null ? 8 : g.classes[0]);
    g.classes.forEach((c, i) => ss.getSheetByName(cfg.storage).getRange(g.editor + 2, i + 2, fields.length, 1)
      .setValues(fields.map(f => [cfg.defaults[f]])));
  }
  ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([Array(13).fill('Normal')]);

  // 36 dos 45 cartões pessoais com Cura e PV temporários ativos, como um personagem jogado há tempo.
  const pessoais = cfg.contextos.filter(g => g.entidade === null || typeof g.entidade === 'undefined');
  const preenchidos = pessoais.slice(0, 36), classe = new Map();
  for (const g of preenchidos) {
    const cl = g.classes[0] === null ? 8 : g.classes[g.classes.length - 1];
    const col = g.classes.indexOf(g.classes[0] === null ? null : cl) + 2;
    const linha = k => ss.getSheetByName(cfg.storage).getRange(g.editor + 2 + fields.indexOf(k), col, 1, 1);
    linha('funcao2').setValue('Cura'); linha('pontos2').setValue(g.fixa ? 0 : 3);
    linha('funcao3').setValue('PV temporários'); linha('pontos3').setValue(g.fixa ? 0 : 2);
    if (g.cel.classe) ss.getSheetByName(g.aba).getRange(g.cel.classe).setValue(cl);
    A.ctx.R53_REF_CACHE_ = {};
    A.ctx.r53Mostrar_(ss, g, cl);
    classe.set(g, cl);
  }
  // Os outros 9 também mostrados: um cartão de modalidade fixa nunca mostrado fica "" em vez da caixa, e a
  // reabertura (com ou sem conserto) devolveria false, um falso erro.
  for (const g of pessoais.slice(36)) {
    A.ctx.R53_REF_CACHE_ = {};
    A.ctx.r53Mostrar_(ss, g, g.classes[0] === null ? 8 : g.classes[0]);
  }
  // Os 17 cartões da primeira entidade, todos com Cura e PV temporários (caso 3).
  const entidade = cfg.contextos.filter(g => g.entidade === 0);
  for (const g of entidade) {
    const cl = g.classes[g.classes.length - 1], col = g.classes.length + 1;
    const linha = k => ss.getSheetByName(cfg.storage).getRange(g.editor + 2 + fields.indexOf(k), col, 1, 1);
    linha('funcao2').setValue('Cura'); linha('pontos2').setValue(g.fixa ? 0 : 4);
    linha('funcao3').setValue('PV temporários'); linha('pontos3').setValue(g.fixa ? 0 : 1);
    if (g.cel.classe) ss.getSheetByName(g.aba).getRange(g.cel.classe).setValue(cl);
    A.ctx.R53_REF_CACHE_ = {};
    A.ctx.r53Mostrar_(ss, g, cl);
  }
  // Abertura a frio: a sincronização só guarda o Amparo atual.
  A.ctx.R53_REF_CACHE_ = {};
  A.ctx.r53SincronizarFamilias_(ss);

  const celulas = [];
  for (const g of pessoais.concat(entidade)) for (const key of ['cura', 'vt']) {
    const pos = g.funcoes_diretas[key]; if (pos && g.portas[key] !== 'FALSE') celulas.push(g.aba + '!' + pos);
  }
  const visiveis = () => Object.fromEntries(celulas.map(p => { const [aba, a1] = p.split('!'); return [p, ss.getSheetByName(aba).getRange(a1).getValue()]; }));
  return { A, ss, cfg, fields, preenchidos, entidade, classe, setCel, celulas, visiveis };
}

// familia: 0 é a pessoal, 1 a primeira entidade (a coluna seguinte na faixa do Amparo).
function trocar(M, valor, familia = 0) {
  M.ss.getSheetByName(M.cfg.amparo.aba).getRange(M.cfg.amparo.faixa.split(':')[0]).offset(0, familia).setValue(valor);
  M.A.reset(); M.A.ctx.R53_REF_CACHE_ = {};
  M.A.ctx.r53SincronizarFamilias_(M.ss);
  const R = M.A.log.filter(e => e.t === 'R');
  return { leituras: R.length, celulas: R.reduce((n, e) => n + e.n, 0), maior: R.reduce((m, e) => Math.max(m, e.n), 0),
    maiores: R.filter(e => e.n > 1000).map(e => e.a + ' (' + e.n + ')') };
}

function conferir(M, esperado, rotulo) {
  const agora = M.visiveis(), erros = Object.keys(esperado).filter(p => agora[p] !== esperado[p]);
  if (erros.length) console.log('  ✗ ' + rotulo + ': ' + erros.length + ' célula(s) erradas, ex.: ' + erros.slice(0, 4).map(p => p + ' ' + JSON.stringify(agora[p]) + '≠' + JSON.stringify(esperado[p])).join(', '));
  return erros.length;
}

const linha = (r) => r.leituras + ' leituras, ' + r.celulas + ' células' + (r.maiores.length ? ' — aba inteira: ' + r.maiores.join(', ') : '');
let falhas = 0;

// (1) Fechar e reabrir.
{
  const M = montar(), antes = M.visiveis();
  console.log('Cartões pessoais com Cura/PV temp. no ensaio:', M.preenchidos.length, '— células conferidas:', M.celulas.length);
  const f = trocar(M, 'Fechada');
  const fechadas = Object.values(M.visiveis()).filter(v => v === '—').length;
  const r = trocar(M, 'Normal');
  console.log('\n(1) FECHAR  —', linha(f), '| em "—" depois:', fechadas);
  console.log('    REABRIR —', linha(r));
  falhas += conferir(M, antes, 'reabrir');
}

// (2) Um cartão gravado com o Amparo fechado (r53Gravar_, como numa edição de outro campo dele): a reabertura traz o
// valor novo.
{
  const M = montar(), antes = M.visiveis();
  trocar(M, 'Fechada');
  const g = M.preenchidos.find(x => !x.fixa && x.classes[0] !== null), cl = M.classe.get(g);
  M.A.ctx.R53_REF_CACHE_ = {};
  const vals = M.A.ctx.r53LerVersao_(M.ss, g, cl);
  vals[M.fields.indexOf('pontos2')] = 5;
  M.A.ctx.r53Gravar_(M.ss, g, cl, vals);
  const r = trocar(M, 'Normal');
  antes[g.aba + '!' + g.funcoes_diretas.cura] = 5;
  console.log('\n(2) REABRIR depois de gravar ' + g.id + ' fechado —', linha(r));
  falhas += conferir(M, antes, 'reabrir depois de gravar fechado');
}

// (3) Fechar e reabrir o Amparo da primeira entidade: lê só as linhas dela, na INVOCAÇÕES e na MONTAGENS.
{
  const M = montar(), antes = M.visiveis();
  const f = trocar(M, 'Fechada', 1);
  const fechadas = M.celulas.filter(p => p.startsWith('INVOCAÇÕES!') && M.visiveis()[p] === '—').length;
  const r = trocar(M, 'Normal', 1);
  console.log('\n(3) ENTIDADE 1, ' + M.entidade.length + ' cartões — FECHAR —', linha(f), '| em "—" depois:', fechadas);
  console.log('    REABRIR —', linha(r));
  if (!fechadas) { console.log('  ✗ entidade: nenhum cartão foi para "—" ao fechar'); falhas++; }
  falhas += conferir(M, antes, 'reabrir a entidade');
}

console.log(falhas ? '\nFALHOU: ' + falhas + ' célula(s) não voltaram ao valor certo.' : '\nOK: todas as células voltaram ao valor certo nos três casos.');
process.exit(falhas ? 1 : 0);
