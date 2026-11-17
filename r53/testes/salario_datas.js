'use strict';
// Datas do salário sem hora (16/11/2026, preparar_salario_datas.js). O defeito: a cada fechamento as datas do livro
// SALÁRIOS acumulavam 9 horas e os vencimentos andavam. Aqui:
//   1. o preparador e o trecho do console: ida e volta, recusa de repetir e de código divergente;
//   2. fechamentos em sequência com o salarioCongelar_ de verdade e a fórmula de verdade do Q2 (o texto do Salarios.gs,
//      traduzido para JS), numa planilha de mentira que guarda data como o Sheets guarda (número, no fuso da planilha);
//   3. a conta esperada feita por fora: o dia de cada fim é emissão + k × intervalo, contado no calendário à mão;
//   4. defeitos plantados, que têm de acender: a fórmula antiga, o código antigo, e os dois juntos.
// Limite: a VM não avalia fórmulas. Do Q2 roda o texto real; o "Períodos vencidos" (Q3) e a tabela (P11) são imitados
// aqui pela regra deles (FLOOR((hoje−Q2)/dias); início = Q2 + k × dias).
const fs = require('node:fs'), assert = require('node:assert'), vm = require('node:vm');
const P = require('../diagnostico-android/preparar_salario_datas');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m || 'valores diferentes'); checks++; };
const agora = fs.readFileSync('apps-script/Salarios.gs', 'utf8');
const volta = P.PARES.map(([a, b]) => [b, a]);
const antes = P.aplicar(agora, volta, 'reverter');

// 1. Preparador e trecho.
eq(P.preparar(antes), agora, 'o preparador leva o salário de antes ao de agora');
assert.throws(() => P.preparar(agora), /já presentes/); checks++;
assert.throws(() => P.preparar(antes.replace('salarioData_(l[1]),', 'salarioData_(l[1]), ')), /divergente/); checks++;
assert.throws(() => P.preparar(antes + antes), /2 vez/); checks++;
eq(P.PARES.length, 2);
eq(agora.includes(P.FORMULA_Q2.replace(/"/g, '\\"')), true, 'a fórmula do Q2 no Salarios.gs é a FORMULA_Q2 do preparador');
const instalado = '// cabeçalho do Codigo\nfunction r53Modulo_(){}\n' + antes + '\nfunction outra_(){}\n';
eq(P.aplicar(instalado, P.PARES, 'instalado'), '// cabeçalho do Codigo\nfunction r53Modulo_(){}\n' + agora + '\nfunction outra_(){}\n');

// 3. Conta por fora: número de série do Sheets (dias desde 30/12/1899) contado no calendário, sem Date.
function serie(ano, mes, dia) {
  const bissexto = a => (a % 4 === 0 && a % 100 !== 0) || a % 400 === 0;
  const meses = a => [31, bissexto(a) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  let n = 2; // 30/12/1899 = 0, então 01/01/1900 = 2
  for (let a = 1900; a < ano; a++) n += bissexto(a) ? 366 : 365;
  for (let m = 1; m < mes; m++) n += meses(ano)[m - 1];
  return n + dia - 1;
}
eq(serie(1970, 1, 1), 25569, 'a conta à mão bate com a constante conhecida do Sheets');
const EMISSAO = serie(2026, 11, 10);
eq(EMISSAO, 46336);

// 2. A planilha de mentira.
/** O Q2 de verdade: o texto da fórmula, com LET/IF/MAX/INT traduzidos. Recusa fórmula de outra forma. */
function q2DaFormula(formula) {
  const m = /^=IF\(ISNUMBER\(N2\);LET\(ult;MAX\('SALÁRIOS'!C2:C\);em;INT\(N2\);(.+)\);""\)$/.exec(formula);
  assert(m, 'forma da fórmula do Q2 mudou: ' + formula);
  const corpo = m[1].replace(/;/g, ',').replace(/\bIF\(/g, 'SE(').replace(/\bMAX\(/g, 'Math.max(').replace(/\bINT\(/g, 'Math.floor(');
  const f = new Function('ult', 'em', 'SE', 'return ' + corpo + ';');
  return (n2, colunaC) => typeof n2 !== 'number' ? '' : f(colunaC.length ? Math.max(...colunaC) : 0, Math.floor(n2), (c, a, b) => c ? a : b);
}
/** Roda `fechamentos` dias de vencimento seguidos e devolve o que ficou no livro e o que a ficha mostrou. */
function simular(fonte, { dias, fechamentos, fusoHoras = -3, livroInicial = [] }) {
  const ctx = {}; vm.createContext(ctx); vm.runInContext(fonte, ctx);
  ctx.Utilities = { formatDate: (d, tz, f) => { const [y, mo, dd] = new Date(d.getTime() - 3 * 3600000).toISOString().slice(0, 10).split('-');
    return f.replace('yyyy', y).replace('MM', mo).replace('dd', dd); } };
  const q2 = q2DaFormula(vm.runInContext('SALARIO_.f.aux[1][1]', ctx));
  // O Sheets guarda a Date como número no fuso da planilha, e devolve Date de célula com formato de data.
  const paraSerie = d => (d.getTime() + fusoHoras * 3600000) / 86400000 + 25569;
  const DataVM = vm.runInContext('Date', ctx);  // a Date da VM: o salarioDia_ testa instanceof Date lá dentro
  const paraDate = s => new DataVM((s - 25569) * 86400000 - fusoHoras * 3600000);
  const livro = livroInicial.map(l => l.slice()), visto = [];
  const abas = {
    DADOS_SALARIOS: { getRange: () => ({ getValues: () => estado.v }) },
    'SALÁRIOS': { insertRowsAfter() {}, getRange: (lin) => ({ setValues: linhas => linhas.forEach((l, i) => {
      livro[lin - 2 + i] = l.map(c => c instanceof DataVM ? paraSerie(c) : c); }) }) },
  };
  const ss = { getSheetByName: n => abas[n] }, estado = {};
  for (let k = 1; k <= fechamentos; k++) {
    const hoje = EMISSAO + k * dias;                       // o dia exato do k-ésimo vencimento
    const inicio = q2(EMISSAO, livro.map(l => l[2]));
    const vencidos = Math.max(0, Math.floor((hoje - inicio) / dias));
    const v = Array.from({ length: 129 }, () => Array(10).fill(''));
    v[0][1] = paraDate(inicio); v[1][1] = vencidos; v[4][1] = livro.length; v[5][1] = 1000; v[6][1] = dias;
    for (let i = 0; i < vencidos; i++) { const s = inicio + i * dias, e = s + dias;
      v[9 + i] = ['SAL1:' + s + ':' + e, s, e, 'Grau 4', 150000, 0, 3, 1, 150000, 'Participação dispensada pela campanha']; }
    estado.v = v;
    const r = ctx.salarioCongelar_(ss, hoje);
    visto.push({ k, inicio, vencidos, novos: r.novos, proximo: r.proximo });
  }
  return { livro, visto };
}
/** As quatro afirmações do conserto; devolve a lista do que falhou (vazia = certo). */
function conferir(r, { dias, fechamentos, primeiroFim = EMISSAO + dias }) {
  const erros = [];
  if (r.livro.length !== fechamentos) erros.push('linhas no livro: ' + r.livro.length + ' em vez de ' + fechamentos);
  r.livro.forEach((l, i) => {
    const fim = primeiroFim + i * dias;                   // conta por fora
    if (Math.floor(l[2]) !== fim) erros.push('fim ' + (i + 1) + ' no dia ' + Math.floor(l[2]) + ', esperado ' + fim);
    if (Math.floor(l[1]) !== fim - dias) erros.push('início ' + (i + 1) + ' no dia ' + Math.floor(l[1]) + ', esperado ' + (fim - dias));
    if (Math.abs(l[2] % 1 - r.livro[0][2] % 1) > 1e-9) erros.push('hora do fim ' + (i + 1) + ' mudou: acumulou');
  });
  r.visto.forEach(x => {
    if (x.inicio % 1 !== 0) erros.push('fechamento ' + x.k + ': período começa com hora (' + x.inicio + ')');
    if (x.novos !== 1) erros.push('fechamento ' + x.k + ': pagou ' + x.novos + ' no dia do vencimento, esperado 1');
  });
  return erros;
}

// Certo: código e fórmula de agora. Intervalo de 1 dia (o do achado), de 7 e de 30; e planilha em outro fuso.
for (const caso of [{ dias: 1, fechamentos: 12 }, { dias: 7, fechamentos: 8 }, { dias: 30, fechamentos: 6 }, { dias: 1, fechamentos: 12, fusoHoras: 9 }])
  eq(conferir(simular(agora, caso), caso), [], 'certo: ' + JSON.stringify(caso));
// O achado, reproduzido com o salário de antes. Emissão num dia, intervalo de 1 dia, conferência em cada um dos 7 dias
// seguintes: saem só 5 fechamentos de ¥150.000 (¥750.000, o que o ChatGPT viu), porque o período que começa com hora
// ainda não venceu no dia certo. Cada fim tem 9 h a mais que o anterior e o terceiro já cai um dia depois.
{
  const r = simular(antes, { dias: 1, fechamentos: 7 });
  eq(r.visto.map(x => x.novos), [1, 0, 1, 1, 0, 1, 1], 'antes: dois dias de vencimento sem pagar');
  eq(r.livro.map(l => Math.round((l[2] - EMISSAO) * 24)), [24 + 9, 48 + 18, 72 + 27, 96 + 36, 120 + 45], 'antes: 9 h a mais por fechamento');
  eq(Math.floor(r.livro[2][2]), EMISSAO + 4, 'antes: o terceiro fim cai um dia depois');
  eq(r.livro.reduce((a, l) => a + l[9], 0), 750000);
  // Com o conserto, os mesmos 7 dias pagam 7: 7 × 150.000, conta por fora.
  eq(simular(agora, { dias: 1, fechamentos: 7 }).livro.reduce((a, l) => a + l[9], 0), 7 * 150000);
}
// Livro que já tem hora (ficha que fechou com o código antigo): o período seguinte volta a começar num dia inteiro.
{
  const caso = { dias: 1, fechamentos: 4, livroInicial: [['SAL1:x', EMISSAO + 0.375, EMISSAO + 1 + 0.375, 0, '', 0, 0, 0, 150000]] };
  const r = simular(agora, caso);
  eq(r.visto.every(x => x.inicio % 1 === 0), true, 'livro com hora: início inteiro');
  eq(r.livro.slice(1).map(l => Math.floor(l[2])), [EMISSAO + 2, EMISSAO + 3, EMISSAO + 4], 'livro com hora: fins nos dias certos');
}

// 4. Defeitos plantados: cada um tem de acender.
const plantados = {
  'fórmula antiga (sem INT), código novo': P.aplicar(agora, [volta[0]], 'plantar'),
  'código antigo (sem arredondar), fórmula antiga': antes,
  'fórmula que soma em vez de arredondar': agora.replace('MAX(INT(ult);em)', 'MAX(ult+0;em)'),
  'código que arredonda só o início': agora.replace('salarioData_(Math.floor(l[2]))', 'salarioData_(l[2])').replace('MAX(INT(ult);em)', 'MAX(ult;em)'),
};
let acesos = 0;
for (const [nome, fonte] of Object.entries(plantados)) {
  assert.notStrictEqual(fonte, agora, 'defeito não plantado: ' + nome);
  const erros = conferir(simular(fonte, { dias: 1, fechamentos: 12 }), { dias: 1, fechamentos: 12 });
  assert(erros.length > 0, 'defeito plantado não acendeu: ' + nome); acesos++; checks++;
}
// O reforço do código, isolado: com a fórmula antiga, o código novo não deixa a hora acumular; o antigo deixa.
{
  const hora = fonte => simular(fonte, { dias: 1, fechamentos: 6 }).livro.map(l => Math.round(l[2] % 1 * 24));
  eq(hora(P.aplicar(agora, [volta[0]], 'x')), [9, 9, 9, 9, 9], 'fórmula antiga + código novo: a hora fica em 9 h (um dia de atraso, sem acumular)');
  eq(hora(antes), [9, 18, 3, 12], 'fórmula antiga + código antigo: 9 h a mais a cada fechamento');
}

// 5. Pente-fino (16/11/2026): as outras datas que o script grava com hora (09:00 de Brasília, pelo salarioData_) são a
// emissão (DADOS_SALARIOS!N2, CONFIGURAÇÃO!O38), o próximo fechamento (O48), o início do ciclo (O69) e as três datas do
// livro SALÁRIOS (B, C, D). Nenhuma fórmula pode comparar ou somar uma delas sem tirar a hora. As datas das missões
// (DADOS_SALARIOS!D) e das trocas (H) são gravadas como dia inteiro e não entram aqui.
function semInt(fonte) {
  const achados = [];
  // a) comparação direta com O38, O48 ou O69 (o certo é INT(O69), INT(O48)…)
  for (const m of fonte.matchAll(/(?:[<>]=?|=)\s*(O38|O48|O69)\b(?!\s*=\\?")/g)) achados.push('comparação sem INT: ' + m[0]);
  // b) N2 em conta sem INT (ISNUMBER(N2) e N2 sozinho num teste não são conta)
  for (const m of fonte.matchAll(/(?<!ISNUMBER\()(?<!INT\()(?<![A-Z$'!])N2\b\s*[-+*/<>]/g)) achados.push('N2 em conta sem INT: ' + m[0]);
  // c) coluna de data do livro lida por fórmula: só o MAX do fim, e o resultado dele passa por INT
  for (const m of fonte.matchAll(/'SALÁRIOS'!\$?([BCD])\$?\d*:\$?[BCD]/g)) {
    if (m[1] !== 'C' || !fonte.includes("LET(ult;MAX('SALÁRIOS'!C2:C)") || !fonte.includes('MAX(INT(ult);em)')) achados.push('livro lido sem INT: ' + m[0]);
  }
  return achados;
}
eq(semInt(agora), [], 'nenhuma fórmula do salário usa data com hora sem INT');
{
  const plantadosInt = {
    'O70 compara a missão com o O69 cru': agora.replace(">=INT(O69));N(\\'DADOS_SALARIOS\\'!D2:D<INT(O48)", ">=O69);N(\\'DADOS_SALARIOS\\'!D2:D<INT(O48)"),
    'O72 compara o O69 cru com a emissão': agora.replace('IF(INT(O69)>INT(O38);O69', 'IF(INT(O69)>O38;O69'),
    'emissão em conta sem INT': agora.replace('em;INT(N2);', 'em;N2+0;'),
    'outra fórmula lê o início do livro': agora.replace("=COUNTA('SALÁRIOS'!A2:A)", "=COUNTIF('SALÁRIOS'!B2:B;\">0\")"),
    'o fim do livro volta sem INT': antes,
  };
  for (const [nome, fonte] of Object.entries(plantadosInt)) {
    assert.notStrictEqual(fonte, agora, 'defeito não plantado: ' + nome);
    assert(semInt(fonte).length > 0, 'defeito plantado não acendeu: ' + nome); acesos++; checks++;
  }
  plantados.__int = Object.keys(plantadosInt).length;
}

// O trecho do console parseia nos dois sentidos e roda contra um editor de mentira.
for (const r of [false, true]) {
  const f = new (Object.getPrototypeOf(async function () {}).constructor)('monaco', 'crypto', 'window', 'return ' + P.trecho(r));
  checks++;
  if (!r) {
    let gravado = null; const win = {};
    const modelo = { getValue: () => gravado === null ? instalado : gravado, setValue: v => { gravado = v; } };
    const outro = { getValue: () => '// outro arquivo', setValue: () => { throw Error('não devia gravar'); } };
    f({ editor: { getModels: () => [outro, modelo] } }, require('node:crypto').webcrypto, win).then(res => {
      assert(!String(res).startsWith('ERRO'), res); eq(gravado, P.aplicar(instalado, P.PARES, 'x')); eq(win.__salarioDatasAntes, instalado);
      console.log(JSON.stringify({ checks, resultado: 'OK', defeitos_plantados: acesos + ' de ' + (Object.keys(plantados).length - 1 + plantados.__int) + ' acenderam', escopo: 'datas do salário sem hora: preparador, trecho e fechamentos em sequência' }));
    }).catch(e => { console.error(e); process.exit(1); });
  }
}
