'use strict';
// Mesmo ensaio de r53/testes/amparo_reabertura_custo.js, mas com um conserto candidato
// aplicado só em memória (nenhum arquivo do pacote é tocado): troca, dentro do
// r53SincronizarFamilias_, a leitura "fresca" de r53Ativa_(ss,g) por uma leitura da
// matriz que a própria rotina já carregou (como o r53AtivaNaFoto_ já faz no cartão
// individual). Serve só para medir o ganho antes de propor o patch de verdade.
//
// Uso: node r53/testes/amparo_reabertura_conserto.js [EditorR53.gs]
const fs = require('fs'), vm = require('vm');
const { criar, custo } = require('../arnes_custo.js');

const arquivo = process.argv[2] || 'apps-script/EditorR53.gs';
let src = fs.readFileSync(arquivo, 'utf8');

// Função candidata: lê a Classe ativa da matriz já carregada do aba; cai para r53Ativa_
// nos casos em que ele não lê a aba do cartão (classes[0]===null, ou só uma versão).
const original = /function r53SincronizarFamilias_\(ss\) \{[\s\S]*?\n\}\n/.exec(src);
if (!original) throw new Error('r53SincronizarFamilias_ não encontrada em ' + arquivo);

const corrigida = original[0]
  .replace(
    'var sh=ss.getSheetByName(g.aba),matrix=snapshots[g.aba]||(snapshots[g.aba]=sh.getDataRange().getValues());',
    'var sh=ss.getSheetByName(g.aba),matrix=snapshots[g.aba]||(snapshots[g.aba]=sh.getDataRange().getValues());' +
    '\n   var ativaDaMatriz=function(){if(g.classes[0]===null||g.classes.length===1)return r53Ativa_(ss,g);var p=r53Pos_(g.cel.classe);return Number(matrix[p[0]-1][p[1]-1]);};'
  )
  .replace('var col=r53Indice_(g,r53Ativa_(ss,g))-1;', 'var col=r53Indice_(g,ativaDaMatriz())-1;');

if (corrigida === original[0]) throw new Error('os dois replace() não bateram com o código atual — confira se o arquivo mudou');
src = src.replace(original[0], corrigida);

function medir(fonte) {
  const sondagem = criar({});
  vm.runInContext(fonte + '\n', sondagem.ctx, { filename: arquivo });
  const cfg = sondagem.ctx.R53_EDITOR_;
  const linhasStorage = Math.max(...cfg.contextos.map(g => g.editor)) + 2 + cfg.campos.length;
  const dump = {
    'FICHA AMALDIÇOADA': { cells: {}, rows: 2000, cols: 120 },
    INVOCAÇÕES: { cells: {}, rows: 2000, cols: 220 },
    MONTAGENS: { cells: {}, rows: linhasStorage, cols: 10 },
    DADOS_R53_CATALOGO: { cells: {}, rows: 20, cols: 50 },
    DADOS_AM: { cells: {}, rows: 20, cols: 230 },
    DADOS_INVOC: { cells: {}, rows: 20, cols: 180 },
  };
  const A = criar(dump);
  vm.runInContext(fonte + '\n', A.ctx, { filename: arquivo });
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

  const pessoais = cfg.contextos.filter(g => g.entidade === null || typeof g.entidade === 'undefined');
  const preenchidos = pessoais.slice(0, 36);
  for (const g of preenchidos) {
    const cl = g.classes[0] === null ? 8 : g.classes[g.classes.length - 1];
    const col = g.classes.indexOf(g.classes[0] === null ? null : cl) + 2;
    const linha = row => ss.getSheetByName(cfg.storage).getRange(g.editor + 2 + row, col, 1, 1);
    const idxFuncao2 = fields.indexOf('funcao2'), idxPontos2 = fields.indexOf('pontos2');
    const idxFuncao3 = fields.indexOf('funcao3'), idxPontos3 = fields.indexOf('pontos3');
    if (g.fixa) { linha(idxFuncao2).setValue('Cura'); linha(idxPontos2).setValue(0); linha(idxFuncao3).setValue('PV temporários'); linha(idxPontos3).setValue(0); }
    else { linha(idxFuncao2).setValue('Cura'); linha(idxPontos2).setValue(3); linha(idxFuncao3).setValue('PV temporários'); linha(idxPontos3).setValue(2); }
    A.ctx.r53Mostrar_(ss, g, cl);
  }

  A.ctx.R53_REF_CACHE_ = {};
  A.ctx.r53SincronizarFamilias_(ss); // abertura fria

  A.log.length = 0;
  setCel(cfg.amparo.aba, cfg.amparo.faixa.split(':')[0], 'Fechada');
  A.ctx.R53_REF_CACHE_ = {};
  A.ctx.r53SincronizarFamilias_(ss);
  const fechar = custo(A.log);

  A.log.length = 0;
  setCel(cfg.amparo.aba, cfg.amparo.faixa.split(':')[0], 'Normal');
  A.ctx.R53_REF_CACHE_ = {};
  A.ctx.r53SincronizarFamilias_(ss);
  const reabrir = custo(A.log);

  let mascarados = 0;
  for (const g of preenchidos) for (const key of ['cura', 'vt']) {
    const pos = g.funcoes_diretas[key]; if (!pos) continue;
    if (ss.getSheetByName(g.aba).getRange(pos).getValue() === '—') mascarados++;
  }
  return { fechar, reabrir, mascarados };
}

const antes = medir(fs.readFileSync(arquivo, 'utf8'));
const depois = medir(src);

console.log('ANTES  — fechar:', antes.fechar.s + 's (' + antes.fechar.leituras + ' leituras)',
  '| reabrir:', antes.reabrir.s + 's (' + antes.reabrir.leituras + ' leituras)', '| mascarados:', antes.mascarados);
console.log('DEPOIS — fechar:', depois.fechar.s + 's (' + depois.fechar.leituras + ' leituras)',
  '| reabrir:', depois.reabrir.s + 's (' + depois.reabrir.leituras + ' leituras)', '| mascarados:', depois.mascarados);

if (depois.mascarados !== 0) { console.error('\nCONSERTO QUEBROU A RECUPERAÇÃO — não usar.'); process.exit(1); }
console.log('\nGanho em reabrir:', Math.round((antes.reabrir.s - depois.reabrir.s) * 10) / 10, 's');
