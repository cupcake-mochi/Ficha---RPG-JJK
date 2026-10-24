'use strict';
// VM com serviços simulados: o lote lê tudo antes de gravar e mapeia fundo, texto, osso e papéis. Não fala com o Sheets.
const vm = require('vm'), assert = require('assert');
const {preparar, NOVO} = require('../diagnostico-android/preparar_lote.js');
const {ANCORA} = require('../diagnostico-android/preparar_tema.js');
const p = preparar({files: [{name: 'Codigo', type: 'SERVER_JS', source: ANCORA}]});
assert.strictEqual(p.files[0].source, NOVO);
const ctx = {console: {log() {}}};
vm.createContext(ctx);
vm.runInContext(p.files.find(f => f.name === 'LotePaleta').source, ctx);
const A = vm.runInContext('r53LoteCores_("Blush · Claro · rosa e coral")', ctx), N = vm.runInContext('r53LoteCores_("Noite · Escuro")', ctx);
const h = x => '#' + x.toLowerCase();
const ordem = [];
const fundos = [[h(A.fundo), h(A.acento), '#123456']], letras = [[h(A.texto), h(A.osso_por_papel.acento), h(A.texto_fraco)]];
const faixa = {getBackgrounds: () => (ordem.push('ler'), fundos), getFontColors: () => letras,
  setBackgrounds: v => { ordem.push('gravar'); faixa.b = v; }, setFontColors: v => { faixa.l = v; }};
const props = {};
const ss = {getSheetByName: n => n === 'DADOS' ? {getRange: () => ({setValue: v => { props.barra = v; }})}
  : n === 'CARTEIRA' || n === 'FICHA' ? {getMaxRows: () => 1, getMaxColumns: () => 3, getRange: () => faixa} : null};
ctx.SpreadsheetApp = {getActive: () => ss, flush: () => ordem.push('flush')};
ctx.PropertiesService = {getDocumentProperties: () => ({getProperty: k => props[k] || null, setProperty: (k, v) => { props[k] = v; }, deleteProperty() {}})};
vm.runInContext('r53LoteTrocar_({value: "Noite · Escuro", oldValue: "Blush · Claro · rosa e coral"})', ctx);
assert.deepStrictEqual(ordem, ['ler', 'ler', 'gravar', 'gravar', 'flush']);
assert.deepStrictEqual(JSON.parse(JSON.stringify(faixa.b)), [['#' + N.fundo, '#' + N.acento, '#123456']]);
assert.deepStrictEqual(JSON.parse(JSON.stringify(faixa.l)), [['#' + N.texto, '#' + N.osso_por_papel.acento, '#' + N.texto_fraco]]);
assert.strictEqual(props.lote_paleta, 'Noite · Escuro'); assert.strictEqual(props.barra, '#' + N.barra);
console.log(JSON.stringify({resultado: 'OK', limite: 'VM com serviços simulados; não mede o Sheets nem o Android.'}));
