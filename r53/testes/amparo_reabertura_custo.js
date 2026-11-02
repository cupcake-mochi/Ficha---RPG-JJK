'use strict';
// Medição offline (sem Google) do fechar/reabrir do Amparo com cartões pessoais preenchidos.
// Etapa 1 do plano "Amparo estourando 30 s ao reabrir" (02/11/2026): confirmar com o arnês de
// custo (r53/arnes_custo.js) se a suspeita do código bate com o tempo observado no Google
// (30,561 s e 30,454 s, RETOMADA-MECANICAS-2026-10-31.md), antes de tocar em qualquer conserto.
//
// Uso: node r53/testes/amparo_reabertura_custo.js [EditorR53.gs]
const fs = require('fs'), vm = require('vm');
const { criar, custo } = require('../arnes_custo.js');

const arquivo = process.argv[2] || 'apps-script/EditorR53.gs';
const src = fs.readFileSync(arquivo, 'utf8');

// 1) Carrega a configuração real (R53_EDITOR_) só para descobrir abas, storage e campos.
const sondagem = criar({});
vm.runInContext(src + '\n', sondagem.ctx, { filename: arquivo });
const cfg = sondagem.ctx.R53_EDITOR_;
if (!cfg || cfg.esquema !== 3) throw new Error('R53_EDITOR_ esquema 3 não encontrado em ' + arquivo);

const linhasStorage = Math.max(...cfg.contextos.map(g => g.editor)) + 2 + cfg.campos.length;
const dump = {
  'FICHA AMALDIÇOADA': { cells: {}, rows: 2000, cols: 120 },
  INVOCAÇÕES: { cells: {}, rows: 2000, cols: 220 },
  MONTAGENS: { cells: {}, rows: linhasStorage, cols: 10 },
  DADOS_R53_CATALOGO: { cells: {}, rows: 20, cols: 50 },
  DADOS_AM: { cells: {}, rows: 20, cols: 230 },
  DADOS_INVOC: { cells: {}, rows: 20, cols: 180 },
};

const A = criar(dump, { verbose: false });
vm.runInContext(src + '\n', A.ctx, { filename: arquivo });
const ss = A.ss;
const fields = cfg.campos.map(f => f[0]);

function setCel(aba, a1, v) {
  ss.getSheetByName(aba).getRange(a1).setValue(v);
}
function colLetras(n) { let s = ''; for (; n; n = Math.floor((n - 1) / 26)) s = String.fromCharCode(65 + (n - 1) % 26) + s; return s; }

// Classe máxima alta o bastante para liberar todas as Classes de todos os cartões.
setCel('DADOS_AM', 'HM4', 8);
for (let i = 2; i <= 13; i++) ss.getSheetByName('DADOS_INVOC').getRange('FP' + i).setValue(8);

// Marca os cartões (nome na célula) e a primeira Classe visível, como numa ficha nova.
for (const g of cfg.contextos) {
  const sh = ss.getSheetByName(g.aba);
  sh.getRange(g.cel.nome).setValue(g.id);
  if (g.cel.classe) sh.getRange(g.cel.classe).setValue(g.classes[0] === null ? 8 : g.classes[0]);
  g.classes.forEach((c, i) => ss.getSheetByName(cfg.storage).getRange(g.editor + 2, i + 2, fields.length, 1)
    .setValues(fields.map(f => [cfg.defaults[f]])));
}

// Amparo: 13 posições (Classe + 12 entidades), todas "Normal" no começo.
ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([Array(13).fill('Normal')]);

// Preenche 36 dos 45 cartões pessoais com Cura e PV temporários ativos (pontos > 0, ou
// checkbox marcada nos de modalidade fixa), como um personagem jogado há tempo.
const pessoais = cfg.contextos.filter(g => g.entidade === null || typeof g.entidade === 'undefined');
const preenchidos = pessoais.slice(0, 36);
for (const g of preenchidos) {
  const cl = g.classes[0] === null ? 8 : g.classes[g.classes.length - 1];
  const idxFuncao2 = fields.indexOf('funcao2'), idxPontos2 = fields.indexOf('pontos2');
  const idxFuncao3 = fields.indexOf('funcao3'), idxPontos3 = fields.indexOf('pontos3');
  const col = g.classes.indexOf(g.classes[0] === null ? null : cl) + 2;
  const linha = row => ss.getSheetByName(cfg.storage).getRange(g.editor + 2 + row, col, 1, 1);
  if (g.fixa) {
    linha(idxFuncao2).setValue('Cura'); linha(idxPontos2).setValue(0);
    linha(idxFuncao3).setValue('PV temporários'); linha(idxPontos3).setValue(0);
  } else {
    linha(idxFuncao2).setValue('Cura'); linha(idxPontos2).setValue(3);
    linha(idxFuncao3).setValue('PV temporários'); linha(idxPontos3).setValue(2);
  }
  // Mostra o cartão (grava a caixa visível) para que a aba FICHA AMALDIÇOADA/INVOCAÇÕES
  // tenha, de fato, o valor de Cura/VT na célula do cartão, não um valor em branco.
  A.ctx.r53Mostrar_(ss, g, cl);
}

console.log('Cartões pessoais:', pessoais.length, '— preenchidos para o ensaio:', preenchidos.length);

// Abre a cópia pela primeira vez: a sincronização "a frio" só guarda o Amparo atual
// (Normal em tudo) sem varrer os 249 cartões — como numa cópia nova (AGENTS.md, 26/10).
A.ctx.R53_REF_CACHE_ = {};
A.ctx.r53SincronizarFamilias_(ss);

// --- Fechar o Amparo (Classe fecha; as 12 entidades continuam Normal) ---
A.log.length = 0;
setCel(cfg.amparo.aba, cfg.amparo.faixa.split(':')[0], 'Fechada');
A.ctx.R53_REF_CACHE_ = {}; // como no onEdit real (r53Editar_ zera o cache a cada evento)
const fecharOk = A.ctx.r53SincronizarFamilias_(ss);
const custoFechar = custo(A.log);
console.log('\nFECHAR — mudou algo:', fecharOk, '| custo estimado:', custoFechar.s + 's',
  '| leituras:', custoFechar.leituras, '| gravações:', custoFechar.gravacoes, '| barreiras:', custoFechar.barreiras);

// --- Reabrir o Amparo (Classe volta a Normal) ---
A.log.length = 0;
setCel(cfg.amparo.aba, cfg.amparo.faixa.split(':')[0], 'Normal');
A.ctx.R53_REF_CACHE_ = {};
const reabrirOk = A.ctx.r53SincronizarFamilias_(ss);
const custoReabrir = custo(A.log);
console.log('REABRIR — mudou algo:', reabrirOk, '| custo estimado:', custoReabrir.s + 's',
  '| leituras:', custoReabrir.leituras, '| gravações:', custoReabrir.gravacoes, '| barreiras:', custoReabrir.barreiras);

// Detalha a composição do custo de reabrir: quantas leituras vieram de r53Ativa_ (classe do
// cartão lida de novo, fora da matriz já carregada) e quantas gravações são de validação
// (cartões de modalidade fixa), que é o que pode interleavar leitura/escrita no meio do laço.
const porTipo = {};
for (const e of A.log) {
  const chave = e.t + ':' + (e.k || '') + (e.barreira ? ' [barreira]' : '');
  porTipo[chave] = (porTipo[chave] || 0) + 1;
}
console.log('\nOperações de REABRIR por tipo:', porTipo);

// Conferência, SEM contar no custo de reabrir: nenhum valor devolvido deve ficar "—".
let mascarados = 0;
for (const g of preenchidos) {
  const sh = ss.getSheetByName(g.aba);
  for (const key of ['cura', 'vt']) {
    const pos = g.funcoes_diretas[key]; if (!pos) continue;
    if (sh.getRange(pos).getValue() === '—') mascarados++;
  }
}
console.log('\nCampos ainda em "—" depois de reabrir:', mascarados, mascarados === 0 ? '(ok)' : '(RECUPERAÇÃO FALHOU)');
