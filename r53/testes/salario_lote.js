'use strict';
// Falhas de serviços e relógio controlados. Não chama o Google nem mede sua latência.
const vm = require('vm'), assert = require('assert'), fs = require('fs'), path = require('path');
const {preparar, NOVO, ANCORA, ANTIGO, ENTRADA, ABRIR_NOVO} = require('../diagnostico-android/preparar_salario_lote.js');
const raiz = path.resolve(__dirname, '../..');
const original = ANCORA + 'if(salarioEditar_(e))return "salario";' +
  'if(e.range.getSheet().getName()==="CARTEIRA"&&e.range.getA1Notation()==="C27")return paleta(e);' +
  'if(r53Editar_(e))return "editor";return r53Modulo_().onEdit(e);}' +
  '\nfunction onOpen(e){e=e||{};if(typeof r53Menu_==="function")r53Menu_();menuPronto=1;}';
const projeto = {files: [{name: 'Codigo', type: 'SERVER_JS', source: original},
  {name: 'Paleta', type: 'SERVER_JS', source: '// cores já resolvidas'},
  {name: 'appsscript', type: 'JSON', source: '{"timeZone":"America/Sao_Paulo"}'}]};
const p = preparar(projeto);
assert(p.files[0].source.startsWith(NOVO));
assert(p.files[0].source.endsWith(ENTRADA));
assert.strictEqual(p.files[0].source.split(ABRIR_NOVO).length, 2);
assert.strictEqual(projeto.files[0].source, original);
assert.deepStrictEqual(p.files.slice(1, 3), projeto.files.slice(1));
// Fonte pública histórica, sem dados/credenciais; mantém o teste de atualização
// portátil também no checkout raso do CI.
const fonteAntiga = fs.readFileSync(path.join(__dirname, 'salario-lote-a2ca590-fixture.gs'), 'utf8');
const upgrade = preparar({files: [{name: 'Codigo', source: original.replace(ANCORA, ANTIGO)},
  {name: 'SalarioLote', type: 'SERVER_JS', source: fonteAntiga}]});
assert.strictEqual(upgrade.files[0].source, p.files[0].source);
assert.strictEqual(upgrade.files[1].source, p.files[3].source);
assert.throws(() => preparar({files: [{name: 'Codigo', source: original.replace(ANCORA, ANTIGO)},
  {name: 'SalarioLote', source: fonteAntiga + '// desconhecido'}]}), /divergente/);
assert.throws(() => preparar(p), /já instalada/);

// Salário por fórmula: a planilha calcula o pendente; aqui só se testa o que o script faz em volta dela.
// A fórmula em si foi conferida no Sheets da cópia de teste (24/10/2026); a VM não avalia fórmulas.
function ambiente(op = {}) {
  let relogio = 0, leituras = 0, travado = false;
  const logs = [], props = {}, celulas = {}, escritas = [], chamadas = [];
  const ctx = {console: {log: m => logs.push(m)}};
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(raiz, 'apps-script/Salarios.gs'), 'utf8'), ctx);
  for (const f of [p.files[0], p.files[3]]) vm.runInContext(f.source, ctx);
  vm.runInContext(fs.readFileSync(path.join(raiz, 'r53/diagnostico-android/salario_lote.gs'), 'utf8'), ctx);
  const VDate = vm.runInContext('Date', ctx);
  VDate.now = () => relogio;
  const hoje = 46319;
  ctx.salarioHoje_ = () => hoje;
  ctx.Utilities = {formatDate: (d, tz, f) => { const [y, m, dd] = new Date(d.getTime() - 3 * 3600000).toISOString().slice(0, 10).split('-');
    return f.replace('yyyy', y).replace('MM', m).replace('dd', dd); }};
  const tabela = op.tabela || [['SAL1:46254:46284', 46254, 46284, 'Grau 3', 300000, 3, 3, 1, 300000, 'Participação no período'],
    ['SAL1:46284:46314', 46284, 46314, 'Grau 4', 150000, 0, 3, 0.25, 37500, 'Participação no período']];
  function aux() {
    relogio += 3000; leituras++;
    const v = Array.from({length: 129}, () => Array(10).fill(''));
    v[0][1] = 'q2' in op ? (typeof op.q2 === 'function' ? op.q2(ctx) : op.q2) : 46254; v[1][1] = tabela.length; v[2][1] = tabela.reduce((a, l) => a + l[8], 0);
    v[3][1] = op.trocas || 0; v[4][1] = op.livro || 0; v[5][1] = op.linhas || 1000; v[6][1] = 30;
    tabela.forEach((l, i) => { v[9 + i] = l.slice(); });
    return v;
  }
  function escrever(aba, a, v) { assert(travado || op.semTrava, 'escrita sob bloqueio'); escritas.push([aba, a, v]); celulas[aba + '!' + a] = v; }
  function faixa(aba, a, l, c) {
    return {getValues: () => aba === 'DADOS_SALARIOS' && a === 'P2:Y130' ? aux()
        : aba === 'DADOS_SALARIOS' && !a && l === 1 && c === 1 ? (leituras++, typeof op.dados === 'function' ? op.dados(ctx) : op.dados) : [[celulas[aba + '!' + a]]],
      getValue: () => { leituras++; return aba === 'DADOS_SALARIOS' && a === 'Q5' ? (op.trocas || 0) : celulas[aba + '!' + a]; },
      setValue: v => escrever(aba, a || l + ',' + c, v), setValues: v => escrever(aba, a || l + ',' + c, v),
      setFormula: v => escrever(aba, a, v), getFormula: () => celulas[aba + '!' + a] || '', setNotes() {},
      clearContent() { escrever(aba, a, ''); return this; }};
  }
  const abas = {};
  for (const n of ['DADOS_SALARIOS', 'SALÁRIOS', 'CONFIGURAÇÃO', 'FICHA PESSOAL', 'CARTEIRA'])
    abas[n] = {getRange: (a, c, h, w) => typeof a === 'number' ? faixa(n, '', a, c) : faixa(n, a),
      getMaxRows: () => 1000, insertRowsAfter() { chamadas.push('inserir'); }, getName: () => n};
  if (!op.semExtrato) abas.EXTRATO = {getRange: (a, c) => typeof a === 'number' ? faixa('EXTRATO', '', a, c) : faixa('EXTRATO', a),
    getLastRow: () => { leituras++; return op.extratoUltima || 1; }, getName: () => 'EXTRATO'};
  const ss = {getSheetByName: n => abas[n]};
  ctx.SpreadsheetApp = {getActive: () => ss, flush() { relogio += 1000; }};
  const trava = {tryLock: () => { if (op.ocupado) return false; travado = true; return true; },
    releaseLock() { travado = false; }};
  ctx.LockService = {getDocumentLock: () => trava, getScriptLock: () => trava};
  ctx.ScriptApp = {getScriptId: () => 'copia'};
  ctx.PropertiesService = {getScriptProperties: () => ({getProperty: () => op.instalavel ? 'copia' : null}),
    getDocumentProperties: () => ({getProperty: k => props[k] || null, setProperty: (k, v) => { props[k] = v; },
      deleteProperty: k => { delete props[k]; }})};
  ctx.salarioApurar_Original = ctx.salarioApurar_;
  ctx.salarioSincronizar_ = () => { chamadas.push('sincronizar'); return []; };
  ctx.r53Modulo_ = () => ({onEdit() { chamadas.push('modulo'); relogio += op.edicaoMs || 1000; return 'XP'; }});
  ctx.r53Editar_ = () => false;
  function evento(aba, a1, l, c, antes, depois) {
    return {source: ss, oldValue: antes, value: depois, range: {getSheet: () => ({getName: () => aba}), getA1Notation: () => a1,
      getRow: () => l, getLastRow: () => l, getColumn: () => c, getLastColumn: () => c,
      getCell: () => ({getValue: () => { leituras++; return op.caixa; }})}};
  }
  return {ctx, ss, props, escritas, chamadas, logs, evento, hoje, leituras: () => leituras, put: (aba, a, v) => { celulas[aba + '!' + a] = v; },
    livro: () => escritas.filter(e => e[0] === 'SALÁRIOS'), trocas: () => escritas.filter(e => e[0] === 'DADOS_SALARIOS' && e[1] === '')};
}
let casos = 0;
{
  // Congelar copia a tabela da fórmula para o livro, depois da última linha, com a data de hoje.
  const a = ambiente({livro: 3, semTrava: true});
  const r = a.ctx.salarioCongelar_(a.ss, a.hoje);
  assert.strictEqual(r.novos, 2); assert.strictEqual(r.proximo, 46254 + 3 * 30);
  const [[, onde, linhas]] = a.livro();
  assert.strictEqual(onde, '5,1'); assert.strictEqual(linhas.length, 2);
  assert.deepStrictEqual(JSON.parse(JSON.stringify(linhas.map(l => [l[0], l[4], l[9]]))), [['SAL1:46254:46284', 'Grau 3', 300000], ['SAL1:46284:46314', 'Grau 4', 37500]]);
  assert.strictEqual(linhas[0][3].toISOString().slice(0, 10), '2026-10-24');
  casos += 4;
}
{
  // Sem nada vencido: não grava no livro.
  const a = ambiente({tabela: [], semTrava: true});
  assert.strictEqual(a.ctx.salarioCongelar_(a.ss, a.hoje).novos, 0); assert.strictEqual(a.livro().length, 0);
  casos++;
}
{
  // Trocas que mudam o passado viram uma linha "valor até a troca"; nada de apuração na edição.
  const a = ambiente({trocas: 2});
  a.ctx.salarioApurar_ = () => { throw Error('não deve apurar na edição'); };
  a.ctx.salarioEditar_(a.evento('CONFIGURAÇÃO', 'O62', 62, 15, '1', '3'));
  a.ctx.salarioEditar_(a.evento('FICHA PESSOAL', 'AB11', 11, 28, 'Grau 4', 'Grau 3'));
  a.ctx.salarioEditar_(a.evento('CONFIGURAÇÃO', 'O43', 43, 15, '0.25', '0.5'));
  a.ctx.salarioEditar_(a.evento('CONFIGURAÇÃO', 'O44', 44, 15, 'TRUE', 'FALSE'));
  const t = JSON.parse(JSON.stringify(a.escritas.filter(e => e[0] === 'DADOS_SALARIOS' && /,8$/.test(e[1])).map(e => [e[1]].concat(e[2][0]))));
  assert.deepStrictEqual(t, [['4,8', a.hoje, 'peso:Curta', 1], ['5,8', a.hoje, 'Grau', 'Grau 4'], ['6,8', a.hoje, 'minimo', 0.25], ['7,8', a.hoje, 'verifica', true]]);
  assert.strictEqual(a.props.salario_trocas, '6'); assert.strictEqual(a.leituras(), 1, 'só a primeira troca lê a contagem');
  assert(!a.chamadas.includes('sincronizar'), 'Grau não relê as missões');
  casos += 2;
}
{
  // Sem valor anterior (colagem, célula vazia) ou sem mudança: não registra.
  const a = ambiente();
  a.ctx.salarioEditar_(a.evento('CONFIGURAÇÃO', 'O62', 62, 15, undefined, '3'));
  a.ctx.salarioEditar_(a.evento('CONFIGURAÇÃO', 'O54', 54, 15, '150000', '150000'));
  assert.strictEqual(a.escritas.filter(e => e[0] === 'DADOS_SALARIOS').length, 0);
  casos++;
}
{
  // Missão: só registra (sincroniza), sem apurar.
  const a = ambiente();
  a.ctx.salarioApurar_ = () => { throw Error('não deve apurar na edição'); };
  a.ctx.salarioEditar_(a.evento('FICHA PESSOAL', 'AW15', 15, 49, '', 'Mesa 1'));
  assert(a.chamadas.includes('sincronizar'));
  casos++;
}
{
  // Edição rápida: entrega a edição e congela depois; a segunda edição pula pela data guardada, sem ler.
  const a = ambiente();
  assert.strictEqual(a.ctx.onEdit(a.evento('FICHA', 'E5', 5, 5, 'a', 'b')), 'XP');
  assert.strictEqual(a.livro().length, 1); assert.strictEqual(Number(a.props.salario_proximo), 46254 + 3 * 30);
  const lidas = a.leituras();
  a.ctx.onEdit(a.evento('FICHA', 'E6', 6, 5, 'a', 'b'));
  assert.strictEqual(a.leituras(), lidas); assert.strictEqual(a.livro().length, 1);
  casos += 3;
}
{
  // Edição lenta (18–24 s medidos): a edição termina e o congelamento fica para depois; o pendente já aparece por fórmula.
  const a = ambiente({edicaoMs: 20000});
  assert.strictEqual(a.ctx.onEdit(a.evento('FICHA', 'E5', 5, 5, 'a', 'b')), 'XP');
  assert.strictEqual(a.livro().length, 0);
  casos++;
}
{
  // Abrir no PC congela; rotina instalável ativa não congela pelo acionador simples.
  const a = ambiente();
  a.ctx.onOpen({}); assert.strictEqual(a.livro().length, 1);
  const b = ambiente({instalavel: true});
  b.ctx.onOpen({}); assert.strictEqual(b.livro().length, 0);
  casos += 2;
}
{
  // Bloqueio ocupado: não congela e tenta de novo depois.
  const a = ambiente({ocupado: true});
  a.ctx.onOpen({}); assert.strictEqual(a.livro().length, 0); assert(!a.props.salario_proximo);
  casos++;
}
{
  // ± GASTO / GANHO: vira linha do extrato e a caixa limpa, sem ler a ficha e sem passar pelo resto da edição.
  const a = ambiente();
  a.props.salario_extrato = '1'; a.props.salario_proximo = String(a.hoje + 30);
  assert.strictEqual(a.ctx.onEdit(a.evento('FICHA PESSOAL', 'O86', 86, 15, undefined, '-500')), 'salario');
  a.ctx.onEdit(a.evento('FICHA PESSOAL', 'O86', 86, 15, undefined, '2.000'));
  const ex = a.escritas.filter(e => e[0] === 'EXTRATO');
  assert.deepStrictEqual(JSON.parse(JSON.stringify(ex.map(e => [e[1], e[2][0][1], e[2][0][2]]))), [['3,1', -500, 'Ficha · gasto'], ['4,1', 2000, 'Ficha · ganho']]);
  assert.strictEqual(a.escritas.filter(e => e[1] === 'O86' && e[2] === '').length, 2);
  assert.strictEqual(a.props.salario_extrato, '3'); assert.strictEqual(a.leituras(), 0);
  assert(!a.chamadas.includes('modulo'), 'não roda cartões/XP');
  casos += 5;
}
{
  // Cópia sem a contagem: lê a última linha do extrato uma vez. Fórmula/colagem sem e.value: lê a caixa.
  const a = ambiente({extratoUltima: 4, caixa: 750});
  a.ctx.salarioEditar_(a.evento('FICHA PESSOAL', 'O86', 86, 15, undefined, undefined));
  const [[, onde, [[, v]]]] = a.escritas.filter(e => e[0] === 'EXTRATO');
  assert.strictEqual(onde, '5,1'); assert.strictEqual(v, 750); assert.strictEqual(a.props.salario_extrato, '4');
  casos += 3;
}
{
  // Texto ou caixa apagada: nada entra no extrato. Sem EXTRATO (não preparado): O86 segue como saldo manual.
  const a = ambiente();
  assert.strictEqual(a.ctx.salarioEditar_(a.evento('FICHA PESSOAL', 'O86', 86, 15, '-5', 'abc')), true);
  assert.strictEqual(a.ctx.salarioEditar_(a.evento('FICHA PESSOAL', 'O86', 86, 15, '-5', undefined)), true);
  assert.strictEqual(a.escritas.length, 0);
  const b = ambiente({semExtrato: true});
  assert.strictEqual(b.ctx.onEdit(b.evento('FICHA PESSOAL', 'O86', 86, 15, '100', '200')), 'XP');
  assert.strictEqual(b.escritas.filter(e => e[1] === 'O86').length, 0);
  casos += 3;
}
{
  // Rotina instalável ativa: o acionador simples deixa o lançamento para ela (não lança em dobro).
  const a = ambiente({instalavel: true});
  a.props.salario_extrato = '0';
  a.ctx.salarioEditar_(a.evento('FICHA PESSOAL', 'O86', 86, 15, undefined, '-500'));
  assert.strictEqual(a.escritas.length, 0);
  const e = a.evento('FICHA PESSOAL', 'O86', 86, 15, undefined, '-500'); e.salarioInstalavel_ = true;
  a.ctx.salarioEditar_(e);
  assert.strictEqual(a.escritas.filter(x => x[0] === 'EXTRATO').length, 1);
  casos += 2;
}
{
  // Números como o Android manda: sinal de menos tipográfico, ¥, milhar com ponto, decimal com vírgula.
  const a = ambiente();
  assert.deepStrictEqual(['−500', '¥ 2.000', '1.500,5', '2,5', '12', 'abc', ''].map(a.ctx.salarioNumero_), [-500, 2000, 1500.5, 2.5, 12, NaN, NaN]);
  casos++;
}
{
  // Migração: o saldo de O86 vira a primeira linha do extrato; O86 limpa e vira a caixa; só uma vez.
  const a = ambiente({semExtrato: true, semTrava: true});
  const feitos = [];
  const cadeia = nome => new Proxy(function () {}, {get: (_, k) => k === 'then' ? undefined : (...x) => { feitos.push([nome, k, x]); return cadeia(nome); }});
  let novo;
  a.ss.insertSheet = n => { novo = {getRange: (r, c, h, w) => { const g = cadeia('EXTRATO'); return typeof r === 'number' ? {setValues: v => feitos.push(['EXTRATO', 'linhas', [r, v]])} : g; },
    setFrozenRows() {}, setColumnWidth() {}, hideSheet: () => feitos.push(['EXTRATO', 'hide'])}; return novo; };
  const ficha = a.ss.getSheetByName('FICHA PESSOAL');
  const o86 = new Proxy({getValue: () => 150000, getFormula: () => ''}, {get: (t, k) => t[k] || ((...x) => { feitos.push(['O86', k, x]); return cadeia('O86'); })});
  ficha.getRange = r => r === 'O86' ? o86 : cadeia(r);
  a.ctx.SpreadsheetApp.newDataValidation = () => cadeia('validacao');
  assert.strictEqual(a.ctx.salarioPrepararCarteira_(a.ss), true);
  const linhas = feitos.find(f => f[1] === 'linhas')[2];
  assert.strictEqual(linhas[0], 2); assert.strictEqual(linhas[1][0][1], 150000);
  assert(feitos.some(f => f[0] === 'O86' && f[1] === 'clearContent'));
  assert(feitos.some(f => f[0] === 'W86' && f[1] === 'setFormula' && /N\(O86\)\+IFERROR\(SUM\(EXTRATO!B2:B\);0\)/.test(f[2][0])));
  assert.strictEqual(a.props.salario_extrato, '1');
  a.ss.getSheetByName = n => n === 'EXTRATO' ? novo : null;
  assert.strictEqual(a.ctx.salarioPrepararCarteira_(a.ss), false);
  casos += 6;
}
{
  // Levar o extrato a uma cópia que já tem o salário por fórmula: troca o bloco inteiro e o desvio; recusa repetir.
  const {preparar: comExtrato} = require('../diagnostico-android/preparar_salario_extrato.js');
  const antes = fs.readFileSync(path.join(__dirname, 'salarios-com-formula.gs'), 'utf8');
  const novo = comExtrato({files: [{name: 'Codigo', source: antes}]});
  const atual = fs.readFileSync(path.join(raiz, 'apps-script/Salarios.gs'), 'utf8');
  assert.strictEqual(require('../diagnostico-android/preparar_xp_atualizar.js').preparar(require('../diagnostico-android/preparar_missoes_sem_registros.js').preparar(require('../diagnostico-android/preparar_missoes_enxutas.js').preparar(require('../diagnostico-android/preparar_missoes.js').preparar(novo.files[0].source)))), atual);
  assert.throws(() => comExtrato(novo), /já atualizado/);
  // Cópia que já tinha o extrato: só o bloco muda, o desvio não duplica.
  const velho = novo.files[0].source.replace('SALARIO_.f.ultimos', 'SALARIO_.f.ultimosVelho');
  const de_novo = comExtrato({files: [{name: 'Codigo', source: velho}]}).files[0].source;
  assert.strictEqual(de_novo.split('salarioGasto_(ss,r,e))return true;').length, 2);
  assert.strictEqual(de_novo.split('function salarioGasto_(').length, 2);
  assert.strictEqual(de_novo.split('function salarioNumero_(').length, 2);
  // Cópia com o extrato da primeira versão (sem marcador de fim): o bloco antigo some inteiro.
  const semMarca = antes.replace(/\n$/, '');
  const primeira = comExtrato({files: [{name: 'Codigo', source: semMarca + '\nfunction depois_(){}\n'}]}).files[0].source;
  assert(primeira.endsWith('// FIM DO SALÁRIO POR FÓRMULA\nfunction depois_(){}\n'));
  const v1 = fs.readFileSync(path.join(__dirname, 'salarios-extrato-v1.gs'), 'utf8');
  const segunda = comExtrato({files: [{name: 'Codigo', source: v1 + 'function depois_(){}\n'}]}).files[0].source;
  assert.strictEqual(segunda.split('salarioCorrigirData_(ss,r,e))return true;').length, 2);
  assert.strictEqual(segunda.split('function salarioGasto_(').length, 2);
  assert(segunda.endsWith('// FIM DO SALÁRIO POR FÓRMULA\nfunction depois_(){}\n'));
  assert.strictEqual(segunda.split('salarioEmitir_(ss,r,e,emitir))return true;').length, 2);
  assert.strictEqual(segunda.split("'reemitirCarteira')").length, 2);
  // Projeto com o desvio do primeiro nome (versão que não ficou): a linha sai e a emissão entra uma vez.
  const linhaNome = "  if(SALARIO_.formula&&nome&&salarioPrimeiroNome_(e)){return false;}\n";
  const comNome = segunda.replace('SALARIO_.f.ultimos', 'SALARIO_.f.ultimosVelho')
    .replace('salarioEmitir_(ss,r,e,emitir))return true;\n', 'salarioEmitir_(ss,r,e,emitir))return true;\n' + linhaNome);
  const semNome = comExtrato({files: [{name: 'Codigo', source: comNome}]}).files[0].source;
  assert(!semNome.includes('salarioPrimeiroNome_')); assert.strictEqual(semNome.split('salarioEmitir_(ss,r,e,emitir))return true;').length, 2);
  casos += 11;
}
{
  // Corrigir data pelo celular: nome em BI11, data em BO11; resultado na caixa da data.
  const dados = ctx => { const v = Array.from({length: 6}, () => Array(17).fill(''));
    v[1][16] = new (vm.runInContext('Date', ctx))(Date.UTC(2026, 7, 20, 15)); 
    // Q2 vem como Date (formato de data), como no Sheets.
    v[1].splice(0, 5, 'id1', 'Missão A', 'Curta', 46300, true); v[2].splice(0, 5, 'id2', "'-Missão B", 'Longa', 46310, true);
    v[3].splice(0, 5, 'id3', 'Missão C', 'Curta', 46301, false); v[4].splice(0, 5, 'id4', 'Dupla', 'Curta', 46300, true); v[5].splice(0, 5, 'id5', 'dupla ', 'Curta', 46301, true); return v; };
  const caso = (nome, data, campo = 'data') => {
    const a = ambiente({dados});
    a.ctx.salarioEditar_(campo === 'data' ? (a.put('FICHA PESSOAL', 'BI11', nome), a.evento('FICHA PESSOAL', 'BO11', 11, 67, undefined, data))
      : (a.put('FICHA PESSOAL', 'BO11', data), a.evento('FICHA PESSOAL', 'BI11', 11, 61, undefined, nome)));
    const ult = a.escritas.filter(e => e[1] === 'BO11').pop();
    return {a, msg: ult && ult[2], dia: a.escritas.filter(e => e[0] === 'DADOS_SALARIOS').map(e => [e[1], e[2]])};
  };
  let r = caso('missão a', '20/10/2026');
  assert.strictEqual(r.msg, '✓ missão a: 20/10/2026'); assert.deepStrictEqual(r.dia, [['2,4', 46315]]);
  assert.strictEqual(r.a.escritas.filter(e => e[1] === 'BI11').pop()[2], '');
  assert.deepStrictEqual(caso('-Missão B', '21/10').dia, [['3,4', 46316]]);
  assert.strictEqual(caso('Missão C', '20/10/2026').msg, '⚠ Nenhuma missão com esse nome');
  assert.strictEqual(caso('dupla', '20/10/2026').msg, '⚠ Mais de uma missão com esse nome');
  assert.strictEqual(caso('Missão A', '01/08/2026').msg, '⚠ Essa data cai num período já pago');
  assert.strictEqual(caso('Missão A', '30/10/2026').msg, '⚠ A data não pode ser depois de hoje');
  assert.strictEqual(caso('Missão A', '31/02/2026').msg, '⚠ Data inválida: use dd/mm/aaaa');
  // Nome escrito com a data vazia ou com o resultado anterior na caixa: não faz nada.
  r = caso('Missão A', '', 'nome'); assert.strictEqual(r.a.escritas.length, 0); assert.strictEqual(r.a.leituras(), 1);
  r = caso('Missão A', '✓ Missão A: 20/10/2026', 'nome'); assert.strictEqual(r.a.escritas.length, 0);
  // Nome e depois data no mesmo arquivo: a data usa o nome guardado, sem ler a caixa.
  {
    const a = ambiente({dados});
    a.ctx.salarioEditar_(a.evento('FICHA PESSOAL', 'BI11', 11, 61, undefined, 'Missão A'));
    const lidas = a.leituras();
    a.ctx.salarioEditar_(a.evento('FICHA PESSOAL', 'BO11', 11, 67, undefined, '20/10/2026'));
    assert.strictEqual(a.leituras() - lidas, 1, 'só a leitura de DADOS_SALARIOS');
    assert.strictEqual(a.escritas.filter(e => e[1] === 'BO11').pop()[2], '✓ Missão A: 20/10/2026');
    assert.strictEqual(a.props.salario_correcao_nome, '');
  }
  // Data primeiro, nome depois: corrige ao escrever o nome.
  assert.deepStrictEqual(caso('Missão A', '20/10/2026', 'nome').dia, [['2,4', 46315]]);
  casos += 15;
}
{
  // Emissão: só a caixa EMITIR grava a data (N2), uma vez; escrever em O38 devolve a fórmula; nome não emite.
  const emitir = (op, aba, a1, l, c, antes, depois) => {
    const a = ambiente(op);
    const r = a.ctx.salarioEditar_(a.evento(aba, a1, l, c, antes, depois));
    const w = k => a.escritas.filter(e => e[1] === k).map(e => e[2] && e[2].toISOString ? e[2].toISOString().slice(0, 10) : e[2]);
    return {r, a, n2: w('N2'), o38: w('O38'), at3: w('AT3'), o39: w('O39'), o46: w('O46')};
  };
  let r = emitir({}, 'CARTEIRA', 'AT3', 3, 46, 'FALSE', 'TRUE');
  assert.strictEqual(r.r, true); assert.deepStrictEqual(r.n2, ['2026-10-24']); assert.deepStrictEqual(r.at3, [false]);
  assert.deepStrictEqual(r.o39, [false]);
  r = emitir({}, 'CONFIGURAÇÃO', 'O39', 39, 15, 'FALSE', 'TRUE'); assert.deepStrictEqual(r.n2, ['2026-10-24']);
  // Já emitida: não regrava; avisa no painel e desmarca.
  {
    const a = ambiente(); a.put('DADOS_SALARIOS', 'N2', 46315);
    a.ctx.salarioEditar_(a.evento('CARTEIRA', 'AT3', 3, 46, 'FALSE', 'TRUE'));
    assert.strictEqual(a.escritas.filter(e => e[1] === 'N2').length, 0);
    assert(/^⚠ Carteira já emitida em 20\/10\/2026/.test(a.escritas.filter(e => e[1] === 'O46').pop()[2]));
    assert.strictEqual(a.escritas.filter(e => e[1] === 'AT3').pop()[2], false);
  }
  // Desmarcar não faz nada.
  r = emitir({}, 'CARTEIRA', 'AT3', 3, 46, 'TRUE', 'FALSE'); assert.strictEqual(r.a.escritas.length, 0);
  // Corrigir a data em O38: a fórmula volta sempre; data válida vai para N2.
  r = emitir({}, 'CONFIGURAÇÃO', 'O38', 38, 15, '', '24/10/2026');
  assert.strictEqual(r.r, true); assert.deepStrictEqual(r.n2, ['2026-10-24']); assert(/^=IF\(ISNUMBER\('DADOS_SALARIOS'!N2\)/.test(r.o38[0]));
  assert.strictEqual(r.a.livro().length, 0, 'sem emissão anterior: nada a congelar');
  assert.deepStrictEqual(emitir({}, 'CONFIGURAÇÃO', 'O38', 38, 15, '', '46319').n2, ['2026-10-24'], 'número de série');
  // Sem emissão, data passada não vale: seria salário retroativo.
  r = emitir({}, 'CONFIGURAÇÃO', 'O38', 38, 15, '', '15/10/2026'); assert.deepStrictEqual(r.n2, []);
  assert.strictEqual(r.o46.pop(), '⚠ A emissão só pode ir para frente: use 24/10/2026 ou depois.');
  r = emitir({}, 'CONFIGURAÇÃO', 'O38', 38, 15, '', '30/10/2026'); assert.deepStrictEqual(r.n2, []); assert.strictEqual(r.o46.pop(), '⚠ A emissão não pode ser depois de hoje.');
  r = emitir({}, 'CONFIGURAÇÃO', 'O38', 38, 15, '', 'ontem'); assert.deepStrictEqual(r.n2, []); assert(/^⚠ Data de emissão inválida/.test(r.o46.pop()));
  r = emitir({}, 'CONFIGURAÇÃO', 'O38', 38, 15, '20/10/2026', undefined); assert.deepStrictEqual(r.n2, []); assert.strictEqual(r.o38.length, 1);
  assert(!r.o46.some(t => /^⚠/.test(t)), 'apagar só devolve a fórmula');
  {
    // Já emitida: congela o vencido antes, registra a troca e grava a data nova.
    const a = ambiente(); a.put('DADOS_SALARIOS', 'N2', 46315); a.props.salario_proximo = '99999';
    a.ctx.salarioEditar_(a.evento('CONFIGURAÇÃO', 'O38', 38, 15, '20/10/2026', '22/10/2026'));
    const ordem = a.escritas.map(e => e[0] === 'SALÁRIOS' ? 'livro' : e[1]).filter(k => ['livro', 'N2'].includes(k) || /,8$/.test(k));
    assert.deepStrictEqual(ordem, ['livro', '2,8', 'N2'], 'livro antes da troca e da data');
    assert.deepStrictEqual(JSON.parse(JSON.stringify(a.escritas.find(e => e[1] === '2,8')[2][0].slice(1))), ['emissão', 46315]);
    assert.strictEqual(a.escritas.find(e => e[1] === 'N2')[2].toISOString().slice(0, 10), '2026-10-22');
    assert.strictEqual(a.props.salario_proximo, undefined);
  }
  {
    // Já emitida: voltar a data é recusado sem congelar nem gravar nada.
    const a = ambiente(); a.put('DADOS_SALARIOS', 'N2', 46315);
    a.ctx.salarioEditar_(a.evento('CONFIGURAÇÃO', 'O38', 38, 15, '20/10/2026', '01/08/2026'));
    assert.strictEqual(a.livro().length, 0); assert(!a.escritas.some(e => e[1] === 'N2' || /,8$/.test(e[1])));
    assert.strictEqual(a.escritas.filter(e => e[1] === 'O46').pop()[2], '⚠ A emissão só pode ir para frente: use 20/10/2026 ou depois.');
  }
  // Escrever o nome não emite.
  r = emitir({}, 'CARTEIRA', 'O9', 9, 15, 'Coloque o nome do personagem aqui', 'Yuji'); assert.deepStrictEqual(r.n2, []); assert.deepStrictEqual(r.o38, []);
  casos += 28;
}
{
  // Congelar: Q2 chega como Date; sem emissão (Q2 vazio) não lê de novo até amanhã.
  const a = ambiente({tabela: [], semTrava: true});
  assert.strictEqual(a.ctx.salarioCongelar_(a.ss, a.hoje).proximo, 46254 + 30, 'Q2 número');
  const d = ambiente({tabela: [], semTrava: true, q2: ctx => new (vm.runInContext('Date', ctx))(Date.UTC(2026, 7, 20, 15))});
  assert.strictEqual(d.ctx.salarioCongelar_(d.ss, d.hoje).proximo, 46254 + 30, 'Q2 como Date (formato de data)');
  const v = ambiente({tabela: [], semTrava: true, q2: ''});
  // 27/10/2026: sem emissão, a próxima conferência fica para longe; emitir apaga a data (abertura_salario.js).
  assert.strictEqual(v.ctx.salarioCongelar_(v.ss, v.hoje).proximo, v.hoje + 3650, 'sem emissão: longe');
  casos += 3;
}
{
  // Preparar uma cópia já instalada: patch exato, recusa repetição.
  const {preparar} = require('../diagnostico-android/preparar_salario_formula.js');
  const antigo = fs.readFileSync(path.join(__dirname, 'salarios-antes-formula.gs'), 'utf8');
  const proj = {files: [{name: 'Codigo', source: antigo}, {name: 'SalarioLote', source: '// antigo'}]};
  const novo = preparar(proj);
  assert(novo.files[0].source.includes('SALARIO_.formula = true;'));
  assert.throws(() => preparar(novo), /já instalado/);
  casos += 2;
}
console.log(JSON.stringify({resultado: 'OK', casos, limite: 'VM; a fórmula foi conferida no Sheets da cópia de teste, não aqui.'}));
