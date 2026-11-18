'use strict';
// ANALISE estática (17/11/2026): apps-script/AnaliseEstatica.gs numa planilha falsa, os ganchos (Codigo, Ficha,
// pacote) e o preparador das oficiais. No fim, defeitos plantados no exportador: cada um tem de derrubar o teste.
//   node r53/testes/analise_estatica.js
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert/strict');
const RAIZ = path.resolve(__dirname, '..', '..');
const FONTE = fs.readFileSync(path.join(RAIZ, 'apps-script/AnaliseEstatica.gs'), 'utf8');
const prep = require(path.join(RAIZ, 'r53/diagnostico-android/preparar_analise_estatica.js'));

// ---------- planilha falsa ----------
// Fórmula "=D(k)" vale dados[k] na hora da leitura; copyTo com contentsOnly troca pela leitura (como o Sheets).
function letras(c) { let s = ''; while (c) { const r = (c - 1) % 26; s = String.fromCharCode(65 + r) + s; c = (c - 1 - r) / 26; } return s; }
function pos(a1) { const m = /^([A-Z]+)(\d+)$/.exec(a1); let c = 0; for (const ch of m[1]) c = c * 26 + ch.charCodeAt(0) - 64; return [+m[2], c]; }
function novaPlanilha(clock) {
  const dados = {}, abas = [], log = { escritas: [], flush: 0, leituras: 0, seq: [] };
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
          getValues: () => (log.leituras++, grade(valor)), getValue: () => (log.leituras++, valor(r0, c0)),
          getFormulas: () => (log.leituras++, grade((r, c) => (celulas.get(k(r, c)) || {}).f || '')),
          setValues: m => { escrever(m, false); return rg; }, setValue: v => { escrever([[v]], false); return rg; },
          setFormulas: m => { m.forEach(l => l.forEach(f => assert.ok(f.charAt(0) === '=', 'setFormulas sem =: ' + f))); escrever(m, true); return rg; },
          clearContent: () => { grade((r, c) => celulas.delete(k(r, c))); log.escritas.push(nome + '!limpa'); return rg; },
          copyTo: (dest, op) => {
            if (op && op.contentsOnly) { const vs = grade(valor); vs.forEach((l, i) => l.forEach((v, j) => celulas.set(k(r0 + i, c0 + j), { v }))); log.escritas.push(nome + '!congela'); }
            else if (op && op.formatOnly) { const d = dest; grade((r, c) => { const x = dv.get(k(r, c)); if (x) d.getSheet()._dv.set(k(d.getRow() + r - r0, d.getColumn() + c - c0), x); }); }
          },
          merge: () => rg,
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
  r = null;
  t('caixa tratada aqui', () => assert.equal(s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 })), true));
  t('caixa desmarcada', () => assert.equal(s.cart.getRange('AT4').getValue(), false));
  t('parcial: exportando e progresso guardado', () => { assert.equal(chave(s, 'analise.estado'), 'exportando'); assert.equal(s.props.m.get('analise_exportar_prox'), '4002'); assert.match(s.cart.getRange('AH4').getValue(), /^Bot: exportando 3998\/6999 · marque de novo$/); });
  t('duração do bloco guardada', () => assert.equal(s.props.m.get('analise_bloco_ms'), '16000'));
  t('blocos feitos já sem fórmula', () => assert.equal(formulasB(s), 0));
  t('primeiro bloco já com o valor novo', () => assert.equal(chave(s, 'chave.0'), 'NOVO'));
  s.clock.t = 0; let lidas = s.p.log.leituras;
  s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('caixa lê a planilha uma vez só', () => assert.equal(s.p.log.leituras - lidas, 1));
  t('segunda marcação termina', () => { assert.equal(chave(s, 'analise.estado'), 'em_dia'); assert.equal(s.props.has ? 0 : s.props.m.has('analise_exportar_prox'), false); });
  t('caixa desmarcada à toa não exporta', () => { const f = s.p.log.flush; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'FALSE')); assert.equal(s.p.log.flush, f); });

  // 4. Editou no meio da exportação: recomeça do começo.
  s.p.dados.k6998 = 'FIM';
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B5', '2'));
  s.clock.t = 0; s.c.analiseNaEdicao_(ev(s, 'CARTEIRA', 'AT4', 'TRUE', { r53Inicio_: 0 }));
  t('parcial de novo', () => assert.equal(s.props.m.get('analise_exportar_prox'), '4002'));
  s.p.dados.k0 = 'MEIO';
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B5', '9'));
  t('edição no meio apaga o progresso', () => { assert.equal(s.props.m.has('analise_exportar_prox'), false); assert.equal(s.cart.getRange('AH4').getValue(), 'Bot: editada no meio · marque de novo'); });
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

  // 6. Cópia da ficha: sem propriedades, lê o estado da ANALISE uma vez.
  s.props.m.clear();
  s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B5', '1'));
  t('cópia em dia vira desatualizada', () => { assert.equal(s.props.m.get('analise_estado'), 'desatualizada'); assert.equal(chave(s, 'analise.estado'), 'desatualizada'); });
  t('cópia reconhece a caixa', () => assert.equal(s.props.m.get('analise_caixa'), '1'));

  // 7. Ficha viva nunca exportada: a edição não escreve nada.
  s = cenario(fonte, 50);
  antes = s.p.log.escritas.length;
  t('viva: não tratada', () => assert.equal(s.c.analiseNaEdicao_(ev(s, 'FICHA', 'B5', '1')), false));
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
um(emp, 'r53CuraMenu_();if(typeof analiseMenu_==="function")analiseMenu_();', 'pacote: menu');
um(ler('nuvem-b47/conferir.py'), "'Socorro.gs', 'AnaliseEstatica.gs'}", 'conferir: pacote');
total += 8;

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
// O trecho do console aplica o mesmo que o preparar, num Monaco falso.
(async () => {
  for (const desfazer of [false, true]) {
    const modelo = { v: desfazer ? prep.preparar(oficial) : oficial, getValue() { return this.v; }, setValue(x) { this.v = x; } };
    const ctx = { monaco: { editor: { getModels: () => [modelo] } }, window: {}, crypto: require('crypto').webcrypto, TextEncoder };
    vm.createContext(ctx);
    const res = await vm.runInContext(prep.trecho(desfazer).replace(/^await /, ''), ctx);
    assert.ok(!/^ERRO/.test(res), res);
    assert.equal(modelo.v, desfazer ? oficial : prep.preparar(oficial));
    total++;
  }

  // ---------- defeitos plantados ----------
  const DEFEITOS = [
    ['sem congelar', 'faixa.copyTo(faixa, {contentsOnly: true});', ''],
    ['sem guardar o progresso', "props.setProperty(C.propProx, String(prox));", ''],
    ['sem marcar desatualizada', "if (est === 'em_dia' || naB) analiseMarcar_(ss, null, props, 'desatualizada');", ''],
    ['marca a cada edição', "if (est === 'em_dia' || naB)", "if (est !== 'viva' || naB)"],
    ['sem juntar no menu', 'if (vazia || juntar) {', 'if (vazia) {'],
    ['modelos vazios não refeitos', 'var vazia = !lista.some(Boolean);', 'var vazia = !m;'],
    ['caixa relê a coluna A', 'if (!juntar) { try { linhas', 'if (false) { try { linhas'],
    ['caixa relê o fim dos modelos', 'if (!n || juntar) n = m.getLastRow() - 1;', 'n = m.getLastRow() - 1;'],
    ['sem garantia de um bloco', ' || (!blocos && !lidos.novos && Date.now() - t0 < limite / 2)', ''],
    ['bloco depois dos modelos', '(!blocos && !lidos.novos &&', '(!blocos &&'],
    ['sem flush depois de congelar', 'acaba (17/11).\n      SpreadsheetApp.flush();', 'acaba (17/11).'],
    ['junta na caixa', "ANALISE_EST_.limiteCaixa, false);", "ANALISE_EST_.limiteCaixa, true);"],
    ['sem a versão 13', 'an.getRange(linhas.versao, 2).setValue("\'" + C.versao);', ''],
    ['caixa não desmarca', 'e.range.setValue(false);', ''],
    ['edição no meio não recomeça', 'props.deleteProperty(C.propProx);\n      if (!naB)', 'if (!naB)'],
    ['B não limpa', 'if (naB) r.getSheet().getRange(r.getRow(), 2, r.getNumRows(), 1).clearContent();', ''],
    ['cópia sem sincronizar', "props.getProperty(C.prop) || analiseSincronizar_(props)", "props.getProperty(C.prop) || 'viva'"],
    ['modelos visíveis', 'if (!m.isSheetHidden()) m.hideSheet();', ''],
    ['caixa por cima', 'if (ocupada) {', 'if (false) {'],
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
