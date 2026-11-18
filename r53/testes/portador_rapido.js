'use strict';
// Editar o portador da CARTEIRA (O9:AH12) sem esperar recálculos à toa.
//
// 18/11/2026: numa cópia do Ciclo, quatro edições do portador deram 29,97, 29,55, 27,43 e 30,68 s (estouro). Medido
// por dentro: 4,4 s no r53Editar_ relendo o Amparo (DADOS_R53_CATALOGO!X10:AJ10) e 4,3 s de espera depois do
// salarioEditar_, que no modo fórmula só travava e dava flush. Sem os dois, 12,4 a 14,4 s.
//
// Confere: (A) o portador não lê o Amparo, e outra edição da CARTEIRA fora dos cartões ainda lê; (B) no modo fórmula
// o portador não trava nem dá flush no salário, e fora do modo fórmula ainda trava.
//
// Uso: node r53/testes/portador_rapido.js [EditorR53.gs] [Salarios.gs]
const fs = require('fs'), vm = require('vm');
const { criar } = require('../arnes_custo.js');

const editor = process.argv[2] || 'apps-script/EditorR53.gs';
const salarios = process.argv[3] || 'apps-script/Salarios.gs';
let falhas = 0;
const ok = (c, m) => { console.log((c ? 'ok   ' : 'FALHA ') + m); if (!c) falhas++; };

// (A) editor de cartões
{
  const A = criar({ CARTEIRA: { cells: {}, rows: 60, cols: 50 }, DADOS_R53_CATALOGO: { cells: {}, rows: 20, cols: 50 } });
  vm.runInContext(fs.readFileSync(editor, 'utf8') + '\n', A.ctx, { filename: editor });
  const cfg = A.ctx.R53_EDITOR_, ss = A.ss;
  ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([Array(13).fill('Normal')]);
  A.props.r53_amparo_direto = JSON.stringify(Array(13).fill('Normal'));
  const areas = cfg.contextos.filter(g => g.aba === 'CARTEIRA').map(g => g.area_editor);
  const livre = (r, c) => !areas.some(a => r >= a[0] && r <= a[2] && c >= a[1] && c <= a[3]);
  const leuAmparo = () => A.log.some(e => e.t === 'R' && String(e.a).indexOf(cfg.amparo.aba + '!') === 0);
  const editar = (r, c, v) => {
    A.reset();
    const range = ss.getSheetByName('CARTEIRA').getRange(r, c);
    return A.ctx.r53Editar_({ range, source: ss, value: v });
  };
  ok(livre(9, 15), 'o portador O9 não é área de cartão');
  ok(editar(9, 15, 'Nome novo') === false && !leuAmparo(), 'portador (O9): não relê o Amparo');
  const fora = [[18, 37], [22, 37], [30, 3], [40, 20]].find(([r, c]) => livre(r, c) && !(r >= 9 && r <= 12 && c >= 15 && c <= 34));
  ok(!!fora, 'achou uma célula da CARTEIRA fora dos cartões e do portador');
  if (fora) ok(editar(fora[0], fora[1], 'x') === false && leuAmparo(), 'outra célula da CARTEIRA (' + fora + '): ainda relê o Amparo');
  // Com a marca do atalho livre (Trilha ou Caminho mudou), o portador sincroniza: o r53LivreConferido_ apaga a marca.
  vm.runInContext("var R53_LIVRE_PROP_='r53_amparo_sujo';", A.ctx);
  ok(editar(9, 15, 'Nome novo') === false && !leuAmparo(), 'portador sem a marca do Amparo sujo: não relê');
  A.props.r53_amparo_sujo = '1';
  ok(editar(9, 15, 'Nome novo') === false && leuAmparo(), 'portador com a marca do Amparo sujo: relê, como antes');
  delete A.props.r53_amparo_sujo;
}

// (C) Codigo: o portador sai antes do módulo, com a paleta pendente; o resto segue para o módulo.
{
  const { preparar } = require('../diagnostico-android/preparar_portador_sem_modulo.js');
  const { DEPOIS } = require('../diagnostico-android/preparar_atalho.js');
  const antes = 'function r53OnEditOriginal_(e){' + DEPOIS + '}';
  const fonte = preparar(antes);
  let threw = false; try { preparar(fonte); } catch (err) { threw = /já presente/.test(err.message); }
  ok(threw, 'C: o preparador recusa um Codigo que já tem o corte');
  const chamadas = [];
  const ctx = {
    r53EdicaoLivre_: () => false, r53LivreMarcar_: () => {}, r53EditarCaminho_: () => false, r53Editar_: () => false,
    r53LivreConferido_: () => chamadas.push('conferido'),
    r53ContinuarPaletaPendente_: () => { chamadas.push('paleta'); return 'paleta'; },
    r53Modulo_: () => { chamadas.push('modulo'); return { onEdit: () => 'modulo' }; },
  };
  vm.createContext(ctx); vm.runInContext(fonte, ctx);
  const ev = (aba, r, c, r2 = r, c2 = c) => ({ range: { getSheet: () => ({ getName: () => aba }), getRow: () => r,
    getLastRow: () => r2, getColumn: () => c, getLastColumn: () => c2 } });
  const rodar = e => { chamadas.length = 0; return [ctx.r53OnEditOriginal_(e), chamadas.join(',')]; };
  let [r, c] = rodar(ev('CARTEIRA', 9, 15));
  ok(r === 'paleta' && c === 'conferido,paleta', 'C: portador (O9) não abre o módulo e continua a paleta pendente');
  [r, c] = rodar(ev('CARTEIRA', 9, 15, 12, 34));
  ok(r === 'paleta' && c.indexOf('modulo') < 0, 'C: o bloco inteiro do portador (O9:AH12) também não abre');
  for (const [aba, l, col, l2, c2] of [['CARTEIRA', 18, 15], ['CARTEIRA', 8, 15], ['CARTEIRA', 9, 15, 13, 15], ['CARTEIRA', 9, 35],
    ['FICHA', 9, 15], ['FICHA PESSOAL', 9, 15]]) {
    [r, c] = rodar(ev(aba, l, col, l2, c2));
    ok(r === 'modulo' && c === 'conferido,modulo', 'C: ' + aba + ' ' + [l, col, l2, c2].filter(x => x !== undefined) + ' segue para o módulo');
  }
}

// (B) salário
{
  const B = criar({ CARTEIRA: { cells: {}, rows: 60, cols: 50 }, 'CONFIGURAÇÃO': { cells: {}, rows: 80, cols: 20 },
    DADOS_SALARIOS: { cells: {}, rows: 20, cols: 30 }, 'FICHA PESSOAL': { cells: {}, rows: 90, cols: 80 } });
  vm.runInContext(fs.readFileSync(salarios, 'utf8') + '\n', B.ctx, { filename: salarios });
  const ss = B.ss, travou = () => B.log.some(e => e.t === 'P' && e.k === 'lock') || B.log.some(e => e.t === 'F');
  const editar = () => {
    B.reset();
    let r;
    try { r = B.ctx.salarioEditar_({ range: ss.getSheetByName('CARTEIRA').getRange(9, 15), source: ss, value: 'Nome novo' }); }
    catch (err) { r = 'erro: ' + err.message; }
    return r;
  };
  ok(B.ctx.SALARIO_.formula === true, 'o salário está no modo fórmula');
  ok(editar() === false && !travou(), 'portador no modo fórmula: não trava nem dá flush');
  B.ctx.SALARIO_.formula = false;
  editar();
  ok(travou(), 'portador fora do modo fórmula: ainda trava');
}

console.log(falhas ? falhas + ' falha(s)' : 'tudo certo');
process.exit(falhas ? 1 : 0);
