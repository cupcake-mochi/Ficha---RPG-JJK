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
      setFormula(v) { mutation('formula', `${sheet}!${addr}`, () => {
        for(let r=r1;r<=r2;r++)for(let c=c1;c<=c2;c++)cells.set(`${sheet}!${r},${c}`, {...get(sheet,r,c),v:'',f:v});
      }); return this; },
      setNote(v) { edit('nota', 'n', v); return this; },
      setValues(m) { mutation('valores', `${sheet}!${addr}`, () => {
        assert.equal(m.length,r2-r1+1); assert(m.every(l=>l.length===c2-c1+1));
        for(let r=r1;r<=r2;r++)for(let c=c1;c<=c2;c++){const v=m[r-r1][c-c1],f=typeof v==='string'&&v.startsWith('=')?v:'';cells.set(`${sheet}!${r},${c}`,{...get(sheet,r,c),v:f?'':v,f});}
      }); return this; },
      setNotes(m) { mutation('notasMatriz', `${sheet}!${addr}`, () => {
        assert.equal(m.length,r2-r1+1); assert(m.every(l=>l.length===c2-c1+1));
        for(let r=r1;r<=r2;r++)for(let c=c1;c<=c2;c++)cells.set(`${sheet}!${r},${c}`,{...get(sheet,r,c),n:m[r-r1][c-c1]});
      }); return this; },
      clearContent() { edit('conteudo', 'v', ''); return this; },
      clearNote() { edit('notas', 'n', ''); return this; }};
  }
  const sheets = {};
  for (const name of ['EXTRATO', 'SALÁRIOS', 'DADOS_SALARIOS', 'FICHA PESSOAL', 'CONFIGURAÇÃO', 'CARTEIRA', 'FICHA', 'DADOS']) {
    sheets[name] = {getRange: addr => range(name, addr), getMaxRows: () => op.rows || 120};
  }
  const ss = {getId: () => op.id || 'copia-descartavel', getSheetByName: n => sheets[n] || null};
  function props(map, scope) { return {
    getProperty: k => map.has(k) ? map.get(k) : null,
    getKeys: () => [...map.keys()],
    setProperty: (k, v) => mutation('propriedade', scope + ':' + k, () => map.set(k, v)),
    deleteProperty: k => mutation('excluirPropriedade', scope + ':' + k, () => map.delete(k))
  }; }
  ctx.PropertiesService = {getDocumentProperties: () => props(doc, 'doc'), getScriptProperties: () => props(script, 'script')};
  ctx.Utilities = {DigestAlgorithm: {SHA_256: 'sha256'}, Charset: {UTF_8: 'utf8'},
    newBlob: value => ({getBytes: () => [...Buffer.from(value, 'utf8')]}),
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
    apply: p => ctx.r53NovaFichaFinanceiroAplicar(ss, context, p.assinatura),
    complete(p) {
      for (let i = 0; i < 20; i++) {
        const r = ctx.r53NovaFichaFinanceiroAplicar(ss, context, p.assinatura);
        if (r.concluido) return r;
        assert.equal(r.retomar, true); assert.equal(r.criacaoDisponivel, false);
        assert.equal(JSON.parse(doc.get(ctx.R53_NOVA_FIN_.diario)).concluido, false);
      }
      throw Error('não concluiu em 20 retomadas');
    }};
}

module.exports = {ambiente, a1};
