'use strict';
// VM com serviços simulados: mapearLote() acha a paleta pintada e grava o mapa; a troca lê só o mapa, grava por papel
// e faz um flush no fim. Não fala com o Sheets.
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
// Faixas: duas linhas iguais emendam; célula fixa fica de fora.
assert.deepStrictEqual(JSON.parse(JSON.stringify(vm.runInContext('r53LoteFaixas_([["a","a",null],["a","a","b"]])', ctx))), {a: ['A1:B2'], b: ['C2']});
assert.strictEqual(vm.runInContext('r53LoteA1_(0, 27)', ctx), 'AB1');
const ordem = [], grav = {};
const fundos = [[h(A.fundo), h(A.acento), '#123456'], [h(A.fundo), h(A.painel), h(A.painel)]];
const letras = [[h(A.texto), h(A.osso_por_papel.acento), '#123456'], [h(A.texto), h(A.linha), h(A.texto)]];
let mapaGravado = null;
const aba = nome => ({getMaxRows: () => 2, getMaxColumns: () => 3,
  getRange: () => ({getBackgrounds: () => (ordem.push('ler'), fundos), getFontColors: () => letras}),
  getRangeList: lista => ({setBackground: c => { ordem.push('gravar'); lista.forEach(a => grav[nome + ' b ' + a] = c); },
                           setFontColor: c => { lista.forEach(a => grav[nome + ' f ' + a] = c); }})});
const mapaAba = {getRange: () => ({setNumberFormat() { return this; }, setValues: v => { mapaGravado = v; },
  getValues: () => (ordem.push('ler mapa'), mapaGravado)}), hideSheet() {}};
let temMapa = false;
const ss = {getSheetByName: n => n === 'DADOS' ? {getRange: () => ({setValue: v => { grav.barra = v; }})}
  : n === 'R53_LOTE' ? (temMapa ? mapaAba : null) : n === 'CARTEIRA' ? aba(n) : null,
  insertSheet: () => (temMapa = true, mapaAba)};
ctx.SpreadsheetApp = {getActive: () => ss, flush: () => ordem.push('flush')};
vm.runInContext('mapearLote()', ctx);
const mapa = JSON.parse(mapaGravado.map(l => l[0]).join(''));
assert.strictEqual(mapa.paleta.split(' · ')[0], 'Blush');
ordem.length = 0;
vm.runInContext('r53LoteTrocar_({value: "Noite · Escuro"})', ctx);
assert.strictEqual(ordem[0], 'ler mapa'); assert.strictEqual(ordem[ordem.length - 1], 'flush');
assert(!ordem.includes('ler'));
assert.strictEqual(grav['CARTEIRA b A1:A2'], '#' + N.fundo);
assert.strictEqual(grav['CARTEIRA b B1'], '#' + N.acento);
assert.strictEqual(grav['CARTEIRA b B2:C2'], '#' + N.painel);
assert(!Object.keys(grav).some(k => k.endsWith(' C1')));
assert.strictEqual(grav['CARTEIRA f B1'], '#' + N.osso_por_papel.acento);
assert.strictEqual(grav['CARTEIRA f B2'], '#' + N.linha);
assert.strictEqual(grav.barra, '#' + N.barra);
console.log(JSON.stringify({resultado: 'OK', limite: 'VM com serviços simulados; não mede o Sheets nem o Android.'}));
// Bordas: toda borda vira #857F99 com o mesmo estilo; lado sem borda fica de fora; um batchUpdate só.
const lotes = [];
ctx.Sheets = {Spreadsheets: {
  get: () => ({sheets: [{data: [{rowData: [{values: [{userEnteredFormat: {borders: {top: {style: 'SOLID_MEDIUM', colorStyle: {rgbColor: {red: 1}}}, left: {style: 'NONE'}}}}]}]}]}]}),
  batchUpdate: (b) => lotes.push(b)}};
const sh1 = {getMaxRows: () => 1, getMaxColumns: () => 1, getSheetId: () => 7, getRange: () => ({getA1Notation: () => 'A1'})};
ctx.SpreadsheetApp = {getActive: () => ({getId: () => 'x', getSheetByName: n => n === 'CARTEIRA' || n === 'FICHA' ? sh1 : null})};
vm.runInContext('fixarBordasLote()', ctx);
assert.strictEqual(lotes.length, 1); assert.strictEqual(lotes[0].requests.length, 2);
const bd = JSON.parse(JSON.stringify(lotes[0].requests[0].updateCells.rows[0].values[0].userEnteredFormat.borders));
assert.deepStrictEqual(Object.keys(bd), ['top']); assert.strictEqual(bd.top.style, 'SOLID_MEDIUM');
assert.strictEqual(Math.round(bd.top.colorStyle.rgbColor.red * 255), 0x85);
console.log(JSON.stringify({bordas: 'OK'}));
