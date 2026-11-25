'use strict';
// ANALISE estática (17/11/2026): apps-script/AnaliseEstatica.gs numa planilha falsa, os ganchos (Codigo, Ficha,
// pacote) e o preparador das oficiais. No fim, defeitos plantados no exportador: cada um tem de derrubar o teste.
//   node r53/testes/analise_estatica.js
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert/strict');
const RAIZ = path.resolve(__dirname, '..', '..');
const FONTE = fs.readFileSync(path.join(RAIZ, 'apps-script/AnaliseEstatica.gs'), 'utf8');
const prep = require(path.join(RAIZ, 'r53/diagnostico-android/preparar_analise_estatica.js'));
const depois = require(path.join(RAIZ, 'r53/diagnostico-android/preparar_analise_depois.js'));
const selecao = require(path.join(RAIZ, 'r53/diagnostico-android/preparar_analise_selecao.js'));

// ---------- planilha falsa ----------
// Fórmula "=D(k)" vale dados[k] na hora da leitura; copyTo com contentsOnly troca pela leitura (como o Sheets).
function letras(c) { let s = ''; while (c) { const r = (c - 1) % 26; s = String.fromCharCode(65 + r) + s; c = (c - 1 - r) / 26; } return s; }
function pos(a1) { const m = /^([A-Z]+)(\d+)$/.exec(a1); let c = 0; for (const ch of m[1]) c = c * 26 + ch.charCodeAt(0) - 64; return [+m[2], c]; }
function novaPlanilha(clock) {
  const dados = {}, abas = [], log = { escritas: [], flush: 0, leituras: 0, seq: [], linhasLidas: {} };
  function aba(nome, linhas, colunas) {
    const celulas = new Map(), dv = new Map();
    let maxR = linhas, maxC = colunas, oculta = false;
    const k = (r, c) => r + ',' + c;
    const valor = (r, c) => { const x = celulas.get(k(r, c)); if (!x) return ''; return x.f ? (dados[x.f.slice(3, -1)] ?? '#REF') : x.v; };
    const sh = {
      getName: () => nome, getMaxRows: () => maxR, getMaxColumns: () => maxC,
      insertRowsAfter: (_, n) => { maxR += n; }, deleteColumns: (_, n) => { maxC -= n; },
      hideSheet: () => { oculta = true; }, isSheetHidden: () => oculta,
      getLastRow: () => { log.leituras++; let u = 0; for (const [key, x] of celulas) { if (x.v === '' && !x.f) continue; const r = +key.split(',')[0]; if (r > u) u = r; } return u; },
      _cel: celulas, _dv: dv,
      getRange(a, b, nr, nc) {
        let r0, c0, r1, c1;
        if (typeof a === 'string') { const [p, q] = a.split(':'); [r0, c0] = pos(p); [r1, c1] = q ? pos(q) : [r0, c0]; }
        else { r0 = a; c0 = b; r1 = a + (nr || 1) - 1; c1 = b + (nc || 1) - 1; }
        if (r1 > maxR || c1 > maxC) throw new Error('fora da grade: ' + nome + ' ' + r1 + ',' + c1);
        const grade = f => { const out = []; for (let r = r0; r <= r1; r++) { const l = []; for (let c = c0; c <= c1; c++) l.push(f(r, c)); out.push(l); } return out; };
        const escrever = (m, formula) => { log.escritas.push(nome + '!' + letras(c0) + r0); log.seq.push('w:' + nome + '!' + letras(c0) + r0); m.forEach((l, i) => l.forEach((v, j) => {
          const s = typeof v === 'string' && v.charAt(0) === "'" ? { v: v.slice(1) } : formula || (typeof v === 'string' && v.charAt(0) === '=') ? { f: v } : { v };
          celulas.set(k(r0 + i, c0 + j), s); })); };
        const rg = {
          getRow: () => r0, getColumn: () => c0, getLastColumn: () => c1, getNumRows: () => r1 - r0 + 1, getNumColumns: () => c1 - c0 + 1,
          getSheet: () => sh, getA1Notation: () => letras(c0) + r0 + (r1 !== r0 || c1 !== c0 ? ':' + letras(c1) + r1 : ''),
          getValues: () => (log.leituras++, log.linhasLidas[nome] = Math.max(log.linhasLidas[nome] || 0, r1 - r0 + 1), grade(valor)), getValue: () => (log.leituras++, valor(r0, c0)),
          getFormulas: () => (log.leituras++, grade((r, c) => (celulas.get(k(r, c)) || {}).f || '')),
          setValues: m => { escrever(m, false); return rg; }, setValue: v => { escrever([[v]], false); return rg; },
          setFormulas: m => { m.forEach(l => l.forEach(f => assert.ok(f.charAt(0) === '=', 'setFormulas sem =: ' + f))); escrever(m, true); return rg; },
          clearContent: () => { grade((r, c) => celulas.delete(k(r, c))); log.escritas.push(nome + '!limpa'); return rg; },
          copyTo: (dest, op) => {
            if (op && op.contentsOnly) { const vs = grade(valor); vs.forEach((l, i) => l.forEach((v, j) => celulas.set(k(r0 + i, c0 + j), { v }))); log.escritas.push(nome + '!congela'); }
            else if (op && op.formatOnly) { const d = dest; grade((r, c) => { const x = dv.get(k(r, c)); if (x) d.getSheet()._dv.set(k(d.getRow() + r - r0, d.getColumn() + c - c0), x); }); }
          },
          merge: () => rg,
          breakApart: () => rg,
          insertCheckboxes: () => { grade((r, c) => dv.set(k(r, c), 'CHECKBOX')); return rg; },
          getDataValidation: () => dv.get(k(r0, c0)) ? { getCriteriaType: () => 'CHECKBOX' } : null
        };
        return rg;
      }
    };
    abas.push(sh); return sh;
  }
  const ss = {
    getSheetByName: n => abas.find(a => a.getName() === n) || null, getSheets: () => abas,
    insertSheet: (n) => aba(n, 1000, 26), toast: () => {}, getSpreadsheetTimeZone: () => 'America/Sao_Paulo'
  };
  return { ss, aba, dados, log };
}

// ANALISE pequena: cabeçalho, formato.versao '12 (texto), N chaves com fórmula, uma constante no meio.
function montarFicha(n, clock) {
  const p = novaPlanilha(clock);
  const an = p.aba('ANALISE', n + 2, 12);
  an.getRange(1, 1, 1, 2).setValues([['chave', 'valor']]);
  an.getRange(2, 1, 1, 2).setValues([['formato.versao', "'12"]]);
  const linhas = [];
  for (let i = 0; i < n; i++) {
    p.dados['k' + i] = 'v' + i;
    linhas.push(['chave.' + i, i === 5 ? 'Ciclo Maldito R53' : '=D(k' + i + ')']);
  }
  an.getRange(3, 1, n, 2).setValues(linhas);
  const cart = p.aba('CARTEIRA', 52, 47);
  cart.getRange('AH3').setValue('Não emitida · marque ao lado');
  cart.getRange('AT3').insertCheckboxes().setValue(false);
  p.aba('FICHA', 200, 47);
  return p;
}

function contexto(p, clock, props) {
  const c = {
    console: { log: () => {} },
    SpreadsheetApp: { getActive: () => p.ss, flush: () => { p.log.flush++; p.log.seq.push('flush'); clock.t += clock.passo; }, DataValidationCriteria: { CHECKBOX: 'CHECKBOX' } },
    PropertiesService: { getDocumentProperties: () => ({
      getProperty: k => (props.leituras++, props.m.has(k) ? props.m.get(k) : null),
      setProperty: (k, v) => { p.log.seq.push('p:' + k); props.m.set(k, String(v)); }, deleteProperty: k => props.m.delete(k) }) },
    LockService: { getDocumentLock: () => ({ tryLock: () => !props.ocupada, releaseLock: () => {} }) },
    Utilities: { formatDate: (d, tz, f) => f.indexOf('T') >= 0 ? '2026-11-17T13:40:00' : '17/11 13:40' },
    Date: Object.assign(function () { return new Date(Date.UTC(2026, 10, 17, 16, 40)); }, { now: () => clock.t })
  };
  vm.createContext(c);
  return c;
}

function cenario(fonte, n) {
  const clock = { t: 0, passo: 1000 }, props = { m: new Map(), leituras: 0 };
  const p = montarFicha(n || 7000, clock), c = contexto(p, clock, props);
  vm.runInContext(fonte, c);
  return { p, c, clock, props, an: p.ss.getSheetByName('ANALISE'), cart: p.ss.getSheetByName('CARTEIRA'), mod: () => p.ss.getSheetByName('ANALISE_MODELOS') };
}
const ev = (s, aba, a1, valor, extra) => {
  const range = s.p.ss.getSheetByName(aba).getRange(a1);
  if (aba === 'CARTEIRA' && a1 === 'AT4') range.setValue(valor === 'TRUE'); // o jogador marca a caixa antes do evento
  return Object.assign({ range, value: valor, source: s.p.ss }, extra || {});
};
const chave = (s, k) => { const vs = s.an.getRange(1, 1, s.an.getLastRow(), 2).getValues(); const l = vs.find(x => x[0] === k); return l ? l[1] : undefined; };
// Entre a escrita e a propriedade que aponta para ela houve um flush (escrita pendente se perde no fim do tempo).
const gravadoAntes = (s, w, prop) => { const q = s.p.log.seq, ip = q.indexOf(prop), iw = q.lastIndexOf(w, ip); return iw >= 0 && ip > iw && q.slice(iw, ip).indexOf('flush') >= 0; };
const formulasB = s => s.an.getRange(1, 2, s.an.getLastRow(), 1).getFormulas().filter(x => x[0]).length;

function suite(fonte) {
  let n = 0;
  const t = (nome, f) => { try { f(); n++; } catch (err) { err.message = nome + ': ' + err.message; throw err; } };

  // 1. Menu na ficha viva: cria os modelos, congela, marca em dia, versão 13, instala a caixa.
  let s = cenario(fonte);
  const vivo = s.an.getRange(1, 1, s.an.getLastRow(), 2).getValues();
  let r = s.c.exportarParaOBot();
  t('menu exporta tudo', () => assert.deepEqual([r.estado, r.feitas, r.total], ['em_dia', 6999, 6999]));
  t('coluna B sem fórmula', () => assert.equal(formulasB(s), 0));
  t('valores iguais ao vivo', () => assert.deepEqual(s.an.getRange(3, 1, 7000, 2).getValues(), vivo.slice(2)));
  t('modelos ocultos, linha a linha', () => { const m = s.mod(); assert.ok(m && m.isSheetHidden()); assert.equal(m.getRange(3, 1).getValue(), '=D(k0)'); assert.equal(m.getRange(8, 1).getValue(), ''); });
  t('formato 13 e estado', () => { assert.equal(chave(s, 'formato.versao'), '13'); assert.equal(chave(s, 'analise.estado'), 'em_dia'); assert.equal(chave(s, 'analise.exportada_em'), '2026-11-17T13:40:00'); });
  t('caixa instalada na AT4', () => { assert.equal(s.cart.getRange('AT4').getDataValidation().getCriteriaType(), 'CHECKBOX'); assert.equal(s.cart.getRange('AH4').getValue(), 'Bot: em dia · 17/11 13:40'); });
  t('propriedade em dia', () => assert.equal(s.props.m.get('analise_estado'), 'em_dia'));
  t('linhas novas gravadas antes da propriedade', () => assert.ok(gravadoAntes(s, 'w:ANALISE!A7003', 'p:analise_linhas')));
  t('caixa gravada antes da propriedade', () => assert.ok(gravadoAntes(s, 'w:CARTEIRA!AT4', 'p:analise_caixa')));

  // 2. Edição depois de exportar: a primeira marca, as outras só leem a propriedade.
  s.p.dados.k0 = 'NOVO';
  let antes = s.p.log.escritas.length;
  t('edição não é tratada aqui', () => assert.equal(s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B5', '3')), false));
  t('primeira edição marca desatualizada', () => { assert.equal(chave(s, 'analise.estado'), 'desatualizada'); assert.equal(s.cart.getRange('AH4').getValue(), 'Bot: desatualizada · marque ao lado'); });
  t('valor congelado não muda sozinho', () => assert.equal(chave(s, 'chave.0'), 'v0'));
  antes = s.p.log.escritas.length; let leit = s.props.leituras;
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B6', '4'));
  t('segunda edição não escreve', () => { assert.equal(s.p.log.escritas.length, antes); assert.equal(s.props.leituras - leit, 1); });
  t('mesmo evento visto duas vezes conta uma', () => { const e = ev(s, 'FICHA', 'B7', '1'); s.c.analiseNaEdicao_(e); leit = s.props.leituras; s.c.analiseNaEdicao_(e); assert.equal(s.props.leituras, leit); });

  // 3. A caixa: exporta o que cabe no tempo, guarda o progresso, continua na próxima marcação.
  s.clock.t = 0; s.clock.passo = 8000;
  r = null; s.p.log.linhasLidas = {};
  s.props.m.delete('analise_caixa'); // como numa cópia da ficha: a caixa existe, a propriedade não
  t('caixa tratada aqui', () => assert.equal(s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 })), true));
  t('caixa desmarcada', () => assert.equal(s.cart.getRange('AT4').getValue(), false));
  t('parcial: exportando e progresso guardado', () => { assert.equal(chave(s, 'analise.estado'), 'exportando'); assert.equal(s.props.m.get('analise_exportar_prox'), '4002'); assert.match(s.cart.getRange('AH4').getValue(), /^Bot: exportando 3998\/6999 · toque de novo$/); });
  t('duração do bloco guardada', () => assert.equal(s.props.m.get('analise_bloco_ms'), '16000'));
  t('blocos feitos já sem fórmula', () => assert.equal(formulasB(s), 0));
  t('caixa lê só as linhas do bloco', () => assert.ok(s.p.log.linhasLidas.ANALISE_MODELOS <= 4000, String(s.p.log.linhasLidas.ANALISE_MODELOS)));
  t('cópia: reconhece a caixa', () => assert.equal(s.props.m.get('analise_caixa'), '1'));
  t('caixa guarda o feito', () => assert.equal(s.props.m.get('analise_exportar_feitas'), '3998'));
  t('primeiro bloco já com o valor novo', () => assert.equal(chave(s, 'chave.0'), 'NOVO'));
  // Ficha instalada antes do total guardado (as oficiais em 18/11): lê a lista inteira uma vez e guarda o total.
  s.props.m.delete('analise_modelos_total');
  s.clock.t = 0; let lidas = s.p.log.leituras;
  s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('caixa lê a planilha uma vez só', () => assert.equal(s.p.log.leituras - lidas, 1));
  t('total guardado', () => assert.equal(s.props.m.get('analise_modelos_total'), '6999'));
  t('segunda marcação termina', () => { assert.equal(chave(s, 'analise.estado'), 'em_dia'); assert.equal(s.props.has ? 0 : s.props.m.has('analise_exportar_prox'), false); });
  t('caixa apagada não exporta', () => { const f = s.p.log.flush; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', undefined)); assert.equal(s.p.log.flush, f); });
  // Marcação que estourou os 30 s deixa a caixa marcada: o toque seguinte desmarca e tem de continuar.
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B6', '3'));
  s.clock.t = 0; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('estouro simulado: parcial', () => assert.equal(chave(s, 'analise.estado'), 'exportando'));
  s.cart.getRange('AT4').setValue(true);
  s.clock.t = 0; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'FALSE', { r53Inicio_: 0 }));
  t('desmarcar continua a exportação', () => { assert.equal(chave(s, 'analise.estado'), 'em_dia'); assert.equal(s.cart.getRange('AT4').getValue(), false); });

  // 4. Editou no meio da exportação: recomeça do começo.
  s.p.dados.k6998 = 'FIM';
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B5', '2'));
  s.clock.t = 0; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('parcial de novo', () => assert.equal(s.props.m.get('analise_exportar_prox'), '4002'));
  s.p.dados.k0 = 'MEIO';
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B5', '9'));
  t('edição no meio apaga o progresso', () => { assert.equal(s.props.m.has('analise_exportar_prox'), false); assert.equal(s.cart.getRange('AH4').getValue(), 'Bot: editada no meio · toque de novo'); });
  s.clock.t = 0; s.clock.passo = 1000; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('recomeço pega a edição do meio', () => { assert.equal(chave(s, 'chave.0'), 'MEIO'); assert.equal(chave(s, 'chave.6998'), 'FIM'); assert.equal(chave(s, 'analise.estado'), 'em_dia'); });

  // 5. Escrita na ANALISE congelada.
  s.an.getRange(10, 2).setValue('mão');
  t('coluna B: tratada aqui', () => assert.equal(s.c.analiseNaEdicao_(ev(s, 'ANALISE', 'B10', 'mão')), true));
  t('coluna B: limpa e marca', () => { assert.equal(s.an.getRange(10, 2).getValue(), ''); assert.equal(chave(s, 'analise.estado'), 'desatualizada'); });
  const linhaEstado = JSON.parse(s.props.m.get('analise_linhas')).estado;
  s.c.analiseNaEdicao_(ev(s, 'ANALISE', 'B' + linhaEstado, ''));
  t('apagou a célula do estado: volta marcada', () => assert.equal(chave(s, 'analise.estado'), 'desatualizada'));
  t('coluna A segue para o restaurador', () => assert.equal(s.c.analiseNaEdicao_(ev(s, 'ANALISE', 'A10', 'x')), false));
  s.c.exportarParaOBot();
  t('a escrita à mão não virou modelo', () => assert.equal(chave(s, 'chave.7'), 'v7'));

  // 6. Cópia da ficha: sem propriedades. Antes da automação a edição não toca na planilha; a conferência (o estado da
  // ANALISE, uma leitura) fica para o fim dela.
  const flushBom = s.c.SpreadsheetApp.flush;
  const copia = () => { s.props.m.clear(); s.c.exportarParaOBot(); s.props.m.clear(); };
  const parado = f => { const l = s.p.log, x = [l.leituras, l.escritas.length, l.flush]; f(); assert.deepEqual([l.leituras, l.escritas.length, l.flush], x); };
  copia();
  let ed = ev(s, 'FICHA', 'B5', '1');
  t('cópia: nada na planilha antes da automação', () => parado(() => assert.equal(s.c.analiseNaEdicao_(ed), false)));
  t('cópia: ainda sem a propriedade', () => { assert.equal(s.props.m.size, 0); assert.equal(chave(s, 'analise.estado'), 'em_dia'); });
  s.p.log.seq.length = 0; lidas = s.p.log.leituras;
  s.c.analiseDepoisDaEdicao_(ed);
  t('cópia: uma leitura no fim', () => assert.equal(s.p.log.leituras - lidas, 1));
  t('cópia: automação gravada antes da conferência', () => assert.equal(s.p.log.seq[0], 'flush'));
  t('cópia em dia vira desatualizada', () => { assert.equal(s.props.m.get('analise_estado'), 'desatualizada'); assert.equal(chave(s, 'analise.estado'), 'desatualizada'); assert.equal(s.cart.getRange('AH4').getValue(), 'Bot: desatualizada · marque ao lado'); });
  t('cópia: marca gravada antes da propriedade', () => { const q = s.p.log.seq, ip = q.lastIndexOf('p:analise_estado'); for (const w of ['w:ANALISE!B7003', 'w:CARTEIRA!AH4']) { const iw = q.lastIndexOf(w, ip); assert.ok(iw >= 0 && q.slice(iw, ip).indexOf('flush') >= 0, w); } });
  t('cópia reconhece a caixa', () => assert.equal(s.props.m.get('analise_caixa'), '1'));
  t('cópia: linhas guardadas', () => assert.deepEqual(JSON.parse(s.props.m.get('analise_linhas')), { estado: 7003, data: 7004 }));
  t('cópia: conferência só uma vez por edição', () => parado(() => s.c.analiseDepoisDaEdicao_(ed)));
  ed = ev(s, 'FICHA', 'B6', '1');
  t('cópia: a edição seguinte não confere', () => parado(() => { s.c.analiseNaEdicao_(ed); s.c.analiseDepoisDaEdicao_(ed); }));
  t('cópia: exporta sem a linha da versão guardada', () => { s.clock.t = 0; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 })); s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 })); assert.equal(chave(s, 'analise.estado'), 'em_dia'); assert.equal(chave(s, 'formato.versao'), '13'); });
  // O tempo acaba: sem chegar na conferência, a próxima edição confere; no meio da marca, a próxima marca.
  copia();
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B5', '1'));
  ed = ev(s, 'FICHA', 'B6', '1'); s.c.analiseNaEdicao_(ed); s.c.analiseDepoisDaEdicao_(ed);
  t('morreu antes: a próxima confere', () => assert.equal(chave(s, 'analise.estado'), 'desatualizada'));
  copia();
  let k = 0; s.c.SpreadsheetApp.flush = () => { if (++k === 2) throw new Error('tempo'); };
  ed = ev(s, 'FICHA', 'B5', '1'); s.c.analiseNaEdicao_(ed); s.c.analiseDepoisDaEdicao_(ed);
  s.c.SpreadsheetApp.flush = flushBom;
  t('morreu na marca: a propriedade não diz desatualizada', () => { assert.equal(k, 2); assert.equal(s.props.m.get('analise_estado'), 'em_dia'); });
  s.an.getRange('B7003').setValue('em_dia'); // a escrita na fila se perdeu com o tempo
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B6', '1'));
  t('morreu na marca: a próxima edição marca', () => assert.equal(chave(s, 'analise.estado'), 'desatualizada'));
  // Passou do limiteDepois: grava a automação e deixa a conferência para a próxima edição (medido em 25/11).
  copia();
  // 25/11, nas cópias das oficiais: o limite é o tempo do próprio onEdit (4 s); a edição pesada (Caminho, 8 a 10 s) deixa.
  s.clock.t = 5000; ed = ev(s, 'FICHA', 'B5', '1', { r53Inicio_: 0 }); s.c.analiseNaEdicao_(ed);
  lidas = s.p.log.leituras; antes = s.p.log.escritas.length; let fl = s.p.log.flush;
  s.c.analiseDepoisDaEdicao_(ed);
  t('sem tempo: só o flush', () => { assert.equal(s.p.log.flush - fl, 1); assert.equal(s.p.log.leituras, lidas); assert.equal(s.p.log.escritas.length, antes); assert.equal(s.props.m.get('analise_estado'), undefined); assert.equal(chave(s, 'analise.estado'), 'em_dia'); });
  t('sem tempo: deixa o aviso pro clique', () => assert.equal(s.props.m.get('analise_depois'), '1'));
  t('sem tempo: aviso depois do flush', () => { const q = s.p.log.seq; assert.ok(q.lastIndexOf('flush') < q.lastIndexOf('p:analise_depois')); });
  s.clock.t = 3000; ed = ev(s, 'FICHA', 'B6', '1', { r53Inicio_: 0 }); s.c.analiseNaEdicao_(ed); s.c.analiseDepoisDaEdicao_(ed);
  t('com tempo: a próxima confere', () => { assert.equal(chave(s, 'analise.estado'), 'desatualizada'); assert.equal(s.props.m.get('analise_estado'), 'desatualizada'); });
  // O clique (onSelectionChange): sem aviso, uma leitura de propriedade; com aviso e já conferida, apaga o aviso.
  let sel = ev(s, 'FICHA', 'C9', '', { r53Inicio_: 0 }); s.clock.t = 1000;
  t('clique: aviso velho apagado', () => parado(() => { assert.equal(s.c.analiseNaSelecao_(sel), false); assert.equal(s.props.m.has('analise_depois'), false); }));
  leit = s.props.leituras;
  t('clique sem aviso: uma leitura de propriedade', () => parado(() => { assert.equal(s.c.analiseNaSelecao_(sel), false); assert.equal(s.props.leituras - leit, 1); }));
  t('clique sem evento: não quebra', () => { s.c.analiseNaSelecao_(); s.c.analiseNaSelecao_({}); });
  // Edição pesada na cópia; o clique que ela mesma dispara roda junto e ainda não vê o aviso; o próximo confere.
  copia();
  ed = ev(s, 'FICHA', 'D11', 'Vanguarda', { r53Inicio_: 0 }); s.c.analiseNaEdicao_(ed);
  s.clock.t = 500;
  t('clique junto da edição: nada', () => parado(() => assert.equal(s.c.analiseNaSelecao_(ev(s, 'FICHA', 'D11', '', { r53Inicio_: 0 })), false)));
  s.clock.t = 9000; s.c.analiseDepoisDaEdicao_(ed);
  t('Caminho frio: deixa pro clique', () => { assert.equal(s.props.m.get('analise_depois'), '1'); assert.equal(chave(s, 'analise.estado'), 'em_dia'); });
  s.clock.t = 7000;
  t('clique tarde: não começa', () => parado(() => assert.equal(s.c.analiseNaSelecao_(ev(s, 'FICHA', 'C9', '', { r53Inicio_: 0 })), false)));
  t('clique tarde: aviso fica', () => assert.equal(s.props.m.get('analise_depois'), '1'));
  s.clock.t = 2000; s.p.log.seq.length = 0;
  t('clique confere', () => assert.equal(s.c.analiseNaSelecao_(ev(s, 'FICHA', 'C9', '', { r53Inicio_: 0 })), true));
  t('clique: marca e apaga o aviso', () => { assert.equal(chave(s, 'analise.estado'), 'desatualizada'); assert.equal(s.props.m.get('analise_estado'), 'desatualizada'); assert.equal(s.props.m.has('analise_depois'), false); assert.equal(s.cart.getRange('AH4').getValue(), 'Bot: desatualizada · marque ao lado'); });
  t('clique: marca gravada antes da propriedade', () => { const q = s.p.log.seq, ip = q.lastIndexOf('p:analise_estado'), iw = q.lastIndexOf('w:ANALISE!B7003', ip); assert.ok(iw >= 0 && q.slice(iw, ip).indexOf('flush') >= 0); });
  // Sem o clique (Android?): a próxima edição leve confere, e o clique seguinte só apaga o aviso.
  copia();
  ed = ev(s, 'FICHA', 'D11', 'Vanguarda', { r53Inicio_: 0 }); s.c.analiseNaEdicao_(ed); s.clock.t = 9000; s.c.analiseDepoisDaEdicao_(ed);
  ed = ev(s, 'FICHA', 'AM26', '-1', { r53Inicio_: 0 }); s.clock.t = 0; s.c.analiseNaEdicao_(ed); s.clock.t = 1000; s.c.analiseDepoisDaEdicao_(ed);
  t('sem clique: edição leve confere', () => { assert.equal(chave(s, 'analise.estado'), 'desatualizada'); assert.equal(s.props.m.get('analise_depois'), '1'); });
  s.clock.t = 1000; s.c.analiseNaSelecao_(ev(s, 'FICHA', 'C9', '', { r53Inicio_: 0 }));
  t('sem clique: o clique seguinte só apaga o aviso', () => assert.equal(s.props.m.has('analise_depois'), false));
  // O tempo acaba no meio do clique: a propriedade fica em dia, e a próxima edição marca (como na edição).
  copia();
  ed = ev(s, 'FICHA', 'D11', 'Vanguarda', { r53Inicio_: 0 }); s.c.analiseNaEdicao_(ed); s.clock.t = 9000; s.c.analiseDepoisDaEdicao_(ed);
  k = 0; s.c.SpreadsheetApp.flush = () => { if (++k === 1) throw new Error('tempo'); };
  s.clock.t = 0; s.c.analiseNaSelecao_(ev(s, 'FICHA', 'C9', '', { r53Inicio_: 0 }));
  s.c.SpreadsheetApp.flush = flushBom;
  s.an.getRange('B7003').setValue('em_dia');
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B6', '1'));
  t('clique morreu na marca: a próxima edição marca', () => assert.equal(chave(s, 'analise.estado'), 'desatualizada'));
  // O que a própria ANALISE trata não espera: a coluna B, a caixa. Na aba de modelos, nada.
  copia();
  t('cópia: coluna B tratada na hora', () => { assert.equal(s.c.analiseNaEdicao_(ev(s, 'ANALISE', 'B10', 'x')), true); assert.equal(chave(s, 'analise.estado'), 'desatualizada'); });
  copia();
  ed = ev(s, 'ANALISE_MODELOS', 'A10', 'x');
  t('cópia: modelos não conferem', () => parado(() => { assert.equal(s.c.analiseNaEdicao_(ed), false); s.c.analiseDepoisDaEdicao_(ed); }));
  ed = ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }); s.clock.t = 0;
  t('cópia: caixa tratada na hora', () => { assert.equal(s.c.analiseNaEdicao_(ed), true); assert.equal(ed.r53AnaliseDepois_, undefined); });
  // As linhas de estado fora do fim da grade: procura na coluna A inteira e escreve na linha certa.
  copia();
  s.an.insertRowsAfter(7004, 3);
  s.an.getRange(7005, 1, 1, 2).setValues([['chave.nova', 'x']]);
  ed = ev(s, 'FICHA', 'B5', '1'); s.c.analiseNaEdicao_(ed); s.c.analiseDepoisDaEdicao_(ed);
  t('cópia: estado fora do fim da grade', () => { assert.equal(chave(s, 'analise.estado'), 'desatualizada'); assert.equal(chave(s, 'chave.nova'), 'x'); assert.equal(s.an.getRange('B7006').getValue(), ''); });
  // Cópia no meio de uma exportação: igual a antes, sem marca nova.
  s.props.m.clear(); s.an.getRange('B7003').setValue('exportando'); antes = s.p.log.escritas.length;
  ed = ev(s, 'FICHA', 'B5', '1'); s.c.analiseNaEdicao_(ed); s.c.analiseDepoisDaEdicao_(ed);
  t('cópia exportando: nada escrito', () => { assert.equal(s.p.log.escritas.length, antes); assert.equal(s.props.m.get('analise_estado'), 'exportando'); });
  t('sem evento: não quebra', () => { s.c.analiseDepoisDaEdicao_(); s.c.analiseDepoisDaEdicao_({}); });

  // 7. Ficha viva nunca exportada: a edição não escreve nada.
  s = cenario(fonte, 50);
  antes = s.p.log.escritas.length; ed = ev(s, 'FICHA', 'B5', '1');
  t('viva: não tratada', () => { assert.equal(s.c.analiseNaEdicao_(ed), false); s.c.analiseDepoisDaEdicao_(ed); });
  t('viva: nada escrito', () => { assert.equal(s.p.log.escritas.length, antes); assert.equal(s.props.m.get('analise_estado'), 'viva'); });
  t('viva: ANALISE com fórmulas', () => assert.equal(formulasB(s), 49));

  // 8. Juntar: fórmula nova na B congelada entra pelo menu; a caixa não junta.
  s.c.exportarParaOBot();
  s.p.dados.extra = 'EXTRA';
  s.an.getRange(4, 2).setFormulas([['=D(extra)']]);
  s.clock.t = 0; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('caixa não junta', () => assert.equal(chave(s, 'chave.1'), 'v1'));
  s.an.getRange(4, 2).setFormulas([['=D(extra)']]);
  s.c.exportarParaOBot();
  t('menu junta', () => { assert.equal(chave(s, 'chave.1'), 'EXTRA'); assert.equal(s.mod().getRange(4, 1).getValue(), '=D(extra)'); });

  // 9. Sem modelos e sem fórmulas: erro claro, sem mexer.
  s = cenario(fonte, 20);
  s.an.getRange(3, 2, 20, 1).copyTo(s.an.getRange(3, 2, 20, 1), { contentsOnly: true });
  t('sem modelos', () => assert.throws(() => s.c.exportarParaOBot(), /não há de onde exportar/));
  t('sem modelos: nada marcado', () => assert.equal(chave(s, 'analise.estado'), undefined));

  // 10. Linha 4 da CARTEIRA ocupada: não instala a caixa, exporta igual.
  s = cenario(fonte, 20);
  s.cart.getRange('AH4').setValue('outra coisa');
  r = s.c.exportarParaOBot();
  t('ocupada: exporta', () => assert.equal(r.estado, 'em_dia'));
  t('ocupada: sem caixa', () => { assert.equal(s.cart.getRange('AT4').getDataValidation(), null); assert.equal(s.cart.getRange('AH4').getValue(), 'outra coisa'); });

  // 11. Outra exportação rodando.
  s = cenario(fonte, 20); s.props.ocupada = true;
  t('ocupada pela trava', () => assert.equal(s.c.exportarParaOBot().estado, 'ocupada'));

  // 12. Montagem: com o pacote R53 exporta; sem ele (sem ganchos) a ANALISE fica viva.
  s = cenario(fonte, 20);
  t('montagem sem pacote', () => { assert.match(s.c.analiseExportarNaMontagem_(), /^viva/); assert.equal(formulasB(s), 19); });
  s.c.r53Modulo_ = () => ({});
  t('montagem com pacote', () => assert.equal(s.c.analiseExportarNaMontagem_(), 'em_dia 19/19'));

  // 13. Caixa numa ficha sem modelos (a primeira exportação pelo celular): grava os modelos e para, sem bloco.
  s = cenario(fonte, 7000);
  s.clock.passo = 2000; s.props.m.set('analise_bloco_ms', '50000'); // ainda antes da metade, mas criou os modelos
  s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('caixa sem modelos: grava e para', () => { assert.ok(s.mod() && s.mod().isSheetHidden()); assert.equal(s.props.m.get('analise_modelos_n'), '7001'); assert.equal(s.props.m.has('analise_exportar_prox'), false); assert.equal(formulasB(s), 6999); assert.equal(chave(s, 'analise.estado'), 'exportando'); });
  s.clock.t = 0; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('caixa sem modelos: a segunda marcação exporta', () => assert.equal(chave(s, 'analise.estado'), 'em_dia'));

  // 14. Aba de modelos criada e vazia (execução que morreu gravando): a caixa refaz, não trava.
  s = cenario(fonte, 20);
  s.p.ss.insertSheet('ANALISE_MODELOS');
  s.clock.passo = 1000;
  s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('modelos vazios: refeitos', () => { assert.equal(s.mod().getRange(3, 1).getValue(), '=D(k0)'); assert.equal(s.props.m.get('analise_modelos_n'), '21'); });
  s.clock.t = 0; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('modelos vazios: depois exporta', () => assert.equal(chave(s, 'analise.estado'), 'em_dia'));

  // 15. Bloco medido acima do limite: a caixa ainda faz um bloco por marcação.
  s = cenario(fonte, 7000);
  s.c.exportarParaOBot(); s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B5', '1'));
  s.props.m.set('analise_bloco_ms', '50000');
  s.clock.t = 0; s.clock.passo = 15000; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('bloco lento: um por marcação', () => assert.equal(s.props.m.get('analise_exportar_prox'), '4002'));
  s.clock.t = 11000; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('bloco lento: passou da metade, não força', () => assert.equal(s.props.m.get('analise_exportar_prox'), '4002'));
  return n;
}

let total = suite(FONTE);

// ---------- ganchos no repositório ----------
const ler = p => fs.readFileSync(path.join(RAIZ, p), 'utf8');
const um = (texto, trecho, onde) => assert.equal(texto.split(trecho).length - 1, 1, onde + ': ' + trecho.slice(0, 60));
// O Codigo.gs (o onEdit de dentro do módulo) fica sem gancho: a entrada do pacote já chama, e o caminho_leve.js
// reconstrói a história do onEdit dele por trechos exatos.
assert.equal(ler('apps-script/Codigo.gs').indexOf('analiseNaEdicao_'), -1, 'Codigo.gs sem gancho');
for (const p of ['apps-script/Ficha.gs', 'ficha/modelo.gs.js']) um(ler(p), "feito.push('ANALISE exportada: ' + analiseExportarNaMontagem_());", p);
const emp = ler('r53/empacotar_script.py');
um(emp, "'Socorro.gs','AnaliseEstatica.gs'])", 'pacote: fora do módulo');
um(emp, "(OUT/'AnaliseEstatica.gs').write_text(", 'pacote: arquivo publicado');
um(emp, 'guard+\'if(typeof analiseNaEdicao_==="function"&&analiseNaEdicao_(e))return;', 'pacote: gancho do onEdit');
um(emp, 'analiseNaEdicao_(e))return;' + depois.ABRE + 'if(r53NivelRestaurar_(e)', 'pacote: abre a conferência no fim');
um(emp, 'return r53Modulo_().onEdit(e);' + depois.FECHA, 'pacote: conferência no fim');
um(emp, 'r53CuraMenu_();if(typeof analiseMenu_==="function")analiseMenu_();', 'pacote: menu');
um(emp, '\n else if(pending)return r53Modulo_().onSelectionChange(e);\n' + selecao.LINHA_SEL + '\n}\n', 'pacote: conferência no clique');
um(ler('nuvem-b47/conferir.py'), "'Socorro.gs', 'AnaliseEstatica.gs'}", 'conferir: pacote');
total += 11;

// ---------- preparador das oficiais ----------
const salario = 'function onEdit(e){return r53SalarioOnEdit_(e);}\nfunction r53OnEditOriginal_(e){if(e)e.r53Inicio_=Date.now();if(r53NivelRestaurar_(e))return;}\n' +
  'function onOpen(e){if(typeof r53CuraMenu_==="function")r53CuraMenu_();e=e||{};}\n';
const pacote = 'function onEdit(e){if(e)e.r53Inicio_=Date.now();if(r53NivelRestaurar_(e))return;}\nfunction onOpen(e){if(typeof r53CuraMenu_==="function")r53CuraMenu_();e=e||{};}\n';
// Forma das oficiais em 17/11/2026: o onEdit de entrada roda os restauradores e depois o salário; o original também
// tem guarda. O gancho tem de ir no de entrada, e o onOpen é o curto.
const oficial = 'function r53OnEditOriginal_(e){if(e)e.r53Inicio_=Date.now();if(r53RestaurarVersaoPublica_(e))return;}\n' +
  'function onOpen(e){r53CuraMenu_();e=e||{};}\n' +
  'function onEdit(e){if(e)e.r53Inicio_=Date.now();if(r53NivelRestaurar_(e))return r53ContinuarPaletaPendente_(e);return r53SalarioOnEdit_(e);}\n';
{
  const out = prep.preparar(oficial);
  assert.ok(out.indexOf('function onEdit(e){if(e)e.r53Inicio_=Date.now();' + prep.GANCHO_EDIT) >= 0, 'oficial: gancho no onEdit de entrada');
  assert.ok(out.indexOf('function r53OnEditOriginal_(e){if(e)e.r53Inicio_=Date.now();if(r53Restaurar') >= 0, 'oficial: original intocado');
  assert.ok(out.indexOf('function onOpen(e){r53CuraMenu_();' + prep.GANCHO_MENU) >= 0, 'oficial: menu');
  assert.equal(prep.reverter(out), oficial, 'oficial: reverter');
  total += 4;
}
for (const [nome, src] of [['salário', salario], ['pacote', pacote], ['oficial', oficial]]) {
  const out = prep.preparar(src);
  assert.equal(out.split(prep.GANCHO_EDIT).length - 1, 1, nome);
  assert.ok(out.indexOf('Date.now();' + prep.GANCHO_EDIT + 'if(r53NivelRestaurar_') > 0, nome + ': gancho logo depois da guarda');
  assert.ok(out.indexOf('r53CuraMenu_();' + prep.GANCHO_MENU) > 0, nome + ': menu');
  assert.throws(() => prep.preparar(out), /já presentes/, nome);
  assert.equal(prep.reverter(out), src, nome + ': reverter');
  total += 5;
}
assert.throws(() => prep.preparar('function onEdit(e){}'), /Guarda do onEdit/); total++;
new vm.Script(prep.trecho()); new vm.Script(prep.trecho(true)); total += 2;

// ---------- conferência no fim da edição ----------
for (const [nome, src] of [['salário', salario], ['pacote', pacote], ['oficial', oficial], ['sem quebra no fim', oficial.trimEnd()], ['CRLF', oficial.replace(/\n/g, '\r\n')]]) {
  const com = prep.preparar(src), out = depois.preparar(com);
  assert.equal(out.length, com.length + depois.ABRE.length + depois.FECHA.length, nome + ': só o embrulho entrou');
  assert.ok(out.indexOf(prep.GANCHO_EDIT + depois.ABRE + 'if(r53NivelRestaurar_') > 0, nome + ': o resto do onEdit no try');
  assert.throws(() => depois.preparar(out), /já presente/, nome);
  assert.equal(depois.reverter(out), com, nome + ': reverter');
  total += 4;
}
assert.throws(() => depois.preparar(oficial), /ausente ou repetido/);
assert.throws(() => depois.preparar(prep.preparar(oficial).replace('return r53SalarioOnEdit_(e);}', 'return r53SalarioOnEdit_(e);\n}')), /não acaba|não fecham/);
assert.throws(() => depois.preparar(prep.preparar(oficial).replace('return r53SalarioOnEdit_(e);}', 'return r53SalarioOnEdit_(e);}function outra(){}')), /Outra função/);
assert.throws(() => depois.reverter(prep.preparar(oficial)), /ausente ou repetida/);
new vm.Script(depois.trecho()); new vm.Script(depois.trecho(true)); total += 6;
// O onEdit preparado rodando: a conferência vem por último, também quando a automação falha ou um restaurador responde.
for (const [nome, o] of Object.entries({ normal: {}, restaurador: { nivel: true }, falha: { falha: true }, caixa: { caixa: true }, antigo: { antigo: true } })) {
  const ordem = [], c = {
    analiseNaEdicao_: () => { ordem.push('antes'); return !!o.caixa; },
    r53NivelRestaurar_: () => { ordem.push('nivel'); return !!o.nivel; },
    r53ContinuarPaletaPendente_: () => 'paleta',
    r53SalarioOnEdit_: () => { ordem.push('automação'); if (o.falha) throw new Error('quebrou'); return 'salário'; }
  };
  if (!o.antigo) c.analiseDepoisDaEdicao_ = () => { ordem.push('depois'); };
  vm.createContext(c);
  vm.runInContext(depois.preparar(prep.preparar(oficial)), c);
  const roda = () => vm.runInContext('onEdit({})', c);
  if (o.falha) assert.throws(roda, /quebrou/); else assert.equal(roda(), o.caixa ? undefined : o.nivel ? 'paleta' : 'salário', nome);
  assert.deepEqual(ordem, { normal: ['antes', 'nivel', 'automação', 'depois'], restaurador: ['antes', 'nivel', 'depois'], falha: ['antes', 'nivel', 'automação', 'depois'], caixa: ['antes'], antigo: ['antes', 'nivel', 'automação'] }[nome], nome);
  total += 2;
}
// ---------- conferência no clique (25/11) ----------
// Forma das oficiais (lida em 16/11) e forma do empacotar_script.py; nas duas a linha entra antes da chave do fim.
const selOficial = 'function onEdit(e){if(e)e.r53Inicio_=Date.now();if(typeof analiseNaEdicao_==="function"&&analiseNaEdicao_(e))return;}\n' +
  'function onSelectionChange(e) {\n if(e)e.r53Inicio_=Date.now();\n if(!e || !e.range)return;\n var pending=true;\n' +
  " try {pending=!!PropertiesService.getDocumentProperties().getProperty('paleta_pendente');}catch(err){}\n" +
  ' var opening=e.abrir;\n if(opening)return r53Modulo_().onSelectionChange(e);\n if(pending)r53PaletaLeve_().continuar(e);\n}\n' +
  'function acabar(){return 1;}\n';
const selPacote = selOficial.replace(' if(pending)r53PaletaLeve_().continuar(e);\n',
  " if(pending && typeof r53PaletaLeve_==='function')r53PaletaLeve_().continuar(e);\n else if(pending)return r53Modulo_().onSelectionChange(e);\n");
for (const [nome, src] of [['oficial', selOficial], ['pacote', selPacote], ['CRLF', selOficial.replace(/\n/g, '\r\n')], ['sem quebra no fim', selOficial.slice(0, selOficial.indexOf('function acabar'))]]) {
  const out = selecao.preparar(src), nl = src.indexOf('\r\n') >= 0 ? '\r\n' : '\n';
  assert.equal(out.length, src.length + nl.length + selecao.LINHA_SEL.length, nome + ': só a linha entrou');
  assert.ok(out.indexOf(selecao.LINHA_SEL + nl + '}') > out.indexOf('function onSelectionChange'), nome + ': antes da chave do fim');
  assert.throws(() => selecao.preparar(out), /já presente/, nome);
  assert.equal(selecao.reverter(out), src, nome + ': reverter');
  total += 4;
}
assert.throws(() => selecao.preparar('function onEdit(e){}\n'), /ausente ou repetido/);
assert.throws(() => selecao.preparar(selOficial + selOficial.replace(/onEdit/g, 'x')), /ausente ou repetido/);
assert.throws(() => selecao.preparar(selOficial.replace(' var pending=true;\n', '')), /pending/);
assert.throws(() => selecao.reverter(selOficial), /ausente ou repetida/);
new vm.Script(selecao.trecho()); new vm.Script(selecao.trecho(true)); total += 6;
// O onSelectionChange preparado rodando: confere só sem paleta pendente e fora da navegação das invocações.
for (const [nome, o, esperado] of [['nada pendente', {}, ['clique']], ['paleta pendente', { paleta: true }, ['paleta']],
  ['navegação', { abrir: true }, ['módulo']], ['sem evento', { semEvento: true }, []], ['antigo', { antigo: true }, []]]) {
  for (const src of [selOficial, selPacote]) {
    const ordem = [], c = {
      PropertiesService: { getDocumentProperties: () => ({ getProperty: () => (o.paleta ? '1' : null) }) },
      r53Modulo_: () => ({ onSelectionChange: () => { ordem.push('módulo'); } }),
      r53PaletaLeve_: () => ({ continuar: () => { ordem.push('paleta'); } }), Date
    };
    if (!o.antigo) c.analiseNaSelecao_ = () => { ordem.push('clique'); };
    vm.createContext(c);
    vm.runInContext(selecao.preparar(src), c);
    c.ev = o.semEvento ? undefined : { range: {}, abrir: !!o.abrir };
    vm.runInContext('onSelectionChange(ev)', c);
    assert.deepEqual(ordem, esperado, nome);
    total++;
  }
}
// O trecho do console aplica o mesmo que o preparar, num Monaco falso.
(async () => {
  for (const desfazer of [false, true]) {
    const modelo = { v: desfazer ? prep.preparar(oficial) : oficial, getValue() { return this.v; }, setValue(x) { this.v = x; } };
    const ctx = { monaco: { editor: { getModels: () => [modelo] } }, window: {}, crypto: require('crypto').webcrypto, TextEncoder };
    vm.createContext(ctx);
    const res = await vm.runInContext(prep.trecho(desfazer).replace(/^await /, ''), ctx);
    assert.ok(!/^ERRO/.test(res), res);
    assert.equal(modelo.v, desfazer ? oficial : prep.preparar(oficial));
    const com = prep.preparar(oficial), m2 = { v: desfazer ? depois.preparar(com) : com, getValue() { return this.v; }, setValue(x) { this.v = x; } };
    const ctx2 = { monaco: { editor: { getModels: () => [m2] } }, window: {}, crypto: require('crypto').webcrypto, TextEncoder };
    vm.createContext(ctx2);
    const res2 = await vm.runInContext(depois.trecho(desfazer).replace(/^await /, ''), ctx2);
    assert.ok(!/^ERRO/.test(res2), res2);
    assert.equal(m2.v, desfazer ? com : depois.preparar(com));
    const m3 = { v: desfazer ? selecao.preparar(selOficial) : selOficial, getValue() { return this.v; }, setValue(x) { this.v = x; } };
    const m3outro = { v: 'function onSelectionChange(e) {\n var pending=1;\n}\n', getValue() { return this.v; }, setValue() { throw new Error('mexeu no arquivo errado'); } };
    const ctx3 = { monaco: { editor: { getModels: () => [m3outro, m3] } }, window: {}, crypto: require('crypto').webcrypto, TextEncoder };
    vm.createContext(ctx3);
    const res3 = await vm.runInContext(selecao.trecho(desfazer).replace(/^await /, ''), ctx3);
    assert.ok(!/^ERRO/.test(res3), res3);
    assert.equal(m3.v, desfazer ? selOficial : selecao.preparar(selOficial));
    total += 3;
  }

  // ---------- defeitos plantados ----------
  const DEFEITOS = [
    ['sem congelar', 'faixa.copyTo(faixa, {contentsOnly: true});', ''],
    ['sem guardar o progresso', "props.setProperty(C.propProx, String(prox));", ''],
    ['sem marcar desatualizada', "if (est === 'em_dia' || naB) analiseMarcar_(ss, null, props, 'desatualizada', null, null, gravar);", ''],
    ['marca a cada edição', "if (est === 'em_dia' || naB)", "if (est !== 'viva' || naB)"],
    ['sem juntar no menu', 'if (vazia || juntar) {', 'if (vazia) {'],
    ['modelos vazios não refeitos', 'var vazia = !lista.some(Boolean);', 'var vazia = !m;'],
    ['caixa relê a coluna A', 'if (!juntar) { try { linhas', 'if (false) { try { linhas'],
    ['caixa relê o fim dos modelos', 'if (!n || juntar) n = m.getLastRow() - 1;', 'n = m.getLastRow() - 1;'],
    ['caixa lê os modelos inteiros', 'if (m && n > 0 && total > 0 && !juntar) return', 'if (false) return'],
    ['caixa perde a conta do feito', "props.setProperty(C.propFeitas, String(feitas));", ''],
    ['sem garantia de um bloco', ' || (!blocos && !lidos.novos && Date.now() - t0 < limite / 2)', ''],
    ['bloco depois dos modelos', '(!blocos && !lidos.novos &&', '(!blocos &&'],
    ['sem flush depois de congelar', 'acaba (17/11).\n      SpreadsheetApp.flush();', 'acaba (17/11).'],
    ['junta na caixa', "ANALISE_EST_.limiteCaixa, false);", "ANALISE_EST_.limiteCaixa, true);"],
    ['sem a versão 13', 'an.getRange(linhas.versao, 2).setValue("\'" + C.versao);', ''],
    ['caixa não desmarca', 'e.range.setValue(false);', ''],
    ['desmarcar não exporta', "if (v !== 'TRUE' && v !== 'FALSE') return true;", "if (v !== 'TRUE') return true;"],
    ['edição no meio não recomeça', 'props.deleteProperty(C.propProx);\n    if (!naB)', 'if (!naB)'],
    ['B não limpa', 'if (naB) r.getSheet().getRange(r.getRow(), 2, r.getNumRows(), 1).clearContent();', ''],
    ['cópia sem sincronizar', "props.getProperty(ANALISE_EST_.prop) || analiseSincronizar_(props)", "props.getProperty(ANALISE_EST_.prop) || 'viva'"],
    ['cópia confere antes da automação', 'if (!est && !naB) { e.r53AnaliseDepois_ = true; return false; }', ''],
    ['cópia não confere no fim', 'e.r53AnaliseDepois_ = true; return false;', 'return false;'],
    ['cópia confere duas vezes', 'e.r53AnaliseDepois_ = false;', ''],
    ['cópia: coluna B espera', 'if (!est && !naB)', 'if (!est)'],
    ['cópia: modelos conferem', 'if (nome === C.modelos) return false;', ''],
    ['cópia: sem flush da automação', 'try {\n    SpreadsheetApp.flush();', 'try {'],
    ['cópia: confere sem tempo', 'Date.now() - e.r53Inicio_ > ANALISE_EST_.limiteDepois) {', 'false) {'],
    ['cópia: limite antes do flush', '  try {\n    SpreadsheetApp.flush();\n    var props', '  try {\n    if (typeof e.r53Inicio_ === \'number\' && Date.now() - e.r53Inicio_ > ANALISE_EST_.limiteDepois) return;\n    SpreadsheetApp.flush();\n    var props'],
    ['cópia: limite curto', 'limiteDepois: 4000,', 'limiteDepois: 2000,'],
    ['cópia: limite de 24/11', 'limiteDepois: 4000,', 'limiteDepois: 12000,'],
    ['sem aviso pro clique', "props.setProperty(ANALISE_EST_.propDepois, '1');", ''],
    ['clique sem olhar o aviso', 'if (!props.getProperty(C.propDepois)) return false;', ''],
    ['clique não apaga aviso velho', 'if (props.getProperty(C.prop)) { props.deleteProperty(C.propDepois); return false; }', ''],
    ['clique sem limite', 'Date.now() - e.r53Inicio_ > C.limiteSelecao) return false;', 'false) return false;'],
    ['clique sem gravar a marca', 'analiseVelha_(e, props, analiseSincronizar_(props), false, true);', 'analiseVelha_(e, props, analiseSincronizar_(props), false);'],
    ['clique não apaga o aviso no fim', '    props.deleteProperty(C.propDepois);\n    return true;', '    return true;'],
    ['cópia: propriedade antes da marca', '  if (gravar) SpreadsheetApp.flush();\n', ''],
    ['cópia: marca sem pedir gravação', '|| analiseSincronizar_(props), false, true);', '|| analiseSincronizar_(props), false);'],
    ['cópia: não confere o fim da grade', "if (fim[0][0] === 'analise.estado' && fim[1][0] === 'analise.exportada_em') {", 'if (true) {'],
    ['cópia: sempre a coluna inteira', "if (fim[0][0] === 'analise.estado' && fim[1][0] === 'analise.exportada_em') {", 'if (false) {'],
    ['cópia: não guarda as linhas', 'if (linhas.estado && linhas.data) props.setProperty(C.propLinhas, JSON.stringify(linhas));', ''],
    ['modelos visíveis', 'if (!m.isSheetHidden()) m.hideSheet();', ''],
    ['caixa por cima', 'if (ocupada) {', 'if (false) {'],
    ['cópia não reconhece a caixa', "CHECKBOX) { props.setProperty(C.propCaixa, '1'); return; }", 'CHECKBOX) { return; }'],
    ['ignora o tempo', 'Date.now() - t0 + est < limite', 'true'],
    ['sem a duração medida', 'est = Date.now() - tb;', ''],
    ['força bloco depois da metade', ' && Date.now() - t0 < limite / 2)', ')'],
    ['linhas sem flush', 'tempo acaba.\n    SpreadsheetApp.flush();', 'tempo acaba.'],
    ['caixa com o bloco do menu', 'var tam = juntar ? C.bloco : C.blocoCaixa;', 'var tam = C.bloco;'],
    ['caixa sem flush', 'insertCheckboxes().setValue(false);\n  SpreadsheetApp.flush();', 'insertCheckboxes().setValue(false);']
  ];
  for (const [nome, velho, novo] of DEFEITOS) {
    assert.equal(FONTE.split(velho).length - 1, 1, 'defeito ' + nome + ': trecho não encontrado');
    let caiu = false;
    try { suite(FONTE.replace(velho, () => novo)); } catch (err) { caiu = true; }
    assert.ok(caiu, 'defeito plantado passou: ' + nome);
    total++;
  }
  console.log('analise_estatica: ' + total + ' verificações, ' + DEFEITOS.length + ' defeitos plantados derrubados');
})().catch(err => { console.error(err); process.exit(1); });
