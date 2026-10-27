'use strict';
// VM offline: falhas de serviço, edição concorrente e propriedades controladas.
// Não executa fórmulas do Sheets nem certifica automações de uma cópia nativa.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const raiz = path.resolve(__dirname, '../..');
const fonte = fs.readFileSync(path.join(raiz, 'r53/inicializacao/financeiro.gs'), 'utf8');
const salarios = fs.readFileSync(path.join(raiz, 'apps-script/Salarios.gs'), 'utf8');
let cenarios = 0;
function caso(nome, fn) {
  try { fn(); cenarios++; } catch (e) { e.message = nome + ': ' + e.message; throw e; }
}
function a1(s) {
  const m = /^([A-Z]+)([0-9]+)(?::([A-Z]+)([0-9]+))?$/.exec(s);
  assert(m, s);
  const col = t => [...t].reduce((n, ch) => n * 26 + ch.charCodeAt(0) - 64, 0);
  return [Number(m[2]), col(m[1]), Number(m[4] || m[2]), col(m[3] || m[1])];
}
function ambiente(op = {}) {
  const cells = new Map(), doc = new Map(), script = new Map(), writes = [];
  let lock = false, hook = null;
  const ctx = {Date};
  vm.createContext(ctx);
  vm.runInContext(salarios, ctx);
  vm.runInContext(fonte, ctx);
  const get = (sheet, r, c) => cells.get(`${sheet}!${r},${c}`) || {v: '', f: '', n: '', fmt: 'tema', dv: 'menu'};
  function put(sheet, addr, v, f = '', n = '') {
    const [r, c] = a1(addr); cells.set(`${sheet}!${r},${c}`, {...get(sheet, r, c), v, f, n});
  }
  function mutation(kind, target, f) {
    assert(lock, 'toda escrita precisa da trava');
    if (hook) hook('antes', kind, target);
    f(); writes.push([kind, target]);
    if (hook) hook('depois', kind, target);
  }
  function range(sheet, addr) {
    const [r1, c1, r2, c2] = a1(addr);
    const read = field => Array.from({length: r2 - r1 + 1}, (_, i) =>
      Array.from({length: c2 - c1 + 1}, (_, j) => {
        const c = get(sheet, r1 + i, c1 + j);
        if (op.recalculo && field === 'v' && c.f) return op.recalculo();
        return c[field];
      }));
    const edit = (kind, field, value) => mutation(kind, `${sheet}!${addr}`, () => {
      for (let r = r1; r <= r2; r++) for (let c = c1; c <= c2; c++) {
        const old = get(sheet, r, c);
        cells.set(`${sheet}!${r},${c}`, field === 'n' ? {...old, n: value} : {...old, v: value, f: ''});
      }
    });
    return {getValues: () => read('v'), getFormulas: () => read('f'), getNotes: () => read('n'),
      getValue: () => read('v')[0][0],
      setValue(v) { edit('valor', 'v', v); return this; },
      clearContent() { edit('conteudo', 'v', ''); return this; },
      clearNote() { edit('notas', 'n', ''); return this; }};
  }
  const sheets = {};
  for (const name of ['EXTRATO', 'SALÁRIOS', 'DADOS_SALARIOS', 'FICHA PESSOAL', 'CONFIGURAÇÃO', 'CARTEIRA', 'FICHA']) {
    sheets[name] = {getRange: addr => range(name, addr), getMaxRows: () => op.rows || 120};
  }
  const ss = {getId: () => op.id || 'copia-descartavel', getSheetByName: n => sheets[n] || null};
  function props(map, scope) { return {
    getProperty: k => map.has(k) ? map.get(k) : null,
    setProperty: (k, v) => mutation('propriedade', scope + ':' + k, () => map.set(k, v)),
    deleteProperty: k => mutation('excluirPropriedade', scope + ':' + k, () => map.delete(k))
  }; }
  ctx.PropertiesService = {getDocumentProperties: () => props(doc, 'doc'), getScriptProperties: () => props(script, 'script')};
  ctx.Utilities = {DigestAlgorithm: {SHA_256: 'sha256'}, Charset: {UTF_8: 'utf8'},
    computeDigest: (algo, s) => [...crypto.createHash(algo).update(s, 'utf8').digest()]};
  ctx.LockService = {getDocumentLock: () => ({tryLock() { if (op.ocupado) return false; lock = true; return true; },
    releaseLock() { assert(lock); lock = false; }})};
  ctx.SpreadsheetApp = {getActive: () => op.ativoDiferente ? {getId: () => 'outro'} : ss, flush() {}};
  const expected = ctx.r53NovaFinFormulas_();
  ctx.R53_NOVA_FIN_.formulas.forEach(([sheet, addr], i) => {
    const [r1, c1, r2, c2] = a1(addr);
    for (let r = r1; r <= r2; r++) for (let c = c1; c <= c2; c++)
      cells.set(`${sheet}!${r},${c}`, {v: 99, f: expected[i][r - r1][c - c1], n: 'explicação', fmt: 'tema', dv: 'menu'});
  });
  const last = op.rows || 120;
  for (const sheet of ['EXTRATO', 'SALÁRIOS', 'DADOS_SALARIOS']) {
    put(sheet, 'A1', 'Cabeçalho'); put(sheet, 'A2', 'SEGREDO financeiro', '', 'nota privada');
    put(sheet, `C${last}`, 123456, '', 'última linha física');
  }
  put('SALÁRIOS', `L${last}`, 'fim'); put('DADOS_SALARIOS', `J${last}`, 'troca antiga');
  for (const col of ['AW', 'BC', 'BI', 'BO']) put('FICHA PESSOAL', col + '15', 'missão privada', '', '[Salário: id-antigo · data]');
  for (const col of ['AZ', 'BF', 'BL', 'BR']) put('FICHA PESSOAL', col + '87', 5);
  for (const col of ['BA', 'BG', 'BM', 'BS']) put('FICHA PESSOAL', col + '15', 10, '=XP_MISSAO()');
  put('DADOS_SALARIOS', 'L2', JSON.stringify({versao: 1, inicio: 46000, graus: ['Grau 1'], ultimaEmissao: 46000, agenda: 'projeto-antigo'}));
  put('DADOS_SALARIOS', 'N1', 'Emissão'); put('DADOS_SALARIOS', 'N2', op.semEmissao ? '' : 46000);
  put('FICHA PESSOAL', 'O86', -500, op.o86Formula ? '=SUM(EXTRATO!C2:C)' : '', 'nota do campo');
  put('FICHA PESSOAL', 'BI11', 'corrigir'); put('FICHA PESSOAL', 'BO11', 46000);
  put('CONFIGURAÇÃO', 'O39', true); put('CARTEIRA', 'AT3', true);
  put('FICHA', 'AH11', 2); put('CONFIGURAÇÃO', 'E46', 'Nível inicial'); put('CONFIGURAÇÃO', 'F46', 5);
  put('CONFIGURAÇÃO', 'G46', 5, '=F46');
  put('CONFIGURAÇÃO', 'AK51', 'habilidade custom da mesa');
  put('FICHA PESSOAL', 'D92', 'inventário antigo fora deste domínio');
  for (const k of ctx.R53_NOVA_FIN_.propriedadesDocumento) doc.set(k, 'SEGREDO-' + k);
  for (const k of ctx.R53_NOVA_FIN_.propriedadesScript) script.set(k, 'SEGREDO-' + k);
  doc.set('r53_recuperacao_personagem', 'recuperação fora deste domínio');
  script.set('paleta', 'conservar');
  const context = {versao: 1, operacao: 'operacao_sintetica_0001', destino: ss.getId(), modelo: 'modelo-sintetico',
    arquivosRegistrados: [], responsavelConfirmado: true, copiaNovaConfirmada: true};
  return {ctx, ss, sheets, cells, doc, script, writes, context, put, range, get,
    hook: fn => { hook = fn; }, locked: () => lock,
    preview: () => ctx.r53NovaFichaFinanceiroPrevia(ss, context),
    apply: p => ctx.r53NovaFichaFinanceiroAplicar(ss, context, p.assinatura)};
}
function verificar(a) {
  const val = (s, x) => a.range(s, x).getValue();
  assert.equal(val('DADOS_SALARIOS', 'L2'), '{"versao":1,"graus":[]}');
  assert.deepEqual(JSON.parse(JSON.stringify(a.ctx.salarioEstado_(a.ss))), {versao: 1, graus: []});
  assert.equal(val('DADOS_SALARIOS', 'N2'), '');
  assert.equal(val('FICHA PESSOAL', 'O86'), '');
  assert.equal(val('CARTEIRA', 'AT3'), false); assert.equal(val('CONFIGURAÇÃO', 'O39'), false);
  assert.equal(val('FICHA', 'AH11'), 2); assert.equal(val('CONFIGURAÇÃO', 'F46'), 5);
  assert.equal(a.range('CONFIGURAÇÃO', 'G46').getFormulas()[0][0], '=F46');
  assert.equal(val('CONFIGURAÇÃO', 'AK51'), 'habilidade custom da mesa');
  assert.equal(val('FICHA PESSOAL', 'D92'), 'inventário antigo fora deste domínio');
  assert.equal(a.range('FICHA PESSOAL', 'O86').getNotes()[0][0], 'nota do campo');
  for (const col of ['BA', 'BG', 'BM', 'BS']) assert.equal(a.range('FICHA PESSOAL', col + '15').getFormulas()[0][0], '=XP_MISSAO()');
  for (const col of ['AW', 'BC', 'BI', 'BO']) assert.equal(a.range('FICHA PESSOAL', col + '15').getNotes()[0][0], '');
  for (const cell of a.cells.values()) { assert.equal(cell.fmt, 'tema'); assert.equal(cell.dv, 'menu'); }
  for (const k of a.ctx.R53_NOVA_FIN_.propriedadesDocumento) assert(!a.doc.has(k));
  for (const k of a.ctx.R53_NOVA_FIN_.propriedadesScript) assert(!a.script.has(k));
  assert.equal(a.doc.get('r53_recuperacao_personagem'), 'recuperação fora deste domínio');
  assert.equal(a.script.get('paleta'), 'conservar'); assert(!a.locked());
  const journal = a.doc.get(a.ctx.R53_NOVA_FIN_.diario);
  assert(Buffer.byteLength(journal) < 9000, 'abaixo do limite por propriedade do Apps Script');
  assert(!/SEGREDO|missão privada|projeto-antigo|id-antigo|123456/.test(journal));
  assert.equal(JSON.parse(journal).concluido, true);
}
caso('prévia não grava e não revela dados', () => {
  const a = ambiente(); const p = a.preview(); assert.equal(a.writes.length, 0);
  assert.equal(p.criacaoDisponivel, false); assert(p.alteracoes > 0);
  assert(!/SEGREDO|missão privada|123456|projeto-antigo/.test(JSON.stringify(p)));
});
caso('limpeza financeira preserva campanha e o que não pertence ao domínio', () => {
  const a = ambiente(); const p = a.preview(), r = a.apply(p); verificar(a);
  assert.equal(r.criacaoDisponivel, false); assert.equal(r.concluido, true);
  assert(r.pendente.includes('inventario')); assert(r.pendente.includes('prova_nativa'));
  const n = a.writes.length; a.apply(p); assert.equal(a.writes.length, n, 'segunda execução não grava');
});
caso('última linha 5000 e notas são limpas mesmo sem emissão', () => {
  const a = ambiente({rows: 5000, semEmissao: true}); a.apply(a.preview()); verificar(a);
  for (const s of ['EXTRATO', 'SALÁRIOS', 'DADOS_SALARIOS']) {
    assert.equal(a.range(s, 'C5000').getValue(), ''); assert.equal(a.range(s, 'C5000').getNotes()[0][0], '');
    assert.equal(a.range(s, 'A1').getValue(), 'Cabeçalho');
  }
});
caso('cache de fórmula de O86 pode recalcular sem representar edição', () => {
  let n = 0; const a = ambiente({o86Formula: true, recalculo: () => ++n});
  a.apply(a.preview()); verificar(a);
});
for (const id of ['1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k', '1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw'])
  caso('recusa oficial ' + id.slice(0, 5), () => { const a = ambiente({id}); assert.throws(() => a.preview(), /cópia nova/); assert.equal(a.writes.length, 0); });
for (const [key, value] of [['responsavelConfirmado', false], ['copiaNovaConfirmada', false], ['versao', 2],
  ['modelo', ''], ['modelo', 'copia-descartavel'], ['destino', 'outro'], ['operacao', 'curta'], ['arquivosRegistrados', ['copia-descartavel']]])
  caso('recusa contexto ' + key + String(value), () => { const a = ambiente(); a.context[key] = value; assert.throws(() => a.preview(), /cópia nova/); assert.equal(a.writes.length, 0); });
for (const op of [{rows: 5001}, {rows: 1}, {ativoDiferente: true}])
  caso('recusa grade/documento ' + JSON.stringify(op), () => { const a = ambiente(op); assert.throws(() => a.preview()); assert.equal(a.writes.length, 0); });
caso('modo legado não suportado', () => { const a = ambiente(); a.ctx.SALARIO_.formula = false; assert.throws(() => a.preview(), /fórmula não confirmado/); assert.equal(a.writes.length, 0); });
for (const [s, addr] of [['EXTRATO', 'B2'], ['SALÁRIOS', 'K3'], ['FICHA PESSOAL', 'AW15'], ['DADOS_SALARIOS', 'L2']])
  caso('fórmula inesperada ' + addr, () => { const a = ambiente(); a.put(s, addr, 3, '=CUSTOM()'); assert.throws(() => a.preview(), /fórmula inesperada/); assert.equal(a.writes.length, 0); });
caso('falta de fórmula protegida', () => { const a = ambiente(); a.put('DADOS_SALARIOS', 'Q2', 3); assert.throws(() => a.preview(), /fórmula financeira/); assert.equal(a.writes.length, 0); });
caso('fórmula protegida desconhecida não é certificada só por começar com igual', () => {
  const a = ambiente(); a.put('FICHA PESSOAL', 'W86', 0, '=0');
  assert.throws(() => a.preview(), /fora do contrato/); assert.equal(a.writes.length, 0);
});
caso('aspas opcionais de DADOS_SALARIOS normalizadas pelo Google são aceitas', () => {
  const a = ambiente();
  for (const c of a.cells.values()) c.f = c.f.replace(/'DADOS_SALARIOS'!/g, 'DADOS_SALARIOS!');
  a.apply(a.preview()); verificar(a);
});
caso('aba ausente', () => { const a = ambiente(); delete a.sheets.SALÁRIOS; assert.throws(() => a.preview()); assert.equal(a.writes.length, 0); });
caso('prévia envelhecida não cria diário nem limpa', () => { const a = ambiente(), p = a.preview(); a.put('EXTRATO', 'B2', 'novo'); assert.throws(() => a.apply(p), /mudou após/); assert.equal(a.writes.length, 0); assert(!a.locked()); });
caso('alterar fórmula da campanha mantendo cache invalida prévia', () => { const a = ambiente(), p = a.preview(); a.put('CONFIGURAÇÃO', 'G46', 5, '=5'); assert.throws(() => a.apply(p), /mudou após/); assert.equal(a.writes.length, 0); });
caso('trava ocupada', () => { const a = ambiente({ocupado: true}), p = a.preview(); assert.throws(() => a.apply(p), /outra operação/); assert.equal(a.writes.length, 0); });
// Todas as fronteiras reais de escrita: antes e depois da chamada, inclusive
// depois de apagar conteúdo e antes de apagar notas, e entre duas propriedades.
const base = ambiente(); base.apply(base.preview());
for (let falha = 1; falha <= base.writes.length; falha++) for (const fase of ['antes', 'depois'])
  caso(`retoma queda ${fase} da escrita ${falha}`, () => {
    const a = ambiente(), p = a.preview(); let n = 0;
    a.hook(f => { if (f === fase && ++n === falha) throw new Error('queda simulada'); });
    assert.throws(() => a.apply(p), /queda simulada/); assert(!a.locked());
    a.hook(null); a.apply(p); verificar(a);
  });
caso('edição alheia em nota depois de queda não é apagada', () => {
  const a = ambiente(), p = a.preview(); a.hook((f, kind) => { if (f === 'depois' && kind === 'conteudo') throw Error('queda'); });
  assert.throws(() => a.apply(p), /queda/); a.hook(null);
  a.put('EXTRATO', 'A2', '', '', 'nota nova'); const n = a.writes.length;
  assert.throws(() => a.apply(p), /editados/); assert.equal(a.writes.length, n);
  assert.equal(a.range('EXTRATO', 'A2').getNotes()[0][0], 'nota nova');
});
caso('propriedade salarial alterada durante pausa não é apagada', () => {
  const a = ambiente(), p = a.preview(); a.hook((f, kind) => { if (f === 'depois' && kind === 'excluirPropriedade') throw Error('queda'); });
  assert.throws(() => a.apply(p), /queda/); a.hook(null); a.doc.set('salario_proximo', 'estado novo');
  const n = a.writes.length; assert.throws(() => a.apply(p), /editados/); assert.equal(a.writes.length, n);
  assert.equal(a.doc.get('salario_proximo'), 'estado novo');
});
caso('mesma chamada depois do uso não reinicializa', () => {
  const a = ambiente(), p = a.preview(); a.apply(p); a.put('EXTRATO', 'A2', 'novo lançamento');
  const n = a.writes.length; assert.throws(() => a.apply(p), /editados|já foi usada/); assert.equal(a.writes.length, n);
});
caso('propriedade original reaparecida após conclusão não é apagada', () => {
  const a = ambiente(), p = a.preview(); a.apply(p); a.doc.set('salario_proximo', 'SEGREDO-salario_proximo');
  const n = a.writes.length; assert.throws(() => a.apply(p), /já foi usada/); assert.equal(a.writes.length, n);
});
caso('outra operação não toma diário pendente nem cria nova prévia', () => {
  const a = ambiente(), p = a.preview(); a.apply(p); a.context.operacao = 'outra_operacao_00002';
  const n = a.writes.length; assert.throws(() => a.apply(p), /operação diferente/); assert.throws(() => a.preview(), /retome/); assert.equal(a.writes.length, n);
});
for (const raw of ['{', 'null', '{}']) caso('diário inválido ' + raw, () => {
  const a = ambiente(), p = a.preview(); a.doc.set(a.ctx.R53_NOVA_FIN_.diario, raw);
  assert.throws(() => a.apply(p), /diário inválido/); assert.equal(a.writes.length, 0);
});
caso('diário adulterado', () => {
  const a = ambiente(), p = a.preview(); a.apply(p); const k = a.ctx.R53_NOVA_FIN_.diario, j = JSON.parse(a.doc.get(k));
  j.plano.alteracoes++; a.doc.set(k, JSON.stringify(j)); const n = a.writes.length;
  assert.throws(() => a.apply(p), /diário inválido/); assert.equal(a.writes.length, n);
});
caso('edição no meio da execução interrompe sem sobrescrever', () => {
  const a = ambiente(), p = a.preview(); a.hook((f, kind) => { if (f === 'depois' && kind === 'conteudo') a.put('DADOS_SALARIOS', 'N2', 'emissão nova'); });
  assert.throws(() => a.apply(p), /concorrente/); assert.equal(a.range('DADOS_SALARIOS', 'N2').getValue(), 'emissão nova');
  assert.equal(JSON.parse(a.doc.get(a.ctx.R53_NOVA_FIN_.diario)).concluido, false);
});
caso('estado inicial não inventa início, emissão ou agenda; fórmulas reais exigem emissão', () => {
  const a = ambiente(); a.apply(a.preview()); const state = a.ctx.salarioEstado_(a.ss);
  for (const key of ['inicio', 'ultimaEmissao', 'agenda']) assert.equal(state[key], undefined);
  assert.equal(a.ctx.SALARIO_.formula, true);
  const aux = a.ctx.SALARIO_.f.aux;
  assert(aux[1][1].startsWith('=IF(ISNUMBER(N2);'), 'início pendente depende de emissão numérica');
  assert(aux[2][1].includes('AND(ISNUMBER(N2);'), 'períodos vencidos dependem de emissão');
  assert(a.ctx.SALARIO_.f.emissao.includes("ISNUMBER('DADOS_SALARIOS'!N2)"));
  // Conferência estática do fonte e do leitor reais; não avaliação das fórmulas.
});
console.log(`${cenarios} cenários offline de inicialização financeira aprovados; nenhuma prova nativa ou liberação de criação.`);
