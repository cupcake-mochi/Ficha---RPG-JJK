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
assert.throws(() => preparar({files: []}), /Codigo/);

function ambiente(op = {}) {
  let relogio = 0, leituras = 0, travado = false, falha = null;
  const logs = [], props = {}, grav = {}, fila = [], livro = [], commits = [];
  let estado;
  const ctx = {console: {log: m => logs.push(m)}};
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(raiz, 'apps-script/Salarios.gs'), 'utf8'), ctx);
  for (const f of [p.files[0], p.files[3]]) vm.runInContext(f.source, ctx);
  const VDate = vm.runInContext('Date', ctx);
  VDate.now = () => relogio;
  const emissao = ctx.salarioDiaISO_('2026-10-20'), hoje = ctx.salarioDiaISO_('2026-12-25');
  const data = d => new VDate((d - 25569) * 864e5 + 12 * 3600000);
  estado = JSON.stringify({versao: 1, inicio: emissao, graus: [[emissao, 'Grau 4']], agenda: 'preservada'});
  ctx.salarioHoje_ = () => hoje;
  ctx.Utilities = {formatDate: d => d.toISOString().slice(0, 10)};
  function problema(k) {
    if (falha === k) { falha = null; throw Error('Falha injetada: ' + k); }
  }
  function grade() {
    relogio += 2000; leituras++;
    const g = Array.from({length: 1000}, () => Array(14).fill(''));
    g[1].splice(0, 7, 'm1', 'Curta', 'Curta', emissao + 3, true, '49:15', emissao + 3);
    g[2].splice(0, 7, 'm2', 'Longa', 'Longa', emissao + 35, true, '49:16', emissao + 35);
    g[3].splice(0, 7, 'm3', 'Removida', 'Longa', emissao + 40, false, '49:17', emissao + 40);
    g[1][11] = estado;
    const pagos = op.resumoVelho ? [] : livro;
    const N = [data(emissao), true, 30, 3, 0.25, true, data(emissao + 30),
      150000, 300000, 600000, 1200000, 2400000, 1, 1, 2, 3, 1, 1, 'Grau 4', 'Teste Salário',
      pagos.length, 1000, pagos.length ? pagos[pagos.length - 1][2] : '', pagos.map(l => l[0]).join('|')];
    N.forEach((v, i) => { g[i + 1][13] = v; });
    return g;
  }
  function escrever(k, v, inicio) {
    assert(travado, 'salário deve escrever sob bloqueio');
    problema(k);
    fila.push(() => {
      grav[k] = v; commits.push(k);
      if (k === 'livro') v.forEach((r, i) => { livro[inicio - 2 + i] = r; });
      if (k === 'dados L2') estado = v;
    });
  }
  const faixa = k => ({setValue: v => escrever(k, v), setValues: v => escrever(k, v)});
  const abas = {
    DADOS_SALARIOS: {getRange: a => typeof a === 'number' ? {getValues: grade} : faixa('dados ' + a)},
    'SALÁRIOS': {getRange: (inicio, col, n) => ({setValues: v => escrever('livro', v, inicio),
      getValues: () => livro.slice(inicio - 2, inicio - 2 + n)}),
      getLastRow: () => livro.length + 1, getMaxRows: () => 1000, insertRowsAfter() { throw Error('não deve expandir'); }},
    'CONFIGURAÇÃO': {getRange: a => faixa('cfg ' + a)}
  };
  const ss = {getSheetByName: n => abas[n]};
  ctx.SpreadsheetApp = {getActive: () => ss, flush() {
    relogio += travado ? (op.flushMs || 1000) : 500;
    if (travado) {
      if (falha && falha.startsWith('flush:')) {
        const n = Number(falha.split(':')[1]); falha = null;
        fila.splice(0, n).forEach(fn => fn()); fila.length = 0;
        throw Error('Falha injetada no flush');
      }
      fila.splice(0).forEach(fn => fn());
    } else problema('flush-edicao');
  }};
  ctx.LockService = {getDocumentLock: () => ({tryLock: () => {
    if (op.lockOcupado) return false;
    assert(!travado); travado = true;
    if (op.outroFechou) props.salario_proximo = String(emissao + 90);
    return true;
  }, releaseLock() {
    // Falha de setter também pode confirmar parte da fila antes do erro.
    fila.splice(0).forEach(fn => fn()); travado = false;
  }})};
  ctx.ScriptApp = {getScriptId: () => 'copia'};
  ctx.PropertiesService = {getScriptProperties: () => ({getProperty: () => op.instalavel ? 'copia' : 'original'}),
    getDocumentProperties: () => ({getProperty: k => props[k] || null, setProperty(k, v) {
      problema('prop ' + k);
      if (k === 'salario_proximo' && props.salario_lote_reparar) assert.strictEqual(fila.length, 0, 'cache após flush');
      props[k] = v;
    }, deleteProperty: k => { delete props[k]; }})};
  const eventos = [];
  let rota = 'modulo', duracaoEdicao = 1000;
  ctx.salarioEditar_ = e => { eventos.push(['salarioEditar', e]); return rota === 'salario'; };
  ctx.r53Editar_ = e => { eventos.push(['editor', e]); return rota === 'editor'; };
  ctx.paleta = e => { eventos.push(['paleta', e]); return 'cores'; };
  ctx.r53Modulo_ = () => ({onEdit(e) {
    eventos.push(['modulo', e]); relogio += duracaoEdicao; problema('edicao'); return 'XP';
  }});
  function evento(aba = 'FICHA', a1 = 'E5', l = 5, c = 5) {
    return {source: ss, value: 'valor original', oldValue: 'anterior', range: {
      getSheet: () => ({getName: () => aba}), getA1Notation: () => a1,
      getRow: () => l, getLastRow: () => l, getColumn: () => c, getLastColumn: () => c}};
  }
  return {ctx, ss, props, grav, livro, logs, eventos, evento, emissao, hoje,
    executar: e => ctx.onEdit(e || evento()), abrir: () => ctx.onOpen({}),
    falhar: k => { falha = k; }, rota: r => { rota = r; }, duracao: n => { duracaoEdicao = n; },
    leituras: () => leituras, estado: () => JSON.parse(estado), travado: () => travado,
    commits: () => commits, tempo: () => relogio};
}
function conferir(a) {
  assert.deepStrictEqual(a.livro.map(l => [l[0], l[6], l[9]]), [
    ['SAL1:' + a.emissao + ':' + (a.emissao + 30), 1, 75000],
    ['SAL1:' + (a.emissao + 30) + ':' + (a.emissao + 60), 2, 112500]]);
  assert.strictEqual(a.estado().inicio, a.emissao + 60);
  assert.strictEqual(a.estado().agenda, 'preservada');
  assert.strictEqual(Number(a.props.salario_proximo), a.emissao + 90);
  assert(!a.props.salario_lote_reparar);
  assert(!a.travado());
  assert(a.grav['cfg O48']); assert(a.grav['cfg O69:O72']);
}
let casos = 0;
{
  // Abertura: fecha os dois períodos sem edição nenhuma; a segunda abertura não lê a planilha.
  const a = ambiente();
  a.abrir(); conferir(a);
  assert.strictEqual(a.eventos.length, 0);
  const lidas = a.leituras(); a.abrir();
  assert.strictEqual(a.leituras(), lidas); assert.strictEqual(a.livro.length, 2);
  assert(a.logs.some(l => l.startsWith('R53_ABRIR ') && JSON.parse(l.slice(10)).fechou === true));
  casos += 2;
}
{
  // Caixa do celular: só fecha o salário, desmarca e não chama a edição original.
  const a = ambiente(), e = a.evento('CONFIGURAÇÃO', 'O75', 75, 15);
  let desmarcou = null; e.value = 'TRUE'; e.range.setValue = v => { desmarcou = v; };
  a.executar(e); conferir(a);
  assert.strictEqual(desmarcou, false); assert.strictEqual(a.eventos.length, 0);
  const d = a.evento('CONFIGURAÇÃO', 'O75', 75, 15); d.value = 'FALSE';
  a.executar(d); assert.strictEqual(a.eventos.length, 0); assert.strictEqual(a.livro.length, 2);
  casos += 2;
}
{
  // Rotina instalável ativa: a abertura não fecha nada.
  const a = ambiente({instalavel: true});
  a.abrir(); assert.strictEqual(a.livro.length, 0); assert.strictEqual(a.leituras(), 0);
  casos++;
}
{
  const a = ambiente({flushMs: 14000}), e = a.evento();
  assert.strictEqual(a.executar(e), 'XP'); conferir(a);
  assert(a.eventos.every(([, ev]) => ev === e), 'evento completo e a mesma instância');
  assert.strictEqual(e.value, 'valor original'); assert.strictEqual(e.oldValue, 'anterior');
  assert.strictEqual(a.eventos.filter(([r]) => r === 'modulo').length, 1);
  const medicao = JSON.parse(a.logs.find(l => l.startsWith('R53_ONEDIT ')).slice(11));
  assert.strictEqual(medicao.ms, a.tempo()); assert(medicao.ms > 12000); assert.strictEqual(medicao.fase, 'concluido');
  const antes = a.leituras(); a.executar(); assert.strictEqual(a.leituras(), antes); conferir(a);
  delete a.props.salario_proximo; a.executar(); conferir(a); casos++;
}
// Escritas e flush incertos; resumo por fórmulas deliberadamente antigo na recuperação.
for (const ponto of ['livro', 'dados L2', 'cfg O48', 'cfg O69:O72', 'cfg O46',
  'flush:0', 'flush:1', 'flush:2', 'flush:5', 'prop salario_proximo']) {
  const a = ambiente({resumoVelho: true}), e = a.evento();
  a.falhar(ponto); a.executar(e);
  assert(a.props.salario_lote_reparar, ponto + ': reparação durável');
  assert(!a.props.salario_proximo, ponto + ': não pode pular a tentativa seguinte');
  const pagosAntes = JSON.stringify(a.livro);
  a.executar(); conferir(a);
  if (JSON.parse(pagosAntes).length === 2) assert.strictEqual(JSON.stringify(a.livro), pagosAntes, 'créditos imutáveis: ' + ponto);
  const antes = a.leituras(); a.executar(); assert.strictEqual(a.leituras(), antes); conferir(a);
  assert.strictEqual(a.eventos.filter(([r, ev]) => r === 'modulo' && ev === e).length, 1, 'sem replay da edição');
  casos++;
}
{
  const a = ambiente(); a.falhar('prop salario_lote_reparar'); a.executar();
  assert.strictEqual(a.livro.length, 0); assert.strictEqual(a.commits().length, 0);
  a.executar(); conferir(a); casos++;
}
{
  const a = ambiente(); a.duracao(14000); a.executar();
  assert.strictEqual(a.leituras(), 0); assert.strictEqual(a.eventos.filter(([r]) => r === 'modulo').length, 1);
  a.duracao(1000); a.executar(); conferir(a); casos++;
}
for (const [aba, a1, l, c] of [['CARTEIRA', 'C27', 27, 3], ['CONFIGURAÇÃO', 'O41', 41, 15],
  ['FICHA PESSOAL', 'AB11', 11, 28], ['FICHA PESSOAL', 'AW15', 15, 49]]) {
  const a = ambiente(); a.props.salario_proximo = '1';
  const e = a.evento(aba, a1, l, c); a.executar(e);
  assert.strictEqual(a.leituras(), 0); assert.strictEqual(a.livro.length, 0);
  assert(a.eventos.every(([, ev]) => ev === e));
  if (a1 === 'C27') assert.strictEqual(a.eventos.filter(([r]) => r === 'paleta').length, 1);
  else assert(!a.props.salario_proximo);
  casos++;
}
{
  const a = ambiente(); a.props.salario_proximo = String(a.hoje + 100); a.duracao(14000);
  a.executar(a.evento('CONFIGURAÇÃO', 'O41', 41, 15));
  assert(!a.props.salario_proximo, 'edição lenta de regra também invalida o cache');
  assert.strictEqual(a.leituras(), 0); a.duracao(1000); a.executar(); conferir(a); casos++;
}
for (const rota of ['salario', 'editor']) {
  const a = ambiente(); a.rota(rota); a.executar(); conferir(a);
  assert.strictEqual(a.eventos.filter(([r]) => r === 'modulo').length, 0); casos++;
}
for (const op of [{lockOcupado: true}, {instalavel: true}, {outroFechou: true}]) {
  const a = ambiente(op); a.executar(); assert.strictEqual(a.leituras(), 0); assert.strictEqual(a.livro.length, 0); casos++;
}
for (const colagem of [true, false]) {
  const a = ambiente(), e = a.evento(); delete e.value; delete e.oldValue;
  if (colagem) { e.range.getLastRow = () => 20; e.range.getLastColumn = () => 50; }
  a.executar(e); conferir(a);
  assert(a.eventos.every(([, ev]) => ev === e)); assert(!('value' in e)); assert(!('oldValue' in e)); casos++;
}
for (const falha of ['edicao', 'flush-edicao']) {
  const a = ambiente(); a.falhar(falha); assert.throws(() => a.executar(), /injetada/);
  assert.strictEqual(a.leituras(), 0); assert(a.logs.some(l => l.includes('"fase":"edicao"'))); casos++;
}
{
  const a = ambiente(); a.falhar('dados L2'); a.executar();
  a.livro.push(a.livro[0]); const antes = JSON.stringify(a.livro); a.executar();
  assert.strictEqual(JSON.stringify(a.livro), antes); assert(a.props.salario_lote_reparar);
  assert(!a.props.salario_proximo); assert(a.logs.some(l => l.includes('incompleto ou repetido'))); casos++;
}
console.log(JSON.stringify({resultado: 'OK', casos, creditos: [75000, 112500],
  limite: 'VM; tempos simulados. Sem aplicação, medição ou aprovação nativa.'}));
