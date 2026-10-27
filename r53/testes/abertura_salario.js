'use strict';
// A abertura sem a releitura diária do salário (27/10/2026). O salarioCongelar_ do Salarios.gs com a DADOS_SALARIOS de
// mentira: sem carteira emitida, a próxima conferência vai para daqui a 3650 dias (antes, amanhã); com a carteira
// emitida, nada muda. E a conferência do SalarioLote, que guarda essa data e só relê quando ela vence ou é apagada.
const fs = require('fs'), vm = require('vm'), assert = require('assert'), { execSync } = require('child_process');
let checks = 0;
function eq(a, b, m) { assert.deepStrictEqual(a, b, m); checks++; }
const novo = fs.readFileSync('apps-script/Salarios.gs', 'utf8');
const antigo = execSync('git show 9536746:apps-script/Salarios.gs').toString('utf8');
const lote = fs.readFileSync('r53/diagnostico-android/salario_lote.gs', 'utf8');
const { par, aplicar } = require('../diagnostico-android/preparar_abertura_salario');
// O Salarios.gs logo depois desta troca (57117fb); a de 27/10 das missões veio em seguida, com o próprio teste.
eq(aplicar(antigo, par()), execSync('git show 57117fb:apps-script/Salarios.gs').toString('utf8'), 'o par do preparador reproduz o Salarios.gs');

const HOJE = 46322;
function mundo(fonte, emitida, linhas) {
 const lidas = [], props = new Map(), gravadas = [];
 const v = Array.from({ length: 129 }, () => Array(10).fill(''));
 v[0][1] = emitida ? 46300 : ''; v[1][1] = 0; v[4][1] = 0; v[5][1] = 10; v[6][1] = 30;
 (linhas || []).forEach((l, i) => { v[9 + i] = l; });
 const dados = { getRange: a => ({ getValues() { lidas.push(a); return v.map(r => r.slice()); } }) };
 const livro = { insertRowsAfter() {}, getRange: () => ({ setValues(m) { gravadas.push(m.length); } }) };
 const ss = { getSheetByName: n => n === 'DADOS_SALARIOS' ? dados : n === 'SALÁRIOS' ? livro : null };
 const ctx = { console: { log() {} }, Date, JSON, Number, isFinite, Math,
  Utilities: { formatDate: () => '2026-10-27' },
  ScriptApp: { getScriptId: () => 'x' },
  LockService: { getDocumentLock: () => ({ tryLock: () => true, releaseLock() {} }) },
  SpreadsheetApp: { flush() {}, getActive: () => ss },
  PropertiesService: { getScriptProperties: () => ({ getProperty: () => null }),
   getDocumentProperties: () => ({ getProperty: k => props.has(k) ? props.get(k) : null, setProperty: (k, x) => props.set(k, x), deleteProperty: k => props.delete(k) }) } };
 vm.createContext(ctx); vm.runInContext(fonte, ctx); vm.runInContext(lote, ctx);
 ctx.salarioHoje_ = () => HOJE;
 return { ctx, ss, lidas, props, gravadas };
}
// Sem carteira: antes, amanhã; agora, longe. Com carteira e sem período vencido, igual.
for (const [emitida, esperado] of [[false, HOJE + 3650], [true, 46300 + 30]]) {
 const a = mundo(antigo, emitida), b = mundo(novo, emitida);
 const fa = a.ctx.salarioCongelar_(a.ss, HOJE), fb = b.ctx.salarioCongelar_(b.ss, HOJE);
 eq(fb.novos, 0); eq(fb.proximo, esperado);
 eq(fa.proximo, emitida ? esperado : HOJE + 1, 'o de antes');
}
// Com período vencido: congela igual, e a data é a mesma conta de antes.
{
 const linha = ['SAL1:46300:46330', 46300, 46330, 1, 2, 3, 4, 5, 6, 7];
 const a = mundo(antigo, true, [linha]), b = mundo(novo, true, [linha]);
 eq(JSON.stringify(b.ctx.salarioCongelar_(b.ss, HOJE)), JSON.stringify(a.ctx.salarioCongelar_(a.ss, HOJE)));
 eq(b.gravadas, a.gravadas);
}
// A abertura: a primeira confere e guarda a data longe; as seguintes, no mesmo dia ou em outro, não leem nada.
{
 const b = mundo(novo, false);
 b.ctx.r53SalarioConferir_(b.ss, Date.now(), b.ctx.PropertiesService.getDocumentProperties());
 eq(b.lidas.length, 1); eq(b.props.get('salario_proximo'), String(HOJE + 3650));
 for (const dia of [HOJE, HOJE + 1, HOJE + 400]) { b.ctx.salarioHoje_ = () => dia; b.ctx.r53SalarioConferir_(b.ss, Date.now(), b.ctx.PropertiesService.getDocumentProperties()); }
 eq(b.lidas.length, 1, 'nenhuma releitura nos dias seguintes');
 // Emitir apaga a data (salarioEmitir_ / onEdit da área própria): a conferência volta na próxima vez.
 b.props.delete('salario_proximo'); b.ctx.r53SalarioConferir_(b.ss, Date.now(), b.ctx.PropertiesService.getDocumentProperties());
 eq(b.lidas.length, 2);
 const a = mundo(antigo, false);
 for (const dia of [HOJE, HOJE + 1, HOJE + 2]) { a.ctx.salarioHoje_ = () => dia; a.ctx.r53SalarioConferir_(a.ss, Date.now(), a.ctx.PropertiesService.getDocumentProperties()); }
 eq(a.lidas.length, 3, 'o de antes relia todo dia');
}
// Os dois caminhos de emissão do Salarios.gs ainda apagam a data guardada.
eq((novo.match(/deleteProperty\('salario_proximo'\)/g) || []).length >= 2, true);
console.log(JSON.stringify({ checks, resultado: 'OK', escopo: 'sem carteira: próxima conferência em 3650 dias (antes, amanhã); com carteira, igual; releituras em 3 dias 3 → 0' }));
